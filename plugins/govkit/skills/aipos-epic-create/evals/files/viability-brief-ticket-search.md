# Viability Brief — Assisted ticket search for support agents

**Validation Decision: GO (revise scope)**
**Date:** 2026-05-14
**Owner:** Priya Raman, PM, Support Platform

Provenance marks: `[E]` evidence-backed · `[I]` inferred · `[A]` assumption

---

## Question 1 — Is the problem real and worth solving?

**Answer: yes, with a smaller prize than we assumed.**

- `[E]` Shadowing session, 2026-03-11, 6 of 40 agents: 35–50 minutes per agent per day
  spent searching historical tickets for similar cases. Median 41 minutes.
- `[E]` Support platform analytics, Jan–Mar 2026: 61% of searches are refined at least
  twice before the agent opens a result. Mean 3.2 queries per resolved search.
- `[E]` Agent interviews (9): all nine described searching as "guessing keywords". Six
  said they give up and ask a colleague instead, which was not something we had modelled.
- `[I]` Loaded cost $38/hour → roughly $390k/year of agent time across 40 agents.
- `[A]` We assumed 30% of that time is recoverable. Untested. Sensitivity: at 15% the
  annual recovery is ~$58k, at 45% it is ~$175k. The business case holds at 15%.

**The colleague-asking behavior was the surprise.** It means the real cost includes the
interrupted colleague, which we have not measured at all.

## Question 2 — Will the solution actually solve it?

**Answer: probably, for retrieval. Not proven for summarization.**

- `[E]` Fake-door demand test, 2026-04-02 to 2026-04-16: "Find similar tickets" button
  shown to 40 agents. 34 of 40 clicked it at least once; 21 used it more than five times.
- `[E]` Prototype walkthrough with 5 agents on a static retrieval mockup: 5 of 5 said they
  would use it daily. 3 of 5 independently said they would not trust a generated summary
  and would open the tickets anyway.
- `[A]` That summaries add value on top of retrieval. Explicitly unvalidated — the demand
  test measured appetite for *finding* similar tickets, not for reading a summary of them.

## Question 3 — Is it feasible and economic?

**Answer: yes for retrieval, with one data constraint.**

- `[E]` Feasibility spike, 2026-04-28: the ticket corpus (1.4M tickets, 2019–present) is
  available and indexable. Embedding the full corpus costs ~$2,100 one-off at current
  pricing, ~$60/month to keep current.
- `[E]` 22% of tickets before 2021 have empty or templated bodies and are unusable.
- `[A]` Per-search inference cost around $0.01. Not measured under real query load.
- `[E]` Legal review, 2026-05-06: ticket bodies contain customer PII. Any retrieval surface
  must not expose tickets from a different customer account to an agent not assigned to it.

## The Validation Decision

**GO, with revised scope: build retrieval, do not build summarization yet.**

Rationale: retrieval demand is evidenced `[E]`, summarization value is an assumption `[A]`
that three of five prototype participants actively pushed back on. Building both would
spend the summarization budget before testing the assumption it rests on.

**Revise:** summarization moves behind a separate validation gate — ship retrieval,
instrument whether agents ask for summaries, and revisit.

## Handoff inputs for Build-to-Earn

Naming only — writing these out is Pillar 3's job.

- **Problem statement** — agents cannot find prior similar tickets, so they re-solve solved
  problems and interrupt colleagues.
- **MVP scope** — semantic retrieval over the ticket corpus, surfaced in the agent console.
  Summarization explicitly out.
- **Evaluation criteria** — retrieval relevance is the thing that must be measured; the
  team has not agreed a threshold. Cross-account leakage must be zero.
- **Guardrail requirements** — account-scoped access enforced at retrieval time, not at
  display time. PII handling per the customer data standard.

## What we still don't know

- The cost of the interrupted colleague — never measured.
- Whether 30% of search time is actually recoverable `[A]`.
- Per-search inference cost under real load `[A]`.
- Whether agents will trust retrieval ranking without an explanation of why a ticket matched.
