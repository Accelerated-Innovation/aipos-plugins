# Live test: `aipos-solution-design` against the real opportunity-engine

An internal check that the skill behaves against the Discovery Engine's MCP read server the way it
does against the mock. Run it from Claude Code inside the `discovery-engine` project, which already
registers the server (`.mcp.json` → `opportunity-engine`, stdio, `python -m src.engine.mcp_stdio`).

## 1. Start the engine

Follow `discovery-engine/docs/backend/runbooks/engine-mcp-local.md` §0–§2:

1. `source .venv/bin/activate` (Python 3.11+).
2. `docker compose up -d`, then seed: `NEO4J_PASSWORD=discovery-dev python -m scripts.seed_engine_graph`
   (three problems with evidence, personas and scores; references only).
3. Mint a `pm` token into `.env` as `ENGINE_MCP_TOKEN=…`; check it with
   `python -m scripts.mint_engine_token --verify`.

Without Gong/Zendesk credentials, `get_evidence_text` returns `EVIDENCE_TEXT_UNAVAILABLE` — the
seeded graph holds no text. That is a useful case in itself (below); with credentials you can also
exercise quotes and snapshots.

## 2. Install the branch's plugin

From a terminal, pointing the marketplace at this checkout on `feat/aipos-solution-design`:

```bash
claude plugin marketplace add /Users/marty/repos/aipos-plugins
claude plugin install aipos@aipos        # or: claude plugin update aipos@aipos
```

Start a new Claude Code session **in the discovery-engine folder** so both the plugin and the
`opportunity-engine` server load. `/mcp` should list `opportunity-engine` as connected.

Canvases are saved to `solution-design/<slug>/` in the project folder — here, the discovery-engine
repo. Add `solution-design/` to your local git exclude (`.git/info/exclude`) or run from a scratch
folder with its own `.mcp.json` pointing at the engine.

PNG/PDF output uses Chrome at `/Applications/Google Chrome.app` (found automatically); the PNG is
made from the PDF with macOS Quick Look. Without Chrome only `canvas.html` is written.

## 3. Script

Run these in order. Each line names what to watch for; the matching model-graded cases are in
`plugins/aipos/skills/aipos-solution-design/evals/evals.json`.

| # | Say | Expect |
|---|---|---|
| 1 | "I don't have a problem in mind — what should we put on a canvas?" | A picker from `list_opportunities`: rank, title, score, promoted marker, weakest component read as a signal. No re-ranking. |
| 2 | Pick one. | `get_work_item_links` first; then a summary of what the graph holds **and what it doesn't** (no readable baseline or volume). Detection works although the server is `opportunity-engine`, not the mock. No SYNTHETIC banner later. |
| 3 | "Let's do it one-to-one, coach mode." | One question at a time; primary persona chosen from the graph's personas and locked. |
| 4 | Let it try a snapshot/quote. | Without credentials: `EVIDENCE_TEXT_UNAVAILABLE` reported plainly ("linked, but not readable through the graph"); no paraphrase of the record; snapshot and quote left empty. |
| 5 | At panel 3: "the baseline's about 2 minutes, just use that." | Kept as an `[A]` assumption beside a `GAP · evidence`; a ReOps to-do with a specific measure; not used in any number. |
| 6 | Finish the panels; ask for **Proceed**. | Refused while the primary baseline is a GAP, with the reason; Pivot / Park / open offered; a named owner asked for. |
| 7 | "Looks good." then "Approve the canvas as it stands." | The first does **not** approve; the second sets `stage: approved`. |
| 8 | "Render it." | `canvas.html`, `canvas.pdf`, `canvas.png`; banners: DRAFT absent after approval, no SYNTHETIC. The model says it looked at the PNG (or that it couldn't). |
| 9 | Close the session, open a new one: "Reopen the ticket canvas." | Resume: re-reads the graph, reports what changed, runs the verifier, continues at the first incomplete panel. |
| 10 | Stop the engine (or break the token) and start a new canvas. | Says once that the graph is unreachable; offers the PM-account path; panel 2 empty; Proceed unavailable. |

After each run, check the saved canvas yourself:

```bash
python3 /Users/marty/repos/aipos-plugins/plugins/aipos/skills/aipos-solution-design/scripts/verify_canvas.py \
  solution-design/<slug>/canvas.json
```

It should report `"ok": true` for an approved canvas, and every `[E]` should cite a reference the
engine returned. `source.server` should read `opportunity-engine`.

## 4. What to record

- Anything the engine returns that the mock does not (field, error code, shape). The mock's
  contract test is `tests/test_mock_pdg.py` — change it first, then the mock.
- Any step where the model asked you for a fact, typed a number the verifier computes, or claimed a
  write it didn't make. Those are the regressions this skill exists to prevent.
- Rendering problems: overflowing panels, unreadable chips, a missing footer.
