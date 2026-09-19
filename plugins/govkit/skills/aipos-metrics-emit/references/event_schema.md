# Event vocabulary — tier1_metrics_catalog v1

All events carry an envelope: `event`, `producer`, `catalog_version`, `schema_version`.
Timestamps are ISO 8601. Every field is repo-relative (org-agnostic law).

## feature.package.snapshot
Emitted per feature directory under `features/`. Feeds **Pair 4** (spec lead time ↔
spec completeness) and **Pair 6** (eval coverage at gate).

| Field | Type | Source |
|---|---|---|
| `feature_id` | string | directory name under `features/` |
| `commit_sha`, `ts` | string | last commit touching `features/<id>/` (git log); falls back to repo HEAD when the feature has no path-specific commit yet. `--validate` fails if neither is available (repo with no commits). |
| `artifacts_present` | map | file existence: acceptance.feature, nfrs.md, plan.md, eval_criteria.yaml, architecture_preflight.md, agent_topology.md |
| `artifacts_valid` | map | parse checks (gherkin ≥1 scenario, prediction block parses, criteria YAML parses) |
| `gherkin_scenario_count` | int | `Scenario:` / `Scenario Outline:` lines, comments excluded |
| `nfr_heading_count` | int | markdown headings in nfrs.md |
| `evaluation_prediction` | object\|null | `first_average`, `virtues_average`, `thresholds_met` from the fenced YAML block in plan.md (schema: `governance/schemas/evaluation_prediction.schema.json`) |
| `eval_criteria_summary` | object\|null | `mode` (llm\|deterministic\|none), `criteria_count`, `tools[]`, `enforce_first`, `enforce_virtues` from eval_criteria.yaml |
| `completeness` | object | rubric result: `score` (0–100), `max`, `components[]` (name, points, awarded, reason) |
| `marker_level` | string\|null | `.govkit/marker.json` → `level` |

### Completeness rubric (Pair 4 quality counterweight)
20 gherkin_scenarios · 10 nfrs · 15 evaluation_prediction_block ·
15 thresholds_met · 15 score_minima (first.average ≥ 4.0 AND virtues.average ≥ 4.0) ·
15 eval_criteria (valid; mode llm requires ≥1 criterion) ·
10 architecture_preflight (required iff marker level = 5; auto-award otherwise).
Score 100 satisfies this metric's completeness rubric (historically called
"gate-ready" for the spec lead-time clock). This metric does not authorize
execution, issue a Development Token, verify product approval, or establish
passing implementation evidence. Later platform artifacts contribute to the
score, so a newly execution-ready package may legitimately score below 100.

## pr.merged
From a PR export (`--prs`). Feeds **Pair 2** (throughput ↔ rework) and **Pair 5**
(review latency ↔ unreviewed merges).
Fields: `pr_id`, `feature_id` (parsed from title/branch `features/<id>` pattern),
`ts_opened`, `ts_ready`, `ts_first_review`, `ts_merged`, `lines_added`,
`lines_deleted`, `files_changed`, `ai_assisted`, `review_count`, `reviewer_types[]`
(human/agent; agent = `[bot]` reviewer accounts).
`ai_assisted` = any commit message matching
`Co-Authored-By: … (claude|copilot|cursor|windsurf|codex|agent|bot)` — exhaust-only detection.

## gate.run.completed
From a CI runs export (`--ci-runs`). Feeds **Pair 3** (first-pass eval-gate rate)
and **Pair 6** (gate throughput). Only workflows in the known gate set are emitted:
eval-gate, deepeval-gate, promptfoo-gate, ui-eval-gate, quality-gate,
ui-quality-gate, l3-quality-gate, l3-ui-quality-gate, guardrails-check,
multi-agent-gate, repo-scope-check, data-common-gate, databricks-gate, dbt-gate
(matches `ci/github/` and `ci/azure/` in the GovKit repo).
Fields: `feature_id`, `gate_name`, `run_attempt`, `conclusion`, `ts_start`,
`ts_end`, `commit_sha`.

## deploy.completed
Defined for **Pair 1** (deployment frequency ↔ change failure rate) and cycle-time
termination (Pair 3). Originates in CI/CD deployment events — **not emitted by this
producer**; a CI-side adapter emits it. Fields: `deploy_id`, `env`, `ts`, `status`
(success|failure|rollback), `commit_shas[]`.

## rework.observed
Git-history scan. Feeds **Pair 2** (rework rate, quality counterweight).
Fields: `commit_sha_origin`, `ts_origin`, `lines_added`, `lines_reworked_21d`,
`rework_author_same`, `feature_id`, `method`.

**Approximation note:** v1 uses file-overlap — deletions by later commits (within
the window) in files the origin commit added to, capped at origin additions.
This is an upper bound; it cannot distinguish which exact lines changed. Always
disclose `method: file-overlap-approximation` when reporting. Exact line
provenance (git blame lineage) is specified for the aggregator's v2 scan.

## refinement.token.issued (RESERVED — not emitted in v1)
Reserved for reading the Development Token decision record that
`aipos-feature-readiness` (govkit-plugins marketplace) writes at
`.govkit/tokens/<feature-id>.json` when it issues a decision. (Attribution note:
`aipos-feature-refine` produces a token *recommendation*; the token itself is
issued by the readiness gate — the record and this event follow the issuer.)
The record carries the decision — Approved / Approved with edits / Blocked —
authorizing AI-assisted coding to start. Now that the record exists as exhaust,
emitting this event unlocks Tier 2 metrics (refinement lead time Draft 0→Token,
blocked-token rate) without changing any v1 metric IDs.
Fields (mirroring the record): `feature_id`, `decision`
(approved|approved_with_edits|blocked), `score`, `blockers[]`, `draft_version`, `ts`.

**The record grew in increment 14A and this field list did not.** It now also
carries `kind`, `authoritative`, `states[]` and `product_approval` — the token
became a *derived execution-readiness record referencing a product approval*
rather than the decision itself. Those fields are deliberately **not** read by
this event: the six above are what the Tier 2 metrics need, and adding more
would change what `refinement.token.issued` means without any metric asking
for it. `tests/test_token_record_contract.py` asserts the six are still
present in what the readiness gate writes, because a reference document and a
script in another skill drift silently otherwise — the first version of that
record dropped three of them.

### Why no new events for commitment authority (increment 14C)

The behavior-contract work produces four candidate events: commitment
preparation, authorization checks, blocked changes, and replacement linkage.
**None is emitted, and that is a decision rather than an omission.**

No metric consumes them. The paired-metric law below means every event exists
to serve a named velocity/quality pair, and inventing a pair to justify an
event is how a metric set stops describing anything. The pilot has not run, so
there is no evidence about which of these is worth counting — and a counter
added now would be reported before anyone knows what a normal value looks
like.

The plan permits exactly this: *"If no telemetry event contract is needed for
the pilot, defer new metrics and retain structured evidence reports."* The
structured evidence already exists and is richer than a counter: the token
record carries `states[]` and `product_approval`, `govkit verify-contract`
reports per-commitment drift and authority, and a change package records what
was proposed and that it was not submitted.

**What must not happen** is inventing token-savings, time-savings or velocity
numbers from this work. Nothing here measures effort, and a number with no
measurement behind it survives longer than the caveat attached to it.

## Metric-pair mapping (paired-metric law)
| Pair | Velocity | Quality | Events consumed |
|---|---|---|---|
| 1 | deployment_frequency | change_failure_rate | deploy.completed (+git revert detection, aggregator) |
| 2 | ai_pr_throughput | rework_rate | pr.merged, rework.observed |
| 3 | feature_cycle_time | first_pass_eval_gate_rate | feature.package.snapshot, deploy.completed, gate.run.completed |
| 4 | spec_lead_time | spec_completeness_score | feature.package.snapshot |
| 5 | review_latency | unreviewed_merge_rate | pr.merged |
| 6 | gate_throughput | eval_coverage_at_gate | gate.run.completed, feature.package.snapshot |
