---
name: pdg-quarterly-planning
description: "Run an evidence-governed quarterly planning session over a Product Definition Graph — read the ranked opportunity list, grade the evidence behind each candidate, find the coverage gaps (products, personas, and regions with no recent research; high-ranked problems nobody is exploring; proposals about to expire), build the session agenda, and record the Exploration Decisions with budget and horizon. Use this when a team plans a quarter against graph evidence: phrases like 'quarterly planning', 'what should we explore next quarter', 'planning session prep', 'gap analysis over the graph', 'which problems deserve research', or 'build the planning agenda' all belong here. Reads the graph over MCP tools; never writes to it. Also runs a dry-run rehearsal against live data."
---

# PDG Quarterly Planning

This skill runs the ceremony where AIPOS Pillar 1 (Continuous Discovery) hands its
evidence to human judgment: the quarterly planning session, held against a live
Product Definition Graph rather than a slide deck of recollections.

Pillar 1's core question: **what problems do customers actually have, ranked by
evidence — and which of them deserve exploration capacity next quarter?** The graph
answers the first half continuously. This skill exists for the second half, which no
graph can answer, because allocating budget is governance:

> "AI acts. Evidence informs. Humans govern." — AIPOS Canon

## The one thing to keep straight

The output is not a ranking — the graph already has one. The output is a set of
**Exploration Decisions**: for each candidate problem, an accountable owner decides
*explore* (with a declared budget and horizon), *decline* (with a reason), or *defer*
(to a named future session). A session that admires the ranked list and decides
nothing has not done quarterly planning. Whenever you finish an artifact, point at
the decisions it serves and say which candidates still lack one.

**This pillar ends at the Exploration Decision. Pillar 2 (Rapid Validation) begins
there.** Hand each *explore* entry of the decision log to `val-rapid-validation`, which
reads it as the **exploration mandate** — owner, budget, horizon, and the record ref once
one exists. That skill carries the mandate in every artifact's header as a running ledger,
states each artifact's cost in the mandate's own units, defaults to the viability brief
when the budget is spent or the horizon has passed, and reconciles the work done in the
brief. It reports against the mandate and never gates on it: the owner holds the line,
and the governed door enforces budget, horizon, and WIP server-side. The brief's last
step offers to record the Validation Decision back against this Exploration Decision, so
the next session's funnel signals see what was funded and what came of it.

## What this skill reads, and how

The skill is **read-only over MCP**. It requires a connected MCP server exposing
read tools over a Product Definition Graph. The reference implementation is the
Accelerated Innovation discovery engine's read server (ADR-025), whose seven tools
are the vocabulary used below; any server exposing equivalent reads works — map the
names and nothing else changes.

| Tool | What it feeds |
|---|---|
| `list_opportunities` | The ranked candidate list — the session's spine |
| `list_problems` | The full problem inventory, including unranked Proposed items |
| `get_problem` | A candidate's detail: statement, descriptors, state |
| `get_lineage` | Why a candidate ranks where it does — the "says who?" answer |
| `list_evidence` | The evidence behind a candidate, with fitness descriptors |
| `get_work_item_links` | What delivery work already touches a candidate |
| `get_evidence_text` | A redacted excerpt, fetched only when a claim needs its exact words |

Where a research-operations system is also connected (the reference: ReOps — intake
triage counts, study coverage, proposal expiry), its reads join the gap analysis.
Absent one, the gap analysis runs on the graph alone and says so.

**Hard rules.** If no MCP server is connected, stop and say what is missing — never
run planning from memory or training data. Every number, rank, and claim in every
artifact either traces to a tool call made in this session and is marked `[E]`, or
carries an `[I]` or `[A]` mark that says it does not. An unmarked figure is a defect; a
plausible-looking figure with no tool call behind it is a worse one. `get_evidence_text`
is a person-adjacent disclosure on the reference server (each call is access-logged);
fetch text only when a decision turns on exact words, and never paste fetched text
into artifacts beyond the quoted fragment the decision needs.

## Provenance marks

Every claim in every artifact carries the AIPOS provenance convention:

- `[E]` — evidence-backed: traceable to a tool call in this session
- `[I]` — inferred: a reasonable reading of `[E]` material, stated as inference
- `[A]` — assumption: not in the graph; named so the session can challenge it

A missing number becomes a marked assumption, never a plausible-looking figure.

## The five moves

Run them in order; each produces a section of the session pack.

### 1. Portfolio read

`list_opportunities` for the ranked list; `list_problems` for the full inventory.
Separate three populations: **ranked problems** (scored, evidence-bearing),
**Proposed problems** (human-originated, unranked by design — deliberately excluded
from scoring until promoted), and **already-linked work** (`get_work_item_links` —
a candidate already in delivery is a status update, not a planning decision).
Record counts and movement since the last session where a prior pack exists.

### 2. Evidence grading

For each candidate that could plausibly receive capacity, `get_lineage` and
`list_evidence`. Grade the evidence, not the idea:

| Grade | Meaning |
|---|---|
| **Strong** | Multiple independent sources, recent, fitness descriptors present |
| **Thin** | Few sources or one source type — rank may be real, confidence is not |
| **Stale** | Nothing new in the graph for a stated window — the world may have moved |
| **Say-so** | Rank rests on volume without corroborating fitness — flag loudest |

The grade goes on the agenda beside the rank. A high rank with thin evidence is a
*research* candidate before it is a *build* candidate — often the session's most
valuable single finding.

### 3. Gap analysis

The graph shows what evidence exists; the gaps are what it cannot volunteer.
Compute, and mark `[E]`/`[I]` honestly:

- **Coverage gaps** — products, personas, or regions carrying no research evidence
  newer than N months (default 6; the session sets N). Where a research-ops system
  is connected, join study coverage; otherwise derive from evidence descriptors.
- **Attention gaps** — high-ranked problems with no exploration, no linked work,
  and no Proposed thread: ranked, evidenced, and ignored.
- **Expiry pressure** — Proposed items nearing their expiry window: decide or lose
  them (on the reference stack, archived proposals stay re-proposable — say so).
- **Funnel signals** — where intake counts are available: rising expiries with
  flat approvals means the funnel is silting up.

### 4. The session agenda

One page. For each candidate: rank, evidence grade, one-sentence problem statement
`[E]`, the gap or pressure that put it on the agenda, and the decision it needs
(explore / decline / defer). Order by decision urgency, not rank. Close the agenda
with the capacity ledger: how many explorations the teams can hold at once (where a
WIP setting is readable, cite it `[E]`; otherwise `[A]`), how many slots are
occupied, how many this session can allocate.

### 5. The Exploration Decision log

The primary output. For each agenda item the session decides:

```
Problem:        <id> — <statement> [E]
Decision:       explore | decline | defer
Owner:          <accountable owner>
Budget:         <e.g. five interviews>       (explore only)
Horizon:        <e.g. two weeks>             (explore only)
Evidence cited: <lineage/evidence refs from this session>
Status:         draft — not yet recorded
Record via:     <the governed door a human must walk through>
Record ref:     <empty until recorded; then the id the door produced>
Rationale:      <one sentence>
```

**This skill never writes a decision anywhere.** Decisions enter the system of
record through its own governed doors — on the reference stack, an exploration
approval goes through the research-intake lifecycle and the propose-opportunity
approve operation, which enforce budget, horizon, and the WIP limit server-side.
The log's `Record via` line names the door; a human walks through it, and only then
does the entry stop being a draft. When they do, the id the door produced goes on the
`Record ref` line — that is what Pillar 2 cites and what the Validation Decision is
recorded against. The `Status` line travels with the entry wherever it is quoted, so a
log read outside this session never looks like a decision already in the system of
record.

## Dry-run mode

The skill's acceptance test is a rehearsal against live data. Run all five moves
end to end — the decision log included — and mark every artifact **DRY RUN** at the
top. In the log, every agenda item still gets its row: `Decision: rehearsal — not
decided`, the owner who would decide, the evidence cited, and the governed door the
decision would walk through. The move the session exists for is the one a rehearsal
must exercise. Then finish with a calibration note: which tool answered slowly or
strangely, which grade thresholds felt wrong against real evidence, which gap
windows (N months) produced noise versus signal, and what the pack was missing that
the room would ask for. The dry run passes when every claim in the pack carries a
provenance mark and every `[E]` traces to a tool call, every agenda item has a log
row naming its door, and the calibration note is specific enough to change the next
run.

## Guardrails

Do not:

- Write to the graph, a tracker, or any record — this skill reads and drafts only
- Run any part of planning without a live MCP connection, or fill gaps from memory
- Invent evidence, counts, ranks, quotes, or fitness descriptors
- Interpret raw ranking scores beyond the server's published ordering — the graph's
  ranking mechanism is the graph's business
- Fetch evidence text speculatively, or retain fetched text beyond the fragment a
  decision needs
- Turn a decline into a deletion — a declined candidate stays in the graph; the
  decision log records why it was declined
- Let the session end without decisions — an agenda with no decision log is a
  failed run, and the skill says so rather than declaring success

Always:

- Mark `[E]`/`[I]`/`[A]` on everything, and trace every `[E]` to a tool call
- Grade evidence separately from rank
- Name the governed door every decision must walk through
- State what was NOT examined (populations skipped, windows not computed), so the
  pack's silence is never mistaken for the graph's
