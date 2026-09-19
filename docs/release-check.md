# AIPOS 1.0.0 candidate verification

**Status:** Implemented locally; not published or ready for release sign-off.
Live routing and coaching acceptance remain open pending an evaluation budget.

**Candidate:** `ac867c9` on `codex/aipos-plugin-consolidation`, plugin version
**1.0.0**. The following record-only commit changes no plugin content.

The candidate replaces `aipos-p1` 0.1.1, `aipos-p2` 0.4.0, and `govkit` 0.17.0
with one `aipos` plugin containing eleven `aipos-*` skills. Descriptions and
handoffs distinguish experiments, artifact authoring, review, scope selection,
visualization, readiness, data generation, and telemetry. Pillars remain the
workflow model. Existing `.govkit/` paths, scoring, token fields, event contracts,
and feature package layouts remain unchanged.

## Completed checks

| Check | Actual result |
|---|---|
| `.venv/bin/python -B -m pytest tests -q -p no:cacheprovider` | **405 passed, 5 skipped**; skips concern absent file-fixture directories, not model results |
| Marketplace and plugin manifest validation | Both passed with Claude Code **2.1.274** |
| Candidate inventory | One catalog entry, one plugin, eleven unique skill IDs; no alias packages |
| Fresh local marketplace installation | One enabled `aipos@aipos` 1.0.0, eleven skills |
| Early-plugin replacement | Installed all three baseline plugins, uninstalled them, refreshed the local marketplace, installed AIPOS; only AIPOS remains enabled |
| Installed resources | Runtime files match the candidate byte for byte; all skill resource references resolve |
| Installed script checks from a separate project | Seven checks passed across six scripts: ingest, render, readiness, batch token refusal, proposed change package, metrics, sizing |
| Script preservation | All nine bundled Python scripts have unchanged executable syntax after normalizing skill names and removing docstrings |
| Behavior fixture retention | All 40 baseline cases retained; 48 total cases across eleven skills |
| Behavior request assembly | Dry runs succeeded for all eleven skills; three original metrics cases need a tool-enabled runtime harness |
| Routing request assembly | Frozen baseline and renamed candidate assemble correctly; 53 cases, including six held-out paraphrases |
| Documentation | Forty local links checked; whitespace/diff check passed |
| Upstream | `origin/main` still `9ec174d9a9d740fddb928f7367cf6e635d637499` at final integration check on 2026-09-19 |

Installation checks used separate configurations under
`/private/tmp/aipos-install-eq2hgh0f` and an unrelated temporary project. No real
user installation was changed. Configuration isolation follows the documented
[`CLAUDE_CONFIG_DIR` setting](https://code.claude.com/docs/en/env-vars).
The native inventory reported eleven skills, zero agents/hooks/MCP/LSP servers,
and an estimated 852 tokens of always-on metadata. That estimate is not measured
model usage or evidence of correct skill selection.

Local evidence is in `.claude/install-check-results.json`,
`.claude/install-inventory.json`, `.claude/request-assembly/`, and the temporary
project. These generated records are gitignored. The isolated check refreshed a
local-path marketplace, not a published GitHub release. CI still pins Claude Code
2.1.199; that hosted CI version was not separately executed in this local check.

## Remaining acceptance work

No paid model calls were made for this candidate. There are **no current live
routing or coaching pass rates**. Fixture counts and dry runs must not be
reported as such.

1. Choose a model, spending limit, and bounded call/token settings. Replay the
   unchanged catalog from `.claude/routing/baseline/inputs.json`; the renamed
   candidate snapshot is `.claude/routing/candidate/inputs.json`. Compare the same
   cases and model with three repetitions, mapping the old public skill IDs to
   their new identities. Historical snapshots keep their original names.
2. Run candidate development and held-out routing cases. The acceptance target is
   at least 90% allowed outcomes overall and every critical case correct in every
   repetition. Preserve complete traces, failures, errors, and missing results.
3. Run the affected coaching cases with a separate judge model. Exercise the three
   runtime-dependent metrics cases with a tool-enabled fixture environment or
   explicitly leave their dependent claims unaccepted.
4. Check native client selection with the installed plugin, including the actual
   competing skill catalog. Walk opportunity-to-prepared-commitment,
   reviewed-package-to-readiness, journey-to-view, and committed-change-to-proposal
   handoffs. Deterministic script checks do not establish agent orchestration.
5. Resolve any critical misroutes, rerun affected checks, and recheck upstream and
   CI before normal review/release. No PR, push, merge, tag, or publication occurred
   in this implementation task.

The [routing guide](../evals/routing/README.md) documents the evaluator and its
limits; the [behavior guide](../evals/README.md) documents coaching evaluations.
The [rollout guide](rollout.md) provides the verified remove-old/install-new
commands. The [plan](plans/2026-09-19-aipos-plugin-consolidation.md#implementation-evidence)
keeps model-dependent increments partial until their acceptance evidence exists.
