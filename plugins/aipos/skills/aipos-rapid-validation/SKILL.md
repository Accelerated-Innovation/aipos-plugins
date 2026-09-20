---
name: aipos-rapid-validation
description: "Design experiments and synthesize evidence to decide whether an opportunity merits investment. Use for interviews, problem sizing, prototypes, demand tests, feasibility, experimental AI evaluations, viability briefs, and commitment-package preparation. Delegate production behavior authoring to feature-create."
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

An explicit request for an epic or program brief belongs to `aipos-epic-create`;
new production Rules and acceptance criteria belong to `aipos-feature-create`.
Use this skill for the experiment and evidence decision, even when the user calls
its experimental pass/fail criteria "acceptance criteria." Distinguish by purpose.

The Validation Decision must answer three questions. That is also how the menu is
organised — it is not an arbitrary list:

1. **Is the problem real and worth solving?**
2. **Will the proposed solution actually solve it?**
3. **Is it technically and economically feasible within acceptable constraints?**

## The boundary, and where it now ends

Pillar 2 is Build-to-**Learn**, and most of it is deliberately ungoverned relative to delivery:

> "It does not need Gherkin acceptance criteria, non-functional requirements, or
> evaluation schemas. It needs a clear hypothesis, a defined experiment, and a decision
> criterion: what will we learn, and what will we do based on what we learn? Applying
> production governance to disposable experiments kills the speed that makes validation
> cheap."

That holds for **experiments**. An interview guide, a fake-door test, a spike that may be thrown
away next week needs no production contract to run, and imposing one destroys the speed that
makes validation worth doing. So the artifacts in Step 1 stay light, and this skill still writes
no Gherkin, NFRs or evaluation schemas *for them*.

**It does not hold at the exit.** The Pillar 2 exit is a hard, versioned commitment, and what it
binds is an exact selection of Rules and scenarios. Drafting them afterwards would leave the
decision binding nothing. So behavior is drafted progressively as validation narrows — by
`aipos-feature-create` in opportunity mode, refined by `aipos-feature-refine` — and this skill
assembles the result into the **commitment package** the decision is made against.

The old rule "specs are born *at* the Validation Decision, not before it" is retired. Specs are
born *during* Pillar 2 and are what the decision is *about*. If a PM asks for acceptance
criteria, do not refuse the need: say this skill does not author them, name the skill that does,
and carry what exists into the package.

**Progressive, not front-loaded.** Early on, a rough hypothesis is enough. As the evidence
narrows toward a commitment, the behavior sharpens. Demanding a production-ready contract before
the first interview is the failure this boundary was written to prevent, and it stays prevented.

Corollary: every artifact this skill produces carries a **hypothesis, an experiment, and a
decision rule**. If you cannot state what the PM will do differently depending on the
result, the artifact is not finished.

---

## Step 1 — Pick the artifact

If the PM named an artifact, select it and proceed. Otherwise open with the menu; do not ask them to repeat a choice already supplied.

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
Preserve a source's own uncertainty: a lead's estimate remains `[I]` or `[A]`,
even when it appears in a document containing observed `[E]` facts. Keep those
labels beside the values wherever reused in a table, hypothesis, or conclusion.
Ask only for unanswered facts; evidence and mandate questions already answered
in the request do not need another round. With neither, explain once that the
interviews and problem sizing will establish the evidence; a finished guide
alone does not establish that the problem is real.

Keep study-design proposals separate from source facts and adopted decisions.
A proposed sample, date, or pass criterion carries `[A]`, an explicit proposal
label, and the decision still needed before the study runs. Unknown inputs may
stay blank. Never backfill a plausible number to complete the template, nor
present a suggested criterion as the team's agreed threshold.

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

1. **Deliver the artifact in the requested form.** Write a working file when that
   is authorized and file tools exist. If the PM requests an inline draft, deliver
   it there. Without tools, give the complete content and proposed filename;
   never claim it was saved.
2. **Say what it retires and what it doesn't.** One or two lines: which of the three
   Validation Decision questions this moves, and what remains unevidenced.
   Then one line against the mandate: what this artifact plans to consume (or consumed,
   for findings from work that has run), what has actually been used, what remains of the
   budget and horizon, and — if either is now exhausted — that the viability brief is the
   next artifact unless the PM chooses to exceed.
3. **Identify the record destination and save status.** Read
   `references/record-writeback.md` and follow it — it covers the three pieces (attachment,
   index comment, to-do), which artifacts warrant a to-do and which do not, the naming
   convention for re-runs, and the fact that you cannot create attachments and must hand
   that step to the PM by filename.

   If the PM already declined saving, acknowledge that choice and identify the
   future destination without asking again. Otherwise offer the concrete save
   once. Write only within explicit authorization for that artifact and destination;
   do not treat approval of its content as approval of a system-of-record write.
4. **Name the next artifact.** For a GO recommendation with existing behavior, include the
   **commitment package** in the viability handoff using `references/viability-brief.md`.
   With no selected behavior or immutable revision, explicitly mark the handoff incomplete
   and not ready for commitment, and route to authoring/refinement first. The recommendation
   never substitutes for the human decision.

   **When the evidence is strong enough that a commitment is in view — before the Validation
   Decision, not after it — the next artifact is the behavior itself.** Say so and hand off:

   > The evidence supports committing. Before that decision there has to be something to commit
   > *to*: `aipos-feature-create` in opportunity mode drafts the Rules and scenarios from this
   > evidence — no epic, no user stories, no estimate — and leaves what we still don't know
   > marked as unknown. `aipos-feature-refine` then works them over. The decision commits that
   > selection.

   The ordering is the point and it is easy to get backwards. The Pillar 2 exit **is** the hard
   commitment, and what it binds is a versioned selection of Rules and scenarios. Drafting them
   after the decision would leave the decision binding nothing and the draft unreviewed — so
   behavior is defined and refined *before* the exit, and the viability brief's go/no-go is made
   against a known scope rather than an intention.

   A **no-go** or **revise** needs none of this. There is nothing to commit, so there is nothing
   to define; name the next validation artifact instead.

   Naming the handoff is in scope here; doing the drafting is not, and this skill still writes no
   Gherkin itself.

---

## The commitment package

When the evidence supports committing, the last artifact of Pillar 2 is the package the decision
is made **against**: the exact proposed commitment, assembled from what validation produced.

Assemble it; do not re-derive it. The Rules and scenarios already exist — reference them.

### What it carries

**Selected behavior, by qualified reference.** Every selected Rule and scenario as
`<source-key>/<feature-key>#rule:<slug>` or `#scenario:<slug>`. **Not bare `@rule:` tags** — a
slug is unique only within its own file, so two features can carry the same one and an
unqualified reference cannot say which is meant. Not a category, not prose: "the approval
scenarios" is not a commitment, it is a description of one.

**The immutable source revision** the selection resolves against — a commit SHA, never a branch
name. A commitment bound to a moving pointer can change without anyone deciding to change it.

**The opportunity and evidence, by reference.** Copy the supplied opportunity,
decision-thread and evidence identifiers exactly; do not add a prefix, normalize a
namespace or infer a different record key. Reference them; do not restate the business case. A copied business case is a second
editable copy that drifts from the first, invisibly, because both look authoritative.

**Exclusions, each with a reason.** Behavior considered and not committed. An exclusion with a
reason is what distinguishes "we decided against it" from "nobody thought of it" six months
later. Silence is not an exclusion.

**Contradicting evidence, carried as contradicting.** Do not drop it, argue it away, or resolve
it. Whether the evidence is adequate is the accountable human's judgement, and a package that
keeps only supporting evidence is a sales deck.

**Unverified claims, marked unverified.** A remark in a readout is not a requirement. Attribute
it and say it is unchecked; do not promote it to an NFR because it sounded official.

### The unresolved register, and what blocks

Every open question, each marked **blocking** or **not blocking**, with the reason:

| | |
|---|---|
| **Blocking** | It could change included behavior, an expected outcome, or a constraint. An undecided threshold that a selected scenario depends on blocks — the scenario cannot be verified without it. |
| **Not blocking** | It is an internal implementation choice inside declared discretion. Which store backs the audit record does not change what was committed. |

Say which each is and why. "There are open questions" is not the finding; *which ones would
change the commitment* is.

When asked whether the package is ready to commit, answer that question directly.
If blocking items remain, say **not ready for commitment**, even when the package
has been assembled and labelled prepared. That is an assessment of the recorded
gaps, not an approval decision. Do not replace it with “that call isn't mine”;
the accountable person's authority does not remove the need to report blockers.

**Never invent a value to clear the register.** Not a threshold, not a date, not a session count
— and not a number lifted from a prototype, which was chosen to make a demo work, not to be the
policy.

### The three states, and which one this is

| State | What it means | Who |
|---|---|---|
| **Prepared** | The package exists and is internally consistent | This skill |
| **Awaiting decision** | It is in front of an accountable person | Them |
| **Approved** | A decision was recorded through an authenticated interface, binding this exact package | Them, elsewhere |

**This skill produces the first and never the third.** It cannot approve a commitment, and
assembling a package is not committing to one. Say so plainly when asked — including when the
question assumes otherwise, which is the moment it matters.

Label the output **prepared**. Do not also call it **awaiting decision** unless its
placement before the accountable person is established. Explain subsequent states
conditionally: submission would make it awaiting decision; a recorded authenticated
decision would make it approved. No badge, status line or summary may read as approval. Where the
authoritative decision service is unavailable, that is a limitation to report, never grounds for
treating the package as approved in the meantime. Pillar 3 is blocked on the decision, not on
the package being finished.

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
