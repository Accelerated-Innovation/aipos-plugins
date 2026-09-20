# PE3 substantive closure — September 20, 2026

**Disposition:** the remaining substantive findings are closed under the versioned
acceptance profile: **81/87 baseline → 87/87 candidate trials**. The original full
rubrics remain **71/87 → 73/87** for these same subjects. Fourteen full-rubric misses
remain; they are described below, not relabeled as full-rubric passes. PR #33 remains
unmerged and unpublished; PE5's release action is a separate decision.

**Tested source:** `0000375fdf358797011855ea66671e5774f171a1`, plugin **1.0.1**. The starting baseline is PR #33's
`c2e3b8d4d848e9772dcc7802cc8521eb36fdd4ff`, not the older consolidation baseline.
The [prior report](2026-09-20-plugin-evaluation-followups.md) and its results remain
the record of that earlier checkpoint.

## Implemented increments

1. **Evidence and unknowns.** Distinguish an observation from a source's interpretation
   or unmeasured estimate. Remove the interview template's adopted sample default.
   Keep unknown quantities unknown, and connect repeated quantitative claims to supplied
   source identifiers without claiming an independent read of underlying records.
2. **GO handoff.** Produce qualified selected behavior, an immutable revision, exclusions
   and a classified unresolved register. Missing selection routes to authoring/refinement
   before commitment. Preserve exact record identifiers and distinguish prepared,
   submitted/awaiting decision and recorded approval. Scope assembly does not validate
   the solution or establish that a planning mandate exists. Honor existing no-save scope.
3. **Grounded scenarios.** Reference the canonical outcome. Keep unsupported policies
   and incomplete opportunity scenario candidates outside acceptance Gherkin. Preserve
   known quality Rules and their evaluation coverage; a prototype number is not policy.
4. **Complete release scope.** Apply the selected journey's Rules/NFRs before prioritizing
   optional work. Retain administrative validation boundaries as well as authorization
   and other required controls. A stubbed integration is an engineering increment,
   not a shippable real-payment outcome under an unchanged contract.

These are focused instruction/reference changes in three skills. Names, descriptions,
both manifests and the other eight subject packages remain byte-identical to the
starting candidate. Bundled scripts and authority/runtime contracts are unchanged.

## Matched assessment

The affected set is **29 cases × three repetitions**, including eight new synthetic
variations added before coaching edits. Opus 5 subjects and Sonnet 5 judges use
32,000-token ceilings. The eight new variations have fresh baseline subjects;
older baseline subjects are reused only after exact package, fixture, conversation
and model verification. Final candidate subjects are fresh for their final skill
revision. No completed failed subject is rerolled under unchanged inputs.

| Skill | Baseline full | Candidate full | Baseline substantive | Candidate substantive |
|---|---:|---:|---:|---:|
| aipos-feature-create | 18/24 | 20/24 | 22/24 | 24/24 |
| aipos-feature-slice | 23/24 | 24/24 | 21/24 | 24/24 |
| aipos-rapid-validation | 30/39 | 29/39 | 38/39 | 39/39 |


Each full/substantive pair grades the **same subject transcript**; the collector checks
their hashes are identical. The [acceptance profile](../../evals/substantive-acceptance.json)
states the substantive bar, and the [runner guide](../../evals/README.md#separate-substantive-acceptance-assessment)
documents reproduction. The [results JSON](2026-09-20-substantive-closure-results.json)
preserves all 348 matched assessment rows, fingerprints, trace hashes, earlier revisions,
original judgments and every repetition. There are no transport errors, missing final
trials or truncated final subjects in this closure run.

All **58 repository cases** remain: 55 text cases and three separately exercised runtime
cases. The 40 original cases are retained. For the eight unchanged skills, all 78 existing
text-trial fingerprints match current inputs; their full-rubric result remains 75/78.
Combining that verified reuse with the affected set gives **146/165 → 148/165** full-rubric
passes. That is not a fresh all-skill run, nor an all-catalog substantive score. The prior
runtime/integration results retain their original dates and limitations.

## Evaluator corrections, with original results retained

Version 1 of the substantive profile was frozen at `f3419ce` before coaching edits.
Four claims in three cases needed documented clarification after source inspection;
the current profile is version 4. Each correction was applied to both baseline and
candidate by regrading the same subjects. None changes the committed selection,
authority, source-fidelity or unknown-value boundary.

- **Slicing, case 4:** the fixture lacks explicit successful-payment and audit-retention
  coverage. Correctly identifying those shippability gaps must not fail a check that
  mistakenly demands declaring the journey complete.
- **Validation, case 7:** describing prototype behavior as lacking agreed policy is a
  valid explanation without repeating a particular aphorism. A named, reasoned item
  explicitly outside this proposed selection pending the human decision also satisfies
  nonselection; the skill need not declare a permanent product exclusion. Silent omission
  or inclusion in committed scope still fails.
- **Validation, case 8:** a reference-only handoff need not copy the 14% telemetry finding.
  If it repeats the number, it must attribute it to PDG-EV-2208. The earlier response
  that repeated the number without that mapping remains a real failure; the later
  response that omitted the number is different.

Separately, before the comparison, the existing full rubric for slicing case 2 was
corrected so a gateway stub is not a shippable payment MVP. Its original baseline
subjects were regraded under that correction; this is not counted as coaching gain.

## Installed-plugin checks

Three final native prompts select the expected owner and meet the inspected substantive
checks: opportunity authoring, administrative-cutoff slicing, and a GO commitment handoff.
These are **one execution per prompt**, using Claude Code / Sonnet 5, not another
three-repetition matched cohort. Actual tool calls are read-only; no write, tracker,
authority-service or aggregator mutation is inferred from generated prose.

Native inspection drove additional fixes for a renamed opportunity ID, confused approval
states, incomplete scenario placement, an open-ended scope override, a false claim that
package assembly validated the solution, and an invented planning mandate. Earlier
responses are retained. A supplemental attribution check also maps the telemetry value
to its supplied source and discloses that underlying source records were not opened.

The [native results JSON](2026-09-20-substantive-native-results.json) contains the final
responses, actual calls, manual check scope, eight earlier records and installed-file
hashes. A fresh isolated profile enables one `aipos@aipos` 1.0.1 installation with eleven
skills; **all 58 runtime files match the source**. Native sessions read development-source
references, whose bytes match the independently checked installed files. The user's
real plugin profile was not changed.

## Remaining full-rubric findings

The affected set still has **14 failed full-rubric trials**:

| Area | Trials | Remaining detail |
|---|---:|---|
| Authoring | 3 | Explicit later-slice metric linkage; a full stub table instead of an MVP-only preview with stated deferral; an explicit intent/size sanity check. Proposed scope remains visible and no write/approval is fabricated. |
| Authoring judge interpretation | 1 | The judge rejects `@genai`/`@evaluation` as classification tags, although both are in the shipped classification table. The raw failure is retained. |
| Validation alternatives/closing | 2 | The funded spike is offered, but the full rubric also expects the viability brief as the immediate alternative/closing handoff and, in one turn, an explicit save offer. The requested artifact and no-save boundary are preserved. |
| Validation presentation | 2 | Extra explanatory text after “none declared”; no mandate values are invented. |
| Validation final-brief detail | 3 | Ledger facts appear outside the exact decision sentence; one final version paraphrases the planning-record entry instead of repeating its earlier copy-ready template. Binding commitment fields and authority limits pass. |
| Validation evaluator interpretation | 3 | The not-selected/pending entry and two reference-only responses fail the original literal rubric; their corrected substantive assessments pass for the reasons above. |

The unchanged skills retain three earlier full-rubric misses: epic closing length,
an omitted explicit estimate invitation, and a refinement-summary heading. These are
coaching/presentation follow-ups, not reopened E1–E5 pilot slices. The overall full rubric
is not green, and no aggregate score erases these findings.

## Verification and limits

- Offline suite: **427 passed, 5 fixture skips**. All eleven skills and both manifests validate.
- Current main was fetched and remains `c622ec4`; it is an ancestor of this branch.
- Historical catalog routing 159/159 and native selection 6/6 remain historical evidence;
  current names/descriptions are byte-identical. The three native checks above are new.
- The prior PE4 metrics, MCP, authority/readiness and browser evidence is unchanged and
  is not reported as rerun here. No merge, tag or publication is part of this closure.

These curated cases guided development; they are regression evidence, not an unseen
statistical holdout or a guarantee across models and production situations. Text-only
subjects establish generated artifacts, not performed writes or real authority. Native
checks use synthetic inputs and read-only tools. Original and clarified evaluator judgments
remain inspectable separately. Hosted CI is checked on the final pushed PR head.

## Per-case matched results

| Skill / case | Baseline full | Candidate full | Baseline substantive | Candidate substantive |
|---|---:|---:|---:|---:|
| feature-create / epic-mode-maps-before-splitting | 2/3 | 2/3 | 3/3 | 3/3 |
| feature-create / stub-creation-requires-explicit-confirmation | 2/3 | 2/3 | 3/3 | 3/3 |
| feature-create / genai-feature-inherits-and-flags-missing-thresholds | 2/3 | 1/3 | 3/3 | 3/3 |
| feature-create / no-tracker-markdown-path-is-complete | 3/3 | 3/3 | 3/3 | 3/3 |
| feature-create / opportunity-mode-drafts-without-epic-story-or-estimate | 0/3 | 3/3 | 1/3 | 3/3 |
| feature-create / unknown-thresholds-and-unmeasured-claims-stay-unknown | 3/3 | 3/3 | 3/3 | 3/3 |
| feature-create / genai-without-quality-policy-does-not-invent-an-acceptance-gate | 3/3 | 3/3 | 3/3 | 3/3 |
| feature-create / stated-quality-rule-still-produces-evaluation-coverage | 3/3 | 3/3 | 3/3 | 3/3 |
| feature-slice / interactive-sizing-recommends-and-pauses | 2/3 | 3/3 | 0/3 | 3/3 |
| feature-slice / large-mvp-critical-path-flagged | 3/3 | 3/3 | 3/3 | 3/3 |
| feature-slice / batch-mode-raw-json | 3/3 | 3/3 | 3/3 | 3/3 |
| feature-slice / first-slice-is-a-complete-journey-not-a-layer | 3/3 | 3/3 | 3/3 | 3/3 |
| feature-slice / required-authorization-cannot-be-deferred-as-an-exception-path | 3/3 | 3/3 | 3/3 | 3/3 |
| feature-slice / cross-feature-prerequisite-and-post-approval-retag-are-surfaced | 3/3 | 3/3 | 3/3 | 3/3 |
| feature-slice / administrative-cutoff-is-part-of-the-selected-contract | 3/3 | 3/3 | 3/3 | 3/3 |
| feature-slice / minimal-release-keeps-controls-and-defers-unrelated-enhancements | 3/3 | 3/3 | 3/3 | 3/3 |
| rapid-validation / mandate-declared-carries-the-ledger | 0/3 | 3/3 | 3/3 | 3/3 |
| rapid-validation / budget-exhausted-routes-to-the-brief-but-builds-what-is-asked | 2/3 | 1/3 | 3/3 | 3/3 |
| rapid-validation / no-mandate-is-legitimate-and-nothing-is-invented | 1/3 | 1/3 | 3/3 | 3/3 |
| rapid-validation / viability-brief-reconciles-the-mandate-and-closes-the-loop | 1/3 | 0/3 | 3/3 | 3/3 |
| rapid-validation / commitment-package-carries-the-exact-selected-behavior | 3/3 | 3/3 | 3/3 | 3/3 |
| rapid-validation / blocking-unknowns-prevent-ready-for-commitment | 3/3 | 3/3 | 3/3 | 3/3 |
| rapid-validation / prototype-behavior-does-not-enter-the-commitment | 3/3 | 2/3 | 3/3 | 3/3 |
| rapid-validation / unverified-claims-and-contradicting-evidence-are-recorded-not-resolved | 3/3 | 1/3 | 3/3 | 3/3 |
| rapid-validation / a-prepared-package-is-never-presented-as-approved | 2/3 | 3/3 | 2/3 | 3/3 |
| rapid-validation / source-attribution-does-not-certify-a-leads-inference | 3/3 | 3/3 | 3/3 | 3/3 |
| rapid-validation / interview-guide-does-not-adopt-a-template-sample | 3/3 | 3/3 | 3/3 | 3/3 |
| rapid-validation / go-handoff-binds-supplied-scope-without-granting-authority | 3/3 | 3/3 | 3/3 | 3/3 |
| rapid-validation / go-without-a-selection-hands-off-authoring-before-commitment | 3/3 | 3/3 | 3/3 | 3/3 |
