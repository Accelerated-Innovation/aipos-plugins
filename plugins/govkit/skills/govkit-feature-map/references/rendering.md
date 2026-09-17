# Rendering the map

`scripts/render_map.py` builds one self-contained HTML file — inline CSS and JS, no network calls, no build step. It gets emailed, pasted into a wiki, and opened offline six months later, so it has to keep working with nothing around it.

```bash
python scripts/render_map.py -f features.json -s scores.json -z sizing_computed.json \
                             -c config.json -o feature-map.html
```

`-s`, `-z` and `-c` are optional. Without scores the map still renders — chain, cards, ledger — just without badges. `-z` takes the **computed** sizing file from `govkit-feature-slice`'s `compute_size.py`, never the raw agent verdicts; entries without a `rollup` are skipped with a warning, because only the script's arithmetic is trusted on the page.

## Contents

- [config.json](#configjson)
- [Hand-placing the chain](#hand-placing-the-chain)
- [Visual grammar](#visual-grammar)
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

  "positions": {"AI-201": [40, 84], "AI-202": [390, 136]}
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

`tokens` and `pills` should equal the scored-feature count, `dims` should be exactly ten times it, and `overlap` must be `0`. A mismatch between token count and score count means a feature key in `scores.json` does not match any key in `features.json` — the renderer warns about this on stdout too.

## Delivering

Send the HTML with `SendUserFile`. A feature map is something a team comes back to and re-reads, so when a desktop is connected also persist it with `create_artifact` so it survives outside the conversation; use `update_artifact` on later rebuilds rather than creating a second copy.

Keep `features.json`, `scores.json` and `config.json` alongside the output. Re-running the map after a spec changes should mean re-ingesting and re-scoring, not rebuilding the inputs by hand.


## The journey views (L1 / L2 / L3)

Pass a **resolved** workflow — `workflow_resolve.py`'s output, not a raw `workflow.json` — and
the page gains a journey section above the feature lanes:

```bash
python scripts/repo_ingest.py features/ -o features.json
python scripts/workflow_resolve.py workflow.json features.json > resolved.json
python scripts/render_map.py -f features.json -w resolved.json -o map.html
```

Taking the resolver's output rather than resolving here is deliberate: two implementations of
"what does this reference mean" would eventually disagree, and the one in the renderer would be
the wrong one.

| View | Shows | Deliberately omits |
|---|---|---|
| **L1** | Outcome, activities in order, actor per activity, branches and their conditions | All Gherkin. A rule slug in the view someone outside the team reads is the failure mode |
| **L2** | The steps inside each activity, actor kinds, and the handoffs where work changes hands | Behavior references |
| **L3** | The Rules and scenarios governing each activity and step, linked to their feature cards | — |

**Reuse must read as reuse.** A Rule referenced from several steps appears once per reference
with an *"also referenced at"* column naming the others. Without it, three references to one
authored Rule look like three Rules.

**Unresolved references are not links.** A `design:` reference lives outside the Gherkin corpus
and a `foreign-source` one belongs to another repository; both render as plain text with the
reason, because linking them would send a reader to a card that does not exist and imply the
behavior was verified.

**Uncovered behavior gets its own panel** — corpus elements no activity or step references,
with the caveat that this is legitimate when they belong to another journey. A
`partial-coverage` diagnostic means the list is a floor: that feature had Gherkin that did not
parse.

### What the page must never claim

A rendered map is generated from files in a working tree. It cannot verify that any decision was
recorded anywhere, so it carries an **advisory banner** and no approval badge, and slice chips
are labelled a planning view over behavior rather than a commitment. If a future version shows
authorization status, it must come from a verifiable decision read at render time and say where
it came from — never from a tag, a file, or the absence of an error.

### Accessibility and width

Every disclosure is a native `<details>` / `<summary>`: focusable, and operable with Enter or
Space with no script. No element wears `role="button"` or a `tabindex`. The journey tables
collapse to stacked rows below 640px, which is the one thing that cannot simply shrink.
