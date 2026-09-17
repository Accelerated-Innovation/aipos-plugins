# AIPOS behavior contract — this repository's scope

Increment 00 record, 2026-09-17. **Design record, not an approval.**

The canonical cross-repository policy, ownership table, authority mapping and interface
decisions live in the AIPOS operating-model record
*AIPOS-Behavior-Contract-Repository-Contract.md*. This file holds only what this repository
decides. Peers: `plans/AIPOS_BEHAVIOR_CONTRACT_PLAN.md` in governed-ai-delivery, and
`ADR-AIG-029` in discovery-engine.

## What changes here, in one sentence

An opportunity from the Opportunity Engine — with no epic, no user story and no point estimate —
becomes a workflow map, a set of Rules and Gherkin scenarios, a selected release scope, and a
reproducible commitment package ready for a human decision.

## Increments owned here

| Increment | Deliverable | Main surfaces |
|---|---|---|
| 02 | **Done.** `references/workflow-source.md`, qualified refs + resolver behavior in `spec-identifiers.md`, `scripts/workflow_resolve.py`, L1/L2/L3 views, plugin-boundary enforcement | `plugins/govkit/references/`, `govkit-feature-map/scripts/`, `tests/` |
| 03 | Opportunity-centred draft authoring; approved-baseline materialization as an explicit mode | `govkit-feature-create`, `govkit-feature-refine`, `val-rapid-validation` routing |
| 04 | Scope selection separated from complexity diagnostics | `govkit-feature-slice`, slicing rubric, story-mapping reference |
| 05A | A proposed `aipos-workflow-map` authoring skill | Pillar 2 plugin surface, plugin metadata |
| 05B | L1 / L2 / L3 views beside the existing producer/consumer chain | `repo_ingest.py`, `render_map.py`, their references and tests |
| 06 | The Pillar 2 commitment package; the Gherkin prohibition replaced by progressive drafting | `val-rapid-validation`, `references/viability-brief.md` |
| 14 | Readiness, maps and change-review consuming the real validators and decision reads | `govkit-feature-readiness`, `govkit-feature-refine`, `govkit-feature-map`, `govkit-metrics-emit` |
| 15 | Plugin descriptions, README routes, installed dependency handling, evals, examples | all three plugins |

## Decisions taken now

**Identifiers are reused, not replaced.** `@rule:<slug>` and `@scenario:<slug>` stay exactly as
`references/spec-identifiers.md` defines them, including the stability rules for renaming,
retagging, splitting and merging. Cross-feature references add a namespace and nothing else:

```
<repository-or-package>/<feature-key>#rule:<slug>
<repository-or-package>/<feature-key>#scenario:<slug>
```

An authored ID (`idSource: "tag"`) is **required** in a new approved AIPOS baseline. A derived ID
(`idSource: "derived"`) stays readable, stays marked derived, and cannot be approved into one.
`repo_ingest.py` already records `idSource` per rule and per scenario, so the migration gate is
a field that exists rather than a new mechanism. Identifiers remain optional and additive for
every non-AIPOS package — a file with them and a file without both ingest, render, score and
slice identically, and that stays true.

**One canonical definition, generated views.** Rules and scenarios live in versioned
`acceptance.feature` artifacts. `workflow.json` **references** them; it never holds an editable
second copy. A Rule referenced at four workflow steps is authored once. Diagrams are projections
of the source, regenerated — never maintained by hand. This repository builds no diagram editor.

**Three vocabularies, never conflated.** Workflow detail L1/L2/L3 (this repo's `workflow.json`),
release scope MVP/V1/V2 (delivery tags, a planning *view*), and GovKit adoption L3/L4/L5
(governed-ai-delivery's install payload). Where a document uses more than one it says which.

**The Pillar 2 Gherkin prohibition is superseded, by policy.** `val-rapid-validation` currently
says "never emit Gherkin, NFRs, evaluation schemas, or build-ready specifications from this
skill". The policy of record moves behavioral definition *into* Pillar 2, so increment 06
replaces that blanket ban with progressive drafting and a complete selected contract at the exit
decision. What survives unchanged: every artifact still carries a hypothesis, an experiment and
a decision rule; an early throwaway experiment still does not need a production-ready
specification to run; a prototype still contributes no requirement that is absent from the
baseline.

**Stories and points go; context stays.** The default AIPOS route requires no user story, no
epic and no point estimate. Summaries, personas and outcomes remain useful and are referenced
from the PDG where available. `test_compute_size.py` coverage is preserved for users who choose
sizing — sizing becomes an opt-in diagnostic, never a forecast, and aggregate scenario counts
are not presented as cost. The legacy epic/tracker input route stays available and explicit.

**Plugin installation boundary.** No skill reaches across plugins today — `plugins/aipos-p2`
holds no relative path into `plugins/govkit/references/` — and increment 02 must not introduce
one. Shared references stay canonical in `plugins/govkit/references/`. Whether a consuming AIPOS
plugin declares a dependency, vendors a copy under a drift check, or the reference moves is
**increment 02's decision**, and it must be tested against the installed plugin layout rather
than this source tree.

**Preparation is not approval.** Every skill here prepares: a draft, a selection, a map, a
commitment package, a change package. None records a product decision. Until the engine contract
lands, increment 06 produces a clearly labelled **preview**, never a fake authoritative
approval, and a map badge is advisory and visibly labelled until a verifiable decision exists.

## Verification posture

```sh
claude plugin validate .
python -m pip install -r requirements-dev.txt
python -m pytest tests -q
```

`tests/test_repo_ingest.py`, `tests/test_render_map.py` and `tests/test_compute_size.py` are the
deterministic gate and must keep passing; new cases land beside them. Per CONTRIBUTING, these
tests assert behavior and semantic preservation, never instructional wording — a test matching a
heading in a `SKILL.md` would pass while the tool silently broke, so new tests follow the same
rule.

Each skill's `evals/evals.json` is a separate **model-graded** pass. A JSON file that parses is
not a passed eval. Where a skill's coaching behavior changes (increments 03, 04, 06, 14), the
eval cases are updated and any run records which cases ran, the model and configuration, the
rubric judgments, and the limitations. An eval that did not run is reported as not run.

Plugin `version` in the affected `.claude-plugin/plugin.json` is bumped when a change is
user-visible, and the README and affected `references/` are updated with it.

## Status

**Increment 02 is implemented.** Workflow source format version **1**:

- `plugins/govkit/references/workflow-source.md` — the `workflow.json` format, the L1/L2/L3
  views, the diagnostic table, and the rule that workflow order is neither release scope nor an
  implementation dependency.
- `plugins/govkit/skills/govkit-feature-map/scripts/workflow_resolve.py` — resolves qualified
  references against an ingested corpus and emits located diagnostics. Read-only.
- `plugins/govkit/references/spec-identifiers.md` — extended with the qualified reference form
  and a table of what a *resolver* does for each identity event (authored, derived, duplicate,
  missing, retired, split, merged, unparsed).
- `tests/test_workflow_resolve.py` (21) and `tests/test_plugin_boundaries.py` (81) — the latter
  enforces that no plugin file reaches into a sibling plugin, which is the installation boundary
  increment 00 left open.

**Plugin boundary decided:** the workflow format and its resolver live in the `govkit` plugin.
A skill needing them lives in the same plugin or receives already-resolved data. Copying a
shared reference into a second plugin is not the alternative — a copied reference is one nobody
maintains — and the boundary test enforces both halves.

Increments 03–06 and 14–15 remain unimplemented. No approval or release is authorized by this.
