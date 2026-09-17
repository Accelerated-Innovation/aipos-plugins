# Journey notes: answering a customer with an approved response

**PDG opportunity:** PDG-OPP-4471

## What the team described in the walkthrough

A customer message arrives in the queue. A support representative picks it up and reads it. An
evidence-retrieval agent assembles supporting material — past tickets, docs, account state — and
the representative reviews what it found. The representative drafts a response, then approves
it. Approved responses are sent by the outbound mail service.

If the agent cannot find enough evidence, the representative handles it manually instead. Nobody
has said what "enough" means.

Editing an approved response withdraws the approval, so it has to be approved again before it
can go out. If sending fails at the gateway, the representative can retry without re-approving.

## Existing feature corpus

`support-app/FEATURE-response-approval` (source key `support-app`) contains:

```gherkin
@rule:only-approved-current-version-may-send
Rule: Only the current response version approved by an authorized support representative may be sent
  @scenario:unapproved-response-blocked
  @scenario:unauthorized-approver-rejected
  @scenario:editing-invalidates-prior-approval
  @scenario:failed-sending-shows-recoverable-state

@rule:responses-cite-their-evidence
Rule: A sent response cites the evidence it was based on
  @scenario:response-shows-cited-evidence
  @scenario:evidence-citation-survives-edit
```

`support-app/FEATURE-evidence-retrieval` (source key `support-app`) contains:

```gherkin
@rule:retrieval-is-read-only
Rule: The retrieval agent reads evidence and cannot send
  @scenario:retrieval-agent-cannot-send
  @scenario:insufficient-evidence-routes-to-person
```
