# Solution Design Workshop — Customer Support Ticket Triage (transcribed from a hand-made canvas image)

**Goal:** Reduce triage time and improve first contact resolution

## 1 Problem & Context
- Support teams spend too much time triaging tickets
- Inconsistent categorization leads to rework and slower resolution
- High ticket volume and growing complexity
- Current state snapshot: #84217 Cannot access account (Uncategorized) · #84218 Billing charge question (Uncategorized) · #84219 Feature not working (Uncategorized)
- Impact: high handle time in triage · inconsistent categories · more escalations and rework · lower CSAT

## 2 Discovery Evidence
- 6 Support Agents interviewed — primary pain: manual categorization is time consuming
- Ticket audit — 200 recent tickets reviewed; 32% were recategorized or updated later
- Time study — average 1.8 min spent per ticket on triage
- Voice of customer — "It takes too long to get to the right team." – Enterprise Admin

## 3 Hypothesis
If we intelligently suggest or assign the right category at intake, then we can reduce triage time and improve routing accuracy without increasing agent effort.
Expected outcomes: reduce triage time per ticket **−30%** · improve correct routing **+20%** · increase agent satisfaction **+15%**

## 4 Solution Options
- A — AI Category Suggestion: AI suggests the best category; agent reviews and selects. Pros: fast to implement, assists agents. Cons: still requires manual action.
- B — Automatic Category Assignment with Override. Pros: saves more time, reduces effort. Cons: risk of incorrect assignment.
- C — Rules-Based Tagging (keyword rules). Pros: transparent, controllable. Cons: ongoing rule maintenance.

## 5 Assumptions & Risks
- Assumptions: historical data is sufficient and representative · categories are well-defined and mutually exclusive · agents trust and will adopt system recommendations
- Risks: incorrect auto-assignment may misroute tickets · bias in data may lead to poor suggestions · over-automation may reduce agent judgment
- Mitigations: confidence scores and override capability · monitor accuracy and retrain models · human-in-the-loop and gradual rollout

## 6 Validation & Decision
- Validation plan: run 4-week controlled pilot with 2 teams · compare triage time, routing accuracy, and rework · collect agent feedback and CSAT · review results and decide to scale or iterate
- Primary metric: average triage time per ticket **1.8 min → 1.2 min** · Target: 30% reduction
- Decision: PIVOT · **PROCEED (highlighted)** · PARK

## Footer
- Who benefits: Support Agents | Team Leads | Customers
- Success looks like: faster triage, accurate routing, happier agents and customers
- Impact at scale: 1 min saved per ticket × 10,000 tickets/month = **166 hours saved**
