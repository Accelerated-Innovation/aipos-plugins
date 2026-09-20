# Feature: Assisted claim file summary

**Key:** CLM-104
**Epic:** CLM-88 — Faster claims triage for regional adjusters
**Release:** V1
**Type:** Feature
**Owner:** Dana Whitfield
**Status:** Stub — not yet refined

## Description

Generate a natural-language summary of an assembled claim file so the adjuster can decide
what to do next without reading every document.

## Notes from the epic

**Primary persona:** Regional adjuster.

**Relevant success metric:** Median time from claim receipt to first adjuster action,
9.5 hours today, target under 2 hours.

**Epic-level evaluation criteria** (set on CLM-88 by the AI governance group):

| ID | Type | Threshold | Gate |
|---|---|---|---|
| EPIC-E1 | Groundedness — generated text traceable to source documents | >= 0.95 | blocking |
| EPIC-E2 | PII leakage in any generated text shared outside the claims team | 0 detections | blocking |
| EPIC-E3 | Adjuster-perceived latency for any assistive feature | p95 < 3s | blocking |
| EPIC-E4 | Cost per assisted action | <= $0.04 | advisory |

**Epic NFRs that apply:** EU claims data does not leave the EU region. Decision audit
records retained per the group retention standard.

## Known constraints

- The document assembly feature (CLM-101) must have completed before a summary can be
  generated. Summaries of partial files were explicitly ruled out in the epic review.
- Legal has asked that summaries never be shown to external partners without review, but
  the review workflow itself is not in this feature.
- No threshold has been agreed for summary usefulness or adjuster acceptance rate.
