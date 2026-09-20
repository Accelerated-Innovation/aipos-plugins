---
name: aipos-feature-slice
description: "Select a complete release from existing scenarios, check prerequisites, and recommend MVP/V1/V2 scope. Use for the smallest shippable outcome, release tags, and scenario splitting. Optionally assess scenario complexity; those scores do not forecast delivery time."
---

# GovKit Feature Slice — Scenario Sizing and Release Slicing

## Purpose

Help a Product Manager answer one question about one feature, and optionally a second:

1. **Which behavior does this release contain?** — a complete, usable journey, selected on
   outcome and consequence, expressed as `@mvp` / `@v1` / `@v2` tags. This is the job.
2. **How complex is each scenario?** *(optional)* — scored on the Scenario Complexity Matrix,
   three dimensions at 1–3 points each.

**Scope selection does not depend on sizing and never waits for it.** Run the skill with sizing
off and it still does its primary job. Where sizing is run, its value is the risk signal — a
Large scenario on the MVP critical path is the first thing a release plan has to deal with —
not a number to plan against.

This skill is not a quality review. If the Gherkin is too weak to judge — tautological scenarios, unclear intent, missing rules — slicing it is premature; say so and point to `aipos-feature-refine`. You cannot size what you cannot read.

## Tool-agnostic design

Same abstract roles as `aipos-feature-refine`: the **generator** is whatever produced the spec, the **tracker** is wherever the feature fields live (Azure DevOps, Jira, Aha!, Linear, a markdown file). Named tools appear only as adapter examples.

## Key terms

- **Size** — a scenario's points (3–9, sum of three dimension judgments) and band: Small (3–4), Medium (5–7), Large (8–9).
- **Slice** — the release a scenario belongs to, expressed as a Gherkin tag: `@mvp`, `@v1`, or `@v2` (V2 or later).
- **Split** — rewriting one oversized scenario into smaller scenarios, each independently sizeable and sliceable.
- **Rollup** — the feature-level summary: band counts, rendered as e.g. `2L / 5M / 3S`. Produced only when sizing was run.
- **Selected behavior** — the scenarios a release actually commits to. Tags are a *view* of it; what binds a commitment is the explicit reference list in a behavioral baseline.

## What a tag is, and what it is not

`@mvp` / `@v1` / `@v2` are a **planning view** over the selected behavior. They make a release
conversation legible; they do not constitute a commitment, and a tag by itself grants nothing.

What binds a commitment is an explicit list of references — `<source>/<feature-key>#rule:<slug>`
and `#scenario:<slug>` — in a behavioral baseline. That list is the authoritative scope; the tags
are how people talk about it.

Two consequences worth stating plainly:

- **Retagging after approval is a scope change when — and only when — it changes what is
  included.** The distinction follows from the paragraph above and is easy to get wrong in both
  directions.

  Where a baseline selects behavior by **explicit reference**, a referenced scenario keeps its
  `@scenario:<slug>` identity whatever its planning tag says, so moving it between `@v1` and
  `@mvp` resolves to exactly the same committed behavior. That is a view change. Say so and make
  it; blocking it would be treating the view as the commitment, which is the error this section
  exists to prevent.

  It *is* a scope change when the edit changes the selected set: adding a scenario the baseline
  does not reference, removing one it does, or retagging in a package where **inclusion is
  derived from tags** because no baseline exists yet. There the tag is doing the selecting, so
  editing it edits scope. Propose it with the affected identifiers and what it adds or drops;
  do not apply it and re-emit the spec.

  When you cannot tell which case you are in — no baseline is in evidence — say that, and ask
  before editing. A wrong guess either way is worse than the question.
- **`@v2` is not a queue position.** A scenario nobody has committed to is uncommitted, and
  tagging it `@v2` is a note about where it would sit *if* it were ever chosen — not a promise
  that it will be, and not a place in a line. Say so when a PM starts treating the V2 tag as a
  backlog.

## Operating principle

**The skill recommends slices. The PM decides.**

Sizing is an optional diagnostic and can be offered freely. Slice tags are release commitments in the making — they land in the spec only after the PM has confirmed or corrected each recommendation. Never present a recommended slice as a decision, and never write anything to a tracker without the explicit confirmation step in `references/tracker-writeback.md`.

The same division of labor applies to arithmetic: **judge the dimensions, never total them by impression.** Dimension scores are judgments a model makes; sums, bands, and rollups are computed by `scripts/compute_size.py`. A reported total that does not match its own dimensions silently moves a scenario across a band, and the band is what release planning runs on.

## Scope

Use this skill for:

- Sizing the scenarios of one feature
- Recommending MVP / V1 / V2 release slices with MoSCoW
- Flagging oversized scenarios and proposing splits
- Emitting tagged Gherkin and copy-ready tracker field updates
- Writing the tagged spec back to the tracker record, after confirmation
- Batch sizing for a corpus caller (see Batch mode)

Do not use it for:

- Reviewing spec quality or issuing a Development Token recommendation (`aipos-feature-refine`)
- Validating a repo package before coding (`aipos-feature-readiness`)
- Mapping a whole epic (`aipos-feature-map`, which calls this skill per feature)
- Story-point estimation or velocity forecasting — complexity points are not story points, and no total here is a delivery estimate
- Deciding what a release commits to on behalf of the PM, or treating a tag as an approval
- Creating or deleting tracker records; write-back is update-in-place only

## Inputs

Accept any input form `aipos-feature-refine` accepts: pasted tracker fields, markdown from a tracker, a draft `acceptance.feature`, a `feature_source.md`, or a single feature object in `aipos-feature-map`'s `features.json` schema (field mapping: `rules[].rule` = business rules, `rules[].scenarios[]` = the Gherkin, `rules[].scenarios[].tags[]` = existing tags).

If scenarios already carry slice or size tags, read them — they are prior decisions, not blanks to overwrite. Re-recommend only where the user asks, and show a diff against the existing tags.

## Required references

| Reference | Use |
|---|---|
| `references/slicing-rubric.md` | The Scenario Complexity Matrix, the MoSCoW slice definitions, the tag vocabulary, and the split patterns. Read before sizing anything. |
| `references/tracker-writeback.md` | Per-tracker write-back adapters and the preview-confirm protocol. Read before offering to write. |
| `../../references/gherkin-authoring-standard.md` | The shared authoring standard. Read before proposing any split — the pieces have to satisfy it too. |
| `../../references/spec-identifiers.md` | The `@rule:` / `@scenario:` convention, and what a split does to identity. Read before splitting or retagging. |

## Process — interactive slicing (default)

### Step 1: Read the feature and check it is sliceable

Normalize the input, list the scenarios, and confirm with the user which feature and which scenarios are in scope. If the Gherkin fails basic readability — you cannot tell what a scenario proves, or rules are missing wholesale — stop and recommend refinement first. Record any existing `@mvp`/`@v1`/`@v2`/size tags as prior decisions.

### Step 2 *(optional)*: Size every scenario

**Skip this step unless the PM wants the complexity diagnostic.** Scope selection is decided on
outcome completeness and consequence, not on points, and Step 3 onward runs without it. Offer it
once; do not make it a gate.

For each scenario, judge the three dimensions per `references/slicing-rubric.md` — Data & State, Integration, UI/UX Steps, each an integer 1–3 — with a note per dimension grounded in the scenario's own text. Never invent context the spec does not contain; if a dimension is unknowable from the spec, score what the text supports and record the uncertainty in the note — an unknowable dimension is itself a spec gap worth reporting.

Write the judgments to a sizing JSON (Batch mode schema below) and run:

```bash
python scripts/compute_size.py sizing.json -o sizing_computed.json
```

The script computes points, bands, the feature rollup and risk flags, and validates every judgment. Present numbers only from its output. If the script cannot be run in the current environment, do the arithmetic explicitly and show it — never total by eye.

**Do not present any total as a forecast.** Complexity points measure how intricate a scenario is
to specify and verify, not how long anything takes, and scenario counts measure only how many
ways someone chose to write the behavior down. "The MVP is 12 points" reads as a delivery
estimate to everyone who sees it and is not one. Report a total only if the PM asks, and say what
it is not when you do.

### Step 3: Recommend a slice per scenario

First identify the selected user journey and its obligations in the stated Rules, NFRs
and prerequisites. Then apply MoSCoW to the remaining optional scope. The MVP test is:
*can the user complete the selected outcome while honoring those obligations without
this scenario?* Give a one-line rationale tied to the supplied contract.

An ordinary business cutoff, validation boundary or refusal path can be required even
when no safety or compliance risk is involved. "Happy path", "error" and "edge case"
do not decide release priority. Include the controls for the behavior selected, or
propose removing the dependent capability/changing its Rule for a human scope decision.
Accepting risk alone does not make a release comply with an unchanged Rule. For committed
behavior, route an intended scope change through refinement and the commitment workflow.

### Step 4: Check the selection is actually shippable

A set of individually reasonable tags can still describe a release nobody can ship. Three checks,
each of which produces a finding rather than a silent fix:

**The journey completes.** Walk the selected scenarios end to end as a user would. If the
selection stops partway — a request that can be submitted but not resolved, an approval that can
be granted but not acted on — the slice is a layer, not a release. Name the missing step. Judge against the supplied journey: do not invent an alternative payment, export, or operations process to make a stated optional enhancement seem required. If the existing selection completes the outcome without it, explain that directly.

**Selected behavior carries its obligations.** Include what makes the stated contract true:
business validation and boundaries, required authorization, recovery and audit behavior.
Use obligations supported by the input, not imagined dependencies for optional enhancements.
Check two places, because an obligation lives in whichever the author
used:

- **The `Rule:` each selected scenario sits under.** A Rule's obligation is not satisfied by
  selecting one scenario that illustrates it while deferring the one that proves the control.
- **The NFRs, feature-level and linked.** A compliance, security, privacy or retention
  requirement frequently exists *only* as an NFR row with no scenario of its own — "every
  approval records approver identity, retained 7 years" obligates the selection just as a `Rule:`
  does. If a selected scenario triggers such an NFR and nothing in the selection proves it, that
  is a gap, and it is the one most easily missed: the Rule check passes and the control still is
  not there.

Report each as a finding naming the obligation and what would satisfy it. Do not add the missing
scenario yourself — that is the PM's scope decision.

**Cross-feature prerequisites are named.** A scenario whose precondition is behavior owned by
another feature is not shippable until that behavior is committed somewhere. An unstated
cross-feature prerequisite is the most common reason an "MVP" turns out not to be one.

Cite the **most specific reference the input actually supports**, and no more:

| What the input gives you | Cite |
|---|---|
| A qualified reference | `<source>/<feature-key>#scenario:<slug>` verbatim |
| A feature key and a scenario slug | `<feature-key>#scenario:<slug>`, noting the source key is unknown |
| Only a feature key or a prose mention ("owned by FIN-388") | The feature, the behavior in the author's words, and that no identifier was given |

**Never construct an identifier that was not written down.** A plausible-looking
`#scenario:<slug>` for a feature you cannot see is a dangling reference that resolves to nothing
and looks authoritative doing it — `../../references/spec-identifiers.md` forbids exactly this.
Naming the gap is the finding; inventing the reference destroys it.

### Step 5: Flag risk and propose splits

Two things must be surfaced before the PM decides:

- **Large scenarios on the critical path.** A Large `@mvp` scenario means the smallest shippable version contains the riskiest work. Propose a split, or make the PM accept the risk explicitly.
- **Any Large scenario.** Per the rubric, 8–9 points means "consider slicing this scenario down further." Propose concrete splits using the rubric's split patterns, with untagged draft Gherkin. Put recommended releases in the separate recommendation table, not in tag lines or tag comments inside the draft; release tags wait for Step 7. After a split, re-size the pieces — splits should land Small or Medium, and a split that doesn't shrink anything is not a split.

**A split must preserve business meaning.** Restructuring is the only thing a split may change. Every piece has to carry across:

| What | Rule |
|---|---|
| Rule association | Each piece stays under the `Rule:` the original illustrated. A split never orphans a scenario or invents a new rule to house one. |
| Setup | Whatever the original needed — a feature-level `Background`, its rule's `Background`, its own `Given` steps — still reaches every piece that needs it. Splitting is the classic way a `Background` silently stops applying. |
| Examples | An outline's `Examples` rows are distributed, never dropped. If a split leaves a row belonging to neither piece, the split is wrong, not the row. |
| Outcomes | Every `Then` from the original is asserted by some piece. A split that quietly sheds an outcome has changed what the feature promises. |
| Boundaries | The boundary case survives the split. Losing the exact-threshold example while "simplifying" is the most expensive split there is. |
| Identity | One piece keeps the original `@scenario:` slug — the one that still verifies the original behavior; the other gets a new one. Record the split. See `../../references/spec-identifiers.md`. |
| Independence | Each piece stands alone. A split that leaves piece B depending on piece A having run has produced a script, not two scenarios. |

Say explicitly, for each split, what moved where. A PM cannot confirm a split they have to reverse-engineer.

**Retagging preserves meaning too.** Changing a delivery tag re-times work; it never changes what a scenario asserts, what rule it sits under, or its identifier.

### Step 6: Pause for the PM's decisions

Present the sizing table, the rollup, the recommendations, and the proposed splits — then STOP. Ask the PM to confirm or correct each slice recommendation and each split. Do not emit tagged Gherkin or tracker updates until they have. If the PM overrides a recommendation, take the override without argument and record it; the PM owns release intent.

### Step 7: Emit the tagged spec

After confirmation, produce the revised Gherkin with tags on the line above each scenario (slice tag first, then size tag), preserving all existing tags this skill does not own. Emit copy-ready tracker field updates in the same shape `aipos-feature-refine` uses.

### Step 8: Offer write-back

If a tracker MCP is connected, offer to update the record in place, following `references/tracker-writeback.md`: exact preview, named destination, one explicit yes, read-back verification. If no MCP is available, the copy-ready block from Step 7 is the deliverable.

## Output format (interactive)

Steps 2–5 present as below. **The sizing sections appear only when sizing was run** — a
scope-only run emits the selection, the shippability findings and the decisions, and omits the
rest. Do not synthesise a sizing table to fill the template; an output contract that forces the
artifact back in would have made Step 2 optional in name only.

````markdown
# Release Selection — <key or title>

## Selection
| # | Scenario | Recommended slice | Why |
|---|---|---|---|

## Shippability
- **Journey** — <completes end to end, or the missing step>
- **Obligations** — <selected behavior whose authorization / recovery / audit is not also selected, or None>
- **Prerequisites** — <cross-feature behavior this selection depends on and where it is committed, or None>

## Sizing table  <!-- only when sizing was run; all numbers from scripts/compute_size.py -->
| # | Scenario | Data & State | Integration | UI/UX | Pts | Size |
|---|---|---|---|---|---|---|

## Feature rollup  <!-- only when sizing was run -->
<nL / nM / nS> — band counts. A total appears only if the PM asked for one, with what it is not.

## Risk flags
- <Large scenario on the critical path, or None — requires sizing>
- <Risk-critical behavior recommended for deferral, with what shipping without it risks>

## Proposed splits
### <original scenario> → <replacement scenarios, with draft Gherkin>

## Decisions needed
1. <numbered, one per slice recommendation, deferral acceptance or split the PM must confirm or correct>
````

Step 7 adds the tagged Gherkin and the copy-ready tracker field updates; Step 8 follows the write-back protocol.

## Batch mode (non-interactive corpus sizing)

The complete assistant message must parse as one JSON object. Do not put it in
a Markdown fence or add an introduction, explanation, or trailing question.
This output contract persists on a bare “proceed”; only a user request to leave
batch mode changes it. Report judgments only; the computation script owns sums.

`aipos-feature-map` (or a script) calls this when a corpus needs size badges. Same rules as refine's batch mode: skip every pause, emit a single raw JSON object and nothing else, one feature per invocation — batching degrades every verdict. Batch mode **never writes to a tracker** and never applies tags; it sizes and recommends, and the caller renders recommendations as recommendations.

Batch mode persists until the caller explicitly changes the task. A bare
“proceed” or “continue” does not switch to interactive slicing, authorize tag
changes, or invite a tracker write-back. Every reply remains one raw JSON object:
no introduction, Markdown fence, decision questions, or write-back offer. The
fenced schema below documents the shape; its fence is not part of the output.
If there is no new input, return the existing batch verdict without adding work.

Emit dimension judgments only — no points, no bands, no totals. The caller runs `scripts/compute_size.py`, which owns all arithmetic. This is deliberate: a schema with no total field cannot carry a wrong total.

### Batch output schema

```json
{
  "key": "AI-124",
  "scenarios": [
    {
      "rule": "Business rule text, or null",
      "name": "Scenario name exactly as in the spec",
      "dimensions": {"dataState": 2, "integration": 1, "uiSteps": 2},
      "notes": {"dataState": "Max 120 chars, grounded in the scenario text.",
                "integration": "…", "uiSteps": "…"},
      "taggedSlice": null,
      "recommendedSlice": "mvp",
      "sliceRationale": "Max 150 chars, citing a rubric indicator.",
      "splitHint": "Max 150 chars, only when the scenario looks oversized; else null"
    }
  ],
  "notes": "Optional feature-level caveat, max 200 chars"
}
```

`taggedSlice` is the slice already tagged in the spec (`mvp` | `v1` | `v2` | null) — read it, never invent it. `recommendedSlice` is this skill's MoSCoW judgment and is always labeled a recommendation downstream. Cover every scenario in the feature; a scenario you cannot size still appears, with the uncertainty in its notes.

## Guardrails

Do not:

- Apply slice tags or write to a tracker without the PM's explicit confirmation
- Total dimension points by impression — `compute_size.py` owns the arithmetic
- Present a point total or a scenario count as a cost, duration or delivery forecast
- Require sizing before scope can be discussed — the diagnostic is optional, the selection is not
- Defer a scenario's required authorization, recovery or audit behavior to a later slice than the scenario it serves
- Retag a scenario that an approved baseline already selected — propose the change instead
- Describe a `@v2` scenario as scheduled, queued, or committed
- Present batch recommendations as decisions
- Size a feature whose Gherkin is too weak to read — route to `aipos-feature-refine`
- Invent scenarios, context, or integrations the spec does not contain
- Let a size argument rewrite product intent — splitting restructures scenarios, it does not change what they promise
- Lose a rule association, a background, an Examples row, an outcome, a boundary case or an identifier in a split
- Defer risk-critical behavior because its tag category usually lands later
- Create or delete tracker records
- Conflate size with quality — a well-written scenario can be Large, a sloppy one Small

Always:

- Ground every dimension note in the scenario's own text
- Run `compute_size.py` before presenting any number
- Preserve existing tags this skill does not own
- Re-size the pieces after any split, and state what moved where
- Preserve `@rule:` / `@scenario:` identifiers through splits and retagging, recording any new identity a split creates
- Flag Large + `@mvp` combinations explicitly
- Show the exact write-back preview before any tracker write, and verify by reading back

## Related

| Skill | Owns | Relationship |
|---|---|---|
| `aipos-feature-refine` | Spec quality and the 3 Amigos conversation | Refine first when the Gherkin is too weak to size; slicing revises structure, refine revises meaning |
| `aipos-feature-readiness` | The repo-side Development Token gate | Slice tags ride along in `acceptance.feature` and survive the handoff; readiness can gate per slice |
| `aipos-feature-map` | The corpus view | Calls this skill's batch mode to badge many features; renders the rollup this skill's script computes |
