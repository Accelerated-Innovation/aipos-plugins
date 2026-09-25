# Plan: `aipos-solution-design` — the Solution Design canvas (replaces the Solution Blueprint)

**Date:** 2026-09-22
**Scope:** `plugins/aipos` — new skill `skills/aipos-solution-design/` (SKILL.md, `references/`,
`scripts/`, `evals/`); routing cases in `evals/routing`; the `Related` tables of `aipos-epic-create`
and `aipos-rapid-validation`; plugin README.
**Status legend:** `[ ]` not started · `[~]` in progress · `[x]` done
**Status: all increments implemented on `feat/aipos-solution-design`; ready for one PR.** `pytest tests` passes (553); routing dry run sees 12 skills; eval cases dry-run wired. **Not run:** model-graded evals, live routing, `claude plugin validate` (CI runs it), and a live test against the engine (`docs/testing/solution-framing-live-test.md`).

## Context

The Solution Design Workshop canvas (example: *Customer Support Ticket Triage*) is a one-page,
six-panel alignment artifact: Problem & Context → Discovery Evidence → Hypothesis → Solution
Options → Assumptions & Risks → Validation & Decision, with a footer of Who Benefits / Success
Looks Like / Impact at Scale.

It **replaces the parked Solution Blueprint** (the six-panel slide: users + JTBD, value
hypothesis, chosen solution + MVP, data/context needs, assumptions/risks + guardrails, success +
evaluation criteria). The Blueprint's granularity decision carries over: **one canvas per
Initiative**; each epic under it carries its own scoped problem statement.

Today the canvas is hand-made or image-generated. That means its numbers are transcribed, not
checked — and the example shows the cost (findings below).

## Findings from the example canvas

These are the failure modes the skill exists to catch; each becomes an eval fixture.

1. **Impact at scale contradicts the primary metric.** 1.8 → 1.2 min is 0.6 min saved, not 1 min;
   0.6 × 10,000 = 100 hrs/month, not 166.
2. **Target and metric disagree.** "Target: 30% reduction" vs 1.8 → 1.2 (a 33% reduction).
3. **Outcome with no baseline.** "+20% correct routing" — the audit's 32% recategorization rate
   is the obvious baseline and isn't used.
4. **Undated, unprovenanced evidence.** "6 agents interviewed", "200 tickets reviewed" carry no
   date or [E]/[I]/[A] mark.
5. **Decision pre-selected.** PROCEED is highlighted before the validation plan has run — the
   canvas should show the *recommended* decision and who makes it, not imply it was made.

## Reuse map — most rubrics already exist

| Canvas panel | Reuse (by pointer, not copy) | New in this skill |
|---|---|---|
| 1 Problem & Context | epic-create `problem-framing.md` — solution-in-problem test, root-cause probing, X/Y/Z statement, impact quantification | Current-state snapshot (2–3 real, anonymised examples) |
| 2 Discovery Evidence | rapid-validation `evidence-intake.md` — three paths, [E]/[I]/[A], dating | Four-tile evidence selection (strongest per type) |
| 3 Hypothesis + Expected Outcomes | epic-create `metrics-and-evaluation.md` — baseline/target/observation | "If we… then… without…" form; ≤3 outcomes |
| 4 Solution Options | — | **Option coaching:** 2–3 genuinely different options, each with a preview, pros, cons, and which outcome it moves |
| 5 Assumptions & Risks | epic-create Step 7 risk+mitigation pairs | Assumptions separated from risks; each assumption tagged with the panel-6 test that retires it |
| 6 Validation & Decision | rapid-validation Validation Decision (go/no-go/revise) | Pilot plan, primary metric baseline → target, Pivot/Proceed/Park recommendation |
| Footer | — | Computed impact-at-scale |

## Opportunity-Engine mapping

**Naming:** the "Opportunity-Engine MCP" is the **Product Definition Graph read server** — the
discovery engine's read server (ADR-025) that `aipos-quarterly-planning` already reads with the same
seven tools. This skill uses the same tool vocabulary so one server feeds both. One deliberate
difference: quarterly-planning stops without a live server; this skill falls back to the PM
interview (D5), because a canvas can legitimately start from a hunch.

**Before the server is live — mock read server (increment 0).** A small stdio MCP server,
`evals/mock_pdg/server.py` (repo-level, never shipped with the plugin), exposes the same seven tools with the confirmed response shapes
(`ScoredOpportunityResponse`, `EvidenceRefResponse`, `LineageResponse`, `schema_version: 1`) and
serves fixture JSON. The skill can't tell mock from real except by server prefix, so going live is
a config swap, not a code change. Rules: every fixture row is visibly synthetic (`fixture:` IDs,
`[SYNTHETIC]` in text); fixtures deliberately include the edge cases (null `occurred_at`, null
`record_url`, 2022–2024 aging split, five rows → one originating source, an unreachable source for
`get_evidence_text`, one `schema_version: 2` row); the ticket-triage example becomes one problem
in the fixture set. The mock is dev/eval infrastructure only and never ships as a data source.

Tool surface (verbatim descriptions supplied 2026-09-22):

| Tool | Args | Canvas use |
|---|---|---|
| `list_opportunities` | limit, offset | **Entry picker** when the PM names nothing: show top ranked with score components; the components are read as a risk map (per `evidence-intake.md`) and tell the facilitator which panel is weakest |
| `list_problems` | limit, offset | Entry picker when the PM thinks in problems, not opportunities |
| `get_problem` | problem_id | Panel 1 problem statement draft + **locked personas** (also footer *Who Benefits*); panel 2 evidence reference list |
| `get_lineage` | problem_id | Separates `source_evidence_refs` from `originating_sources` — used to **dedupe**: panel 2 counts distinct originating sources, not refs, and the entry picker flags ranked rows that trace to the same source. No dates here |
| `list_evidence` | problem_id | **Primary evidence read.** Qualified `provenance_reference` (the `gong:…` form `get_evidence_text` requires) + `occurred_at` → panel 2 tile dates and staleness. Drives which excerpts to request. Never quoted |
| `get_evidence_text` | provenance_reference, problem_id? | Panel 1 *current-state snapshot* examples and panel 2 *Voice of Customer* tile — redacted, PM-approved, ref kept beside it (D10) |
| `get_work_item_links` | problem_id | Pre-flight promotion check (D11); write-back destination candidates |

**Contract facts (confirmed 2026-09-22 against a dry run, 21 opportunity rows = 21 problem rows):**
- An opportunity *is* a scored problem: `ScoredOpportunityResponse.problem_id` is singular and required;
  there is no `opportunity_id` and no `problem_ids`. **One canvas ↔ one `problem_id`**; no bundling rule needed.
- Every row carries `schema_version` (currently `1`). The adapter checks it and stops with a clear
  message on any other value — bundling or shape changes arrive as a detectable bump, not silently.
- `occurred_at` is `str | None`. **Null means date unknown, not old**: the tile shows "date unknown"
  and the staleness rule skips it. `record_url` is also nullable — link only when present.
- Staleness: evidence older than 18 months (configurable) is marked *aging* on its tile and named in
  Open Questions; a panel whose evidence is all aging is called out to the PM once (the 2022–2024
  split in the dry-run pack is the fixture).

**Call order:** `get_work_item_links` → `get_problem` → `list_evidence` → `get_lineage` →
`get_evidence_text` (on demand, capped, per D10).

**What the Engine can't supply — always from the PM interview:** baselines and targets (panel 3),
the hypothesis wording, solution options (panel 4), assumptions/risks/mitigations (panel 5), the
validation plan, primary metric and decision owner (panel 6), and volume for impact-at-scale.
The Engine makes panels 1–2 a *confirm* conversation; panels 3–6 stay a *coach* conversation.

**Source contract (`opportunity_source` block in `canvas.json`):**

```yaml
opportunity_source:
  kind: opportunity-engine | tracker | pm-interview
  schema_version: 1                             # adapter refuses unknown versions
  problem_id: <as returned>                     # opportunity == scored problem, 1:1
  score: {composite, components: {...}}        # as returned, unmodified
  problem_statement: <engine text> [E|I]
  personas: [<role>, ...]                       # locked after PM confirms
  evidence_refs: [{provenance_reference, occurred_at: <str|null>, record_url: <str|null>, reachable: bool}]
  originating_sources: [...]                    # from get_lineage; used for dedupe counts
  excerpts: [{provenance_reference, text, approved_for_canvas: bool}]
  work_items: [{ref, system, status}]; promoted_verdict: <as returned>
  read_at: <timestamp>
```

## Design decisions

**D1 — New skill, not a rapid-validation artifact.** `aipos-solution-design` owns facilitation of
the canvas and its rendering. It points at the epic-create and rapid-validation rubrics rather than
duplicating them. Move any rubric used by more than one skill into `plugins/aipos/references/` if a
pointer across skill folders proves fragile.

**D2 — Two stages, like feature-refine.** Stage 1 is the coached interview producing `canvas.json`
(the governed artifact). Stage 2 renders it. The PM approves stage 1 before any render.

**D3 — Deterministic render, no image generation.** `scripts/render_canvas.py` fills an HTML
template from `canvas.json` and exports PNG + PDF via Playwright (same pattern as feature-map's
`render_map.py`). What's on the canvas is byte-for-byte what's in the JSON.

**D4 — The skill computes; it does not transcribe.** Percent change, impact at scale, and
target-vs-metric consistency are calculated in the script and checked in the interview. A mismatch
is surfaced to the PM once with the corrected figure; the PM decides.

**D5 — Opportunity-Engine first, PM interview as fallback.** At start, detect the Opportunity-Engine
by its **tool signature** (`get_problem` + `list_evidence` + `get_lineage` present under one
server prefix), not by server name. `get_evidence_text` is optional: the engine does not advertise
it at all when evidence text is unconfigured, so requiring it would misread a live graph as absent — the prefix differs per install. If present, read the record and
summarise back ("here's what I found — correct me"); never re-ask what the record answers. If absent,
run the evidence-intake Path C interview. Either way, every claim carries [E]/[I]/[A]. The adapter
fills a small **opportunity source contract** so the rest of the skill doesn't care where data came
from. Full mapping below.

**D10 — The Engine is read-only and quote-guarded; the skill honours both.** `list_evidence` returns
provenance references only, by design. The only text the skill may put on a canvas comes from
`get_evidence_text` (a redacted excerpt for one reference), carried with its `provenance_reference`.
Excerpts are read on demand, capped (default 5 per session), and a customer quote is placed on the
canvas only after the PM approves that specific quote — the canvas is a shareable artifact.
Unreachable sources are said to be unreachable, never paraphrased from the problem summary.

**D11 — Check promotion before facilitating.** `get_work_item_links` returns the problem's work items
and derived promoted verdict. If the problem is already promoted or has an active canvas/epic link,
say so first and offer update-vs-new. The same links are the write-back destination candidates (O2).

**D6 — Blueprint panels that the canvas lacks are folded in, not dropped.**
- *Data/source + context needs* → a required line in panel 5 assumptions ("the data exists and is
  representative") with its source named.
- *Success + evaluation criteria* → panel 6. In GenAI mode (same detection list as epic-create),
  panel 6 gains the evaluation criteria and says out loud that epics/features under this Initiative
  inherit them.

**D7 — Decision vocabulary.** Canvas shows Pivot / Proceed / Park, mapped explicitly to AIPOS
revise / go / no-go (defer) in `canvas.json` so rapid-validation's viability brief can consume it.
The canvas shows the *recommendation* and the named decision owner; it never implies the decision
was made.

**D8 — Brand.** Accelerated Innovation brand system: Poppins; Dark Purple `#19004f`, Purple
`#5865e7`, Magenta `#821db0`, Light Blue `#0abeef`; secondary palette for sticky-note tints; header
gradient 35° `#0abeef → #5865e7 → #19004f`. Tokens live in one `brand.json` so a client theme is a
file swap later.

**D9 — Coachiness inherited from epic-create.** One primary question at a time; summarise after each
panel and default forward; proceed protocol; push once per adjective/missing baseline, at most twice
per framing; never invent numbers, quotes, or evidence; required Open Questions & Gaps list (an
empty list is itself flagged); no write to repo or tracker without destination-named approval.

**D12 — Where the canvas lives.** Not the plugin repo. Output goes to the **Cowork project folder
the skill is running from**: `solution-design/<problem_id>/canvas.json`, `canvas.png`, `canvas.pdf`
(re-runs suffixed `-v2`, `-v3`, per rapid-validation's naming convention). If
`get_work_item_links` returns a linked **Jira or Aha!** ticket, the canvas is also attached there —
following `aipos-rapid-validation/references/record-writeback.md`: neither connector has an upload
tool, so the skill posts the index comment itself (after destination-named approval) and hands the
attachment to the PM by exact filename ("Attach `canvas.pdf` to OPP-7 — I can't upload files
myself"). If a connector gains an upload tool, the skill uses it under the same approval. No linked
ticket → folder only, no prompt about trackers. The index comment carries: problem statement,
hypothesis, primary metric baseline → target, recommended decision + owner, the evidence-base line
(including aging and deduped-source counts), and open gaps. A to-do is offered only when panel 6 has
a pilot — its actions with owner and date — per record-writeback's "named next action" test.

**D14 — The PDG is the source of truth for facts; the PM owns decisions.** Supersedes the "ask the
PM for missing data" parts of D5, D9 and D13.
- **Facts** — evidence, baselines, volumes, dates, quotes, current-state examples — come **only**
  from PDG reads. The skill never asks the PM to recall a fact and never records a recollection as
  one. A fact the graph lacks becomes a **`GAP · evidence`** chip on the canvas.
- **Decisions** — hypothesis wording, solution options, risks and mitigations, validation plan,
  decision owner — are authored by the PM and stay fully coached. They are never in the graph, so
  they are never turned into gather-tasks. Unresolved in workshop mode → **`GAP · decision`**.
- **Every evidence GAP is wired through the canvas, not left as a hole:** it becomes a Key
  Assumption in panel 5 (stated as an assumption, `[A]`) and an item in the panel 6 validation plan
  that would settle it. Example: routing baseline missing → panel 3 `routing accuracy: GAP` → panel 5
  "current misroute rate is material" → panel 6 "measure misroutes over 4 weeks of tickets".
- **Coaching shifts from "give me a number" to "what evidence would settle this, and where would it
  come from?"** — so each gather to-do names the source type, the measure, the window, and the
  intake route.
- **Intake route: ReOps** (for now). Each evidence to-do reads as an action: *"Log 4 weeks of misroute
  counts via ReOps intake → PDG."* Route is a config value so it can change without rewriting the skill.
- **To-dos live** on the linked Jira/Aha! ticket when one exists (D12 approval rules), otherwise in
  `todo.md` beside `canvas.json`. One to-do per evidence GAP, ordered by which GAP blocks the
  decision most (primary-metric baseline first).
- **Refresh on resume.** Re-opening a canvas re-reads the PDG first; any evidence GAP the graph can
  now fill is filled (`[E]`, with its `provenance_reference`), its to-do is marked done, and the PM
  is told what changed. This loop is what keeps the PDG authoritative.
- **Computed fields with a GAP input show the formula, not a number** (e.g. "0.6 min × GAP
  tickets/month"). Never a placeholder value.
- **Proceed guard:** the recommendation cannot be *Proceed* while the primary metric's baseline is
  a GAP. *Pivot* and *Park* remain available. The canvas says why Proceed is unavailable.
- **Vocabulary:** one marker, `GAP`, typed `evidence | decision`. When a canvas feeds
  `aipos-epic-create`, a metric GAP maps to that skill's `TBD` threshold convention.

**D13 — Two run modes, one artifact.** Ask once at the start, or infer it ("we're in the workshop
now"):
- **Workshop (live, facilitated):** panel-at-a-time; several questions per panel allowed; one push
  max; gaps accepted and shown as typed `GAP` chips (D14); a draft render is available
  after any panel so the room watches it build. Ends by turning the gap list into named follow-ups.
- **Coach (async, PM alone):** full epic-create discipline (D9) — one primary question at a time,
  push on decision quality (never ask the PM to supply a fact — D14) and up to twice on framing; no final render until panels 1–6
  pass their rubrics or the PM explicitly accepts the remaining gaps.

Same `canvas.json`, rubrics and computed checks (D4) in both; only pacing and gap tolerance differ.
`canvas.json` records `mode` and a per-field `status: confirmed | gap | provisional` (gaps carry `gap_type: evidence | decision` and, for evidence, the to-do id), so a workshop
canvas can be resumed later in coach mode to close its gaps.

## Increments

| # | Deliverable | Status |
|---|---|---|
| 0 | `evals/mock_pdg/server.py` + `fixtures/default.json` + `mcp.example.json` — seven tools, shapes copied from `discovery-engine/src/engine/api/schemas.py`, synthetic data, edge cases, optional access log; `tests/test_mock_pdg.py` pins every field set | [x] |
| 1 | `references/canvas-schema.md` + `scripts/verify_canvas.py` (no separate JSON Schema: it would add a non-stdlib dependency and a second source of truth — the script is the executable contract, and a test keeps the doc's code list identical to the script's) | [x] |
| 2 | `references/panel-rubrics.md` — per-panel quality bar and push scripts; pointers to reused rubrics; option-coaching rubric (panel 4) | [x] |
| 3 | `references/facilitation.md` — Step 0 mode (D13) + source detection (D5/D11) → panels 1–6 → footer → review → save (D12) → write-back offer; workshop and coach pacing side by side | [x] |
| 4 | `SKILL.md` from `templates/skill-template` — purpose, lifecycle position, scope/handoffs, proceed protocol, guardrails, output format | [x] |
| 5 | `references/opportunity-source.md` — OE adapter (signature detection, call order, excerpt cap, quote approval) + Path C fallback against the source contract | [x] |
| 6 | `scripts/render_canvas.py`, `templates/canvas.html`, `brand.json`; `scripts/verify_canvas.py` for D4 arithmetic | [x] |
| 7 | `evals/evals.json` + fixtures: solution-shaped problem; findings 1–3 (math/baseline); undated evidence; OE present vs absent; GenAI mode inherits criteria; PM declines write; **PM volunteers a remembered baseline → recorded as `[A]` assumption + GAP, not `[E]`; missing baseline → GAP + panel 5 assumption + panel 6 plan item + ReOps to-do; resume re-reads PDG and closes a now-filled GAP; Proceed blocked while primary baseline is a GAP;** workshop canvas with gaps renders `GAP` chips and resumes in coach mode; linked Jira item → named-attachment handoff, no claimed upload; **null `occurred_at` not treated as stale; 2022–2024 aging split; five ranked rows → one originating source; unknown `schema_version` stops cleanly** | [x] eight cases; not yet executed |
| 8 | Routing cases vs `aipos-epic-create` ("epic/initiative brief") and `aipos-rapid-validation` ("viability brief / prototype") | [x] six cases added; live routing passed 2026-09-25 (development 192/192, held-out 36/36; [record](../evaluations/2026-09-25-map-render-journey-evals.md)) |
| 8b | `references/record-writeback.md` pointer + folder writer (D12) | [x] |
| 9 | Update `Related` tables in epic-create and rapid-validation; README; plugin version bump | [x] v1.1.0 |

## Lifecycle position

```
Exploration Decision (P1) → aipos-solution-design (canvas, one per Initiative)
   → aipos-rapid-validation (runs the panel-6 plan → viability brief)
   → aipos-epic-create (optional, per epic) → aipos-feature-create
```

The canvas feeds rapid-validation's evidence intake as a Path B source; panel 1 feeds epic-create's
problem statement; panel 3 outcomes seed epic success metrics.

## What building 0–2 changed

- **The graph holds references, not numbers.** `ProblemDetailResponse` has a title, personas and
  evidence references — no statement, no measures. A baseline can only be `[E]` if an excerpt or a
  graph record carries it. ReOps records have no evidence-text adapter, so their content is never
  readable through MCP. Expect most canvases to start with their primary baseline as a GAP; the
  ReOps to-do is what gets it into the graph. Tile findings say what the graph *establishes*
  (linkage, dates, source type, excerpt words), not what unreadable records said.
- **Tile counts are refs, breadth is problem-level.** `get_lineage` gives two flat lists with no
  per-ref mapping, so a tile cannot count originating sources. Breadth is reported once, from
  `originating_sources`, with a single-source warning.
- **Independent review (2026-09-22)** found the D14 guarantees held only for well-behaved input.
  Fixed: content is checked by position, not shape; a fact can only be an evidence GAP; `[A]` is
  never a present fact; on engine canvases `[I]` needs graph refs; Proceed needs a graph-backed
  primary baseline (the hand-drawn example's pre-selected PROCEED is now caught); unit-conversion
  and %-kind checks; zero/negative baselines; malformed input reported, never a crash; empty quotes;
  speaker roles the graph never gave; snapshot approval; excerpt membership and cap; provisional
  content cannot be approved; recommendation needs an owner. Rejected: that the mock mis-anchors
  excerpts — it mirrors the engine's `_anchor_terms` fallback.
- **Naming (D12) reconciled with the schema:** folder slug = `problem_id` with `:`/`/` → `-`
  (`pm-<title>` without one); re-runs dated `canvas-<YYYY-MM-DD>.json`, matching rapid-validation.
- **Source contract** field names follow the engine (`composite_score`, `components`); quote and
  snapshot approval live on the canvas items, not on excerpts.

## What building 3–6 changed

- **Rendering:** PDF from headless Chrome is the exact render; the PNG is rasterised from it
  (`pdftoppm`, or macOS `qlmanage`/`sips`). Chrome's own `--screenshot` crops fixed-height pages in
  new-headless mode — the first render lost the footer that way. The renderer re-runs the verifier
  and never trusts a stored `computed`. Looking at renders caught a formatter bug that drew a
  computed 100 hours as "1"; now pinned by a test.
- **Second review (model's-eye) fixes:** `through_panel` so the verifier checks only panels reached
  (it had failed every in-progress canvas on later panels); approval needs `through_panel: 8` and is
  asked for by name; a new `[T]` mark for values a person reads from a graph-linked record — it
  computes but is **not graph-backed**, so it never unlocks Proceed; pain points come from the
  engine's problem title (`[I]`) or snapshot excerpts (`[E]`) only; Step 0 chooses the problem before
  looking for a saved canvas and freezes the slug; per-step "Writes:" lines; `todo.md` always
  written; stricter write rule wins (one yes per record per write); excerpts stripped before any
  tracker fallback; per-item `schema_version` on list responses; unapproved quotes/records withheld
  from drafts; minutes→hours conversion derived; retirement counts either side.
- **Routing:** this skill's description hands the canvas's pilot/experiment to rapid-validation, and
  rapid-validation's description now names canvas pilots and hands the canvas itself back.

## Open questions

- **O1 — resolved.** 1:1 by contract; dates from `list_evidence.occurred_at`; see *Contract facts*.
- **O2 — resolved (2026-09-22).** See D12.
- **O3 — resolved (2026-09-22).** Both; see D13.

- **O5 — `[T]` and Proceed.** ReOps records have no evidence-text adapter, so a baseline held only
  in a ReOps study can be transcribed (`[T]`) but can never unlock Proceed until the engine exposes
  it. Conservative by design; flip `graph_backed()` to accept `[T]` if that proves too strict.
- **O4 — resolved (2026-09-22).** Moved `problem-framing.md` and `metrics-and-evaluation.md` to
  `plugins/aipos/references/`, per CONTRIBUTING; epic-create's paths updated.
