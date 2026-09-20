# Feature: Warehouse stock adjustments (WI-6220)

| Role | What it means | Examples |
|---|---|---|
| **Generator** | Whatever produced Draft 0 | Aha! Feature Agent, an LLM prompt, a human author |
| **Tracker** | Wherever the feature fields live | Azure DevOps, Jira, Linear, a markdown file |

## Description

Warehouse supervisors correct stock levels after a physical count. Every
adjustment records the counted quantity, the variance against the system figure,
and the supervisor who made it.

**Delivery note:** the team will implement this feature with an AI coding agent,
as they do for all work this quarter. The product itself contains no model
inference of any kind — the adjustment rules below are deterministic arithmetic
against the stock ledger.

## Acceptance Criteria

```gherkin
@feature
Feature: Warehouse stock adjustments

  As a warehouse supervisor
  I want to correct stock levels after a physical count
  So that picking lists reflect what is actually on the shelf

  @rule:variance-approval-threshold
  Rule: Adjustments with a variance above 100 units need a second approver

    @mvp @functional @scenario:variance-approval-by-size
    Scenario Outline: Variance size decides whether a second approver is needed
      Given the system holds 500 units of SKU "BRK-4410"
      When supervisor Dana Ellis records a counted quantity of <counted>
      Then the adjustment status is "<status>"

      Examples: Around the second-approver threshold
        | counted | status            |
        | 401     | Applied           |
        | 400     | Awaiting approval |
        | 250     | Awaiting approval |

  @rule:adjustment-audit-record
  Rule: Every adjustment is attributable

    @mvp @functional @scenario:adjustment-records-actor
    Scenario: An applied adjustment records who made it
      Given the system holds 500 units of SKU "BRK-4410"
      When supervisor Dana Ellis records a counted quantity of 480
      Then the stock ledger shows 480 units of SKU "BRK-4410"
      And the adjustment record names "Dana Ellis" with the counted and system figures

  @rule:supervisor-role-required
  Rule: Only warehouse supervisors may record adjustments

    @mvp @security @scenario:non-supervisor-refused
    Scenario: A picker cannot record an adjustment
      Given a user with the "Picker" role is signed in
      When the user attempts to record a stock adjustment
      Then the attempt is refused with an authorization error
      And the stock ledger is unchanged
```

## NFRs

- Performance: an adjustment is applied within 1 second at the 95th percentile.
  Evidence: performance test report. Owner: Engineering.
- Security: adjustment endpoints enforce role-based access. Evidence: automated
  authorization tests in CI. Owner: Engineering.
- Data quality: the stock ledger and the adjustment record never disagree.
  Evidence: reconciliation report in CI. Owner: QA.
- Observability: every adjustment emits an audit event. Evidence: log assertion
  in the integration suite. Owner: Engineering.

## Evaluation Criteria

None. The product performs no model inference; ordinary test evidence applies.

## Assumptions

- The 100-unit variance threshold is set by warehouse operations and fixed for
  this release.

## Out of scope

- Cycle-count scheduling
- Multi-warehouse transfers
