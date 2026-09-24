---
name: aipos-product-strategy
description: "Create, assess, or revise a Product Opportunity Brief covering product vision, target segment, needs, differentiation, and business viability. Use for starting a new commercial or internal product, choosing its strategic focus, or changing strategy after research or product results. Specific experiments belong to rapid-validation; initiative canvases to solution-framing; epics to epic-create."
---

# AIPOS Product Strategy

## Purpose

Help a PM and cross-functional team make, test, and evolve the choices behind a
product. Own one **Product Opportunity Brief**: the current product vision and
strategy hypothesis, its evidence, and the next decision. A useful first draft
can start with an idea and no customers, graph, measurements, tracker, or backlog.

## Scope and handoffs

Use for a new product, assessment of an existing strategy, or strategy revision
after research or product results. Support commercial and internal products.
Work with the PM, design, engineering, and relevant business stakeholders; do not
invent their participation or treat the PM as the authority for every decision.

Read `../../references/strategy-handoff.md` when work crosses skill boundaries.
Delegate experiment artifacts and findings to `aipos-rapid-validation`, an
initiative canvas to `aipos-solution-framing`, graph-based capacity allocation to
`aipos-exploration-planning`, and an explicitly requested epic to `aipos-epic-create`.
An explicit request for one of those outputs does not require this brief first.
Behavior authoring, refinement, release selection, and readiness keep their owners.
This skill does not implement analytics, a full roadmap, or production software.

## Start from the available context

Read the supplied brief and evidence before questioning the PM. Reuse the known
product type, users, constraints, decisions, and source identifiers. If there is
an existing canonical brief, assess or revise it in place within the requested
scope; do not create another strategy document beside it.

Choose the mode from the request:

| Mode | Work |
|---|---|
| Start | Turn the idea into a concise draft with explicit strategic choices and unknowns. |
| Assess | Identify the consequential weak choices, unsupported claims, contradictions, and next decision. Rewrite only if requested. |
| Revise | Compare new evidence with the current hypothesis, propose the affected changes, and preserve the decision history and downstream references. |

Ask one focused primary question at a time when discussion is wanted, choosing
the question that would most change direction. Do not repeat supplied answers.
When asked for a draft now, produce it with unknowns instead of requiring an
interview to finish first. End with the most useful unresolved question or next
action. A missing graph is a source limitation, not a prerequisite failure.

## Frame and challenge the strategy

Read `references/brief-template.md` to compose the brief and
`references/strategy-review.md` when comparing choices, assessing a strategy, or
revising it from results. Keep the main brief approximately one or two pages;
link detailed evidence and assumptions only when they would crowd out the choices.

Cover purpose, initial segment and exclusions, need and current alternatives,
strategic concept and switching rationale, opportunity and fit, business
viability, desired outcomes, critical uncertainties, and the next learning decision.
Make the consequence of a choice visible: whom we serve first, what we defer,
and what evidence would cause us to reconsider. Do not silently select among
several segments. A proposed focus is useful; an invented agreement is not.

Use `../../references/problem-framing.md` for separating a need from a proposed
solution and for evidence limits. **Product-strategy adaptations:** a selected
technology belongs in the concept or constraints; an unproven cause stays a
hypothesis. Missing roles, quantities, or a complete problem statement do not
block an initial draft. Segment choices can change as evidence changes; review
the consequences instead of importing the epic's locked-persona rule.

Use `../../references/metrics-and-evaluation.md` for outcome over output,
observation methods, and provenance. **Product-strategy adaptations:** one initial
outcome is enough; do not require three to five metrics or a numeric vision.
Keep an unknown baseline or target unknown. A current-workaround comparison,
pilot measurement, or appropriate absolute success criterion can guide learning.
Any suggested threshold is a proposal until adopted. Do not create production
evaluation schemas or inherit experimental thresholds as release gates.

## Evidence and decision discipline

Read `references/evidence-and-decisions.md` before recording claims or decision
status. Use `[E]`, `[I]`, and `[A]` with claim-level attribution and limits. Preserve
reported versus directly observed evidence in words; a source link alone does
not establish the claim. Preserve a received `[T]` as a transcription with its
limits, never promote it to graph-backed evidence.

Record proposed and adopted choices separately from factual provenance. Distinguish
agreement on a strategy hypothesis, authorization for bounded learning, evidence
supporting further investment, and approval of production scope. Recommendations
and a well-written brief establish none of those authorities by themselves.

For the most consequential unresolved assumption, name what observation would
change the decision and recommend an appropriate learning method. Include only
agreed owner, budget, and horizon values; leave others unknown or explicitly
proposed. Delegate the detailed experiment to rapid-validation. Missing baseline
evidence can be exactly what that experiment is intended to collect.

## Review results and maintain the brief

When new evidence arrives, check its population, period, measure, and limitations
against the hypothesis being tested. Explain what it supports, contradicts, or
leaves unanswered. Do not declare the whole strategy validated from one result.
Recommend retaining, changing, pausing, or ending the relevant bet and identify
the decision owner when known. Mark unadopted strategy changes as proposed.

Preserve the existing brief reference, update its revision, and record a short
change note linking the evidence and affected choices. Identify initiatives,
experiments, or commitments that need review; never silently rewrite their scope
or approvals. Product results return here for strategy interpretation even when
their collection and analysis happen in another system.

## Deliver and save

Deliver the requested inline assessment or brief. For a new local artifact, the
default is `strategy/<product-slug>/product-opportunity-brief.md`; use an existing
canonical location when supplied. A heading or local label is not a graph ID.
Use a revision and section anchors for downstream references. Keep detailed
evidence in its source, or a linked companion register when needed, rather than
copying the strategy into every experiment or epic.

Finish with the evidence limitation that matters, decision sought, and the next
owning skill. For a handoff, use the shared contract. Respect prior authorization
and inline-only requests. Save local files when requested; external writes need
authorization for their destination and scope. Never claim a write, graph ingest,
customer contact, experiment, or approval that did not occur.

## Influences

`references/sources.md` attributes the primary sources and distinguishes their
principles from AIPOS's brief, provenance, decision, and handoff conventions.

## Examples

- “We have an idea for a commercial product and no research. Draft our first brief.”
- “Assess the strategy for our internal service without rewriting it yet.”
- “Our pilot contradicts the target-segment hypothesis. Revise the strategy.”
