# Feature: Loyalty tier upgrade on annual review (WI-6012)

| Role | What it means | Examples |
|---|---|---|
| **Generator** | Whatever produced Draft 0 | Aha! Feature Agent, an LLM prompt, a human author |
| **Tracker** | Wherever the feature fields live | Azure DevOps, Jira, Linear, a markdown file |

## Description

Each year on a member's anniversary, the loyalty programme reviews the points
they earned in the preceding twelve months and upgrades their tier. Gold members
receive priority support and free returns.

## Acceptance Criteria

```gherkin
Feature: Loyalty tier upgrade on annual review

  Rule: Members with 50,000 or more points in the review year are upgraded to Gold

    Scenario: A high-earning member is upgraded
      Given a Silver member earned 61,000 points in the review year
      When the annual review runs
      Then the member's tier is "Gold"

  Rule: Members below 60,000 points remain at their current tier

    Scenario: A mid-earning member is not upgraded
      Given a Silver member earned 52,000 points in the review year
      When the annual review runs
      Then the member's tier is unchanged

  Rule: Members who returned more than the acceptable share of their orders are excluded from upgrade

    Scenario: A high-return member is excluded
      Given a Silver member earned 61,000 points in the review year
      And the member returned an excessive share of their orders
      When the annual review runs
      Then the upgrade is handled appropriately
```

## NFRs

- Performance: the annual review batch completes overnight. Evidence: batch run
  log. Owner: Engineering.

## Evaluation Criteria

None provided.

## Open questions

- What counts as "an excessive share" of returns? Percentage not yet agreed.

## Out of scope

Not stated.
