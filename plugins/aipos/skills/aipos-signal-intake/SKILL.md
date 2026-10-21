---
name: aipos-signal-intake
description: "Report which step 1 signal sources feed the Product Definition Graph — source by source: connection state, whether records are present, last ingestion and volume in a window, each with its own basis or 'unknown' — and draft connector requests for missing sources. Use when asked whether customer signals are current, which sources aren't feeding the graph, or for step 1 Ingest Signals coverage. Read-only; never starts an ingestion run. Choosing which problems get exploration capacity belongs to aipos-exploration-planning."
---

# AIPOS Signal Intake

Step 1 is done when *"signals land on a repeatable cadence, not on request"*. This skill answers
"are our signals current?" with a table a PM can act on: every step 1 source, what is known about
it, how that is known, and a drafted connector request for each source that is missing. Read
`references/step-1-sources.md` first: it holds the source list and the request template.

> "AI acts. Evidence informs. Humans govern." — AIPOS Canon

## What can be known, and from where

Five separate fields per source. Each has its own basis and its own fallback; one field never
stands in for another.

| Field | Authoritative basis | Without it |
|---|---|---|
| Connection | An ingestion-status read, or a supplied inventory naming the source (attributed to whoever supplied it) — never graph records, never what the engine's code supports | `unknown` |
| Records in graph | `list_evidence` across the problems read, grouped by `source_system` | `not checked` |
| Last ingestion | An ingestion-status read, or a supplied status note (attributed, unverified) | `unknown — no ingestion-status read` |
| Volume in window | An ingestion-status read, or a supplied status note (attributed, unverified) | `unknown` |
| Staleness | Last ingestion compared with an agreed cadence, both known | `unknown` |

- **Records are not connection, and evidence dates are not freshness.** Records from a source
  show it delivered something at some point. They do not show the connector is connected now,
  when it last ran, or how much arrived in a window. `occurred_at` is when an event happened, not
  when it was ingested: never report the newest evidence date as last ingestion, and never count
  evidence by `occurred_at` as window volume.
- **No status read, no freshness claim.** As of the last verification (see the reference), the
  engine exposes no ingestion-status read. Say freshness is unknown and name the missing
  capability. If a connected server does advertise a status read, report its values labelled
  *unverified contract* until its response fields are confirmed against the engine's published
  contract; do not call that freshness authoritative.
- **Absence needs coverage.** "No records" is only as strong as the read behind it: always state
  how many problems were read out of how many, and name any that failed. A failed read is not an
  empty one.

## Instructions

1. **Find the inputs.** A connected Product Definition Graph read server (the seven-tool
   vocabulary: `list_problems`, `list_evidence`, …), any supplied inventory or status notes, and
   the window and cadence the PM cares about. With none of them, still produce the table with
   every field unknown and say what input would fill each field — never invent states, dates or
   volumes.
2. **Read the graph for records.** Page through `list_problems` (its order is not a ranking),
   call `list_evidence` per problem, and group by `source_system`. Record failures per problem.
   Do not call `get_evidence_text`: this report needs no evidence text, and each call is a
   logged disclosure.
3. **Fill each field from its own basis**, attributing supplied facts to their source ("per the
   admin inventory of 2026-10-20"). Supplied material — an inventory, a status note, or a capture
   of graph reads someone else made — is labelled supplied (and synthetic when it says so), never
   described as a read made in this session. With no basis for a field, the cell says `unknown`
   and names the missing input; `connected` and `not connected` both need a basis.
4. **Flag staleness only with both halves.** When last ingestion and an agreed cadence are both
   known, compute the age against today's date and flag the source when the age exceeds the
   cadence. Say which half came from where.
5. **Draft connector requests** from the reference template for every source that is not
   connected, or has unknown connection and no records. Drafts only; the skill sends nothing.
6. **Report.** One table, every step 1 source in the reference's order plus an "Also in the
   graph" row, then the drafted requests, then one line on coverage and one on what is unknown
   and why.

```text
| Source | Connection | Records in graph | Last ingestion | Volume (window) | Stale? | Request |
```

A plain table is the output; no panel is needed.

## Guardrails

- Never start, schedule, retry or request an ingestion run through a tool — even one the server
  advertises, and even after the user says yes. Ingestion runs are a service operation; offer a
  drafted request to its owner instead.
- Never infer connection from records, freshness from evidence dates, or volume from evidence
  counts.
- Never drop a step 1 source from the table because nothing is known about it.
- Never claim a live read for supplied material, or call a supplied status note verified.
- Never build or configure a connector; drafting the request is the whole job.

## Where this sits

`aipos-exploration-planning` decides which evidenced problems get capacity; this skill reports
whether the evidence is arriving at all. Building connectors and exposing an ingestion-status
read are engine work.
