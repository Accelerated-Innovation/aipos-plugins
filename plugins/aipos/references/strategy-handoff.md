# Product strategy handoffs

Shared by product-strategy, exploration-planning, solution-framing, rapid-validation,
and epic-create. The Product Opportunity Brief owns product-level choices. Other
artifacts reference those choices and own their local decisions. No skill needs
to reconstruct or copy the whole strategy to accept a scoped handoff.

## Minimum handoff

Carry these fields as links or a compact record; unknowns remain explicit:

| Field | Contents |
|---|---|
| Source brief | Canonical path/record, revision and relevant section; unknown if none exists |
| Context | Relevant target segment, need, outcome, constraints; proposed/adopted status |
| Evidence | Actual source IDs/locations, claim marks and access/fitness limits |
| Assumptions | Open questions that affect this work; the first uncertainty to address |
| Decision sought | Strategy agreement, bounded learning, investment recommendation, or production-scope decision; authority status separately |
| Learning limits | Supplied authorization, owner, budget and horizon; otherwise unknown or proposed |
| Next owner | Named skill and the specific artifact/action requested |

A source brief is optional for existing work. A missing brief never blocks a
requested experiment, canvas, epic, or behavior task. A bare brief reference does
not supply an exploration mandate. Strategy agreement does not authorize learning
or production; evidence supporting investment does not record approval. Preserve
existing actual authority and its limits when supplied.

## Routes

- **Product strategy → rapid-validation:** the assumption, evidence, decision
  sought, and recommended method. Rapid-validation owns interview guides, sizing,
  demand tests, prototypes, feasibility/evaluation work, and experiment findings.
  It can begin without a graph or baseline. Findings return with provenance for
  strategy review; detailed artifacts reference the brief instead of copying it.
- **Product strategy → solution-framing:** a sufficiently framed initiative problem,
  segment and outcome, with the relevant brief sections and evidence. Solution
  options and its canvas remain solution-framing's work.
- **Product strategy → exploration-planning:** allocate research capacity across
  opportunities only with the live graph reads that planning requires. Brief
  choices inform the discussion but do not invent graph entries, rankings,
  mandates, or decisions. An empty/unavailable graph can still permit local
  strategy and validation work.
- **Product strategy → epic-create:** only when an epic is requested, passing the
  initiative context and source references. The optional epic is not the product
  strategy and grants no investment or delivery approval.
- **Research/product results → product strategy:** identify the original hypothesis,
  population, period, criterion if adopted, findings and limits. Product-strategy
  owns deciding what changes to the brief to recommend. Other systems own
  analytics; their data must actually be supplied or read.

## Current canvas compatibility boundary

The strategy brief accepts attributable supplied research outside the graph.
The current Solution Framing canvas has stricter rules: its primary baseline must
be graph-backed to offer Proceed; its no-graph path remains a PM-account draft;
a linked-record `[T]` transcription cannot unlock Proceed. Neither an adopted
strategy nor permission for an experiment changes those rules. Do not copy a
brief's evidence labels into the canvas and claim the graph was read.

If this blocks the requested recommendation, state the gap. Hand baseline
collection or source accessibility work to rapid-validation/research intake and
resume the canvas when its own evidence requirements are met. A draft canvas can
still be facilitated under its existing rules. New findings need the intended
system-of-record intake; saving the brief does not perform ingestion.

The canvas's Proceed/Pivot/Park is a learning decision made before experiments;
the viability brief's GO/REVISE/NO-GO decides production investment once the
evidence is in. The two do not map onto each other (see `aipos-solution-framing`'s
*Two different decisions* and `aipos-rapid-validation`'s viability brief). Keep
the origin, timing, evidence state, and decision sought explicit. A canvas
recommendation is an input to validation, never the result of experiments not run.
Do not convert a strategy's “learn next” into production GO.

A bounded follow-up should examine the ReOps-to-graph baseline adapter, with
cold-start and transcription evaluations.
This product-strategy addition does not change canvas approval, baseline, or
recommendation rules. Production behavior, commitment preparation, actual
approval, and execution-readiness continue through their existing owners.
