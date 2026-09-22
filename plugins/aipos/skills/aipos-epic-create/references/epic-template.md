# Epic Template

> These field names are `aipos-feature-create`'s `epic:` input contract. Writing them means the handoff needs no translation.

## Contents

- [The package](#the-package)
- [epic.md](#epicmd)
- [Field rules](#field-rules)
- [Elevator pitch](#elevator-pitch)
- [Initial scope / MVP](#initial-scope--mvp)
- [Risks and mitigations](#risks-and-mitigations)
- [Non-functional requirements](#non-functional-requirements)
- [Open questions and gaps](#open-questions-and-gaps)

## The package

```text
epics/<key>/
  epic.md                    # always
  epic_eval_criteria.yaml    # GenAI mode only
```

`<key>` is the tracker key when one exists (`CLM-88`), otherwise a slug from the epic name.

`aipos-feature-create` writes the derived features to `features/<key>/` and its story map alongside this epic as `epics/<key>/story-map.md` — so the epic, the reasoning that split it, and the features it produced stay traceable to each other.

**Never invent a field.** If the PM wants something the template doesn't hold, put it in Open Questions and say where it should properly live. Template drift is how two epics stop being comparable, and comparability is most of what a portfolio view is for.

## epic.md

```markdown
# <Epic Name>

| | |
|---|---|
| **Key** | <tracker key, or `—`> |
| **Target release** | <release or timeframe> |
| **Category / product area** | <area> |
| **Owner** | <owner> |
| **GenAI** | yes / no |
| **Validation Decision** | <go / not run — with a link if one exists> |
| **Status** | Draft — not yet broken into features |

## Elevator pitch

<one paragraph — see below>

## User problem(s)

The problem of <X> affects <Y>, resulting in <Z>, and solving it will lead to <benefits>.

### Impacted personas

| Persona | Primary? | How the problem reaches them |
|---|---|---|

### Quantified impact

| Impact | Measure | Provenance |
|---|---|---|
| <what it costs> | <number> | `[E]` measured (source, date) / `[I]` estimated (whose) / `[A]` assumption |

## Alignment to business objectives

| Objective / OKR | How this epic moves it |
|---|---|

## Success metrics

| Metric | Baseline | Target | How measured |
|---|---|---|---|

## GenAI evaluation criteria

<GenAI mode only — the table form of epic_eval_criteria.yaml>

| ID | Type | Threshold | Gate | Applies to |
|---|---|---|---|---|

**Golden test cases:** <named cases the system must get right>
**Evaluation cadence:** <when evaluation runs>

## Evidence and insights

### Qualitative
- <source, size, date> — <what it establishes>

### Quantitative
- <source, period> — <the measure>

## Initial scope / MVP

**In scope:**
- <capability>

**Out of scope:**
- <capability> — <where it lives instead>

**Evaluation gates for MVP release:** <GenAI mode — which thresholds must be met before shipping>

## Risks and mitigations

| Risk | Category | Mitigation |
|---|---|---|

## Non-functional requirements

| Dimension | Requirement | Threshold or standard |
|---|---|---|

## Open questions and gaps

- <every unmeasured baseline, unevidenced claim, and TBD threshold>
```

The **Status** and **Validation Decision** lines carry governance state on the artifact itself, where it survives being pasted somewhere without context. An epic whose Validation Decision reads *not run* is not blocked — it is honestly labelled.

## Field rules

| Field | Rule |
|---|---|
| **Epic Name** | Outcome-focused. "Cut adjuster time-to-first-action" beats "Claims triage improvements" |
| **User Problem(s)** | **No solutions, ever.** See `../../../references/problem-framing.md` |
| **Personas** | Named roles, one marked primary. Locked once confirmed |
| **Success Metrics** | 3–5, each with baseline, target, method |
| **Evidence** | Dated, sized, and honest about what it doesn't establish |
| **Initial Scope** | Both halves. Out of scope non-empty |
| **Risks** | Paired with mitigations, or explicitly marked unmitigated |
| **NFRs** | Epic-wide standards, not feature-specific thresholds |
| **Open Questions** | Required. An empty list usually means insufficient examination |

## Elevator pitch

One paragraph, assembled from what the interview already produced — not a fresh question:

> For **[persona]** who **[problem]**, the **[epic name]** delivers **[capability]** so that **[benefit]**. Unlike **[the status quo]**, it **[key difference]**.

> For **regional adjusters** who **open every claim to find out whether it's urgent**, **claims triage** delivers **an ordered worklist with the document set already assembled** so that **the right claim gets worked first**. Unlike **the shared inbox**, it **makes routing an explicit, auditable decision instead of whoever-notices-first**.

Write it after the problem statement and personas exist. Asking a PM to write an elevator pitch cold produces marketing copy; assembling it from their own confirmed answers produces something true.

The "unlike the status quo" clause is the one that earns its place — it forces an answer to *why doesn't the current approach work*, which is where weak epics fall apart.

## Initial scope / MVP

Two lists, both required.

**In scope** — the capabilities the MVP must have to deliver meaningful value. Capabilities, not features: `aipos-feature-create` derives features from this, and pre-deciding them here skips the story mapping that catches the wrong split.

**Out of scope** — what this epic deliberately does not do, and where it lives instead ("later phase", "different epic", "not doing"). The third answer is the most valuable and the least written down.

This is also where a **pre-decided solution** belongs. When an executive commitment or compliance mandate has fixed the approach, record it here as a decision with its source — never in the problem statement.

One test before moving on: does anything in the MVP move a stated success metric? If not, either the scope or the metrics are wrong. Say which you suspect.

## Risks and mitigations

Walk five categories; adoption and compliance are the two most often forgotten.

| Category | Typical risks |
|---|---|
| **Delivery** | Dependencies, sequencing, team capacity, unproven integrations |
| **Technical** | Legacy constraints, data quality, scale, migration |
| **Compliance** | Regulatory approval, audit, data residency, retention |
| **Adoption** | Workflow change, training, trust — acute for GenAI features |
| **Data** | Availability, quality, licensing, PII exposure |

A mitigation must be an action someone could take. "Monitor closely" is not a mitigation; recording the risk as **unmitigated** is more honest and more useful, because it surfaces at review instead of hiding behind a verb.

GenAI epics carry two risks worth prompting for directly: **model drift** (vendor changes the model under you) and **trust collapse** (one bad output in front of the wrong person ends adoption regardless of aggregate quality).

## Non-functional requirements

Epic-level NFRs are the standards every feature must meet or explicitly except itself from. Feature-specific thresholds belong to `aipos-feature-create`.

```markdown
| Dimension | Requirement | Threshold or standard |
|---|---|---|
| Security | Regional access control on all claims data | Group access standard SEC-04 |
| Compliance | EU claims data does not leave the EU region | Absolute |
| Reliability | Available during regional business hours | 99.5%, nightly maintenance permitted |
```

Categories — the same ten areas the delivery gates review: **Performance · Security · Privacy · Reliability · Observability · Accessibility · Data quality · Compliance · Cost · Supportability**. (Scalability lands under Performance or Reliability.)

GenAI mode adds: **latency and token cost constraints · model and vendor constraints** (permitted models, data residency, no-train guarantees) **· data handling · observability and drift monitoring**.

Prefer citing an organizational standard over restating its numbers — the epic then stays correct when the standard changes. Where no standard exists and the PM has no number, record the requirement with the threshold marked unknown rather than inventing one.

## Open questions and gaps

Required, and required to be honest. It collects:

- Unmeasured baselines ("we don't currently measure time-to-first-action")
- Claims asserted without evidence
- `TBD` evaluation thresholds
- Decisions deferred to another owner
- Anything the PM said they'd need to check

This is the most actionable section in the epic. It is the list of what to find out first, and it is what `aipos-feature-create` reads to avoid deriving features from assumptions nobody has tested.

If the list comes out empty, say so — an epic with no open questions has usually not been examined hard enough, and saying that out loud invites the examination.
