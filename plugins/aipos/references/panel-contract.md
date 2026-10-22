# Panel contract — shared rules for visual views

> **Shared reference.** One copy, read by every skill that offers a visual view of graph data
> (first: `aipos-problem-clustering`'s Cluster Review board). `aipos-portfolio-dashboard`'s
> offline dashboard predates this contract and is the same kind of view; it has not yet been
> reviewed against it. From a skill folder the path is
> `../../references/panel-contract.md`; under an installed plugin it is also
> `${CLAUDE_PLUGIN_ROOT}/references/panel-contract.md`. Skills cite this file; they do not
> restate it.

A view is worth offering only when the PM needs to **inspect, compare, edit or confirm**
something; text or a generated chart is enough otherwise. These rules keep a view from saying
more than the data behind it.

## What kind of view this is — say it

| Kind | What it is | Status today |
|---|---|---|
| **Offline snapshot** | One self-contained HTML file rendered by a bundled script from a capture, opened in a browser. No network, no live refresh, no writes. | What AIPOS ships (portfolio dashboard, Cluster Review board) |
| **Native in-chat panel (MCP App)** | A UI resource the MCP server publishes (`ui://…`, linked from a tool's `_meta.ui`) that an MCP-Apps-capable host renders inside the chat | **Not available.** The engine registers no UI resources (checked 2026-10-21); it needs engine and host work outside this repository |

Never call an offline snapshot an in-chat panel, a live view or a dashboard "connected to" the
graph. Say where it is (a file path) and how to open it (a browser).

### What a native panel would need (integration contract, not built)

For a future MCP App version of a view, the engine — not this plugin — must: register a UI
resource (`ui://aipos/<view>`) served with the MCP Apps mime type; reference it from the read
tool whose result the panel shows (`_meta.ui.resourceUri`); keep the tool's text result complete,
so hosts without MCP Apps lose nothing; and accept from the panel only the same read tools,
never a write. The host must advertise MCP Apps support and sandbox the panel. Until all of that
exists and is verified in a real host, the offline snapshot and the plain-text answer are the
only views.

## Host capability and the plain-text fallback

- Offer the offline snapshot only when the session can write a file and run the bundled Python
  script, and the user can open the file. Otherwise answer in plain text.
- The plain-text answer is complete on its own: every fact, reference and suggestion the view
  would show. A view adds layout and interaction, never information the text lacks.
- If rendering fails, say so and give the text answer; never describe a view that was not
  produced.

## Provenance on every view

- **Source mode** — `connected` (reads made in this session, naming the server) or `supplied`
  (records given to the session) — and **synthetic** when the records say so.
- **Capture time** (timezone-aware) and, when the server provides one, the graph revision or
  snapshot digest.
- **Coverage** — how many records were read out of how many, and which reads failed. A failed
  read is shown, never folded into "none".
- A **Draft** label on anything that proposes rather than records.

## Evidence text

- Evidence appears as provenance references. Text appears only as **redacted excerpts** the
  server returned with redaction applied, labelled as redacted, each traced to the reference it
  came from.
- **At most five excerpts per view** (the AIPOS convention; the engine also caps each excerpt at
  1,500 characters and logs every fetch). Fetch only the excerpts the view needs.
- Never reconstruct, expand or paraphrase redacted text into something closer to the original.

## Stale previews and the confirmation boundary

- A view states its capture time; past 24 hours it says the capture is stale and that the graph
  must be re-read before anyone relies on it.
- Anything a view lets the user **prepare** — a correction, a request — is **pending**: shown as
  not applied, carrying the capture it was based on, and handed to a person. A view never
  applies, sends or records anything.
- When a write path does exist (a later integration), it follows the full confirmation boundary
  in the conversation, not in the view: a full preview of exactly what will change, the exact
  destination, one explicit yes per write, then a read-back of what was recorded. A preview
  older than the current graph state is re-read before the yes is asked for.
