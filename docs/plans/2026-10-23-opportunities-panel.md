# Opportunities panel (the first MCP App panel)

**Updated · 2026-10-23.** Owner: AIPOS (Marty Bradley). Planned; nothing is built here yet.
The engine side is complete: discovery-engine feature 27 (`27_engine_mcp_opportunities_panel`,
PRs #151–#156). The engine binds this panel to `list_opportunities` and serves it as
`ui://aipos/opportunities` once a release is pinned there. This repository authors, brands,
tests and releases the panel.

## Purpose and ownership

When a PM asks for opportunities in an MCP-Apps-capable host (Claude, Claude Desktop), the host
renders an interactive panel next to the `list_opportunities` result. The PM can filter the
ranked list, open a problem's detail and evidence references, and hand a selection back to the
conversation. Hosts without MCP Apps keep exactly today's JSON answer.

| Repository | Owns | Shared contract |
|---|---|---|
| discovery-engine | Binding, serving and verifying the pinned file; `/health` status; the allowed tool set | `docs/backend/api-contract/ui_handoff.md`, "MCP App panels"; feature 27 `nfrs.md` |
| aipos-plugins (here) | Panel source, brand (`panels/BRAND.md`), UI tests, the contract test on the built file, releases | One HTML file per release, with version and SHA-256 |
| MCP host | Rendering in a sandboxed iframe; proxying the panel's tool calls with the user's token | MCP Apps spec, version 2026-01-26 |

Authoritative engine package:
https://github.com/Accelerated-Innovation/discovery-engine/tree/main/features/27_engine_mcp_opportunities_panel

## Where it lives: `panels/`, beside `viewers/`

`viewers/` holds offline snapshots: HTML a skill writes from captured data, shipped inside the
plugin under `plugins/aipos/skills/*/scripts/assets/` and released by a plugin version bump.
A panel differs in four ways:
- **Who ships it:** the engine serves it, not the plugin.
- **Data:** it reads live through the host instead of baking data in.
- **Release:** a tagged file pinned by a bump PR in discovery-engine.
- **Gates:** it carries the engine's extra ones (size, no external requests, allowed tool names).

Keeping it in a separate top-level folder keeps the two release paths from being confused.

```
panels/
  BRAND.md                      # how every panel carries the brand (done in this PR)
  opportunities/
    template.html  app.mjs  model.mjs  style.css   # source, dependency-free like viewers/portfolio
    bridge.mjs                  # the MCP Apps host bridge (see "Host bridge")
    build.py                    # inlines everything into one HTML file; --check for freshness
    dist/opportunities.html     # committed build output, reviewed as generated code
    model.test.mjs  check-page.mjs  fixtures/
tests/test_panel_contract.py    # the engine contract, run on dist/ in pytest
```

`model.mjs` is pure: it shapes tool results into rows and filters, so it can be shared with
`viewers/` later. Nothing under `panels/` is packaged into the plugin, so a panel change needs
no plugin version bump until the "Afterwards" step below.

## Behaviour

From feature 27's user flows. The panel only reads; anything that changes something goes back to
the conversation.

1. **Open.** The model calls `list_opportunities`, and the host renders the panel with that call's
   input and result. Show the ranked list: problem title, composite score, score components, and
   active work-item links. It is one page of the result (`offset`, `limit`, `total`); offer "more"
   by calling `list_opportunities` with the next offset.
2. **Filter and sort** in the panel, over the rows it holds. Say plainly when a filter covers only
   the loaded page.
3. **Drill in.** On selection, call `get_problem` and `list_evidence` for that `problem_id`, and
   show personas, lineage, and evidence **as provenance references** (source, record link, study
   measurement when present). **No evidence text:** `get_evidence_text` is not allowed, and the
   engine refuses to serve a panel that names it.
4. **Hand back** (in v1 only if decision Q4 says so; see "Open questions"). Selected
   opportunities plus an action ("draft Aha! records", "package for gate 1") become a
   `ui/message` to the conversation. The skill and its confirmation step take it from there. If
   it is in v1, increment 2 defines the payload and the consumer contract:
   - the message text the model reads;
   - the `problem_id`s it carries;
   - which skill picks it up.

   No write tool is ever called from the panel.
5. **Fallbacks.** Show empty states for an empty list (no scoring run yet), errors for a refused
   or failed call (show the engine's code: `INSUFFICIENT_SCOPE`, `INVALID_TOKEN`), and a stale
   label (capture time, past 24 hours) per `plugins/aipos/references/panel-contract.md`.
   Provenance on the panel: source mode `connected`, the server name, the read time, and
   coverage (rows shown of `total`).

## Host bridge (MCP Apps spec 2026-01-26)

The panel speaks JSON-RPC over `postMessage` with the host:
- `ui/initialize`, then `ui/notifications/initialized`, for the handshake;
- `ui/notifications/tool-input` and `ui/notifications/tool-result` deliver the
  `list_opportunities` call that opened it;
- `tools/call` reaches `list_opportunities`, `get_problem` and `list_evidence` (the engine leaves
  their `visibility` at the default, model and app);
- `ui/message` hands back to the conversation;
- `ui/notifications/size-changed` asks for height;
- `ui/notifications/host-context-changed` follows theme changes;
- `ui/open-link` opens record links.

Re-check these names against the spec version the target host implements before building.

**Decision for increment 2:** a hand-written `bridge.mjs` covering only the messages above, or the
official SDK `@modelcontextprotocol/ext-apps` (2.0.3 at writing) bundled in. Hand-written keeps the
file small and dependency-free and makes the tool-name scan trivial to reason about. The SDK
tracks the spec. Recommendation: hand-written, unless the target host needs negotiation the SDK
handles. Either way, the contract test below decides.

## Brand

`panels/BRAND.md`, from the Accelerated Innovation Brand Book V01. In short:
- the host's surfaces and font;
- purple accent in light mode, light blue in dark;
- one small official mark;
- left-aligned type;
- status never by colour alone.

Every panel PR carries its checklist and light and dark screenshots, reviewed by Marty Bradley.

## The contract test (on the built file)

`tests/test_panel_contract.py`, in pytest, so the `validate.yml` pytest job runs it on every PR.
This is the primary control; the engine's load-time scan is only a tripwire.
- `dist/opportunities.html` is **at most 256,000 bytes** and valid UTF-8.
- **No external requests:** no `http(s)://` in `src`, `href` (except record links opened through
  `ui/open-link`), `@import`, `url(…)` or `fetch(`; no `<link rel=stylesheet>`; no web fonts.
- **Tool names:** names `list_opportunities`, `get_problem` and `list_evidence`, and **none** of
  the engine's other tools. That means no other tool name as a whole identifier anywhere in the
  file, comments and bundled code included. The forbidden list mirrors discovery-engine's
  `src/engine/api/mcp/panels.py` `ENGINE_TOOL_NAMES`; the test cites that file so the two are
  updated together.
- `build.py --check` passes: the committed `dist/` is what the source builds. This and the
  model's `node --test` need their own `validate.yml` steps, added in increment 4; the existing
  Node steps cover only `viewers/`.

## Increments and acceptance

| Increment | Result | Completion evidence |
|---|---|---|
| 1 — Brand and plan | `panels/BRAND.md`; this plan | Reviewed and merged |
| 2 — Model and fixtures | `model.mjs` (rows, filters, sort, paging state, provenance), fixtures from discovery-engine's published samples (`opportunities.json`, `problem-detail.json`, `problem-evidence.json`), the bridge decision | `node --test panels/opportunities/model.test.mjs`; fixtures cite their source paths and SHA-256 |
| 3 — Page, bridge, build | `template.html`, `app.mjs`, `style.css`, `bridge.mjs`, `build.py` producing `dist/opportunities.html`; a mock-host page for local checks | `check-page.mjs` drives the mock host with Playwright (reusing the journey viewer's pinned install): open, filter, drill in, error and empty states, a partial host-context update, keyboard only; hand back **only if Q4 put it in v1**, asserting the exact `ui/message` payload; light and dark screenshots |
| 4 — Contract test and CI | `tests/test_panel_contract.py`; **new `validate.yml` steps** for `python panels/opportunities/build.py --check` and `node --test panels/opportunities/model.test.mjs`. Today's Node steps test only the viewers | Each check proven able to fail (a planted forbidden name, an external URL, an oversized file, a stale `dist/`); the increment is not done until the new steps run on a PR |
| 5 — Release | Tag `panels-opportunities-v<version>`; `gh release` with `opportunities.html` and its SHA-256 in the notes | Release published; SHA-256 recomputed from the downloaded asset |
| 6 — Pin and verify in a host | discovery-engine bump PR (its `DEPLOYMENT.md` part F1); the engine run with `ENGINE_MCP_PANELS_ENABLED=true` (stdio for Claude Desktop, or the hosted engine via F2) | `/health` shows `bound` at the release version; the panel renders in Claude Desktop in light and dark; drill-in and hand-back work against the real engine |

**Afterwards:** update the "Native in-chat panel (MCP App): Not available" row in
`plugins/aipos/references/panel-contract.md`, which is a plugin change and needs a version bump.
Tell the skills that call `list_opportunities` that a panel may be showing.

## For the demo

Increments 2–6 must land, in order. The engine side needs nothing more than the pin (6) and the
switch. For a local demo in Claude Desktop, the engine's server entry in
`~/Library/Application Support/Claude/claude_desktop_config.json` needs these in its `env`:
- `ENGINE_MCP_PANELS_ENABLED=true`;
- `ENGINE_MCP_TOKEN`;
- `JWT_SECRET_KEY`, equal to the secret the token was minted with. The stdio server reads `.env`
  only from its working directory.

## Open questions

1. The bridge implementation: hand-written, or the SDK (decide in increment 2).
2. The official SVG artwork for the mark (`BRAND.md` "Open items"). The panel ships without a mark
   until it arrives.
3. Brand book discrepancies for the brand owner (`BRAND.md` "Source notes"): the secondary blue
   and yellow RGB values against their hex codes, and the wordmark minimum size.
4. **Hand-back in v1, or read-only browsing first? Decide before increment 2**, because
   increment 3's tests depend on it. If yes, increment 2 also defines the `ui/message` payload
   and the receiving skill's contract.
5. Which host versions to verify against: Claude Desktop is the demo host; check whether Claude
   Code renders MCP App panels before relying on it.
