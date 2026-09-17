# Story Mapping and Feature Derivation

> **Tool-agnostic.** *Tracker* = wherever epic and feature records live. Named tools are examples, not requirements.

## Contents

- [Why map before splitting](#why-map-before-splitting)
- [The backbone](#the-backbone)
- [Horizontal slices](#horizontal-slices)
- [Deriving feature candidates](#deriving-feature-candidates)
- [Scope boundaries](#scope-boundaries)
- [Integrity check 1 — overlap](#integrity-check-1--overlap)
- [Integrity check 2 — vertical-only features](#integrity-check-2--vertical-only-features)
- [Defaults](#defaults)
- [Feature stubs](#feature-stubs)
- [Sizing sanity](#sizing-sanity)

## Why map before splitting

An epic split without a map splits along whatever seam is nearest to hand — usually the architecture. You get "Database layer", "API layer", "UI layer", or "Search service", "Notification service". Each is a coherent engineering unit and none of them can ship on its own, so the first releasable increment is *all of them*.

Mapping the user's journey first forces features to be slices of something usable. The backbone is the tool that makes the wrong split visibly wrong.

## The backbone

The backbone is the sequence of **user activities** in the workflow the epic serves, left to right in the order the user does them.

Rules:

- **4–7 activities.** Fewer and you haven't decomposed the journey; more and you've started listing steps rather than activities.
- **Named from the user's side.** "Submit a claim", not "Claim ingestion API". If an activity name contains a system component, rewrite it.
- **Ordered by the user's time, not by build order.** The backbone is a narrative.
- **One primary persona per backbone.** If two personas have genuinely different journeys, that is two backbones — say so rather than interleaving them into one confusing row.

Present as a simple ordered list. Resist the temptation to draw a grid; the value is in the sequence, and a grid invites an argument about cell contents that the PM does not need to have yet.

**Test:** read the backbone aloud as a sentence. "The adjuster receives a claim, reviews the documents, requests missing information, makes a determination, and notifies the claimant." If it reads as a story, it is a backbone. If it reads as an inventory, it is an architecture diagram wearing a costume.

## Horizontal slices

A slice cuts across the backbone. It answers: *what is the thinnest version of this whole journey that someone could actually use?*

| Slice | Contains | Test |
|---|---|---|
| **MVP** | The critical path across every backbone stage that the journey requires — happy path, primary persona, default settings. | Could a real user complete the journey end to end? If not, it's not an MVP. |
| **V1** | Operational stability: common error paths, validation, the second-most-common variation. | Would you be comfortable leaving this running unattended? |
| **V2** | Optimization, advanced UX, edge cases, secondary personas, heavy third-party integration. | Would the journey survive without this indefinitely? |

**Permissions are not listed above, deliberately.** They used to sit in V1, and a flat category
default is exactly how a required control gets deferred by a table rather than by a decision.
Authorization, privacy, safety, regulatory compliance, financial correctness and data loss are
placed by **the consequence of shipping without them**, which routinely puts an "edge case" in
MVP. A login feature that cannot legally go live without lockout has lockout in its MVP, whatever
the category says. This is the same rule `govkit-feature-slice`'s rubric applies scenario by
scenario — see *"A tag category never defers risk-critical behavior by itself"* — and the two
must not drift apart.

Four rules that catch most mistakes:

1. **A slice spans stages.** If a proposed slice touches one backbone activity, it is a layer, not a slice. Rework it.
2. **A slice delivers a usable outcome.** "The data model is complete" is not an outcome anybody outside the team can use.
3. **A slice ties to a success metric.** If the epic states success metrics, name which one each slice moves. If a slice moves none of them, either the slice is wrong or the metrics are — surface it either way.
4. **A slice carries the controls its own behavior requires.** Including a scenario pulls in what that behavior cannot safely ship without — the authorization it assumes, the recovery path for the failure it can hit, the audit record its Rule obligates. Deferring those to a later slice leaves the earlier one unshippable while looking complete on the map, which is the failure this check exists to catch.

MVP discipline is the whole point. The strict test — *can the journey fundamentally function without this?* — puts most things outside MVP, and a thin MVP is the desired outcome, not a sign of under-scoping.

## Deriving feature candidates

Features hang off the backbone. Each one owns a durable responsibility within one or two adjacent activities, for one slice.

Good candidates:

- **Action-oriented names.** "Route high-value claims to a senior adjuster", not "Routing".
- **A durable responsibility.** The feature would still make sense as a unit six months later. "Phase 2 work" is not a responsibility.
- **One or two adjacent backbone activities.** A feature spanning the entire backbone is an epic; a feature spanning nothing is a task.
- **Sized to roughly two sprints.** See [Sizing sanity](#sizing-sanity).

Anti-patterns to coach away from:

| Anti-pattern | Looks like | Say instead |
|---|---|---|
| Layer feature | "Claims API", "Adjuster dashboard UI" | "What can the adjuster *do* when this ships?" |
| Bucket feature | "Reporting", "Admin", "Miscellaneous" | "What's the first report someone actually asks for?" |
| Phase feature | "Phase 2", "Fast follow" | "That's a slice, not a feature — which capability is in it?" |
| Enabler-only feature | "Set up the vector store" | "Which user-visible feature needs this? Fold it in as that feature's first scenario." |

The enabler case deserves care: sometimes real infrastructure genuinely precedes user value. Don't pretend otherwise. Name it as an enabler, attach it to the feature that consumes it, and let the PM decide whether it warrants its own record. What you must not do is let a wall of enabler features become the MVP.

## Scope boundaries

Every candidate carries **one line describing what it owns**. This is the single highest-value output of Epic mode, because it is what makes overlap visible.

Format: `<Feature name> — owns <responsibility>, up to <boundary>. Does not own <the adjacent thing>.`

> **Route high-value claims** — owns the routing decision and its audit trail, up to assignment. Does not own the adjuster's queue display.

Vague boundaries ("owns claims handling") are how two teams build the same thing twice. Push for the second half of the sentence.

**Boundaries become the dependency chain.** When a boundary says "A owns the routing decision, B consumes it", that is a producer/consumer edge: A *produces* `routing-decision`, B *consumes* it. Carry these into each feature's `## Produces` / `## Consumes` sections (kebab-case artifact names, per `feature-template.md`) — `govkit-feature-map` draws its chain from exactly these, and a boundary left as prose is an edge the map can't see.

## Integrity check 1 — overlap

Two features overlap when both could reasonably claim the same responsibility. Read the scope boundaries against each other, pairwise.

Signals: the same noun as the object of both boundaries · one feature's "does not own" is absent from any other feature's "owns" (an orphan responsibility) · two features that would both write the same field.

When found, name the responsibility and propose an owner:

> These two look like they overlap on <responsibility>. I'd suggest <A> owns it and <B> consumes it, so each has a clean boundary. Does that match how you'd split it?

Resolve before creating anything. Overlap discovered after the stubs exist means renaming records other people have already linked to.

## Integrity check 2 — vertical-only features

A vertical-only feature has depth without journey: sophisticated capability that never spans enough of the backbone to deliver a usable outcome.

Signals: the feature touches one backbone activity and nothing downstream consumes it in the same slice · the description is about how well something is done rather than what becomes possible · you cannot write a user story for it whose "so that" is an outcome rather than a restatement.

> This is a lot of depth without enough of the journey to be usable on its own. I'd suggest widening the scope so it lands a complete outcome — or moving the depth to a later slice and keeping a thinner version in MVP.

## Defaults

Propose defaults so the PM confirms rather than composes:

| Field | Default from |
|---|---|
| **Release** | The slice the feature belongs to, mapped to the team's release naming |
| **Type** | The epic's type, or the team's convention; `Feature` when nothing is known |
| **Owner** | The epic's owner |

> I'll apply these defaults unless you prefer otherwise.

Allow per-feature overrides. If the tracker's allowed values are unknown, do not guess them — fetch the field metadata (`references/tracker-adapters.md`) or leave the field unset and say so.

## Feature stubs

A stub carries exactly:

- Name
- Epic link
- Release
- Type
- Owner
- One-sentence description

And nothing else. No acceptance criteria, no NFRs, no Definition of Done, no privacy text.

This is deliberate. A stub padded with unreviewed generated detail looks finished, so nobody refines it, and the unreviewed Gherkin ends up in a sprint. An empty stub is honestly empty and invites the Feature-mode conversation that produces something real.

**Create the MVP slice's stubs first; defer V1/V2 as the default.** Stubs for features two slices out are inventory — they age, get renamed, and invite premature work. The story map already records what the later slices contain, so nothing is lost by waiting. The PM can override and create the full set; recommend the deferral once and take their answer.

The one-sentence description should be the scope boundary, trimmed. It has already done its job once.

## Sizing sanity

Target roughly two sprints per feature, unless the PM consciously chooses otherwise.

This is a smell test, not arithmetic. Signals a candidate is too big: more than two backbone activities · "and" in the name joining two capabilities · a boundary sentence that needs a semicolon · more than one persona doing genuinely different things.

Say it once and move on:

> This one might be bundling a couple of features — worth splitting? Happy to carry on if it's deliberate.

Real sizing is `govkit-feature-slice`'s job, on real scenarios, with the Scenario Complexity Matrix. Do not attempt point scores here; a number invented before the scenarios exist is a number the team will quote back for months.
