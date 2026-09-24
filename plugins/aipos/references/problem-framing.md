# Problem Framing

> The discipline this whole skill exists to enforce. Everything downstream inherits this section — features, scenarios, and eventually code.
>
> **Shared** by `aipos-epic-create` (epics) and `aipos-solution-design` (the Solution Design canvas). The canvas applies it with the exceptions its `panel-rubrics.md` names — chiefly that facts come from the Product Definition Graph, never from the PM.

> `aipos-product-strategy` also reuses this guidance with the adaptations in its
> `SKILL.md`: an initial hypothesis can retain unknowns, segment choices can evolve,
> and a single initial outcome is sufficient. Epic and canvas contracts are unchanged.

## Contents

- [The solution-in-problem test](#the-solution-in-problem-test)
- [Reframing scripts](#reframing-scripts)
- [Root cause probing](#root-cause-probing)
- [Impacted personas](#impacted-personas)
- [Quantifying impact](#quantifying-impact)
- [Benefits of solving](#benefits-of-solving)
- [The final problem statement](#the-final-problem-statement)
- [Evidence quality](#evidence-quality)

## The solution-in-problem test

Most epics arrive as solutions. "We need an AI assistant for adjusters" is a solution; the problem it implies has never been stated, so nobody ever checks whether the solution addresses it.

Apply this test to every stated problem:

> **Could this sentence be false while the underlying difficulty is still real?**

If the answer is yes, it is a solution. "We don't have a routing engine" can be false — you could build one and adjusters could still miss SLAs — so it is a solution. "High-value claims sit unassigned for days because nobody owns the routing decision" cannot be false while the difficulty persists.

Faster signals, when you need one:

| Signal | Example | Why it's a solution |
|---|---|---|
| Names a system that doesn't exist yet | "There's no dashboard" | Absence of a solution is not a problem |
| Contains a technology | "We need RAG over the claims corpus" | Names the mechanism, not the difficulty |
| Starts with "we need" or "we should" | "We should automate triage" | States a desire, not a condition |
| Has no sufferer | "The data model is fragmented" | Nobody in the sentence is struggling |
| Is only fixable one way | "Users can't bulk-export" | The verb *is* the feature |

The last one is subtle and worth care. "Users can't bulk-export" sounds like a problem but smuggles in the answer. The real problem is underneath: *what are they doing that requires exporting 400 records one at a time, and what does it cost them?* Sometimes the answer is still bulk export. Often it is something else entirely, and the epic that asked the question finds it.

## Reframing scripts

When a solution appears, do not reject it — mine it. The PM's solution encodes real knowledge about the problem; the job is to recover the problem, not to win a framing argument.

**Primary script:**

> Let's reframe that as a user problem. Who's struggling, and what's difficult or slow for them right now?

**When the PM insists the solution is the problem:**

> Fair — let's say we build exactly that. Who notices, and what stops being painful for them? That's the problem statement, and it'll make the epic much easier to justify.

**When the solution is genuinely already decided** (an executive commitment, a compliance mandate, a contract):

> Understood, that's decided. I'll record it in Initial Scope where decisions belong. For the problem statement I still need the difficulty underneath it, so the features we derive solve the right thing.

That third case matters. Sometimes the solution really is fixed, and pretending otherwise wastes the PM's time. The move is to relocate it — solutions live in **Initial Scope / MVP**, never in **User Problem(s)** — not to litigate it.

Push at most twice. If the PM holds firm after two attempts, record their framing, note the concern in one line in Open Questions, and move on. This skill coaches; it does not block.

## Root cause probing

Once you have a problem, check whether it is the real one. Ask "and why is that?" until the answer stops changing — usually two or three hops, not five.

> "Adjusters take too long to triage."
> → *Why?* "They open every claim to find out if it's urgent."
> → *Why?* "There's no ordering signal in the shared inbox."
> → **Root:** the queue has no priority signal, so triage is manual and inconsistent.

Stop when the next "why" leaves the epic's control ("because insurance is regulated") or when the answer starts naming solutions. Both mean you've arrived.

Beware of stopping too early: the first answer is almost always a symptom, and an epic scoped to a symptom produces features that treat symptoms.

## Impacted personas

**If the workspace has personas**, list them with a one-line summary each and ask which apply:

> This workspace has defined personas. Which of these experience the problem?

**If none fit**, capture the new group descriptively — role, what they're trying to do, how the problem reaches them. **Do not create a persona record.** Persona creation is a separate governance act with its own owner; describing a group in an epic is not.

Rules:

- Name a **role**, never "users". If the honest answer is that it affects everyone, name the two or three roles it affects *most* — an epic that helps everyone equally usually helps nobody measurably.
- Mark one **primary** persona. Downstream features anchor their user stories to it, and an epic with three co-equal primaries produces features that serve none of them well.
- Distinguish who **suffers** from who **acts**. A compliance analyst may suffer from missing audit trails while the adjuster is the one who would create them. Both belong; conflating them produces features aimed at the wrong person.
- **Lock personas once confirmed.** They are inherited by `aipos-feature-create` and every feature under this epic. Changing them later invalidates downstream work, so confirm deliberately.

## Quantifying impact

> What measurable impact does this problem have — time, cost, errors, risk, satisfaction?

Walk those five categories when the PM stalls. For each, push once toward a number:

| PM says | Ask |
|---|---|
| "It takes forever" | Roughly how long, and how often? |
| "It's expensive" | What's the cost driver — people's time, rework, penalties? |
| "It's error-prone" | How often does it go wrong, and what happens when it does? |
| "It's a compliance risk" | What's the exposure if it's found — fine, finding, remediation? |
| "Users hate it" | How does that show up — churn, support volume, a survey score? |

Then mark provenance honestly, using the same marks Pillar 2's artifacts use — so a viability brief's provenance survives into the epic without translation:

- **`[E]` evidence-backed / measured** — from a system, a study, or a report. Name the source and its date.
- **`[I]` inferred / estimated** — the PM's informed judgment or a derivation from measured inputs. Say whose, and from what.
- **`[A]` assumption / unknown** — nobody knows. Record it as a gap and an assumption to test.

**Never convert an `[I]` or `[A]` into an `[E]` by writing it without qualification.** An unqualified "22 minutes per claim" in an epic becomes a fact in a business case within a month, and nobody can trace where it came from.

If a claimed impact has no evidence in Step 5, it stays an assumption. Do not soften it into fact for symmetry.

## Benefits of solving

> If we solve this, what positive outcomes do you expect?

The common failure is a benefit that restates the solution: "adjusters will have a prioritized queue" is the feature, not the benefit. Push once:

> And what does that let them do that they can't do today?

Good benefits mirror the quantified impact — if the problem costs 22 minutes per claim, the benefit is measured in minutes recovered. That symmetry is what makes Step 4's success metrics almost write themselves, and a benefit that maps to no stated impact usually means an impact went uncaptured.

## The final problem statement

One structure, assembled from the four preceding tasks:

> The problem of **[X]** affects **[Y]**, resulting in **[Z]**, and solving it will lead to **[benefits]**.

Worked example:

> The problem of **claims arriving with no priority signal** affects **regional adjusters and their supervisors**, resulting in **manual triage of every claim, a 9.5-hour median time to first action, and six SLA breaches last year on claims over $250k**, and solving it will lead to **adjusters acting on the right claim first, first-action time under two hours, and no SLA breaches on high-value claims**.

Before accepting it, check all four:

1. **[X] is a problem**, not a missing solution — re-run the solution-in-problem test on the final wording, since solutions creep back in during assembly.
2. **[Y] is a named role**, not "users".
3. **[Z] is a consequence with a number**, or an explicitly marked assumption.
4. **[benefits] are outcomes**, not features.

**Do not proceed past this step while a structural problem remains.** Everything downstream inherits it: features, scenarios, and eventually code. Ten more minutes here saves a quarter.

## Evidence quality

Evidence answers one question: *how do we know this problem is real?* Sort it into two buckets.

**Qualitative** — interviews, shadowing sessions, support ticket themes, sales or CS anecdotes, compliance findings. Record: who, how many, when, and what they actually said. "Users complained" is not evidence; "four supervisor interviews in March, all four independently described the shared inbox as the bottleneck" is.

**Quantitative** — analytics, incident counts, cycle times, error rates, financials. Record: the source system, the period covered, and the measure. A number with no period is unusable — "14 SLA breaches" over what, a month or a decade?

Three rules:

- **Date everything.** Evidence ages. An eighteen-month-old analytics snapshot describes a system that may no longer exist, and the date is what lets a reader judge it.
- **Say what each source establishes, and what it doesn't.** A shadowing study of 8 adjusters in one region is strong evidence about that region and weak evidence about the other four. Naming the limit is what makes the strong part usable.
- **Absent evidence is a finding.** If the biggest claimed impact has nothing behind it, that belongs in Open Questions, and it is often the most valuable line in the epic — it tells the team what to go measure first.

Anti-evidence to push back on once: "everyone knows", "it's obvious", a single loud customer generalized to a segment, and a competitor's feature list. None of these establish that *your* users have *this* problem.
