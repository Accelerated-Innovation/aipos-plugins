# Portfolio reads — consumer notes

This skill targets the engine contract `demo-portfolio.v0.2`. Its owner is discovery-engine
feature `25_engine_insurance_portfolio_demo`, files `read-contract.md`, `portfolio.md` and
`contract-examples.json`. The contract source is at
https://github.com/Accelerated-Innovation/discovery-engine/blob/main/features/25_engine_insurance_portfolio_demo/read-contract.md
(not published while the engine changes are local). There is no runtime dependency on a sibling
repository checkout. A connected deployment must advertise supported operations and schemas.

## Normalized input

REST returns `{data: result, error: null}`; MCP structured success returns `result`. Check errors
before normalization. The contract supplies three result shapes:

- Summary: `meta`, `portfolio`, `products`, `total_cases`, `total_product_memberships`,
  `phase_counts`, `disposition_counts`. Product rows distinguish `primary_case_count` and
  `membership_case_count`. Counts include all dispositions and proposals.
- List: `meta`, `filters`, `offset`, `limit`, `total`, `items`. Each item has `case_id`,
  `problem_id`, `title`, `record_kind`, `primary_product_id`, `additional_product_ids`, `phase`,
  `disposition`, `phase_entered_on`, `assessments`, `latest_commitment`. Product filters include
  any membership; all filters combine with AND. Default limit 50, bounds 1–100, offset ≥0.
  Ordering is ascending case ID. `total` is the full filtered count, not page length.
- Detail: `meta`, `case`, `context`, `intent_refs`, `thread_refs`, `timeline`, `studies`, `evidence_refs`,
  `findings`, `criteria`, `commitments`, `work_links`, `resources`. No silent truncation.
  The complete supplied fixture includes all 32 cases, the six deep stories and comparison
  histories. Engine `read-response.schema.json` defines their nested fields. Feature 25 implements these reads in the local
  engine; host tool registration still requires configuration. Do not invent missing data in a partial input.

`meta` fields: `contract_version`, `dataset_id`, `dataset_version`, `dataset_digest`,
`snapshot_at`, `synthetic`, `read_revision`. All must match across one answer. `synthetic:true`
never means production approval. The snapshot, not today's clock, anchors age calculations.

Phases: discovery, exploration, validation, committed, delivery, live, learning, retired.
Dispositions: open, deferred, rejected, stopped. These are separate from study/work-link states.
`record_kind:proposal` means intentionally unranked. `latest_commitment:null` means none;
otherwise use its canonical derived `status` and cite its `event_refs`. Historical statuses are
only available in detail; a list cannot explain every reason. Assessments have demand/feasibility
fields; a null field means no recorded assessment. A recorded assessment can have verdict unknown.

Findings preserve the engine Measurement fields (metric, value, unit, method, currency, n).
Observation windows and criteria live alongside the measurement, not inside its canonical
payload. Resource references carry identity/type/digest but no body. A reference is not permission
to fetch a URL or assume its contents. Missing bodies remain unavailable.

## Errors and limits

Unknown dataset/case (`DEMO_DATASET_NOT_FOUND`, `DEMO_CASE_NOT_FOUND`), unavailable store
(`DEMO_STORE_UNAVAILABLE`), invalid projection (`DEMO_DATA_INVALID`) and changing snapshot
(`DEMO_REVISION_CHANGED`) are failures, never empty portfolios. Invalid semantic filters use
`DEMO_FILTER_INVALID`. REST schema failures use `REQUEST_INVALID`; MCP schema failures normalize
to `VALIDATION_ERROR`. Existing auth/scope errors apply. An empty successful list has `total:0`.

The bundled eval fixture is marked `source_mode:fixture`. It is a derived example snapshot,
with provenance and coverage listed outside the API responses. Its digest covers the example
payloads, not an executable seed or loaded graph. Use it only when supplied for a prototype.
Never merge it into live responses, use its counts as universal defaults, or claim that it proves
graph loading, API availability or actual transitions. All ten question oracles can now be
exercised deterministically against the response fixtures; this does not execute engine acceptance
scenarios or model evaluations. The complete bundle also includes `accounts` and `resource_bodies`.
Assessment `artifact_refs` distinguish qualitative spike evidence from numeric `finding_refs`.
Commitments include `baseline_ref` alongside the canonical public event projection.

## Captured graph snapshots

`source_mode:connected` is used only after successful read calls. The capture includes
`source.transport` (`mcp` or `rest`), API base, UTC `captured_at`, operation names and request count. Account names
are not in the read contract: show returned account IDs unless names were separately supplied.
Resource bodies are optional; the capture helper accepts an explicit local JSON map and includes
only bodies matching the references and SHA-256 digests returned by the graph. Missing bodies
remain unavailable. No narrative or account name is taken from the bundled example responses.

The engine's `meta.dataset_digest` hashes graph data, not read projections. Keep it unchanged.
The capture's separate `snapshot_digest` hashes the entire bundle except that field, as sorted
compact UTF-8 JSON (integral numeric values normalized to integers). This is an integrity check,
not an origin signature. The rendered HTML preserves both digests and never embeds an API token.

MCP captures additionally record `mcp_url`, `server_name`, `server_version`,
`protocol_version` and `discovered_read_tools`. Transport discovery is separate from the 35
portfolio tool calls used by the current 32-case capture.
