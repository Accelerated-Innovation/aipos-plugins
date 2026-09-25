# `aipos-map-render` journey diagram evaluation — 2026-09-25

Follow-up to PR #39 (interactive L1/L2/L3 journey diagrams, merged as `c6857a4`), which
changed `aipos-map-render`'s description and SKILL.md without running model-graded evals or
live routing. This record covers both, and the new cases they needed.

## New cases

The skill's two existing eval cases tested only rubric choice; nothing exercised the journey
diagram. Added:

| Kind | Case | Tests |
|---|---|---|
| Skill eval | `journey-impact-across-two-workflows` | One ingest, one resolve per workflow, one render with `-w` per journey; reports both answers only after the render; no invented results |
| Skill eval | `rule-reference-does-not-place-its-scenarios` | A scenario under a referenced Rule is not counted as specifying the journey; placement goes through `aipos-workflow-create` |
| Skill eval | `no-workflow-source-yet` | Hands workflow authoring to `aipos-workflow-create` instead of drafting one |
| Routing (development) | `journey-feature-impact`, `journey-specifying-scenarios` | Journey questions route to `aipos-map-render` |
| Routing (development) | `journey-diagram-no-source` | A diagram request with no workflow routes to `aipos-workflow-create`, handing off to `aipos-map-render` |
| Routing (held-out) | `journey-impact-heldout` | Paraphrase of the impact question |

## Skill evals

Subject `claude-opus-5`, judge `claude-sonnet-5`, default 16,000-token budgets.

| Run | Skill text | Result |
|---|---|---|
| 1 | As merged in PR #39 | **3/5**. Failed `rule-reference-does-not-place-its-scenarios` (0.75) and `journey-impact-across-two-workflows` (0.86) |
| 2 | + placement and post-render guidance | **4/5**. `journey-impact-across-two-workflows` (0.86) |
| 3 | + how readers get the answers from the page | **15/15** (5 cases × 3 repetitions) |

The failures were skill gaps, not rubric harshness, so the fix went into SKILL.md and the
rubrics were not loosened:

1. The rule-reference answer was correct but left the fix unowned. SKILL.md never said a
   missing scenario reference is added through `aipos-workflow-create`.
2. Asked only to *describe* its plan, the subject presented concrete impact results, using
   identifiers from the worked example in `workflow-source.md` (part of the skill package).
   SKILL.md told it to answer both journey questions when presenting the map, but not that the
   answers exist only after the render. The case deliberately keeps the example's feature key.
3. After (2) was fixed, the plan committed to naming the affected journeys but not to telling
   readers how to get the same answer from the page, which outlives the conversation.

## Routing

`claude-opus-5`, descriptions from `SKILL.md` frontmatter (unchanged by the skill-body edits
above).

| Split | Calls | Result |
|---|---|---|
| Development (64 cases × 3) | 192 | **192/192**, no critical failures — accepted |
| Held-out (12 cases × 3) | 36 | **36/36**, no critical failures — accepted |

The held-out run first stopped at a 12-call cap (the runner's default is 3 repetitions) and
was resumed with a 36-call cap; the 12 completed results were reused, not re-run.

## Not covered

Text-only evals grade what the subject says it will do. They do not show that a real render
happened or that the diagram draws; that is covered by the deterministic tests and the
browser checks recorded in PR #39. Raw results and traces are in `.claude/hillclimb/` and
`.claude/routing/`, which are gitignored.
