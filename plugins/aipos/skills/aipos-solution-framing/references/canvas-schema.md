# Canvas schema — `canvas.json`

> The canvas is a shareable one-page artifact, so it gets quoted. `canvas.json` is the governed
> record; the rendered PNG/PDF is a view of it. Nothing on the render is typed by hand if it can
> be computed, and nothing is presented as evidence unless the Product Definition Graph (PDG)
> returned it.

`scripts/verify_canvas.py` is the executable form of this document. When the two disagree, the
script is right and this file is the bug. Run it after every change to the canvas:

```bash
python3 scripts/verify_canvas.py solution-framing/<folder>/canvas.json --write
```

`--write` refreshes the `computed` block. Exit code 1 means errors; the JSON report names each
by code and path.

## Contents

- [The field object](#the-field-object) — facts, decisions, GAPs
- [Top level](#top-level)
- [`source` — the graph read](#source--the-graph-read)
- [Panels](#panels)
- [Footer](#footer)
- [To-dos](#to-dos)
- [`computed` — output only](#computed--output-only)
- [Files and naming](#files-and-naming)
- [Verifier codes](#verifier-codes)

## The field object

Every piece of canvas content that could be questioned is a **field**:

```json
{ "kind": "fact",     "status": "confirmed",   "value": "...", "mark": "E", "refs": ["zendesk:tkt-88121"] }
{ "kind": "fact",     "status": "provisional", "value": 1.8,   "mark": "I", "refs": [], "note": "whose, from what" }
{ "kind": "decision", "status": "confirmed",   "value": "Head of Support" }
{ "kind": "fact",     "status": "gap", "value": null, "gap_type": "evidence", "todo": "t1",
  "assumed": { "value": 1.8, "mark": "A", "said_by": "PM" } }
{ "kind": "decision", "status": "gap", "value": null, "gap_type": "decision" }
```

**Facts** describe the world: evidence, baselines, volumes, dates, examples. They come from the
graph. **Decisions** are authored by the PM and the room: wording, targets, options, owners,
the plan, the recommendation. The split is the whole contract:

| | Fact | Decision |
|---|---|---|
| Source | PDG reads only | The PM / the room |
| Provenance mark | `E` or `I` (see below) | None; a mark on a decision is an error |
| `[E]` | Cites `refs` the graph returned in this read | — |
| `[I]` | Inferred from graph `refs`. A `note` alone is allowed only on a `pm-interview` canvas | — |
| `[T]` | Transcribed: a person read the value from a record the graph links (`refs`) and the `note` says who, from which `record_url`, when. Computes, but is **not graph-backed** — Proceed waits for the graph to carry the value | — |
| `[A]` | Never on a present fact — an assumption is a GAP with the figure in `assumed` | — |
| Missing | `GAP · evidence` (always, for a fact), wired to a to-do | `GAP · decision` |

Rules:

- A GAP carries **no value**. A figure the PM volunteers goes in `assumed` with mark `A`. It is
  displayed beside the GAP and **never computed with**.
- `status: provisional` means present but not yet confirmed — a fact the room is still checking,
  or a decision Claude drafted for the PM. It renders with a lighter treatment and **cannot be
  approved**: confirm or change it first.
- Never write an `[E]` whose reference was not returned by a tool call recorded in `source`.
- **Content is checked by position, not by shape.** Every position listed below holds a field
  object of the stated kind; a bare string, a status-less dict, or a fact written as a decision
  (e.g. a baseline typed `decision`) is an error. Numeric positions (baseline, target,
  target_change_pct, volume) hold numbers, not numeric strings.
- **Graph-backed** means an `[E]` fact, or an `[I]` fact whose `refs` are all graph references.
  `[T]` is not graph-backed. Proceed rests only on a graph-backed primary baseline.
- **On a `pm-interview` canvas** the PM's account is the only source: facts are `[I]` with a `note`
  naming whose account, and they **are** computed with — the arithmetic is still checked — but
  nothing is graph-backed, so Proceed is unavailable and the render says the canvas rests on the
  PM's account. On a graph canvas, a figure the PM remembers is never computed with (`assumed`).

## Top level

| Key | Type | Notes |
|---|---|---|
| `canvas_version` | `1` | |
| `mode` | `workshop` \| `coach` | Pacing and gap tolerance; same artifact either way |
| `stage` | `draft` \| `approved` | `approved` = the PM approved the content (stage 1) |
| `gaps_accepted` | bool | Coach mode: the PM explicitly accepts remaining decision GAPs |
| `through_panel` | int 0–8 | How far facilitation has got (1–6 panels, 7 footer, 8 reviewed). Checks for later panels wait until they are reached; approval needs 8. Absent means 8 |
| `slug` | string | The folder name, frozen at first save (see *Files and naming*) |
| `genai` | bool | Same detection list as `aipos-epic-create` |
| `aging_months` | int, optional | Default 18 |
| `title`, `goal` | decision fields | Canvas header |
| `source`, `panels`, `footer`, `todos`, `open_questions` | see below | |
| `computed` | object | Written by the verifier; never input |

## `source` — the graph read

A record of exactly what the graph returned, so every `[E]` can be checked against it.

```json
{
  "kind": "opportunity-engine",           // or "pm-interview" (no graph; no [E] possible)
  "server": "opportunity-engine",         // the tool prefix read from; a mock server banners the render
  "schema_version": 1,                    // any other value: stop — do not guess the shape
  "problem_id": "…", "title": "…", "composite_score": 0.82,
  "components": { "evidence_strength": …, "revenue_impact": …, "persona_breadth": …,
                  "recency": …, "validation_signal": … },
  "personas": [{ "name": "Support Agent", "confidence": 0.91 }],
  "evidence_refs": [{ "provenance_reference": "zendesk:tkt-88121", "source_system": "zendesk",
                      "source_type": "support_ticket", "occurred_at": "…" | null,
                      "record_url": "…" | null }],
  "originating_sources": ["…"],           // from get_lineage — breadth, not the ref count
  "excerpts": [{ "provenance_reference": "…", "text": "…", "anchored": true,
                 "redaction_applied": true }],   // only what get_evidence_text returned
  "work_items": [{ "external_reference": "OPP-12", "target_system": "aha",
                   "link_type": "promoted", "status": "active", "record_url": "…" }],
  "promoted": false,                      // null when links were unavailable — unknown, not false
  "read_at": "2026-09-22T18:00:00Z"       // staleness is judged against this, not today
}
```

Copy values as returned. `occurred_at: null` means **date unknown**, never old.

## Panels

### `panels.problem` — Problem & Context

| Key | Content |
|---|---|
| `personas` | `{ primary, others[], locked }`. Primary should be a graph persona; locked before approval |
| `pain_points[]` | 1–3 fact fields — what the graph shows people struggling with |
| `snapshot[]` | 0–3 `{ ref, label, approved_for_canvas }` — real records the graph returned text for (current-state examples), each approved by the PM for a shareable canvas |
| `impact[]` | fact fields — consequences, with numbers only where the graph holds them |
| `statement` | decision fields `problem`, `affects`, `resulting_in`, `benefits` — the X/Y/Z/benefits sentence |

### `panels.evidence` — Discovery Evidence

| Key | Content |
|---|---|
| `tiles[]` | 1–4 `{ label, refs[], finding }`. `finding` is a fact field phrased as what the graph establishes. Counts (distinct refs), date ranges and aging are **computed**, never typed. Breadth is reported once for the whole problem from `originating_sources` — the graph does not map each ref to its originating source, so a tile cannot count sources |
| `voice` | `{ provenance_reference, quote, approved_for_canvas }` or null. `quote` is a verbatim, non-empty substring of that reference's excerpt; approved by the PM before it appears. Attribute it to its source type and date — the graph does not say who the speaker was, so a `speaker_role` is flagged |

### `panels.hypothesis` and `panels.metrics` — Hypothesis & Expected Outcomes

`hypothesis`: decision fields `if`, `then`, `without` — each carries its own subject ("we suggest
the right category at intake"); the render supplies only the words *If*, *then*, *without*.
`outcomes[]` lists ≤3 metric ids, one of them the primary.

Each metric:

| Key | Content |
|---|---|
| `id`, `name`, `unit` | |
| `direction` | `decrease` \| `increase` — the target and % sign must agree |
| `primary` | exactly one metric is primary; the decision and impact at scale key off it |
| `counter` | bool — a guard metric against harm |
| `baseline` | fact field (numeric) — from the graph, or an evidence GAP |
| `target` | decision field (numeric, absolute), optional |
| `target_change_pct` | decision field (numeric, signed), optional — at least one target form is required |
| `target_change_kind` | `relative` (default) \| `points`. **Required on a % metric**: +20 on 60% is 72% relative, 80% in points. A % target outside 0–100 is an error |
| `observation` | decision field — how it will be measured |

When both target forms are given they must agree (±0.5 points). When only the % is given and the
baseline is known, the absolute target is derived.

### `panels.options` — Solution Options

2–3 items, each `{ id: A|B|C, name, approach (decision field), preview[], pros[], cons[],
moves[metric ids] }`, plus `panels.recommended_option` (an id or null). Every option has at least
one pro and one con.

### `panels.assumptions` and `panels.risks` — Assumptions & Risks

- Assumption: `{ id, text, from_gap (field path | null), retired_by[plan ids] }`. Every evidence
  GAP has an assumption whose `from_gap` is its path.
- Risk: `{ id, text, mitigation | null }`. Null renders as **unmitigated**, plainly.

### `panels.validation` — Validation & Decision

- `plan[]`: `{ id, action, owner (decision field), by (date | null), retires[assumption ids],
  todo (id | null) }`.
- `recommendation`: `{ decision: proceed | pivot | park | null, owner (decision field),
  rationale }`. A **learning** recommendation, made before any experiment: *proceed* = run the
  panel-6 plan on the recommended option; *pivot* = rework the approach before testing it;
  *park* = defer and run nothing now. It is not a production-investment decision and does not map
  to the viability brief's go / revise / no-go, which `aipos-rapid-validation` reaches once the
  evidence is in. It is a recommendation to the named owner, never a record that the decision was
  made; a recommendation without a named owner is an error.
  **Proceed is unavailable unless the primary metric's baseline is graph-backed** — a GAP, a
  PM's figure, or a note-based inference all block it.
- `genai_criteria[]`: GenAI mode only. Criteria that work under this Initiative inherits.

## Footer

| Key | Content |
|---|---|
| `who_benefits[]` | persona / role names |
| `success` | decision field — "success looks like" |
| `scale` | `{ volume (fact field), volume_unit, result_unit, per_unit_factor }` — `per_unit_factor` may be omitted when both units are time units (min → hours is derived as 1/60); otherwise give it as a JSON number. Impact at scale = primary-metric saving × volume × factor, **computed**. The factor is checked against the primary metric's unit when both are time units; a percentage primary metric has no per-unit saving and cannot be scaled. With a GAP input it renders as the formula (`GAP × GAP ÷ 60`), never a placeholder number |
| `scale.stated_*` | Only when importing a hand-made canvas: stated figures the verifier checks against its own |

## To-dos

Each evidence GAP has one:

```json
{ "id": "t1", "field": "panels.metrics[0].baseline",
  "action": "Log the time-study result (study-ts-07) via ReOps intake → PDG",
  "measure": "average minutes per ticket spent on triage", "source_type": "study_outcome",
  "window": "4 weeks" | null, "intake_route": "reops",
  "destination": "ticket" | "todo.md", "status": "open" | "done",
  "reops_draft": { "project_name": "…", "background": ["…"], "needs": ["…"], "personas": ["…"] } }
```

`reops_draft` pre-fills a ReOps research-intake request (project name, background statements,
needs, target-audience personas). The skill drafts it; a person submits it. A to-do whose field
is no longer a GAP is stale and gets closed on refresh.

## `computed` — output only

Written by `verify_canvas.py --write`; the renderer reads numbers only from here.

| Key | Holds |
|---|---|
| `metrics.<id>` | `change_abs`, `change_pct`, `target` (derived if from %), `formula`, `blocked_by[]` |
| `impact_at_scale` | `saving_per_unit`, `result`, `formula`, `blocked_by[]` |
| `evidence` | per-tile `count`, `undated`, `earliest`, `latest`, `aging`; totals; `single_source`; `all_aging`; `as_of` |
| `proceed_available`, `proceed_blocked_by[]`, `aipos_decision`, `gaps` | the decision guard and the GAP tally |

## Files and naming

In the Cowork project folder the skill runs from:

```
solution-framing/<problem-slug>/
  canvas.json          canvas.png          canvas.pdf          todo.md (when no ticket)
```

`<problem-slug>` is the `problem_id` with `:` and `/` replaced by `-` (a colon is not a safe
folder name on every OS). A `pm-interview` canvas has no `problem_id`; its slug is `pm-` plus the
slugified working title at first save. The slug is recorded in `canvas.json` and **never changes**
afterwards, even if the title does. `todo.md` is always written, whether or not a ticket is linked.

**Paths inside the canvas** (`from_gap`, `todo.field`) use the verifier's syntax:
`panels.metrics[0].baseline`, `panels.problem.impact[1]`, `footer.scale.volume`. They are indexes:
after reordering a list, run the verifier — it names any path that no longer points at its GAP. A re-run that supersedes an approved canvas writes
`canvas-<YYYY-MM-DD>.json` beside it, per rapid-validation's naming convention. An approved
canvas is never overwritten.

## Verifier codes

The verifier never crashes: malformed input is reported as `MALFORMED` (or a more specific code).

**Errors** (exit 1):
- *Shape:* `MALFORMED` `CANVAS_VERSION` `MODE` `STAGE` `INCOMPLETE_AT_APPROVAL` `MISSING` `NOT_A_FIELD` `WRONG_KIND`
  `NOT_NUMERIC` `SOURCE_KIND` `SCHEMA_VERSION_UNSUPPORTED` `EXCERPT_NOT_IN_GRAPH`
- *Provenance:* `FIELD_STATUS` `PROVISIONAL_AT_APPROVAL` `GAP_HAS_VALUE` `GAP_TYPE` `ASSUMED_MARK`
  `EMPTY_FIELD` `DECISION_MARKED` `FACT_UNMARKED` `FACT_ASSUMED` `E_WITHOUT_REF` `T_WITHOUT_RECORD` `REF_NOT_IN_GRAPH`
  `I_WITHOUT_BASIS` `TODO_ORPHANED`
- *Arithmetic:* `PRIMARY_METRIC` `TOO_MANY_OUTCOMES` `UNKNOWN_METRIC` `PRIMARY_NOT_OUTCOME`
  `NO_TARGET` `DIRECTION` `TARGET_INCONSISTENT` `OUT_OF_RANGE` `SAVING_INCONSISTENT`
  `IMPACT_INCONSISTENT` `IMPACT_UNSUPPORTED` `IMPACT_UNIT` `FACTOR_INVALID` `FACTOR_MISMATCH`
- *Evidence:* `QUOTE_EMPTY` `QUOTE_WITHOUT_EXCERPT` `QUOTE_NOT_VERBATIM` `SNAPSHOT_WITHOUT_EXCERPT`
- *Decision:* `PERSONAS_UNLOCKED` `UNKNOWN_OPTION` `DECISION_VALUE` `OWNER_MISSING` `PROCEED_BLOCKED`

**Coach mode errors, workshop mode warnings:** `GAP_WITHOUT_TODO` `GAP_WITHOUT_ASSUMPTION`
`ASSUMPTION_NOT_RETIRED` `OPTION_COUNT` `OPTION_TRADEOFFS` `GENAI_CRITERIA` `PCT_KIND`; and
`DECISION_GAP` (coach only, lifted by `gaps_accepted`). `QUOTE_NOT_APPROVED` and
`SNAPSHOT_NOT_APPROVED` are errors once `stage` is `approved`.

**Warnings:** `INTAKE_ROUTE` `TODO_STALE` `TODO_ORDER` `ZERO_BASELINE` `EVIDENCE_AGING`
`ALL_EVIDENCE_AGING` `SINGLE_SOURCE` `DUPLICATE_REF` `EXCERPT_CAP` `SPEAKER_UNSOURCED`
`PERSONA_NOT_IN_GRAPH` `RISK_UNMITIGATED` `NUMBER_IN_PROSE` `NO_OPEN_QUESTIONS` `FACTOR_ASSUMED`
