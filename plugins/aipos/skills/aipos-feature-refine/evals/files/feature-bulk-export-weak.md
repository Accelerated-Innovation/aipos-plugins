# Feature: Bulk export of customer records (WI-5104)

| Role | What it means | Examples |
|---|---|---|
| **Generator** | Whatever produced Draft 0 | Aha! Feature Agent, an LLM prompt, a human author |
| **Tracker** | Wherever the feature fields live | Azure DevOps, Jira, Linear, a markdown file |

## Description

Account managers need to export customer records to CSV so they can prepare
quarterly business reviews. The export should include customer profile fields
and activity history.

## Acceptance Criteria

```gherkin
Feature: Bulk customer export

  Scenario: Export customer records to CSV
    Given I am on the customer list page
    When I select customers and click "Export"
    Then a CSV file downloads with the selected customer records

  Scenario: Export completes for a large selection
    Given I have selected 5,000 customers
    When I click "Export"
    Then the CSV file downloads successfully
```

## NFRs

None provided.

## Evaluation Criteria

None provided.

## Open questions

- Which customer fields are included in the export? Some profile fields may
  contain PII — unresolved, waiting on privacy review.

## Out of scope

Not stated.
