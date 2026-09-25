# Rendering the map

`scripts/render_map.py` builds one self-contained HTML file — inline CSS and JS, no network calls, nothing to build or install when you render. It gets emailed, pasted into a wiki, and opened offline six months later, so it has to keep working with nothing around it. The journey diagram is no exception: its viewer is a prebuilt bundle in `scripts/assets/` that the renderer inlines.

```bash
python scripts/render_map.py -f features.json -s scores.json -z sizing_computed.json \
                             -c config.json -o feature-map.html
```

`-s`, `-z` and `-c` are optional. Without scores the map still renders — chain, cards, ledger — just without badges. `-z` takes the **computed** sizing file from `aipos-feature-slice`'s `compute_size.py`, never the raw agent verdicts; entries without a `rollup` are skipped with a warning, because only the script's arithmetic is trusted on the page.

## Contents

- [config.json](#configjson)
- [Hand-placing the chain](#hand-placing-the-chain)
- [Visual grammar](#visual-grammar)
- [The journey diagram (L1 / L2 / L3)](#the-journey-diagram-l1--l2--l3)
- [Verifying the render](#verifying-the-render)
- [Delivering](#delivering)

## config.json

```jsonc
{
  "title": "AI Vision Builder — Feature Map",
  "eyebrow": "Epic AI-123 · Initiative KTW_AIOS",
  "motto": "Visuals orient · specs authorise · Jira reports status.",
  "lede": "How the chain was derived, which labels drive it, what is excluded.",

  "central": ["AI-201", "AI-202"],     // rendered in the 'central' border colour
  "undecided": ["AI-207"],             // dashed amber — an unresolved boundary
  "centralLabel": "Runs centrally",
  "deploymentLabel": "Runs in the client VPC",

  "lanes": [
    {"name": "Experience", "sub": "what the client touches",
     "note": "Client-visible surface. Every question here must earn its place."}
  ],

  "positions": {"AI-201": [40, 84], "AI-202": [390, 136]},

  // Journey diagram only (see below)
  "sourceBaseUrl": "https://github.com/acme/specs/blob/3f9c2e1/",
  "journeyPositions": {"j:invoice-approval/a:route": {"x": 300, "y": 40}}
}
```

`lanes` controls order and adds framing text; `name` must match the features' `workstream`. Omit it and lanes are inferred in first-seen order with no framing.

`central` / `undecided` express whatever boundary matters in the architecture — deployment topology, team ownership, trust zone. The two colours plus a dashed state are deliberately few; a diagram that encodes five distinctions in border style stops being readable.

Put the derivation in `lede`. A reader needs to know the chain is *derived* from label conventions rather than drawn by hand, or they will treat a missing edge as an architectural claim rather than a missing label.

## Hand-placing the chain

Auto-layout places nodes by dependency depth — column is depth, row is a barycentre pass over producers to reduce crossings. It is honest and fast, and fine for a working session.

It is not as good as a person. For anything going in front of stakeholders, set `positions` explicitly: `{"KEY": [x, y]}`, nodes are 200×84, and 350×140 spacing reads well. Hand placement lets you group by phase, put the boundary crossing in the middle, and keep related features adjacent — none of which an algorithm infers from a DAG.

Long chains render wide and the container scrolls horizontally. That is deliberate: scaling a nine-column chain down to page width makes every label unreadable, which defeats the diagram. If the width is genuinely unwieldy, hand-place into a serpentine.

## Visual grammar

**Development Token ribbon** across the top of each card, colour-coded, with the score. Green Approved, amber Approved with edits, red Blocked.

**Score pill** on each chain node, same colours. This is the piece that makes readiness spatial — a reader sees *where* in the flow the weakness sits.

**GovKit readiness panel** inside each card: summary, critical blockers, ranked edits, and the ten-dimension breakdown with a coloured pip per dimension. Collapsed by default so the card stays scannable, but present so the badge is auditable in place. A badge nobody can interrogate gets ignored the first time somebody disagrees with it.

**The standing caveat** renders above the chain whenever scores are present, stating that the blocker list is the gate rather than the number, and that these are batch scores. Do not remove it. Someone will read this page without the conversation that produced it.

**Size badge** in each sized card's metrics row — the distribution `nL · nM · nS · total pts`, with the Large count in amber when nonzero. A corpus with committed `@small`/`@medium`/`@large` tags but no sizing file still gets the badge with band counts only — the points total renders only from a computed sizing file, because points are arithmetic and arithmetic comes from `compute_size.py` or not at all. A distribution rather than an average, because the Large count is the risk signal an average hides. The **Scenario sizing panel** inside the card carries the per-scenario breakdown (dimensions, points, band, slice) and the Large-on-MVP risk flags; slices marked `rec` are unconfirmed batch recommendations. The size note above the chain carries the same caveat page-side. Do not remove that one either.

**Gherkin fidelity on the card.** Whatever ingestion preserved has to be visible, or preserving it changed nothing: feature-level and rule-level `Background` blocks render with their scope named (they run for different scenarios, and a card that shows one without saying which invites the wrong conclusion); `Scenario Outline` carries an **Outline** chip and its `Examples` tables render with the row count; step data tables and doc strings render under the step they belong to. The metrics row shows `N examples` beside `N scenarios` whenever the two differ — one authored outline is several executable cases, and both numbers are real.

**Parse errors** render as a red block at the top of the acceptance-criteria panel, naming file, line and column. A feature whose Gherkin did not parse is not a feature with a thin spec, and the card must not let a reader confuse the two.

**Slice tags** (`@mvp` / `@v1` / `@v2`, `@small` / `@medium` / `@large`) render as chips on scenario names, and a **release-slice filter bar** appears above the lanes whenever any scenario carries a slice tag. The filter dims scenarios outside the chosen slice and works from *tagged* slices only — recommendations never drive it, so the filter cannot present an unconfirmed release plan as a decided one. Tags inherit: a slice tag on the `Feature:` or the `Rule:` applies to the scenarios beneath it, and a scenario's own tag overrides that default.

## The journey diagram (L1 / L2 / L3)

Pass one or more **resolved** workflows — `workflow_resolve.py`'s output, not a raw
`workflow.json` — and the page gains a journey section above the feature lanes:

```bash
python scripts/repo_ingest.py features/ -o features.json
python scripts/workflow_resolve.py invoice-approval.workflow.json features.json > invoice.json
python scripts/workflow_resolve.py threshold-setup.workflow.json features.json > setup.json
python scripts/render_map.py -f features.json -w invoice.json -w setup.json -o map.html
```

Taking the resolver's output rather than resolving here is deliberate: two implementations of
"what does this reference mean" would eventually disagree, and the one in the renderer would be
the wrong one. `-w` repeats; each workflow is one journey, identified by its `workflow_key`. Two
workflows with the same key, or resolved against different sources, are refused rather than
merged.

The section is an interactive diagram with the same journeys as tables beneath it.
`scripts/journey_graph.py` builds one graph from the corpus and every resolved workflow, and
both are drawn from it, so they cannot disagree.

| Level | Shows | Deliberately omits |
|---|---|---|
| **L1 Journey** | Each journey's activities in customer order, branch conditions on the edges, the actor on each activity, and a count of the handoffs its steps record | All Gherkin. A rule slug in the view someone outside the team reads is the failure mode |
| **L2 Features** | The Gherkin features each activity uses. A feature used by several activities or journeys is **one node** with an edge from each | Scenarios |
| **L3 Scenarios** | The Rules and scenarios under each feature. Selecting a scenario shows its Background, Given / When / Then with data tables and doc strings, Examples, tags, identity, where it is referenced, and its source file and line | — |

The diagram answers two questions directly; say both answers when you present the map:

- **Which scenarios specify this journey?** Select the journey. The panel lists the scenarios
  it references, and separately the ones that only sit under a Rule it references. Naming a
  Rule does not place every scenario beneath it, so those are not counted as specifying it.
- **Which journeys are affected if this feature changes?** Select the feature. Every journey
  and activity that uses it lights up, and the panel lists them.

A journey selector narrows the diagram to one journey; *Show only this feature's scenarios*
narrows L3 to one feature. Neither changes a fact — they only hide what is out of scope.

**Handoffs come only from steps.** An activity's handoff count is what its steps' `handoff`
fields record. Adjacent activities with different actors are not evidence that work changed
hands, and the diagram does not infer one.

**Reuse must read as reuse.** A shared feature is one node. In the tables, a Rule referenced
from several steps appears once per reference with an *"also referenced at"* column naming the
others; without it, three references to one authored Rule look like three Rules. With more
than one journey, a *Features and the journeys that use them* table answers the second
question without the diagram.

**Unresolved references are not links.** A `design:` reference lives outside the Gherkin corpus,
a `foreign-source` one belongs to another repository, and a dangling one names behavior the
corpus does not declare. Each is a dashed node on the activity that wrote it, with the reason,
because linking it would send a reader to a card that does not exist and imply the behavior was
verified.

**Uncovered behavior stays visible.** Features no journey on the page uses appear at L2 marked
*in no journey*; at L3, scenarios are marked by whether a journey references them, sit under a
referenced Rule, or are in no journey at all. With several journeys the page-wide finding is
what *no* journey references; each journey's own coverage is still reported. A
`partial-coverage` diagnostic means the list is a floor: that feature had Gherkin that did not
parse.

**Source links are explicit.** Set `sourceBaseUrl` in `config.json` to turn each scenario's
`path:line` into a link — for GitHub, `https://github.com/<org>/<repo>/blob/<commit>/`, pinned
to the commit the specs were ingested from so a link opened later shows what was rendered.
Without it the panel shows `path:line` as text. Paths are as `repo_ingest.py` recorded them, so
run ingestion from the repository root when you want links.

**Hand placement.** The diagram lays itself out left to right with dagre. `journeyPositions`
pins individual nodes by graph id (`j:<workflow_key>/a:<activity id>` for an activity), for a
stakeholder-facing journey that reads better arranged by a person.

**The page never depends on the diagram.** The tables start open and collapse to a *Table view*
disclosure once the diagram loads; with script off, or if the bundle is missing from
`scripts/assets/`, the tables are all there is and the renderer warns. Printing hides the canvas
and prints the tables.

### What the page must never claim

A rendered map is generated from files in a working tree. It cannot verify that any decision was
recorded anywhere, so it carries an **advisory banner** and no approval badge, and slice chips
are labelled a planning view over behavior rather than a commitment. If a future version shows
authorization status, it must come from a verifiable decision read at render time and say where
it came from — never from a tag, a file, or the absence of an error.

### Accessibility and width

Every disclosure in the page's own markup is a native `<details>` / `<summary>`: focusable, and
operable with Enter or Space with no script. No element in that markup wears `role="button"` or a
`tabindex`. The journey diagram is the exception by necessity — React Flow makes its nodes
focusable, and Enter or Space on one selects it — so it is a supplementary view, and the tables
remain the complete keyboard and screen-reader route to every fact it shows. The journey tables
collapse to stacked rows below 640px, and the diagram stacks its detail panel under the canvas
below 860px, with no horizontal page scroll.

## Verifying the render

Screenshot and look at it. Then assert the things eyes miss:

```javascript
const {chromium} = require('playwright');
(async () => {
  const b = await chromium.launch({executablePath: '/opt/pw-browsers/chromium'})
    .catch(() => chromium.launch());
  const p = await b.newPage({viewport: {width: 1700, height: 1250}, deviceScaleFactor: 1.3});
  await p.goto('file://' + process.cwd() + '/feature-map.html', {waitUntil: 'load'});
  await p.screenshot({path: 'check.png'});

  console.log(JSON.stringify(await p.evaluate(() => ({
    cards:  document.querySelectorAll('article.card').length,
    tokens: document.querySelectorAll('.card .token').length,
    pills:  document.querySelectorAll('svg .tkbg').length,
    dims:   document.querySelectorAll('table.dim tr').length,   // 10 per scored feature
    // node rects must not overlap; exclude the pill rects nested inside each node
    overlap: (() => {
      const r = [...document.querySelectorAll('svg .node rect:not(.tkbg)')]
        .map(n => n.getBoundingClientRect());
      let c = 0;
      for (let i = 0; i < r.length; i++)
        for (let j = i + 1; j < r.length; j++)
          if (!(r[i].right < r[j].left || r[j].right < r[i].left ||
                r[i].bottom < r[j].top || r[j].bottom < r[i].top)) c++;
      return c;
    })()
  }))));

  // mobile
  const m = await b.newPage({viewport: {width: 390, height: 844}, deviceScaleFactor: 2});
  await m.goto('file://' + process.cwd() + '/feature-map.html', {waitUntil: 'load'});
  await m.screenshot({path: 'check-mobile.png'});
  await b.close();
})();
```

When the page has a journey diagram, check it too — it only draws in a browser, so this is the
one place a layout or script fault shows up:

```javascript
  const j = await b.newPage({viewport: {width: 1360, height: 900}});
  const external = [];
  j.on('request', r => { if (!/^(file|data|blob|about):/.test(r.url())) external.push(r.url()); });
  await j.goto('file://' + process.cwd() + '/feature-map.html', {waitUntil: 'load'});
  await j.waitForSelector('.jv .react-flow__node');
  for (const n of [1, 2, 3]) {                       // L1, L2, L3
    await j.locator('.jv-levels button').nth(n - 1).click();
    await j.waitForTimeout(250);
    await j.locator('.jv').screenshot({path: `check-journey-l${n}.png`});
    console.log(`L${n}`, await j.evaluate(() => {
      const r = [...document.querySelectorAll('.jv .react-flow__node')].map(x => x.getBoundingClientRect());
      let c = 0;
      for (let i = 0; i < r.length; i++) for (let k = i + 1; k < r.length; k++)
        if (!(r[i].right <= r[k].left || r[k].right <= r[i].left ||
              r[i].bottom <= r[k].top || r[k].bottom <= r[i].top)) c++;
      return {nodes: r.length, overlap: c};
    }));
  }
  console.log('network requests', external);         // must be []
```

`tokens` and `pills` should equal the scored-feature count, `dims` should be exactly ten times it, and every `overlap` — chain and journey — must be `0`, as must the journey page's network requests. A mismatch between token count and score count means a feature key in `scores.json` does not match any key in `features.json` — the renderer warns about this on stdout too.

## Delivering

Send the HTML with `SendUserFile`. A feature map is something a team comes back to and re-reads, so when a desktop is connected also persist it with `create_artifact` so it survives outside the conversation; use `update_artifact` on later rebuilds rather than creating a second copy.

Keep `features.json`, `scores.json`, `config.json` and any resolved workflows alongside the output. Re-running the map after a spec changes should mean re-ingesting and re-scoring, not rebuilding the inputs by hand.
