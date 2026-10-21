# Mock opportunity-engine (Product Definition Graph read server)

A **development and evaluation stand-in** for the Discovery Engine's `opportunity-engine` MCP
read server. It exists so skills that read the Product Definition Graph (PDG) —
`aipos-solution-framing` first — can be built and exercised before a live engine is reachable.

**It is not a data source.** Every record is synthetic: IDs start with `fixture:`, text carries
`[SYNTHETIC]`, and links point at `fixture.invalid`. It never ships as part of the `aipos` plugin.

## Contract

Same seven tools, same arguments, same response shapes as the engine
(`discovery-engine/src/engine/api/schemas.py`, `src/engine/api/mcp/tools.py`, schema_version 1):

| Tool | Returns |
|---|---|
| `list_problems(offset=0, limit=20)` | `ProblemListResponse` |
| `get_problem(problem_id)` | `ProblemDetailResponse` |
| `get_lineage(problem_id)` | `LineageResponse` |
| `list_evidence(problem_id)` | `ProblemEvidenceResponse` (dates in `occurred_at`, nullable) |
| `list_opportunities(offset=0, limit=20)` | `OpportunityListResponse` (an opportunity *is* a scored problem, 1:1 on `problem_id`) |
| `get_work_item_links(problem_id)` | `ProblemLinksResponse` (`promoted` = any ACTIVE `promoted` link) |
| `get_evidence_text(provenance_reference, problem_id=None)` | `EvidenceExcerptResponse` |

Errors are tool results with `isError: true` and text `<CODE>: <message>` —
`PROBLEM_NOT_FOUND`, `VALIDATION_ERROR`, `EVIDENCE_TEXT_UNAVAILABLE`, `LINKS_UNAVAILABLE`.
`tests/test_mock_pdg.py` pins every field set to the engine's models; change the test first when
the engine's contract changes.

## Running it

Standard library only; Python 3.9+.

```bash
# Register with Claude Code for this repo (dev only):
claude mcp add opportunity-engine-mock -- python3 evals/mock_pdg/server.py
# or copy evals/mock_pdg/mcp.example.json into a local .mcp.json
```

The server name differs from the real one on purpose (`opportunity-engine-mock` vs
`opportunity-engine`), so a skill that detects the engine by tool signature rather than name is
exercised on every run. Going live is swapping the registration, not changing the skill.

| Variable | Effect |
|---|---|
| `MOCK_PDG_FIXTURE` | Serve a different fixture file |
| `MOCK_PDG_EVIDENCE_TEXT=off` | `get_evidence_text` is not advertised (the engine's behaviour when evidence text is unconfigured) |
| `MOCK_PDG_LINKS=off` | `get_work_item_links` raises `LINKS_UNAVAILABLE` — unknown, not "not promoted" |
| `MOCK_PDG_ACCESS_LOG=<path>` | JSON lines: every `get_evidence_text` call, refusals included |
| `MOCK_PDG_CALL_LOG=<path>` | JSON lines: every `tools/call` — name, arguments, outcome |
| `MOCK_PDG_CANARY_TOOLS=a,b` | Advertise **canaries**: names a skill must never call (see below) |

## Canaries are not contracts

A canary is a tool name a skill must never call — a write it has no authority for, or a tool
whose engine contract has not been verified — advertised so that declining it is observable.
Its input schema is deliberately open, every call is refused with `CANARY_INVOKED` and logged,
and nothing it returns can pass for a record. `evals/run_traces.py` uses canaries and the call
log to check tool behaviour in real Claude Code sessions. Never build a skill against a
canary's shape; when the engine publishes a tool, pin its contract here like the seven reads.

## Verification against the engine — 2026-10-21

- **Field sets match.** Read responses captured through an authenticated, connected read
  connector serving the Harborlight demo (seven PDG reads plus three demo reads; no write,
  ingestion-status or correction tool advertised) have the same key sets as this mock for
  `list_problems`, `list_opportunities`, `get_problem`, `list_evidence`, `get_lineage` and
  `get_work_item_links`. `get_evidence_text` was not called (each call is an access-logged
  disclosure). A second pass against the direct endpoint `https://opportunity.aidlc.org/mcp/`
  (authenticated by an interactive OAuth login) confirmed the same tool list, input schemas and
  field sets, including work-item link rows.
- **Behaviour the mock does not yet follow** (engine source at discovery-engine `1a8919d`,
  confirmed live on the direct endpoint where marked): errors on the wire carry the SDK prefix
  `Error executing tool <name>: ` before `CODE: message` (seen live); `get_lineage` on an
  unknown problem is `LINEAGE_NOT_FOUND` (seen live); `get_work_item_links` on an unknown problem
  returns an empty, `promoted: false` result (seen live); `list_problems` is ordered by creation time in persistent mode,
  not by score (seen live); `list_opportunities` holds only scored problems, so it is not 1:1
  with `list_problems`; `evidence_references` and `source_evidence_refs` are bare external IDs
  while `list_evidence` uses `source:id` (seen live); `lineage_ref` equals `problem_id` and
  `originating_sources` has one `source:id` per evidence record (seen live); `get_evidence_text`
  is always advertised by the engine. Aligning the mock changes tests that existing skills
  rely on, so it is a separate change; until then a skill must not depend on these mock-only
  invariants.

## What the default fixture exercises

| Problem | Case |
|---|---|
| `fixture:prb-ticket-triage` | The Solution Framing canvas example. Recent, mixed sources; two readable tickets and one readable call; one ticket and all ReOps records with no readable text; one **study finding** from time study `study-ts-07` — the misrouting rate, 32% of 400 tickets (`log_analysis`), with a measurement and no URL. **No ticket volume and no triage-time figure in the graph**, so both must become evidence GAPs. The finding is not the first-time-correct routing baseline either: it is its complement, a *candidate* the PM must confirm counts the same tickets the same way. |
| `fixture:prb-invoice-dup` | Already promoted (active Aha! link) plus a severed Jira link. |
| five `fixture:prb-*` renewal rows | Five ranked problems tracing to **one** originating call. |
| `fixture:prb-month-end` | Evidence only from 2022–2024 (aging), one null `occurred_at` (unknown, not old). |
| `fixture:prb-schema-next` | `schema_version: 2` — a consumer must stop, not guess. |
