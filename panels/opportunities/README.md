# Opportunities panel

The MCP App panel that discovery-engine serves as `ui://aipos/opportunities` beside
`list_opportunities`, laid out as the "Explore the Opportunities" screen of the AIPOS prototype: a
ranked list with title search, a semantic search over the engine's `find_similar_problems`, and a
side panel for the opened opportunity (score, the five components, personas, evidence references
grouped by source type with their record links). Its one write-shaped action, Add Opportunity,
hands a plain user message to the conversation (`ui/message`); the conversation chooses the
tracker (Aha!, Jira, ...) from what the user has connected, never this panel. Plan, decisions and status:
[`docs/plans/2026-10-23-opportunities-panel.md`](../../docs/plans/2026-10-23-opportunities-panel.md).
Brand rules and the PR checklist: [`panels/BRAND.md`](../BRAND.md).

| File | Role |
|---|---|
| `model.mjs` | Pure shaping: rows, paging, filters, sort, provenance, host-context merge, colour checks. No SDK |
| `bridge.mjs` | The only code that touches the MCP Apps SDK. It offers named reads, `openLink` and `sendMessage`, and returns normalized results |
| `app.mjs`, `template.html`, `style.css` | The page, in vanilla DOM |
| `build.mjs` | Bundles everything, the SDK included, into `dist/opportunities.html` with licence notices |
| `dist/opportunities.html` | The committed build, which is what a release publishes |
| `fixtures/` | The engine's published samples, plus MCP results captured from its server (`capture_mcp.py`) |
| `mock-host.mjs`, `mock-scenarios.mjs`, `check-page.mjs` | A local host on the SDK's `AppBridge`, its fixtures, and the checks that drive it in Chrome |
| `dev.mjs` | The dev server for UI work: the panel in the mock host on localhost, rebuilt and reloaded on save |

```sh
cd panels/opportunities
npm ci                          # exact SDK and esbuild versions from the lockfile
npm run dev                     # http://localhost:5173 (PORT to change); reloads on save
npm test                        # model and bridge tests (node --test)
node build.mjs                  # rebuild dist/; prints bytes and SHA-256
node build.mjs --check          # CI: the committed dist/ matches the source
node check-page.mjs /tmp/shots  # Chrome via the journey viewer's Playwright; writes screenshots
python -m pytest ../../tests/test_panel_contract.py -q   # the engine's release contract
```

The dev server builds in memory and never writes `dist/`; its toolbar picks a scenario (list,
paging, samples, slow reads, empty, refused, failed evidence, cancelled), a theme and a width. The
data is the captured fixtures, not a live engine. Run `node build.mjs` before committing.

`check-page.mjs` needs `viewers/journey/node_modules` (`npm ci` there) and Google Chrome, or
`PANEL_CHROME=/path/to/chrome` for another Chromium build.

To re-capture the MCP fixtures after an engine change, run `fixtures/capture_mcp.py` from a
discovery-engine checkout, as its docstring shows, and update `fixtures/SOURCES.json` if the
samples changed.

Nothing here is packaged into the plugin, so a panel change needs no plugin version bump.
