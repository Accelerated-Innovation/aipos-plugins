# AIPOS live evaluation — 2026-09-19

**Decision:** Catalog routing meets the proposed acceptance target. Coaching has unresolved failures, so the candidate remains a draft PR and is not signed off for release.

The final tested source is `a1e2522` (plugin content last changed in `f87a714`), including metrics/map corrections (`0554278`), routing grading (`3b13e62`), persistent slicing batch mode (`f6bb4ba`), streaming judge budgets (`8fb689b`), and workflow coverage grounding (`7b488de`, `f87a714`). Catalog descriptions did not change after `0554278`. These changes are in [PR #31](https://github.com/Accelerated-Innovation/govkit-plugins/pull/31). Baseline: `9ec174d9a9d740fddb928f7367cf6e635d637499`. Later evidence-only changes do not alter those inputs. The [machine-readable results](2026-09-19-aipos-live-results.json) retain per-repetition outcomes, missed claims, input fingerprints, and trace hashes.

## Routing

| Catalog | Development | Reserved paraphrases | All trials | Critical failures / missing |
|---|---:|---:|---:|---:|
| Baseline | 129/141 | 18/18 | 147/159 (92.5%) | 12 / 0 |
| Candidate | 141/141 | 18/18 | 159/159 (100.0%) | 0 / 0 |

Configuration: `claude-sonnet-5`, 53 cases, three repetitions, 4,096 output-token ceiling per call, identical evaluator instructions and case expectations after mapping skill identities. The evaluator sees the complete eleven-description catalog and the request; it does not see expected outcomes or skill bodies. The target is at least 90% overall and every critical case correct in every repetition. Baseline failures concern rendering existing source, journey-to-render handoff, prepared commitment ownership, and the assessment owner for reviewed packages.

The first live pass exposed ambiguous evaluator wording about internal delegated assessments. We clarified that a required assessment helper counts as a handoff, made feature-map's actual assessment owners explicit, and reran **both** catalogs under the same contract. We also corrected invalid skill selections being classified as infrastructure errors: the baseline's unknown skill is a failed selection. All saved responses were regraded deterministically, without rerolling failures; only the never-attempted repetition was newly executed. Original traces and error records remain intact.

The six reserved paraphrases were exercised before the evaluator correction and repeated afterward. They provide regression coverage; they are not a pristine, never-observed final holdout. This is a catalog-selection proxy on one model, not a universal claim about host routing.

## Installed-client selection

Claude Code **2.1.274**, `claude-sonnet-5`: **6/6** first-selection checks passed for creating a specification, reviewing an existing draft, checking readiness, rendering existing source, planning validation, and an unrelated arithmetic request. The last invoked no AIPOS skill.

The isolated configuration resolved `aipos@aipos` 1.0.0 to the local candidate source. The observed catalog contained **28 skills: eleven AIPOS and seventeen built-in competitors**; their exact names are in the results JSON. Only `Skill` and `Read` were enabled for these selection checks, with no MCP servers. These checks do not establish complete workflow execution or compatibility with every third-party plugin.

## Coaching

`claude-opus-5` subject, separate `claude-sonnet-5` judge, three repetitions per runnable case. Each conversation has two assistant turns separated by the user saying `proceed`; subject calls allow at most 16,000 output tokens. Judge calls use the same ceiling except the interactive-sizing and viability-brief cases, whose three repetitions use 32,000 after recorded judge truncations. The final variant is `live-acceptance`, except slicing uses `batch-contract-v2`, workflow authoring uses `coverage-evidence-v3`, and the two cases with increased judge budgets use `judge-32k`.

**87/135 trials passed every rubric claim with complete subject turns; 48 were not accepted.** All 45 runnable cases have three recorded grades. Four conversations contain a truncated subject turn and count as failures, including two whose judge verdict was favorable; the JSON keeps the raw judge verdict separately. These four need a larger subject budget before they can establish complete-conversation behavior. The three original metrics cases require a tool-enabled repository fixture and are skipped, not passes. No original rubric or fixture was relaxed to improve the aggregate.

| Skill | Passed / graded | Planned trials |
|---|---:|---:|
| `aipos-epic-create` | 6/12 | 12 |
| `aipos-feature-create` | 6/18 | 18 |
| `aipos-feature-map` | 6/6 | 6 |
| `aipos-feature-readiness` | 6/6 | 6 |
| `aipos-feature-refine` | 14/27 | 27 |
| `aipos-feature-slice` | 14/18 | 18 |
| `aipos-metrics-emit` | 3/3 | 3 |
| `aipos-quarterly-planning` | 3/3 | 3 |
| `aipos-rapid-validation` | 16/27 | 27 |
| `aipos-synthetic-data` | 6/6 | 6 |
| `aipos-workflow-map` | 7/9 | 9 |

The original judge request omitted fixture content and concatenated assistant answers without the user's intervening reply. That could mislabel supplied facts as inventions and legitimate continuation as failure to pause. The corrected judge sees the fixtures and chronological role boundaries. Subject conversations were reused only after their actual skill package, fixtures, model, turn count, and follow-ups matched; changed subjects ran afresh. Current grades, including failures, were reused without outcome-based selection. Old grades and conversations remain available separately. Do not compare the old and corrected judge aggregates as if only skill wording changed.

### Findings and next slices

1. **Evaluate complete interactions at the appropriate stage.** Epic and feature-authoring rubrics sometimes expect a completed artifact after two generic `proceed` replies, while required business facts remain unanswered. Add explicit case-specific user replies and stage expectations, preserving refusal to invent facts or authority. A text response is not proof of a file or tracker write.
2. **Repair conflicting fixtures without lowering safety expectations.** Both invoice fixtures omit the successful manager-approval outcome while their rubrics require approval with no blockers. Traces also raise possible overblocking around unstated self-approval policy; adjudicate these separately. The stock-adjustment fixture says a variance **above** 100 requires approval, but its exactly-100 example requires it too; its approval-only rubric incorrectly penalizes identifying that contradiction. The GenAI feature case requires inheriting a PII rule that the epic scopes to external sharing, while the feature excludes that workflow and the skill says to retain only applicable criteria. The interactive-sizing rubric also expects permission/error scenarios to be deferred and totals to be emitted, conflicting with the skill’s consequence-based controls and optional-total policy. Clarify applicability and retain the original threshold and provenance; do not train the skill to invent a stronger policy.
3. **Address demonstrated coaching misses in small batches.** Examples include release slices spanning only one journey stage, evidence omission, unnecessary metadata questions, copying opportunity rationale, fragmented write confirmations, and strict formatting requirements. The per-case results below preserve the actual failures. Retest all three repetitions of an affected case after a change, retaining earlier outcomes.
4. **Complete the remaining runtime evidence.** The original metrics fixture cases and positive live Product Definition Graph integration remain outside the text harness. No acceptance claim that depends on those integrations is made. Retain external approval and committed-baseline protections during follow-up work.

The metrics-versus-token and feature-map advisory-boundary failures found early in this run were fixed and rerun: **3/3 metrics** and **6/6 map** conversations passed under the final judge.

The first slicing pass also exposed batch replies wrapped in Markdown and a bare `proceed` switching to interactive arithmetic and write-back offers. We clarified persistent batch mode and reran all eighteen slicing trials with fresh subject conversations; the original run, including a judge-truncation error, is retained.

Workflow authoring also attached unsupported behavior to plausible journey steps and claimed full coverage in all three gap trials. We separated the corpus (what behavior exists) from the walkthrough (where it occurs) and required a supported placement; all nine workflow trials were rerun. The first clarification still allowed inferred placements into coverage (0/3 gap trials); the final clarification keeps proposed placements outside reference arrays until confirmed, followed by another complete nine-trial rerun: **7/9 passed**. All three gap responses leave the unsupported scenarios uncovered; remaining misses are a missing representative-to-agent handoff and overconfident placement of a gap in this journey rather than leaving that judgement to the user.

Judge truncation prevented three final-candidate conversations from being graded at 16,000 tokens. Both affected case families were evaluated with a 32,000-token streaming judge; completed subject conversations were reused, including failures, and unrecorded conversations required fresh subjects. The initial non-streaming recovery error and interrupted requests remain disclosed in the local logs. There is no matched baseline coaching run, so the remaining failures cannot be attributed to consolidation alone.

### Per-case outcomes

| Skill | Case | Passed / graded |
|---|---|---:|
| `aipos-epic-create` | `reframes-solution-shaped-problem` | 2/3 |
| `aipos-epic-create` | `consumes-viability-brief-and-preserves-provenance` | 0/3 |
| `aipos-epic-create` | `genai-thresholds-flagged-as-inherited-contract` | 1/3 |
| `aipos-epic-create` | `no-tracker-markdown-path-and-write-discipline` | 3/3 |
| `aipos-feature-create` | `epic-mode-maps-before-splitting` | 1/3 |
| `aipos-feature-create` | `stub-creation-requires-explicit-confirmation` | 1/3 |
| `aipos-feature-create` | `genai-feature-inherits-and-flags-missing-thresholds` | 0/3 |
| `aipos-feature-create` | `no-tracker-markdown-path-is-complete` | 0/3 |
| `aipos-feature-create` | `opportunity-mode-drafts-without-epic-story-or-estimate` | 1/3 |
| `aipos-feature-create` | `unknown-thresholds-and-unmeasured-claims-stay-unknown` | 3/3 |
| `aipos-feature-map` | `repo-draft-uses-refinement` | 3/3 |
| `aipos-feature-map` | `reviewed-package-uses-readiness` | 3/3 |
| `aipos-feature-readiness` | `draft-in-repo-is-not-reviewed` | 3/3 |
| `aipos-feature-readiness` | `local-readiness-is-not-product-approval` | 3/3 |
| `aipos-feature-refine` | `strong-spec-boundary-gap-surfaced` | 1/3 |
| `aipos-feature-refine` | `happy-path-only-blocked` | 3/3 |
| `aipos-feature-refine` | `ai-feature-missing-evals-blocked` | 3/3 |
| `aipos-feature-refine` | `summary-checkpoint-pauses` | 1/3 |
| `aipos-feature-refine` | `boundary-complete-spec-not-flagged-for-coverage` | 0/3 |
| `aipos-feature-refine` | `contradictory-rules-and-unresolved-threshold-blocked` | 3/3 |
| `aipos-feature-refine` | `scenario-dependency-and-ambiguous-outcome-flagged` | 2/3 |
| `aipos-feature-refine` | `agent-built-feature-is-not-a-genai-feature` | 0/3 |
| `aipos-feature-refine` | `approved-behavior-change-is-proposed-not-applied` | 1/3 |
| `aipos-feature-slice` | `interactive-sizing-recommends-and-pauses` | 0/3 |
| `aipos-feature-slice` | `large-mvp-critical-path-flagged` | 3/3 |
| `aipos-feature-slice` | `batch-mode-raw-json` | 3/3 |
| `aipos-feature-slice` | `first-slice-is-a-complete-journey-not-a-layer` | 2/3 |
| `aipos-feature-slice` | `required-authorization-cannot-be-deferred-as-an-exception-path` | 3/3 |
| `aipos-feature-slice` | `cross-feature-prerequisite-and-post-approval-retag-are-surfaced` | 3/3 |
| `aipos-metrics-emit` | `gate-readiness-audit` | skipped |
| `aipos-metrics-emit` | `aggregator-export` | skipped |
| `aipos-metrics-emit` | `org-agnostic-verification` | skipped |
| `aipos-metrics-emit` | `completeness-is-not-an-execution-token` | 3/3 |
| `aipos-quarterly-planning` | `no-live-graph-does-not-invent-planning` | 3/3 |
| `aipos-rapid-validation` | `mandate-declared-carries-the-ledger` | 1/3 |
| `aipos-rapid-validation` | `budget-exhausted-routes-to-the-brief-but-builds-what-is-asked` | 1/3 |
| `aipos-rapid-validation` | `no-mandate-is-legitimate-and-nothing-is-invented` | 0/3 |
| `aipos-rapid-validation` | `viability-brief-reconciles-the-mandate-and-closes-the-loop` | 0/3 |
| `aipos-rapid-validation` | `commitment-package-carries-the-exact-selected-behavior` | 3/3 |
| `aipos-rapid-validation` | `blocking-unknowns-prevent-ready-for-commitment` | 2/3 |
| `aipos-rapid-validation` | `prototype-behavior-does-not-enter-the-commitment` | 3/3 |
| `aipos-rapid-validation` | `unverified-claims-and-contradicting-evidence-are-recorded-not-resolved` | 3/3 |
| `aipos-rapid-validation` | `a-prepared-package-is-never-presented-as-approved` | 3/3 |
| `aipos-synthetic-data` | `schema-only-is-supported` | 3/3 |
| `aipos-synthetic-data` | `production-masking-is-outside-scope` | 3/3 |
| `aipos-workflow-map` | `journey-is-authored-from-the-existing-corpus-not-re-described` | 2/3 |
| `aipos-workflow-map` | `uncovered-behavior-is-reported-not-quietly-attached` | 2/3 |
| `aipos-workflow-map` | `only-consequential-gaps-are-asked-about` | 3/3 |

## Native workflows

Claude Code 2.1.274 with `claude-sonnet-5`, all eleven AIPOS skills available, four isolated projects. These were single native sessions with local Read/Write/Edit/Glob/Grep/Bash/Skill tools, no MCP servers, and no external writes.

| Workflow | Observed artifacts and boundary |
|---|---|
| Opportunity to prepared commitment | Wrote the six-scenario selection pinned to the supplied source revision, exclusions and evidence, plus a readiness note retaining blocking unknowns. Status stayed prepared, with no product approval. |
| Reviewed package to readiness | Inspected the incomplete fixture and wrote a report plus blocked token through the readiness script. The token has `authoritative: false` and `product_approval: null`; no passing tests were invented. |
| Existing journey to HTML | Ran ingestion, workflow resolution, and rendering; produced a 32,615-byte HTML map with five resolved behavior references, two uncovered-behavior warnings, and no token or assessment badges. Source files were unchanged. |
| Committed behavior to change proposal | Wrote a separate proposal and proposed Gherkin, ran the change-package script, and verified the requested digest against the proposed file bytes. `submitted` is false and `decision` is null; the committed source is unchanged. |

All four artifact checks passed, including before/after hashes for every supplied source file. This covers a deliberately **blocked** readiness package, not a successful live authority-service check. Rendering source was inspected, but browser visual QA was unavailable in the native session. The proposed-change digest is a real file digest; equivalence to an external baseline service's canonicalization was not asserted.

## Evidence and limits

- Routing snapshots, original responses, errors, and final summaries: `.claude/routing/live-{baseline,candidate}-v2/`.
- Coaching results and full traces: `.claude/hillclimb/<skill>/live-acceptance/`; earlier `consolidation`, `consolidation-v2`, and `conversation-judge-v2` runs are preserved where present.
- Native selection and workflow records: `/private/tmp/aipos-live-evals/`. Configuration and projects are disposable; real user installations were not changed.
- Full local suite: **415 passed, 5 skipped**. Both hosted PR checks passed at `a1e2522`; the hosted manifest check uses pinned Claude Code 2.1.199. `origin/main` remained at the recorded baseline when rechecked.
- Usage is retained in raw results, with reuse provenance. Interrupted in-flight requests may have billed without returning usage, so no precise total-spend claim is made.
- These manual model evaluations remain outside required offline CI. Passing scripts, selecting a skill, completing a coached conversation, and executing a full workflow are distinct evidence.
