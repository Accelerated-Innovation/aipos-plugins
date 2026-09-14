Feature: Bulk customer export

  Scenario: Export customer records to CSV
    Given I am on the customer list page
    When I select customers and click "Export"
    Then a CSV file downloads with the selected customer records

  Scenario: Export completes for a large selection
    Given I have selected 5,000 customers
    When I click "Export"
    Then the CSV file downloads successfully
