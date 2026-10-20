# Portfolio chat and dashboard prototype

**Updated · 2026-10-20.** Owner: AIPOS. Engine feature 25 owns the fictional portfolio and its reads.
The complete response fixture, offline HTML prototype and local MCP/REST capture are implemented.
Graph captures preserve source metadata and remain fixed until rerun. General AI chat and a
native MCP App surface remain unimplemented.

## Purpose and ownership

Let a PM inspect Harborlight Insurance Technologies across discovery, validation, commitment,
delivery and learning. Start with supplied responses so the conversation can be evaluated while
the graph is being designed. Then connect the same skill to real read operations and add the
smallest panel that improves browsing.

| Repository | Owns | Shared contract |
|---|---|---|
| discovery-engine | Canonical dataset, graph mapping, loader/reset, REST/MCP reads, deterministic oracles | Draft `demo-portfolio.v0.2`, metadata, summary/list/detail and Q01–Q10 |
| aipos-plugins | Skill, routing/behavior evaluations, normalized consumer data, later panel renderer | Consumes engine results; preserves IDs, provenance, errors and revisions |
| Chat host | Capability discovery and actual panel surface | Explicit host adapter, selected during panel work |

Authoritative engine package:
https://github.com/Accelerated-Innovation/discovery-engine/tree/main/features/25_engine_insurance_portfolio_demo
The files are local drafts until published. In a sibling checkout, find that exact package;
installed skills must not depend on the checkout. Link the contract instead of maintaining a
second source portfolio. Bundled response examples are derivatives, labeled with source paths,
SHA-256 file hashes, contract version and coverage.

## First deliverable: the skill now

`plugins/aipos/skills/aipos-portfolio-dashboard/` holds the initial skill, consumer notes and
evaluation cases. It owns portfolio inspection and comparison. Exploration-planning still owns
research-capacity allocation; rapid-validation owns experiments; map-render owns repository
feature/journey diagrams. Routing cases contrast those requests.

Fixture mode is explicitly selected or supplied. Connected mode requires successful real read
calls. No fallback silently replaces a failed live read with canned data. The current version
answers in chat and renders an offline interactive HTML dashboard from a supplied fixture or
a consistent capture of the engine read API. It does not write to Neo4j or seed data.
The repository currently packages Claude plugins; a Codex-specific plugin manifest or native
chat panel is not implied by this skill folder.

## Consumer behavior

- Overview: 32 distinct cases, four products, primary and membership counts distinguished,
  all lifecycle phases/dispositions included. Counts come from summary, not a visible page.
- Filtered selection: product membership + phase + disposition; retain filters and stable IDs
  in follow-ups. Exhaust pagination before global comparisons. Explicit empty/partial states.
- Detail: inspect evidence, decisions, commitment revisions and results by case ID. Cite record
  references; missing resource bodies remain missing. Historical explanations require detail.
- Consistency: use one metadata tuple for each answer/panel. Discard mixed responses, refetch
  once, then show a refresh failure. Clear previous details when selection or dataset changes.
- Authorization: render phase separately from commitment status. No write buttons or write
  calls. A synthetic approval never becomes authority to change real work.
- Metrics: fixed snapshot ages, preserved units/windows/n/targets, computed differences and
  no causal inference. Record phase age without calling the case blocked.

## Increments and acceptance

| Increment | Result | Completion evidence |
|---|---|---|
| 1 — Draft skill and fixture contract | Skill instructions, examples, routing cases, behavior eval cases | Structural/package tests and eval harness dry run; actual model evaluation reported separately |
| 2 — Complete fixture-driven conversation | Published nested detail schema and response fixtures for six deep stories plus all edge cases | Run Q01–Q10 through skill; evaluate claims/references/errors and follow-up filtering; no invented detail |
| 3 — Dashboard panel | Overview counts, product/phase/disposition filters, opportunity list, selected-case evidence/history | Keyboard navigation, empty/loading/error states, stable selection, clear synthetic/snapshot label; inspect rendered UI |
| 4 — Connect engine reads | Same consumer views populated from implemented demo operations | Q01–Q10 against loaded graph; real auth/error/pagination/revision tests; no mock fallback |

The selected host for increment 3 is an offline browser page. Source lives under
`viewers/portfolio/`; `build.py` packages three assets under the skill's `scripts/assets/`.
`scripts/render_dashboard.py` embeds the explicitly supplied fixture into one HTML file.
The renderer needs only Python 3.11+; the viewer needs no framework, remote assets or service.
The page's question panel executes deterministic queries for the ten sample questions, and
explicitly discloses that a conversational model is not connected. The skill itself can still
interpret portfolio questions in its host chat using supplied records.

## Evaluation coverage

The fixture covers all 32 detail responses, 187 timeline events, nine numeric findings, six deep
stories and the required comparisons. Its statuses were checked with the engine's canonical
commitment derivation function and all 34 response objects validated against the draft schema.
Sixteen model evaluation cases cover all ten oracles plus missing/partial/stale inputs and write
requests. A separate incomplete-detail fixture retains the requirement to disclose missing data.

The viewer's 16 deterministic tests exercise Q01–Q10, measurement arithmetic, filtering,
pagination, revision conflicts and integrity. Renderer tests check self-contained output,
script escaping, changed resources, invalid inputs and package freshness. Browser checks cover
filters, all ten queries, case tabs, keyboard activation, narrow layouts and error/reload states.
Actual model evaluation remains pending; the harness dry run only establishes runnable inputs.

Before live integration, replace the draft examples with generated samples from the engine's
published schemas. Verify source hashes and semantic oracles on every refresh. Keep malformed,
partial and stale fixtures distinct from success responses. Model graders check answer claims;
deterministic checks own arithmetic, schema and counts. A dry run does not count as a model pass.

## Validation and release boundaries

Run the repository's deterministic suite, skill structure validation, plugin/marketplace
validation, and the affected skill's eval dry run. Report actual model calls only if executed;
do not spend on `--execute` as part of the offline draft. The local plugin minor-version bump
records the new skill per CONTRIBUTING; merging/publishing is a separate action.

This plan neither rewrites ReOps nor builds SOAA. It records where lifecycle data is missing and
what a later producer would need to supply. Loading history demonstrates retrieval and future
transition examples; it does not execute or validate the legality of those transitions today.

## Local verification — 2026-10-20

- Root pytest suite: 749 passed, 6 skipped.
- Portfolio query tests: 16 passed, including Q01–Q10 and integrity/error cases.
- Real Chrome checks: filters, case selection, detail tabs, keyboard navigation, all ten guided
  queries, read-only behavior, narrow layouts and invalid-file/reload behavior passed. No page
  script errors or network requests from the standalone HTML. Desktop and mobile screenshots
  were inspected; viewport captures were used to confirm the mobile layout.
- Skill structure, marketplace/plugin validation and packaged asset freshness passed.
- Model evaluation: 16 cases prepared; harness dry run only. No subject/judge model calls.
- Engine fixture schemas and references validated; no graph load, runtime API test, lifecycle
  transition execution or performance claim.

Next integration milestone: the engine's approved loader/read implementation, followed by
consumer reads against a loaded demo graph. Keep the offline fixture route for repeatable
interaction and error-state testing.


## Graph-backed rerun — 2026-10-20

Captured local REST at `http://127.0.0.1:18000`: 35 authenticated reads, 32 case details,
`graph.1`, revision 229, graph digest
`sha256:d32c088184706b3eb28c5a647b1f4876760d52b38bde3c4051e39560f83ac587`.
The business snapshot remains 2026-10-19. All 68 included narrative bodies were taken from the
explicit engine resource file and verified against graph references. Account display names are
absent from this API contract, so this capture shows account IDs. No bundled response rows or
account names were substituted. The HTML contains no API token and performs no live refresh.

Validation: the full plugin suite passed in a disposable source copy (765 passed, 6 skipped),
including 21 dashboard tests. All 19 Node model tests and all ten deterministic query oracles
against the actual captured graph passed. Skill/manifest validation and packaged-asset checks
passed. The 16-case model-eval harness ran in dry-run mode only; no model calls were made. Browser visual verification for this rerun
was unavailable: the in-app browser tool blocked the local file URL; no alternate browser
route was used. Earlier fixture UI verification remains historical, not proof of this rerun.
No paid model evaluation was executed.


## MCP consumer connection — 2026-10-20

The user's “continue” authorized connecting to the existing discovery-engine MCP server.
The host now has a `harborlight_demo` connection at `http://127.0.0.1:18000/mcp/`, with only
`get_demo_portfolio`, `list_demo_opportunities`, and `get_demo_opportunity` enabled. Credentials
come from the engine's local `auth-headers` helper; no JWT is stored in config or artifacts.
A separate Codex app-server verification process successfully discovered exactly those three
tools (no model call or new chat). The already-running chat's tool inventory did not refresh;
no direct native chat tool invocation is claimed for this turn.

The capture helper's MCP client initialized the existing `opportunity-engine` 0.1.0 server,
negotiated protocol 2025-11-25, and made 35 portfolio tool calls. The resulting revision-229
snapshot contains all 32 case details and agrees with the same-revision REST capture. All ten
query oracles pass, including UW08's feasibility rejection, BI08's incomplete commitment,
CL07's invalidated commitment and the outcome comparisons. Dashboard provenance now says MCP.
The HTML still uses fixed-snapshot guided questions, not open-ended model chat or live refresh.

Validation: the full plugin suite passed in a disposable source copy (773 passed, 6 skipped),
including 25 focused consumer tests. All 19 Node model tests and 23 engine fixture/operator tests
passed. The 16-case model-eval harness ran in dry-run mode only; no model calls were made. The real MCP capture and Codex discovery check passed. Browser visual verification
remains unavailable because local file navigation was previously blocked; no workaround was
attempted. Paid model evaluation was not run.

The host UI rejected automated interaction with its own settings, so the current chat could
not be refreshed automatically. Restart the host to load the saved MCP connection into the chat.
