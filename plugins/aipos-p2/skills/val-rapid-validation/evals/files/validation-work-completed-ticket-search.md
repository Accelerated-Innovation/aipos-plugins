# Ticket-search assistant — validation work completed, 2026-10-13

## Exploration Decision (recorded — REOPS-2041)

```
Problem:        PRB-118 — Support agents spend a large share of each shift searching
                closed tickets for similar cases, and mostly fail to find them [E]
Decision:       explore
Owner:          Priya Natarajan (Support Product)
Budget:         5 interviews + 1 feasibility spike (2 days)
Horizon:        2026-10-15
Status:         recorded — REOPS-2041
Record via:     research-intake lifecycle → propose-opportunity approve
```

## Artifacts and results

| Artifact | Done | Result | Budget used |
|---|---|---|---|
| Interview guide | 2026-09-26, 5 sessions | 5/5 confirm title-only search fails them; 4/5 keep a workaround. Rule met. | 5 of 5 interviews |
| Problem sizing | 2026-09-18 | $290k–$420k/yr in agent time [I]; threshold $150k cleared at the low end; minutes/day is the dominating assumption [A] | none |
| Visual prototype | not run | — | — |
| Demand test | 2026-10-08, concierge, 6 agents, 3 days | 6 of 6 used the human-backed lookup daily; median 2.1 lookups/agent/day; 0 support-volume regression. Decision rule (≥ 4 of 6 daily use) met. | 3 days of horizon; **not in the budget** — owner approved on 2026-10-03 |
| Feasibility spike | 2026-10-07, 2 days | Closed-ticket bodies are searchable with the vendor embedding API; top-3 hit rate 71% on a 40-ticket labelled set [E]; kill threshold (< 50%) not hit. PII in ticket bodies needs redaction before indexing [E]. | 2 of 2 days |
| Eval stub | 2026-10-09 | Dimensions: retrieval hit rate, answer groundedness, PII leakage; starter set of 40 labelled tickets; threshold for the decision: hit rate ≥ 65%, 0 PII leaks | none |

Horizon: 2 days remain.

## Owner's note

Priya approved the demand test on 2026-10-03 as an addition to the mandate after the
interviews came back stronger than expected. Recorded as a comment on REOPS-2041.
