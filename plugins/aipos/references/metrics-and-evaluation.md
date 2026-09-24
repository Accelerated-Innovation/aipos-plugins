# Success Metrics and GenAI Evaluation Criteria

> Metrics are what the epic will be judged by. Evaluation criteria are what every feature under it will be gated by. Both are contracts; write them like it.
>
> **Shared** by `aipos-epic-create` (epics) and `aipos-solution-design` (the Solution Design canvas). The canvas applies it with the exceptions its `panel-rubrics.md` names — chiefly that facts come from the Product Definition Graph, never from the PM.

> `aipos-product-strategy` also reuses this guidance with the adaptations in its
> `SKILL.md`: an initial hypothesis can retain unknowns, segment choices can evolve,
> and a single initial outcome is sufficient. Epic and canvas contracts are unchanged.

## Contents

- [The three-part metric](#the-three-part-metric)
- [Choosing metrics](#choosing-metrics)
- [Pushing for numbers](#pushing-for-numbers)
- [Business objective alignment](#business-objective-alignment)
- [GenAI evaluation criteria](#genai-evaluation-criteria)
- [The evaluation dimensions](#the-evaluation-dimensions)
- [Thresholds](#thresholds)
- [Golden test cases](#golden-test-cases)
- [Evaluation cadence and gates](#evaluation-cadence-and-gates)
- [epic_eval_criteria.yaml](#epic_eval_criteriayaml)

## The three-part metric

Every success metric needs all three:

| Part | Question | Without it |
|---|---|---|
| **Baseline** | Where are we today? | Nobody can tell whether the target is ambitious or already met |
| **Target** | Where do we need to be? | It's a direction, not a goal |
| **Observation method** | How will we know? | It's unfalsifiable, and will be quietly dropped at review time |

```markdown
| Metric | Baseline | Target | How measured |
|---|---|---|---|
| Median time to first adjuster action | 9.5 hours (FY25 claims log) | < 2 hours | Claims log, monthly median |
| SLA breaches on claims > $250k | 6 (FY25) | 0 | SLA breach report, quarterly |
| Claims with document set auto-assembled | 0% | 80% | Assembly job telemetry |
```

A missing baseline is not a reason to drop the metric. Write it with the baseline marked unknown and list it in Open Questions — *"we don't currently measure this"* is frequently the most actionable line in an epic, because it names the first thing to instrument.

## Choosing metrics

**Three to five.** Fewer and the epic is under-specified; twelve and nobody knows which one matters when they conflict.

Prefer:

- **Outcome over output.** "Time to first action" beats "number of features shipped". Output metrics are always met and never mean anything.
- **Metrics that mirror the quantified impact** from the problem statement. If the problem costs 22 minutes per claim, minutes recovered is the natural metric — and the symmetry is a check that the epic is internally coherent.
- **At least one counter-metric** where the epic could plausibly cause harm. An epic that speeds up triage should track determination quality too, or it will optimize for speed at the cost of correctness and the metrics will show a triumph.

Push back once on:

| Metric type | Problem | Ask |
|---|---|---|
| Adoption-only ("80% of adjusters use it") | Usage isn't value; mandated tools hit 100% adoption and change nothing | What changes for them once they're using it? |
| Satisfaction-only | Lags, and moves for unrelated reasons | Is there a behavioral measure that moves first? |
| A metric nobody owns | Won't be reported | Who reports this, and to whom? |
| A metric that can't move within the horizon | Unfalsifiable in practice | What leading indicator moves inside two quarters? |

## Pushing for numbers

Once per metric, then accept the answer:

> Do we know roughly where that sits today? Even an order of magnitude helps — we can mark it as an estimate.

Offering "an estimate is fine" is what usually unblocks this. PMs withhold numbers because they fear being held to a guess; making the provenance explicit removes the fear and gets you a usable figure.

Mark provenance the same three ways the impact section uses — Pillar 2's marks: **`[E]`** measured (source + date), **`[I]`** estimated (whose), **`[A]`** unknown (a gap). Never launder an `[I]` into an `[E]`.

## Business objective alignment

> Which business objectives or OKRs does this epic support?

Map to the workspace's actual objectives where they're exposed. Then apply one test:

> **How does this epic move that objective?**

If the answer is a chain of three or more inferences, the alignment is decorative. Say so once — an epic aligned to everything is aligned to nothing, and the conversation is far cheaper now than in a portfolio review where the epic is competing for funding.

One or two genuine alignments beat five aspirational ones.

## GenAI evaluation criteria

GenAI mode only.

**These are inherited by every feature under this epic.** `aipos-feature-create` reads them, applies the relevant subset to each feature, and writes them into that feature's `eval_criteria.yaml`, where `aipos-feature-readiness` gates on them. A number set here becomes a release gate two skills downstream.

Say that out loud when setting them:

> These thresholds will be inherited by every feature under this epic and become release gates. Worth setting deliberately rather than aspirationally.

PMs set very different numbers once they understand they are writing a contract rather than a hope. That sentence is the single highest-value thing this section does.

## The evaluation dimensions

Ask which matter here — not all do, and criteria for dimensions the epic doesn't exercise are noise that trains people to ignore the section.

| Dimension | Measures | Typical method |
|---|---|---|
| **Groundedness** | Output traceable to source material | LLM-as-judge or citation check over a labelled set |
| **Correctness / accuracy** | Output is factually right | Labelled eval set, exact or graded match |
| **Retrieval accuracy** | The right context was fetched | Recall@k / precision@k against known-relevant documents |
| **Safety** | No harmful, abusive, or prohibited output | Safety classifier plus red-team set |
| **Privacy** | No sensitive data in output | PII detector over eval outputs |
| **Tone / style** | Matches the required voice | Rubric-graded sample, human or judge |
| **Reasoning** | Multi-step conclusions hold | Step-level review on a reasoning set |
| **Tool use** | Correct tool, correct arguments, correct handling of failure | Trace assertions over a scripted set |
| **Latency** | User-perceived response time | p50/p95 end to end, including model time |
| **Cost** | Spend per action or per period | Token accounting over the eval set |

Two that get forgotten: **refusal rate** (a model that refuses everything scores perfectly on safety and is useless) and **degradation under load** (quality measured on a quiet afternoon is not the quality users get).

## Thresholds

Every criterion needs a **method** and a **threshold**. A dimension without a threshold is a topic, not a gate.

Ask directly:

> What's the number, and what happens if we miss it — does it block the release, or do we ship and track it?

That second half establishes `gate: blocking` versus `gate: advisory`, and it's the part that makes the threshold real.

**Never supply a threshold yourself.** Not `0.95`, not `p95 < 3s`, not "industry standard". If the PM doesn't have a number:

```yaml
pass_threshold: "TBD"
```

and list it in Open Questions as a gap. An invented threshold is worse than a blank one in a specific, predictable way: the blank prompts a conversation, and the invented number gets implemented, gated on, and defended in a review by someone who assumes a human chose it.

Where an organizational standard exists ("all customer-facing GenAI meets the group's safety baseline"), cite the standard rather than restating its numbers — then the epic stays correct when the standard changes.

## Golden test cases

> Are there specific cases the system must get right — or past failures it must never repeat?

The best sources, in order:

1. **Past incidents.** A production failure is a golden test case that already proved it matters.
2. **Known-hard cases** the team argues about — the ambiguous claim, the multilingual document, the 300-page attachment.
3. **Regulatory or contractual musts.**
4. **The boring happy path**, so a regression can't hide behind interesting cases.

Name them here; building the eval set is the delivery team's job, and the epic's contribution is knowing what belongs in it.

## Evaluation cadence and gates

> Should evaluation run continuously, or only before release?

| Cadence | Fits | Cost |
|---|---|---|
| **Pre-release only** | Stable prompts, infrequent model changes | Cheap; blind to drift between releases |
| **Continuous (CI)** | Active development, frequent prompt changes | Every change gated; needs a maintained eval set |
| **Scheduled (e.g. nightly/weekly)** | Vendor-hosted models that change under you | Catches drift; delayed signal |
| **Production sampling** | High-volume, high-risk output | Real distribution; needs sampling and review capacity |

Most GenAI epics need at least two: something in CI on change, and something scheduled to catch vendor-side drift. Vendor model updates are the drift source teams most consistently fail to plan for — the prompt didn't change, the model did.

Then split the criteria: which must be met **before MVP release** (gates) and which are targets for later phases. That split is what makes the MVP scope honest.

## epic_eval_criteria.yaml

GenAI mode. Same schema as the feature-level `eval_criteria.yaml`, so inheritance is a copy rather than a translation:

```yaml
evaluation_criteria:
  - id: EPIC-E1
    type: groundedness
    rule_link: "Generated text is traceable to source claim documents"
    method: "LLM-as-judge over a labelled eval set"
    data_source: "Labelled eval set, minimum 200 items"
    pass_threshold: ">= 0.95"
    evidence: "Eval report attached to the PR"
    owner: "QA / evaluation owner"
    gate: blocking
    applies_to: all_features

  - id: EPIC-E2
    type: privacy
    rule_link: "No claimant PII in text shown outside the claims team"
    method: "PII detector over eval set outputs"
    data_source: "Eval set outputs, full run"
    pass_threshold: "0 detections"
    evidence: "Detector report attached to the PR"
    owner: "QA / evaluation owner"
    gate: blocking
    applies_to: all_features

  - id: EPIC-E3
    type: cost
    rule_link: "Assisted actions stay within the FY26 budget envelope"
    method: "Token accounting over the eval set"
    data_source: "The eval set, priced at current rates"
    pass_threshold: "<= $0.04 per assisted action"
    evidence: "Cost report in CI artifacts"
    owner: "Eng lead"
    gate: advisory
    applies_to: all_features
```

The `data_source` / `evidence` / `owner` fields match the feature-level schema and are what the delivery gates check ("thresholds, data, evidence, and owner") — filling them here means every inheriting feature gets them for free. Owners named at the epic level are default owners; a feature can override.

`applies_to` is the one field the feature-level schema doesn't carry — `all_features`, or a named subset. It exists because epic criteria are inherited: without it, every feature inherits every criterion, and a PM ends up gating a settings page on retrieval accuracy.

Use `EPIC-` prefixed IDs so an inherited criterion is traceable to its origin once it appears in a feature package.
