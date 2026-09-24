# Opportunity source — reading the Product Definition Graph

> Where the canvas's facts come from. With the graph connected, panels 1 and 2 become a
> *confirm* conversation and the facts on the canvas are traceable to tool calls. Without it,
> the PM's account is the only source, and the canvas says so on its face.

The reference server is the Discovery Engine's `opportunity-engine` read server: seven read tools
over the Product Definition Graph (PDG), the same vocabulary `aipos-exploration-planning` uses. It
**writes nothing**, and this skill never tries to write to it.

## Contents

- [Detecting the graph](#detecting-the-graph)
- [Choosing the problem](#choosing-the-problem)
- [The read sequence](#the-read-sequence)
- [Evidence text — sparingly](#evidence-text--sparingly)
- [Errors and what they mean](#errors-and-what-they-mean)
- [Filling the `source` block](#filling-the-source-block)
- [Refresh on resume](#refresh-on-resume)
- [No graph — the PM-interview path](#no-graph--the-pm-interview-path)

## Detecting the graph

Detect by **tool signature, not server name**. The graph is connected when one server prefix
exposes `get_problem`, `list_evidence` and `get_lineage`. `get_evidence_text` is optional — the
engine does not advertise it at all when evidence text is unconfigured — so its absence means *no
excerpts*, not *no graph*. `get_work_item_links` may be advertised but answer `LINKS_UNAVAILABLE`.

- **More than one server matches** (say, a live engine and the mock): name both and ask which to
  read. Never mix reads from two servers in one canvas.
- **The mock** (`opportunity-engine-mock`, or any server whose records carry `fixture:` IDs and
  `[SYNTHETIC]` text) is for development and evaluation. Say so once — *"this is the mock graph;
  everything it returns is synthetic"* — and record the server in `source.server`. The renderer
  banners a synthetic canvas.

## Choosing the problem

An opportunity **is** a scored problem: `list_opportunities` rows are keyed by `problem_id`, one
to one. A canvas is always about exactly one `problem_id`.

| The PM gives | Do |
|---|---|
| A `problem_id` | Use it |
| A name or description | `list_problems` (page with `offset`/`limit`, max 100), match on title, confirm the match |
| Nothing | `list_opportunities` (top 10) and show the picker below |

**The picker** — one line per row: rank, title, composite score, whether it is already promoted
(active `promoted` link), and the weakest score component read as a signal for the canvas:

| Low component | What the canvas will find |
|---|---|
| `evidence_strength` | Panel 2 will be thin — the problem itself may still need confirming |
| `revenue_impact` | Impact at scale will likely be a formula, not a number |
| `persona_breadth` | One role carries the pain — or breadth is untested |
| `recency` | Evidence is aging; check dates before relying on it |
| `validation_signal` | Nothing has met a user yet; panel 6's plan carries the weight |

Read components as signals, never recompute or second-guess the ranking — the graph owns its
ranking. Skip any row whose `schema_version` is not `1`, and say it was skipped and why.

## The read sequence

For the chosen `problem_id`, in this order:

1. **`get_work_item_links`** — before facilitating anything. If `promoted` is true or an active
   link exists, say so first: *"This is already promoted to OPP-12 in Aha!. Update the canvas that
   goes with it, or start a new one?"* `LINKS_UNAVAILABLE` means **unknown**, not "not promoted" —
   record `promoted: null` and say you could not check.
2. **`get_problem`** — title, `composite_score`, personas with confidence, evidence references.
   The title is the engine's label for the problem, not a problem statement; panel 1's statement
   is still the PM's to write.
3. **`list_evidence`** — the primary evidence read: qualified `provenance_reference`
   (`<source_system>:<id>`), `source_type`, `occurred_at` (nullable — **null is unknown, not
   old**), `record_url` (nullable).
4. **`get_lineage`** — `originating_sources`, for breadth. Several references tracing to one
   source is one source; five ranked problems from one call is one call.
5. **`get_evidence_text`** — only on demand, below.

Check `schema_version` on every record: on `get_problem`, `get_lineage` and `get_work_item_links`
it is on the response; on `list_evidence`, `list_problems` and `list_opportunities` it is on each item
(the list wrapper has none). Anything other than `1` on the chosen problem or its evidence: stop and
say the graph is serving a version this skill does not understand. Do not guess the shape.

Summarise the read back to the PM before panel 1 — what the graph holds and, just as important,
what it does not:

> The graph links 8 pieces of evidence to this problem: 3 interview notes (July), 3 tickets
> (August), 1 customer call (June) and a time study with no date. Three roles: Support Agent (0.91),
> Support Team Lead (0.74), Enterprise Admin (0.52). It holds no ticket volume and no triage-time
> figure I can read — those will be gaps unless you know where they live.

## Evidence text — sparingly

`get_evidence_text` is a **person-adjacent disclosure**: the engine access-logs every call,
including refused ones. Fetch an excerpt only when a panel needs exact words:

- up to 3 records for panel 1's current-state snapshot — the same excerpts back panel 1's pain
  points, so no separate fetch is needed for them — and
- 1–2 for panel 2's quote.

Default cap: **5 per canvas**. Pass `problem_id` so the excerpt is anchored on the problem.
Prefer source types that carry text (call transcripts, tickets); records such as ReOps interview
notes and study outcomes have no text adapter and will answer `EVIDENCE_TEXT_UNAVAILABLE`.

Show the PM only the fragment you propose to use, and ask before it goes on the canvas — the canvas
is shareable. Never paraphrase an excerpt into a finding it does not state, and never paraphrase a
record you could not read.

## Errors and what they mean

Errors arrive as tool results reading `<CODE>: <message>`.

| Code | Meaning | Do |
|---|---|---|
| `PROBLEM_NOT_FOUND` | No such `problem_id` | Say so; offer the picker |
| `VALIDATION_ERROR` | A bad argument (limit outside 1–100, malformed reference, a list where one reference belongs) | Fix the call; don't retry blind |
| `EVIDENCE_TEXT_UNAVAILABLE` | The reference is not held, or its source has no readable text | Say *"the graph links it, but its text isn't readable through the graph"*; use the record as linked evidence only |
| `LINKS_UNAVAILABLE` | Links are not configured | `promoted: null` — unknown |
| `INVALID_TOKEN`, `INSUFFICIENT_SCOPE` | Access problem | Stop graph reads; say what is missing; offer the PM-interview path |

## Filling the `source` block

Copy values exactly as returned — the verifier checks every `[E]` against this block
(`canvas-schema.md`):

| `source` key | From |
|---|---|
| `kind` | `"opportunity-engine"` |
| `server` | the tool prefix you read from |
| `schema_version`, `problem_id`, `title`, `composite_score`, `personas` | `get_problem` |
| `components` | the problem's `list_opportunities` row, when read |
| `evidence_refs[]` | `list_evidence` items: `provenance_reference`, `source_system`, `source_type`, `occurred_at`, `record_url` |
| `originating_sources` | `get_lineage` |
| `excerpts[]` | each `get_evidence_text` result actually used: `provenance_reference`, `excerpt` → `text`, `anchored`, `redaction_applied` |
| `work_items[]`, `promoted` | `get_work_item_links` (`promoted: null` when unavailable) |
| `read_at` | the time of this read, ISO 8601 |

## Refresh on resume

Reopening a saved canvas starts with a fresh read — the graph may have moved since `read_at`.

1. Re-run the read sequence (links, problem, evidence, lineage). Do not re-fetch excerpts already
   in `source.excerpts` unless the PM asks.
2. Report the delta in plain words: new evidence (with dates), removed evidence, persona changes,
   a new promotion. Evidence that disappeared from the graph can no longer back an `[E]` — the
   verifier will say which fields lost their footing.
3. For each open evidence GAP, look at the new references. A GAP closes when a graph record carries
   the value — an excerpt that states it: quote the fragment, cite the reference, mark it `[E]`.

**Transcribed values (`[T]`).** A record the graph links but can't show as text (a ReOps study
outcome, say) may carry the value behind its `record_url`. The PM may read it from there — in any
session, not just on resume — and it is recorded `[T]`, citing that reference, with `note: "read
from <record_url> by <who> on <date>"`. This is the one place a person keys a number in. A `[T]`
value is traceable and it computes, so the formulas resolve — but it is **not graph-backed**:
Proceed stays unavailable until the graph itself carries the value. Close the GAP's to-do only if
the PM agrees the transcription is enough; otherwise keep the to-do open to get it into the graph.
4. Close the to-do for every GAP that filled, update `read_at`, run the verifier, and tell the PM
   which numbers resolved — the formula that became a figure is the news.

## No graph — the PM-interview path

If no server matches the signature (or access fails), say once:

> I can't reach the Product Definition Graph from here, so this canvas will rest on your account.
> That's a legitimate start — it'll say so on its face, and Proceed won't be available until it's
> rebuilt from the graph.

Then run the facilitation with `source.kind: "pm-interview"`:

- Facts come from the PM, recorded `[I]` with a `note` saying whose account it is. These **are**
  computed with — the arithmetic is still checked — but none is graph-backed. Anything the PM
  doesn't know is an evidence GAP with a ReOps to-do, exactly as on a graph canvas.
- No quotes, no snapshot examples and no panel 2 — there are no excerpts to take them from verbatim.
- Proceed is unavailable: nothing is graph-backed. Pivot and Park remain.
- Once the graph is reachable, a resume rebuilds `source` from it and re-grounds each fact.
