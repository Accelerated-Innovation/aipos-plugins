# Pillar 2 close-out pack — PDG-OPP-4471 (support response approval)

**Exploration Decision:** explore. Budget 3 weeks / 12 interview-hours. Horizon: 2026-10-31.
**Ledger:** used 11 of 12 interview-hours, 18 of 21 days. Owner: Priya N. (PM).

## Validation artifacts produced

| # | Artifact | Date | Finding |
|---|---|---|---|
| 1 | Interview guide + 9 sessions | 09-22 | Seven of nine representatives re-read answers after sending, to check the version that went out was the one they approved. |
| 2 | Problem sizing | 09-25 | 14% of outbound responses are followed within 30 min by a correction from the same representative. Measured from tooling telemetry. |
| 3 | Visual prototype | 10-02 | Clickable. Representatives approve a draft, then send. The prototype also sends on its own when the retrieval agent's confidence is above 0.8. |
| 4 | Feasibility spike | 10-08 | Approval state and audit record fit the existing message store. No new service needed. |
| 5 | Eval stub | 10-09 | Evidence sufficiency is a judged call, not a deterministic check. Dimensions drafted: coverage, recency, source agreement. |

## Evidence

- **PDG-EV-2201** — the 9 interviews (artifact 1).
- **PDG-EV-2208** — the 14% correction rate (artifact 2).
- **PDG-EV-2213** — a team lead on the high-volume billing queue: "any approval step costs us
  throughput we don't have; we'd turn it off."

## Readout notes (09-30, verbatim)

> Someone from the platform side said retention needs to be seven years for compliance.
> Priya: "we should get an owner on the approval-threshold question before we commit."

## Behavior drafted during validation

`support-app/FEATURE-response-approval` (source key `support-app`):

```gherkin
@rule:only-approved-current-version-may-send
Rule: Only the current response version approved by an authorized support representative may be sent
  @scenario:unapproved-response-blocked
  @scenario:unauthorized-approver-rejected
  @scenario:editing-invalidates-prior-approval
  @scenario:failed-sending-shows-recoverable-state
  @scenario:automatic-send-on-high-confidence
  @scenario:bulk-approve-queue
```

`support-app/FEATURE-evidence-retrieval`:

```gherkin
@rule:retrieval-is-read-only
Rule: The retrieval agent reads evidence and cannot send
  @scenario:retrieval-agent-cannot-send
  @scenario:insufficient-evidence-routes-to-person
```

Source revision at close-out: `1f0c9a6d3b5e27184c0a9f2d6b8e4713a5c9d0f2`.
