# GovKit Gherkin Authoring Standard

> **Shared reference.** One copy, read by `aipos-feature-create`, `aipos-feature-refine`,
> `aipos-feature-readiness`, `aipos-feature-slice` and `aipos-map-render`. From a skill
> folder the path is `../../references/gherkin-authoring-standard.md`; under an installed
> plugin it is also `${CLAUDE_PLUGIN_ROOT}/references/gherkin-authoring-standard.md`.
> Skill-local references govern their own subjects — tags in
> `aipos-feature-create/references/gherkin-tagging.md`, scoring in
> `aipos-feature-refine/references/gherkin-quality-rubric.md`, the repo gate in
> `aipos-feature-readiness/references/govkit-readiness-rubric.md`. They cite this file;
> they do not restate it. Where they disagree with it, this file is the authoring rule and
> the rubric is the scoring rule.

## Contents

- [What this standard is for](#what-this-standard-is-for)
- [BRIEF](#brief)
- [Rules are explicit in GovKit](#rules-are-explicit-in-govkit)
- [What a scenario has to do](#what-a-scenario-has-to-do)
- [Choosing coverage](#choosing-coverage)
- [Three registers: confirmed, proposed, unresolved](#three-registers-confirmed-proposed-unresolved)
- [Writing for automation without writing the automation](#writing-for-automation-without-writing-the-automation)
- [Backgrounds](#backgrounds)
- [Scenario Outlines](#scenario-outlines)
- [Public contracts: API and UI features](#public-contracts-api-and-ui-features)
- [Placeholders and readiness](#placeholders-and-readiness)
- [Deterministic checks and aggregate evaluations](#deterministic-checks-and-aggregate-evaluations)
- [Worked example: a threshold, all three sides](#worked-example-a-threshold-all-three-sides)

## What this standard is for

A GovKit feature specification has two audiences that usually get one document each. The
business audience needs to read it and say "yes, that is our policy". The delivery
audience — engineers and coding agents — needs to turn it into working software and
evidence without guessing what the business meant.

The standard exists so one document serves both. Everything below is in service of that:
readable enough to be argued with in a refinement session, precise enough that automation
built from it verifies the thing the business actually asked for.

It is not a style guide for its own sake. Where a rule here would make a specification
less clear to either audience, the rule is wrong for that case — say so and note why.

## BRIEF

Six properties worth checking before a scenario leaves your hands. They are the shape of
a scenario that survives contact with both audiences.

**Business language.** Words the business already uses, and the same word for the same
thing every time. If a reviewer has to translate a step before agreeing with it, the step
is written in the wrong vocabulary.

**Real domain data.** Concrete, plausible values from the actual domain — `INV-2210`,
`$12,500`, `"Pending manager approval"` — not `foo`, `X`, or "a valid invoice". Concrete
data is what makes disagreement possible; nobody argues with an abstraction.

**Intention-revealing.** Every line says *what* is meant to happen and why it matters,
never *how* the system pulls it off. A different implementation that still satisfies the
business rule must still satisfy the scenario.

**Essential detail only.** Every value present should affect the behavior being specified.
A customer's middle name in a scenario about credit limits invites the reader to wonder
whether the middle name matters. Move it into the automation's fixtures.

**Focused behavior.** One behavior per scenario, normally one meaningful triggering
action. A scenario that proves three things fails as one thing and tells you little.

**Brief.** Short enough to hold in your head. Three to six steps is typical and a useful
smell test — but it is guidance, not a gate. A scenario that genuinely needs seven steps to
state one behavior is fine; a four-step scenario that hides two behaviors is not. Never
reject a specification on step count alone, and never pad one to reach a number.

## Rules are explicit in GovKit

Standard Gherkin makes `Rule:` optional. A file of ungrouped scenarios is valid Gherkin
and every Cucumber-family runner will execute it happily.

**GovKit's convention is that rules are explicit anyway**, with each scenario sitting under
the `Rule:` it illustrates. This is a deliberate choice, not a syntax requirement, and it
earns its keep: the business rule is the unit the rest of the toolchain organizes on — the
rule-coverage dimension in refinement, Example Mapping's Rules cards, `rule_link` in
`eval_criteria.yaml`, the readiness gate's structure check, and the cards in the feature
map. A rule that exists only in a reviewer's head cannot be checked for coverage.

### Legacy specifications

When you meet Gherkin that has no `Rule:` blocks, separate two very different situations
before doing anything:

**Missing grouping.** The business decisions are all there — visible in the scenarios, in
the description, or in the team's answers — but nobody wrote `Rule:` lines. This is a
formatting gap. Propose the grouping, in the team's own words, and show which scenarios
land under which rule so they can correct it.

**Missing decision.** A scenario asserts something no stated policy explains, and nobody
can say where the policy came from. This is a product gap, and it is the more valuable
finding. Surface it as an open question naming the scenario and what it appears to assume.

**Never invent a policy to satisfy a formatting convention.** A `Rule:` line you wrote
because the file looked untidy will be read downstream as a business decision somebody
made. If the decision does not exist, the correct output is a question, not a heading.

## What a scenario has to do

Three things, every time:

1. **Illustrate a stated rule.** The scenario is an example of a policy, not a free-standing
   assertion. A scenario that illustrates no stated rule is a missing rule to surface.
2. **Establish a meaningful context and a trigger.** `Given` sets the state that makes this
   example different from its neighbours; `When` is the one thing that happens. If the
   `Given` is identical to every other scenario's, the scenario is not illustrating a
   distinct case.
3. **Assert observable outcomes.** Something checkable from outside the system: a status a
   user sees, a response a caller receives, a record in an audit log, an event published, a
   notification sent. "Then the record is saved" is not observable. "Then the invoice status
   is `Pending manager approval` and the assigned finance manager receives an approval task"
   is. Several related outcomes of one trigger are fine and often better than one.

## Choosing coverage

For each rule, think through — and then decide, explicitly:

- **Boundaries.** Any rule with a threshold, a limit, a window or a count has a boundary,
  and the boundary is where the business disagrees with itself. "At or above $10,000" needs
  $10,000 itself, not only comfortably-above and comfortably-below. See the
  [worked example](#worked-example-a-threshold-all-three-sides).
- **Negative paths.** Invalid input, missing data, duplicate submission, expired state,
  the dependency being unavailable.
- **Permissions.** Who may do this, and what happens to someone who may not.
- **Exceptions.** The documented carve-outs from the rule — and whether the team has
  actually decided them.

Then stop. The goal is the set of examples that makes the rule unambiguous, not every
combination of every input. A dozen near-identical scenarios drives readers away from the
document, which costs more understanding than the extra cases buy. Combinations that
matter belong in an Outline; combinations that do not matter belong nowhere.

Deferring a case deliberately is a legitimate outcome, and better than an unexamined gap.
Record it in the feature's out-of-scope section where it can carry a reason.

## Three registers: confirmed, proposed, unresolved

Every statement in a specification is in exactly one of three registers, and conflating
them is how invented policy becomes committed policy.

| Register | What it is | How it appears |
|---|---|---|
| **Confirmed requirement** | A decision the business has actually made | Plain text — a `Rule:`, a threshold, a status name |
| **Proposed illustrative data** | An example an agent derived to illustrate a confirmed rule | Plain text, flagged in the summary as a proposed example for confirmation |
| **Unresolved product decision** | Something nobody has decided yet | A visible placeholder plus an open question, never a value |

An agent may **derive examples from confirmed rules**. Given "invoices at or above $10,000
require manager approval", proposing $9,999.99 / $10,000.00 / $12,500 as the illustrating
examples is exactly the right move: the rule is the team's, the arithmetic is not a
decision. Say that the values are proposed, and let the team correct them.

An agent may **never invent**:

- a policy or business rule nobody stated,
- a threshold, limit, score, percentage, or timeout,
- a permission model,
- an approval, a sign-off, or a stakeholder's agreement.

The failure mode is specific and worth naming: a plausible number, written once in a draft,
is treated as a commitment by everyone downstream because nobody can tell it apart from the
numbers the business chose. Leave the gap visible instead — a gap the gate can see beats a
number nobody can trust.

## Writing for automation without writing the automation

The point of these rules is that automation built from the specification verifies the
business rule. None of them turn Gherkin into implementation instructions; every one of
them is about the specification staying honest.

**One behavior per scenario.** Normally one meaningful triggering action. Multiple related
outcomes of that action are fine — an approval that also notifies and also writes an audit
record is one behavior with three observable consequences.

**Independently executable.** Each scenario must pass on its own, in any order, run alone.
A scenario that says "Given the invoice from the previous scenario" is not a specification,
it is step three of a manual script. Put the state it needs into its own `Given`. This is
what lets a suite run in parallel, and what lets a failure be diagnosed.

**Consistent domain vocabulary, reused step language.** Before writing a new step, look for
one that already says this. Reusing existing step language means reusing the step
definition behind it; inventing a synonym means a second definition that will drift from
the first. Same word, same concept, every feature file in the repository.

**Concrete values wherever they affect behavior.** Include units (`45 seconds`, `$10,000`,
`14 documents`), roles (`finance manager`, not `the user`), states (`Pending manager
approval`), and the actual values a rule turns on. A value that changes the outcome must
appear; a value that does not must not.

**Incidental fixture detail lives in support code.** The customer's address, the seed data,
the account that had to exist first — if it does not affect this behavior, the automation's
fixtures own it. `Given a finance analyst has submitted an invoice for $12,500` implies
whatever setup that takes; the scenario should not enumerate it.

**Correctly scoped backgrounds.** See [Backgrounds](#backgrounds).

**Outlines for real data variation.** See [Scenario Outlines](#scenario-outlines).

**No internal design.** No endpoints, selectors, table names, queue names, class names, or
click mechanics — unless the feature *is* that contract; see the next section.

## Backgrounds

`Background:` states setup shared by **every** scenario in its scope. Gherkin gives you two
scopes and GovKit uses both:

- A `Background:` before the first `Rule:` applies to every scenario in the feature.
- A `Background:` inside a `Rule:` applies only to that rule's scenarios, and runs after
  the feature-level one.

A feature-level `Background` that is only true for some scenarios is a defect, not an
inconvenience: it silently adds state to the scenarios it does not belong to, and those
scenarios then pass for the wrong reason. If setup is shared by one rule's scenarios, put
it in that rule's `Background`. If it is shared by three of five scenarios spread across
rules, put it in the three `Given` steps and accept the repetition.

Keep backgrounds short and free of assertions. A `Background` that ends in a `Then` is
testing something, and whatever it tests deserves its own scenario.

## Scenario Outlines

Use `Scenario Outline` when **the same behavior** is exercised across **meaningful data
variation** — a threshold's two sides plus the boundary, a set of statuses that route
differently, the currencies a rule treats alike.

Do not use it to compress unrelated cases into a table because a table looks tidy. If two
rows would need different `Then` wording to be honest, they are different behaviors and
belong in different scenarios.

Every `Examples` row must be a case somebody chose. Rows generated to fill out a grid are
noise that costs execution time and reader attention.

The distinction between an **authored** outline and its **expanded executable examples**
matters and GovKit preserves it: one outline with four rows is one scenario a person
reviews and four cases a runner executes. Counting it either way is defensible; conflating
the two is not.

## Public contracts: API and UI features

Implementation-neutral does not mean contract-free. When the feature *is* the interface,
the interface details are the business behavior:

- **API features.** The resource, the operation, the status code, and the fields a
  consumer depends on are the contract — a caller integrates against them. Keep them.
  Internal handler names, query plans and table columns are not, and go.
- **UI features.** When the specified behavior is genuinely about the interface — a field
  becomes available, an error appears next to the input that caused it, a control is
  disabled for a role — say so in user-facing terms. `When the analyst submits the
  expense claim` is behavior. `When the user clicks #submit-btn` is a selector, and it
  will outlive neither the redesign nor the framework.

The test is whether a reasonable reimplementation would still satisfy the scenario. A
different HTTP status breaks a caller, so it belongs. A different CSS class breaks nothing,
so it does not.

## Placeholders and readiness

Drafts legitimately contain unknowns, and hiding them is worse than carrying them. Keep an
unresolved decision visible in the text where a reader will trip over it:

```gherkin
    Then the escalation is retried after <TBD — retry window not yet decided>
```

and list it as an open question.

**A scenario carrying a placeholder is not ready for execution**, and nothing downstream
may present it as ready. It stays in the draft, it appears in the review, it counts against
the gate, and it must not be tagged, planned or reported as an automatable case until the
decision lands. The placeholder is the point: it is a decision waiting for an owner, not a
formatting problem to tidy away.

## Deterministic checks and aggregate evaluations

Two different things get called "acceptance", and mixing them in one scenario produces a
check that can neither pass nor fail honestly.

**A deterministic behavior check** asserts what happens on one occasion, given one input.
Same input, same result, every run. Most scenarios are these.

**An aggregate evaluation** asserts a statistic over a dataset — accuracy, groundedness,
refusal rate, retrieval precision. It says nothing about any single case, and no single
case proves or disproves it.

Never assert both in one scenario. "The summary is labelled AI-generated" is deterministic;
"groundedness is at least 0.95 across the evaluation set" is aggregate; a scenario that
asserts both is unfalsifiable, because one run cannot decide it.

An aggregate evaluation is only a specification when it names all five of:

| | |
|---|---|
| **Dataset** | Which set, how many cases, where it lives, how it is versioned |
| **Method** | What is computed and how — the scorer, judge, or metric, named |
| **Threshold** | The pass/fail number, from the team, never invented |
| **Execution context** | Where it runs and what it gates — nightly, PR, pre-release |
| **Evidence** | The artifact that appears in the PR or release review, and its owner |

Missing any of the five, it is an intention, not a gate. Record it as a gap.

### Using an AI coding agent does not make a feature GenAI

This confusion is common and expensive. **GenAI evaluation requirements attach to
model-generated behavior in the running product** — the product summarizes, classifies,
retrieves, ranks, decides, or converses at runtime.

A feature is ordinary software, needing ordinary test evidence, when a model was merely
used to *build* it. Invoice routing whose code was written by a coding agent is invoice
routing: deterministic rules, deterministic tests, no evaluation dataset. Demanding
groundedness metrics for it is a false gate that teaches teams to ignore real ones.

The question is always *what does the shipped product do at runtime*, never *what wrote
the code*.

## Worked example: a threshold, all three sides

The confirmed policy: **invoices at or above $10,000 require finance manager approval;
below that they are auto-approved.** The threshold is the team's; the illustrating values
below are derived from it and proposed for confirmation.

Written as a rule with its boundary covered:

```gherkin
  @rule:invoice-approval-threshold
  Rule: Invoices of $10,000 or more require finance manager approval

    @mvp @functional @scenario:approval-routing-by-amount
    Scenario Outline: Invoice amount decides the approval path
      Given a finance analyst has submitted an invoice for <amount>
      When the invoice enters the approval workflow
      Then the invoice status is "<status>"
      And the approval record names approver "<approver>"

      Examples: Around the manager-approval threshold
        | amount     | status                    | approver        |
        | $9,999.99  | Approved                  | system          |
        | $10,000.00 | Pending manager approval  | finance manager |
        | $12,500.00 | Pending manager approval  | finance manager |
```

Three rows, three jobs. `$9,999.99` is the last amount that auto-approves. `$10,000.00` is
the boundary the rule's own wording turns on — the row that catches the off-by-one an
implementation is most likely to get wrong, and the one specifications most often omit.
`$12,500.00` confirms the rule keeps holding above the boundary rather than only at it.

Notice what the example does **not** do. It does not enumerate every amount. It does not
specify how routing is implemented. It does not invent the $10,000 figure — that came from
the business, and if it had not, the correct output would be
`<TBD — approval threshold not yet decided>` and an open question, not a plausible number.
