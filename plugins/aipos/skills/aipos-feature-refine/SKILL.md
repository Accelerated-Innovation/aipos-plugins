---
name: aipos-feature-refine
description: "Review and improve an existing feature specification with Product, QA, and Engineering. Use for 3 Amigos, ambiguity, missing behavior, evidence gaps, and draft rewrites. For committed behavior, propose changes for reapproval. Repo execution-readiness and token decisions belong to readiness."
---

# GovKit Feature Refine — Gherkin Collaboration Skill

## Purpose

Help Product Managers, QA, and Engineering review Draft 0 Gherkin, NFRs, and evaluation criteria before GovKit execution.

This skill improves shared understanding during refinement. It is not the repo readiness gate and it is not an implementation planner.

Use this skill to:

- Explain generated Gherkin in plain language
- Review Acceptance Criteria, NFRs, and Evaluation Criteria fields
- Find ambiguity, missing rules, weak outcomes, and evidence gaps
- Facilitate Example Mapping against real work
- Suggest revised Gherkin while preserving product intent
- Produce a readiness signal and Development Token recommendation
- Create improvement notes for the generator

## Tool-agnostic design

This skill runs regardless of the tools a team uses to create or store feature specs. It uses two abstract roles:

| Role | What it means | Examples |
|---|---|---|
| **Generator** | Whatever produced Draft 0 | Aha! Feature Agent, an LLM prompt, a human author |
| **Tracker** | Wherever the feature fields live | Azure DevOps, Jira, Linear, a markdown file |

Throughout this skill, "generator" and "tracker" are the rules. Aha! and Azure DevOps appear only as named examples. When the skill emits feedback for the upstream system, it produces **generator improvement notes**; when it emits copy-ready field text, it produces **tracker field updates**. Substitute your own generator and tracker names freely.

## Key terms

- **Draft 0** — the generator's raw output, before human review.
- **Draft 1** — the version Product, QA, and Engineering approve together during refinement.
- **Development Token** — GovKit's name for the explicit go/no-go decision that authorizes AI-assisted coding to start. A token is *Approved*, *Approved with edits*, or *Blocked*. No token, no coding. It is a decision record, not a file format. The token itself is issued by `aipos-feature-readiness` against the feature package in the repo; this skill produces a *recommendation* toward it.

## Operating principle

The generator creates Draft 0.

Refinement creates Draft 1.

GovKit executes Draft 1.

Do not treat generated Gherkin as approved until Product, QA, and Engineering review it together.

## Scope

Use this skill for collaboration before AI-assisted coding starts.

Use it for:

- Generator output review
- Tracker field review
- PM pre-review
- QA evidence review
- refinement facilitation
- Gherkin rewrite support
- readiness signal before repo handoff

Do not use it for:

- Writing implementation code
- Creating step definitions
- Running tests
- Inspecting full repository architecture
- Final repo readiness enforcement
- Replacing Product, QA, or Engineering review
- Sizing scenarios or slicing a feature into MVP/V1/V2 releases

For repo execution-readiness and token decisions, use `aipos-feature-readiness`.
New Rules or acceptance criteria belong to `aipos-feature-create`; mentioning
Gherkin alone is not a review request. For release selection and optional scenario
complexity, use `aipos-feature-slice`. Refinement judges an existing specification;
slicing selects a complete, shippable outcome.

## Inputs

Accept any of these input forms:

- Pasted generator output (e.g. an Aha! feature)
- Pasted tracker fields (e.g. Azure DevOps or Jira fields)
- Markdown copied from a tracker
- A local source file (e.g. `feature_source.md`)
- Draft `acceptance.feature`
- Draft `nfrs.md`
- Draft `eval_criteria.yaml`
- PM notes, QA notes, or refinement notes

Normalize input into this working structure:

```yaml
source:
  generator: free text (e.g. aha, llm_prompt, human, unknown)
  tracker: free text (e.g. azure_devops, jira, linear, markdown, none)
  work_item_id: optional
  title: optional
  description: optional
fields:
  acceptance_criteria: optional
  nfrs: optional
  evaluation_criteria: optional
  agentic_behavior: optional (yes | no, only if the team has stated it explicitly)
  assumptions: optional
  open_questions: optional
  out_of_scope: optional
```

If a field is missing, record the gap. Do not invent product intent, thresholds, or business rules.

## Required references

Read these reference files when present:

| Reference | Use |
|---|---|
| `../../references/gherkin-authoring-standard.md` | **Load before reviewing or rewriting any Gherkin.** The shared authoring standard — BRIEF, explicit rules, scenario isolation, provenance, automation suitability, deterministic checks vs aggregate evaluations. Every skill in GovKit judges Gherkin against this one file. |
| `../../references/spec-identifiers.md` | The `@rule:` / `@scenario:` identifier convention. Load before rewriting Gherkin, so a rewrite preserves what evaluations and evidence point at. |
| `references/gherkin-quality-rubric.md` | Score Gherkin quality and identify blockers |
| `references/example-mapping-facilitator.md` | Structure refinement discussion |
| `references/pm-review-checklist.md` | Review intent, scope, rules, and business language |
| `references/qa-evidence-checklist.md` | Review testability, edge cases, NFRs, and evidence |

The standard is the authoring rule; the rubric is the scoring rule. They are written to agree — where they appear not to, the standard says what good looks like and the rubric says what it is worth.

If a reference file is unavailable, continue from the guidance in this file and say which rules you are applying from memory.

## Collaboration rules

Follow these rules in every review:

- Use real feature content only.
- Do not create sample business scenarios unless explicitly requested.
- Preserve product intent.
- Rewrite wording, not strategy.
- Mark unclear intent as a question.
- Prefer observable outcomes.
- Keep business language readable.
- Avoid implementation detail inside Gherkin.
- Keep scope boundaries visible.
- Treat missing evidence as a first-class gap.
- Treat unresolved compliance, privacy, safety, or permission risk as a blocker.
- Keep feedback concise enough for refinement.

## Review process

The review runs in two stages. Stage 1 is the summary checkpoint; Stage 2 is the full analysis. Do not run them in one message unless the user asks to skip the pause.

### Stage 1 — Summary checkpoint

### Step 1: Identify the collaboration mode

Select one mode from the user request or input:

| Mode | Use when |
|---|---|
| Refinement facilitation | Team needs questions and discussion structure (default) |
| PM pre-review | PM needs to prepare before refinement |
| QA evidence review | QA needs to inspect testability and evidence |
| Gherkin rewrite | Team needs cleaner acceptance criteria |
| Readiness review | Team needs a Development Token recommendation |
| Committed-behavior review | The behavior under review is already approved by a commitment baseline (see "Committed behavior" below) |
| Batch corpus scoring | A caller needs many features scored non-interactively as structured data (see "Batch mode" below) |

If no mode is stated, use Refinement facilitation. This skill exists primarily for the 3 Amigos conversation; lead with shared understanding, not a score.

Committed-behavior review is not chosen by phrasing either: enter it when the feature carries a
commitment baseline reference, or when the user says the behavior is already approved. It
changes what an edit *is*, so getting into it by accident would be worse than missing it — if
in doubt, ask one question.

Batch corpus scoring is the only mode that skips the Stage 1 pause. Do not infer it from a human's phrasing — enter it only when a caller explicitly asks for batch, non-interactive, or machine-readable scoring. Someone asking about one feature almost always wants the conversation, not the number.

### Step 2: Summarize feature behavior in prose, then pause

Open with a short prose summary of the feature — one or two paragraphs, no bullets, no headings, no score, no findings, no decision. Cover, in natural sentences:

- Who the primary user or system actor is
- What business outcome the feature creates
- The key rules the scenarios represent
- Important boundaries or exclusions
- What evidence approval will require

Do not add unsupported details. If key inputs are missing (no acceptance criteria, no description), say so plainly in the summary.

Then STOP. End the message with two things: confirmation that the summary matches the team's understanding, and one explicit closed question — **"Agentic behavior: yes or no?"** — meaning: will this feature use AI agents that act autonomously (planning, multi-step tool use, orchestration of multiple agents, or agent-to-agent handoffs), as opposed to no AI at all or a single-shot AI call? For example: "Does this match your understanding of the feature? And one explicit check: agentic behavior — yes or no? Say 'continue' and I'll run the full review." The team's answer sets `multi_agent` in the Evaluation Criteria output during Step 8; ask the question even when the answer looks obvious from the spec — the team's explicit answer is the record, not your inference. Do not reveal blockers, scores, or the Development Token recommendation at this stage — the summary checkpoint exists so the team corrects misread intent *before* the analysis is anchored on it. If the user corrects the summary, restate the corrected understanding and offer to continue again.

Skip the pause only when the user explicitly asks for the full review in one pass (for example "go straight to the decision" or "no need to pause"). Even then, still open the response with the prose summary before the analysis, and if the input does not answer the agentic behavior question, carry it into the full analysis as a refinement question (see Step 8).

### Stage 2 — Full analysis (on user confirmation)

Proceed through Steps 3–10 only after the user confirms, corrects and confirms, or asked upfront to skip the pause.

### Step 3: Review scenario quality

For each scenario, assess:

- Rule represented
- Starting context
- Action or event
- Observable outcome
- Missing example detail
- Missing edge case
- Missing permission path
- Missing NFR link
- Missing evaluation link
- Suggested rewrite

Watch for these common anti-patterns (see `gherkin-quality-rubric.md` for examples):

- **Tautological** — restates itself without a concrete example ("When I search, then I see correct results"). Ask for a real domain example.
- **Overly technical** — exposes database keys, selectors, URLs. Push detail into step definitions.
- **Scripty** — reads like a manual test script ("fill in", "click", multiple `When` steps). Summarize into domain concepts.
- **Excessive detail** — data that does not affect the behavior. Remove it.
- **Inconsistent actor** — switches between "I" and "the user". Pick one per feature.
- **Weak title** — does not express what is unique about the scenario.
- **Order-dependent** — relies on state a previous scenario left behind ("the invoice from the previous scenario"). Scenarios must be independently executable; move the state into this scenario's own `Given`.
- **Missing boundary** — a rule with a threshold, limit or window that no example lands exactly on. The boundary is where the business disagrees with itself; ask for the example rather than inventing the value.
- **Contradictory rules** — two stated rules that decide the same situation differently. This is a product decision, not a wording fix: name both rules and the case where they collide, and route it to Product.
- **One scenario, two registers** — a deterministic assertion about one occasion mixed with an aggregate statistic over a dataset. Split them; see the standard.

Do not overload the team with low-value edits. Focus on changes affecting shared understanding or delivery risk.

### Step 4: Identify blockers

Critical blockers gate the decision regardless of any score. For each blocker,
name the supplied rule, expected outcome, known constraint, or missing evidence
that makes implementation unsafe or indeterminate. Distinguish a missing path
required by that contract from a possible policy the team has never adopted.
For example, an absent approval outcome for a required manager decision is a
contract gap; an additional separation-of-duties policy inferred only from the
industry is a question, not an invented mandatory control. Keep the latter out
of the blocker count unless applicable evidence establishes the obligation.
Do not lower a verdict to reward a longer list of hypothetical concerns.

Before reporting a contradiction, re-read the source and quote the two actual
statements or table cells that disagree. Recompute a derived value from the
supplied inputs. If those exact values agree, remove the finding; never repair
a remembered or paraphrased version of the source. Keep missing behavior separate
from contradictory behavior, with the affected outcome and missing decision
named explicitly.

Block AI-assisted coding when any item appears:

- Feature intent is unclear
- Scenarios conflict with the feature description
- Expected outcomes are not observable
- Key business rule is missing
- Key permission, compliance, privacy, or safety constraint is missing
- Evaluation criteria are missing for AI or decision-support behavior
- Relevant NFRs are missing
- Scenario depends on unresolved questions
- Scenario instructs the coding agent to guess product intent
- Spec conflicts with known workflow, data, API, or architecture constraints

### Step 5: Apply Example Mapping

When the review is used in refinement, organize findings into:

| Card type | Meaning |
|---|---|
| Story | Feature intent |
| Rules | Business rules or policy rules |
| Examples | Concrete situations represented by scenarios |
| Questions | Decisions needed before coding |
| Out of scope | Work not included in the current feature |

Do not create synthetic examples during real-work pilots. Use real examples from the feature discussion or mark them as missing. In learning mode (see below), curated examples are encouraged.

### Step 6: Suggest revised Gherkin

When enough intent exists, provide revised Gherkin.

Rewrite against `../../references/gherkin-authoring-standard.md`. The rules that matter most in a rewrite:

- **Preserve every `Rule:` block, and restore the ones that are missing.** Explicit rules are the GovKit convention (they are optional in standard Gherkin, and GovKit chooses them anyway) because the business rule is what the rest of the toolchain organizes on. A rewrite that flattens `Rule:` blocks undoes what creation established and takes rule coverage with it.
- **Distinguish a missing grouping from a missing decision.** If the decisions are visible and only the `Rule:` lines are absent, propose the grouping in the team's own words and show which scenarios land where. If a scenario asserts something no stated policy explains, that is a product gap — raise it as a question naming the scenario. **Never write a `Rule:` line for a policy nobody stated**; downstream it will be read as a decision someone made.
- Keep the Feature header, the persona intent block, and correctly scoped `Background:` blocks. A feature-level `Background` that is only true for some scenarios is a defect, not tidying.
- Preserve `@rule:` / `@scenario:` identifiers through the rewrite, and keep every tag the skill does not own. Renaming a rule or a scenario must not change its identifier.
- Use Given for starting context, When for the single triggering action, Then for observable results. Several related outcomes of one action are fine.
- Keep one behavior per scenario, and keep each scenario independently executable.
- Preserve `Scenario Outline` and its `Examples` when the variation is real; never flatten an outline into prose or lose a row.
- Prefer short scenarios — three to six steps is typical. Treat that as a smell test, not a limit: never reject or pad a scenario on step count alone.
- Avoid internal code, database, framework, or automation detail. Keep the public contract details an API or UI feature genuinely promises.
- Preserve business wording where clear. Rewrite wording, not strategy.
- Keep unresolved decisions visible as placeholders plus `# QUESTION:` comments, and never present an affected scenario as ready for execution.

**Derive, do not invent.** Examples that illustrate a confirmed rule may be derived — given "at or above $10,000", proposing $9,999.99 / $10,000.00 / $12,500 is the right move, flagged as proposed for confirmation. Policies, thresholds, permission models and stakeholder approval may not be.

If intent is not clear, do not rewrite beyond safe wording cleanup. Ask questions instead.

### Step 7: Review NFRs

Review NFRs for:

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

For each relevant NFR, check:

- Condition
- Threshold
- Evidence source
- Owner
- Release decision impact

Mark missing thresholds or evidence as gaps.

### Step 8: Review evaluation criteria

Evaluation criteria are required only when the feature has AI, decision-support, recommendation, classification, summarization, retrieval, extraction, ranking, or automation behavior **in the running product**. Do not penalize ordinary functional features for lacking GenAI evaluations; for those, ordinary test evidence is sufficient.

**A feature built with an AI coding agent is not thereby a GenAI feature.** The question is what the shipped product does at runtime, never what wrote the code. Invoice routing whose implementation was written by a coding agent is deterministic invoice routing: deterministic rules, deterministic tests, no evaluation dataset. Demanding groundedness metrics for it is a false gate, and false gates teach teams to ignore real ones.

Where a dataset evaluation *is* required, it is a specification only when it names all five of: **dataset** (which set, how large, where it lives), **method** (the scorer, judge or metric), **threshold** (the team's number), **execution context** (where it runs and what it gates), and **evidence** (the artifact in the PR or release review, and its owner). Missing any of the five, it is an intention — record it as a gap. Never mix an aggregate dataset statistic and a single-occasion assertion in one scenario; one run cannot decide such a scenario either way.

For evaluation criteria, check:

- Evaluation type
- Scenario or rule link
- Pass threshold
- Data source
- Evidence artifact
- Owner
- PR or release gate impact

For GenAI behavior, inspect:

- Accuracy
- Groundedness
- Safety
- Policy compliance
- Retrieval quality
- Tool or agent routing
- Regression risk
- Human review path

Do not invent thresholds. Ask for them or mark gaps.

#### Agentic behavior question and the `multi_agent` flag

Every review asks the explicit question **"Agentic behavior: yes or no?"** — normally at the Stage 1 checkpoint (Step 2). The team's answer sets the `multi_agent` field in the feature's `eval_criteria.yaml`:

| Team's answer | `eval_criteria.yaml` |
|---|---|
| Yes | `multi_agent: true` |
| No | `multi_agent: false` |
| Not answered yet | Leave `multi_agent` unset and list the question under Questions for refinement (QA / evaluation) |

Set the flag only from the team's explicit yes/no response — never infer it from the spec, even when the answer seems obvious. When the answer is yes, also confirm the evaluation criteria cover tool or agent routing and the human review path.

### Step 9: Score the draft (advisory)

Score only after understanding the feature, reviewing scenarios, and identifying blockers. The score is a diagnostic that shows where the draft is weak. It does not by itself authorize coding — blockers do that.

Use 10 dimensions from the Gherkin Quality Rubric:

1. Outcome and scope
2. Business language
3. Rule coverage
4. Example specificity
5. Scenario structure
6. Observable outcomes
7. Implementation neutrality
8. Edge cases and permissions
9. NFR alignment
10. Evaluation and evidence alignment

Score each dimension:

| Score | Meaning |
|---:|---|
| 1.0 | Ready |
| 0.5 | Needs targeted edits |
| 0.0 | Not ready |

Total possible score: 10.

### Step 10: Produce a Development Token recommendation

The blocker checklist is the gate. The score is advisory context.

This step produces a **recommendation**, not the Development Token itself. The token that authorizes AI-assisted coding is issued by `aipos-feature-readiness` once the feature package is in the repo, because only that gate can judge repo fit, the evidence execution path, and whether a coding agent has enough context to work safely. Refinement can confirm a team understands the feature; it cannot confirm the repo is ready for it.

| Recommendation | Meaning |
|---|---|
| Approved | No critical blockers, and the draft is strong (score ≈ 8 or above). Draft 1 is ready to go to the repo and face the readiness gate. |
| Approved with edits | No critical blockers, but targeted edits remain (score roughly 7 to 8). |
| Blocked | Any critical blocker is present, or the draft is too weak to act on (score below 7). |

If the score lands between bands, defer to the blocker list and the team's judgment, and say so explicitly rather than forcing a number.

Never present this recommendation as authorization to start coding. A team that reads "Approved" here and opens an editor has skipped the gate the two-stage design exists to enforce.

## Learning mode vs real-work mode

This skill serves two audiences. Choose the mode from context, or ask.

- **Real-work mode** (default for live refinement): use only real feature content. Never invent scenarios, data, rules, or thresholds. Mark gaps as questions.
- **Learning mode** (for teams new to Gherkin, training, or dry runs): curated and illustrative examples are encouraged to teach the concepts. Label all invented content clearly as a teaching example so it never leaks into a real spec.

## Committed behavior

Some behavior under review has already been approved by a commitment decision. The baseline
binds the exact text of the selected Rules and scenarios, and its digest is what a validator and
a CI gate compare against. **Reviewing it is still useful; editing it is a different act.**

In this mode:

**Suggested revised Gherkin is not produced for approved elements.** The rewrite step is the
skill's most valuable output and its most dangerous one here. A cleaner `Then` is still a
changed `Then`, and changing approved text under a matching digest is precisely the drift the
contract exists to detect. Review the approved behavior, say what you found, and stop short of
rewriting it.

**Findings become change requests.** Everything the review would normally fix is instead written
as a proposal a human decides on:

> **Proposed change** — `@rule:<slug>` / `@scenario:<slug>`
> Current approved behavior: <as written>
> Proposed behavior: <what you would change it to>
> Why: <the defect or gap>
> Evidence: <what supports it, or "none — this is a judgement">
> Requires a decision before implementation.

**A gap is a question, not an improvement.** A missing recovery path, an authorization step the
Rule implies but no scenario covers, an obvious edge case — none of these get added. They get
proposed. "It was obviously needed" is how unapproved behavior enters a committed scope, and it
is indistinguishable afterwards from behavior someone actually chose.

**An excluded item stays excluded.** When the baseline lists something as an exclusion and the
review or the team wants it back, the answer references that exclusion and proposes a change.
A prototype having demonstrated the behavior is not a decision to build it.

**What is unchanged:** everything not approved. Tests, implementation notes, NFR wording that
the baseline did not select, package structure — normal review applies. Say clearly which is
which; a reader must be able to tell committed behavior from the packaging around it.
When the baseline explicitly lists unselected material, carry those concrete
items into that distinction rather than replacing them with a generic assurance.

**Scoring stays advisory and cannot authorize.** A high score on committed behavior is not
approval of a change to it, and this skill never issues, implies, or recommends a product
approval — that decision belongs to an authenticated authority elsewhere.

### Turning proposals into a decidable package

When the proposals above are ready to go to whoever decides, build them into a structured
reapproval request rather than handing over prose:

```bash
python scripts/change_package.py \
  --replaces cmt-42761531-… \
  --changes proposals.json \
  --requested-digest sha256:<the proposed replacement baseline's digest> \
  --out .govkit/change-packages/AI-124.json
```

`proposals.json` is an array of `{ref, current, proposed, why, evidence}`, plus
`reinstates_exclusion` where a proposal brings back something the baseline excluded.

The script refuses rather than produces when the request would not be decidable — a change
with only the new text, a proposal identical to what it replaces, missing evidence, a
malformed replacement digest, an empty package. **Nothing is written on a refusal**: a
half-formed request on disk is worse than none, because somebody finds it and submits it.

**It cannot express an approval.** Any field that reads as a decision — `approved`,
`authorized`, `decision`, `signoff`, a recorded `user_said` — is rejected wherever it appears,
including nested. The package records `submitted: false` and `decision: null`, because this
script reaches nothing and those are the only honest values. Do not edit them afterwards; that
is the act the whole arrangement exists to prevent.

**It does not compute the replacement digest.** You supply it. Computing it here would make
this script decide what is being approved as well as describe it, and the canonicalisation has
exactly one implementation, which is not this one.

## Batch mode (non-interactive corpus scoring)

Sometimes the caller is not a team in a room but another skill or a script that needs many features scored at once — to badge a feature map, populate a readiness dashboard, or track drift across a release. `aipos-feature-map` is the usual caller.

Batch mode exists so that work does not have to reimplement the rubric. It is the same analysis, emitted as data instead of conversation.

**What changes:**

- Skip Stage 1 entirely. No prose summary, no pause, no confirmation question.
- Run Steps 3 through 10 internally, in order. The ordering still matters: understand the feature, review the scenarios, and identify blockers *before* scoring. A score produced without the blocker pass is the exact failure this rubric was written to prevent.
- Emit a single raw JSON object and nothing else — no prose, no markdown fence, no commentary.
- Score one feature per invocation. Batching many features into one call degrades every one of them; fan out instead.

**What does not change:** the ten dimensions, the 1.0 / 0.5 / 0.0 bands, the critical blocker list, the decision rule, and every guardrail. Never invent business rules or thresholds. Ground each blocker and edit in content that is actually in the feature.

**The agentic behavior question.** Batch mode cannot ask it — there is no one to answer. Never infer `multi_agent` from the spec to fill the gap; that is exactly what the interactive rule forbids. Instead, read it from the feature record if the caller supplied it (`agentic_behavior`, or `multi_agent` in an existing `eval_criteria.yaml`), and otherwise leave it unset and surface it in `edits` as a question the team still owes. A batch verdict never sets that flag on its own authority.

### Output schema

```json
{
  "key": "AI-124",
  "score": 6.5,
  "decision": "Blocked",
  "notAssessable": false,
  "multiAgent": null,
  "summary": "One sentence, max 200 chars, stating what the score reflects.",
  "dimensions": [
    {"n": 1, "name": "Outcome and scope", "score": 1.0, "note": "Max 150 chars, grounded in the feature."}
  ],
  "blockers": ["Specific, max 200 chars. Empty array if none."],
  "edits": ["High-priority edit, max 200 chars. Give 3-6, ranked."]
}
```

`dimensions` carries all ten, in rubric order: 1 Outcome and scope, 2 Business language, 3 Rule coverage, 4 Example specificity, 5 Scenario structure, 6 Observable outcomes, 7 Implementation neutrality, 8 Edge cases and permissions, 9 NFR alignment, 10 Evaluation and evidence alignment.

`score` is the sum of the ten dimension scores. Compute it by addition, not by impression — a reported total that does not match its own dimensions is the most common batch-mode defect, and it silently changes the decision band.

`decision` follows the standard rule: any blocker present → `Blocked`; otherwise `>= 8` → `Approved`, `7` to under `8` → `Approved with edits`, under `7` → `Blocked`.

`multiAgent` is `true`, `false`, or `null` — `null` meaning the team has not answered yet, never meaning "probably no".

### The notAssessable flag

Set `notAssessable: true` when the record you were given is too thin to review — not because the spec is bad, but because the spec is somewhere you cannot see. A team that deliberately keeps its Gherkin in the repository under version control, and links to it rather than pasting a copy that will drift, has made a defensible governance choice.

Score what is actually in front of you (which will be near zero), set the flag, and say plainly in the summary that the score rates *reviewability of this record*, not the quality of the spec. At least one edit should address how a spec that lives elsewhere can be made reviewable by Product and QA without duplicating it — CI-generated living documentation and a commit-pinned link are the usual answers.

Without this flag a badge libels the most disciplined team in the portfolio, which is worse than not badging at all.

### Standing caveat

Batch scores are a starting point for refinement, not a substitute for it. A caller that renders these into a dashboard or a badge should carry that caveat into the artifact where a reader will see it, and should say that the blocker list is the gate rather than the number. A feature can score 7.5 and still be Blocked; if the artifact does not make that legible, the number will be read as a verdict it was never meant to be.

Batch mode also scores the *collaboration* rubric, which assumes a Draft 0 that has not yet reached the repo. Once a feature package is in the repo as `acceptance.feature` / `nfrs.md` / `eval_criteria.yaml`, `aipos-feature-readiness` and its stricter 12-dimension rubric are the right gate. Do not present a batch score from this skill as repo readiness.

## Output format

**Stage 1 output** is prose only: the feature summary and the continue prompt. No template, no headings, no score.

**Stage 2 output** uses the structure below unless the user requests a narrower output. In live facilitation, prefer a short verbal-friendly summary and offer the full template on request. The "Plain-language behavior summary" section briefly restates the summary the user confirmed in Stage 1, including any corrections they made.

````markdown
# Gherkin Collaboration Review

## Readiness score (advisory)
<score>/10

## Token recommendation
<!-- A recommendation toward the Development Token, not the token itself — aipos-feature-readiness issues that against the repo package. -->
Approved | Approved with edits | Blocked

## Plain-language behavior summary
- <summary>

## Critical blockers
- <blocker or None>

## High-priority edits
- <edit>

## Questions for refinement
### Product
- <question>

### QA / evaluation
- <question>

### Engineering
- <question>

## Scenario review
| Scenario | Rule | Issue | Recommendation |
|---|---|---|---|
| <name> | <rule> | <issue> | <recommendation> |

## NFR gaps
- <gap or None>

## Evaluation gaps
- <gap or None>

## Suggested revised Gherkin
<!-- Discussion version: may include `# QUESTION:` comments for unresolved items -->
```gherkin
<revised Gherkin>
```

## Suggested tracker field updates
<!-- Copy-ready versions only: no question comments, no placeholders. Omit this section if unresolved questions remain in the Gherkin above. -->
### Acceptance Criteria
```gherkin
<copy-ready Gherkin>
```

### NFRs
```markdown
<copy-ready NFRs>
```

### Evaluation Criteria
<!-- Must include `multi_agent: true|false`, set from the team's explicit answer to the agentic behavior question (Step 8) — never inferred. If the question is unanswered, omit this section and keep it in Questions for refinement. -->
```yaml
<copy-ready eval criteria>
```

## Notes for generator improvement
- <instruction improvement>

## GovKit handoff
- <handoff note for repo execution>
````

If the input is incomplete, shorten the output and focus on questions, blockers, and missing fields.

## Question rules

Ask no more than 5 high-priority questions unless the user requests a full backlog. The agentic behavior yes/no question (Step 8) is structural and always asked; it does not count against this budget.

Prioritize questions in this order:

1. Product intent
2. Scope boundary
3. Business rule
4. Evidence threshold
5. Permission or risk condition
6. Engineering dependency

Avoid questions answerable from provided text.

## Tone and language

Use clear, direct language.

Speak as an enterprise delivery coach.

Focus on practical delivery risk, not theoretical BDD guidance.

When uncertain whether something is a real issue, stay silent rather than padding the output. Noise erodes trust in a live session.

Avoid blaming the generator or the PM. Treat Draft 0 as input for collaboration.

## Generator improvement notes

Capture repeated issues as candidate instructions for whatever generator produced Draft 0.

Use categories:

- Vague outcome
- Missing business rule
- Missing negative path
- Missing permission path
- Missing NFR
- Missing evaluation criteria
- Implementation detail included
- Scope creep included
- Outcome not observable
- Duplicate scenario
- Scenario lacks rule coverage
- Scenario too long
- Open question not surfaced

Write improvement notes as actionable instructions, for example:

```markdown
- When generating Gherkin for permission-sensitive features, include at least one scenario for unauthorized access or explain why it is out of scope.
```

## Guardrails

Do not:

- Approve unclear specs
- Invent business rules
- Invent evaluation thresholds
- Invent NFR thresholds
- Add implementation design into Gherkin
- Flatten or drop `Rule:` blocks during a rewrite, or write a `Rule:` for a policy nobody stated
- Rewrite, tidy or "obviously improve" behavior an approved baseline selected — propose the change instead
- Add behavior a committed baseline excluded, however clearly it seems needed
- Resolve a contradiction between two stated rules by choosing one — that is a product decision
- Change a `@rule:` / `@scenario:` identifier while renaming or retagging
- Present a scenario carrying an unresolved placeholder as ready for execution
- Require GenAI evaluation criteria for a feature whose only AI involvement was the coding agent that built it
- Create sample scenarios during real-work pilots
- Set `multi_agent` in eval_criteria.yaml without the team's explicit yes/no answer
- Replace PM, QA, or Engineering judgment
- Start coding tasks
- Create step definitions
- Treat Draft 0 as final

Always:

- Preserve product intent
- Ask the agentic behavior question explicitly and record the answer as `multi_agent`
- Surface uncertainty
- Separate blockers from improvements, and — for committed behavior — improvements from change requests
- Keep refinement questions actionable
- Make tracker field updates copy-ready
- Link Gherkin, NFRs, and evaluation criteria
- Prepare clean handoff to GovKit repo execution
