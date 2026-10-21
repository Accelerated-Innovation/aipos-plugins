# Plan: Close the four P1 skill gaps in Define & Design

**Date:** 2026-10-21
**Naming note:** the source issues call governed MCP writes "engine feature 17"; in the engine they
are feature 19 (ADR-AIG-030) — feature 17 is study findings. This plan uses 19.
**Source:** The four P1 new-skill items from the AIPOS skills-to-PDLC gap backlog
([tracking issue #86](https://github.com/Accelerated-Innovation/aipos-plugins/issues/86)) that sit in
Pillar 1 "Define & Design" (steps 1–10, gates G1–G2). Sequenced in the 2026-10-21 planning session;
adds per-skill view specs and acceptance-honesty rules on top of the tests-first criteria each issue
already carries.
**Status legend:** `[ ]` not started · `[~]` in progress · `[x]` done
**Status:** In progress — Step 0 verified (below); #60 package slice in PR #91.

## Context

Five skills in the backlog scored P1. Four of them live in Pillar 1 (Define & Design):

| Issue | Skill | Step | Wave | Recorded blocker |
|---|---|---|---|---|
| [#60](https://github.com/Accelerated-Innovation/aipos-plugins/issues/60) | `aipos-opportunity-package` | 4 → G1 | 2 | engine feature 19 (write half only) |
| [#59](https://github.com/Accelerated-Innovation/aipos-plugins/issues/59) | `aipos-agent-contract` | 7 | 3 | nothing |
| [#57](https://github.com/Accelerated-Innovation/aipos-plugins/issues/57) | `aipos-signal-intake` | 1 | 3 | engine ingestion-status read tool, E9 connectors |
| [#61](https://github.com/Accelerated-Innovation/aipos-plugins/issues/61) | `aipos-problem-clustering` | 2 | 3 | engine correction path (merge/split) |

The fifth P1, `aipos-research-plan` (#58), sits in Pillar 2 (Rapid Validation) and is out of scope
here.

Every issue already contains its acceptance criteria as tests — routing cases, model-graded eval
cases, deterministic pytest — and a Definition of Done. This plan does not replace those; it
sequences the work, states what "closed" means when only part of a skill can ship, and adds the
chat-panel (view) specs agreed on 2026-10-21.

## Sequencing and what "done" means per skill

Order: **#60 package slice → #59 → (#57, #61 prep in parallel) → remaining blocked halves.**
The Step 0 live-server pass runs in parallel and does **not** block #60's package slice — it
gates the mock-contract updates and the blocked-skill ship decisions, not the package build.

The two unblocked skills go first, in wave order. The two blocked skills get their tests and mock
fixtures written now — their specs already define graceful degradation — but their wave and
`blocked: engine` labels stay until the live engine's capabilities are verified (below). Preparing
tests early does not require reassigning waves. Partial delivery is not issue closure: a PR that
ships a slice says so, and the issue stays open with the remaining half restated.

### 1. #60 `aipos-opportunity-package` — package slice first

- [x] Routing cases and eval cases for the four-part package (evidence, hypothesis, impact
  estimate, recommended action), shown failing in the PR. (PR #91)
- [x] Build the package half of the skill; the issue explicitly permits the package output to ship
  before the write half. (PR #91 — plus a native tool-use trace that the skill declines
  advertised write canaries.)
- [ ] **Write-integration slice (separate):** extend `evals/mock_pdg` with the feature 19 (ADR-AIG-030) tools
  (`find_similar_problems`, `propose_problem`, `attach_intent` with `dry_run` and
  `idempotency_key`), pin them in `tests/test_mock_pdg.py`, and define them **only against a
  verified engine contract** — the hosted server is read-only (see Step 0), so these mocks wait for
  a contract to verify against, not the mock author's guess.
- [ ] Write half (propose after dry-run preview + one explicit yes) follows engine feature 19.

**Done for the package slice** = the package output ships and passes its evals. The issue stays
open until the write half lands.

### 2. #59 `aipos-agent-contract` — shared schema in references

- [ ] Routing and eval cases first, shown failing.
- [ ] Contract schema in `plugins/aipos/references/agent-contract.md` (six sections; tool side
  effects with confirmation status; escalations naming trigger + human role; TBDs with owners,
  never invented) so `dialogue-flow`, `feature-create` and `risk-review` cite it rather than copy
  it.
- [ ] Completeness-checker pytest against fixtures, if a checker script is bundled.

**Done** = full issue; nothing blocks it.

### 3. #57 `aipos-signal-intake` — prep now; ship decision after verification

- [ ] Routing and eval cases first (including the `no-status-tool-means-unknown` case), shown
  failing.
- [ ] Source inventory (which listed sources are connected, which aren't, with drafted connector
  requests) is the useful-now slice and does not require building any connector. Authoritative
  freshness monitoring is separate and depends on the engine's ingestion-status read.
- [ ] Verify whether the live engine already exposes an ingestion-status read (Step 0). If it
  truly doesn't, keep `blocked: engine` and use the existing dependency entry in #86 — do not open
  a duplicate engine issue.
- [ ] "Freshness unknown" is the documented fallback, not a claim that freshness monitoring is
  complete.

### 4. #61 `aipos-problem-clustering` — prep now; review slice can precede the correction path

- [ ] Routing and eval cases first (including `no-correction-path`), shown failing.
- [ ] The review slice — inspect clusters, compare masked quotes, suggest merges/splits with
  evidence, prepare the correction for hand-off — is non-mutating by design and does not require a
  merge/split execution tool to be useful. The Cluster Review board (view spec below) can ship as
  this same slice.
- [ ] Full issue closure still requires the engine's correction path, per the issue's recorded
  blocker. Verify its status on the live server (Step 0) before treating it as absent.
- [ ] The skill never applies a correction itself.

## Step 0: the live server — verified facts and pending verification

The engine's read service is hosted at `https://opportunity.aidlc.org/mcp/` (hosted Harborlight
demo; `demos/insurance/HOSTED.md` and decision record
`docs/backend/architecture/ADR/ADR-AIG-038-explicit-hosted-demo-target.md` in the private
`discovery-engine` repo — cite paths, not URLs, since the repo is not publicly readable). On
2026-10-21 the plan author verified directly:

- **Live and reachable** — streamable-HTTP MCP endpoint (uvicorn/FastMCP), responds to `initialize`.
- **OAuth 2.0 Bearer required.** RFC 9728 protected-resource metadata names Keycloak realm
  `discovery` (`https://opportunity.aidlc.org/auth/realms/discovery`, scope `openid`), which
  advertises `client_credentials`, `password` and device-code grants.
- **The hosted configuration is read-only.** (Re-confirmed in engine source on 2026-10-21:
  `ENGINE_MCP_WRITE_ENABLED=false` in every deployed environment.) The engine's hosted-demo docs state OIDC is required
  and the two MCP write flags stay disabled in the application configuration. So feature 19 write
  tools are **not** verifiable against this server; the write halves of #60 (and any write view)
  wait on engine work regardless of what `tools/list` shows.

### Verified 2026-10-21 (second pass)

- **Live reads, field sets.** An authenticated claude.ai read connector serving the Harborlight
  demo advertised the seven PDG reads plus `get_demo_portfolio`, `list_demo_opportunities` and
  `get_demo_opportunity` — no write, ingestion-status or correction tool. Representative calls
  to the six non-disclosing reads returned the same key sets as `evals/mock_pdg` and
  `tests/test_mock_pdg.py`; input schemas match. `get_evidence_text` was deliberately not called.
  The connector's URL is not visible to the verifying session, so this is recorded as "a
  connected hosted-demo read connector", not as proof about `opportunity.aidlc.org` itself. The
  locally configured direct entries for that URL were disabled or needed an interactive OAuth
  login, and no token was handled.
- **Engine source** (`discovery-engine` `1a8919d`, clean, equal to origin HEAD):
  - Governed MCP writes (ADR-AIG-030) are engine **feature 19** (feature 17 is study findings).
    `find_similar_problems`, `propose_problem`, `attach_intent` are implemented and merged,
    all behind `ENGINE_MCP_WRITE_ENABLED`, which is `false` everywhere deployed.
  - **No ingestion-status read** over MCP or REST. Only Gong and Zendesk are wired for
    ingestion; no Jira/ADO, CRM, product-usage or eval-drift ingestion exists. `/health`
    lists evidence-text sources with credentials — not ingestion state.
  - **Merge/split corrections were retired without replacement** (ADR-AIG-031; the workflows
    corrections router was deleted 2026-10-09). #61's "correction path" blocker therefore has
    no engine owner today — see #61 below.
  - **No MCP Apps support**: no `ui://` resources or `_meta.ui` anywhere in the engine.
  - Excerpts are redacted server-side and capped at 1,500 characters; the five-excerpt cap is
    an AIPOS convention (solution-framing `opportunity-source.md`), not an engine rule.
- **Mock behaviour drift** (not field sets) is recorded in `evals/mock_pdg/README.md`; aligning
  it touches tests existing skills rely on and is a separate change. New skills must not depend
  on the mock-only invariants (score-ordered `list_problems`, 1:1 opportunities, identical
  reference formats across tools).

### Verified 2026-10-21 (direct endpoint)

After an interactive OAuth login to `https://opportunity.aidlc.org/mcp/` (the `discovery-engine`
MCP entry; no token handled in the session), a read-only session confirmed:

- **`tools/list`:** the seven PDG reads plus the three demo-portfolio reads. **No** write
  (`find_similar_problems`, `propose_problem`, `attach_intent`), ingestion-status or merge/split
  correction tool is advertised. Input schemas match `evals/mock_pdg`.
- **Response shapes:** `list_problems`, `list_opportunities`, `get_problem`, `list_evidence`,
  `get_lineage` and `get_work_item_links` (including link rows) have the mock's field sets.
  `get_evidence_text` was not called.
- **Behaviour drift, confirmed live:** errors carry the `Error executing tool <name>: ` prefix;
  `get_lineage` on an unknown problem is `LINEAGE_NOT_FOUND`; `get_work_item_links` on an
  unknown problem returns an empty `promoted: false` result; `list_problems` is not ordered by
  score. (Recorded in `evals/mock_pdg/README.md`; aligning the mock is a separate change.)
- **Data:** 28 problems; evidence sources are `demo` synthetic references and `reops` study
  findings only.

The checklist below is kept for the record; its items are now answered by the two verification
passes above.

Originally blocked on a direct Bearer token to `https://opportunity.aidlc.org/mcp/` (the engine's local `auth-headers` helper is
local-only and refuses `--hosted`; a hosted token needs a Keycloak client credential or user
login):

- [ ] `tools/list` against the live server, diffed against `evals/mock_pdg/server.py` and
  `tests/test_mock_pdg.py`. Compare the mock's **supported subset** — extra live tools don't make
  the mock wrong, and `tools/list` establishes advertised input schemas, not response shapes.
  Where the shared subset differs, change the test and mock **first**, then the skill.
- [ ] Response shapes, not just input schemas: make one authenticated representative call per
  shared read tool and capture the response shape; compare against `evals/mock_pdg` fixtures and
  `tests/test_mock_pdg.py` **before** changing the mock — otherwise the mock can remain
  compatible with stale fields. If the engine publishes a response-schema source, prefer it.
- [ ] While connected: check specifically for an ingestion-status read (#57) and any merge/split
  correction path (#61). Update #86's engine-dependency list with what is found rather than
  assuming absence.

## Acceptance-honesty rules

These apply to all four skills; they refine the DoD already in each issue.

1. **Response-content evals cover explanation and fallback behavior. Tool-use claims — "dry-run
   before write", "no mutation", "similarity outage blocks propose" — require observed invocation
   traces or instrumented integration tests** demonstrating ordering, refusal, confirmation
   boundaries, and absence of unauthorized mutation. Mock contract tests alone do not prove the
   skill followed those rules, and neither does an eval case whose prompt merely narrates the
   condition.
2. **Mock schemas must match verified engine contracts** — see Step 0. A skill built against a
   mock that drifted from the live server is not done.
3. **Never report an eval as passing unless it ran.** Dry-run and `--execute` results are reported
   separately in the PR, per [CONTRIBUTING](../../CONTRIBUTING.md).

## View specs (chat panels)

### Shared panel contract

Multiple skills will render panels, so the shared rules live in one place (a new
`plugins/aipos/references/` file when the first view-bearing skill ships) rather than copied per
skill. It must cover, from the 2026-10-06 gap analysis:

- Evidence provenance marks and revision/timestamp information.
- Masked excerpts and the established five-excerpt limit on evidence text.
- Draft and synthetic labels.
- Plain-text fallback for every view-backed tool, and compatible-host capability handling.
- Confirmation and stale-preview handling for consequential actions (full preview, exact
  destination, one explicit yes, read-back).

**Implementation boundary:** the skill's instructions decide *when* to offer a panel; an
MCP-Apps-capable server supplies the tool and UI resource; a compatible host renders it. A live
server — or a read-only server — does not by itself determine whether panels are supported. This
contract must be reconciled with the panel architecture already sketched in
[the portfolio-dashboard plan](2026-10-19-portfolio-dashboard.md), not compete with it.

### Per-skill specs

Add a view only when the PM needs to **inspect, compare, edit or confirm** something; text or a
generated chart is enough otherwise.

| Skill | View | Spec and dependency boundary |
|---|---|---|
| [#61](https://github.com/Accelerated-Innovation/aipos-plugins/issues/61) `aipos-problem-clustering` | **Cluster Review board** (best fit in this set) | One row per candidate problem: masked supporting quotes, suggested merges/splits with evidence references, persona and workflow tags. PM compares and confirms; confirmations are prepared for the engine's correction path and shown as pending, never applied. Plain-text list is the fallback. **Can ship with the review slice** — it doesn't need the correction-path tool; full issue closure does. |
| [#60](https://github.com/Accelerated-Innovation/aipos-plugins/issues/60) `aipos-opportunity-package` | **Structured Opportunity card + confirm panel** | The card displays the four-part package with cited evidence and needs no write capability. The propose action's confirm panel (full dry-run preview, exact destination, one explicit yes, then read-back) ships with the write half, after feature 19. |
| [#57](https://github.com/Accelerated-Innovation/aipos-plugins/issues/57) `aipos-signal-intake` | **Source-health table panel** (low priority) | Source-by-source: connected or not, last ingestion, volume in window, drafted connector request. A plain table is nearly as good; build the panel only if the engine gains the status read and PMs ask. Reporting missing sources does not require building those connectors. Before implementing the panel, verify the ingestion-status **response fields** (connection state, last ingestion, volume for the selected window) with a representative authenticated call; define freshness semantics per field and give each field its own fallback ("connection unknown", "last ingestion unknown", "volume unknown") rather than relying solely on the blanket "freshness unknown". |
| [#59](https://github.com/Accelerated-Innovation/aipos-plugins/issues/59) `aipos-agent-contract` | None | The contract is a document to review, not something to inspect visually. Text/file. |

### View testing

No current evals check when a view should appear or that the text fallback works (verified against
`evals/` on 2026-10-21). Each view-bearing skill adds:

- [ ] Eval cases for when the view should appear and when plain text is correct.
- [ ] Host-rendering check: render the panel in an MCP-Apps-capable host (or the repo's viewer
  harness) and record the evidence in the skill's completion criteria — text-only evals
  cannot establish that a panel mounted or worked.

## Work-item summary

- [x] 0. Live-server verification pass (direct endpoint, hosted-demo connector and engine source,
  2026-10-21; mock behaviour alignment is a separate change) — parallel, non-blocking for #60's package slice (needs
  a Bearer token: `tools/list` and response-shape diff vs mock; ingestion-status and
  correction-path checks; update #86)
- [~] 1. #60 package slice (PR #91) (tests first → skill → PR); feature-19 mocks deferred to the
  write-integration slice
- [ ] 2. #59 agent contract (tests first → references schema → skill → PR)
- [ ] 3. #57 prep (tests + degraded-behavior cases + source-inventory slice; ship decision on
  verification)
- [ ] 4. #61 prep (tests; review slice and board can precede the correction path)
- [ ] 5. Shared panel contract reference + view-appearance, text-fallback and host-rendering
  checks added with each view-bearing skill
- [ ] 6. Write half of #60 after engine feature 19; #57's freshness half after the status read;
  #61's full closure after the correction path
