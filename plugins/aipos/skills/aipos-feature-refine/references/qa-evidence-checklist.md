# QA Evidence Checklist

> **Tool-agnostic.** *Generator* = whatever produced Draft 0 (e.g. Aha!, an LLM prompt, a human author). *Tracker* = wherever the feature fields live (e.g. Azure DevOps, Jira, Linear, a markdown file). Named tools are examples, not requirements.

## Contents

- [Purpose](#purpose)
- [Applies to](#applies-to)
- [QA review principle](#qa-review-principle)
- [QA responsibilities](#qa-responsibilities)
- [Pre-refinement review](#pre-refinement-review)
- [NFR evidence review](#nfr-evidence-review)
- [Evaluation criteria review](#evaluation-criteria-review)
- [Refinement facilitation prompts](#refinement-facilitation-prompts)
- [QA decision model](#qa-decision-model)
- [QA readiness score](#qa-readiness-score)
- [Critical blockers](#critical-blockers)
- [Review output](#review-output)
- [Required PR evidence](#required-pr-evidence)
- [Skill response format](#skill-response-format)
- [Generator feedback rules](#generator-feedback-rules)
- [Repo readiness note](#repo-readiness-note)

## Purpose

Use this checklist to help QA review generated Gherkin, NFRs, and evaluation criteria before AI-assisted coding starts.

The goal is evidence readiness. QA should confirm each approved behavior has a clear pass/fail path before GovKit execution.

GovKit treats QA as the owner of proof, not only testing. QA helps the team answer:

- What behavior needs proof?
- What evidence proves it worked?
- What failure modes need coverage?
- Which NFRs need measurable thresholds?
- Which evaluation criteria need pass/fail rules?
- What evidence belongs in the PR or release record?

## Applies to

Use this checklist for:

- Draft 0 review
- tracker Acceptance Criteria review
- tracker NFR field review
- Evaluation criteria review
- Refinement / Spec Alignment
- GovKit Gherkin collaboration skill review
- GovKit spec readiness review
- AI coding agent handoff

## QA review principle

The generator creates candidate scenarios.

QA turns candidate scenarios into provable behavior.

Do not approve a spec for AI-assisted coding unless the team knows how success and failure will be proven.

## QA responsibilities

QA owns:

- Testability
- Evidence quality
- Edge case discovery
- Negative path coverage
- Permission and access coverage
- Evaluation criteria completeness
- Pass/fail thresholds
- PR evidence expectations
- Regression risk notes

QA does not need to own product intent, architecture design, or final implementation decisions.

QA should challenge any scenario with unclear proof.

## Pre-refinement review

Before refinement, QA should review the tracker work item fields and mark issues for discussion.

### 1. Behavior proof

Check each scenario for a visible or auditable outcome.

Ready signals:

- The Then step describes an observable result.
- The expected result is testable through UI, API, event, report, audit trail, metric, log, or evaluation output.
- The scenario has enough context to reproduce the behavior.
- The expected result is not hidden inside internal implementation detail.

Questions:

- How will QA prove this scenario passed?
- What artifact shows the outcome?
- What would failure look like?
- Is the expected result visible outside code internals?

Blockers:

- The outcome is vague.
- The Then step describes another action instead of a result.
- The expected result depends on unstated data or state.
- The scenario requires QA to infer product intent.

### 2. Rule coverage

Check whether each business rule has evidence coverage.

Ready signals:

- Each important rule maps to at least one scenario.
- Each rule has at least one concrete example.
- Rules with risk have negative or boundary coverage.
- Deferred rules are listed as out of scope.

Questions:

- Which rule is this scenario proving?
- Which rule lacks a scenario?
- Which rule has only happy path coverage?
- Which rule belongs outside this feature?

Blockers:

- A key rule is missing.
- A rule is implied but not stated.
- A scenario exists without a clear rule.
- The feature depends on a rule still unresolved.

### 3. Edge cases

Check for important failure, boundary, duplicate, and invalid-state paths.

Review these categories:

- Missing input
- Invalid input
- Duplicate submission
- Unsupported status
- Expired or stale state
- Unauthorized access
- Insufficient permissions
- Conflicting data
- Empty results
- Partial failure
- Retry behavior
- Timeout behavior
- External dependency failure

Questions:

- What would break this feature in production?
- What happens when the input is missing or invalid?
- What happens when the same action runs twice?
- What happens when a dependency fails?
- Which edge case must be covered now?
- Which edge case should be deferred?

Blockers:

- Only happy path scenarios exist for a risky feature.
- Permission behavior is missing.
- Failure behavior is undefined.
- Boundary conditions are obvious but absent.

### 4. Permissions and role behavior

Check whether the scenario states the actor and access expectations.

Ready signals:

- Relevant user role or system actor is named.
- Authorized behavior is clear.
- Unauthorized behavior is clear when relevant.
- Sensitive actions include audit or trace expectations when needed.

Questions:

- Who is allowed to perform this action?
- Who should be blocked?
- What should the user see when access is denied?
- What evidence proves access control worked?

Blockers:

- Role is unstated for permission-sensitive behavior.
- Unauthorized behavior is missing.
- Sensitive action lacks audit expectations.

### 5. Data conditions

Check whether test data needs are clear.

Ready signals:

- Starting state is clear.
- Required records, entities, or inputs are named in business language.
- Data freshness or version assumptions are stated when relevant.
- Test data setup is feasible.

Questions:

- What data must exist before this scenario runs?
- What data should not exist?
- Which record state matters?
- Does the scenario depend on time, freshness, or sequence?

Blockers:

- Given step lacks enough state.
- Test data setup is unclear.
- Scenario depends on unspecified external data.
- Data state conflicts with current system behavior.

## NFR evidence review

QA should verify NFRs are measurable and tied to evidence.

### Performance

Ready signals:

- Threshold is stated.
- Load or usage condition is stated.
- Measurement method is stated.
- Evidence artifact is named.

Questions:

- What response time or processing threshold applies?
- Under which load condition?
- Which report or metric proves it?

### Security

Ready signals:

- Authentication and authorization expectations are stated.
- Sensitive data handling is clear.
- Audit expectations are named when relevant.
- Security evidence type is named.

Questions:

- What access control must be proven?
- What sensitive data needs protection?
- What audit evidence is required?

### Privacy

Ready signals:

- PII or sensitive data is identified.
- Redaction, masking, consent, or retention expectations are stated when relevant.
- Evidence path is named.

Questions:

- What data is sensitive?
- Where does it appear?
- What should never appear in logs, prompts, responses, or exports?

### Reliability

Ready signals:

- Failure behavior is stated.
- Retry, fallback, or user messaging expectation is stated when relevant.
- Evidence artifact is named.

Questions:

- What happens when a dependency fails?
- What does the user see?
- What system record proves recovery or failure handling?

### Observability

Ready signals:

- Logs, metrics, traces, audit events, or dashboards are named.
- Required correlation identifiers are stated when relevant.
- Evidence is accessible for review.

Questions:

- What trace proves the workflow happened?
- Which metric shows health or failure?
- What audit event should exist?

### Accessibility

Ready signals:

- Accessibility expectations are stated for user-facing changes.
- Required standard or check is named.
- Evidence type is named.

Questions:

- What accessibility rule applies?
- Which screen, flow, or component needs review?
- What scan or manual check proves it passed?

### Data quality

Ready signals:

- Data validity rules are stated.
- Duplicate, missing, stale, or malformed data expectations are clear.
- Evidence artifact is named.

Questions:

- What makes data valid?
- What records should be excluded?
- What data quality report proves the rule passed?

## Evaluation criteria review

Use this section for GenAI, decision-support, recommendation, summarization, classification, extraction, routing, or ranking behavior.

Ready signals:

- Evaluation type is named.
- Dataset, fixture, or test input set is identified.
- Pass/fail threshold is stated.
- Evidence artifact is named.
- Regression expectations are stated.
- The agentic behavior question was asked explicitly, and the team's yes/no answer is recorded as `multi_agent: true|false` in `eval_criteria.yaml`.

Evaluation areas:

- Accuracy
- Groundedness
- Completeness
- Policy compliance
- Safety
- Tone
- Format adherence
- Retrieval quality
- Tool or routing correctness
- Hallucination risk
- Refusal behavior
- Citation or source alignment

Questions:

- Agentic behavior: yes or no? (The explicit answer sets `multi_agent: true|false` in `eval_criteria.yaml` — never infer it.)
- What does good output mean for this feature?
- What dataset or examples prove it?
- What threshold decides pass or fail?
- What failure should block release?
- What evidence should attach to the PR?

Blockers:

- AI behavior has no evaluation criteria.
- Evaluation criteria lack thresholds.
- Dataset or test inputs are missing.
- No evidence artifact is named.
- Policy or safety behavior is undefined.

## Refinement facilitation prompts

Use these prompts during Spec Alignment:

- What evidence proves this scenario passed?
- What would make this scenario fail?
- Which edge case belongs in this feature?
- Which edge case should move out of scope?
- What data state does this scenario require?
- What role or permission matters here?
- Which NFR applies to this behavior?
- What threshold makes the NFR measurable?
- What evaluation result belongs in the PR?
- What should the AI coding agent not infer?

## QA decision model

Use the decision model below at the end of refinement.

| Decision | Meaning |
|---|---|
| Approved | Evidence path is clear. Ready for GovKit execution. |
| Approved with edits | Targeted changes needed before GovKit execution. |
| Blocked | Evidence path is missing or unsafe. Do not start AI-assisted coding. |

## QA readiness score

Score each dimension from 0 to 1.

| Dimension | Score |
|---|---:|
| Observable outcomes | 0 to 1 |
| Rule coverage | 0 to 1 |
| Edge case coverage | 0 to 1 |
| Permission coverage | 0 to 1 |
| Data condition clarity | 0 to 1 |
| NFR measurability | 0 to 1 |
| Evaluation criteria quality | 0 to 1 |
| Evidence artifact clarity | 0 to 1 |
| Regression risk coverage | 0 to 1 |
| AI coding readiness | 0 to 1 |

Total possible score: 10.

The critical blocker list is the gate. The numeric score is advisory: it shows where evidence is weak but does not by itself authorize coding. If any critical blocker is present, the decision is Blocked regardless of score.

| Total score      | Decision (when no blocker is present) |
|------------------|---|
| 8.0 to 10.0      | Ready |
| 7.0 to under 8.0 | Needs targeted edits |
| Under 7.0        | Block AI-assisted coding |

## Critical blockers

Block GovKit execution when any item below appears:

- Expected outcome is not observable.
- Key rule lacks scenario coverage.
- Permission behavior is missing for restricted actions.
- Failure behavior is missing for risky workflows.
- AI behavior lacks evaluation criteria.
- NFRs are vague or unmeasurable when relevant.
- Pass/fail threshold is missing for important evidence.
- Test data conditions are unknown.
- QA cannot identify evidence for PR review.
- The coding agent would need to infer product or QA intent.

## Review output

A completed QA review should produce:

- QA evidence notes
- Missing edge cases
- Missing permission checks
- Missing NFR thresholds
- Missing evaluation criteria
- Required PR evidence
- Deferred test risks
- QA readiness score
- Development Token recommendation

## Required PR evidence

For each approved feature, identify which evidence belongs in the PR or release record.

Common evidence artifacts:

- Gherkin test result
- Unit test result
- Integration test result
- API contract test result
- Evaluation report
- Golden dataset result
- Performance report
- Security review result
- Accessibility check
- Data quality report
- Observability screenshot or trace link
- Manual test note
- Risk acceptance note

## Skill response format

A GovKit Gherkin collaboration skill using this checklist should return:

```markdown
# QA Evidence Review

## QA readiness score
<score>/10

## Decision
Approved | Approved with edits | Blocked

## Critical blockers
- <blocker or None>

## Evidence gaps
- <gap>

## Missing edge cases
- <edge case>

## NFR evidence gaps
- <gap>

## Evaluation criteria gaps
- <gap>

## Questions for refinement
- <question>

## Required PR evidence
- <artifact>

## Suggested QA edits
- <edit>

## Notes for generator improvement
- <agent instruction improvement>
```

## Generator feedback rules

When QA finds a repeated issue, add an improvement note for the generator.

Common feedback categories:

- Outcome not observable
- Missing negative path
- Missing permission path
- Missing data condition
- Missing NFR threshold
- Missing evaluation threshold
- Missing evidence artifact
- Edge case omitted
- Test data unclear
- AI output quality undefined
- Safety or policy behavior undefined

## Repo readiness note

This checklist supports collaboration review. Repo-based readiness still requires GovKit validation against:

- Existing test framework
- Existing step definitions
- Evaluation runner
- Test data setup
- CI workflow
- Observability setup
- Security and privacy controls
- Local GovKit configuration
