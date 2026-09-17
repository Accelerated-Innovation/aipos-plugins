# Scenario Sizing and Slicing Rubric

> **Tool-agnostic.** *Generator* = whatever produced the spec. *Tracker* = wherever the feature fields live. Named tools are examples, not requirements.

## Contents

- [Purpose](#purpose)
- [Step 1 — the Scenario Complexity Matrix](#step-1--the-scenario-complexity-matrix)
- [Size bands](#size-bands)
- [Step 2 — MoSCoW release slicing](#step-2--moscow-release-slicing)
- [Size × slice: the risk view](#size--slice-the-risk-view)
- [Splitting oversized scenarios](#splitting-oversized-scenarios)
- [Tag vocabulary](#tag-vocabulary)
- [What size is not](#what-size-is-not)

## Purpose

Two judgments per scenario, kept deliberately separate:

1. **Size** — how big the scenario is, judged from the underlying architecture it touches, not from its line count.
2. **Slice** — which release it belongs to, judged from what the feature needs to fundamentally function.

Size never decides slice. A tiny nice-to-have stays `@v2`; a Large must-have stays `@mvp` — and that combination is precisely the risk the rubric exists to surface.

## Step 1 — the Scenario Complexity Matrix

Score each scenario on three dimensions, **integers 1–3 only**:

| Dimension | Low (1 point) | Medium (2 points) | High (3 points) |
|---|---|---|---|
| **Data & State** | Uses static data; no special session state required. | Requires specific database states or pre-existing accounts. | Third-party data dependencies or complex state transitions. |
| **Integration** | Isolated to a single system component or service. | Integrates two internal systems (e.g., frontend to internal API). | Connects to external vendor APIs, payment gateways, or legacy systems. |
| **UI/UX Steps** | Standard form inputs, simple button clicks, or static redirects. | Dynamic elements, multi-step modals, or conditional UI rendering. | Complex charts, drag-and-drop interfaces, or real-time updates. |

Judging guidance per dimension:

**Data & State** — read the `Given` steps. What must exist before this scenario can run? Static or no preconditions score 1. A precondition naming a specific record, account, or prior state scores 2. Data owned by a third party, or a `Given` describing a multi-step state machine ("an order that has been paid, partially shipped, and disputed"), scores 3.

**Integration** — count the systems the scenario's `When`/`Then` traverse. One component, 1. Two internal systems talking, 2. Anything crossing the organization's boundary — vendor API, payment gateway, legacy system with its own release cycle — 3. External systems score high because their failure modes, auth, and rate limits are not under the team's control.

**UI/UX Steps** — judge the interaction surface's mechanics, not its visual polish. For non-UI features (APIs, batch jobs, CLIs), score the interface analogously: a simple request/response is 1, a multi-step or stateful protocol is 2, streaming/real-time or long-running orchestration is 3.

Scoring rules:

- Judge from the scenario's own text plus the feature's stated context. Never assume an integration or state the spec does not mention.
- Write a note per dimension grounded in the text ("Given references a pre-existing locked account → 2").
- If a dimension is genuinely unknowable from the spec, score what the text supports and record the uncertainty in the note. An unknowable dimension is a spec gap — report it; do not inflate the score to be safe.
- **Never total the points yourself.** `scripts/compute_size.py` computes sums, bands, and rollups. The judgments are yours; the arithmetic is not.

## Size bands

| Band | Points | Reading |
|---|---|---|
| **Small** | 3–4 | Quick to build; automates easily. |
| **Medium** | 5–7 | Standard user flow; average development effort. |
| **Large** | 8–9 | High risk; consider slicing this individual scenario down further. |

A Large band is an instruction, not just a label: propose a split (patterns below) or make the PM accept the risk explicitly.

## Step 2 — MoSCoW release slicing

Map each scenario to a release slice using MoSCoW matched against its Gherkin structure.

**The MVP test is strict:** *can the feature fundamentally function without this scenario?* If yes, it is not `@mvp`. Most scenarios fail this test; a thin MVP is the point.

| Slice | MoSCoW | Contains | Gherkin indicators | Example (login feature) |
|---|---|---|---|---|
| `@mvp` | Must-have | The critical path only — scenarios without which the feature cannot fundamentally function. | The simplest positive happy path. Usually zero error handling, standard default settings, primary user persona. | Authenticating with a basic username and password. |
| `@v1` | Should-have | Vital operational stability, security, and the most common alternative paths. | Common error pathways, critical validation rules (e.g., password strength), primary data variations (often a `Scenario Outline`). | Resetting a forgotten password, locked-account handling, basic form validation. |
| `@v2` | Could-have / nice-to-have | Optimization, advanced UX, edge cases, and secondary personas. V2 *or later*. | Complex third-party integrations, edge-case rules, performance-heavy scenarios, nice-to-have UI enhancements. | Biometric FaceID login, social SSO, "Remember Me" session persistence. |

Slicing guidance:

- **Compliance can promote a scenario.** The table puts security and error handling in `@v1`, but a scenario backed by a compliance, privacy, or safety NFR may be unshippable-without — in some organizations a login feature cannot go live without lockout. When an NFR or a privacy note implies promotion, flag it and let the PM make the call. Release intent is theirs.
- **A tag category never defers risk-critical behavior by itself.** The "Gherkin indicators" column says where a scenario *usually* lands, not what it is worth. Authorization, privacy, safety, regulatory compliance, financial correctness and data loss are judged on the consequence of shipping without them, and that routinely puts an "edge case" in `@mvp`. When a recommendation would defer such a scenario, name what shipping without it risks and make the PM accept it explicitly — never let the category do the deferring silently.
- **A selected scenario brings its obligations with it.** Including a scenario commits the
  behavior it cannot safely run without: the authorization it assumes, the recovery path for the
  failure it can hit, the audit record it must leave. Those are not separate candidates to be
  triaged independently — deferring one leaves the selected scenario unshippable while the slice
  table looks complete. Check **both** places an obligation lives: the `Rule:` the scenario sits
  under (a Rule's obligation is not satisfied by selecting one scenario that illustrates it and
  deferring the one that proves the control), **and the NFRs**, where a compliance, security,
  privacy or retention requirement frequently exists with no scenario of its own. The NFR case is
  the one most easily missed: the Rule check passes and the control still is not there.
- **Dependencies across features count too.** A scenario whose precondition is behavior owned by
  another feature is not in a shippable slice until that behavior is committed somewhere; an
  unstated cross-feature prerequisite is the most common reason an "MVP" cannot ship. Cite the
  most specific reference the input supports — a qualified
  `<source>/<feature-key>#scenario:<slug>` where those identifiers exist, otherwise the feature
  and the behavior in the author's own words, saying which identifiers were not given.
  **Never construct one that was not written down:** a plausible `#scenario:<slug>` for a feature
  you cannot see is a dangling reference that looks authoritative, and `spec-identifiers.md`
  forbids exactly that. Naming the gap is the finding.
- **`Scenario Outline` rows can split across slices.** If the happy row is critical path and the edge rows are not, recommend splitting the outline rather than dragging the whole table into `@mvp`.
- **Untagged is a valid state.** A scenario the PM has not decided on stays untagged; do not default it into a slice to make the table look finished.

## Size × slice: the risk view

Sizing is a **complexity diagnostic, and it is optional**. Scope selection — which behavior a
release contains — is decided on outcome completeness and consequence, never on points, and it
runs perfectly well with sizing switched off.

Where sizing *is* run, what it is for is finding risk, not forecasting cost:

- **Large + `@mvp`** — the highest-risk combination: the smallest shippable version contains the
  riskiest work. Every such scenario gets either a split proposal or an explicit, recorded risk
  acceptance. Never let one pass silently. This is the finding sizing exists to produce.
- **The feature rollup** — band counts, e.g. `2L / 5M / 3S`. Counts, not an average: ten Medium
  scenarios and a feature hiding two Large ones can average the same, and the two Large ones are
  the finding.

**A point total is not a forecast, and per-slice totals are not a roadmap.** "The MVP is 12
points, V1 adds 18" reads as a delivery estimate to everyone who sees it, and it is not one:
complexity points measure how intricate a scenario is to specify and verify, not how long
anything takes. Scenario counts are worse — they say only how many ways someone chose to write
the behavior down. Neither belongs in a release commitment, and a team that plans against them
has substituted a proxy nobody validated for an estimate nobody made.

Report a total only when the PM asks for one, and say what it is not when you do.

## Splitting oversized scenarios

Patterns for taking an 8–9 point scenario apart. After any split, re-size each piece; a split whose pieces are still Large has not split the risk, only the text.

| Pattern | When | How |
|---|---|---|
| **Split by rule** | The scenario proves two business rules at once. | One scenario per rule; each keeps its own observable outcome. |
| **Split by variation** | A `Scenario Outline` mixes the critical row with edge rows. | Happy row becomes a plain `@mvp` scenario; edge rows stay an outline in a later slice. |
| **Split by state** | A heavy `Given` sets up a complex prior state. | One scenario establishes and proves the state transition; a second consumes it with a thin `Given`. |
| **Split by integration boundary** | The critical path routes through a third party. | An `@mvp` scenario proves the behavior against a stubbed boundary; a later-slice scenario proves the live integration. State the stub in the `Given` so the scenario stays honest. |
| **Reduce interaction ambition** | The UI/UX dimension alone drives the score. | A static or simplified interaction in `@mvp`; the dynamic/real-time version as its own `@v2` scenario. |

Splitting restructures scenarios; it never changes what they promise. If a split would alter product intent, that is a refinement conversation (`govkit-feature-refine`), not a slicing edit.

**Behavior-preservation checklist — run it on every split before proposing it.** Each piece must carry across its rule association (still under the `Rule:` the original illustrated), its setup (feature-level `Background`, rule-level `Background`, and its own `Given` steps still reach it), every `Examples` row (distributed, never dropped), every `Then` from the original (asserted by some piece), the boundary case (losing the exact-threshold example while "simplifying" is the most expensive split there is), its identity (`@rule:` / `@scenario:` per `../../../references/spec-identifiers.md` — one piece keeps the original scenario slug, the other gets a new one, and the split is recorded), and its independence (no piece may depend on another having run). Say what moved where; a PM cannot confirm a split they have to reverse-engineer.

## Tag vocabulary

| Tag | Meaning | Set by |
|---|---|---|
| `@mvp` `@v1` `@v2` | Release slice (`@v2` = V2 or later) | The PM's confirmed decision — never applied unconfirmed |
| `@small` `@medium` `@large` | Size band | Derived from `compute_size.py` output; regenerate on every re-size |

Rules:

- Tags go on the line above the `Scenario` / `Scenario Outline` keyword, slice tag first: `@mvp @small`.
- Exactly one slice tag and at most one size tag per scenario. Untagged means undecided, not `@v2`.
- Numeric points live in the sizing JSON, never in tags — bands are stable under small re-judgments, points are not, and CI filters (`--tags @mvp`) want stable names.
- Preserve any tag this skill does not own (`@wip`, `@smoke`, team conventions) exactly as found.
- These are standard Cucumber tags: a team can run `cucumber --tags @mvp` and execute exactly the MVP slice. That is a feature, not a coincidence — the tags survive the tracker→repo handoff and every downstream skill and CI step can read them.

## What size is not

- **Not story points.** Complexity points measure architectural surface, not effort or velocity. Do not feed them into sprint capacity math.
- **Not a quality judgment.** Quality is `govkit-feature-refine`'s rubric. A beautifully written scenario can be Large; a sloppy one can be Small. A feature can score 9/10 on quality and still carry three Large scenarios — those are different findings, and both matter.
- **Not a verdict on the team.** Size describes the work, not the people. A portfolio where everything is Large is a slicing opportunity, not an indictment.
