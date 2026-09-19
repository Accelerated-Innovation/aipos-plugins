# AIPOS 1.0.0 candidate verification

**Status:** Pushed to [draft PR #31](https://github.com/Accelerated-Innovation/govkit-plugins/pull/31). Routing meets the acceptance target. Coaching has unresolved findings, so release sign-off remains open. No merge, tag, or publication has occurred.

**Tested source:** `a1e2522` on `codex/aipos-plugin-consolidation`, plugin **1.0.0**. Subsequent evidence-only commits do not change plugin/evaluator inputs. Baseline: `9ec174d9a9d740fddb928f7367cf6e635d637499`.

One `aipos` plugin replaces `aipos-p1`, `aipos-p2`, and `govkit`, with eleven distinct `aipos-*` skills. Pillars remain the workflow model; `.govkit/` paths, execution contracts, event fields, scoring, and bundled script behavior are preserved.

## Verification

| Check | Actual result |
|---|---|
| Offline suite | **415 passed, 5 skipped**; skips are absent file-fixture directories |
| Hosted PR checks | Both passed at the tested source; manifest CI uses Claude Code 2.1.199 |
| Marketplace and manifest | Both validate; one entry, one plugin, eleven unique skill IDs, no aliases |
| Live catalog routing | Original **147/159**; candidate **159/159**, including all 102 critical trials |
| Installed-client selection | **6/6** with Claude Code 2.1.274 / Sonnet 5; observed catalog: eleven AIPOS plus seventeen built-in skills |
| Live coaching | **87/135 passed**, **48 not accepted (including four subject truncations)**; 45 cases × three repetitions, Opus 5 subject / Sonnet 5 judge |
| Runtime-dependent metrics cases | Three cases unrun in the text-only harness; not passes |
| Native workflow artifact checks | **4/4**: prepared commitment, deliberately blocked readiness, rendered journey, unsubmitted change proposal |
| Fresh isolated installation | Only `aipos@aipos` 1.0.0 enabled, eleven skills |
| Early-plugin replacement | Three baseline plugins installed, removed, then replaced with AIPOS in a disposable profile |
| Installed resources/scripts | Resource references resolve; seven checks across six scripts passed from a separate project |
| Script preservation | All nine bundled scripts retain executable syntax after normalizing public names and docstrings |
| Case retention | All forty original cases retained; 48 total cases across eleven skills |

The [live evaluation report](evaluations/2026-09-19-aipos-live-evaluation.md) records the configurations, per-case outcomes, fixes, fixture conflicts, raw-evidence locations, and limitations. Its [JSON record](evaluations/2026-09-19-aipos-live-results.json) preserves per-repetition results and fingerprints. The higher judge budget used for two case families is recorded separately; earlier failures and infrastructure errors remain visible.

## Installation and native evidence

Initial installation checks at `ac867c9` used separate configurations under `/private/tmp/aipos-install-eq2hgh0f`; live native checks used `/private/tmp/aipos-live-evals/`. Later live checks resolved the local candidate source; per-skill fingerprints verify the final coaching inputs. Real user installations were not changed. Isolation follows the documented [`CLAUDE_CONFIG_DIR` setting](https://code.claude.com/docs/en/env-vars). The native client resolves this local marketplace to the candidate source; this is not a published GitHub release check.

The four native projects retained every supplied source file byte for byte. Readiness correctly blocked missing behavior/repo context and claimed no product approval. The change proposal is unsubmitted with `decision: null`, and its requested digest matches the proposed file bytes. The renderer produced HTML and reported uncovered behavior without a token. Browser visual QA and live authority-service integration remain unverified.

Local installation evidence remains in `.claude/install-check-results.json`, `.claude/install-inventory.json`, and `.claude/request-assembly/`. Full model traces are gitignored and retained at the locations in the live report.

## Remaining acceptance work

1. Adjudicate and repair the conflicting positive-review fixtures, preserving rejection of actual contradictions and missing approval behavior.
2. Add stage-aware evaluation interactions for longer interviews; distinguish unanswered facts from a completed artifact and verify real writes with tools.
3. Address the remaining concrete coaching misses in focused increments and rerun the affected cases, retaining previous outcomes.
4. Exercise the original metrics runtime cases and positive live graph/authority integrations before making claims about those capabilities. Complete browser verification of the generated map where required.
5. Recheck upstream and CI at release review. Merge/publish only under the authorization for that action.

The [plan](plans/2026-09-19-aipos-plugin-consolidation.md#live-verification-and-pr-handoff) tracks these slices. The [rollout guide](rollout.md) supplies the verified remove-old/install-new commands. Routing success is not a substitute for the remaining coaching and integration evidence.
