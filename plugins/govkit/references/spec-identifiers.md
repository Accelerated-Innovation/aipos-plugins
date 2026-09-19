# Stable Rule and Scenario Identifiers

> **Shared reference.** Read by `govkit-feature-create`, `govkit-feature-refine`,
> `govkit-feature-slice`, `govkit-feature-readiness` and `govkit-feature-map`.
> From a skill folder: `../../references/spec-identifiers.md`.
> Companion to [`gherkin-authoring-standard.md`](gherkin-authoring-standard.md)
> and [`workflow-source.md`](workflow-source.md).

## The problem this solves

A feature's rules and scenarios get reworded constantly — that is what refinement is for.
But everything that points *at* them currently points by text: `rule_link` in
`eval_criteria.yaml` quotes the rule sentence, NFR rows name a scenario, a readiness
report's evidence table keys on a scenario title, a sizing verdict matches on `name`.

Rewording a rule therefore silently breaks every link into it. Nothing errors; the
evaluation just stops being about anything.

## The convention

**Identifiers are Gherkin tags.** No new file, no sidecar, no registry.

| Element | Tag | Example |
|---|---|---|
| Business rule | `@rule:<slug>` on the `Rule:` line | `@rule:invoice-approval-threshold` |
| Scenario or Scenario Outline | `@scenario:<slug>` on the scenario | `@scenario:approval-routing-by-amount` |

Slugs are lowercase kebab-case, unique within their feature file, and describe the
*decision or behavior* rather than its current wording. Prefer
`@rule:invoice-approval-threshold` over `@rule:invoices-of-10000-or-more` — the second one
is a rename waiting to happen the first time the threshold moves.

```gherkin
@feature
Feature: Invoice approval routing

  @rule:invoice-approval-threshold
  Rule: Invoices of $10,000 or more require finance manager approval

    @mvp @functional @scenario:approval-routing-by-amount
    Scenario Outline: Invoice amount decides the approval path
      ...
```

Tags in both positions are standard Gherkin, so nothing about this is GovKit-specific at
the file level. A Cucumber run, a `--tags` filter and every other Gherkin tool see ordinary
tags.

## Why tags rather than a new field

- **The delivery-tag vocabulary is untouched.** `@mvp` / `@v1` / `@v2` and
  `@small` / `@medium` / `@large` keep their exact meanings and their closed sets.
  Identifier tags are outside those sets, and downstream code already preserves unknown
  tags verbatim while ignoring them for slicing and sizing.
- **They survive the round trip.** Ingestion, rendering, tracker write-back and the
  slice pass all carry tags through already.
- **They are visible in the artifact people argue about.** An identifier in a sidecar file
  is an identifier nobody maintains.

## What identifiers connect

| Points at | Field | Value |
|---|---|---|
| `eval_criteria.yaml` | `rule_link` | `@rule:<slug>` (the rule sentence may stay alongside as prose) |
| `eval_criteria.yaml` | `scenario_link` | `@scenario:<slug>`, when the evaluation is about one scenario |
| `nfrs.md` | `Scenarios` column | one or more `@scenario:<slug>` |
| Readiness report | scenario verification plan rows | keyed by `@scenario:<slug>` |
| Evidence artifacts | filenames or report keys | `@scenario:<slug>` where the runner allows it |
| `features.json` | `rules[].id`, `rules[].scenarios[].id` | the slug, with `idSource` recording where it came from |

## Stability rules

**Renaming preserves identity.** Rewording a `Rule:` sentence or a `Scenario:` title does
not change its identifier. That is the entire point — the identifier is what survives the
rewording.

**Retagging preserves identity.** Changing `@v1` to `@mvp`, adding `@nfr-security`, or applying
a size tag never touches the identifier tag.

**Splitting creates identity, deliberately.** A split is a product event, not a rename, and
it has to be recorded:

- *Scenario split into two.* One child keeps the original `@scenario:` slug — the one that
  still verifies the behavior the original was about. The other gets a new slug. If neither
  child is recognisably the original behavior, both get new slugs and the old one is
  retired. Note the split in the feature's source notes: `approval-routing-by-amount split
  into approval-routing-by-amount + approval-routing-when-manager-absent`.
- *Rule split into two.* Both children get new slugs, the parent slug is retired, and every
  `rule_link` that pointed at the parent has to be repointed. A retired slug is never
  reused for a different decision.
- *Two scenarios merged.* The surviving scenario keeps one slug; the other is retired.

Slicing and retagging must not change identifiers. `govkit-feature-slice` may split a
scenario for size reasons, and when it does, it applies the split rules above and says so
in its output — a split that silently re-identifies its own outputs breaks every evaluation
that pointed at them.

## Referring to another feature's rule or scenario

A slug is unique **within its feature file** and nowhere else. Two features may legitimately
carry the same one — `@rule:invoice-approval-threshold` can mean the finance-manager threshold
in one feature and the partner-manager rule in another, and both authors were right.

So anything pointing *across* features qualifies the slug:

```
<source-key>/<feature-key>#<kind>:<slug>
```

```
acme/FEATURE-inv_full#rule:invoice-approval-threshold
acme/FEATURE-inv_partner#rule:invoice-approval-threshold     ← a different rule
acme/FEATURE-inv_full#scenario:approval-routing-by-amount
```

| Segment | Is |
|---|---|
| `source-key` | The repository or package, so behavior spanning applications resolves |
| `feature-key` | `features.json`'s `key` — the identity ingestion already guarantees unique |
| `kind` | `rule` · `scenario` · `design` · `nfr` · `evaluation` · `agent-authority` |
| `slug` | The authored tag slug, exactly as written above |

**The tags themselves do not change.** Qualification is a prefix applied by whatever holds the
reference — a workflow, a baseline, an evaluation. Nothing is added to the `.feature` file, and
a package that never participates in a cross-feature reference never sees any of this.

An unqualified slug in a cross-feature position is **refused, not guessed**. Resolving it to
whichever feature happened to be ingested first would make the reference mean something nobody
wrote.

## What a tool does with each identity event

The authoring rules above say what an author does. This is what a resolver does when it meets
the result — `govkit-feature-map`'s workflow resolver implements exactly this table.

| Situation | Resolver behavior |
|---|---|
| **Authored id** (`idSource: "tag"`) | Resolves. |
| **Derived id** (`idSource: "derived"`) | Resolves, with a **warning**. The map still renders; the id cannot bind an approval, because a slug taken from a name changes when the name does. Readable is not approvable. |
| **Duplicate** slug within one feature | **Error.** Neither entry resolves — picking one would be silently wrong about half the time. |
| **Missing** slug | **Error**, naming the feature and the slug. |
| **Retired** slug | Dangles, because a retired slug is never reused. |
| **Split** | One child keeps the original slug and resolves. If neither child is recognisably the original, both are new and the old reference dangles. |
| **Merged** | The survivor keeps one slug; references to the retired one dangle. |
| **Unparsed** feature file | **Error** reporting the parse failure — not "not found", which would send someone to fix the reference instead of the spec. |

**Dangling is the designed outcome for a retired, split or merged identifier, not a gap.**
Auto-following an old slug to "whatever replaced it" would silently repoint an approved
reference at behavior nobody approved. Where the behavior now lives is a decision a person
makes; failing loudly is what forces that decision to happen instead of being assumed.

## Packages with no identifiers

Identifiers are **additive**: every existing feature package keeps working, ingests,
renders, scores and slices exactly as before.

**They are not optional where a project commits to behavior.** A behavioral baseline binds
the exact Rules and scenarios an approval covers and refuses `id_source: derived`, so an
element with no authored tag cannot be part of a commitment — `govkit inspect-package`
flags it rather than converting it. The resolver table above already says why: *readable is
not approvable.* This section used to say "optional and additive" without that
qualification, which was true when it was written and stopped being true when baselines
landed.

Where no identifier tag is present, tools derive one from the name — lowercase, non
alphanumeric runs collapsed to `-`, trimmed — and record `idSource: "derived"` beside it.
`repo_ingest.py` does this per rule and per scenario, so `features.json` always has an
`id`, and a consumer can tell an authored identity from a derived one.

A derived identifier is stable only as long as the name is. That is the whole argument for
adding explicit ones, and the migration is exactly as heavy as adding a tag line:

1. Add `@rule:<slug>` above each `Rule:`.
2. Add `@scenario:<slug>` to each scenario's tag line.
3. Repoint `rule_link` values in `eval_criteria.yaml` from quoted sentences to slugs.

Steps 1 and 2 can be done a feature at a time, with no coordination — a file with
identifiers and a file without both ingest, render, score and slice identically.
