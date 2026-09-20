# 7 — Viability brief

**Produces:** the viability brief supporting a **Validation Decision** — go,
no-go, or revise — and, where a commitment is proposed, a prepared package.

This is not the seventh item on a list. It is Pillar 2's primary output and the hard gate
between Build-to-Learn and Build-to-Earn. Behavior is drafted and refined during
validation, so the decision can bind an exact selected scope. This skill prepares
the evidence and package; the accountable person records approval through the
authoritative interface. Everything else in this skill feeds that decision.

Treat it accordingly. The brief is decision-grade, not ceremonial: someone reads it and
commits or declines production engineering capacity.

## Before you start

Ask what evidence exists, then say plainly what's thin. A viability brief assembled over
gaps is still worth writing — but only if the gaps are visible in it. A brief that reads
as confident when three of its four legs are assumption is the most dangerous artifact this
skill can produce, because it travels further than the person who wrote it and gets quoted
by people who never saw the evidence.

If the honest answer is *we don't know enough to decide*, that is a legitimate output.
Write **revise**, name the one or two things that would settle it, and say how long they'd
take. That is a better outcome than a manufactured go.

## The three questions

The decision must answer all three. The brief is organised around them because that is what
makes it readable by someone who wasn't in any of the sessions.

1. **Is the problem real and worth solving?** — interview guide, problem sizing
2. **Will the proposed solution actually solve it?** — prototype, demand test, eval stub
3. **Is it technically and economically feasible within acceptable constraints?** —
   feasibility spike, including data and context readiness

For each, state the answer, the evidence behind it, and your confidence. Where there is no
evidence, say so in the same voice — an empty cell is information.

## Output template

```markdown
# Viability brief — <opportunity>
## Validation Decision: **GO / NO-GO / REVISE**

<One paragraph. The decision, the single most important reason for it, and the biggest
risk being accepted by making it. Someone should be able to read only this and act
correctly. If there was a mandate, one sentence on whether it held — and if validation
exceeded it, by how much and why that was the right call.>

---

## Evidence base
<the evidence-base header from evidence-intake.md>
**Mandate cost:** none — the brief is the decision; the ledger below is the reconciliation

**Validation work completed:**
| Artifact | Done | Result | Budget used |
|---|---|---|---|
| Interview guide | <date / not run> | <finding> | <n of the interviews budgeted> |
| Problem sizing | | | <none> |
| Visual prototype | | | |
| Demand test | | | |
| Feasibility spike | | | <n days of the spike budgeted> |
| Eval stub | | | |
| **Against the mandate** | | | <used / declared, e.g. 4/5 interviews, 1/1 spike · horizon <date>: met / passed by <n> days | none declared [A]> |

<Gaps stay visible. "Not run" is a finding. So is an unused budget: say why it was not
needed, or that it still should be spent before this decision is trusted.>

---

## 1. Is the problem real and worth solving?
**Answer:** <yes / no / partly> · **Confidence:** <high / medium / low>

<What we learned, marked [E/I/A]. Size, who has it, what it costs them, what they do
today.>

**What would change this:** <...>

## 2. Will the proposed solution actually solve it?
**Answer:** <...> · **Confidence:** <...>

<Prototype results — including whether users trusted it, not just whether they completed
the task. Demand signal against its baseline. Output quality against the stub's threshold.>

**What would change this:** <...>

## 3. Is it feasible and economic within acceptable constraints?
**Answer:** <...> · **Confidence:** <...>

<Spike findings. Data and context readiness verdict. Cost to serve at the volume the
sizing implies. The break point.>

**What would change this:** <...>

---

## Gap and risk log
| # | Gap or risk | Impact if wrong | Status | Owner |
|---|---|---|---|---|
| 1 | | | Open / accepted / retired | |

<Accepted risks are the honest part of a go decision. List them, so that when one lands
later it was a known bet rather than a surprise.>

## Output quality summary
<Where the eval stub landed, on which dimensions, and how the safety cases went. If no
stub was run and the feature is model-based, say so — it is a material gap in a go.>

## Recommended MVP scope
**In:** <the smallest thing that delivers the validated value>
**Out:** <what validation showed can wait — and what evidence says so>
**Why this line:** <...>

<Scope that narrowed because of what validation taught is the clearest sign the work paid
for itself. Say what changed and why.>

## Handoff to Build-to-Earn
<When the decision is GO, this section is superseded by the **commitment package** (see the
skill's "The commitment package"): the exact selected behavior by qualified reference, bound to
an immutable revision, with exclusions and the unresolved register. Naming inputs was the right
output when specs were born after the decision; the decision now binds a selection, so the
selection has to exist for the decision to be about anything.

For a REVISE, or where behavior has not been drafted yet, name the inputs as below — that is
still the honest output when there is nothing yet to reference.>
- **Problem statement:** <one line, ready to be specified>
- **MVP scope:** as above
- **Evaluation criteria to be derived from:** <the stub's dimensions and thresholds>
- **Guardrail requirements to be derived from:** <the safety cases and boundary findings>
- **Known architecture and data constraints:** <from the spike>

## If NO-GO or REVISE
**What we learned that was worth the cost:** <...>
**What would have to be true to revisit:** <...>
**Where the evidence goes:** <so the next person doesn't redo this>

<A no-go that produces reusable learning is a successful Pillar 2, not a failed one.
Failing here is what prevents failure in the much more expensive half that follows.>
```

## Writing the decision itself

- **Lead with it.** The decision goes in the first line, not the conclusion. Readers who
  stop after a paragraph should stop with the right answer.
- **Confidence is not optional.** A go at low confidence is a real and sometimes correct
  position — but it must be labelled, because it changes how much the organisation should
  bet.
- **Name what you're accepting.** Every go accepts risk. Listing it converts a future
  surprise into a recorded bet, and it is what makes the decision defensible later.
- **Don't let scope drift in.** If validation didn't test it, it doesn't belong in the MVP
  scope. The most common way a viability brief goes wrong is quietly restoring everything
  the prototype deliberately left out.
- **Revise is a real answer.** Under-used, because it feels indecisive. It is usually the
  most accurate one: the problem is real, the solution isn't right yet, and here is the
  narrower thing worth testing next.

## After the decision

Remind the PM once:

> Record the decision and its evidence against the opportunity — with a verdict and a
> signal strength — so the discovery engine picks it up and the next person doesn't redo
> this work.

Offer to write it back to the tracker. Do it only on explicit approval.

**If there was an Exploration Decision, close its loop too.** The mandate came out of a
planning session; the next session's gap analysis reads funnel signals, and an explored
problem that never reports back looks identical to one that was never explored. So the
second destination is the decision record itself, through the same governed door Pillar 1
named. What goes there, in one entry:

```
Exploration Decision:  <ref>
Validation Decision:   go | no-go | revise · confidence <high / medium / low>
Budget used:           <used / declared> · horizon <met / passed by n days>
Evidence:              <the artifacts, by filename, attached or linked to the opportunity>
Next:                  <Pillar 3 handoff | what would have to be true to revisit>
```

Same rules as every write: prompt every time, write only on an explicit yes, and where the
skill cannot write to that door, hand the PM the exact text and the exact destination. See
`references/record-writeback.md`, "The decision record".
