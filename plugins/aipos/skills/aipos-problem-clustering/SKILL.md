---
name: aipos-problem-clustering
description: "Review the candidate problems the engine extracted and clustered: compare them on their evidence, and suggest merges and splits that each cite the evidence behind them, with masked quotes only and persona tags. Prepares accepted corrections as pending hand-offs and never applies them. Use for step 2 cluster review, 'should these merge?', 'is this one problem or two?', or reviewing this week's candidates. Deciding which problems get exploration capacity belongs to aipos-exploration-planning; packaging one problem for gate 1 to aipos-opportunity-package."
---

# AIPOS Problem Clustering

Step 2 extracts problems from signals and clusters them. The engine does the extracting; a person
reviews the result. This skill makes that review traceable: every suggested merge or split cites
the evidence that motivates it, quotes appear only as masked, redacted references, and an accepted
correction is prepared for whoever can apply it — never applied here.

> "AI acts. Evidence informs. Humans govern." — AIPOS Canon

## What the graph can show, and what it cannot

Reads (the engine's read vocabulary; any equivalent server works): `list_problems` (its order is
not a ranking), `get_problem` (title, score, personas with confidence, evidence references),
`list_evidence` (provenance references, source, type, date), `get_lineage` (originating sources)
and `get_evidence_text` (one redacted excerpt per call, access-logged).

- **Personas** are readable, with confidence. **Workflow tags, cluster membership and similarity
  scores are not** (engine checked 2026-10-21). Report workflow tags as unknown — never invent
  them or a grouping by them — unless the user supplies a mapping.
- **There is no correction path.** The engine retired its merge and split corrections without a
  replacement (ADR-AIG-031). A prepared correction therefore has no destination: it is a pending
  hand-off whose destination is `TBD`, owned by the product and engine leads. If a server ever
  advertises a merge or split tool, this skill still does not call it — the review is
  non-mutating, and applying a correction is a governed act by a person with authority over the
  problem inventory.

Supplied records (a capture of graph reads, pasted records) are labelled supplied — and
synthetic when they say so — never described as reads made in this session. With neither a
connected server nor supplied records, stop and say what is missing.

## Instructions

1. **Read.** Page through `list_problems`; for each candidate call `get_problem`,
   `list_evidence` and `get_lineage`. Record coverage — how many read out of how many, and every
   failed read by problem and error code. A failed read is not an empty one. A response with a
   `schema_version` other than 1 stops the review for that problem rather than being guessed at.
2. **Find the overlaps.** When the session can run Python, save the reads as a
   `cluster-reads.v1` capture and run `python3 scripts/overlap_signals.py <reads> -o <review>`:
   it lists shared evidence, shared originating sources and shared personas per pair. Otherwise
   compute the same overlaps by hand. **An overlap is where to look, not a verdict**: several
   problems drawn from one call share an origin and can still be different problems.
3. **Suggest, citing evidence.**
   - A **merge** cites, for each problem, the references that show it is the same problem — and
     names what each holds that the other does not, so the reviewer sees what a merge would
     blur. Recommending *keep separate* is as valid an answer as merge, cited the same way.
   - A **split** names one problem and at least two sides, each with its own label, persona
     where one applies, and the references behind it.
   - Mark each suggestion `[E]` when the cited records themselves show it and `[I]` when it rests
     on reading titles, personas or which side a reference belongs on without text to confirm.
     Title or wording similarity is never more than `[I]`.
4. **Quote sparingly, masked.** Fetch `get_evidence_text` only where a suggestion turns on exact
   words — **at most five excerpts per review** — and show only what the server returned
   redacted, labelled as a redacted excerpt with its reference. Never reproduce full transcripts
   or reconstruct redacted text; point people with access to the source record instead.
5. **Prepare corrections, never apply them.** When the reviewer accepts a suggestion, write it up
   as a correction hand-off: kind, problem IDs, the evidence for each side, the rationale, the
   capture it was based on, `status: pending — not applied`, and destination `TBD — no engine
   correction path`. Say plainly that nothing was merged, split or written.
6. **Answer in text; offer the board when it helps.** The plain-text review is always complete:
   one entry per candidate (ID, title, personas with confidence, evidence references, workflow
   tags as unknown), then the suggestions with their citations, then any prepared hand-offs, then
   coverage. Offer the **Cluster Review board** when the PM wants to compare many candidates side
   by side or prepare several corrections, and the session can write files and run Python: add
   the suggestions and excerpts to the review JSON and run
   `python3 scripts/render_board.py <review> -o <board.html>`. Follow
   `../../references/panel-contract.md`: the board is an **offline HTML file** opened in a
   browser, not an in-chat panel and not a live view; corrections prepared on it are pending
   hand-offs. If the renderer refuses the review, fix what it names — it refuses evidence a
   problem does not hold, one-sided splits, anything marked applied, and more than five or
   unredacted excerpts.

## Guardrails

- Never call a merge, split, propose, attach or any other tool that changes graph state, even
  when advertised and even after the user says yes.
- Never claim or imply a correction was applied; prepared means pending.
- Never suggest a merge or split without evidence references for every side.
- Never quote unredacted text, exceed five excerpts, or reconstruct redacted words.
- Never invent workflow tags, cluster membership, similarity scores or personas.
- Never call the offline board an in-chat panel or a live dashboard.

## Where this sits

The engine extracts and clusters (step 2); this skill reviews the result. Choosing which problems
get exploration capacity belongs to `aipos-exploration-planning`; packaging one problem for gate 1
to `aipos-opportunity-package`.
