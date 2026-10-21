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
3. **Impact estimate** — with its inputs and range stated; unknown inputs marked `[A]`.
4. **Recommended action** — what the reviewer is being asked to approve, and what
   would have to be true for it to be a mistake.

## What this skill reads, and how

The skill is **read-only over MCP**. It requires a connected MCP server exposing read
tools over a Product Definition Graph. The reference implementation is the Accelerated
Innovation discovery engine's read server, whose seven tools are the vocabulary used
below; any server exposing equivalent reads works — map the names and nothing else
changes.

A session may instead supply graph-style records directly (files, pasted records,
fixtures). That is **supplied-fixture mode**: work from the supplied facts, label the
material synthetic or supplied as it is labelled, and never claim a live graph read.
Supplied facts carry the same `[E]` weight as tool observations — with the fixture
labelled, not hidden. If neither a live server nor supplied records exist, stop and say
what is missing.

| Tool | What it feeds |
|---|---|
| `get_problem` | The candidate: statement, descriptors, state |
| `list_evidence` | The evidence behind the candidate, with fitness descriptors |
| `get_lineage` | Why the candidate ranks where it does — the "says who?" answer |
| `list_problems` | The inventory, to place the candidate and name neighbours |
| `list_opportunities` | The ranked list the candidate sits in |
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

- `[E]` — evidence-backed: traceable to a tool call in this session
- `[I]` — inferred: a reasonable reading of `[E]` material, stated as inference
- `[A]` — assumption: not in the graph; named so the reviewer can challenge it

## The four parts, in detail

### Evidence

Every evidence line cites a graph reference (provenance reference, lineage, or
problem record field). Evidence the graph cannot show is a gap in the package, not a
gap in the graph — write it as what is missing, never as zero. Nothing is quoted
unmasked: masked references only, per the disclosure rules above.

### Hypothesis

One falsifiable statement. If the reviewer cannot say what evidence would disprove it,
the hypothesis is not written yet. The hypothesis is `[I]` by nature — the graph
informs it, but no graph contains it.

### Impact estimate

State the inputs and the range, always. An estimate without its inputs is a number
impersonating evidence. Inputs the graph or a supplied record provides are `[E]`;
inputs the user supplies are attributed to the user and marked `[A]` unless the
record supports them; unknown inputs are named as unknown — never silently
defaulted to zero, one, or all. When inputs are too incomplete to bound the
estimate, say the range is **TBD** and name the missing inputs; do not invent
bounds to avoid an unquantified answer.

### Recommended action

The concrete ask: what the reviewer is approving, what it costs (owner, budget,
horizon where the graph or session supplies them), and what would make it wrong.
Recommended actions the session invented are `[A]` and say so.

## The write half (deferred — not implemented in this release)

The engine's MCP write tools (feature 17: `find_similar_problems`, `propose_problem`,
`attach_intent`) do not exist in this release's scope: **this release does not invoke
`propose_problem` or `attach_intent`, even where a deployment advertises them.**
Asked to propose or attach, the skill produces the package, states that the write
integration is deferred, and stops short of writing — it never simulates a write or
claims one.

The rules below are the requirements the write integration must meet before it
ships — they describe required behavior, not enabled functionality:

1. **Duplicate check before propose.** Run `find_similar_problems` and present strong
   matches before proposing. A similarity **outage is not an empty result** — if the
   check didn't run, the package ships without a proposal and says so. Never propose
   while the similarity check is unavailable.
2. **Dry-run preview and one explicit yes.** Writes happen only after the user has
   seen the dry-run preview (with `recorded:false`) and said yes once. One yes per
   write; a yes to the package is not a yes to the write.
3. **Identity is never an argument.** The skill passes no user identity into a write;
   identity comes from the authenticated session, not from the conversation.

## Where this sits

- `aipos-product-strategy` owns new-product framing; this skill packages one
  evidenced problem from the graph.
- `aipos-solution-framing` takes an accepted problem and frames solution options —
  after gate 1, not this artifact.
- `aipos-exploration-planning` decides which opportunities get capacity; this skill
  hands it the package it allocates against.

Gate 1 remains a human decision. The package informs it; the reviewer governs it.
