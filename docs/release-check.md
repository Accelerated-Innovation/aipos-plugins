# AIPOS 1.0.1 candidate verification

**Status:** PE1–PE5 changes are in [draft PR #33](https://github.com/Accelerated-Innovation/govkit-plugins/pull/33). Consolidation [PR #31](https://github.com/Accelerated-Innovation/govkit-plugins/pull/31) and label-clarification [PR #32](https://github.com/Accelerated-Innovation/govkit-plugins/pull/32) are merged. This candidate has not been merged, tagged, or published. Release sign-off remains open for the findings below.

**Tested source:** `767398a22728299a88407dc05b8bb26566894a2e` on `codex/plugin-evaluation-followups`, plugin **1.0.1**. The committed evidence records per-trial input fingerprints and installed-file hashes. Baseline skill bodies come from `c622ec4`; both comparison cohorts use the final corrected cases.

One `aipos` plugin contains eleven focused skills. Names and routing descriptions are unchanged from the accepted consolidation catalog. Pillars remain the workflow model; `.govkit/` paths, bundled script behavior, event contracts, and authority boundaries are preserved.

## Verification

| Check | Actual result |
|---|---|
| Offline suite | **427 passed, 5 skipped**; absent file-fixture directories account for the skips |
| Hosted checks | Pytest and manifest jobs pass at `83e5fa1`; final evidence commit is checked separately |
| Marketplace, plugin, skill structure | Both manifests and all eleven skills validate |
| Matched coaching comparison | **106/141 baseline; 122/141 candidate**, 47 cases × three repetitions, Opus 5 / Sonnet 5, 32,000-token ceilings |
| Routing | Historical **159/159**, all 102 critical trials; current catalog is byte-identical, so no new routing run claimed |
| Native selection | Historical **6/6**; fresh 1.0.1 installation independently loads eleven skills |
| Metrics fixture | All five deterministic checks pass; ten events, scores 100/15, trailer control, canaries absent, no readiness token |
| Native metrics cases | **3/3**, with nine independent runtime checks each; inputs unchanged |
| Live quarterly planning | **3/3** final controlled rehearsals through actual MCP; ten read calls each; unknown state stays unknown |
| Authority pilot | **12/12 executed checks pass**; nine other pilot entries explicitly not run by that harness |
| Authority → readiness | Actual current authority yields approved; actual invalidation plus fresh read yields blocked; local score/completeness are synthetic premises |
| Browser | Actual map inspected: L1/L2/L3, handoff, canonical references, uncovered items, filter, diagnostics; zero console warnings/errors |
| Fresh installation | One enabled `aipos@aipos` **1.0.1**, eleven skills, matching runtime source files, disposable profile |
| Case retention | Forty original cases retained; **50 total = 47 text + 3 separately exercised runtime cases** |

The [follow-up report](evaluations/2026-09-20-plugin-evaluation-followups.md) contains per-skill and per-case outcomes, fixture decisions, failed earlier revisions, and limitations. Its [coaching JSON](evaluations/2026-09-20-plugin-coaching-results.json) and [runtime JSON](evaluations/2026-09-20-plugin-runtime-results.json) retain individual verdicts, hashes, and observed checks. The prior [September 19 report](evaluations/2026-09-19-aipos-live-evaluation.md) remains historical evidence, not the new comparison baseline.

## Release disposition

PE1, PE2, and the scoped PE4 integrations are complete. PE3 remains open with **19 strict coaching failures**; PE5's review is performed, but release acceptance remains open. The material misses concern evidence/inference labeling and unknown values, GO-to-commitment handoff completeness, a proposed evaluation scenario without a stated Rule, and deferral of required validation in one release-scope proposal. Smaller formatting and coaching omissions also remain. All are retained in the report and JSON; no passing aggregate is used to waive them.

Implementation and evaluation are not a claim that every coaching rubric passes. Text-only trials establish produced responses, not actual writes. Runtime checks use synthetic fixtures and real transports/services with in-memory stores; they do not establish durable production behavior or application conformance. The readiness integration supplies local review premises rather than running a complete native review. Browser coverage is one inspected viewport. Partial transport-failed calls have error records but no recoverable full trace/usage.

No tracker or aggregator transfer, real-user plugin change, production authority mutation, merge, tag, or publication was performed for this candidate. Temporary servers were stopped and their credentials removed. The [plan](plans/2026-09-19-aipos-plugin-consolidation.md#current-slice-status-september-20) records slice status; the [rollout guide](rollout.md) remains the installation procedure. Merge and publication require authorization for that action.
