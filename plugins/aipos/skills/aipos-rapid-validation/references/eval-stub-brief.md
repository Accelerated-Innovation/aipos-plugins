# 6 — Eval stub & brief

**Retires:** *Will the solution actually solve it?* — the output-quality and safety half.
**Produces:** a definition of "good" and a small starter set of examples that test it.

For a GenAI feature, "does it work" has no obvious answer. The same output can be excellent
for one user and useless for another; the system can be right about the facts and wrong
about the job. Until someone writes down what good means, every review is an argument about
taste, and the team ships on whoever is most senior in the room.

## What this is and isn't

This is a **stub** — deliberately small, deliberately disposable. Its job is to produce
enough of a shared definition of quality to inform the Validation Decision.

Production evaluation schemas belong to `aipos-feature-create` and are reviewed
with `aipos-feature-refine`; they may develop during Pillar 2 as commitment scope
becomes concrete. This experimental stub remains smaller. If you find yourself writing schema
definitions, scoring rubrics with weighted sub-criteria, or CI-ready assertions, you have
crossed the line — stop and cut back. The stub's value is that it can be written in an
afternoon and thrown away if the idea dies.

What survives into Pillar 3 is the *thinking*: the dimensions that mattered, the failure
modes found, the thresholds argued over. Those become inputs to the real evaluation
criteria later.

## Interview the PM

1. **What does a great output look like — and a merely acceptable one?** Ask for a real
   example of each if they have one. This is the fastest route to the dimensions.
2. **What would make an output unacceptable?** Separate *wrong* from *harmful*. They need
   different treatment and different thresholds.
3. **Who judges?** A domain expert, the PM, the end user, a model. Say who, because "we'll
   know it when we see it" doesn't survive the first disagreement.
4. **What's the worst realistic failure?** This seeds the safety and boundary cases.
5. **Where does it have to be right, and where is a near-miss fine?** Not all output
   carries equal cost. Say where the bar is high.

## Output template

```markdown
# Eval stub & brief — <capability>

## Evidence base
<the evidence-base header from evidence-intake.md>
**Mandate cost:** <starter-set construction effort, if any — otherwise "none">

## What "good" means
<2–3 sentences in plain language. If a new team member read only this, would they
recognise a good output?>

## Quality dimensions
| Dimension | What it means here | How judged | Bar |
|---|---|---|---|
| <e.g. Factual accuracy> | <specific to this domain> | <human / model / rule> | <threshold> |
| <e.g. Relevance to the job> | | | |
| <e.g. Tone and register> | | | |
| <e.g. Legibility of reasoning> | | | |

<Three to five dimensions. More than five and nobody applies them consistently.>

## Failure modes we expect
| Failure | Why it happens | Cost when it does | Detectable? |
|---|---|---|---|
| Plausible but wrong | | | |
| Confidently wrong on an edge case | | | |
| <domain-specific failure> | | | |

<"Plausible but wrong" belongs on nearly every list. It is the failure that costs most,
because the cost lands on the user rather than the system.>

## Safety and boundary cases
| Input | Expected behaviour | Unacceptable behaviour |
|---|---|---|
| <adversarial / out-of-scope request> | <refuses, redirects, escalates> | |
| <empty or malformed input> | | |
| <request touching sensitive data> | | |

## Starter example set
<15–25 real inputs with expected outputs. Composition matters more than count:>
- **<n> typical cases** — the everyday bulk
- **<n> hard cases** — right answer requires care
- **<n> edge cases** — sparse input, unusual format, boundary of scope
- **<n> should-refuse cases** — the system should decline or escalate

<Use real inputs. Synthetic examples are systematically easier than reality and produce
a system that passes its own eval and fails its users.>

## Threshold for the Validation Decision
We consider output quality validated if <n>% of the starter set passes on <dimensions>,
with **zero** failures on the safety cases. Below <n>% we <revise / stop>.

<Safety cases are pass/fail, not a percentage. Say so.>

## What this doesn't cover
<Scale, drift over time, adversarial pressure at volume, long-tail inputs. Name it — a
stub that pretends to be comprehensive is worse than one that admits its edges.>
```

## Building the starter set

The examples are the artifact. The prose around them is scaffolding.

- **Pull from reality.** Support tickets, real documents, actual user queries. If evidence
  came in from Path A or B, mine it — the inputs are usually already there.
- **Include the ones you're afraid of.** The tempting move is a set the system passes.
  A set that only passes tells you nothing you didn't already believe.
- **Write the expected output, not just a label.** "Good" is not a target. What the answer
  should actually say is.
- **Keep it small enough to run by hand.** If a human can't grade the whole set in an hour,
  it will be graded once and never again.

## Quality bar

- A new team member could apply the dimensions and reach roughly the same verdict as you.
- Every dimension has a threshold, not just a name.
- The safety cases are pass/fail and treated as such.
- Nothing in the document is a schema, a rubric with weights, or a CI assertion.
- The threshold connects to a decision — what happens at 60% is written down.
