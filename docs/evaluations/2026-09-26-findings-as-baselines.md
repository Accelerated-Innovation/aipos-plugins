# Study findings as canvas baselines — 2026-09-26

Increment 4 of the cross-repo study-findings plan (discovery-engine
`docs/backend/architecture/migrations/2026-09-pdg-study-findings.md`), and the plugin side of
product-strategy gap 2 ([plan](../plans/2026-09-24-aipos-product-strategy.md#remaining-integration-gaps)).
The engine now stores a study finding and returns its measurement on `list_evidence` (engine
features 17 and 18). Until now a canvas baseline could come from the graph only as an excerpt that
states it, and the one ReOps "result" the mock graph held was a `study_outcome` row the engine can
never return.

## Change

- **Mock graph.** The triage problem's impossible `study_outcome` row becomes a real
  `study_finding` from the same time study (`reops:study-ts-07:fnd-0002`). Its measurement is the
  misrouted-ticket rate: 32% of 400 tickets, by log analysis. Every `list_evidence` row carries
  `measurement` (`null` except on the finding), and `list_evidence` uses the engine's feature 18
  description. The finding is deliberately *not* the triage-time figure: triage time stays an
  evidence GAP, so the existing cases keep their premise. It also gives the rubric's
  candidate-baseline example a real instance, because first-time-correct routing is its
  complement.
- **Verifier.** An `[E]` numeric fact citing a finding must state the finding's value
  (`FINDING_MISMATCH`). An `[E]` metric baseline must be in the finding's unit where the canvas
  unit is recognisable (`FINDING_UNIT_MISMATCH`). A finding with `measurement: null` backs no
  number (`FINDING_UNREADABLE`). An `[I]` derivation (a complement, say) is not held to the
  finding's number.
- **No transcription from ReOps** (open question 3, decided 2026-09-26). A `[T]` figure citing a
  `reops:` record is refused (`T_FROM_REOPS`), and the to-do asks for the finding to be recorded in
  ReOps. `[T]` remains for other sources.
- **References.** `canvas-schema.md`, `opportunity-source.md` (a new *Findings as baselines*
  section), `panel-rubrics.md` and `SKILL.md`.
- **Evals.** Cases 1 and 2 are updated for the finding. Three cases are new:
  - `a-finding-that-is-the-metric-becomes-the-baseline`
  - `a-related-finding-is-a-candidate-not-the-baseline`
  - `a-figure-read-off-a-reops-page-is-not-transcribed`

  The eval transcripts are regenerated from the mock, and the canvases are migrated with the
  verifier passing on each.

`pytest`: 638 passed, 5 skipped.

## Results

Subject `claude-opus-5`, judge `claude-sonnet-5`, 32,000-token ceilings, three repetitions.

The whole `aipos-solution-framing` suite (now 12 cases) scored **26/36** on the first run. The
runs found gaps in the new wording and in two new rubrics (below). After those fixes, the affected
cases were re-run:

| Case | First run | After fixes |
|---|---|---|
| `reads-the-graph-before-asking` | 2/3 | **3/3** |
| `remembered-figure-becomes-an-assumption-beside-a-gap` | **3/3** | — |
| `a-figure-read-off-a-reops-page-is-not-transcribed` | **3/3** | — |
| `a-related-finding-is-a-candidate-not-the-baseline` | 1/3 | **2/3** |
| `a-finding-that-is-the-metric-becomes-the-baseline` | 1/3 | **2/3** |
| `proceed-is-not-a-go-ahead-to-build` | 2/3 | 2/3 |
| `proceed-unavailable-while-baseline-is-a-gap` | **3/3** | — |
| the other five cases | 11/15 | — |

Taking each case's latest run, the suite stands at about **29/36**. The first run of the whole
suite was 26/36.

## What the runs found

**My new text said "can support Proceed" without the owner.** In two of three runs of the
finding-baseline case, the model said the baseline "makes Proceed available" without calling it a
recommendation. 1.3.3's rule is that Proceed is recommended to a named owner, never a decision
made. `panel-rubrics.md` and `opportunity-source.md` now repeat it where findings are introduced.

**The candidate path lacked its discipline.** The related-finding case asked several
sub-questions and left the interim state unstated. The text now says to ask one question — do
the two count the same things, over the same population, the same way? — and to keep the
baseline a GAP until the PM confirms.

**Two rubrics were too strict, and were corrected.**

- Case 1 required the finding to be named only as a candidate. But the finding *can* be a
  baseline if the PM chooses the misrouting rate as a metric, which the skill's own rule says. The
  assertion now tests that nothing is adopted before the metrics are chosen.
- Case 10 required Proceed to go "to a named owner" at panel 3, but the owner is named at panel 6.
  The assertion now tests that Proceed is framed as a recommendation.

## Code review follow-up

Qodo's review of PR #46 found three gaps in the verifier, and all three are fixed with tests
written first:

- **Units written as phrases skipped the check.** `% of tickets` (the fixture's own routing unit)
  and `minutes per ticket` were not recognised, so an `[E]` baseline in an incompatible unit that
  happened to share the finding's number passed. The verifier now reads a `%` anywhere as percent,
  a time unit by its first word, and an ISO 4217 code or currency symbol as currency.
- **NaN and Infinity counted as numbers.** NaN compares unequal to everything, so it slipped past
  the finding check and into the computed block. `is_num` now requires a finite number, so such a
  figure is `NOT_NUMERIC` everywhere. The Proceed guard also requires a numeric primary baseline:
  a NaN `[E]` baseline had still reported Proceed as available.
- **Findings inflated source breadth.** The engine's lineage lists each finding as
  `reops:<study>:<finding>`, so two findings of one study counted as two sources and could hide
  `SINGLE_SOURCE`. The verifier now counts a study's findings as one source. The mock keeps
  matching the engine.

`pytest`: 646 passed, 5 skipped.

## Remaining misses

- `a-finding-that-is-the-metric-becomes-the-baseline`, 1 of 3: the model typed the derived 16%
  target instead of leaving it to the verifier. This is an existing skill rule ("numbers are
  computed, never typed") that the model breaks here, not a finding rule. It is left visible
  rather than loosened.
- `a-related-finding-is-a-candidate-not-the-baseline`, 1 of 3: the confirmation is still bundled
  as several questions.
- Known misses from earlier records:
  - `checks-a-hand-made-canvas-before-it-is-shared`: the 166-vs-167 rounding point, recorded as
    low reliability in the [eval-debt record](2026-09-25-eval-debt.md).
  - `says-promotion-before-facilitating`: drafts panel content before the gating answer.
  - `proceed-is-not-a-go-ahead-to-build` and `write-back-names-destination-and-hands-over-attachment`:
    one miss each, neither about findings.

Not re-run: `aipos-rapid-validation` and `aipos-feature-create`. Their triage cases do not read
the study row, and their references are unchanged.

Raw results and traces are in `.claude/hillclimb/` (gitignored).
