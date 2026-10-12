# Install or replace the initial AIPOS plugins

The new package is `aipos@aipos`, containing all fourteen `aipos-*` skills. The
repository and marketplace source are `Accelerated-Innovation/aipos-plugins`
(renamed from `govkit-plugins`; the old URL redirects).
Everything merged to `main` is released: the version in
`plugins/aipos/.claude-plugin/plugin.json` is the release, and each one is tagged
and listed on the [releases page](https://github.com/Accelerated-Innovation/aipos-plugins/releases).
The sections below say what an existing user must do when updating to a
version. The earlier [1.0.1 release record](release-check.md) is historical.

## Updating to 1.5.2

`verify_vision.py --todo` told the author there was nothing to do while their own record was not ready.

- **An open blocking raise is now a question to close.** `R8` sat on the list of checks excluded as
  "the author cannot close this". Waiting on a reviewer to respond is not the author's to close;
  dispositioning the raise that reviewer left is exactly their job. `R7` stays excluded.
- **Advisory checks reached no list at all.** The todo loop only considered blocking checks, so an
  unanswered advisory raise could sit open indefinitely with nothing anywhere saying so. Failing
  advisory checks now appear under the owner's call.
- **`R8` and `R14` carry actions**, so the list reads as instructions rather than status.

Found while dispositioning raises on the first vision run through the released skill. Rules 2.1.1.

## Updating to 1.5.1

Fourteen defects found by review on the `aipos-product-vision` PR, before it shipped. Four let a
control fail silently open, and the readiness rules now say what the verifier does rather than what
it was meant to do.

- **Learn mode.** A grant block with nothing in it (`learn_mode: {}`) selected Commit mode, bypassing
  every Learn check including the one that would have reported the empty grant. It is now Learn mode
  and fails L1. A grant must also carry `triage_at_grant`, or a risk trigger that goes live after the
  grant produces no promotion signal.
- **Blocking checks that passed on no answer.** `B0: {}` satisfied V13. An unowned sizing gap
  satisfied V4. A linked but unaccepted opportunity satisfied R2. A revision with no predecessor was
  read as a new vision — now R18.
- **Governance gates.** Ratification must name the accountable owner, not just somebody (R16). A
  review counts as a response only with a named responder, a real date and a routed reviewer (R7).
  A blocking raise closes only on a documented disposition type carrying that type's fields (R8).
  `review_by` must parse as a date (L2).
- **Facilitation.** `questions.py` now prints required follow-ups and choice lists, so A4's reason,
  A7's how and basis, and D3's stop-ask-or-hand-off are asked rather than skipped. The
  product-language warning uses word boundaries — it was firing on "storage", "rapid" and "capital".
- **References.** `vision-schema.md` documented v1 block shapes (`A4` as the claims list, `F1i` as
  the statement check); a record written to it failed V3 and V12. It now matches the verifier.

Existing records are unaffected: every shipped fixture already satisfied the stricter rules. Rules
version 2.1.0.

## Updating to 1.5.0

A fourteenth skill, `aipos-product-vision`, writes the PMLC Step 6 Product Vision and takes it
through review and ratification.

- **New skill.** Ask for a product vision, or for Step 6, and it drafts the artifact, routes the
  reviewers and computes readiness. Nothing else changes behaviour; no existing artifact, file
  layout or script is touched.
- **`aipos-product-strategy` no longer answers to "product vision".** Its description said it
  covered one, meaning the vision statement inside a Product Opportunity Brief. Both descriptions
  now draw the line: the brief holds the strategic choices, and the vision is the Step 6 artifact
  with its own review and ratification. A request for a brief still routes to product-strategy, and
  its behaviour is unchanged. If your team says "product vision" and means the brief, say "brief".
- **Two things are computed, and one of them is owned elsewhere.**
  `data/engagement-policy.json` decides which reviewers a risk tier engages, and Security and
  Compliance own it. It ships at `2.0.0-pilot` and is marked `maturity: pilot` - it has been run
  against one real vision, not hardened for client use. Review it before this skill is used on
  client work.
- **Learn mode.** The same artifact at exploration depth, granted by the accountable owner after
  triage rather than chosen at setup. Ratifying any vision records agreement on direction, not
  approval to build.

Nothing to do beyond updating.

## Updating to 1.4.1

The canvas verifier's two study-finding rules now read the graph, not a system name.

- **Transcription.** A `[T]` figure citing a `study_finding` row is refused
  whichever system recorded the finding. Records of a system that records findings
  into the graph are refused too; ReOps is the only such system, named once in the
  verifier (`FINDING_SYSTEMS`). The code stays `T_FROM_REOPS`, so nothing matching
  on it breaks.
- **Source breadth.** Findings of one study count as one source when a
  `study_finding` row in the read carries the lineage entry — no longer because the
  entry starts with `reops:`.

Nothing to do beyond updating. With today's engine, which records findings only from
ReOps, a canvas's errors are unchanged; at most, the source-breadth count and the
`SINGLE_SOURCE` warning can differ for a `reops:` lineage entry that is not a finding
in the read.

## Updating to 1.4.0

A study finding in the Product Definition Graph can now be a canvas baseline. A
finding is a researcher's measured result — metric, value, unit, sample size and
method — recorded in ReOps and held by the graph; the engine returns it as
`measurement` on the finding's `list_evidence` row (engine feature 18).

- **A finding that is the metric is the baseline.** Cite it `[E]` with its own
  value, and the baseline is graph-backed, so Proceed can be recommended. The
  verifier checks the number (`FINDING_MISMATCH`) and, where the canvas unit is
  recognisable, the unit (`FINDING_UNIT_MISMATCH`); the PM confirms it is the
  same measure. A finding that measures a related rate is a candidate: once the PM
  confirms it, the derived figure is `[I]`, citing the finding.
- **No transcription from ReOps.** A `[T]` figure citing a `reops:` record is
  refused (`T_FROM_REOPS`): a ReOps figure reaches the canvas as a finding in the
  graph. The missing-baseline to-do now asks for the finding to be recorded in
  ReOps. `[T]` still works for other sources.
- A finding the graph returns with `measurement: null` backs no number
  (`FINDING_UNREADABLE`).

**If you have saved canvases:** re-run the verifier on any canvas with a `[T]`
figure citing a `reops:` reference. It now fails with `T_FROM_REOPS`; make that
field an evidence GAP with a "record the finding in ReOps" to-do. Canvases without
`[T]` on ReOps records need nothing.

## Updating to 1.3.3

The Solution Framing canvas and the viability brief now say plainly that they make
different decisions. A canvas's Proceed / Pivot / Park is a learning decision made
before any experiment — run its validation plan, rework the approach, or defer.
The viability brief's GO / REVISE / NO-GO decides production investment once the
evidence is in. They no longer map onto each other: a canvas Proceed is cited as
where validation started, never carried into a brief as GO. Approval authority is
unchanged. Rendered canvases add a line saying the recommendation is about the
validation plan.

Also in 1.3.3, for `aipos-solution-framing`: a workshop goes straight into panel 1
at workshop pace (1.3.2's one-question rule now clearly covers set-up only), a
figure is offered for transcription only when its record has a link to read from,
and a volunteered figure is recorded beside its GAP before moving on to the target.
Nothing to do beyond updating; no files move.

## Updating to 1.3.2

`aipos-solution-framing` asks one question per turn while setting up, states the
mode instead of asking for it, and checks a hand-made canvas properly: it
recomputes drawn figures, proposes a candidate baseline the canvas already holds,
and offers a graph-backed rebuild. Nothing to do beyond updating; no files move.

## Updating to 1.3.1

1.3.1 delivers `aipos-map-render` guidance that shipped after 1.3.0 without a
version bump, so installations updated to 1.3.0 before 2026-09-25 do not have it:
journey answers are given only after a render, a scenario under a referenced
Rule is placed through `aipos-workflow-create`, and readers are told how to get
both answers from the page. Nothing to do beyond updating; no files move.

## Product strategy (since 1.2.0)

`aipos-product-strategy` shipped in 1.2.0. Canvas decision language, graph
baseline access, and first-evidence intake are tracked follow-ups, not
prerequisites for using the brief workflow. Existing downstream evidence and
approval rules continue to apply. Its [verification record](plans/2026-09-24-aipos-product-strategy.md)
lists what was checked at release; full Anthropic model evaluations, native
installation, and connected-workflow checks were not run then.

## Updating to 1.3.0

1.3.0 renames four skills and adds interactive journey diagrams. Update as in
[Later updates](#later-updates), then start a new session.

| Before 1.3.0 | From 1.3.0 |
|---|---|
| `aipos-workflow-map` | `aipos-workflow-create` |
| `aipos-feature-map` | `aipos-map-render` |
| `aipos-quarterly-planning` | `aipos-exploration-planning` |
| `aipos-solution-design` | `aipos-solution-framing` |

There are no aliases. Anything that names an old skill — saved prompts, team
docs, hooks, scripts calling `skills/aipos-feature-map/scripts/...` — needs the
new name.

**Solution canvases move folders.** The canvas is now the *Solution Framing*
canvas, saved under `solution-framing/<slug>/` rather than `solution-design/<slug>/`.
To resume an existing canvas, move its folder first:

```bash
git mv solution-design solution-framing   # or plain mv if the folder is not tracked
```

Renders from 1.3.0 on say "Solution Framing" in the canvas header.

**Journey diagrams.** `aipos-map-render` draws L1 / L2 / L3 journey diagrams
from one or more workflows (`render_map.py -w` repeats), showing which scenarios
specify a journey and which journeys a feature change affects. The viewer ships
prebuilt; nothing extra to install. Maps rendered before 1.3.0 are unchanged
until re-rendered.

## New installation

```bash
claude plugin marketplace add Accelerated-Innovation/aipos-plugins
claude plugin install aipos@aipos
claude plugin list
claude plugin details aipos@aipos
```

Start a new session so it loads the updated catalog.

## Replace an early installation

Inspect `claude plugin list --json` to see which old plugins are installed and
at which scope. Uninstall only those present, using their original scope. For
user-scope installations:

```bash
claude plugin uninstall aipos-p1@aipos --scope user
claude plugin uninstall aipos-p2@aipos --scope user
claude plugin uninstall govkit@aipos --scope user
claude plugin marketplace update aipos
claude plugin install aipos@aipos --scope user
claude plugin list --json
claude plugin details aipos@aipos
```

Use `--scope project` or `--scope local` from the corresponding project when
that is where an old plugin was installed. Remove old entries at every scope in
which they remain enabled; do not retain old and new packages together.

Check that only `aipos@aipos` is enabled for this marketplace and its inventory
contains thirteen skills. Start a new session. Existing `.govkit/` artifacts and
feature packages need no conversion. There are no compatibility aliases or
migration scripts.

## Later updates

Refresh the marketplace and update the installed plugin at its installed scope:

```bash
claude plugin marketplace update aipos
claude plugin update aipos@aipos --scope user
```

Maintainers: every change under `plugins/` bumps the version in `plugin.json`,
which is what makes it reach installed users; see
[Releases](../CONTRIBUTING.md#releases). Historical plans and evaluation traces retain
the identities recorded when they were created.
