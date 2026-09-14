@feature @v1
Feature: Invoice approval routing
  Finance invoices route to the correct approval path based on amount,
  and every approval decision is recorded for audit.

  Background:
    Given the finance period is open

  @rule:invoice-approval-threshold
  Rule: Invoices of $10,000 or more require finance manager approval

    Background:
      Given a finance manager is on duty

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

    @scenario:manager-rejects-with-reason
    Scenario: Manager rejects a high-value invoice with a reason
      Given the following invoice is pending manager approval:
        | invoice  | amount     | vendor        |
        | INV-2210 | $15,000.00 | Northwind Ltd |
      When the finance manager rejects INV-2210 with the reason:
        """
        Duplicate of INV-2118, already paid on 2026-08-03.
        """
      Then the invoice status is "Rejected"
      And the submitting analyst is notified with the rejection reason

  @rule:configurable-thresholds
  Rule: Approval thresholds are configurable per legal entity
