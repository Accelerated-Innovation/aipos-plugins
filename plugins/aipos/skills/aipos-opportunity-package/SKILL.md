---
name: aipos-opportunity-package
description: "Package a graph problem into the four-part Structured Opportunity (evidence, hypothesis, impact estimate, recommended action) a gate 1 reviewer can accept or reject without reading the raw signals. Use when asked to turn a problem, PRB or candidate into a structured opportunity, opportunity package, one-pager for gate 1, or an opportunity brief from a live Product Definition Graph or a supplied graph record. Read-only; this release packages only — proposing or attaching an Intent is a deferred engine write integration, not implemented here. Solution framing and capacity allocation belong to their own skills."
---

# PDG Opportunity Package

This skill produces the artifact of step 4: the one-page **Structured Opportunity**
that gate 1 reviews. Step 4 is done when *"a reviewer can accept or reject it without
reading the raw signal"* — so the package is not a summary of everything known; it is
the smallest complete case for acting on one problem, built only from what the graph
says.

> "AI acts. Evidence informs. Humans govern." — AIPOS Canon

The package has exactly four parts. A package missing one is not a draft — it is not
a package:

1. **Evidence** — the problem's supporting facts, each cited to a graph reference,
   nothing quoted unmasked.
2. **Hypothesis** — the falsifiable statement of what solving this problem would
   change, for whom.
3. **Impact estimate** — with its inputs, its basis and its range stated; an assumed
   input is marked `[A]`, and a range the evidence cannot bound is **TBD**.
4. **Recommended action** — what the reviewer is being asked to approve, and what
   would have to be true for it to be a mistake.

## What this skill reads, and how

The skill is **read-only over MCP**. It requires a connected MCP server exposing read
tools over a Product Definition Graph. The reference implementation is the Accelerated
Innovation discovery engine's read server, whose seven tools are the vocabulary used
below; any server exposing equivalent reads works — map the names and nothing else
changes.

A session may instead supply graph-style records directly (files, pasted records,
fixtures). That is **supplied mode**. Supplied records are what the session was given,
not what the graph holds: work from them, but never call them live, current or
verified, and never claim a graph read — whatever the user says about where they came
from. Open the package with its **source mode** — `connected` (reads made in this
session against a named server) or `supplied` (records given in the session, and
`synthetic` when they say so) — so a reviewer knows what the evidence is before reading
it. If neither a live server nor supplied records exist, stop and say what is missing.

| Tool | What it feeds |
|---|---|
| `get_problem` | The candidate: title, composite score, personas, evidence references |
| `list_evidence` | The evidence behind the candidate: provenance references, dates, and a study finding's measurement |
| `get_lineage` | Where the candidate came from — the "says who?" answer |
| `list_problems` | The inventory, to name neighbours (its order is not a ranking) |
| `list_opportunities` | The ranked list the candidate sits in, with score components |
| `get_work_item_links` | Delivery work already touching the candidate |
| `get_evidence_text` | A redacted excerpt, fetched only when the package turns on exact words |

**Hard rules.** If no MCP server is connected and no records are supplied, stop and
say what is missing — never package from memory or training data. Every claim in the
package either traces to a tool call made in this session or to a supplied, labelled
record and is marked `[E]`, or carries an `[I]` or `[A]` mark that says it does not. An
unmarked figure is a defect; a plausible-looking figure with no tool call or supplied
record behind it is a worse one. `get_evidence_text` is a person-adjacent disclosure on
the reference server (each call is access-logged); fetch text only when the
recommended action turns on exact words, and never paste fetched text into the
package beyond the quoted fragment the action needs.

## Provenance marks

Every claim in the package carries the AIPOS provenance convention:

- `[E]` — evidence-backed: traceable to a tool call in this session, or in supplied
  mode to a named field of a supplied record (the source mode says which)
- `[I]` — inferred: a reasonable reading of `[E]` material, stated as inference
- `[A]` — assumption: not in the graph; named so the reviewer can challenge it

## The four parts, in detail

### Evidence

Every evidence line cites a graph reference (provenance reference, lineage, or
problem record field). Evidence the graph cannot show is a gap in the package, not a
gap in the graph — write it as what is missing, never as zero. Nothing is quoted
unmasked: masked references only, per the disclosure rules above.

Attribute each finding only to the record that states it. A figure from one study
finding is that finding's, not "the sources'". A reference that appears only in lineage
or `originating_sources`, with no evidence record behind it in this session, supports
nothing: name it as listed but unread, never as corroboration.

### Hypothesis

One falsifiable statement. If the reviewer cannot say what evidence would disprove it,
the hypothesis is not written yet. The hypothesis is `[I]` by nature — the graph
informs it, but no graph contains it.

### Impact estimate

State the inputs and the basis — the formula, written out — always. An estimate
without its inputs is a number impersonating evidence. Inputs cited to evidence are
`[E]`; inputs with no evidence reference, including figures the user volunteers, are
attributed to whoever supplied them and marked `[A]`; unknown inputs are named as
unknown — never silently defaulted to zero, one, or all.

- **Use the right denominator.** A rate applies to the population it was measured on.
  If 41% of reviews need a chase, cost the chased reviews, not every review. Say when a
  statistic is a stand-in for the one the formula needs (a median used as a mean is an
  `[A]`).
- **Baseline is not savings.** What the problem costs today (the modeled baseline) and
  what solving it would return (the achievable impact) are different numbers. Savings
  need an explicit reduction assumption, marked `[A]` with who should validate it;
  without one, report the baseline and state the impact as **TBD**.
- **A range only where the evidence bounds it.** Give bounds the inputs support, or
  clearly labelled scenarios that each state their assumption. When nothing bounds the
  estimate, the range is **TBD** with the missing inputs named — never invent bounds to
  avoid an unquantified answer.

### Recommended action

The concrete ask: what the reviewer is approving, what it costs (owner, budget,
horizon where the graph or session supplies them), and what would make it wrong.
Recommended actions the session invented are `[A]` and say so.

## Proposing and attaching are not part of this release

This release reads and packages. It never calls `propose_problem`, `attach_intent`,
`find_similar_problems` or any other tool that proposes, attaches, records or changes
graph state, **even where the connected server advertises them** and even after the user
says yes. Those tools belong to the engine's governed-write work (ADR-AIG-030), whose
contracts this release has not been verified against.

Asked to propose or attach: produce the package, say that proposing and attaching are
not part of this release so nothing was recorded, and hand the package to the human who
owns gate 1. Never show a simulated write, a dry-run preview or a confirmation prompt
for a write this skill cannot make. If the user reports that a duplicate or similarity
check failed or was unavailable, say the check did not run and that an outage is not an
empty result — the package must not imply there are no duplicates.

## Where this sits

- `aipos-product-strategy` owns new-product framing; this skill packages one
  evidenced problem from the graph.
- `aipos-solution-framing` takes an accepted problem and frames solution options —
  after gate 1, not this artifact.
- `aipos-exploration-planning` decides which opportunities get capacity; this skill
  hands it the package it allocates against.

Gate 1 remains a human decision. The package informs it; the reviewer governs it.
