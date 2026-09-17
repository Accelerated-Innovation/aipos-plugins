# Feature: Support response approval

**Commitment baseline:** `commitments/support-response-approval/baseline.json`
**Baseline digest:** `sha256:f46421b637caa83e72d30fc08150dfff863842fbfeb9731e224f367761e99f21`
**Status:** Approved — this behavior is committed. Decision thread PDG-THREAD-4471-a.

The baseline binds the exact text of the Rules and scenarios below. Its digest is what the
local validator and the CI gate compare the working tree against.

## Selected behavior

```gherkin
@feature
Feature: Support response approval

  @rule:only-approved-current-version-may-send
  Rule: Only the current response version approved by an authorized support representative may be sent

    @mvp @functional @scenario:unapproved-response-blocked
    Scenario: An unapproved draft cannot be sent
      Given a drafted response that no one has approved
      When the representative attempts to send it
      Then the send is refused
      And the representative is told the response needs approval first

    @mvp @functional @scenario:unauthorized-approver-rejected
    Scenario: Someone without approval authority cannot approve
      Given a drafted response awaiting approval
      And a user who does not hold support-approver authority
      When that user attempts to approve it
      Then the approval is refused
      And the response remains unapproved

    @mvp @functional @scenario:editing-invalidates-prior-approval
    Scenario: Editing an approved response withdraws its approval
      Given a response that has been approved
      When the representative edits its text
      Then the prior approval no longer applies
      And the response must be approved again before it can be sent

    @v1 @functional @scenario:failed-sending-shows-recoverable-state
    Scenario: A failed send leaves a recoverable state
      Given an approved response
      When sending fails at the mail gateway
      Then the response is shown as not sent
      And the representative can retry without re-approving
```

## Exclusions recorded by the baseline

| Reference | Reason |
|---|---|
| `@scenario:automatic-send-on-high-confidence` | The prototype sent automatically above a confidence threshold. That behavior is NOT committed. It stays uncommitted until decided on its own evidence — a prototype demonstrating something is not a decision to build it. |
| `@scenario:bulk-approve-queue` | Attractive, and unnecessary for the first complete journey. Deferred without promise of a queue position. |

## Not part of the approved selection

Implementation notes, the persistence choice for the approval record, and the test structure
are packaging around the commitment, not part of it.
