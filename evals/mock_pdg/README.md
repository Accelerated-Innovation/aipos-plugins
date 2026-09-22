# Mock opportunity-engine (Product Definition Graph read server)

A **development and evaluation stand-in** for the Discovery Engine's `opportunity-engine` MCP
read server. It exists so skills that read the Product Definition Graph (PDG) —
`aipos-solution-design` first — can be built and exercised before a live engine is reachable.

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

## What the default fixture exercises

| Problem | Case |
|---|---|
| `fixture:prb-ticket-triage` | The Solution Design canvas example. Recent, mixed sources; two readable tickets and one readable call; one ticket and all ReOps records with no readable text; a study outcome with null date and URL. **No ticket volume and no routing baseline in the graph** — both must become evidence GAPs. |
| `fixture:prb-invoice-dup` | Already promoted (active Aha! link) plus a severed Jira link. |
| five `fixture:prb-*` renewal rows | Five ranked problems tracing to **one** originating call. |
| `fixture:prb-month-end` | Evidence only from 2022–2024 (aging), one null `occurred_at` (unknown, not old). |
| `fixture:prb-schema-next` | `schema_version: 2` — a consumer must stop, not guess. |
