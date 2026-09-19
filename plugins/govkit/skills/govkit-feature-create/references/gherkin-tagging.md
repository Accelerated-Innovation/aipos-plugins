# Gherkin Structure and Automatic Tagging

> **Tool-agnostic.** These are standard Cucumber/Gherkin tags. A team can run `cucumber --tags @mvp` and execute exactly the MVP slice — that is the point, not a coincidence.
>
> **This file owns tags and the validation checks.** How to write the scenarios themselves — BRIEF, explicit rules, boundaries, scenario isolation, provenance, backgrounds, outlines, deterministic checks versus aggregate evaluations — lives once in `../../../references/gherkin-authoring-standard.md`. Read that first; this file does not restate it.

## Contents

- [Required structure](#required-structure)
- [Scenario writing rules](#scenario-writing-rules)
- [Tag vocabulary](#tag-vocabulary)
- [Automatic tag assignment](#automatic-tag-assignment)
- [GenAI mode requirements](#genai-mode-requirements)
- [Validation checks](#validation-checks)
- [Interop with govkit-feature-slice](#interop-with-govkit-feature-slice)

## Required structure

Always emit a complete, syntactically valid Gherkin artifact — never a fragment, never a bare list of scenarios.

```gherkin
@feature
Feature: <Feature Name>

  As a <primary persona>
  I want <capability>
  So that <outcome>

  Background:
    Given <setup shared by EVERY scenario in the file>

  @rule:<stable-slug>
  Rule: <One business rule, in the PM's own words>

    Background:
      Given <setup shared by this rule's scenarios only>

    @mvp @functional @scenario:<stable-slug>
    Scenario: <Clear scenario title>
      Given <precondition>
      When <the single action under test>
      Then <observable outcome>

  @rule:<stable-slug>
  Rule: <The next business rule>

    @v1 @edge-case @scenario:<stable-slug>
    Scenario: <Clear scenario title>
      Given ...
```

Rules:

- Always include the `Feature:` header and the persona intent block. The intent block is what makes the file readable six months later by someone who never attended the refinement.
- **One `Rule:` block per business rule**, scenarios grouped beneath the rule they prove. The whole downstream organizes on rules: `govkit-feature-refine`'s rule-coverage dimension, Example Mapping's Rules cards, `eval_criteria.yaml`'s `rule_link`, the readiness gate's structure check, and the feature map's cards (which render "(no Rule declared)" for ungrouped scenarios). A scenario that proves no stated rule is a missing rule to surface, not an orphan to leave.
- Use a feature-level `Background:` **only** when setup is genuinely shared by every scenario in the file. A `Background` that applies to three of five scenarios is a bug: it silently changes the meaning of the other two. Where setup is shared by one rule's scenarios, put it in a `Background:` inside that `Rule:` — Gherkin scopes it there, and so does GovKit's ingestion.
- Keep scenarios atomic — one behavior, one `When`.
- No implementation detail. "When the user submits the form", not "When a POST is sent to `/api/claims`". The Gherkin outlives the endpoint.
- Prefer several concise scenarios over one long one. A scenario with four `When` steps is usually three scenarios.
- Use `Scenario Outline` for genuine data variation of one behavior, not to compress unrelated cases into a table.

## Scenario writing rules

Every scenario needs an **observable outcome** — something a person or a test can check from outside the system. `Then the record is saved` is not observable; `Then the claim appears in the adjuster's queue with status "Pending review"` is.

This is the single most common Draft 0 defect and it is a named blocker in `govkit-feature-readiness`. Catching it here costs one sentence; catching it at the gate costs a round trip.

Ground every scenario in the feature's stated rules. If a scenario would require a business rule nobody has stated, that is a gap to surface — not a rule to invent.

## Tag vocabulary

### Delivery phase — exactly one required

| Tag | Meaning |
|---|---|
| `@mvp` | Critical path. The journey cannot fundamentally function without it. |
| `@v1` | Operational stability: common errors, validation, permissions. |
| `@v2` | Optimization, advanced UX, edge cases, secondary personas. **V2 or later** — this is also where explicitly deferred work goes. |

Exactly one per scenario. Never two. A scenario the PM has not decided on stays untagged and is reported as undecided — do not default it into a phase to make the file look complete.

**These three tags are the entire vocabulary.** Do not invent a fourth. `@v2` already means "V2 or later", so work the PM has parked indefinitely is `@v2`, and the *reason* it was parked belongs in the Out of Scope section of `feature_source.md` where it can carry an explanation a tag never could. A tag outside this set is not merely unrecognized downstream — it is silently discarded; see [Interop](#interop-with-govkit-feature-slice).

### Classification — at least one required

| Behavior | Tag |
|---|---|
| User-visible business behavior | `@functional` |
| Error handling, invalid input, failure paths | `@edge-case` |
| Authentication, authorization, security constraint | `@nfr-security` |
| Latency, throughput, load validation | `@nfr-performance` |
| Regulatory or statutory rule | `@nfr-compliance` |
| Personal or sensitive data handling | `@nfr-privacy` |
| Model-generated behavior | `@genai` |
| A measurable evaluation threshold | `@evaluation` |
| Invocation of an external tool or function by a model | `@tool-use` |
| Harm, abuse, or unsafe-output prevention | `@safety` |

More than one is normal and expected: `@v1 @edge-case @nfr-security` is a well-tagged
scenario.

**Why four of these carry an `@nfr-` prefix.** They are the ones GovKit's own validator
enforces. `govkit validate` cross-references the populated categories in `nfrs.md` against
`@nfr-<category>` tags in the feature file, so a scenario tagged `@security` did **not**
satisfy a populated Security NFR — the check looked for `@nfr-security` and found nothing.
This reference previously taught the bare spellings, which meant a package authored exactly
as instructed could fail its own validation.

The categories `govkit validate` currently enforces are `performance`, `availability`,
`security`, `compliance`, `scalability`, `observability`, `reliability`, `compatibility`,
`freshness`, `quality`, `pii`, `lineage` and `cost`. A populated NFR section in one of
those demands the matching `@nfr-<category>` tag.

**`privacy` is not in that list, and `@nfr-privacy` is still the right tag.** The NFR
dimension this template walks is *Privacy*, so the tag has to carry the same word or the
table and the Gherkin stop describing each other. An earlier draft of this change used
`@nfr-pii` — matching the validator's nearest category — and that was the wrong trade: it
made the tag agree with a checker at the cost of disagreeing with the document that tells
authors what to write. The pair being coherent matters more than the pair being enforced.

The consequence, stated plainly: a populated Privacy section is **not** cross-referenced
against its tag today. Closing that is one entry in `known_categories` in
`cli/validate.py`, and it would make validation stricter for every existing project with a
Privacy section and no tag — a compatibility decision rather than a typo fix, which is why
it is named here and not made.

**One divergence is deliberate and unresolved.** GovKit's installed tag reference
distinguishes `@edge-case` (boundary or unusual input) from `@error` (expected failure:
invalid input, permission denied, timeouts). This vocabulary folds both into `@edge-case`.
Neither tag is enforced by a validator, so nothing breaks either way — but the two
documents do not agree, and that is recorded here rather than quietly reconciled in one
direction.

Preserve any tag this skill does not own — `@wip`, `@smoke`, team conventions — exactly as found.

### Identity — recommended, and **required under a behavior contract**

| Tag | On | Meaning |
|---|---|---|
| `@rule:<slug>` | a `Rule:` | Stable identity for the business decision |
| `@scenario:<slug>` | a scenario or outline | Stable identity for the behavior |

Outside the delivery and classification vocabularies, so they never affect slicing, sizing
or filtering. They exist so `rule_link` in `eval_criteria.yaml`, NFR rows, readiness
evidence and test names survive rewording.

**Where a project commits to behavior, these stop being optional.** A behavioral baseline
binds the exact Rules and scenarios an approval covers, and it **refuses**
`id_source: derived` — a slug taken from an element's name changes when the name does, so
it cannot bind an approval. An element with no authored tag therefore cannot be part of a
commitment at all: `govkit inspect-package` flags it rather than converting it, and no
amount of later tooling recovers it.

This section previously said identifiers were "optional and additive", on the grounds that
a package without them "still ingests, renders, scores and slices identically". All four of
those remain true. The sentence was written before baselines existed and was never revisited
when they did, so it kept reassuring authors about the four things that still work while
omitting the one that stopped working. **Readable is not approvable.**

For a project with no decision service, nothing changes: add them because a derived id is
stable only as long as a name is. See `../../../references/spec-identifiers.md`.

### Inheritance

Tags inherit downward: a tag on `Feature:` applies to every scenario in the file, a tag on `Rule:` to that rule's scenarios. GovKit resolves a delivery slice **most specific first** — a scenario's own `@mvp` overrides an `@v1` declared on the Feature. Use a feature-level slice tag as a deliberate default for a file, never as a substitute for deciding per scenario where the phases actually differ.

## Automatic tag assignment

**Derive tags. Do not ask the PM to pick them.**

Delivery phase comes from the feature's confirmed slice. Classification comes from the scenario's own behavior, using the table above. Both are mechanical enough that asking wastes the PM's attention on the one part of the process where their judgment adds nothing.

Ask for clarification **only** when:

1. The feature's slice is genuinely unknown (no slice was confirmed in Epic mode and none was given).
2. A scenario spans delivery phases — part of it is MVP and part is not. That is usually a split, so propose the split rather than the tag.
3. The scenario's intent cannot be classified from its text, which normally means the scenario itself is unclear and needs rewriting first.

When derivation is ambiguous but the scenario is sound, pick the tag the scenario's text best supports and note the call in one line rather than stopping the flow.

## GenAI mode requirements

When GenAI mode is active, the file must satisfy all of:

- At least one scenario tagged `@genai` — the model-generated behavior itself.
- At least one scenario tagged `@evaluation` with a **measurable, threshold-based** outcome.
- Any scenario where the model invokes an external tool or function tagged `@tool-use`.
- Hallucination, groundedness, or unsafe-output validation tagged `@nfr-compliance` or `@safety`.

Generate these without prompting the PM. They are the difference between a GenAI feature that can be gated and one that ships on vibes.

**Keep the two registers in separate scenarios.** A deterministic behavior check says what happens on one occasion; an aggregate evaluation says what a statistic does over a dataset. A scenario that asserts both is unfalsifiable, because a single run cannot decide it. This is the most common defect in GenAI Gherkin:

```gherkin
  @mvp @genai @functional @scenario:summary-cites-its-sources
  Scenario: A generated summary cites the documents it drew on
    Given a claim file with 12 uploaded documents
    When the assistant generates a claim summary
    Then the summary is labelled "AI-generated summary"
    And every factual statement in the summary carries a link to a source document
```

```gherkin
  @mvp @genai @evaluation @scenario:groundedness-gate
  Scenario: Summary groundedness clears the release gate
    Given the claim-summary evaluation set of 300 reviewed claim files
    When groundedness is scored with the reviewed-reference scorer
    Then the mean groundedness score is at least 0.95
    And the evaluation report is attached to the release review
```

The first is checkable on one claim file and belongs in the ordinary suite. The second is a property of the dataset, and it is a specification only when all five parts are present: **dataset** (which set, how large, where it lives), **method** (the scorer, judge or metric, named), **threshold** (the team's number), **execution context** (where it runs and what it gates), and **evidence** (the artifact and its owner). The `eval_criteria.yaml` entry carries the rest; the scenario names enough that a reader knows what is being claimed.

The number must come from the PM or from inherited epic criteria — never from you. If the PM has not given a threshold, write it as an open gap (`Then the mean groundedness score is at least <TBD — threshold needed>`), list it in the summary, and do not report that scenario as ready for execution. A `0.95` you invented will be treated as a commitment by everyone downstream.

**An AI coding agent building the feature does not make the feature GenAI.** These tags describe what the product does at runtime. Ordinary software written with a coding agent gets ordinary test evidence and no `@genai` tag.

## Validation checks

Run these before presenting Gherkin. Fix what fails — a missing tag is a defect to correct, not a question to ask.

1. Every scenario has **exactly one** delivery-phase tag (or is deliberately untagged and reported as undecided).
2. Every delivery-phase tag is one of `@mvp`, `@v1`, `@v2` — nothing else. Anything outside that set is discarded silently downstream.
3. Every scenario has **at least one** classification tag.
4. No scenario is untagged by accident.
5. No scenario carries two delivery-phase tags.
6. GenAI mode: `@genai` present, `@evaluation` present, tool use tagged `@tool-use`, safety validation tagged `@nfr-compliance` or `@safety`.
7. Delivery tags are consistent with the feature's confirmed slice — an `@mvp` scenario in a V2 feature is either a mis-tag or a scoping error, and both are worth a line.
8. Every `@evaluation` scenario asserts a threshold, or marks the threshold as an open gap.
9. Every scenario has an observable outcome.
10. Every scenario sits under the `Rule:` block it proves; a scenario no stated rule explains is a missing-rule gap to surface, not a formatting fix.
11. The file parses: `Feature:` header present, persona block present, `Rule:` blocks present, no orphaned steps. GovKit ingestion parses with the official Cucumber parser, so anything it rejects is genuinely invalid Gherkin, not a house-style quibble.
12. No scenario depends on another scenario having run — each is independently executable.
13. Every `Background:` is correctly scoped: a feature-level one is true for every scenario in the file; setup true for only one rule's scenarios sits in that rule's `Background:`.
14. Every rule with a threshold, limit, window or count has an example **on** the boundary, not only either side of it.
15. No scenario mixes a single-occasion assertion with an aggregate statistic over a dataset.
16. Every scenario carrying an unresolved `<TBD — …>` placeholder is listed as not ready for execution.

Correcting a tag needs no announcement. **Hiding the result does** — always present the full Gherkin plus a one-line coverage summary so the tagging is inspectable even though it was automatic:

> `5 scenarios · 2 @mvp, 3 @v1 · 3 @functional, 1 @edge-case, 1 @genai + @evaluation`

If a check fails in a way you cannot fix without a product decision — a scenario with no observable outcome because nobody has said what the system should do — say so explicitly. That is a gap, not a formatting problem.

## Interop with govkit-feature-slice

`govkit-feature-slice` owns the `@mvp` / `@v1` / `@v2` vocabulary for **re-slicing existing scenarios**, per-scenario, using the Scenario Complexity Matrix and MoSCoW. This skill assigns the delivery tag once, at creation, from the feature's confirmed slice.

Two consequences worth stating plainly:

- **These tags are a starting position, not a final release commitment.** When slice re-decides a scenario, its decision wins — it judged the scenario; this skill judged the feature.
- **The vocabulary is closed, and enforced by code downstream.** `mvp` / `v1` / `v2` are hard-coded in `govkit-feature-slice`'s `compute_size.py` (`SLICES`) and `govkit-feature-map`'s `render_map.py` (`SLICE_TAGS`). A delivery tag outside that set fails silently and in three separate ways:

| Where | What happens to an unrecognized delivery tag |
|---|---|
| `render_map.py` — `scen_slice()` | Returns `""`, so the scenario gets no `data-slice` attribute: dimmed under every release filter, selectable by none |
| `render_map.py` — card rendering | Tag chips render only for known slice and size tags, so the tag is not displayed at all |
| `compute_size.py` — validation | `taggedSlice` outside `SLICES` fails the verdict outright; via tags it resolves to `null` and the scenario's points fall into the `untagged` bucket |

  None of these produce an error the PM will see. The scenario simply stops counting. Emit only the three tags above.

Size tags (`@small` / `@medium` / `@large`) belong to `govkit-feature-slice` and are computed from its script. **Never emit a size tag here** — a size judged before the scenarios were reviewed is a guess wearing a badge.
