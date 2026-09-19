# aipos-p1

Continuous Discovery (AIPOS Pillar 1): decide what deserves exploration capacity
*before* anyone commits it. One skill, one ceremony, one primary output — the
**Exploration Decisions**: explore with a declared budget and horizon, decline with a
reason, or defer to a named session.

## What it does

The `aipos-quarterly-planning` skill runs a quarterly planning session against a live
**Product Definition Graph**, read over MCP. It answers Pillar 1's core question —
*what problems do customers actually have, ranked by evidence, and which of them
deserve exploration next quarter?* — in five moves:

| Move | Output |
|---|---|
| Portfolio read | Ranked, Proposed, and already-in-delivery populations, with movement since last session |
| Evidence grading | Strong / Thin / Stale / Say-so — the grade beside the rank, because a high rank with thin evidence is a research candidate before it is a build candidate |
| Gap analysis | Coverage gaps (nothing recent for a product, persona, or region), attention gaps (ranked, evidenced, ignored), expiry pressure, funnel signals |
| Session agenda | One page, ordered by decision urgency, closed by the capacity ledger |
| Exploration Decision log | The primary output — each decision with owner, budget, horizon, evidence cited, and the governed door it gets recorded through |

Every claim is provenance-marked (`[E]` evidence-backed, `[I]` inferred, `[A]`
assumption) and traceable to an MCP tool call made in that session. The skill never
invents evidence, counts, ranks, or quotes; a missing number becomes a marked
assumption.

What it does **not** do: it never writes. Not to the graph, not to a tracker, not to
any record. Decisions enter the system of record through its own governed doors —
on the reference stack, the research-intake lifecycle and the propose-opportunity
approval, which enforce budget, horizon, and WIP limits server-side. The skill
drafts the pack; humans govern.

## What it needs

An MCP server exposing read tools over a Product Definition Graph. The reference
implementation is the Accelerated Innovation discovery engine's read server
(seven tools: `list_opportunities`, `list_problems`, `get_problem`, `get_lineage`,
`list_evidence`, `get_work_item_links`, `get_evidence_text` — redacted and
access-logged). Any server exposing equivalent reads works. Without a connection
the skill stops and says what is missing rather than planning from memory.

## The handoff

**Pillar 1 ends at the Exploration Decision. Pillar 2 begins there.** An explored
problem enters Rapid Validation carrying its decision entry, which the companion
plugin's `aipos-rapid-validation` skill reads as the *exploration mandate* — owner,
budget, horizon. Every Pillar 2 artifact carries that mandate in its header as a
running ledger and states its own cost against it; the viability brief reconciles the
work done and, on an explicit yes, records the Validation Decision back against the
Exploration Decision so the next planning session sees what it funded. Pillar 2
reports against the mandate and never gates on it — the owner holds the line, and the
governed door enforces budget, horizon, and WIP limits server-side.

## Install

```
/plugin install aipos-p1@aipos
```

## Skills

- **[aipos-quarterly-planning](./skills/aipos-quarterly-planning/SKILL.md)** — the
  quarterly session pack: portfolio read, evidence grading, gap analysis, agenda,
  and the Exploration Decision log, plus a dry-run rehearsal mode whose pass
  condition is that every claim traces and the calibration note is specific enough
  to change the next run.
