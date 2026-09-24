# Ingestion contract

Every adapter normalizes into the same `features.json`: a JSON array of feature objects. The renderer and the scoring fan-out both read this and nothing else, so a new source only ever needs a new adapter — never a change to scoring or rendering.

## Contents

- [Schema](#schema)
- [Minimum viable feature](#minimum-viable-feature)
- [Jira adapter](#jira-adapter)
- [Aha adapter](#aha-adapter)
- [Repo directory adapter](#repo-directory-adapter)
- [Gherkin fidelity](#gherkin-fidelity)
- [Parse failures](#parse-failures)
- [Merging a tracker record with a repo spec](#merging-a-tracker-record-with-a-repo-spec)
- [Artifact naming](#artifact-naming)

## Schema

```jsonc
{
  "key": "AI-124",                  // required, unique; the badge and anchor key
  "title": "Guided Session Shell",  // required
  "url": "https://.../browse/AI-124",// optional; makes the card key a link
  "source": "jira",                 // jira | aha | repo | tracker+repo
  "sourcePath": "features/ai124/",  // repo-sourced features only

  "status": "Ready - Delivery Intake",
  "workstream": "Experience",       // becomes the lane; free text
  "phases": [2, 3, 4],
  "clientVisible": true,

  "consumes": ["context-pack"],     // artifact names; drives the chain
  "produces": ["capsule"],

  "userContext": "As a client stakeholder, I want …",
  "scope": ["…"],
  "outOfScope": ["…"],

  "featureTags": ["@feature"],      // tags on the Feature: line
  "language": "en",
  "background": {                   // feature-level Background, or null
    "name": "", "file": "acceptance.feature", "line": 6,
    "steps": ["Given the finance period is open"],
    "stepDetails": [ /* same shape as a scenario's, below */ ]
  },
  "backgrounds": [ /* every feature-level Background, when a dir holds several files */ ],

  "rules": [                        // the Gherkin
    {
      "rule": "The client is never asked for what the platform already knows",
      "id": "context-reuse",        // @rule:<slug> tag, else a slug derived from the text
      "idSource": "tag",            // "tag" | "derived"
      "tags": ["@rule:context-reuse"],
      "file": "acceptance.feature",
      "line": 12,
      "description": "",            // free text under the Rule: line
      "background": null,           // Rule-scoped Background, or null
      "scenarios": [
        {
          "name": "The session opens on a prepared capsule",
          "id": "session-opens-on-capsule",
          "idSource": "derived",
          "type": "scenario",       // "scenario" | "scenario_outline"
          "keyword": "Scenario",
          "file": "acceptance.feature",
          "line": 15,
          "steps": ["Given a context pack exists", "When the session begins", "Then …"],
          "stepDetails": [          // the same steps, with what a flat string cannot hold
            {"keyword": "Given", "text": "a context pack exists", "line": 16},
            {"keyword": "When", "text": "the following packs exist:", "line": 17,
             "dataTable": [["pack", "state"], ["P-1", "ready"]]},
            {"keyword": "Then", "text": "the note reads:", "line": 20,
             "docString": {"content": "…", "mediaType": ""}}
          ],
          "examples": [             // [] for a plain scenario
            {"name": "Around the threshold", "tags": ["@boundary"], "line": 24,
             "effectiveTags": ["@feature", "@mvp", "@small", "@boundary"],
             "header": ["amount", "status"],
             "rows": [["$9,999.99", "Approved"], ["$10,000.00", "Pending"]]}
          ],
          "exampleCount": 2,        // executable examples this scenario expands to
          "tags": ["@mvp", "@small"],          // the scenario's OWN tags, verbatim
          "inheritedTags": ["@feature"],       // from the Rule, then the Feature
          "effectiveTags": ["@feature", "@mvp", "@small"]
        }
      ]
    }
  ],
  "ruleCount": 7,                   // denormalized for the card metrics
  "scenarioCount": 15,              // authored scenarios (an outline counts once)
  "exampleCount": 23,               // executable examples (outlines expanded)
  "parseErrors": [],                // see "Parse failures"

  "nfr": [
    {"id": "N1", "dim": "Performance", "req": "Turn response time",
     "threshold": "TBD", "evidence": "Session telemetry", "gap": "Unset"}
  ],
  "nfrTbd": [ /* subset of nfr with unset or TBD thresholds */ ],

  "evals": [
    {"id": "no_jargon_leak", "type": "policy_compliance",
     "rule_link": "No internal vocabulary reaches the client",
     "method": "assert the banned-term list is absent",
     "pass_threshold": "zero occurrences", "gate": "pr"}
  ],

  "openQuestions": ["P0-7: how vision sensitivity is calculated"],
  "dod": ["All scenarios automated and passing"],
  "privacy": "Free text on confidentiality handling",
  "specNote": "Shown on the card when rules[] is empty — say where the spec lives"
}
```

Every field except `key` and `title` is optional. Missing fields degrade the card gracefully; they do **not** get invented. An empty `nfr` array means this feature declares no NFRs, and the rubric will score that honestly.

**Scenario tags** carry release-slicing and sizing decisions made by `aipos-feature-slice`: `@mvp` / `@v1` / `@v2` for the release slice, `@small` / `@medium` / `@large` for the size band. Ingest them verbatim, wherever the Gherkin lives — the repo adapter parses tag lines above each scenario, and a tracker adapter parsing Gherkin out of a description or Acceptance Criteria field must preserve those lines onto `tags` rather than dropping them. Tags are decisions someone made; an adapter that loses them silently un-decides a release plan. Never derive or invent tags during ingestion — an untagged scenario is untagged.

**Tag inheritance.** Gherkin tags inherit: a tag on `Feature:` applies to every scenario in the file, and a tag on `Rule:` to every scenario beneath it. Three fields keep the two facts apart:

| Field | Contents |
|---|---|
| `tags` | The scenario's own tag line, verbatim. The pre-existing contract; unchanged. |
| `inheritedTags` | Tags from the `Rule:` and then the `Feature:` — most specific first. |
| `effectiveTags` | Inherited then own, de-duplicated — what a `--tags` run would match for the scenario as a whole. Tags on an `Examples:` block apply only to that block's rows, so they are **not** folded in here; each block carries its own `examples[].effectiveTags` (the scenario's effective tags plus the block's own). |

Slice resolution reads **most specific first**: the scenario's own delivery tag, then the `Rule:`'s, then the `Feature:`'s. A `@v1` on the `Feature:` is a default for the file; a `@mvp` on a `Rule:` narrows that default for its scenarios; a scenario tagged `@mvp` has overridden both deliberately. `inheritedTags` is ordered so that a consumer walking it front to back gets this precedence for free. Records that predate `effectiveTags` and carry only `tags` keep resolving exactly as before.

**Identifiers.** `rules[].id` and `rules[].scenarios[].id` are the stable identity used to link rules, scenarios, NFRs, evaluations and evidence. They come from an `@rule:<slug>` / `@scenario:<slug>` tag when the author wrote one (`idSource: "tag"`), and are otherwise slugified from the name (`idSource: "derived"`). See `../../../references/spec-identifiers.md`.

## Minimum viable feature

Scoring needs `rules` to say anything useful. A feature with `key`, `title` and nothing else will score near zero — which is correct, and should carry `notAssessable` if the spec exists somewhere the ingestion could not reach. Set `specNote` so the card explains itself rather than looking like an oversight.

## Jira adapter

Use the Atlassian MCP tools.

1. `searchJiraIssuesUsingJql` with `parent = <epic>` or `"Epic Link" = <epic>` to enumerate features.
2. `getJiraIssue` per key for description and custom fields.

| Contract field | Jira source |
|---|---|
| `key` | issue key |
| `title` | summary |
| `url` | browse URL |
| `status` | status name |
| `workstream`, `phases`, `clientVisible` | labels, by convention (e.g. `map-ws-experience`, `map-p2`, `map-client-visible`) |
| `consumes` / `produces` | labels `map-in-<artifact>` / `map-out-<artifact>` |
| `rules` | Gherkin parsed out of the description or the Acceptance Criteria field |
| `nfr`, `evals` | custom fields, or tables in the description |
| `openQuestions` | a description section, or linked issues |

Label conventions vary per organisation. Confirm the convention with the user rather than assuming, and record it in the map's lede so a reader knows the chain is derived from labels.

Jira descriptions arrive in ADF or wiki markup. Convert to plain text before parsing Gherkin, and expect `Given`/`When`/`Then` to survive as line-leading tokens.

## Aha adapter

Use the Aha MCP tools. `find_project` resolves the workspace; `read_records` and `search_records` pull features. Call `fields_metadata` first — Aha! custom field keys are workspace-specific and guessing them silently produces empty specs.

| Contract field | Aha! source |
|---|---|
| `key` | reference number (e.g. `PRJ-123`) |
| `title` | name |
| `url` | record URL |
| `status` | workflow status |
| `workstream` | initiative, epic name, or a custom field |
| `phases` | release, or a custom field |
| `rules` | Gherkin in the description, or a custom field holding acceptance criteria |
| `nfr`, `evals` | custom fields; confirm keys via `fields_metadata` |
| `consumes` / `produces` | a custom field, or tags |

Aha! features often carry requirements as child records. If the Gherkin lives there rather than on the feature, pull requirements and fold them into `rules` — one rule per requirement, scenarios beneath.

## Repo directory adapter

`scripts/repo_ingest.py` walks a directory tree. A directory is treated as a feature when it contains at least one `*.feature` file or a `feature_source.md`.

```
<root>/
  <epic>/
    <feature>/
      acceptance.feature      -> rules[]
      nfrs.md                 -> nfr[]      (markdown table, columns matched by header name)
      eval_criteria.yaml      -> evals[]
      feature_source.md       -> userContext, scope, outOfScope, openQuestions, dod, privacy,
                                 produces[], consumes[]   (from `## Produces` / `## Consumes`
                                 sections; entries normalized to kebab-case)
```

A repo-first corpus therefore carries its own chain: `aipos-feature-create` writes the
`## Produces` / `## Consumes` sections from the story map's scope boundaries, and this
adapter reads them. When merging with a tracker (below), tracker labels take precedence
and repo sections fill in where the tracker is silent.

These are the artifact names `aipos-feature-refine` already declares in its Inputs section, so a repo laid out for refinement needs no changes to be mappable.

Feature keys are derived from the directory name — `ai204_content_and_gates` → `AI-204` — or from a key appearing in the `Feature:` line. Pass `--key-from feature` to prefer the latter.

Gherkin without explicit `Rule:` blocks parses into a single unnamed rule. That is deliberate: the rubric's rule-coverage dimension will mark it as a gap rather than the adapter inventing rules the author never wrote.

A `Rule:` that declares a decision but carries **no scenarios** is kept, with an empty `scenarios` array. A declared rule nobody has illustrated is precisely the coverage gap a reviewer needs to see, and dropping it made it invisible. This does raise `ruleCount` for such files relative to older runs — deliberately, and it is the only count that moved.

## Gherkin fidelity

`repo_ingest.py` parses with [`gherkin-official`](https://pypi.org/project/gherkin-official/), the Cucumber team's own parser (MIT, same licence as this repository). Install it first:

```bash
python -m pip install -r scripts/requirements.txt
```

The dependency is pinned in that file. It exists because hand-rolled line scanning cannot preserve what a review actually needs:

| Preserved | Where it lands |
|---|---|
| Rule association | `rules[].scenarios[]`, plus `rules[].id` |
| Scenario vs Scenario Outline | `type`, `keyword` |
| Feature-level Background | `background`, `backgrounds[]` |
| Rule-level Background | `rules[].background` |
| Examples tables | `scenarios[].examples[]` with `header` and `rows` |
| Step data tables | `stepDetails[].dataTable` |
| Doc strings | `stepDetails[].docString` |
| Tags and inheritance | `tags`, `inheritedTags`, `effectiveTags`, `featureTags` |
| Source locations | `line` and `file` on features, rules, scenarios and steps |

**Authored scenarios and executable examples stay distinct.** `scenarioCount` counts what a person reviews — one `Scenario Outline` is one scenario. `exampleCount` counts what a runner executes — that same outline expanded over its `Examples` rows. Neither number is wrong; reporting one as the other is.

## Parse failures

A `.feature` file that does not parse contributes **no rules at all**. It does not contribute the scenarios that happened to appear before the error, because a partial feature that looks complete sends the reviewer to the wrong person.

Instead the feature record carries `parseErrors` — `{file, line, column, message}` per error — and a `specNote` saying so. `repo_ingest.py` prints the same diagnostics to stderr as `path:line:column: message`, still writes `features.json` (one malformed spec should not make a corpus unmappable), and exits **3**. Other exit codes: `0` fine, `1` nothing found, `2` the parser is not installed.

The renderer shows the diagnostics on the card. "Did not parse" and "has no acceptance criteria" need different responses, and only one of them is the author's fault.

`feature_source.md` sections are matched loosely by heading name, because teams name them differently. "Out of scope" is tested before "scope" — otherwise every exclusion lands in the scope list.

## Merging a tracker record with a repo spec

```bash
python scripts/repo_ingest.py <repo-root> --merge tracker-features.json -o features.json
```

Matched by `key`. The repo wins on spec content — `rules`, `ruleCount`, `scenarioCount`, `exampleCount`, `featureTags`, `background`, `backgrounds`, `language`, `parseErrors`, `nfr`, `nfrTbd`, `evals`. The tracker keeps everything it uniquely knows: status, workstream, phases, ownership, and the `consumes`/`produces` arrays that build the chain. Any other field the tracker left empty is filled from the repo. Merged features are marked `"source": "tracker+repo"`.

This is the case worth designing for. A team that deliberately keeps its spec in the repo — because two copies of a spec drift — should not be badged as though it has no spec.

## Artifact naming

The chain is built by matching strings in `produces` against strings in `consumes`. Normalize to kebab-case during ingestion. A chain that silently drops edges because two features spelled `context-brief` and `Context Brief` differently is worse than no chain at all, because it looks complete.

After ingesting, print the artifact ledger and check it with the user. Artifacts with no producer, or produced but never consumed, are usually either genuine boundary cases or a naming mismatch — and the difference matters.
