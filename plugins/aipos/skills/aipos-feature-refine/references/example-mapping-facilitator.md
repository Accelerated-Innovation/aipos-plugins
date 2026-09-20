# Example Mapping Facilitator Reference

> **Tool-agnostic.** *Generator* = whatever produced Draft 0 (e.g. Aha!, an LLM prompt, a human author). *Tracker* = wherever the feature fields live (e.g. Azure DevOps, Jira, Linear, a markdown file). Named tools are examples, not requirements.

## Contents

- [Purpose](#purpose)
- [Core idea](#core-idea)
- [When to use this reference](#when-to-use-this-reference)
- [Inputs](#inputs)
- [Expected outputs](#expected-outputs)
- [Facilitation principles](#facilitation-principles)
- [Team roles](#team-roles)
- [Refinement flow](#refinement-flow)
- [Facilitator prompts](#facilitator-prompts)
- [Skill behavior rules](#skill-behavior-rules)
- [Output format for the skill](#output-format-for-the-skill)
- [Tracker update guidance](#tracker-update-guidance)
- [Handoff to repo mode](#handoff-to-repo-mode)

## Purpose

Use this reference with the GovKit Gherkin Collaboration Skill during refinement.

The goal is to help Product, QA, and Engineering convert Draft 0 Gherkin into an approved behavior contract before AI-assisted coding starts.

This reference is designed for real work.

## Core idea

Example Mapping creates a shared view of a feature through five buckets:

- Feature intent
- Rules
- Examples
- Questions
- Out-of-scope items

In GovKit, these buckets align to the spec package:

| Example Mapping item | GovKit artifact |
|---|---|
| Feature intent | the generator feature description and tracker title |
| Rules | Acceptance rules inside the Gherkin review |
| Examples | Concrete scenarios in `acceptance.feature` |
| Questions | Refinement questions and blockers |
| Out-of-scope items | Explicit exclusions in the feature notes or NFR file |

## When to use this reference

Use this reference when:

- the generator created Gherkin for a Feature
- The team needs refinement before coding starts
- PMs are unsure whether the Gherkin reflects intent
- QA needs stronger evidence or edge-case coverage
- Engineering sees ambiguity dangerous for AI coding agents
- The team needs a Development Token decision

Do not use this reference after coding has started except for change review or defect-driven clarification.

## Inputs

The skill should work from the best available set of inputs.

Preferred inputs:

- tracker feature title
- tracker feature description
- Acceptance Criteria field
- NFRs field
- Evaluation Criteria field
- generator assumptions
- generator open questions
- generator out-of-scope notes
- Team comments from refinement

Optional inputs:

- Linked epic or parent feature
- User or persona notes
- API, workflow, or data contract notes
- QA risk notes
- Prior defect context

## Expected outputs

The skill should produce:

- Mapped feature intent
- Candidate rules
- Scenario-to-rule coverage notes
- Missing or weak examples from the real feature
- Questions for refinement
- Out-of-scope recommendations
- Suggested Gherkin edits
- NFR gaps
- Evaluation gaps
- GovKit readiness score
- Development Token recommendation

## Facilitation principles

### Use real work

Every question should improve the actual tracker work item under review.

Avoid:

- Generic classroom scenarios
- Sample banking, shopping, or login examples unrelated to the feature
- Training-only artifacts
- Rewrites detached from the team’s real product language

### Preserve product intent

The skill must not invent intent.

When intent is unclear, return a question instead of writing new behavior.

Preferred behavior:

- Explain uncertainty
- Identify the missing rule or example
- Ask the smallest useful question
- Suggest a safe wording option only when intent is present

### Separate rules from examples

Rules describe what must be true.

Examples show a concrete situation proving the rule.

The skill should flag scenarios with no rule and rules with no scenario coverage.

### Keep Gherkin behavioral

The skill should keep scenarios focused on behavior, not implementation.

Good scenario traits:

- One clear business rule
- One meaningful event or action
- One observable outcome
- Plain language
- Clear role, state, or condition when needed

Weak scenario traits:

- Several unrelated outcomes
- UI click paths unless UI behavior is the feature
- Internal database or framework detail
- Vague words like successful, valid, appropriate, or handled
- Hidden assumptions about permissions, timing, or data state

### Treat questions as valuable output

Open questions are not failure. Hidden questions are failure.

The skill should help the team expose questions before coding starts.

## Team roles

### Product Manager

Owns:

- Feature intent
- Business rules
- Scope boundaries
- Priority of behavior
- Out-of-scope decisions

The PM should answer:

- What outcome should this feature create?
- Which users or roles matter?
- Which rule must never be violated?
- Which behavior is outside this feature?

### QA or evaluation owner

Owns:

- Evidence strategy
- Negative paths
- Edge cases
- Evaluation criteria
- Pass/fail thresholds
- Test data needs

QA should answer:

- How will success be proven?
- What failure path matters most?
- What data state creates risk?
- Which evidence belongs in the PR?

### Engineering

Owns:

- Repo fit
- Architecture constraints
- Test automation path
- Feasibility
- AI coding agent readiness

Engineering should answer:

- What context does the coding agent need?
- Which dependency or contract is missing?
- Which scenario creates implementation risk?
- Which assumption conflicts with the repo?

### Facilitator

Owns:

- Keeping the discussion focused
- Separating rules, examples, questions, and scope
- Preventing premature implementation design
- Capturing decisions in the tracker
- Driving the Development Token decision

The facilitator should not own product intent.

## Refinement flow

### Step 1: Confirm feature intent

Ask:

- What is this feature responsible for?
- What user, system, or workflow benefits?
- What outcome matters most?
- What is explicitly outside this feature?

Skill action:

- Summarize intent in two to four sentences
- Flag conflicts between feature description and Gherkin
- Identify unclear scope boundaries

### Step 2: Extract rules

Ask:

- What rules appear in the current Gherkin?
- Which rules are stated in prose but missing from scenarios?
- Which rule is implied but not explicit?
- Which rule is disputed?

Skill action:

Return a rules table:

```markdown
| Rule ID | Rule | Source | Covered by scenario | Notes |
|---|---|---|---|---|
| R1 | <rule> | Gherkin / description / NFR / team note | Yes / No / Partial | <notes> |
```

### Step 3: Map scenarios to rules

Ask:

- Which scenario proves this rule?
- Which scenario proves too many rules?
- Which scenario has no clear rule?
- Which rule needs another scenario from the real feature?

Skill action:

Return coverage notes:

```markdown
| Scenario | Rule covered | Coverage | Concern |
|---|---|---|---|
| <scenario name> | R1 | Full / Partial / None | <concern> |
```

### Step 4: Strengthen examples from real work

In this reference, examples mean concrete feature situations, not practice exercises.

Ask:

- What real user role or system state triggers this behavior?
- What real input, decision, record, or event matters?
- What result would prove the rule worked?
- What production risk deserves a negative scenario?

Skill action:

- Identify vague scenarios
- Suggest revised scenarios using only supplied feature facts
- Ask questions where details are missing
- Avoid inventing fake data unless the team asks for placeholder test data

### Step 5: Capture questions

Ask:

- What must be answered before AI-assisted coding starts?
- What question affects product behavior?
- What question affects evidence or testing?
- What question affects architecture or repo fit?

Skill action:

Return questions grouped by owner:

```markdown
| Owner | Question | Blocking? | Reason |
|---|---|---|---|
| PM | <question> | Yes / No | <reason> |
| QA | <question> | Yes / No | <reason> |
| Engineering | <question> | Yes / No | <reason> |
```

### Step 6: Identify out-of-scope items

Ask:

- What is valuable but not part of this slice?
- What belongs in a future feature?
- What would make this feature too large?
- What is a tempting assumption for the coding agent?

Skill action:

Return out-of-scope notes:

```markdown
## Out of scope

- <item> because <reason>
```

### Step 7: Check NFR and evaluation alignment

Ask:

- Which NFRs matter for this behavior?
- What threshold makes each NFR measurable?
- What evidence proves each NFR passed?
- Which scenario needs evaluation criteria?

Skill action:

Return gaps:

```markdown
## NFR gaps

- <gap>

## Evaluation gaps

- <gap>
```

### Step 8: Decide readiness

Ask:

- Is product intent clear?
- Are key rules covered?
- Are outcomes observable?
- Are NFRs and evaluation criteria sufficient?
- Is this safe for an AI coding agent?

Skill action:

Return:

```markdown
## Development Token recommendation

Decision: Approved | Approved with edits | Blocked
Score: <score>/10
Reason: <short reason>
```

## Facilitator prompts

Use these prompts during refinement.

### Intent prompts

- What outcome should this feature create?
- Which user or system receives value?
- What would make this feature successful?
- What is outside this feature?

### Rule prompts

- What rule is this scenario proving?
- Which rule is missing from the Gherkin?
- Which rule is hidden in the description?
- Which rule matters most for risk?

### Example prompts

- What real situation proves this rule?
- What input or state matters?
- What result should be observable?
- What negative case would break trust?

### Question prompts

- What must be answered before coding starts?
- Who owns this question?
- Does this question block execution?
- What assumption would the coding agent make without the answer?

### Evidence prompts

- What evidence proves success?
- What evidence belongs in the PR?
- What metric, trace, test, or report proves the outcome?
- What threshold creates a pass/fail decision?

### Scope prompts

- What should the coding agent avoid changing?
- What belongs in a future feature?
- What is too broad for this slice?
- What should be listed as out of scope?

## Skill behavior rules

The GovKit Gherkin Collaboration Skill must follow these rules.

### Do

- Use the supplied feature context as the source of truth
- Preserve product intent
- Separate rules, examples, questions, and out-of-scope items
- Ask focused questions when intent is unclear
- Improve Gherkin wording where intent is clear
- Identify missing NFR and evaluation coverage
- Return a readiness score
- Produce tracker-ready revised text when requested

### Do not

- Invent product behavior
- Invent business rules
- Treat Draft 0 as approved
- Push implementation choices into Gherkin
- Write toy examples during pilot refinement
- Resolve open questions without user input
- Start coding guidance before readiness is approved
- Hide uncertainty behind polished language

## Output format for the skill

Use this standard response format.

```markdown
# Example Mapping Review

## Feature intent
<short summary>

## Rules
| Rule ID | Rule | Source | Coverage | Notes |
|---|---|---|---|---|

## Scenario coverage
| Scenario | Rule covered | Coverage | Concern |
|---|---|---|---|

## Questions for refinement
| Owner | Question | Blocking? | Reason |
|---|---|---|---|

## Out of scope
- <item>

## NFR gaps
- <gap>

## Evaluation gaps
- <gap>

## Suggested Gherkin edits
<only revise when intent is clear>

## Readiness score
<score>/10

## Development Token recommendation
Approved | Approved with edits | Blocked

## Notes for generator improvement
- <note>
```

## Tracker update guidance

After refinement, update the tracker with the approved content.

Minimum tracker updates:

- Acceptance Criteria field contains final Gherkin
- NFRs field contains final NFRs
- Evaluation Criteria field or section contains final evaluation criteria
- Open questions are resolved, deferred, or marked blocking
- Out-of-scope items are recorded
- Readiness score is recorded
- Development Token decision is recorded

## Handoff to repo mode

After approval, the repo-based GovKit skill should receive the finalized spec package.

Expected local files:

```text
/specs/<work-item-id>/acceptance.feature
/specs/<work-item-id>/nfrs.md
/specs/<work-item-id>/eval_criteria.yaml
/specs/<work-item-id>/readiness_report.md
```

The collaboration skill helps the team reach shared understanding.

The repo readiness skill validates execution fit.
