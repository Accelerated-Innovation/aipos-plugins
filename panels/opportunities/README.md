# Opportunities panel

The MCP App panel that discovery-engine serves as `ui://aipos/opportunities` beside
`list_opportunities`. It is read-only: it browses the ranked list, filters and sorts it, loads more
pages, and drills into a problem's personas and evidence references. Plan, decisions and status:
[`docs/plans/2026-10-23-opportunities-panel.md`](../../docs/plans/2026-10-23-opportunities-panel.md).
Brand rules and the PR checklist: [`panels/BRAND.md`](../BRAND.md).

| File | Role |
|---|---|
| `model.mjs` | Pure shaping: rows, paging, filters, sort, provenance, host-context merge, colour checks. No SDK |
| `bridge.mjs` | The only code that touches the MCP Apps SDK. It offers named reads and returns normalized results |
| `app.mjs`, `template.html`, `style.css` | The page, in vanilla DOM |
| `build.mjs` | Bundles everything, the SDK included, into `dist/opportunities.html` with licence notices |
| `dist/opportunities.html` | The committed build, which is what a release publishes |
| `fixtures/` | The engine's published samples, plus MCP results captured from its server (`capture_mcp.py`) |
| `mock-host.mjs`, `check-page.mjs` | A local host on the SDK's `AppBridge`, driven in Chrome |

```sh
cd panels/opportunities
npm ci                          # exact SDK and esbuild versions from the lockfile
npm test                        # model and bridge tests (node --test)
node build.mjs                  # rebuild dist/; prints bytes and SHA-256
node build.mjs --check          # CI: the committed dist/ matches the source
node check-page.mjs /tmp/shots  # Chrome via the journey viewer's Playwright; writes screenshots
python -m pytest ../../tests/test_panel_contract.py -q   # the engine's release contract
```

`check-page.mjs` needs `viewers/journey/node_modules` (`npm ci` there) and Google Chrome.

To re-capture the MCP fixtures after an engine change, run `fixtures/capture_mcp.py` from a
discovery-engine checkout, as its docstring shows, and update `fixtures/SOURCES.json` if the
samples changed.

Nothing here is packaged into the plugin, so a panel change needs no plugin version bump.
