# AIPOS 1.0.1 candidate verification

**Status:** PE1–PE5 changes are in [draft PR #33](https://github.com/Accelerated-Innovation/govkit-plugins/pull/33). Consolidation [PR #31](https://github.com/Accelerated-Innovation/govkit-plugins/pull/31) and label-clarification [PR #32](https://github.com/Accelerated-Innovation/govkit-plugins/pull/32) are merged. This candidate has not been merged, tagged, or published. Substantive coaching acceptance is complete; the remaining full-rubric follow-ups and evaluator adjudications are recorded below. Merge/publication remains a separate decision.

**Tested source:** `0000375fdf358797011855ea66671e5774f171a1` on `codex/plugin-evaluation-followups`, plugin **1.0.1**. The latest closure comparison starts at PR #33 candidate `c2e3b8d`; the earlier `c622ec4` comparison remains historical. Per-trial fingerprints, original/clarified judgments and installed-file hashes are committed in the evidence.

One `aipos` plugin contains eleven focused skills. Names and routing descriptions are unchanged from the accepted consolidation catalog. Pillars remain the workflow model; `.govkit/` paths, bundled script behavior, event contracts, and authority boundaries are preserved.

## Verification

| Check | Actual result |
|---|---|
| Offline suite | **427 passed, 5 skipped**; absent file-fixture directories account for the skips |
| Hosted checks | Pytest and manifest jobs are required on the final pushed PR head; see PR #33 checks |
| Marketplace, plugin, skill structure | Both manifests and all eleven skills validate |
| Latest matched coaching comparison | **81/87 → 87/87 substantive; 71/87 → 73/87 full rubric**, 29 affected cases × three repetitions; same subjects, versioned criteria, Opus 5 / Sonnet 5, 32,000-token ceilings |
| Unchanged coaching evidence | 75/78 full-rubric passes, current fingerprints verified; combined full result **146/165 → 148/165**, with 17 full-rubric misses retained |
| New installed-plugin coaching | **3/3** final native prompts pass inspected substantive checks; one execution each, actual read-only tool calls |
| Routing | Historical **159/159**, all 102 critical trials; current catalog is byte-identical, so no new routing run claimed |
| Native selection | Historical **6/6**; fresh 1.0.1 installation independently loads eleven skills |
| Metrics fixture | All five deterministic checks pass; ten events, scores 100/15, trailer control, canaries absent, no readiness token |
| Native metrics cases | **3/3**, with nine independent runtime checks each; inputs unchanged |
| Live quarterly planning | **3/3** final controlled rehearsals through actual MCP; ten read calls each; unknown state stays unknown |
| Authority pilot | **12/12 executed checks pass**; nine other pilot entries explicitly not run by that harness |
| Authority → readiness | Actual current authority yields approved; actual invalidation plus fresh read yields blocked; local score/completeness are synthetic premises |
| Browser | Actual map inspected: L1/L2/L3, handoff, canonical references, uncovered items, filter, diagnostics; zero console warnings/errors |
| Fresh installation | One enabled `aipos@aipos` **1.0.1**, eleven skills, matching runtime source files, disposable profile |
| Case retention | Forty original cases retained; **58 total = 55 text + 3 separately exercised runtime cases** |

The [substantive closure report](evaluations/2026-09-20-substantive-closure.md), [matched results](evaluations/2026-09-20-substantive-closure-results.json), and [native results](evaluations/2026-09-20-substantive-native-results.json) are the current coaching evidence. The prior [follow-up report](evaluations/2026-09-20-plugin-evaluation-followups.md) and [runtime JSON](evaluations/2026-09-20-plugin-runtime-results.json) retain the earlier comparison and PE4 integrations; those integrations were not rerun for instruction-only changes.

## Release disposition

PE1, PE2 and scoped PE4 are complete. PE3 substantive acceptance is complete under the versioned profile, with all 87 trials passing. The affected full rubric still has 14 failed trials: coaching/detail omissions and documented evaluator interpretations. Three older presentation/coaching misses remain in unchanged skills. All are retained; this is not an all-rubrics-pass claim. PE5 review is complete, with merge and publication awaiting the release decision.

Implementation and evaluation are not a claim that every coaching rubric passes. Text-only trials establish produced responses, not actual writes. Runtime checks use synthetic fixtures and real transports/services with in-memory stores; they do not establish durable production behavior or application conformance. The readiness integration supplies local review premises rather than running a complete native review. Browser coverage is one inspected viewport. Partial transport-failed calls have error records but no recoverable full trace/usage.

No tracker or aggregator transfer, real-user plugin change, production authority mutation, merge, tag, or publication was performed for this candidate. Temporary servers were stopped and their credentials removed. The [plan](plans/2026-09-19-aipos-plugin-consolidation.md#current-slice-status-september-20) records slice status; the [rollout guide](rollout.md) remains the installation procedure. Merge and publication require authorization for that action.
