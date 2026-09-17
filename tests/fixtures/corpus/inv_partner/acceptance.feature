@feature
Feature: Partner invoice approval

  A second feature that deliberately reuses the local slug
  `invoice-approval-threshold` from inv_full. Within its own file the slug is
  unique, which is all the authoring standard requires — so two features can
  legitimately carry the same slug, and a reference that omits the feature key
  cannot say which one it means.

  @rule:invoice-approval-threshold
  Rule: Partner invoices of any amount require partner-manager approval

    @mvp @functional @scenario:partner-approval-required
    Scenario: A partner invoice waits for its partner manager
      Given a partner invoice for $250
      When it is submitted
      Then it is routed to the partner manager for approval
      And it is not paid before that approval

    @v1 @functional @scenario:partner-manager-unavailable
    Scenario: Approval falls back when the partner manager is away
      Given a partner invoice for $250
      And the partner manager is out of office
      When it is submitted
      Then it is routed to the partner-manager delegate
