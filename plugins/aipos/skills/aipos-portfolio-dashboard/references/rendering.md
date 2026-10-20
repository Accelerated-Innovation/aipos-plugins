# Offline portfolio rendering

This renderer supports the complete synthetic Harborlight response fixtures and captured graph reads using contract
`demo-portfolio.v0.2`. It creates one self-contained HTML file with no external fonts, scripts,
data requests, model calls or network dependencies. Rendering needs no API token or graph access; capture does.

From the installed skill directory (substitute the actual absolute paths):

```sh
python scripts/render_dashboard.py /absolute/path/portfolio.json -o /absolute/path/harborlight.html
```

Use Python 3.11+. If the user explicitly wants the bundled demo, the input is
`evals/files/portfolio.json` relative to the skill directory. Do not use bundled examples as a
silent fallback for a failed live read. The output contains supplied fictional narrative bodies;
choose a local destination consistent with the user's request.

Open the generated file in a browser. It supports product/phase/disposition filters, title/ID
search, keyboard case selection, five detail tabs, and ten prepared portfolio queries. The
question box recognizes those queries and case IDs; it is guided snapshot chat, not a connection
to a general language model. Other questions are explicitly unsupported. Phase, disposition,
study completion, link state and commitment authorization remain separate.

The renderer checks complete pagination, metadata consistency, source snapshot digest and local
resource digests before writing output. Browser validation repeats consistency checks and adds
summary reconciliation. An imported invalid file hides the previous dashboard and shows a
failure. A valid replacement clears prior selection and conversation. Open snapshot reads a
local JSON file only; it does not refresh from a live service.

Validation limits: these checks establish fixture integrity and predictable presentation, not
the legal execution of transitions, backend persistence, authentication, REST/MCP parity, or
model answer quality. The capture exercises the explicitly selected MCP or REST transport. A native MCP App surface and open-ended model chat remain separate work.

## Refresh from the local graph

The read-only capture helper defaults to the three existing MCP tools over streamable HTTP.
Install `scripts/requirements.txt` in the Python interpreter used for MCP capture (Python 3.11+).
The renderer and explicit `--transport rest` mode still need only the standard library. It accepts a loopback HTTP base with an explicit port, rejects
redirects, and needs an existing bearer token in `ENGINE_DEMO_TOKEN` (or `--token-env NAME`).
Use the engine operator's token command or the host's configured auth flow; do not print the
token or embed it in the snapshot/HTML. From the skill directory:

```sh
python scripts/capture_portfolio.py --transport mcp --api-base http://127.0.0.1:18000 \
  --dataset harborlight-insurance-v1 --resources /absolute/demo/resources.json \
  -o /absolute/harborlight-graph-snapshot.json
python scripts/render_dashboard.py /absolute/harborlight-graph-snapshot.json \
  -o /absolute/harborlight-portfolio.html
```

`--resources` is optional and must name a local JSON reference-to-body map explicitly supplied
for this demo (the engine's `demos/insurance/resources.json`). The helper verifies each included
body against the graph's digest. No arbitrary resource URLs are fetched. Without this file,
the dashboard still shows references and marks narrative bodies unavailable.

The MCP connection uses `/mcp/` on that base, discovers and verifies the three read-only tools,
and records the server name/version and negotiated protocol in the snapshot. It never calls
`/v1` routes in MCP mode. To explicitly use REST, pass `--transport rest`.

The helper exhausts pagination and fetches every detail, checks a final summary, and requires
identical metadata across all responses. A revision conflict discards the complete set and
retries once. Any remaining conflict, auth error or unavailable API stops the run; there is no
fixture fallback. The output is labeled as captured from the local graph, with capture time,
graph revision and separate snapshot checksum. It is a fixed capture; rerun these commands to
refresh. Guided answers query only that captured snapshot.


## Codex host connection

Configure the existing discovery-engine HTTP MCP endpoint in the host, allowing only
`get_demo_portfolio`, `list_demo_opportunities`, and `get_demo_opportunity`. For the local
Harborlight profile the engine operator command `python -m scripts.insurance_demo --local
auth-headers` emits the temporary Authorization header JSON consumed by Codex's
`http_headers_helper`. The command must run from the engine checkout with its interpreter.
No token belongs in the skill, dashboard, or checked-in host configuration. See the engine's
`demos/insurance/README.md` for the local configuration example and expiry behavior.

Host configuration and an SDK capture are distinct evidence. After configuring, verify that
the host discovers the three tools. An already-running chat may retain its previous tool
catalog; reload its MCP connection or reopen the chat when necessary. Do not claim a direct
host tool call occurred unless it actually did. A standalone SDK capture records MCP as its
transport but does not establish that the current chat has reloaded its tools.
