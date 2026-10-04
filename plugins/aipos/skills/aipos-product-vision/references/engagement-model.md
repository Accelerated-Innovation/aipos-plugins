# Engagement model

How the review roster is decided, and why it is not a conversation.

## The shape of it

```
triage answers  →  risk tier  →  baseline roster
                       +
              trigger escalations  →  final roster (right + engagement per reviewer)
```

All of it is computed by `scripts/verify_vision.py` from `data/engagement-policy.json`. The skill
reads the result. It does not reason about who should be in the room, and neither does the AIOS
screen when it exists.

## Rights: what a reviewer may do

| Right | May | May not |
|---|---|---|
| `shape` | Change where the product is aimed — the outcome, the measures, the boundaries | — |
| `constrain` | Impose a constraint, narrow the scope, rule an approach out | Re-aim the product |
| `inform` | Comment, for the record | Hold the brief |

This distinction is the whole point. Engineering and Architecture hold `shape` because feasibility
can legitimately change what you are aiming at, and learning that here is far cheaper than learning
it at Step 7. Security, Compliance, Privacy, Finance and People hold `constrain` because a
constraint is real but it is not a product direction. Without the split, a review round turns into
design by committee and the Product Lead loses the brief.

## Engagement levels

| Level | Meaning |
|---|---|
| `blocking` | Must respond before the brief can be finalized. Every raise needs a disposition |
| `advisory` | Invited; raises need dispositions if made, but silence does not hold the brief |
| `inform` | Receives a copy. No response expected |
| `absent` | Not engaged at this tier |

## Scope does not change the roster

Triage runs in every mode and every scope, increments included. A small increment on a safe product
can still be the one that touches regulated data, so an increment never inherits its parent's risk
tier — it computes its own.

## Tiers

| Tier | When | Shape of the review |
|---|---|---|
| `tier_1` Standard | No material risk dimension live | Engineering shapes; everyone else is informed |
| `tier_2` Elevated | Any one of sensitive data, autonomous action, regulated domain, external users | Security and Privacy blocking; Compliance advisory |
| `tier_3` High | Regulated **and** (sensitive data or autonomous action), or three or more dimensions live | Security, Compliance and Privacy all blocking; the accountable owner is named before the round opens |

Round ceilings rise with tier: 3, 4, 5. When the ceiling is hit without readiness, **escalate rather
than open another round** — a brief that will not converge is a decision that needs making.

## Escalations that ignore the tier

Some triggers engage a reviewer regardless of tier, because the trigger is that reviewer's call and
not a risk average:

| Trigger | Effect |
|---|---|
| `regulated_domain` | Compliance becomes blocking |
| `sensitive_data` | Data and Privacy becomes blocking |
| `committed_spend` | Finance becomes blocking |
| `workforce_impact` | People and HR becomes blocking |
| `brand_attribution` | Marketing becomes advisory **and its right rises to `shape`** |

That last one is deliberate. When output carries the company's or a client's name, how the product
sounds is part of what it is, so Marketing gets a say in the brief rather than only in the wording.

## Not Sure

Not Sure routes **exactly as Yes** and raises a `GAP · triage` naming the reviewer it engaged.

The brief cannot ratify with an open triage gap, so the question gets settled — but it gets settled
with the reviewer already in the room rather than before anyone has looked. A Product Lead who does
not know whether the product touches a regulated domain is precisely the case where Compliance
should be reading it.

Closing the gap can remove a reviewer from the roster. That is fine and expected. What is not
available is leaving it open.

## The Learn mode grant

Learn mode is granted by the **named accountable owner**, in their name, with a reason and a review-by
date. Not by the Product Lead, not by the triage answers, and not by this skill.

Before asking for the grant, **show the owner the computed roster**. That is the whole substance of
what they are deciding: a tier_2 product in Learn mode means Security and Data Privacy, who the triage
made blocking, drop to inform. The verifier prints this as **ROUTED PAST BY THE GRANT** and it belongs
in front of the owner before they answer, not in the record afterwards.

> Three reviewers would have been engaged on this brief: Security and Data Privacy as blocking,
> Compliance as advisory. A Learn mode grant drops them to inform. Granting it is your call, Marcus,
> what is the reason, and by what date will you look at this again?

The grant does not travel. A new record starts in Commit mode however the last one went, and promotion
is one-way: a Learn-mode vision that has become a Product Vision does not go back.

**Why the grant survived the peer framing.** Calling these peer modes removes the implication that one
is a lesser copy of the other, which is the point. It also removes the sense that the lighter one needs
justifying, and that sense was doing real work. The grant is what keeps it: the mode is a peer in the
language and an owner's decision in the mechanism. If the grant is ever dropped because "it is just a
mode choice now", the structure survives and the control does not.

## Promotion

Promotion to a Product Vision is the accountable owner's decision. The verifier computes **promotion
signals** and reports them on every run:

| Signal | Fires when |
|---|---|
| S1 Risk profile changed | Any triage answer is now Yes or Not Sure |
| S2 Real users | Anyone outside the build team uses it or receives its output |
| S3 Production or client data | It has moved off synthetic or sample data |
| S4 Review-by date passed | The granted window has ended |
| S5 Spend committed | Budget, headcount or a contract beyond discovery |

Signals never promote a brief and never block one. The single rule that backs them is check **L6**: a
Learn-mode vision cannot sit **ratified** with a live signal the owner has not acknowledged.
Acknowledging ("seen, continuing as learning for two more weeks because…") and promoting are both one
line, and both are the owner's. If the organization decides even that is too much, deleting L6 from
`readiness-rules.json` makes the signals purely informational, and the design still holds.

What L6 buys is narrow and worth being precise about: it does not stop a Learn mode build from
drifting, and it is not meant to. It stops one from drifting *unnoticed*.

## When someone asks to skip a reviewer

This will happen, usually as schedule pressure late in a round. The answer is the same every time:

> The roster came from the triage answers, and Security and Compliance own the policy that routes
> it. I can show you which answer put <reviewer> on this brief. If that answer is wrong, change it
> and the roster recomputes. If the policy is wrong, that is a change to
> `engagement-policy.json` and a version bump, and it applies to every brief after it.

Three things make this answer honest rather than bureaucratic: the routing rule is visible, the
triage answer is changeable, and the policy is a file somebody owns. Never make an exception in the
conversation. An undocumented exception is indistinguishable from the policy not existing.

## What gets recorded

Every brief records the `policy_version` it was routed under. A brief routed in March under a
different policy stays auditable in October without anyone reconstructing what the rules used to be.

Reviewer responses are recorded against the **named person**, not the roster slot. "Security
reviewed it" is not a record; "Priya Raman, Security, responded on 14 October with two blocking
raises" is.
