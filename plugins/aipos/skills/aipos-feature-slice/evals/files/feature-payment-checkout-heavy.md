# Feature: Order checkout with card payment (SHOP-118)

## Description

Customers pay for their order at checkout with a credit card. Payments are
processed by the external payment gateway (PayFlex), including 3-D Secure
verification. A paid order is confirmed and receipted.

## Acceptance Criteria

```gherkin
Feature: Order checkout with card payment
  A customer pays for an order and the order becomes confirmed exactly once.

  Rule: A customer can pay for an order with a credit card

    Scenario: Customer pays for an order with a saved card
      Given a customer has an order in "awaiting payment"
      And the customer has a card tokenized with the payment gateway
      When the customer confirms payment and completes 3-D Secure verification
      Then the payment is captured via the payment gateway
      And the order status is "confirmed"
      And the customer sees an order confirmation with a payment reference

  Rule: A declined payment leaves the order payable

    Scenario: Payment is declined by the card issuer
      Given a customer has an order in "awaiting payment"
      When the payment is declined by the card issuer
      Then the order remains in "awaiting payment"
      And the customer sees the decline reason and can retry

  Rule: A confirmed order is receipted

    Scenario: Customer receives a receipt email after payment
      Given an order has just been confirmed
      When the confirmation is processed
      Then the customer receives a receipt email listing the order and payment reference
```

## NFRs

- Security: no card data is stored or logged by the platform; all card handling
  is delegated to the gateway. Evidence: security review sign-off. Owner: Engineering.
- Reliability: a captured payment confirms the order exactly once, including
  under gateway webhook retries. Evidence: idempotency tests in CI. Owner: Engineering.

## Evaluation Criteria

None. No AI or decision-support behavior; ordinary test evidence applies.

## Out of scope

- Alternative payment methods (wallets, bank transfer)
- Refunds and partial captures
