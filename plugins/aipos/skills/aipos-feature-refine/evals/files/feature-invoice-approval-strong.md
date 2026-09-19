# Feature: Invoice approval routing (WI-4821)

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
Feature: Invoice approval routing
  Finance invoices route to the correct approval path based on amount,
  and every approval decision is recorded for audit.

  Rule: Invoices of $10,000 or more require finance manager approval

    Scenario: High-value invoice routes to manager approval
      Given a finance analyst has submitted an invoice for $12,500
      When the invoice enters the approval workflow
      Then the invoice status is "Pending manager approval"
      And the assigned finance manager receives an approval task

    Scenario: Manager rejects a high-value invoice with a reason
      Given an invoice for $15,000 is pending manager approval
      When the finance manager rejects the invoice with reason "Duplicate of INV-2210"
      Then the invoice status is "Rejected"
      And the submitting analyst is notified with the rejection reason
      And the rejection is recorded in the audit log

  Rule: Invoices under $10,000 are auto-approved

    Scenario: Low-value invoice is auto-approved
      Given a finance analyst has submitted an invoice for $4,200
      When the invoice enters the approval workflow
      Then the invoice status is "Approved"
      And the approval is recorded in the audit log with approver "system"

  Rule: Only finance roles can submit invoices for approval

    Scenario: Non-finance user cannot submit an invoice
      Given a user with the "Sales" role is signed in
      When the user attempts to submit an invoice
      Then the submission is refused with an authorization error
      And no invoice record is created
```

## NFRs

- Performance: approval routing decision completes within 2 seconds of
  submission at the 95th percentile. Evidence: performance test report.
  Owner: Engineering.
- Auditability: every approval, auto-approval, and rejection writes an
  immutable audit record (actor, timestamp, decision, reason). Evidence:
  audit log inspection in QA sign-off. Owner: QA.
- Security: submission and approval endpoints enforce role-based access.
  Evidence: automated authorization tests in CI. Owner: Engineering.

## Evaluation Criteria

None. This feature has no AI or decision-support behavior; ordinary test
evidence applies.

## Assumptions

- The $10,000 threshold is fixed for this release; configurable thresholds
  are a later feature.

## Out of scope

- Multi-currency invoices
- Delegated approval when a manager is out of office
