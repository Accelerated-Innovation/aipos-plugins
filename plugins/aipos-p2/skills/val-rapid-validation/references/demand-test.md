# 4 — Demand test

**Retires:** *Will the solution actually solve it?* — the adoption half.
**Produces:** an experiment design with a stopping rule, ready to run.

A prototype test tells you whether people *can* use it and say they like it. A demand test
tells you whether they will actually do something that costs them — click, sign up, pay,
give up a slot in their week. The gap between the two is where most product failures live.

## Pick the instrument

Ask what the PM can actually put in front of people this month, then choose:

| Instrument | Measures | Costs | Use when |
|---|---|---|---|
| **Fake door** | Click-through to a described capability | Hours | The capability is easy to describe and you have traffic |
| **Landing page + signup** | Willingness to give an email and wait | Days | There's no existing surface to instrument |
| **Concierge** | Willingness to use it when a human does the work | Weeks | The value is real but the automation is expensive |
| **Pre-sale / LOI** | Willingness to commit money or signature | Weeks | B2B, high ticket, few buyers |
| **Waitlist with a cost** | Demand strong enough to survive friction | Days | You need to separate polite interest from intent |

Bias toward the one with the highest cost to the user that you can realistically run.
A click is weak evidence; a signature is strong. If the honest option is a fake door,
run the fake door — but say in the brief what it can and cannot prove.

### On fake doors, briefly

A fake door shows a real entry point to a capability that does not exist yet and counts
who tries. It works. It also spends a little of your users' goodwill, so: land people
somewhere honest ("this isn't built yet — want us to tell you when it is?"), never take
money for something that doesn't exist, and don't run one repeatedly against the same
audience. Say this to the PM once; most already know, and the ones who don't need to.

## Interview the PM

1. **What action counts as demand?** One primary action, defined precisely enough that two
   people would count it the same way.
2. **Against what baseline?** A conversion number with nothing to compare it against is
   unreadable. Find an existing rate on a comparable surface, or state up front that this
   is establishing the baseline.
3. **What rate would change the decision?** Set the threshold *before* running. This is
   the whole discipline — a threshold chosen afterwards is a rationalisation.
4. **How much traffic can you get, and how fast?** This determines whether the result can
   mean anything. Do the arithmetic with them.
5. **What's the honest landing?** What the user sees after they act.

## Output template

```markdown
# Demand test — <capability>

## Evidence base
<the evidence-base header from evidence-intake.md>
**Mandate cost:** <the instrument's duration against the horizon — a Weeks-class instrument inside a two-week horizon does not fit; say so and name the Days-class alternative | none declared>

## Hypothesis
If <audience> is offered <capability, in their language>, at least <rate> will <action>.
[E/I/A]

## Instrument
<Fake door | landing page | concierge | pre-sale | waitlist>, because <why this one is
the highest-cost signal we can actually run>.

## What counts
- **Primary metric:** <action>, defined as <precise definition>
- **Baseline:** <comparable rate and where it comes from> [E/I/A]
- **Guardrail:** <what must not get worse — support volume, unsubscribes, trust>

## Decision rule — set before running
| Result | Reading | Action |
|---|---|---|
| ≥ <strong> | Demand confirmed | <next step> |
| <weak>–<strong> | Inconclusive | <what we'd change and retest> |
| < <weak> | Demand not there | <stop / reframe> |

## Sample and stopping rule
- **Exposure needed:** <n> — because at the baseline rate, fewer than this can't
  distinguish <strong> from <weak>.
- **Duration:** <window>, covering <at least one full weekly cycle>. Inside the horizon:
  <yes | no, by <n> days>.
- **Stop when:** <n reached, or the window closes> — whichever comes first.
- **Do not stop early on a good result.** Early stopping on a favourable number is the
  most common way these tests lie.

## What the user experiences
<The exact copy of the offer, and what they see after they act. Write the honest landing
in full — it's the part that gets improvised badly if it isn't specified.>

## Confounds to watch
<Seasonality, a concurrent campaign, an audience that skews to power users, novelty
effects in week one.>

## What this can't prove
<Say it plainly. A click is interest, not retention. Signups are not usage. Concierge
demand at ten users may not survive at a thousand.>
```

## The arithmetic, plainly

If the baseline is 2% and the PM wants to detect a lift to 4%, a hundred exposures cannot
tell those apart — the noise is larger than the effect. Do this calculation with them
before they run anything, and if the traffic isn't there, say so and pick a
higher-signal instrument instead. A demand test that couldn't have detected its own
hypothesis is worse than none, because it produces a number people then act on.

## GenAI angle

Two things are worth separating and are easy to conflate.

**Novelty inflates first-run demand.** Users click AI features because they're curious.
Where possible, measure a second action — did they come back, did they use it twice — and
say in the brief that first-run numbers are an upper bound.

**Willingness to rely is not willingness to try.** For a feature whose value depends on
trust, the interesting metric is often not "did they use it" but "did they act on its
output without checking." If the instrument can capture that, capture it.
