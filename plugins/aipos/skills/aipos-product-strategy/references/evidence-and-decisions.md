# Evidence and decisions

## Attribute each claim

Use the existing AIPOS marks, supplemented by plain-language source limits:

| Kind | Recording rule |
|---|---|
| Observed evidence | `[E]` with the supplied or actually read source ID/location, date or unknown date, population, period, and what was observed. |
| Attributed report | State who reported what and whether the underlying observation is available. A read transcript can establish `[E] participant reported X`; it does not establish X as an independently measured fact. Preserve estimates as `[I]` or unsupported beliefs as `[A]`, even inside an evidence-bearing document. |
| Inference or estimate | `[I]`, who inferred it and from which inputs, with limits. Do not replace its source's uncertainty with stronger wording. |
| Assumption or unknown | `[A]`, the proposition to test or the missing value. Unknown is not zero and not evidence against the proposition. |
| Received transcription | Keep `[T]`, its source and attribution, when passed from the canvas. It is not `[E]` or graph-backed; do not relabel it to pass a downstream check. |

An inaccessible link establishes that a reference was supplied, not that its
content was inspected or its claims verified. Preserve original identifiers and
disclose access limits. Multiple rows or excerpts from one study are not multiple
independent studies. Missing dates stay unknown rather than becoming stale by
assumption. Contradictory observations belong beside supporting ones.

Example: an interview note supports “three participants described invoice delays
[E, INT-7]”; a sales lead's “probably half the market” remains an attributed estimate
[I, INT-7]. Neither establishes a measured market prevalence. A draft acquisition
target is a proposed choice, not observed demand.

No source is required for a PM to propose a vision, segment, target, or concept.
Label these **proposed** or **adopted** and attribute adopted choices to the supplied
decision. The factual premise behind a choice still needs `[E]`, `[I]`, or `[A]`.
Do not invent customers, findings, competitors, quotes, market sizes, baselines,
targets, budgets, or approvals. Suggestions for methods and choices are welcome
when visibly proposed, but fabricated factual inputs are not.

## Evidence can begin outside the graph

Accept attributable research, notes, or source documents the user supplies.
Read connected sources when relevant and available, without requiring a graph,
tracker, or repository. Do not pretend a source is graph-backed because its URL
appears in the brief. Keep the source's marks and identifiers in downstream use.

New research returns via `aipos-rapid-validation` as findings with provenance.
Identify the intended ReOps/research intake or other system of record if known,
and the handoff needed to record them. Prepare an intake draft when requested;
do not claim ingestion from saving a local file. If the destination or connector
is unknown, record it as an integration gap and continue with attributable local
evidence. Graph-backed planning waits for its own required reads.

## Four distinct decision states

| State | What establishes it | What it does not establish |
|---|---|---|
| Agreement on the strategy hypothesis | Attributed agreement on named choices and revision | That assumptions are true or any spending is authorized |
| Authorization for bounded learning | Explicit authority for an experiment or exploration, with agreed limits where supplied | Permission for production scope or unlimited exploration |
| Evidence supporting further investment | Findings relevant to the tested risks, with limitations and a recommendation | A recorded investment decision or approval to build |
| Approval of production scope | Applicable accountable authority's decision against the exact reviewed commitment | Created by a strategy brief, an experiment plan, or a GO recommendation |

Report only the states relevant to the request; keep them separately named. If
authority, limits, or a record reference are not supplied or verified, say unknown
or not established by the available information. “No approval supplied” does not
assert that no approval exists anywhere. Reuse supplied authorization within scope;
do not repeatedly ask for it. “Looks good” confirms the current discussion, not
unspecified spending, system writes, or production scope.

Recommend learning with a missing baseline when that is the right next step.
Identify the current-workaround comparison, pilot measurement, or absolute test
criterion and its observation method. If no criterion has been adopted, mark it
proposed or unknown and carry that decision into the experiment handoff. The
strategy brief can be useful before the study is authorized or ready to run.
