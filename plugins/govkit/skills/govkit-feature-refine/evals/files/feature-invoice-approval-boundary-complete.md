# Feature: Invoice approval routing (WI-4821, boundary-complete)

| Role | What it means | Examples |
|---|---|---|
| **Generator** | Whatever produced Draft 0 | Aha! Feature Agent, an LLM prompt, a human author |
| **Tracker** | Wherever the feature fields live | Azure DevOps, Jira, Linear, a markdown file |

## Description

Finance analysts submit vendor invoices for payment. Invoices at or above the
manager-approval threshold must be approved by a finance manager before payment
is scheduled. Invoices below the threshold are auto-approved. Rejected invoices
return to the submitting analyst with a required rejection reason.

## Acceptance Criteria

```gherkin
@feature
Feature: Invoice approval routing
  Finance invoices route to the correct approval path based on amount,
  and every approval decision is recorded for audit.

  @rule:invoice-approval-threshold
  Rule: Invoices of $10,000 or more require finance manager approval

    @mvp @functional @scenario:approval-routing-by-amount
    Scenario Outline: Invoice amount decides the approval path
      Given a finance analyst has submitted an invoice for <amount>
      When the invoice enters the approval workflow
      Then the invoice status is "<status>"
      And the approval record names approver "<approver>"

      Examples: Around the manager-approval threshold
        | amount     | status                   | approver        |
        | $9,999.99  | Approved                 | system          |
        | $10,000.00 | Pending manager approval | finance manager |
        | $12,500.00 | Pending manager approval | finance manager |

    @mvp @functional @scenario:manager-rejects-with-reason
    Scenario: Manager rejects a high-value invoice with a reason
      Given an invoice for $15,000 is pending manager approval
      When the finance manager rejects the invoice with reason "Duplicate of INV-2210"
      Then the invoice status is "Rejected"
      And the submitting analyst is notified with the rejection reason
      And the rejection is recorded in the audit log

  @rule:finance-role-required
  Rule: Only finance roles can submit invoices for approval

    @mvp @security @scenario:non-finance-submission-refused
    Scenario: Non-finance user cannot submit an invoice
      Given a user with the "Sales" role is signed in
      When the user attempts to submit an invoice
      Then the submission is refused with an authorization error
      And no invoice record is created
```

## NFRs

- Performance: approval routing decision completes within 2 seconds of
  submission at the 95th percentile. Evidence: performance test report.
  Owner: Engineering. Scenarios: @scenario:approval-routing-by-amount.
- Auditability: every approval, auto-approval, and rejection writes an
  immutable audit record (actor, timestamp, decision, reason). Evidence:
  audit log inspection in QA sign-off. Owner: QA.
- Security: submission and approval endpoints enforce role-based access.
  Evidence: automated authorization tests in CI. Owner: Engineering.
  Scenarios: @scenario:non-finance-submission-refused.

## Evaluation Criteria

None. This feature has no AI or decision-support behavior; ordinary test
evidence applies.

## Assumptions

- The $10,000 threshold is fixed for this release; configurable thresholds
  are a later feature.

## Out of scope

- Multi-currency invoices
- Delegated approval when a manager is out of office
