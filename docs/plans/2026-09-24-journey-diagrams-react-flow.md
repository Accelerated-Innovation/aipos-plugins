# Plan: interactive L1 / L2 / L3 journey diagrams with React Flow

**Date:** 2026-09-24
**Owner skill:** `aipos-map-render` renders the diagrams. `aipos-workflow-create` owns the
`workflow.json` source; this plan does not change that format.
**Scope:** new repo-level viewer source `viewers/journey/`; in `plugins/aipos/skills/aipos-map-render/`
a committed viewer bundle, a new `scripts/journey_graph.py`, and changes to `render_map.py`,
`SKILL.md` and `references/rendering.md`; `plugins/aipos/references/workflow-source.md`;
wording in `aipos-workflow-create/SKILL.md`; tests; CI; `CONTRIBUTING.md`.
**Status legend:** `[ ]` not started · `[~]` in progress · `[x]` done
**Status:** all increments implemented on `feat/journey-diagrams` (2026-09-25), not yet committed. `pytest tests` 612 passed / 5 skipped; `npm test` 18 passed; `npm run check-bundle` clean; `claude plugin validate` passes; `check-page.mjs` passes in Chrome, WebKit and Firefox. **Not run:** model-graded evals and live routing for `aipos-map-render`, whose description and SKILL.md changed.

## Goal

Replace the table-only journey section with a diagram that traces a product journey down to the
behavior that specifies it, and answers two questions directly:

1. **Which scenarios specify this journey?**
2. **Which journeys are affected if this feature changes?**

## Decisions (agreed 2026-09-24)

| # | Decision | Consequence |
|---|---|---|
| D1 | **L2 shows features and business rules; actors and handoffs stay visible.** | L1 activity nodes show their actor, and a count of explicit handoffs you can expand. Handoffs come only from the `handoff` field on steps, never from adjacency, matching `aipos-workflow-create`. |
| D2 | **The viewer ships bundled into the HTML.** | React, React Flow and the layout library are built once into a committed JS file that `render_map.py` inlines. The page stays a single file with no network requests. Only contributors need Node. |
| D3 | **One page can show several journeys.** | `-w` becomes repeatable. Impact across journeys is computed in Python and tested. |
| D4 | **The existing HTML tables stay as the fallback.** | They are the keyboard and screen-reader view, what readers see with JavaScript off, and the printed view. |

## The three levels

| Level | Shows | Built from |
|---|---|---|
| **L1 — Product journey** | Journey outcome; activities in customer order; branches with conditions; actor on each activity; handoff count | `workflow.json`: `outcome`, `activities`, `next`, `actor`, and each step's `handoff` |
| **L2 — Logical features** | The Gherkin Features and Rules behind each activity. A feature shared by several activities or journeys appears **once**, with an edge to each | Behavior references on activities and steps, grouped by `featureKey` |
| **L3 — Scenarios** | Scenarios under each Rule. Clicking one shows Given / When / Then (data tables and doc strings included), Examples, tags, identity, and a link to the `.feature` file and line | `features.json` `stepDetails`, `examples`, `file`, `line` |

Almost all of this model already exists. Stable IDs are the `@rule:` / `@scenario:` tags. The
"small mapping file" is `workflow.json`. Journey order is `next`. Shared behavior is authored once
and referenced many times. What's new is the graph model that joins them across journeys, and the
viewer.

**Journey ids.** Each journey is identified by its workflow's `workflow_key`. Two workflows with the
same key on one page are an error, not a merge.

### Rules the diagram must keep (from existing guardrails)

- **Referencing a Rule doesn't place its scenarios.** A scenario appears as *specifying* a journey
  only when a reference names it. Scenarios under a referenced Rule without their own reference
  render as *under a referenced rule, not placed*, and are counted separately in answer 1.
  (`aipos-workflow-create` Step 5; the resolver's coverage already works this way.)
- **Unresolved references are not links.** `design:`, `foreign-source`, dangling and ambiguous
  references render as dashed nodes that give the reason, and link nowhere.
- **Uncovered behavior stays visible.** With several journeys, *not in any journey on this page*
  is the union finding and gets its own cluster. Coverage for each journey is still reported.
- **Advisory banner and no approval badge**, as today. Slice chips (`@mvp` / `@v1` / `@v2`) are
  labelled a planning view.
- **Order is not scope.** L1 edges are `next` only. No build-order or release edges.

## Architecture

```
features.json ─┐
               ├─ workflow_resolve.py (unchanged, once per workflow) ─► resolved-*.json
workflow.json ─┘                                                        │
                                                                        ▼
          render_map.py -f features.json -w a.json -w b.json
                 │
                 ├─ journey_graph.py  → graph model: nodes, edges, the two answer indexes, uncovered
                 ├─ embeds the model as <script type="application/json" id="journey-data">
                 ├─ inlines assets/journey-viewer.js + .css (the committed bundle)
                 └─ keeps the existing tables as the fallback (wf_l1 / wf_l2 / wf_l3)
```

**All logic stays in Python; the viewer only presents it.** `journey_graph.py` computes every
node, edge, count, and both answer indexes. The viewer does layout, selection, highlighting and
the detail panel. Every fact on the diagram is tested with `pytest`, and the JavaScript contains
no resolution logic that could disagree with the resolver (the same reason `render_map.py`
refuses to resolve on its own today).

**Graph model sketch** (`journey_graph.build(features, resolved_list)`):

```jsonc
{
  "version": 1,
  "journeys":   [{ "id": "invoice-approval", "outcome": "…", "ok": true, "diagnostics": 3 }],
  "nodes": [
    { "id": "j:invoice-approval/a:route", "level": 1, "kind": "activity", "journey": "invoice-approval",
      "name": "Route for approval", "actor": {"id": "routing", "kind": "system", "name": "…"},
      "handoffs": [{"step": "evaluate-threshold", "from": "submitter", "to": "routing"}] },
    { "id": "f:acme/FEATURE-inv_full", "level": 2, "kind": "feature", "name": "…", "journeys": ["…"] },
    { "id": "acme/FEATURE-inv_full#rule:invoice-approval-threshold", "level": 2, "kind": "rule" },
    { "id": "acme/FEATURE-inv_full#scenario:approval-routing-by-amount", "level": 3, "kind": "scenario",
      "placement": "referenced" /* | "under-referenced-rule" | "uncovered" */,
      "steps": [...stepDetails], "examples": [...], "tags": [...], "idSource": "authored",
      "source": {"file": "features/inv/acceptance.feature", "line": 15, "href": "…"} },
    { "id": "unresolved:acme/FEATURE-x#design:panel", "kind": "unresolved", "reason": "non-gherkin-kind" }
  ],
  "edges": [
    { "source": "j:…/a:route", "target": "j:…/a:approve", "kind": "next", "condition": "standard invoice" },
    { "source": "j:…/a:route", "target": "f:acme/FEATURE-inv_full", "kind": "uses" },
    { "source": "f:…", "target": "…#rule:…", "kind": "contains" },
    { "source": "…#rule:…", "target": "…#scenario:…", "kind": "contains" }
  ],
  "index": {
    "scenariosByJourney": { "invoice-approval": { "referenced": [...], "underReferencedRule": [...] } },
    "journeysByFeature":  { "acme/FEATURE-inv_full": ["invoice-approval", "partner-onboarding"] }
  },
  "uncovered": [...]
}
```

**Source links.** An `href` is written only when `config.json` supplies `sourceBaseUrl` (for
example a GitHub `blob/<sha>/` prefix). Otherwise the panel shows `file:line` as text. Pinning to a
commit means a link opened six months later still shows the spec that was rendered.

## Viewer (`viewers/journey/`, repo level, never shipped)

- **Stack:** `@xyflow/react` (React Flow, MIT, free version), `react`/`react-dom` (MIT),
  `@dagrejs/dagre` (MIT) for left-to-right layout, `esbuild` to build. Everything is pinned in
  `package-lock.json`. No React Flow Pro features. ELK is not used (EPL-2.0 licence, larger).
- **Output:** a single IIFE `journey-viewer.js` and `journey-viewer.css`, written to
  `plugins/aipos/skills/aipos-map-render/scripts/assets/` together with `THIRD_PARTY_NOTICES.txt`
  (MIT notices for everything bundled). The bundle reads `#journey-data` and mounts into
  `#journey-root`.
- **Custom nodes:** activity cards (name, actor badge by kind, handoff count, branch conditions on
  edges); feature cards (rule count, scenario count, the journeys using it); rule cards; scenario
  chips (placement style, slice chips, derived-id warning); dashed unresolved nodes.
- **Interaction:**
  - An L1 / L2 / L3 switch. Each level adds detail to the level above rather than replacing it,
    so you keep your place.
  - A journey selector (one or all). Selecting a journey highlights its activities and features
    and dims the rest.
  - Selecting a feature highlights **every journey and activity that uses it**. This is answer 2.
  - A per-journey panel, *Scenarios that specify this journey*, split into referenced and
    under-a-referenced-rule. This is answer 1.
  - Selecting a scenario opens the detail panel: Given / When / Then, Examples, tags, identity,
    *also referenced at*, and the source link.
  - Built-in React Flow controls: fit view, zoom and minimap.
- **Attribution:** keep React Flow's default attribution visible. The licence allows removing it,
  but the maintainers ask non-subscribers to keep it.

## Increments

### 0. Spike: bundle size and offline behaviour `[x]`
Build a throwaway bundle with React Flow and dagre rendering fixture data from `file://`.
**Exit:** it renders offline in Chrome, Safari and Firefox; the bundle is under 450 KB minified
(React Flow core, React and dagre are roughly 300–400 KB combined, so this is a ceiling, not a
guess we're happy with); the page makes no network requests. If the spike fails any of these,
stop and revisit D2 before continuing.

### 1. Graph model: `journey_graph.py` `[x]`
Build the graph from `features.json` plus N resolved workflows, including the placement rules,
the two indexes, the uncovered union, unresolved nodes and duplicate-journey errors.
**Tests (`tests/test_journey_graph.py`):**
- A feature shared by two journeys appears once, with two `uses` edges.
- `journeysByFeature` is correct across journeys.
- A Rule-only reference doesn't place its scenarios.
- `scenariosByJourney` separates referenced scenarios from those under a referenced Rule.
- The uncovered union differs from any single journey's coverage.
- Foreign, design and dangling references become unresolved nodes, never features.
- Handoffs come only from `step.handoff`.
- Duplicate `workflow_key` values raise an error.
- IDs stay stable across renames that keep the slug.

### 2. Viewer app `[x]`
Build the React Flow app over the graph model: custom nodes, the level switch, selection and
highlighting, the answer panels and the detail panel. Layout is recomputed per level from dagre;
`config.json` `positions` can still pin activity nodes. Add a small `vitest` suite covering only
the viewer's own logic (level filtering, highlight sets), never facts about the model.

### 3. Integrate with `render_map.py` `[x]`
- `-w` repeatable (`action="append"`); a single `-w` behaves exactly as today.
- Embed the model and inline the bundle and CSS. Show the tables when JavaScript is off
  (`<noscript>`), keep a *Table view* toggle, and use the tables when printing (`@media print`
  hides the canvas).
- If the bundle file is missing, render the tables and print a warning. Never fail the render.
- **Tests (extend `tests/test_render_map.py`):**
  - Several `-w` render several journeys.
  - The embedded JSON matches `journey_graph.build`.
  - The page has no `http(s)://` script or stylesheet references (self-contained).
  - The fallback tables are still present.
  - A page with no `-w` has no bundle, so its size doesn't change.

### 4. Docs and skill text `[x]`
- `references/rendering.md`: rewrite the journey section around the three new levels, the two
  questions and the multi-journey command. Narrow the accessibility rule: the diagram is a
  supplementary view (React Flow nodes are focusable, so "no `tabindex`" can't hold there), and
  the tables remain the complete keyboard and screen-reader route.
- `aipos-map-render/SKILL.md`: step 6 uses repeatable `-w`. Say to report both answers when you
  present the map.
- `references/workflow-source.md`: replace the L1/L2/L3 table with the new meanings. State that
  handoffs are still authored on steps and shown on L1. The format itself doesn't change.
- `aipos-workflow-create/SKILL.md`: update the line describing what the views show.

### 5. CI and contributor workflow `[x]`
- `validate.yml`: a new `viewer` job runs `npm ci`, `npm run build` and `npm test`, then
  `git diff --exit-code` on `scripts/assets/`, so the committed bundle always matches its source.
  The pytest job needs no Node.
- `CONTRIBUTING.md`: how to rebuild the viewer, and that the bundle is a build output reviewed as
  generated code.
- A size guard in pytest: the bundle stays under the spike's ceiling.

### 6. Verify `[x]`
Extend the Playwright check in `rendering.md` to:
- load a two-journey fixture;
- switch levels;
- select a shared feature and assert both journeys highlight;
- open a scenario and assert Given / When / Then renders;
- check there's no horizontal overflow at 375 px;
- confirm the printed view shows the tables.

Then look at the screenshots.

## Risks

| Risk | Mitigation |
|---|---|
| Page size grows by about 350 KB once a workflow is included | Inlined only when `-w` is passed; size guard in CI |
| The committed bundle drifts from its source | CI rebuild and diff; pinned lockfile |
| The diagram and the tables disagree | Both are built from the same Python model; the render test compares them |
| Dense L3 graphs become unreadable | L3 shows only the selected journey or feature by default; the per-level layout keeps other levels collapsed |
| Canvas accessibility | Tables stay the complete accessible route (D4) |

## Open questions — resolved 2026-09-25, before increment 4

1. **Activity, not stage.** The format, diagnostics, tables and `aipos-workflow-create` all say
   *activity*; the diagram matches.
2. **Source links are explicit.** `sourceBaseUrl` in `config.json` only; without it the panel shows
   `path:line`. No git-remote auto-detection.
3. **NFRs and evaluations stay on the feature lanes.** The feature panel links to the full card.

## As built — deviations from the plan

- **Bundle ceiling raised from 450 KB to 550 KB.** The spike's bare bundle was 441.5 KB; React DOM
  alone is 205 KB. Swapping in Preact would save about 190 KB, but React Flow does not officially
  support it. The shipped bundle is 463.6 KB (about 150 KB gzipped); `tests/test_render_journeys.py`
  enforces the ceiling.
- **Rules are drawn at L3, not L2.** L2 draws feature nodes and lists their Rules in the panel;
  drawing every Rule at L2 made the level unreadable. The plan's L2 "features and business rules"
  holds through the panel.
- **`workflow_resolve.py` now reports `sourceKey`** in its output, so the graph can refuse
  workflows resolved against different sources instead of guessing.
- **Uncovered keeps the resolver's meaning.** A scenario under a referenced Rule without its own
  reference is uncovered (as the resolver counts it) and additionally marked
  *under a referenced rule*; the diagram's uncovered count matches the resolver's for one journey.
- **Tables gained a *Features and the journeys that use them* table** when several journeys are on
  the page, so question 2 has a no-script answer.
- **Licence notices are generated.** The bundle carries MIT, ISC (d3) and BSD-3-Clause (d3-ease)
  code; `build.mjs` writes `THIRD_PARTY_NOTICES.txt` and an attribution banner in the bundle from
  the packages actually bundled.
- **Plugin version bumped to 1.3.0** (user-visible change).
