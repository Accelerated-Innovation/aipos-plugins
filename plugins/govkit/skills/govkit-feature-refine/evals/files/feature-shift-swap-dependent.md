# Feature: Shift swap requests between nurses (WI-6104)

| Role | What it means | Examples |
|---|---|---|
| **Generator** | Whatever produced Draft 0 | Aha! Feature Agent, an LLM prompt, a human author |
| **Tracker** | Wherever the feature fields live | Azure DevOps, Jira, Linear, a markdown file |

## Description

A nurse can offer one of their rostered shifts for swap. Another nurse on the
same ward can accept it, and the ward manager approves the swap before the
roster changes.

## Acceptance Criteria

```gherkin
Feature: Shift swap requests

  Rule: A rostered nurse may offer a shift for swap

    Scenario: Nurse offers a shift
      Given nurse Amara Okafor is rostered for the night shift on 2026-10-14
      When she offers that shift for swap
      Then the shift appears on the ward swap board

    Scenario: Another nurse accepts the offer
      When nurse Liam Petrov accepts the offer from the previous scenario
      Then the swap is marked "Awaiting manager approval"

    Scenario: The manager approves the swap
      When the ward manager approves the swap created above
      Then the roster is updated

  Rule: A swap must not create an unsafe roster

    Scenario: An unsafe swap is handled
      Given a swap would leave the ward below its minimum staffing level
      When the ward manager reviews the swap
      Then the system responds appropriately
```

## NFRs

- Reliability: roster updates are atomic. Evidence: integration test.
  Owner: Engineering.

## Evaluation Criteria

None provided.

## Out of scope

Not stated.
