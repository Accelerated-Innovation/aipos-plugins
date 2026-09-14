# Where we are — ticket-search assistant, 2026-10-02

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

## Validation work so far

- **Interview guide** — built 2026-09-12. **Five sessions run** (agents A–E from the
  shadowing set), 2026-09-16 to 2026-09-26. Synthesis attached to OPP-118.
  Finding: 5 of 5 confirm the search fails on anything but title text; 4 of 5 keep a
  workaround (spreadsheet, chat, a colleague). Decision rule ("confirmed if 4 of 5
  describe a workaround") met.
- **Problem sizing** — built 2026-09-18 from the shadowing figures. Bottom-up range
  $290k–$420k/yr in agent time [I]; the dominating assumption is minutes per day [A].
  Decision threshold ($150k/yr) cleared at the low end of the range.
- **Feasibility spike** — **not yet run.** The 2-day spike on whether closed-ticket
  bodies are searchable with the vendor's embedding API is scheduled for 2026-10-06.

## Budget ledger

Interviews: 5 of 5 used. Spike: 0 of 1 used. Horizon: 13 days remain.
