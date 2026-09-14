# GovKit Readiness Rubric

> **Tool-agnostic.** *Generator* = whatever produced Draft 0 (e.g. Aha!, an LLM prompt, a human author). *Tracker* = wherever the feature fields live (e.g. Azure DevOps, Jira, Linear, a markdown file). Named tools are examples, not requirements.

## Purpose

Use this rubric to decide whether an approved feature package is ready for GovKit repo execution and AI-assisted coding.

This rubric is stricter than the Gherkin refine review. The refine review improves shared understanding during refinement. The readiness review validates whether the feature package is complete, consistent, repo-aware, and safe for a coding agent to execute.

## Applies to

Use this reference inside the `govkit-feature-readiness` skill.

Recommended location:

```text
skills/
  feature-readiness/
    references/
      govkit-readiness-rubric.md
```

Use it for:

- Approved tracker work item specs copied into the repo
- GovKit feature packages generated from a generator or tracker
- Pre-coding readiness checks
- AI coding agent handoff reviews
- PR preparation checks
- Development Token decisions

## Operating principle

The generator creates Draft 0.

Refinement approves Draft 1.

GovKit validates repo readiness.

AI-assisted coding starts only after the feature package passes this readiness gate.

## Readiness decision

| Decision | Meaning |
|---|---|
| Approved | The feature package is ready for GovKit execution and AI-assisted coding. |
| Approved with edits | Minor issues remain. Fix them before implementation starts. |
| Blocked | Do not start AI-assisted coding. Resolve blockers first. |

## Expected feature package

A complete GovKit feature package should include:

```text
/features/<work-item-id>/
  acceptance.feature
  nfrs.md
  eval_criteria.yaml
```

Optional files:

```text
/features/<work-item-id>/
  architecture_preflight.md
  plan.md
```

## Required inputs

The readiness review should inspect:

| File or field | Purpose |
|---|---|
| `acceptance.feature` | Behavior contract |
| `nfrs.md` | Quality constraints |
| `eval_criteria.yaml` | Evidence and pass/fail criteria |
| Repo architecture docs | Fit with system design |
| Existing tests | Test strategy and conventions |
| Existing step definitions | Reuse and consistency |
| GovKit config | Local workflow expectations |
| CI pipeline | Evidence and execution path |

If one of these inputs is missing, record the gap and decide whether it blocks implementation.

## Scoring model

Score each dimension from 0 to 1.

| Score | Meaning |
|---:|---|
| 1.0 | Ready |
| 0.5 | Needs targeted edits |
| 0.0 | Not ready |

Total possible score: 12.

The critical blocker list is the gate. The numeric score is advisory: it shows where the package is weak but does not by itself authorize coding. If any critical blocker is present, the decision is Blocked regardless of score.

| Total score       | Decision (when no blocker is present) |
|-------------------|---|
| 10.0 to 12.0      | Approved |
| 8.5 to under 10.0 | Approved with edits |
| Under 8.5         | Blocked |

## Critical blockers

Block AI-assisted coding when any item below is present:

- `acceptance.feature` is missing.
- `nfrs.md` is missing when quality constraints are relevant.
- `eval_criteria.yaml` is missing for AI, decision-support, data, or risk-sensitive behavior.
- The feature intent conflicts with the accepted scenarios.
- A scenario lacks an observable outcome.
- A key business rule is missing.
- A relevant permission, privacy, security, compliance, or safety path is missing.
- Evaluation criteria lack pass/fail thresholds.
- NFRs lack measurable thresholds where thresholds are needed.
- The feature depends on unresolved product questions.
- The feature asks the coding agent to infer business intent.
- The feature conflicts with existing architecture or repo conventions.
- The feature needs external dependencies with no stated assumption or integration path.
- The test or evaluation evidence path is unknown.
- The repo lacks enough context for an AI coding agent to operate safely.

## Rubric dimensions

### 1. Feature package completeness

The required files are present and readable.

| Score | Guidance |
|---:|---|
| 1.0 | Required files exist and contain usable content. |
| 0.5 | Core files exist, but one or more supporting sections are thin or missing. |
| 0.0 | A required file is missing or empty. |

Review checks:

- Is `acceptance.feature` present?
- Is `nfrs.md` present when NFRs matter?
- Is `eval_criteria.yaml` present when evidence matters?
- Is source content traceable to the generator or tracker?
- Are assumptions and out-of-scope items visible?

### 2. Source traceability

The repo feature maps back to the approved product record.

| Score | Guidance |
|---:|---|
| 1.0 | Work item ID, title, source system, and approved fields are traceable. |
| 0.5 | Source is identifiable, but field mapping or approval status is incomplete. |
| 0.0 | The repo feature lacks traceability to the approved feature. |

Review checks:

- Which tracker work item or generator record supplied the feature package?
- Is the approved version reflected in the repo files?
- Are copied fields complete?

### 3. Gherkin syntax and structure

The behavior contract is valid enough for humans, tools, and agents.

| Score | Guidance |
|---:|---|
| 1.0 | `Feature`, `Rule`, `Scenario`, `Given`, `When`, and `Then` are used consistently. |
| 0.5 | Structure is understandable, but formatting or step discipline needs cleanup. |
| 0.0 | Gherkin is malformed, incomplete, or hard to parse. |

Review checks:

- Does the file have one clear `Feature`?
- Are rules and scenarios organized cleanly?
- Do scenarios have context, action, and outcome?
- Are scenario names specific?
- Are scenario outlines and examples tables valid when used?

### 4. Behavior clarity

The feature package describes behavior without implementation leakage.

| Score | Guidance |
|---:|---|
| 1.0 | Scenarios state business or system behavior in clear language. |
| 0.5 | Most behavior is clear, but some wording or scope needs refinement. |
| 0.0 | Scenarios read like implementation tasks or ambiguous notes. |

Review checks:

- What behavior does each scenario prove?
- Does the wording preserve product intent?
- Does the feature avoid internal design detail?
- Does each scenario fit the feature boundary?

### 5. Observable outcomes

Expected results have a clear evidence path.

| Score | Guidance |
|---:|---|
| 1.0 | Outcomes are visible through UI, API, event, record, report, metric, trace, or audit evidence. |
| 0.5 | Outcomes are partly observable, but evidence details are incomplete. |
| 0.0 | Outcomes rely on hidden assumptions or internal logic only. |

Review checks:

- How will the team prove each `Then` happened?
- What output, event, record, or artifact confirms success?
- Which outcomes need logs, traces, metrics, or audit evidence?

### 6. Rule and edge-case coverage

The feature covers the important business paths and risk paths.

| Score | Guidance |
|---:|---|
| 1.0 | Happy paths, negative paths, permission paths, and key edge cases are covered or explicitly deferred. |
| 0.5 | Main path is covered, but risk paths need more detail. |
| 0.0 | Coverage is too thin for implementation. |

Review checks:

- Which business rules lack scenarios?
- Which invalid, duplicate, expired, unauthorized, or boundary cases matter?
- Which edge cases are intentionally out of scope?
- Are deferred cases captured in the package's out-of-scope section (e.g. in `feature_source.md`) or source notes?

### 7. NFR readiness

Quality constraints are measurable and tied to the feature.

| Score | Guidance |
|---:|---|
| 1.0 | Relevant NFRs include conditions, thresholds, evidence, and owner. |
| 0.5 | NFRs exist, but thresholds or evidence need detail. |
| 0.0 | Relevant NFRs are missing or too vague. |

Review NFR areas:

- Performance
- Security
- Privacy
- Reliability
- Observability
- Accessibility
- Data quality
- Compliance
- Cost
- Supportability

Review checks:

- Which NFRs apply to this feature?
- What threshold defines pass or fail?
- What evidence proves the NFR passed?
- Which NFRs affect release approval?

### 8. Evaluation criteria readiness

Evaluation criteria provide a clear pass/fail standard.

| Score | Guidance |
|---:|---|
| 1.0 | Criteria link to scenarios or rules and include thresholds, data, evidence, and owner. |
| 0.5 | Criteria exist, but links, thresholds, or artifacts need refinement. |
| 0.0 | Criteria are missing or not actionable. |

For GenAI behavior, inspect:

- Accuracy
- Groundedness
- Policy compliance
- Safety
- Retrieval quality
- Tool or agent routing
- Regression risk
- Human review path

Review checks:

- Which scenario or rule does each eval support?
- What dataset, prompt set, test case, or trace set drives the evaluation?
- What threshold defines success?
- What artifact will appear in the PR or release review?

### 9. Repo fit

The feature fits the application architecture and local conventions.

| Score | Guidance |
|---:|---|
| 1.0 | Feature aligns with repo structure, architecture, tests, and GovKit configuration. |
| 0.5 | Some local adaptation is needed, but the path is clear. |
| 0.0 | Feature conflicts with architecture, test strategy, or repo reality. |

Review checks:

- Which app, service, API, job, workflow, or module is affected?
- Do architecture docs confirm the likely target area?
- Do existing tests show expected style and boundaries?
- Are domain names, API routes, events, or data entities consistent with the repo?
- Are technology assumptions stated correctly?

### 10. Test and evidence execution path

The team knows how evidence will be produced — **credibly**, not yet actually.

| Score | Guidance |
|---:|---|
| 1.0 | Every scenario has a named verification boundary, an identified place in the existing suite, and a known or explicitly-to-be-established command and evidence artifact. |
| 0.5 | The boundary and the suite are identified for most scenarios, but fixtures, isolation, or the evidence artifact need detail. |
| 0.0 | No credible evidence path exists, or the path is unknown for scenarios that carry real risk. |

This dimension scores the **plan**, not its execution. New step definitions and passing tests are **not** prerequisites for the Development Token — see "Ready, automated, verified" below. What is required is that nobody has to invent the approach after coding starts.

Review checks:

- Which tests should be added or updated?
- Which existing tests and step definitions relate to the spec, and can their step language be reused?
- What is the right verification boundary for each scenario — domain/service, API, UI, evaluation, or justified manual evidence?
- What fixtures, controlled time, isolation and dependency handling does each scenario need?
- Which eval runner or script will execute the criteria?
- Which command produces the evidence, and which CI step runs it? Where no command exists yet, is that stated as still to be established rather than left blank?
- What evidence belongs in the PR?

### 11. AI coding agent safety

The feature package gives the coding agent enough context without asking it to invent intent.

| Score | Guidance |
|---:|---|
| 1.0 | The agent has clear behavior, boundaries, constraints, and evidence expectations. |
| 0.5 | The agent has enough to start after small edits or added context. |
| 0.0 | The agent would need to guess product intent, architecture, or acceptance evidence. |

Review checks:

- What should the coding agent not assume?
- Are open questions resolved or deferred?
- Are files and target areas identified enough for safe planning?
- Are constraints explicit?
- Does the feature package prevent overbuilding?

### 12. Handoff quality

The package is ready to feed into the GovKit workflow.

| Score | Guidance |
|---:|---|
| 1.0 | The handoff includes copy-ready files, clear decision, and next steps. |
| 0.5 | Handoff is usable, but needs cleanup before execution. |
| 0.0 | Handoff is fragmented or unclear. |

Review checks:

- Is the Development Token decision recorded?
- Is `readiness_report.md` generated or ready to generate?
- Does the scenario verification plan cover every scenario, naming the behavior and the rule each one verifies?
- Are rules, scenarios, NFRs, evaluations and evidence connected by stable identifiers (`@rule:` / `@scenario:`) rather than by quoted wording that the next rewrite will break? A package without authored tags is keyed by derived ids and is not blocked for it; recommend the tags as an improvement.
- Are blockers separated from improvements?
- Are deferred items recorded?
- Is the next GovKit command or agent task clear?

## Ready, automated, verified

Three different states, routinely collapsed into one, and collapsing them is how a
readiness gate turns into a build blocker:

| State | What it means | When |
|---|---|---|
| **Ready to implement** | The behavior contract is complete and a credible execution path exists for every scenario | This gate. What the Development Token authorizes. |
| **Automated** | Step definitions and tests exist and run | During implementation |
| **Verified passing** | Those tests have actually run and passed, and the evidence exists | After implementation, at PR |

**At readiness, require a credible path; after implementation, require actual results.**
Missing step definitions and unwritten tests are not blockers at this gate — writing them
is the work the token authorizes. What *is* a blocker is not knowing how a scenario could
be verified at all, because that means nobody has decided what "done" looks like.

Never report "automated" or "verified passing" from this gate. It has not run anything.

## Development Token rules

A Development Token is approved only when:

- Score is 10.0 or higher out of 12.
- No critical blockers exist.
- Product intent is traceable to source.
- QA evidence path is defined.
- Engineering repo fit is acceptable.
- AI coding agent safety is acceptable.

Use this language:

```markdown
## Development Token
Decision: Approved | Approved with edits | Blocked
Reason: <one concise reason>
Required before coding: <items or None>
```

## Required readiness report format

The feature-readiness skill should produce:

```markdown
# GovKit Readiness Report

## Work item
- Source: <generator | tracker | local>
- Work item ID: <id>
- Title: <title>

## Score
<score>/12

## Decision
Approved | Approved with edits | Blocked

## Development Token
Approved | Not approved

## Critical blockers
- <blocker or None>

## Required edits before coding
- <edit or None>

## Feature package status
| File | Status | Notes |
|---|---|---|
| acceptance.feature | Present | <notes> |
| nfrs.md | Present | <notes> |
| eval_criteria.yaml | Present | <notes> |


## Scenario readiness
| Scenario | ID | Status | Issue |
|---|---|---|---|
| <name> | @scenario:<slug>, or <slug> (derived) | Ready | None |

## Scenario verification plan
<!-- One row per scenario. This is the handoff an implementer or coding agent works from.
     "To be established" is a legitimate value and far better than a confident blank. -->
| Scenario | Verifies (behavior · rule) | Boundary | Existing tests / step definitions | Proposed additions | Fixtures · time · isolation · dependencies | Command | Expected evidence | To establish |
|---|---|---|---|---|---|---|---|---|
| @scenario:<slug>, or <slug> (derived) | <behavior> · @rule:<slug>, or <slug> (derived) | domain \| service \| API \| UI \| evaluation \| manual (justified) | <path::name, or None found> | <new step defs / test files> | <fixture, frozen clock, isolation, stub or contract test> | `<known command, or —>` | <artifact that lands in the PR> | <what is not yet known> |

## NFR readiness
| Area | Status | Threshold | Evidence |
|---|---|---|---|
| <area> | Ready | <threshold> | <artifact> |

## Evaluation readiness
| Eval ID | Status | Threshold | Evidence |
|---|---|---|---|
| <id> | Ready | <threshold> | <artifact> |

## Repo fit
- Target area: <area>
- Existing tests: <summary>
- Architecture notes: <summary>
- Risks: <risks or None>

## AI coding agent instructions
- <safe instruction>

## Do not assume
- <assumption the agent must not make>

## Deferred items
- <item or None>

## Next step
- <GovKit workflow command or agent handoff instruction>
```

## Recommended failure handling

When blocked, do not rewrite the feature into an approved state.

Return:

- The blocker
- The likely owner
- The exact question to resolve
- The file or field needing change
- The reason coding should not start

Example format:

```markdown
- Blocker: Evaluation threshold is missing for groundedness.
  Owner: QA / evaluation owner
  Required change: Add pass threshold and evidence artifact to `eval_criteria.yaml`.
  Reason: The coding agent has no release evidence target for this behavior.
```

## Agent guardrails

The feature-readiness skill must not:

- Invent product intent
- Invent business rules
- Invent NFR thresholds
- Invent evaluation thresholds
- Hide unresolved questions
- Start implementation when blocked
- Rewrite architecture to fit the spec
- Treat collaboration approval as repo readiness approval
- Require step definitions, written tests, or passing runs as a precondition for the token
- Report a scenario as automated or verified passing — this gate runs nothing
- Present a scenario carrying an unresolved placeholder as ready for execution
- Replace human approval for risk-sensitive decisions

The skill should:

- Validate the package as written
- Separate blockers from improvements
- Preserve traceability
- Surface repo conflicts early
- Keep the Development Token decision explicit
- Produce a clear handoff for AI-assisted coding
