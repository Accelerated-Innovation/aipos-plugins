# 2 — Problem sizing

**Retires:** *Is the problem worth solving?* — the second half of question one.
**Produces:** a defensible range with a visible assumption chain, not a number.

A single confident number is the failure mode here. It survives exactly one meeting, until
someone asks where it came from. A range with its assumptions exposed survives scrutiny,
and — more usefully — it tells you which assumption to go test next.

## The shape that works

**Estimate twice, from different directions, and compare.**

- **Top-down:** population × incidence × value. Starts from a market or install base.
- **Bottom-up:** unit of pain × frequency × count. Starts from a single user's day.

If the two land within roughly the same order of magnitude, you have something. If they
diverge wildly, that gap *is* the finding — one of the two chains contains an assumption
that is badly wrong, and locating it is worth more than the estimate was.

## Interview the PM

One question at a time.

1. **What are we sizing — the cost of the problem today, or the value of solving it?**
   These differ, often by a lot, and conflating them is the most common error. Cost of the
   problem is usually the honest starting point.
2. **What's the unit of pain?** Hours lost, deals slipped, tickets raised, errors shipped,
   churn. One unit, chosen deliberately. If they can't name one, go back to artifact 1.
3. **Who has it, and how many of them are there?** Push for a countable population with a
   source, even a rough one.
4. **How often, and what does one instance cost?** This is where you'll get the softest
   numbers. Take them, mark them `[A]`, and move on — the sensitivity pass is what deals
   with the softness.
5. **What number would change the decision?** The threshold. Sizing exists to be compared
   against something; without a threshold the output is trivia.

## Output template

```markdown
# Problem sizing — <problem>

## Evidence base
<the evidence-base header from evidence-intake.md>
**Mandate cost:** <desk time only — usually no mandate cost; say "none" rather than inventing one | <n> days of the horizon if inputs must be measured>

## What we're sizing
<Cost of the problem today | value of solving it>, measured in <unit>.

## Decision threshold
This is worth pursuing if the annual figure exceeds <threshold> — because <what that
number is being compared against: team cost, opportunity cost, an alternative bet>. [A]

---

## Bottom-up
| Step | Value | Basis | Mark |
|---|---|---|---|
| Users affected | | | [E/I/A] |
| Incidents per user per month | | | |
| Cost per incident | | | |
| **Annual total** | | | |

## Top-down
| Step | Value | Basis | Mark |
|---|---|---|---|
| Addressable population | | | [E/I/A] |
| % experiencing the problem | | | |
| Annual value per affected unit | | | |
| **Annual total** | | | |

## Reconciliation
<Do they agree? If not, which assumption explains the gap, and which chain do you trust
more and why?>

---

## Range
| | Annual value | What it assumes |
|---|---|---|
| Conservative | | |
| Central | | |
| Optimistic | | |

## The assumption that dominates
<Name the single input that moves the answer most. Show the swing: "if adoption is 5%
rather than 20%, the central case falls from X to Y." This is the most useful line in the
document — it tells the PM exactly what to go measure next.>

## What would change this materially
1. <measurable thing, and how to find it out>
2. <...>

## Verdict
<Above / below / straddles the threshold> → next artifact: ______
```

## Rules that keep this honest

- **Never present a number without its chain.** Every figure shows its basis and its
  marker. A number whose origin is invisible is indistinguishable from one that was
  invented.
- **Round to the precision you actually have.** "$2.4M" implies two significant figures of
  confidence. If the inputs are estimates, write "$2–3M" and be believed.
- **Never fill a gap with a plausible figure.** If the PM doesn't know the incident rate,
  the cell says `[A] unknown — assumed 2/month` and the sensitivity pass shows what that
  assumption is worth. Inventing a source is the one unrecoverable error in this skill.
- **Sanity-check against something real.** Is the implied total larger than the segment's
  entire spend? Larger than the team's revenue? Absurd totals are common and easy to catch.
- **Sizing is not a business case.** It sizes the problem. Pricing, cost to build, and
  margin belong in the feasibility spike and the viability brief.

## GenAI angle

If the solution involves model behaviour, add a line on **cost to serve**. Per-call
inference cost multiplied by the volume the sizing implies has killed more GenAI features
than technical feasibility ever has, and it is cheap to check now. A back-of-envelope
figure with its assumptions shown is enough at this stage — precision comes in the spike.
