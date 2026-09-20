# PM Review Checklist

> **Tool-agnostic.** *Generator* = whatever produced Draft 0 (e.g. Aha!, an LLM prompt, a human author). *Tracker* = wherever the feature fields live (e.g. Azure DevOps, Jira, Linear, a markdown file). Named tools are examples, not requirements.

## Contents

- [Purpose](#purpose)
- [Applies to](#applies-to)
- [PM review outcome](#pm-review-outcome)
- [Review rule](#review-rule)
- [Before refinement](#before-refinement)
- [1. Feature intent](#1-feature-intent)
- [2. Scope boundary](#2-scope-boundary)
- [3. Business rules](#3-business-rules)
- [4. Gherkin readability](#4-gherkin-readability)
- [5. Acceptance outcomes](#5-acceptance-outcomes)
- [6. Edge cases and exceptions](#6-edge-cases-and-exceptions)
- [7. NFR review](#7-nfr-review)
- [8. Evaluation criteria review](#8-evaluation-criteria-review)
- [9. Open questions](#9-open-questions)
- [10. Readiness decision](#10-readiness-decision)
- [PM pre-review summary format](#pm-pre-review-summary-format)
- [Skill guidance](#skill-guidance)
- [Skill response format](#skill-response-format)
- [Handoff to refinement](#handoff-to-refinement)

## Purpose

Use this checklist to help Product Managers review generated Gherkin, NFRs, and evaluation criteria before AI-assisted coding begins.

This checklist supports the GovKit Gherkin Collaboration Skill. It is designed for real feature specs from any generator and tracker during refinement.

The PM does not need to make the Gherkin perfect alone. The PM owns product intent, business rules, scope, and acceptance language. QA and Engineering collaborate to strengthen evidence, feasibility, and repo readiness.

## Applies to

Use this checklist when reviewing:

- generated Feature Acceptance Criteria
- tracker Acceptance Criteria fields
- tracker NFR fields
- Evaluation criteria
- Feature scope and assumptions
- Refinement-ready specs
- Draft specs before GovKit execution

## PM review outcome

After review, the PM should be able to answer:

- What outcome should this feature create?
- What user or business problem does it solve?
- What behavior must be true when the feature works?
- What is in scope?
- What is out of scope?
- What questions must be answered before coding starts?
- Which scenarios need team review during refinement?

## Review rule

The generator creates Draft 0.

The PM prepares Draft 0 for refinement.

The team approves Draft 1 during refinement.

GovKit executes Draft 1.

Do not send Draft 0 directly into AI-assisted coding.

## Before refinement

The PM should review the feature and mark each section as:

| Status | Meaning |
|---|---|
| Ready | Clear enough for team review |
| Needs discussion | Requires Product, QA, or Engineering input |
| Blocked | Intent or scope is not clear enough for refinement |

## 1. Feature intent

Confirm the feature has one clear purpose.

Checklist:

- The feature title is specific.
- The feature description explains the desired outcome.
- The target user, role, system, or workflow is clear.
- The feature solves one primary problem.
- The business value is understandable without technical translation.
- The feature is not a bundle of unrelated changes.

Questions to ask:

- What should be different after this feature exists?
- Who benefits from this feature?
- What decision, workflow, or task does this improve?
- What would make this feature successful?

Red flags:

- The feature describes a solution but not an outcome.
- The feature includes multiple unrelated behaviors.
- The user or workflow is unclear.
- The expected business value is unstated.

## 2. Scope boundary

Confirm the scenarios belong to this feature.

Checklist:

- Each scenario supports the feature intent.
- Each scenario fits the current delivery slice.
- Future enhancements are separated from current scope.
- Deferred work is listed as out of scope.
- Dependencies are named.
- Assumptions are visible.

Questions to ask:

- Which scenario feels outside this feature?
- Which scenario belongs in a later feature?
- What work should the AI coding agent not assume?
- What dependency needs to be resolved first?

Red flags:

- One scenario introduces a separate feature.
- The feature depends on an unstated workflow change.
- The Gherkin includes behavior not discussed by Product.
- Out-of-scope work is hidden inside acceptance criteria.

## 3. Business rules

Confirm the important rules are explicit.

Checklist:

- The main business rules are listed or visible in the scenarios.
- Each rule is understandable to Product, QA, and Engineering.
- Rules do not conflict with one another.
- Rules include permission, timing, status, or data conditions when relevant.
- Rules avoid vague words such as appropriate, fast, accurate, seamless, normal, valid, or user-friendly unless defined.

Questions to ask:

- What rule is this scenario proving?
- What condition changes the expected behavior?
- What must always be true?
- What must never happen?
- What rule is missing from the Gherkin?

Red flags:

- Rules are implied instead of stated.
- The same rule appears with different wording.
- Product cannot explain why a scenario exists.
- QA or Engineering would need to guess the rule.

## 4. Gherkin readability

Confirm a business reviewer understands the scenarios.

Checklist:

- Scenario names are meaningful.
- Given steps describe starting context.
- When steps describe one meaningful action or event.
- Then steps describe expected outcomes.
- Scenarios are short enough to review in refinement.
- The wording is business-facing.
- The Gherkin avoids unnecessary technical implementation detail.

Questions to ask:

- Would a stakeholder understand this scenario?
- Is the Then step an outcome or another action?
- Which step needs clearer wording?
- Does this scenario describe behavior, not implementation?

Red flags:

- The scenario reads like a technical task list.
- The scenario describes clicks, fields, or database changes when those details are not the feature behavior.
- The expected outcome is missing.
- The scenario is too broad to test.

## 5. Acceptance outcomes

Confirm each scenario has a clear result.

Checklist:

- Every scenario has an observable outcome.
- Outcomes are specific enough for QA to verify.
- Outcomes align with the business rule.
- Outcomes do not require hidden interpretation.
- Success and failure conditions are clear.

Observable outcomes include:

- User-visible result
- API response
- System event
- Audit record
- Notification
- Report value
- Status change
- Logged decision
- Evaluation result

Questions to ask:

- How will we know this worked?
- What should the user, system, or reviewer see?
- What evidence proves this outcome?
- What would count as failure?

Red flags:

- Then steps use vague outcomes.
- The scenario says the system handles something without saying how success appears.
- QA would need to ask Product what passing means.
- The outcome is only visible inside code.

## 6. Edge cases and exceptions

Confirm the feature is not only the happy path.

Checklist:

- Common failure paths are considered.
- Missing or invalid inputs are considered when relevant.
- Duplicate actions are considered when relevant.
- Unauthorized access is considered when relevant.
- Boundary conditions are considered when relevant.
- Deferred edge cases are listed as out of scope.

Questions to ask:

- What happens when the user is not allowed to do this?
- What happens when required information is missing?
- What happens when the action is repeated?
- What exception creates the most risk?
- Which edge case should be deferred?

Red flags:

- Only happy path scenarios exist.
- Permission behavior is missing.
- Error behavior is vague.
- Edge cases are assumed but not captured.

## 7. NFR review

Confirm relevant quality constraints are present.

The PM does not need to define every technical threshold alone. The PM should confirm which quality expectations matter to the business.

Checklist:

- Relevant NFR categories are present.
- NFRs are connected to the feature outcome.
- NFRs are measurable or ready for QA and Engineering to make measurable.
- Business-impacting thresholds are stated where known.
- Missing NFR categories are flagged for refinement.

NFR categories to consider:

- Performance
- Security
- Privacy
- Reliability
- Observability
- Accessibility
- Compliance
- Data quality
- Cost
- Supportability

Questions to ask:

- What quality expectation matters for this feature?
- What risk would hurt users, customers, or operations?
- What threshold matters from a business perspective?
- What should QA or Engineering help define?

Red flags:

- No NFRs exist for a feature with security, privacy, performance, or reliability impact.
- NFRs are generic and not connected to this feature.
- NFRs say fast, secure, reliable, or compliant without measurable evidence.
- Observability is missing for behavior requiring support or audit.

## 8. Evaluation criteria review

Confirm the feature has a way to prove success.

Checklist:

- Evaluation criteria exist for AI, decision-support, recommendation, classification, summarization, retrieval, or automation behavior.
- Evaluation criteria connect to user or business outcomes.
- Pass/fail expectations are stated or marked for QA input.
- Evidence artifacts are named.
- The evaluation owner is clear.

Questions to ask:

- What does good look like?
- What result would be unacceptable?
- What evidence should be attached before release?
- Which scenario needs an evaluation threshold?
- Who owns the evaluation result?

Red flags:

- AI behavior has no evaluation criteria.
- Evaluation criteria are subjective.
- Thresholds are missing.
- The team has no evidence plan.
- The feature depends on model behavior but only functional tests are described.

## 9. Open questions

Confirm questions are visible before coding starts.

Checklist:

- Product questions are listed.
- QA questions are listed.
- Engineering questions are listed.
- Blockers are separated from non-blocking questions.
- Deferred questions are tied to out-of-scope items or later features.

Questions to ask:

- Which question blocks refinement approval?
- Which question blocks AI-assisted coding?
- Which question belongs to Product?
- Which question belongs to QA or Engineering?
- Which question should become a later feature?

Red flags:

- The team plans to let the coding agent decide.
- Questions are discussed but not captured.
- The PM cannot confirm intended behavior.
- Engineering cannot confirm feasibility because intent is missing.

## 10. Readiness decision

The PM should enter refinement with a recommended decision.

| Decision | Meaning |
|---|---|
| Ready for team review | Product intent and scope are clear enough for refinement. |
| Needs targeted discussion | Specific rules, outcomes, or questions need team input. |
| Not ready | Feature intent or scope needs more Product work before refinement. |

The final Development Token decision happens with the team.

## PM pre-review summary format

Use this format before refinement:

```markdown
# PM Pre-Review

## Feature intent
<one or two sentences>

## Scope summary
In scope:
- <item>

Out of scope:
- <item>

## Business rules needing team review
- <rule or question>

## Scenarios needing review
- <scenario name>: <reason>

## NFRs needing QA or Engineering input
- <NFR area>: <question>

## Evaluation criteria needing review
- <eval area>: <question>

## Open questions
Blocking:
- <question>

Non-blocking:
- <question>

## PM recommendation
Ready for team review | Needs targeted discussion | Not ready
```

## Skill guidance

When the GovKit Gherkin Collaboration Skill uses this checklist, it should help the PM prepare for refinement.

The skill should:

- Preserve product intent.
- Explain the scenarios in plain language.
- Identify vague business rules.
- Identify missing outcomes.
- Identify scope creep.
- Identify open questions.
- Suggest refinement discussion points.
- Avoid inventing business rules.
- Avoid converting unclear intent into final Gherkin.
- Mark unclear items as questions.

The skill should not:

- Approve the spec without PM, QA, and Engineering review.
- Replace Product judgment.
- Add implementation design as acceptance criteria.
- Hide assumptions inside rewritten scenarios.
- Send Draft 0 directly to AI-assisted coding.

## Skill response format

```markdown
# PM Review

## Readiness for refinement
Ready for team review | Needs targeted discussion | Not ready

## Product intent summary
<plain-language summary>

## Scope concerns
- <concern or None>

## Business rule gaps
- <gap or None>

## Scenario concerns
- <scenario>: <concern>

## NFR questions for refinement
- <question or None>

## Evaluation questions for refinement
- <question or None>

## Open questions
Blocking:
- <question or None>

Non-blocking:
- <question or None>

## Suggested PM edits
- <edit>

## Recommended refinement focus
- <topic>
```

## Handoff to refinement

The PM should bring the following to refinement:

- Feature intent summary
- Final or draft scope boundary
- generated Gherkin
- NFRs
- Evaluation criteria
- Open questions
- Out-of-scope notes
- Specific scenarios needing team review

The refinement team should leave with:

- Approved or revised Gherkin
- Approved or revised NFRs
- Approved or revised evaluation criteria
- Resolved questions
- Deferred scope
- GovKit readiness score
- Development Token decision
