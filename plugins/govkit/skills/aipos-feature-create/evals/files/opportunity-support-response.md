# Opportunity: support representatives re-check answers they have already sent

**PDG opportunity:** PDG-OPP-4471
**Decision thread:** PDG-THREAD-4471-a
**Exploration decision:** explore — budget 2 weeks, horizon end of quarter
**Tracker record:** none. No epic exists and none is planned.

## Outcome being pursued

A support representative can answer a customer with an evidence-backed response they have
explicitly approved, without a draft ever leaving the product unapproved.

## Evidence

| Ref | What it is | What it shows |
|---|---|---|
| PDG-EV-2201 | 9 representative interviews | Seven describe re-reading answers after sending, to check whether the version that went out was the one they meant to approve. |
| PDG-EV-2208 | Support tooling telemetry | 14% of outbound responses are followed within 30 minutes by a correction message from the same representative. |
| PDG-EV-2213 | One team lead, high-volume queue | Reports that any added approval step will cost them throughput. Contradicts the direction; recorded, unresolved. |

## Conversations

The team believes an approval step is the answer, and that an evidence-retrieval agent should
assemble supporting material for the representative to check. Nobody has said what happens when
the retrieval agent cannot find enough evidence, and nobody has proposed a number for what
"enough" means.

The compliance lead mentioned in passing that approvals need to be attributable afterwards, but
has not said for how long records must be kept.

## Prototype

A clickable prototype exists. It sends automatically when the retrieval agent's confidence is
high, because that was quicker to demonstrate. Nobody has decided whether it should.
