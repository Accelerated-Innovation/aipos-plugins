# Opportunities panel (the first MCP App panel)

**Updated · 2026-10-23.** Owner: AIPOS (Marty Bradley). Planned; nothing is built here yet.
The engine binding is complete: discovery-engine feature 27 (`27_engine_mcp_opportunities_panel`,
PRs #151–#156). The engine binds this panel to `list_opportunities` and serves it as
`ui://aipos/opportunities` once a release is pinned there. The SDK decision below requires an
engine bundle-budget change before that pin. This repository authors, brands, tests and releases
the panel.

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
    template.html  app.mjs  model.mjs  style.css   # vanilla JavaScript UI; pure model
    bridge.mjs                  # narrow adapter around the official MCP Apps SDK
    package.json  package-lock.json  # exact SDK/build-tool pins and locked dependencies
    build.mjs                   # bundles SDK and source into one HTML file; --check for freshness
    dist/opportunities.html     # committed build output, reviewed as generated code
    model.test.mjs  check-page.mjs  fixtures/
tests/test_panel_contract.py    # the engine contract, run on dist/ in pytest
```

`model.mjs` is pure and imports no SDK: it shapes normalized tool data into rows and filters,
so it can be shared with `viewers/` later. `bridge.mjs` owns SDK integration and normalizes MCP
results before passing data to the model. Nothing under `panels/` is packaged into the plugin,
so a panel change needs no plugin version bump until the "Afterwards" step below.

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

These are protocol responsibilities delegated to the SDK, not messages to implement by hand.
Verify the pinned SDK against the spec version the target host implements in increment 2.

**Decision for increment 2 — SDK selected by Marty Bradley, 2026-10-23.** Use the official
`@modelcontextprotocol/ext-apps` SDK behind a small `bridge.mjs` adapter. Start with exact version
`2.0.3`, the version measured during review; pin the build tool and commit the dependency lock.
Use the app-side SDK with a vanilla JavaScript UI. The SDK and all dependencies are bundled
locally into the HTML; no CDN or runtime package loading is introduced.

The adapter owns initialization, host context, tool-result normalization and the three allowed
read calls, plus opening record links and the optional conversation hand-back. Register result
handlers before connecting; handle transport failures and tool-result errors separately. Keep
the SDK instance private to the adapter and expose named application operations, rather than an
unrestricted tool-call method. The SDK handles protocol transport and lifecycle; application
state, loading, errors and selection remain panel responsibilities.

Increment 2 proves a minimal panel in Claude Desktop before the full page is built: receive the
initial result, make a detail call through the host, follow theme changes and resize. Test the
hand-back and its rejection path if Q4 puts it in v1. Record the host and SDK versions. A mock
host supports repeatable tests, but does not replace this early integration check or the final
release check in increment 6.

### Required engine bundle-budget change

The existing **256,000-byte** ceiling does not fit the straightforward SDK builds measured in
the 2026-10-23 review. A minimal app exercising the planned bridge methods, bundled with esbuild
`0.28.2`, minification and tree shaking, produced:

| SDK 2.0.3 entry point | JavaScript bytes, before panel markup and styles |
|---|---:|
| `@modelcontextprotocol/ext-apps` | 601,224 |
| `@modelcontextprotocol/ext-apps/app-with-deps` | 455,884 |

These are probe results, not the final release size or a host performance measurement. Both
builds passed the forbidden engine-tool identifier scan. Increment 2 records the selected entry
point, dependency lock, reproducible build command and complete HTML byte count.

**Proposed new ceiling: 1 MiB (1,048,576 bytes) for the complete, uncompressed HTML file.** This
is a pending cross-repository contract change, not an existing engine allowance. Before the SDK
panel can be pinned or the early engine/host check can pass, discovery-engine must update its
loader limit, boundary tests, API handoff and feature 27 budget documentation. Update
`panels/BRAND.md`'s size constraint and this repository's contract test to the same agreed limit.
Keep the single-file, UTF-8, hash verification, no-external-requests and allowed-tool rules.

Do not fall back to a hand-written bridge merely to pass the old limit. If the budget change
cannot proceed, revisit that constraint explicitly; the selected implementation remains the SDK.

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
- `dist/opportunities.html` is valid UTF-8 and within the **agreed engine byte limit**. The
  current limit is 256,000 bytes; the SDK plan proposes 1,048,576 bytes as described above.
  The panel test must match the engine's revised limit before release, including boundary cases.
- **No external requests:** no `http(s)://` in `src`, `href` (except record links opened through
  `ui/open-link`), `@import`, `url(…)` or `fetch(`; no `<link rel=stylesheet>`; no web fonts.
- **Tool names:** names `list_opportunities`, `get_problem` and `list_evidence`, and **none** of
  the engine's other tools. That means no other tool name as a whole identifier anywhere in the
  file, comments and bundled code included. The forbidden list mirrors discovery-engine's
  `src/engine/api/mcp/panels.py` `ENGINE_TOOL_NAMES`; the test cites that file so the two are
  updated together.
- After `npm ci` in `panels/opportunities/`, `node build.mjs --check` passes: the committed
  `dist/` is what the locked source and dependencies build. This and the model's `node --test`
  need their own `validate.yml` steps, added in increment 4; the existing Node steps cover only
  `viewers/`.

## Increments and acceptance

| Increment | Result | Completion evidence |
|---|---|---|
| 1 — Brand and plan | `panels/BRAND.md`; this plan | Reviewed and merged |
| 2 — SDK integration, model and fixtures | Pinned SDK/build dependencies, minimal `bridge.mjs` and `build.mjs`, early Claude Desktop check after the engine budget change; `model.mjs` (rows, filters, sort, paging state, provenance); domain fixtures from the engine's published samples plus actual MCP result/error fixtures | Reproducible full HTML byte count; initial result, detail call, theme and resize work in the real host; hand-back if Q4 includes it; `node --test panels/opportunities/model.test.mjs`; fixtures cite source paths and SHA-256 |
| 3 — Page and interactions | `template.html`, `app.mjs`, `style.css`, completed `bridge.mjs` and `build.mjs` producing `dist/opportunities.html`; a mock-host page for local checks | `check-page.mjs` drives the mock host with Playwright (reusing the journey viewer's pinned install): open, filter, drill in, error and empty states, a partial host-context update, keyboard only; hand back **only if Q4 put it in v1**, asserting the exact `ui/message` payload; light and dark screenshots |
| 4 — Contract test and CI | `tests/test_panel_contract.py`; **new `validate.yml` steps** for panel `npm ci`, `node panels/opportunities/build.mjs --check` and `node --test panels/opportunities/model.test.mjs`. Today's Node steps test only the viewers | Each check proven able to fail (a planted forbidden name, an external URL, an oversized file, a stale `dist/`); the increment is not done until the new steps run on a PR |
| 5 — Release | Tag `panels-opportunities-v<version>`; `gh release` with `opportunities.html` and its SHA-256 in the notes | Release published; SHA-256 recomputed from the downloaded asset |
| 6 — Pin and verify in a host | discovery-engine bump PR (its `DEPLOYMENT.md` part F1); the engine run with `ENGINE_MCP_PANELS_ENABLED=true` (stdio for Claude Desktop, or the hosted engine via F2) | `/health` shows `bound` at the release version; the panel renders in Claude Desktop in light and dark; drill-in works against the real engine, and hand-back works if Q4 includes it |

The published domain samples use REST envelopes (`{data, error}`). MCP `structuredContent`
corresponds to their `data` field. Include captured MCP results and errors in the bridge/mock-host
fixtures so the tests verify this boundary rather than passing REST envelopes directly to the UI.

**Afterwards:** update the "Native in-chat panel (MCP App): Not available" row in
`plugins/aipos/references/panel-contract.md`, which is a plugin change and needs a version bump.
Tell the skills that call `list_opportunities` that a panel may be showing.

## For the demo

Increments 2–6 must land, in order. The engine budget change is a prerequisite for increment 2's
real-host check; the final demo also needs the release pin (6) and the switch. For a local demo
in Claude Desktop, the engine's server entry in
`~/Library/Application Support/Claude/claude_desktop_config.json` needs these in its `env`:
- `ENGINE_MCP_PANELS_ENABLED=true`;
- `ENGINE_MCP_TOKEN`;
- `JWT_SECRET_KEY`, equal to the secret the token was minted with. The stdio server reads `.env`
  only from its working directory.

## Open questions

1. Land the engine budget change for the selected SDK: proposed ceiling 1 MiB; confirm the
   complete bundle size and host loading in increment 2. The bridge implementation is decided.
2. The official SVG artwork for the mark (`BRAND.md` "Open items"). The panel ships without a mark
   until it arrives.
3. Brand book discrepancies for the brand owner (`BRAND.md` "Source notes"): the secondary blue
   and yellow RGB values against their hex codes, and the wordmark minimum size.
4. **Hand-back in v1, or read-only browsing first? Decide before increment 2**, because
   increment 3's tests depend on it. If yes, increment 2 also defines the `ui/message` payload
   and the receiving skill's contract.
5. Which host versions to verify against: Claude Desktop is the demo host; check whether Claude
   Code renders MCP App panels before relying on it.
