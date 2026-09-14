---
name: govkit-feature-slice
description: Size and slice a feature's Gherkin scenarios for release planning — score every scenario on the Scenario Complexity Matrix (Data & State, Integration, UI/UX Steps), map scenarios to release slices with MoSCoW (@mvp, @v1, @v2 tags), recommend splits for oversized scenarios, and write the tagged spec back to the tracker after the PM confirms. Tool-agnostic; works with any tracker (Jira, Aha!, Azure DevOps, markdown). Trigger whenever the user asks to slice a feature, size scenarios or estimate how big a feature is, plan MVP versus V1 versus V2, tag scenarios for releases, apply MoSCoW, find the smallest shippable version, or asks which scenarios could wait for a later release — even if they don't say GovKit or "slice". Also provides a non-interactive batch sizing mode that emits one JSON verdict per feature; govkit-feature-map calls it to put size badges on a whole corpus.
---

# GovKit Feature Slice — Scenario Sizing and Release Slicing

## Purpose

Help a Product Manager answer two questions about one feature, scenario by scenario:

1. **How big is each scenario?** — scored on the Scenario Complexity Matrix, three dimensions at 1–3 points each.
2. **Which release does each scenario belong to?** — mapped with MoSCoW onto `@mvp` / `@v1` / `@v2` tags.

Size and slice are orthogonal judgments and this skill keeps them separate: a scenario's size never decides its slice, but the *combination* is the risk signal — a Large scenario on the MVP critical path is the first thing a release plan has to deal with, and this skill exists to surface it before coding starts.

This skill is not a quality review. If the Gherkin is too weak to judge — tautological scenarios, unclear intent, missing rules — slicing it is premature; say so and point to `govkit-feature-refine`. You cannot size what you cannot read.

## Tool-agnostic design

Same abstract roles as `govkit-feature-refine`: the **generator** is whatever produced the spec, the **tracker** is wherever the feature fields live (Azure DevOps, Jira, Aha!, Linear, a markdown file). Named tools appear only as adapter examples.

## Key terms

- **Size** — a scenario's points (3–9, sum of three dimension judgments) and band: Small (3–4), Medium (5–7), Large (8–9).
- **Slice** — the release a scenario belongs to, expressed as a Gherkin tag: `@mvp`, `@v1`, or `@v2` (V2 or later).
- **Split** — rewriting one oversized scenario into smaller scenarios, each independently sizeable and sliceable.
- **Rollup** — the feature-level summary: band counts plus total points, rendered as e.g. `2L / 5M / 3S · 41 pts`, and points per slice.

## Operating principle

**The skill recommends slices. The PM decides.**

Sizing is analysis and can be offered freely. Slice tags are release commitments in the making — they land in the spec only after the PM has confirmed or corrected each recommendation. Never present a recommended slice as a decision, and never write anything to a tracker without the explicit confirmation step in `references/tracker-writeback.md`.

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

- Reviewing spec quality or issuing a Development Token recommendation (`govkit-feature-refine`)
- Validating a repo package before coding (`govkit-feature-readiness`)
- Mapping a whole epic (`govkit-feature-map`, which calls this skill per feature)
- Story-point estimation or velocity forecasting — complexity points are not story points
- Creating or deleting tracker records; write-back is update-in-place only

## Inputs

Accept any input form `govkit-feature-refine` accepts: pasted tracker fields, markdown from a tracker, a draft `acceptance.feature`, a `feature_source.md`, or a single feature object in `govkit-feature-map`'s `features.json` schema (field mapping: `rules[].rule` = business rules, `rules[].scenarios[]` = the Gherkin, `rules[].scenarios[].tags[]` = existing tags).

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

### Step 2: Size every scenario

For each scenario, judge the three dimensions per `references/slicing-rubric.md` — Data & State, Integration, UI/UX Steps, each an integer 1–3 — with a note per dimension grounded in the scenario's own text. Never invent context the spec does not contain; if a dimension is unknowable from the spec, score what the text supports and record the uncertainty in the note — an unknowable dimension is itself a spec gap worth reporting.

Write the judgments to a sizing JSON (Batch mode schema below) and run:

```bash
python scripts/compute_size.py sizing.json -o sizing_computed.json
```

The script computes points, bands, the feature rollup, per-slice points, and risk flags, and validates every judgment. Present numbers only from its output. If the script cannot be run in the current environment, do the arithmetic explicitly and show it — never total by eye.

### Step 3: Recommend a slice per scenario

Apply the MoSCoW mapping from the rubric. The MVP test is strict: *can the feature fundamentally function without this scenario?* If yes, it is not `@mvp`. Give a one-line rationale per recommendation, citing the rubric's Gherkin indicators (happy path, error pathway, third-party integration, …).

**Never defer risk-critical behavior on the strength of a tag category alone.** "Error pathway", "edge case" and "permission" are indicators of where a scenario usually lands, not a licence to postpone. A scenario that guards authorization, privacy, safety, regulatory compliance, financial correctness or data loss is judged on the consequence of shipping without it — and that consequence often puts an "edge case" squarely in the MVP. When a recommendation defers such a scenario, say what shipping without it risks and make the PM accept it explicitly rather than letting a category do the deferring silently.

### Step 4: Flag risk and propose splits

Two things must be surfaced before the PM decides:

- **Large scenarios on the critical path.** A Large `@mvp` scenario means the smallest shippable version contains the riskiest work. Propose a split, or make the PM accept the risk explicitly.
- **Any Large scenario.** Per the rubric, 8–9 points means "consider slicing this scenario down further." Propose concrete splits using the rubric's split patterns, with draft Gherkin. After a split, re-size the pieces — splits should land Small or Medium, and a split that doesn't shrink anything is not a split.

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

### Step 5: Pause for the PM's decisions

Present the sizing table, the rollup, the recommendations, and the proposed splits — then STOP. Ask the PM to confirm or correct each slice recommendation and each split. Do not emit tagged Gherkin or tracker updates until they have. If the PM overrides a recommendation, take the override without argument and record it; the PM owns release intent.

### Step 6: Emit the tagged spec

After confirmation, produce the revised Gherkin with tags on the line above each scenario (slice tag first, then size tag), preserving all existing tags this skill does not own. Emit copy-ready tracker field updates in the same shape `govkit-feature-refine` uses.

### Step 7: Offer write-back

If a tracker MCP is connected, offer to update the record in place, following `references/tracker-writeback.md`: exact preview, named destination, one explicit yes, read-back verification. If no MCP is available, the copy-ready block from Step 6 is the deliverable.

## Output format (interactive)

Steps 2–4 present as:

````markdown
# Scenario Sizing and Slicing — <key or title>

## Sizing table
<!-- All numbers from scripts/compute_size.py output -->
| # | Scenario | Data & State | Integration | UI/UX | Pts | Size | Recommended slice | Why |
|---|---|---|---|---|---|---|---|---|

## Feature rollup
<nL / nM / nS · N pts> — MVP <n> pts · V1 <n> pts · V2 <n> pts · untagged <n> pts

## Risk flags
- <Large scenario on the critical path, or None>

## Proposed splits
### <original scenario> → <replacement scenarios, with draft Gherkin and re-sized points>

## Decisions needed
1. <numbered, one per slice recommendation or split the PM must confirm or correct>
````

Step 6 adds the tagged Gherkin and the copy-ready tracker field updates; Step 7 follows the write-back protocol.

## Batch mode (non-interactive corpus sizing)

`govkit-feature-map` (or a script) calls this when a corpus needs size badges. Same rules as refine's batch mode: skip every pause, emit a single raw JSON object and nothing else, one feature per invocation — batching degrades every verdict. Batch mode **never writes to a tracker** and never applies tags; it sizes and recommends, and the caller renders recommendations as recommendations.

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
- Present batch recommendations as decisions
- Size a feature whose Gherkin is too weak to read — route to `govkit-feature-refine`
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
| `govkit-feature-refine` | Spec quality and the 3 Amigos conversation | Refine first when the Gherkin is too weak to size; slicing revises structure, refine revises meaning |
| `govkit-feature-readiness` | The repo-side Development Token gate | Slice tags ride along in `acceptance.feature` and survive the handoff; readiness can gate per slice |
| `govkit-feature-map` | The corpus view | Calls this skill's batch mode to badge many features; renders the rollup this skill's script computes |
