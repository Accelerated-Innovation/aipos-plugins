# Facilitation — running the canvas, panel by panel

> The interview that fills the canvas. The same steps run live in a workshop and one-to-one with a
> PM; the pace and the tolerance for gaps change, the artifact does not.

Read alongside `panel-rubrics.md` (the quality bar for each panel), `canvas-schema.md` (what gets
recorded) and `opportunity-source.md` (reading the graph).

## Contents

- [Two modes](#two-modes)
- [How every step runs](#how-every-step-runs)
- [Step 0 — Set up](#step-0--set-up)
- [Steps 1–6 — The panels](#steps-16--the-panels)
- [Step 7 — Footer](#step-7--footer)
- [Step 8 — Review and approve](#step-8--review-and-approve)
- [Step 9 — Render](#step-9--render)
- [Step 10 — Save and hand off](#step-10--save-and-hand-off)
- [Resuming a canvas](#resuming-a-canvas)

## Two modes

Ask once at the start, unless the request already says: *"we're in the workshop now"* → workshop;
*"help me put together the canvas for…"* → coach.

> Are we running this live with a room, or working through it together at your pace?

| | **Workshop** — live, facilitated | **Coach** — one PM, async |
|---|---|---|
| Pace | One panel at a time; several questions per panel are fine | One primary question at a time |
| Pushing | At most once per item; then record it and move | Once per adjective or missing measure; up to twice on framing |
| Gaps | Accepted and shown as `GAP` chips; the room keeps moving | Pushed on; a decision GAP blocks the final render unless the PM accepts it |
| Draft renders | Any time — after any panel, so the room watches it build | On request; the final render after review |
| Ends with | The GAP list turned into named follow-ups | A canvas that passes its rubrics, or explicitly accepted gaps |

Record the mode in `canvas.json`. A workshop canvas can be resumed later in coach mode to close its
gaps.

## How every step runs

The same rhythm as `aipos-epic-create`:

1. **Propose from what's known, then ask.** If the graph answers it, summarise and ask the PM to
   correct you — never ask for something the read already holds.
2. **Push per `panel-rubrics.md`** — once, with the script, then accept the answer. This skill
   coaches; it does not block.
3. **Record it** in `canvas.json` as a fact or a decision, with its status. Anything Claude drafted
   is `provisional` until the PM confirms it.
4. **Set `through_panel`** to the step just finished (1–6 panels, 7 footer, 8 reviewed) and **run the
   verifier** from the project folder:
   `python3 <skill-folder>/scripts/verify_canvas.py solution-design/<slug>/canvas.json --write`
   (`<skill-folder>` is the folder this SKILL.md is in). It checks only the panels reached, so an
   error is always about something already on the canvas. Translate it into one plain sentence —
   never read out a code. *"The −30% target and the 1.2-minute target
   disagree: from 1.8 that's −33%. Which did you mean?"*
5. **Summarise in two or three lines and default forward.** Silence is agreement; a correction is
   the point of the step.

**Proceed protocol.** *proceed, continue, looks good, yes, go* confirm the latest summary. Where
options were offered, the option's name, number or *default* chooses it. A bare "proceed" never
authorizes a write to a tracker (Step 10).

**Open questions** go into `open_questions` as they come up, not at the end.

**When a fact is missing,** don't ask the PM for it. Ask what would settle it and where it would come
from, create the GAP with its to-do on the spot (`panel-rubrics.md`, *The one rule*), and carry on.
Its assumption and plan item are completed in Steps 5 and 6 — keep a running list so none is
forgotten.

## Step 0 — Set up

In this order, briefly:

1. **Mode** — above.
2. **The graph** — detect it and choose the problem (`opportunity-source.md`). No graph → say so
   once and take the PM-interview path.
3. **An existing canvas?** Now that the problem is known, look for
   `solution-design/<slug>/canvas.json` in the project folder (slug rules in `canvas-schema.md`; on
   the no-graph path, ask whether an earlier canvas exists). If one exists, go to
   [Resuming a canvas](#resuming-a-canvas).
4. **Already promoted?** From `get_work_item_links`: say so before anything else, and ask whether
   this canvas updates the one that goes with it or starts fresh.
5. **Read and summarise** what the graph holds and what it doesn't.
6. **GenAI check** — silently, with the keyword and behaviour list shared with `aipos-epic-create`
   (AI, LLM, RAG, classifier, summarisation, assistant, agent, retrieval, generation, reasoning…).
   If it applies, say once: *"This involves model behaviour, so panel 6 will carry evaluation
   criteria — and anything built under this Initiative inherits them."*
7. **Title and goal** — propose both from the graph's title, in outcome terms: *"Reduce triage time
   and improve first-contact routing"*, not *"Triage improvements"*. One push on a title that names
   an area instead of an outcome.
8. **Where it's kept** — once: *"I'll keep the canvas in `solution-design/<slug>/` in this project
   as we go, so we can pick it up later. OK?"* Local files need one confirmation for the set; trackers
   are Step 10. Freeze the slug now; it never changes.

*Writes:* `canvas_version: 1`, `mode`, `stage: "draft"`, `through_panel: 0`, `slug`, `genai`,
`gaps_accepted: false`, `title`, `goal`, the whole `source` block, `todos: []`,
`open_questions: []`.

## Steps 1–6 — The panels

Each step fills one panel. `panel-rubrics.md` holds the quality bar, push scripts and common defects
for each; this is the order and what to propose.

### Step 1 — Problem & Context

1. **Personas.** Show the graph's personas with confidence and ask which suffers most — that is the
   primary. Lock them once confirmed.
2. **Pain points.** Propose 1–3 from what the graph actually says: the problem's **title** (the
   engine's own extraction from its evidence — record it `[I]`, `refs` = the problem's evidence
   references, `note: "engine problem title"`) and the **excerpts** you fetch for the snapshot
   (`[E]`). Nothing else holds text, so nothing else can back a pain point; never paraphrase a record
   you haven't read. If the PM names a pain the graph doesn't show, it's an evidence GAP.
3. **Current-state snapshot.** Offer 2–3 records with readable text (fetch excerpts now, within the
   cap). Show the proposed label for each and get approval — they will appear on a shared page.
4. **Impact.** What the graph shows it costs people. A number only if a record states one; otherwise
   an evidence GAP.
5. **Statement.** Draft *the problem of [X] affects [Y], resulting in [Z], and solving it will lead
   to [benefits]* as `provisional`; run the solution-in-problem test on it; confirm.

Don't leave Step 1 while the statement contains a solution or names no sufferer — everything
downstream inherits it.

*Writes:* `panels.problem` — `personas {primary, others, locked}`, `pain_points[]`,
`snapshot[] {ref, label, approved_for_canvas}`, `impact[]`, `statement {problem, affects,
resulting_in, benefits}`; each fetched excerpt into `source.excerpts[]`; `through_panel: 1`.

### Step 2 — Discovery Evidence

1. **Tiles.** Group the evidence by source type and propose up to four tiles, each with a finding
   phrased as what the graph establishes. Counts and dates are the verifier's, not yours.
2. **Breadth and age.** Say plainly if everything traces to one source, or if the newest evidence is
   older than 18 months. Name undated evidence as undated.
3. **Voice of customer.** Propose one quote from an excerpt, verbatim, attributed to source and date.
   Ask before it goes on.

No graph: skip this panel — say it stays empty until the canvas is rebuilt from the graph.

*Writes:* `panels.evidence` — `tiles[] {label, refs[], finding}`, `voice {provenance_reference,
quote, approved_for_canvas}` or null; `through_panel: 2`.

### Step 3 — Hypothesis & Expected Outcomes

1. **The primary metric first.** *"What's the one number the decision turns on?"*
2. **Its baseline** — from the graph, or an evidence GAP with its to-do.
3. **Its target** — the PM's decision, absolute or % (and for a % metric, relative or points).
4. **Up to two more outcomes**, including a counter-metric if the *without* clause needs one.
5. **The hypothesis** — draft *If …, then …, without …* from the answers; each field carries its
   own subject ("we suggest the right category at intake"). Confirm it.

*Writes:* `panels.metrics[] {id, name, unit, direction, primary, counter, baseline, target and/or
target_change_pct, target_change_kind (on % metrics), observation}`; `panels.hypothesis {if, then,
without, outcomes[]}`; for each missing baseline, a GAP plus its `todos[]` entry
`{id, field, action, measure, source_type, window, intake_route: "reops", destination, status:
"open", reops_draft}`; `through_panel: 3`.

### Step 4 — Solution Options

1. If the PM arrived with a solution, record it as option A — theirs.
2. Ask for alternatives before offering any (`panel-rubrics.md` scripts). Propose one only to fill a
   gap in the spread, and mark it provisional.
3. For each: approach, preview (what the user sees), a pro, an honest con, the outcomes it moves.
4. Recommended option — optional. If chosen, tie it to the riskiest assumption.

*Writes:* `panels.options[] {id, name, approach, preview[], pros[], cons[], moves[]}`;
`panels.recommended_option` (an id or null); `through_panel: 4`.

### Step 5 — Assumptions & Risks

1. **Seed from the gaps.** Every evidence GAP so far becomes an assumption, pre-filled — show them.
2. **The data assumption** — always present: the data the options need exists, is representative,
   and can be used.
3. **More assumptions** — what would have to be true for the recommended option to work?
4. **Risks with mitigations**, walking the categories if the PM stalls. A risk with no credible
   mitigation is recorded as unmitigated, plainly.

*Writes:* `panels.assumptions[] {id, text, from_gap (the GAP's path, or null), retired_by[]}`;
`panels.risks[] {id, text, mitigation | null}`; `through_panel: 5`.

### Step 6 — Validation & Decision

1. **Plan the evidence first.** One plan item per evidence GAP, from its to-do — cheap, and it
   unlocks the numbers. Owners and dates are the PM's.
2. **Then the test** — usually a pilot of the recommended option against the primary metric, with a
   comparison and a duration.
3. **Check every assumption is retired** by some plan item.
4. **The recommendation.** Ask who makes the call; then which of Proceed / Pivot / Park to recommend
   to them, and why, in a line. If Proceed is unavailable, say so before it's chosen:
   > Proceed isn't available yet — the triage-time baseline isn't in the graph. Pivot or Park, or
   > leave the recommendation open until the baseline arrives?
5. **GenAI** — evaluation criteria with thresholds; say that work under this Initiative inherits them.

*Writes:* `panels.validation.plan[] {id, action, owner, by, retires[], todo}` and each assumption's
`retired_by[]` (either side counts; keep both in step); `panels.validation.recommendation {decision,
owner, rationale}`; `genai_criteria[]` in GenAI mode; `through_panel: 6`.

## Step 7 — Footer

- **Who benefits** — the panel-1 personas.
- **Success looks like** — one line mirroring the outcomes. No numbers in the prose.
- **Impact at scale** — volume from the graph or a GAP; the verifier derives minutes → hours itself
  (give `per_unit_factor` only for other conversions) and computes the rest. Show the formula if an input is a GAP: *"0.6 minutes × GAP tickets ÷ 60 — it becomes a
  number when volume is in the graph."*

*Writes:* `footer {who_benefits[], success, scale {volume, volume_unit, result_unit}}`;
`through_panel: 7`.

## Step 8 — Review and approve

1. Run the verifier. Resolve every error with the PM, in plain words.
2. Run the coherence checks (`panel-rubrics.md`, *Across the panels*). One line per break.
3. Confirm or change everything still `provisional`.
4. Coach mode: remaining decision GAPs are either closed or explicitly accepted (`gaps_accepted`).
5. Read back the three-line summary: what the canvas recommends and to whom, the GAP that most
   blocks the decision, and the first to-do.
6. Ask one question: *"Approve the canvas as it stands?"* Only an answer to **that** question — "approve",
   "yes, approve", "approved" — sets `through_panel: 8` and `stage: "approved"`. A "proceed" or "looks
   good" to the summary does not; approval freezes the canvas, so it is asked for by name. Approving
   the content is not approval to write anywhere outside the project folder.

## Step 9 — Render

```bash
python3 <skill-folder>/scripts/render_canvas.py solution-design/<slug>/canvas.json
```

Writes `canvas.html`, and `canvas.png` / `canvas.pdf` when a headless browser is available (the
script says which it produced). The renderer reads numbers only from `computed`, so run the verifier
first. Look at the PNG before handing it over — if a panel overflows or a chip is unreadable, fix the
content, not the picture. If no browser was found and only `canvas.html` exists, say so: the layout
has **not** been checked, and the PM should open the HTML to look. Never say you looked at an image
that wasn't produced.

Workshop: render a draft after any panel on request; drafts carry a DRAFT banner. A canvas built from
the mock graph carries a SYNTHETIC banner, always.

## Step 10 — Save and hand off

**The project folder** (`solution-design/<slug>/`): `canvas.json`, the render, and **always**
`todo.md` — every open evidence to-do, whatever happens with a ticket. Never overwrite an approved canvas — a re-run writes
`canvas-<YYYY-MM-DD>.json` beside it.

**The ReOps to-dos.** For each evidence GAP, hand the PM the drafted intake request (project name,
background, need, target personas) ready to submit. This skill drafts; a person submits.

**A linked Jira or Aha! ticket** (from `get_work_item_links`, or one the PM names): offer write-back
**once**, in one prompt, naming the ticket. Follow the canonical update protocol in
`../../aipos-feature-create/references/tracker-adapters.md` — preview the exact text, name the
destination, one explicit yes per record, read back, report either way — and the three pieces of
`../../aipos-rapid-validation/references/record-writeback.md`:

1. **Attachment** — neither connector uploads files. Hand it over by exact filename:
   *"Attach `canvas.pdf` to OPP-12 — I can't upload files myself."* Fallback: the canvas summary plus
   `canvas.json` as a second comment — with `source.excerpts` removed first; evidence text is an
   access-logged disclosure and does not go into a tracker.
2. **Index comment** — dated first line; the problem statement; the hypothesis; the primary metric
   baseline → target (or its formula); the recommendation and to whom; the evidence-base line
   (references read, originating sources, aging); open GAPs.
3. **To-do** — only when panel 6 has a pilot with an owner and a date: its actions, in order.

Where the protocols differ, the stricter one wins: **one explicit yes per record, per write**
(tracker-adapters). An earlier yes in the session does not carry over to a different record or a
different piece.

No linked ticket → the folder is the record; don't raise trackers at all. **The graph is read-only**:
nothing is written back to it.

Close by naming the next step: `aipos-rapid-validation` runs the panel-6 plan and turns its results
into a viability brief; `aipos-epic-create` can take panel 1's statement and panel 3's metrics into an
epic when one is wanted.

## Resuming a canvas

1. Read `canvas.json` and summarise where it stands: mode, stage, open GAPs, open to-dos.
2. **Refresh from the graph** (`opportunity-source.md`, *Refresh on resume*) and report what changed.
3. Run the verifier; report which numbers resolved.
4. Continue at the first panel that doesn't meet its quality bar — or, in coach mode after a
   workshop, work through the GAP list.

An approved canvas reopened for changes becomes a new dated draft; the approved one stays as it was.
