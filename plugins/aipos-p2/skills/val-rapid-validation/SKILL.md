---
name: val-rapid-validation
description: "Build the validation artifacts of AIPOS Pillar 2 (Rapid Validation) — interview guide, problem sizing, visual prototype brief, demand test, feasibility spike, eval stub and brief, and the viability brief that carries the Validation Decision. Use this whenever a PM wants to test an assumption before committing engineering capacity — talking to users, sizing a problem, prototyping to learn, running a fake-door or demand test, checking technical or data feasibility, defining success criteria for a GenAI feature, or making a go / no-go / revise call. Trigger it even when the user doesn't name an artifact; phrases like 'is this worth building', 'how do we know people want this', 'size this opportunity', 'can we actually build this', 'what would prove this works', 'should we kill this', 'prep for user interviews', or 'we need to validate before we commit' all belong here. Works with or without an Aha! record — evidence is optional input, never a prerequisite."
---

# Rapid Validation

This skill helps a Product Manager produce the artifacts that retire risk *before* an
organization commits production engineering capacity.

Pillar 2's core question, from the AIPOS: **can this solution create useful, safe,
measurable value before we invest in full production buildout?** It tests the highest-risk
assumptions at the cheapest point in the lifecycle — before development, where testing an
assumption costs days instead of sprints.

## The one thing to keep straight

> "The output is not a prototype. The prototype is evidence. The output is a documented
> decision — go, no-go, or revise."

Pillar 2's primary output is the **Validation Decision**. Every artifact in this skill is
evidence feeding that decision. A PM who collects six beautiful artifacts and never makes
the call has not completed Pillar 2. Whenever you finish an artifact, point at the
decision it serves and say what is still unevidenced.

The Validation Decision must answer three questions. That is also how the menu is
organised — it is not an arbitrary list:

1. **Is the problem real and worth solving?**
2. **Will the proposed solution actually solve it?**
3. **Is it technically and economically feasible within acceptable constraints?**

## The boundary you must not cross

Pillar 2 is Build-to-**Learn**. It is deliberately ungoverned relative to delivery:

> "It does not need Gherkin acceptance criteria, non-functional requirements, or
> evaluation schemas. It needs a clear hypothesis, a defined experiment, and a decision
> criterion: what will we learn, and what will we do based on what we learn? Applying
> production governance to disposable experiments kills the speed that makes validation
> cheap."

So: **never emit Gherkin, NFRs, evaluation schemas, or build-ready specifications from
this skill.** Those belong after the Validation Decision, in Build-to-Earn — that is what
the GovKit feature-refinement work is for. If a PM asks for acceptance criteria here, say
plainly that specs are born *at* the Validation Decision, not before it, and offer the
artifact that would actually get them there.

The one exception is the **viability brief**, whose job includes naming the handoff inputs
Pillar 3 will need — problem statement, MVP scope, evaluation criteria, guardrail
requirements. Naming them is in scope. Writing them out as specifications is not.

Corollary: every artifact this skill produces carries a **hypothesis, an experiment, and a
decision rule**. If you cannot state what the PM will do differently depending on the
result, the artifact is not finished.

---

## Step 1 — Pick the artifact

Open with the menu. Most PMs know what they want; show it and let them choose.

> Which validation artifact do you want to build?
>
> **Is the problem real and worth solving?**
> 1. **Interview guide** — talk to users
> 2. **Problem sizing** — size the prize
>
> **Will the solution actually solve it?**
> 3. **Visual prototype** — prompt or build
> 4. **Demand test** — measure demand
> 6. **Eval stub & brief** — define success
>
> **Is it feasible and economic?**
> 5. **Feasibility spike** — can we build it?
>
> **Make the call**
> 7. **Viability brief** — the Validation Decision
>
> Or tell me where you are and I'll suggest one.

Keep the numbering as shown — it matches the PM's own tooling, even though the grouping
reorders it.

If the PM describes their situation instead of picking, route them:

| They say | Route to |
|---|---|
| "We have a hunch and no data" | 1 — Interview guide |
| "Leadership wants to know if it's big enough" | 2 — Problem sizing |
| "People say they want it, I'm not sure they'd use it" | 3 then 4 — prototype, then demand test |
| "We don't know if it's buildable / the data may not exist" | 5 — Feasibility spike |
| "It's a GenAI feature and 'good' is fuzzy" | 6 — Eval stub & brief |
| "We've done the work, I need to decide" | 7 — Viability brief |
| "We've spent the budget" / "the horizon has passed" | 7 — Viability brief, with what exists; *revise* is a real answer |

If they ask for an artifact whose prerequisite is missing, build what they asked for —
they own the call — but say once what is missing and why it weakens the result. A demand
test with no sized problem produces a number nobody can interpret.

## Step 2 — Take in whatever evidence exists

Read `references/evidence-intake.md` and follow it. It covers the three intake paths — an
Aha! record, material the PM pastes or attaches, or nothing at all — the **exploration
mandate** read alongside them (the Exploration Decision's owner, budget, and horizon, if
planning issued one), and the provenance convention every artifact uses.

**Evidence is optional input, never a prerequisite.** Plenty of real validation starts from
a hunch. What is not acceptable is an artifact that *looks* evidence-backed when it is not.
Mark every claim, and say in one line at the top what the evidence base actually was.

## Step 3 — Build it

Read the matching reference and follow it:

| # | Artifact | Reference |
|---|---|---|
| 1 | Interview guide | `references/interview-guide.md` |
| 2 | Problem sizing | `references/problem-sizing.md` |
| 3 | Visual prototype | `references/visual-prototype.md` |
| 4 | Demand test | `references/demand-test.md` |
| 5 | Feasibility spike | `references/feasibility-spike.md` |
| 6 | Eval stub & brief | `references/eval-stub-brief.md` |
| 7 | Viability brief | `references/viability-brief.md` |

Read only the one you need. Each reference carries its own interview steps, output
template, and quality bar.

## Step 4 — Close the loop

End every artifact the same way:

1. **Deliver the file.** These are working documents — write them out, don't just print
   them into the conversation.
2. **Say what it retires and what it doesn't.** One or two lines: which of the three
   Validation Decision questions this moves, and what remains unevidenced.
   Then one line against the mandate: what this artifact plans to consume (or consumed,
   for findings from work that has run), what has actually been used, what remains of the
   budget and horizon, and — if either is now exhausted — that the viability brief is the
   next artifact unless the PM chooses to exceed.
3. **Prompt to save it to the record.** Every artifact, every time. Read
   `references/record-writeback.md` and follow it — it covers the three pieces (attachment,
   index comment, to-do), which artifacts warrant a to-do and which do not, the naming
   convention for re-runs, and the fact that you cannot create attachments and must hand
   that step to the PM by filename.

   **Prompt every time; write only on an explicit yes.** Never write to a system of record
   unprompted, and never treat an earlier "sounds good" as standing approval for a later
   write.
4. **Name the next artifact.** Validation is a sequence, not a menu visit.

---

## How to behave throughout

These carry across every artifact. They exist because a validation artifact is only worth
the discipline behind it.

- **Ask one primary question at a time.** A wall of questions gets a wall of shallow
  answers.
- **Read first, then propose.** If evidence is on the record, never ask the PM for a fact
  that is already there. Summarise it back and ask them to correct you. Proposing beats
  interrogating.
- **Default forward.** After each step, summarise and continue unless the PM objects.
  Their silence is agreement; their correction is the point of the step.
- **Never invent evidence, personas, metrics, or quotes.** This is the rule the whole skill
  rests on. If a number would be useful and you don't have it, write `[A]` and say it is an
  assumption to be tested — never a plausible-looking figure. A fabricated baseline that
  reaches a Validation Decision is worse than no artifact at all.
- **Keep the solution out of the problem framing.** If the PM states a solution where a
  problem belongs, reframe to the user's problem and show them the reframe.
- **Refuse to pad.** If three interview questions carry the risk, write three. Length is
  not rigour.
- **Report against the mandate; never gate on it.** Every artifact states its cost in the
  Exploration Decision's own units — as a plan until the work has run, as spend once it
  has — and the header's ledger moves only on spend. An artifact whose
  decision rule cannot be reached inside the remaining budget or horizon says so and names
  the cheaper route — then builds what the PM chose. The owner holds the line, not this
  skill.

### Proceed protocol

If the PM replies *Proceed, Continue, Looks good, Approved, Yes* — treat it as confirming
your most recent summary and continue. If you offered options, they may answer with the
option name, its number, or *Default* (take your recommendation). Only stop when there is
real ambiguity.

### GenAI check

Run this silently on every artifact. If the solution involves model behaviour — generation,
retrieval, classification, reasoning, chat, agents — say once:

> This looks like a GenAI solution, so I'll add an evaluation angle: the test needs to
> check model behaviour, not just whether the user can complete the flow.

Then make sure the artifact carries it. What that means per artifact is in each reference;
the through-line is that with GenAI, **a user completing the task is not proof the system
worked** — they may have trusted a wrong answer. Design for that.

Otherwise skip it silently. Don't announce a check that found nothing.
