# Canvas and viability-brief decision language — 2026-09-25

Product-strategy integration gap 1 ([plan](../plans/2026-09-24-aipos-product-strategy.md#remaining-integration-gaps)).
The Solution Framing canvas's Proceed / Pivot / Park was documented as mapping to the viability
brief's GO / REVISE / NO-GO "without translation", although the canvas decides whether to run a
validation plan before any experiment and the brief decides production investment on the
evidence. The rendered canvas already labelled Proceed "Pilot and validate"; the contracts did not
say so.

## Change

- The canvas recommendation is defined as a **learning** decision (run the plan, rework the
  approach, defer); the brief's as a **production-investment** decision. They no longer map onto
  each other; the brief cites a canvas recommendation as its origin, never its answer. Approval
  authority is unchanged: both remain recommendations to a named owner.
- Carried in `canvas-schema.md`, `panel-rubrics.md` and SKILL.md (`aipos-solution-framing`);
  SKILL.md and the viability-brief template, which gains *Decides* and *Origin* lines
  (`aipos-rapid-validation`); the shared `strategy-handoff.md`; `docs/workflow.md`; and one line
  on the rendered canvas.
- New cases: `proceed-is-not-a-go-ahead-to-build` (solution framing) and
  `canvas-proceed-is-not-a-go` (rapid validation).

## Results

Subject `claude-opus-5`, judge `claude-sonnet-5`, 32,000-token ceilings, three repetitions.

| Check | Result |
|---|---|
| `proceed-is-not-a-go-ahead-to-build` | **3/3**, and 3/3 again after the final wording |
| `canvas-proceed-is-not-a-go` | **3/3** |
| `aipos-rapid-validation`, whole suite | 35/42 — the seven misses are the known full-rubric polish items below |
| `aipos-solution-framing`, whole suite | 22/27 → 23/27, then the two fixes below rerun at 3/3 each |

## What the runs found

**Workshop pacing regressed in 1.3.2.** The set-up rule said the turn's one question becomes
panel 1's first, which pulled workshops into coach pacing. It now depends on the mode: coach asks
panel 1's first question; a workshop takes the panel's questions together with gaps as chips.
Workshop and the three set-up cases: **12/12**.

**Transcription and moving on were implicit.** The rules now say a figure can be transcribed only
when the graph read returned its `record_url`, and that a volunteered figure is recorded beside its
GAP before moving on to the target. `remembered-figure-becomes-an-assumption-beside-a-gap`, which
had failed 5 of 12 trials across runs: **3/3**.

**The new wording displaced an older point.** In `proceed-unavailable-while-baseline-is-a-gap` the
subject explained learning versus production instead of the required "recommended to a named owner,
not a decision made" (2 of 3). The learning point now explicitly adds to the owner point rather
than replacing it: **3/3**.

## Remaining misses

- `aipos-rapid-validation` (7/42): the closing handoff naming the brief, extra text after "none
  declared", ledger facts outside the decision sentence, and reference-only answers. All match the
  full-rubric findings in the [2026-09-20 closure report](2026-09-20-substantive-closure.md#remaining-full-rubric-findings);
  none concern decision language.
- `says-promotion-before-facilitating`, 1 of 3 in one run (asked for pasted tool output); 3/3 in
  the run before.
- `checks-a-hand-made-canvas-before-it-is-shared`, the 166 vs 167 rounding point: the
  low-reliability criterion recorded in the [eval-debt record](2026-09-25-eval-debt.md).

Raw results and traces are in `.claude/hillclimb/` (gitignored).
