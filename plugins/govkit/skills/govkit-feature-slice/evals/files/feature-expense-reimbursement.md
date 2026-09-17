# Feature: Expense reimbursement (FIN-410)

## Description

Employees submit expense claims; finance approves them; approved claims are paid in the next
run. Claims above a threshold need a second approver. The receipt store is owned by a separate
feature.

## Acceptance Criteria

```gherkin
@feature
Feature: Expense reimbursement

  Employees claim what they spent, finance approves it, and approved claims are paid.

  @rule:claims-require-approval-before-payment
  Rule: No claim is paid before an authorized approver has approved it

    @scenario:submit-claim
    Scenario: An employee submits a claim
      Given an employee has a receipt for a $40 taxi fare
      When they submit a claim for it
      Then the claim is recorded as awaiting approval

    @scenario:approver-approves-claim
    Scenario: An authorized approver approves a claim
      Given a claim awaiting approval
      When a finance approver approves it
      Then the claim is marked approved
      And it is included in the next payment run

    @scenario:unauthorized-approver-rejected
    Scenario: Someone without approval authority cannot approve
      Given a claim awaiting approval
      And a user who does not hold finance-approver authority
      When that user attempts to approve the claim
      Then the approval is refused
      And the claim remains awaiting approval

  @rule:large-claims-need-two-approvers
  Rule: A claim of $2,000 or more requires a second approver

    @scenario:second-approver-required-at-threshold
    Scenario Outline: Large claims wait for a second approval
      Given a claim for <amount>
      When one approver approves it
      Then the claim is <state>

      Examples:
        | amount  | state                        |
        | 1999.99 | approved                     |
        | 2000.00 | awaiting a second approval   |
        | 5000.00 | awaiting a second approval   |

  @rule:payment-failures-are-recoverable
  Rule: A failed payment leaves the claim recoverable

    @scenario:payment-failure-is-retryable
    Scenario: A failed payment can be retried without re-approval
      Given an approved claim in a payment run
      When the payment fails at the bank
      Then the claim is shown as unpaid with the failure reason
      And it can be retried without a further approval

  @rule:claims-attach-receipts
  Rule: A claim carries the receipt it is based on

    @scenario:claim-shows-attached-receipt
    Scenario: A reviewer sees the receipt while approving
      Given a claim submitted with a receipt
      When an approver opens the claim
      Then the receipt is displayed alongside the amount
      # Receipt storage and rendering are owned by FIN-388 (Receipt store),
      # which is not yet committed to any release.

  @rule:claims-can-be-exported
  Rule: Finance can export approved claims

    @scenario:export-approved-claims-to-csv
    Scenario: Export approved claims for the accounting system
      Given a set of approved claims
      When finance exports the month
      Then a CSV downloads containing each approved claim
```

## NFRs

| ID | Area | Requirement |
|---|---|---|
| NFR-1 | Compliance | Every approval records approver identity and timestamp, retained 7 years. |
| NFR-2 | Security | Approval authority is checked server-side on every approval attempt. |
