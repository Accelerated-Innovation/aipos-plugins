# 5 — Feasibility spike

**Retires:** *Is it technically and economically feasible within acceptable constraints?*
**Produces:** a timeboxed investigation plan, and the findings write-up when it's done.

This artifact also carries **data and context readiness**, which AIPOS names as its own
risk area under Pillar 2's Data/Source/Context governance domain. It sits here because in
practice the same investigation answers both — and because for AI products the data
question kills more ideas than the engineering question does.

## The two things that make a spike work

**A timebox.** A spike is not a project. Two to five days, with a hard stop. Without one it
becomes an unfunded prototype and the team drifts into building the thing before anyone
decided to build it.

**A question, not a topic.** "Investigate the search stack" produces a document nobody
reads. "Can we return results in under 400ms across 2M records on our current
infrastructure?" produces an answer. Every spike needs a question whose answer is yes, no,
or a number.

## Interview the PM

1. **What could make this impossible or uneconomic?** Push past the first answer — the
   first is usually the one they already know. Get to three or four candidate blockers.
2. **Which is most likely to be fatal?** Spike the one that would kill the idea, not the
   one that is most interesting to investigate.
3. **What answer would stop us?** The kill threshold, stated before the work starts.
4. **Who is running it, and for how long?** A named person and a hard stop.
5. **What does the system need to know that it doesn't already have?** This opens the
   data and context readiness section, and it is the question PMs most often haven't asked.

## Output template — the plan

```markdown
# Feasibility spike — <the question>

## Evidence base
<the evidence-base header from evidence-intake.md>
**Mandate cost:** <the timebox below, against the spike budget and the horizon | none declared>

## The question
<One question with a yes / no / numeric answer.>

## Why this one
<What makes this the fatal risk rather than merely an interesting one.> [E/I/A]

## Kill threshold — set before starting
We stop or reframe if <specific finding>. We proceed if <specific finding>.
Anything between is a **revise** signal, and here is what we'd change: <...>

## Timebox
<n> days · Owner: <name> · Hard stop: <date> · Inside the horizon: <yes | no, by <n> days>

## Method
<What will actually be done. Load real volumes of representative data. Call the actual
API against the real rate limits. Run the model on twenty real examples. Not: read the
documentation and form an impression.>

## Data & context readiness
| Question | Finding | Mark |
|---|---|---|
| What sources does this need? | | [E/I/A] |
| Do we have access today — technically and contractually? | | |
| Is the quality sufficient — completeness, accuracy, consistency? | | |
| Is there enough volume and history? | | |
| How fresh does it need to be, and how fresh is it? | | |
| Any PII, consent, residency or retention constraints? | | |
| Licensing: are we permitted to use it this way? | | |
| Who owns it, and will they say yes? | | |

<The last row is not a technical question and is the one that most often turns out to be
the blocker. Ask it.>

## Economics
- **Cost to serve at the volume the sizing implies:** <estimate and its basis> [E/I/A]
- **What dominates the cost:** <the input that moves it most>
- **At what volume does this stop making sense:** <the break point>

## Out of scope
<What the spike will deliberately not answer, so the timebox holds.>
```

## Output template — the findings

```markdown
# Spike findings — <the question>

## Answer
<Yes / No / the number.> One line, first.

## Confidence
<High / medium / low> — because <what was actually tested versus assumed>.

## What we did
<Enough that someone could repeat it.>

## What we found
<Findings, each marked. Include what surprised you.>

## Data & context readiness verdict
<Ready / ready with work / blocked> — and the specific blocker if blocked.

## What this changes
- **For the decision:** <does it move go / no-go / revise>
- **For scope:** <what the finding rules in or out of an MVP>
- **Still unknown:** <what a second spike would need to answer, if anything>
```

## GenAI angle

For a model-based feature, the spike answers different questions than a conventional one.
Cover these explicitly:

- **Does the model actually do the task on real inputs?** Twenty representative real
  examples — including the messy ones — beats any benchmark. Run them.
- **Latency at realistic context size.** Prompts grow in production. Test at the size you
  expect, not the size that's convenient.
- **Cost per call × expected volume.** Multiply it out. This is the number that most often
  makes a demo-able feature uneconomic, and it takes ten minutes to check.
- **Failure shape.** When it's wrong, is it obviously wrong or plausibly wrong? Plausibly
  wrong is far more expensive, because the cost lands on the user rather than the system.
- **Boundary behaviour.** What happens at the edges — adversarial input, empty input,
  input in another language, input designed to elicit something it shouldn't produce.
  Record what you find; the eval stub picks it up from here.
