---
name: govkit-feature-map
description: Build a visual, scored feature map of a whole epic, release or spec corpus — a chain diagram of how artifacts flow between features, one card per feature with its Gherkin, NFRs and evaluation criteria, a GovKit Development Token badge on every feature showing whether it is ready for AI-assisted coding, and optionally a size badge per feature (scenario complexity distribution) with MVP/V1/V2 slice views from Gherkin tags. Ingests from Jira, Aha!, or a repo directory of feature specs, and merges a tracker record with repo-resident Gherkin. Trigger whenever the user asks to map, visualise, chart, or diagram an epic or set of features, wants a readiness dashboard or portfolio view, asks to score, size, or badge many features at once, wants to see how features connect or what produces and consumes what, asks where a release is weakest or what is blocking delivery, or wants to see how big features are or what the MVP slice costs across a corpus — even if they don't say "feature map" or name GovKit.
---

# GovKit Feature Map

Turn a corpus of feature specs into one self-contained HTML page that a delivery team, a PM and a sponsor can all read: how the features connect, what each one actually specifies, and how ready each is for AI-assisted coding.

## What this produces and why it is shaped this way

The map has three registers, and each answers a question the others cannot.

**The chain** shows producer-to-consumer flow between features. It exists because the sequencing risk in an epic is rarely visible from a backlog: a feature that looks independent is often waiting on an artifact nobody has committed to producing. Readiness badges sit on the chain nodes so a reader can see *where* in the flow the weakness is, not just that it exists.

**The lanes** carry one card per feature, holding the real spec — rules, scenarios, NFRs with thresholds and evidence, evaluation criteria with gates, open questions. This is what makes the map a working document rather than a status picture. The card is where somebody goes to argue with the spec.

**The ledger** lists every artifact with its producers and consumers. Terminal artifacts — produced but never consumed — are usually either genuine outputs or a modelling error worth catching.

The deliverable is one HTML file with no external dependencies, because it gets emailed, dropped in a wiki, and opened six months later.

## Workflow

Run these in order. Steps 4 and 5 are the ones people are tempted to skip, and they are the ones that make the artifact trustworthy.

### 1. Establish the corpus and the question

Ask what the map is for before building it. A map for a sponsor wants the chain and the badges; a map for a refinement session wants the cards open. Both are the same build, but the framing text differs.

Confirm: which epic, project or directory; whether readiness scoring is wanted; and whether the user has a preferred lane grouping (workstream, team, phase, component).

### 2. Ingest

Pick the adapter that matches the source. `references/ingestion-contract.md` has the full `features.json` schema and the field mapping for each adapter — read it before writing any ingestion code.

| Source | How |
|---|---|
| Jira | Atlassian MCP: `searchJiraIssuesUsingJql` for the epic's children, then `getJiraIssue` per feature |
| Aha! | Aha MCP: `read_records` / `search_records` scoped to the release or epic |
| Repo directory | `scripts/repo_ingest.py <root>` — walks nested epic/feature folders |
| Tracker + repo | `scripts/repo_ingest.py <root> --merge tracker.json` |

The repo adapter needs the official Cucumber Gherkin parser (MIT), pinned in `scripts/requirements.txt`:

```bash
python -m pip install -r scripts/requirements.txt
```

It parses rather than pattern-matches, so `Background` scoping, `Scenario Outline` and its `Examples`, step data tables, doc strings, tag inheritance and source locations all survive into `features.json` — and invalid Gherkin produces file/line/column diagnostics instead of a partial feature that looks complete. `repo_ingest.py` exits 3 when any file failed to parse; the output is still written, so a corpus stays mappable, but a pipeline can act on the code.

That last row matters more than it looks. Teams that keep Gherkin under version control rather than pasting it into a tracker have made a defensible call — two copies of a spec drift. But it leaves the tracker record thin, and a map built from the tracker alone will score that feature near zero and badge the most disciplined team in the portfolio as the worst. Merging the repo spec onto the tracker record fixes that: the tracker keeps status, ownership, phase and the artifact chain, and the repo supplies the spec.

Always show the user what was ingested — counts of rules, scenarios, examples, NFRs and evals per feature — before scoring. A feature that ingested zero rules is either genuinely empty or a parse failure, and those need different responses; `parseErrors` tells you which, and the card says so too.

Scenario and example counts are different numbers on purpose: `scenarioCount` is what a person reviews (one `Scenario Outline` is one scenario), `exampleCount` is what a runner executes (that outline expanded over its rows). Report whichever the question calls for, and never present one as the other.

### 3. Derive the chain

The chain comes from each feature's `consumes` and `produces` arrays. How those get populated depends on the source: Jira label conventions (`map-in-*` / `map-out-*`), an Aha! custom field, or explicit declaration in the spec. Whatever the convention, record it in the map's lede so a reader knows the diagram is derived rather than drawn.

If artifact names are inconsistent across features (`context-brief` vs `contextBrief` vs `Context Brief`), normalize to kebab-case during ingestion. A chain that silently drops edges because two features spelled the same artifact differently is worse than no chain.

### 4. Score

Scoring is delegated to another skill, which owns the rubric. Do not reimplement dimensions, bands, or blocker lists here — a second copy drifts from the first, and the rubric is what the whole map's credibility rests on.

**Which rubric depends on where the corpus sits in the lifecycle.** GovKit gates twice, and the two are not interchangeable:

| Corpus | Skill | Rubric |
|---|---|---|
| Draft 0 from a tracker — Jira, Aha!, not yet in the repo | `govkit-feature-refine` batch mode | 10 dimensions; Approved ≥ 8/10 |
| Approved packages in the repo — `acceptance.feature`, `nfrs.md`, `eval_criteria.yaml` | `govkit-feature-readiness` | 12 dimensions; Approved ≈ 10/12, Blocked < 8.5 |

The refine rubric asks whether a team understands the feature well enough to build it. The readiness rubric asks whether a coding agent can execute the package without guessing — it adds package completeness, source traceability, repo fit, and AI coding agent safety, none of which a tracker record can answer.

Badging a repo-resident package with the refine rubric flatters it: it scores well on shared understanding while never being asked whether it fits the architecture. Default to the source — tracker-sourced features get refine, repo-sourced packages get readiness — and state which rubric produced the badge in the map's lede. Never mix rubrics in one map without labelling each badge; 7.5 does not mean the same thing on the two scales.

For a mixed corpus, ask which gate the user is trying to see before rendering. The answer is usually "the one we have not passed yet".

The rest of this section covers refine batch mode, the common case for a tracker corpus. Read `references/scoring.md` for the fan-out pattern and the exact subagent prompt. The essentials:

- **One feature per subagent, run in parallel.** Batching features into one call degrades every verdict. Write each feature to its own JSON file first so each agent reads ~10KB rather than the whole corpus.
- **Each agent reads the rubric itself** — `../govkit-feature-refine/references/gherkin-quality-rubric.md` and that skill's SKILL.md — then scores in batch mode and returns raw JSON.
- **Tell agents explicitly to skip the Stage 1 pause.** `govkit-feature-refine` is built for a conversation about one feature and will otherwise stop and ask for confirmation.
- Collect the verdicts into `scores.json` keyed by feature key.

**Sizing is a separate, optional pass** delegated to `govkit-feature-slice`, which owns the Scenario Complexity Matrix and the MoSCoW slice definitions. Offer it when the user wants size badges, Large-scenario risk, or MVP/V1/V2 slice views. If the corpus already carries slice and size tags on scenarios, render from the tags and skip the fan-out; otherwise fan out per feature exactly like quality scoring, collect judgments into `sizing.json`, and let `compute_size.py` do every piece of arithmetic. `references/scoring.md` has the sizing prompt and the tagged-versus-recommended rule. Size and quality verdicts never mix — a feature can be Approved and huge, or Blocked and tiny, and both facts belong on the card separately.

### 5. Verify — this is a gate, not a lint

```bash
python scripts/verify_scores.py scores.json --features features.json
```

If a sizing pass ran, its gate is the compute step itself:

```bash
python ../govkit-feature-slice/scripts/compute_size.py sizing.json --features features.json
```

It validates every dimension judgment and exits non-zero without writing anything on failure; only its computed output goes to the renderer, never the raw agent verdicts.

Run these before rendering, every time. Batch scoring is done by language models reading a rubric, and the characteristic failure is a reported total that does not match its own dimensions — which silently moves a feature across a decision band. A score of 8.5 reported for dimensions summing to 8.0 is the difference between "Approved" and a conversation.

The script checks: every dimension is 1.0/0.5/0.0, all present and in rubric order, the stated score equals the sum, the decision follows from blockers plus bands, and every ingested feature was scored. It defaults to refine's 10-dimension scale; pass `--scale readiness` for 12-dimension readiness verdicts. It exits non-zero on any failure. If it fails, fix the verdicts — re-run the agent for that feature — rather than rendering anyway. `--fix-sums` will recompute totals and decisions mechanically, but prefer re-scoring when the error suggests the agent was confused rather than sloppy.

### 6. Render

```bash
python scripts/render_map.py -f features.json -s scores.json -z sizing_computed.json \
                             -c config.json -o feature-map.html
```

`-z` is optional and takes the *computed* sizing file. Size renders as a distribution — `2L / 5M / 3S · 41 pts` — because the Large count is the risk signal an average hides. Slice tags render as chips on scenarios, and the release-slice filter works from tagged slices only; batch recommendations appear marked `rec` and never drive grouping.

`references/rendering.md` documents `config.json` — title, lanes, boundary sets, and explicit node positions.

The chain auto-layouts by dependency depth, which is fine for a working session. For anything going in front of stakeholders, hand-set `positions` in the config; a laid-out diagram reads far better than any algorithm will manage, and the escape hatch exists precisely for that.

### 7. Verify the render, then deliver

Screenshot the output and actually look at it before sending. Check that badge counts match `scores.json`, that no chain nodes overlap, and that the page works at mobile width. `references/rendering.md` has a Playwright check script that asserts these.

Deliver with `SendUserFile`. A feature map is something a team returns to, so also persist it as an artifact when a desktop is connected.

## What the badge must never imply

The Development Token is a governance signal, and the fastest way to discredit the whole map is to let the number read as a verdict it was never meant to be. Three things have to survive into the artifact:

**The blocker list is the gate; the score is advisory.** A feature can score 7.5 and still be Blocked because one critical blocker stands. If the map does not make that legible, readers will rank features by number and act on the ranking.

**A near-zero score may mean unreviewable, not bad.** When a spec lives outside the record — in a repo, in a linked doc — the `notAssessable` flag has to reach the badge, with the summary saying plainly that the score rates reviewability of *this record*. Without it the badge libels the most disciplined team in the portfolio.

**These are batch scores, not a refinement.** Carry the caveat into the page itself, not just the chat message that delivered it. The map is a starting point for the 3 Amigos conversation and it should say so where a reader will see it.

## Reading the result

When presenting the map, resist listing eleven verdicts. Cluster the blockers instead — in practice they collapse into a handful of shapes across the whole corpus, and that is the actionable finding. Typical clusters: evaluation criteria carrying `TBD` thresholds on release gates; unresolved product decisions that scenarios actually branch on; missing actor or permission paths; NFRs with no measurable threshold.

Lead with the cluster, name the two or three features where it bites hardest, and state the one decision the user actually has to make. A count of blocked features is a fact; a named pattern is something a team can fix on Monday.

## Bundled resources

| Path | Use |
|---|---|
| `references/ingestion-contract.md` | The `features.json` schema, per-adapter field mapping, Gherkin fidelity and parse-failure handling. Read before ingesting. |
| `../../references/gherkin-authoring-standard.md` | The shared Gherkin authoring standard the corpus is judged against. |
| `../../references/spec-identifiers.md` | The `@rule:` / `@scenario:` identifiers carried through `features.json`. |
| `scripts/requirements.txt` | Pinned ingestion dependencies. Install before running `repo_ingest.py`. |
| `references/scoring.md` | Fan-out pattern, rubric selection, and the subagent prompt. Read before scoring. |
| `references/rendering.md` | `config.json` options, visual grammar, and the render verification script. |
| `scripts/repo_ingest.py` | Walk a repo of feature specs; `--merge` overlays them onto a tracker export. |
| `scripts/verify_scores.py` | The verification gate. Run before every render. |
| `scripts/render_map.py` | Build the HTML map. |

## Related

This skill is for the **corpus**. The other GovKit skills act on one feature at a time, and each owns something this one deliberately does not:

| Skill | Owns | Use instead of this one when |
|---|---|---|
| `govkit-feature-refine` | The 10-dimension collaboration rubric and the 3 Amigos conversation | Working on *one* feature — improving its Gherkin, running refinement, discussing a Development Token |
| `govkit-feature-readiness` | The 12-dimension repo-side gate | Validating *one* approved feature package before coding starts |
| `govkit-feature-slice` | The Scenario Complexity Matrix, MoSCoW slicing, and the `@mvp`/`@v1`/`@v2` tag vocabulary | Sizing and slicing *one* feature with a PM — the conversation where slice tags actually get decided |

The map reads their rubrics; it never restates them. If a rubric changes, the badges change with it — which is the point.

A map is not a substitute for either gate. It shows where the corpus stands so a team knows which feature to open next, and the artifact says so on its face.
