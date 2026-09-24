---
name: aipos-feature-readiness
description: "Check whether a reviewed repository feature package is ready for AI-assisted implementation and produce its Development Token record. Use for pre-coding checks, repo fit, verification paths, and token requests. Verify applicable existing product approval; this skill does not grant that approval."
---

# GovKit Feature-Readiness Skill

## Purpose

Decide whether an approved feature package is ready for GovKit repo execution and AI-assisted coding.

This skill is stricter than the GovKit Gherkin Feature Refine skill. Collaboration improves shared understanding during refinement. Readiness validates that the feature package is complete, internally consistent, repo-aware, and safe for a coding agent to execute without guessing.

Use this skill to:

- Validate a feature package copied into the repo
- Check Gherkin, NFRs, and evaluation criteria against the readiness rubric
- Confirm repo fit, evidence path, and AI coding agent safety
- Identify critical blockers before coding starts
- Produce a readiness report and Development Token decision

## Tool-agnostic design

This skill runs regardless of the tools a team uses. It uses two abstract roles:

| Role | What it means | Examples |
|---|---|---|
| **Generator** | Whatever produced Draft 0 | Aha! Feature Agent, an LLM prompt, a human author |
| **Tracker** | Wherever the feature fields live | Azure DevOps, Jira, Linear, a markdown file |

Aha! and Azure DevOps appear only as named examples. Substitute your own generator and tracker freely.

## Key terms

- **Draft 0** — the generator's raw output, before human review.
- **Draft 1** — the version Product, QA, and Engineering approved together during refinement (the input to this skill).
- **Feature package** — the set of repo files that carry Draft 1 into execution (see below).
- **Development Token** — GovKit's name for the explicit go/no-go decision that authorizes AI-assisted coding to start. *Approved*, *Approved with edits*, or *Blocked*. No token, no coding.

## Operating principle

The generator creates Draft 0.

Refinement approves Draft 1.

GovKit validates repo readiness.

AI-assisted coding starts only after the feature package passes this readiness gate.

## Scope

Use this skill for repo-side readiness validation after collaboration review is complete.

Confirm the review state from available evidence. A package being stored in a
repository does not mean it has completed refinement. If it is an unreviewed
Draft 0, route its quality review to `aipos-feature-refine` before issuing a
token. A batch assessment can expose readiness gaps but cannot invent the missing
review or write a token. Where the requested decision is unclear, distinguish
spec review, repo readiness, and metric completeness before choosing the gate.

Use it for:

- Approved feature packages copied into the repo
- Pre-coding readiness checks
- AI coding agent handoff reviews
- PR preparation checks
- Development Token decisions

Do not use it for:

- Improving shared understanding during refinement (use the refine skill)
- Writing implementation code or step definitions
- Inventing product intent, rules, NFR thresholds, or evaluation thresholds
- Rewriting architecture to fit the feature
- Replacing human approval for risk-sensitive decisions

## Inputs

Inspect the feature package and supporting repo context.

Expected feature package:

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

`architecture_preflight.md` and `plan.md` are produced **later**, by the GovKit platform process, after the token — they are not expected at this gate, and their absence here is normal, not a gap. (Consequence for metrics: `aipos-metrics-emit`'s completeness score weights `plan.md` heavily, so a fresh post-token package scoring well under 100 there is the expected lifecycle stage, not a defect.) When they do exist — a re-validation of an in-flight feature — read them.

Also inspect, when available: repo architecture docs, existing tests, existing step definitions, GovKit config, and the CI pipeline. If an input is missing, record the gap and decide whether it blocks implementation.

## Required references

| Reference | Use |
|---|---|
| `references/govkit-readiness-rubric.md` | The 12 scoring dimensions, the critical blocker list, the Development Token rules, and the required readiness report format — including the scenario verification plan. |
| `../../references/gherkin-authoring-standard.md` | The shared Gherkin authoring standard. Validate the behavior contract against it rather than against a private notion of good Gherkin. |
| `../../references/spec-identifiers.md` | The `@rule:` / `@scenario:` convention that connects rules, scenarios, NFRs, evaluations and evidence. |

If a reference is unavailable, continue from the guidance in this file and say which rules you are applying from memory.

## Readiness process

1. **Confirm package completeness.** Verify `acceptance.feature` exists; verify `nfrs.md` and `eval_criteria.yaml` exist where relevant; confirm source traceability back to the approved generator/tracker record.
2. **Validate the behavior contract.** Check Gherkin structure, behavior clarity, observable outcomes, and rule/edge-case coverage.
3. **Validate quality constraints.** Check NFRs for measurable thresholds, evidence, and owners. Check evaluation criteria only where AI, decision-support, or data behavior is present.
4. **Validate repo fit.** Confirm the spec aligns with architecture, existing tests, conventions, and that target areas are identifiable.
5. **Validate the evidence path, scenario by scenario.** For every scenario, establish a *credible* path — not a completed one. Fill the verification plan in the rubric's report format: what behavior and which rule it verifies; the existing tests and step definitions that relate to it and whose step language can be reused; the proposed additions; the right verification boundary (domain/service, API, UI, evaluation, or manual evidence with a stated justification for why automation is not appropriate); the fixtures, controlled time, isolation and dependency handling it needs; and the command and evidence artifact where those are known. Where something is not yet known, write "to be established" — a confident blank is worse than an admitted gap.

   **Keep three states apart.** *Ready to implement* is this gate. *Automated* happens during implementation. *Verified passing* happens after it. Missing step definitions and unwritten tests are the work the token authorizes, not a reason to withhold it; not knowing how a scenario could be verified at all is a blocker, because it means nobody has decided what done looks like. This gate runs nothing, so it never reports a test as passing.
6. **Check AI coding agent safety.** Confirm the agent has enough context, that open questions are resolved or deferred, and that the spec does not ask it to invent intent.
7. **Identify critical blockers.** The blocker list is the gate (see rubric).
8. **Score (advisory) and decide.** Produce the readiness report and Development Token decision.

## Five states, kept apart

A Development Token answers *may execution start*. Under a behavior contract
that is half the question; the other half — **is this exact scope approved,
and does that approval still hold** — lives in the decision service and
cannot be read from the repository at all.

Keep the source of that state explicit. A user's hypothetical, pasted example,
or earlier report is supplied context, not a fresh service read. Explain what
would follow from it without inventing a fetch, timestamp, or verification.
For an actual token, record the authoritative response and check time that
support the exact commitment/baseline binding before setting verified flags.
`scripts/readiness_state.py` consumes those observations; it does not fetch or
validate the authority service itself.

So the token is a **derived execution-readiness record that references the
product approval**, never a substitute for one. Five states, and they are
not a ladder:

| State | What it means | Where it comes from |
|---|---|---|
| **prepared** | a package exists; nobody has decided anything | the repo |
| **approved for exact scope** | a commitment binds *this* baseline | the decision service |
| **locally executable** | this gate finds no critical blockers | the repo |
| **authority verified** | a *fresh* read says the approval still holds | the decision service |
| **implementation verified** | the behavior was afterwards shown to work | test evidence, later |

*Locally executable* and *authority verified* are independent, and collapsing
them is the mistake this table exists to prevent: a clean package is ready to
run, which says nothing about whether anyone approved the behavior.

`scripts/readiness_state.py` derives all of this, and **writing the token
record is what running it does** — the safeguards below live in the script so
that following this skill executes them rather than reimplementing them by
hand:

```bash
python scripts/readiness_state.py \
  --feature-id AI-124 --score 10.5 --package-complete \
  --commitment cmt-42761531-… --binds-baseline \
  --authority verified --checked-at 2026-08-24T15:03:41Z \
  --out .govkit/tokens/AI-124.json
```

`--authority` is `verified`, `withdrawn` or `unknown`; `--no-contract` is a
project with no decision service; `--batch` scores without deciding and
writes nothing. Exit status is 0 for an approved token and non-zero
otherwise — **a blocked token is still written**, because it feeds the
blocked-token rate.

Two refusals are built into it and must not be worked around in prose:

- **A stale reading cannot produce an authoritative green.** A check from
  last week proves what was true last week, and an approval can be withdrawn
  in between. Past the freshness window the result is execution readiness
  only, and it says so.
- **Could-not-determine is neither approval nor rejection.** An unreachable
  decision service does not block preparation, and it does not produce a
  result a protected boundary would accept.

**If the project has no decision service**, which is most projects using
GovKit, nothing changes: the token is issued on local grounds exactly as
before, and simply never claims to carry a product approval.

## Decision model

The critical blocker list is the gate. The 12-dimension score is advisory context that shows where the package is weak; it does not by itself authorize coding.

| Decision | Meaning |
|---|---|
| Approved | No critical blockers, and the package is strong (score ≈ 10 of 12 or above). Ready for execution. |
| Approved with edits | No critical blockers, but targeted edits remain (score roughly 8.5 to <10). Fix before coding starts. |
| Blocked | Any critical blocker is present, or the package is too weak to act on (score below 8.5). |

If the score lands between bands, defer to the blocker list and state that explicitly rather than forcing a number.

## The token record — machine-readable exhaust

The Development Token is a governance decision, and decisions that live only in prose cannot feed metrics. After producing the readiness report, **write the decision as a structured record** at:

```text
.govkit/tokens/<feature-key>.json
```

```json
{
  "feature_id": "AI-124",
  "decision": "approved",
  "score": 10.5,
  "blockers": [],
  "draft_version": "draft-1",
  "ts": "2026-08-24T15:04:00Z",

  "kind": "execution_readiness",
  "authoritative": true,
  "states": ["approved_for_scope", "authority_verified", "locally_executable", "prepared"],
  "product_approval": {
    "commitment_id": "cmt-42761531-2198-4d8b-8776-6160f1c4dbcd",
    "verified_at": "2026-08-24T15:03:41Z"
  }
}
```

`kind` says what the record **is**, so it cannot be filed later as evidence
that somebody approved the behavior. `product_approval` names the decision
this token derives from and when that was read — a derived record that does
not say what it derives from is just an assertion. It is explicit `null`
where the project has no decision service: absent would read as "not
recorded yet", and null says the question was asked and there is no answer.

`decision`, `blockers` and the other original fields are unchanged.
They preserve the input contract for the reserved `refinement.token.issued` metric
event; the current emitter does not yet emit that event.

`decision` is `approved` | `approved_with_edits` | `blocked` — write it for **every** decision, including Blocked; a blocked token is exhaust too (it feeds the blocked-token rate). `blockers` carries the critical blocker list verbatim. This record supplies the planned input for `aipos-metrics-emit`'s reserved `refinement.token.issued` event. Emitting that event and computing its downstream metrics are separate future work.

Writing this file is part of issuing the decision, not a separate confirmation — it is repo-local, versioned, and exactly as reversible as any other file in the working tree. If a record for this feature already exists, the new decision supersedes it; keep the old one only if the team's conventions version them.

Batch mode (below) **never** writes a token record — batch verdicts are advisory scores for a corpus view, not decisions.

## Output format

Produce the readiness report defined in `references/govkit-readiness-rubric.md`. In short, it includes: work item, advisory score, decision, Development Token, critical blockers, required edits, spec package status, scenario readiness, the **scenario verification plan** (one row per scenario — behavior and rule verified, boundary, existing and proposed tests, fixtures and isolation, command, expected evidence, what is still to be established), NFR and evaluation readiness tables, repo fit, AI coding agent instructions, "do not assume" list, deferred items, and the next GovKit step.

Key rules and scenarios by their identifiers throughout, so the report keeps pointing at the same things after the next rewording. Use the authored `@rule:<slug>` / `@scenario:<slug>` where the package has one. Where it does not — identifiers are optional, per `../../references/spec-identifiers.md` — use the derived id `repo_ingest.py` records (`idSource: "derived"`, slugified from the name) and mark it `(derived)`, so the reader knows it is only as stable as the wording. Never write a tag the feature file does not contain, and never make adding identifiers a blocker.

## Batch mode (non-interactive corpus validation)

Sometimes the caller is not a team at the gate but another skill or script that needs many repo packages scored at once — `aipos-map-render` badging a repo-first corpus is the usual case. Same rules as `aipos-feature-refine`'s batch mode: it is the same analysis, emitted as data instead of conversation.

**What changes:**

- No conversation, no pauses. Run the readiness process internally, in order — package completeness and blockers *before* scoring.
- Emit a single raw JSON object and nothing else — no prose, no markdown fence.
- Score one feature package per invocation; fan out for a corpus.
- **Never write a token record and never claim to issue a token.** Batch verdicts are advisory badges; the token is an interactive decision at the gate.

**What does not change:** the 12 dimensions, the 1.0 / 0.5 / 0.0 bands, the critical blocker list, the decision rule, and every guardrail. Never invent content; ground every blocker in what is actually in the package.

### Batch output schema

```json
{
  "key": "AI-124",
  "score": 10.5,
  "decision": "Approved",
  "notAssessable": false,
  "summary": "One sentence, max 200 chars, stating what the score reflects.",
  "dimensions": [
    {"n": 1, "name": "Feature package completeness", "score": 1.0, "note": "Max 150 chars, grounded in the package."}
  ],
  "blockers": ["Specific, max 200 chars. Empty array if none."],
  "edits": ["High-priority edit, max 200 chars. Give 3-6, ranked."]
}
```

`dimensions` carries all twelve, in rubric order: 1 Feature package completeness, 2 Source traceability, 3 Gherkin syntax and structure, 4 Behavior clarity, 5 Observable outcomes, 6 Rule and edge-case coverage, 7 NFR readiness, 8 Evaluation criteria readiness, 9 Repo fit, 10 Test and evidence execution path, 11 AI coding agent safety, 12 Handoff quality.

`score` is the sum of the twelve dimension scores — compute by addition, never by impression. `decision` follows the standard rule: any blocker present → `Blocked`; otherwise ≥ 10 → `Approved`, 8.5 to under 10 → `Approved with edits`, under 8.5 → `Blocked`. Set `notAssessable: true` when the package itself is unreachable from what you were given — score what is in front of you and say in the summary that the score rates reachability, not quality.

Callers verify these verdicts with `aipos-map-render`'s `verify_scores.py --scale readiness` before rendering anything from them.

## Failure handling

When blocked, do not rewrite the spec into an approved state. For each blocker, return: the blocker, the likely owner, the exact change needed, the file or field, and why coding should not start.

## Guardrails

Do not:

- Invent product intent, business rules, NFR thresholds, or evaluation thresholds
- Hide unresolved questions
- Start implementation when blocked
- Rewrite architecture to fit the spec
- Treat collaboration approval as repo readiness approval
- Require step definitions, written tests, or a passing run as a precondition for the token
- Report a scenario as automated or verified passing — this gate executes nothing
- Present a scenario carrying an unresolved placeholder as ready for execution
- Replace human approval for risk-sensitive decisions

Always:

- Validate the package as written
- Separate blockers from improvements
- Preserve traceability to the approved source
- Surface repo conflicts early
- Keep the Development Token decision explicit
- Give every scenario a verification plan row, with "to be established" where the path is genuinely unknown
- Produce a clean handoff for AI-assisted coding
