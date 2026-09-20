# Plugin evaluation follow-ups — 2026-09-20

**Historical checkpoint:** the results below describe PR #33 before substantive closure. See the [current closure report](2026-09-20-substantive-closure.md) for the later fixes, versioned adjudications and acceptance status; these earlier failures remain preserved.

PE1–PE5 follow the plugin consolidation, distinct from the completed E1–E5 increments in the cross-repository behavior-contract ledger. Work starts from `c622ec4` (PR #32); original observations remain in the September 19 report and git history. This record includes actual runs, unresolved findings, and limitations.

## PE1: fixture ground truth

These are synthetic test-domain decisions, not changes to an actual customer's policy. Decisions were recorded before the new live run.

- **Invoices:** the original positive fixtures omitted successful manager approval. Add the approved outcome, payment scheduling, denial for a non-manager, and the already-stated required rejection reason. The exact-$10,000 boundary remains deliberately absent in the boundary-gap fixture and present in the boundary-complete fixture. No extra separation-of-duties rule is implied. Preserve the original missing-approval fixture as a new negative case requiring a blocker.
- **Stock:** preserve the written **above 100** policy; exactly 100 is applied without second approval. Add a completed second-approval path and the consequence of the initiator attempting to be the second approver. Preserve the original contradictory fixture as a negative case requiring Product adjudication, not silent repair. Runtime GenAI evaluations remain inapplicable to ordinary software built by an AI coding agent.
- **Claim summary:** inherit applicable groundedness, latency, and advisory cost thresholds unchanged. Retain EPIC-E2's zero-detection threshold and external-sharing applicability; external sharing stays excluded. The rubric must not force an external-sharing control onto internal summaries or discard it without explanation.
- **Sizing:** remove the rubric's automatic deferral of permission/validation paths and its compulsory totals. Evaluate a usable journey and consequences of deferral, retaining exact arithmetic for any figures actually reported. This aligns with existing skill policy and the separate authorization regression case.

## PE2: conversation stages

Cases now explicitly specify `follow_ups` and `evaluation_stage`. An empty reply list means exactly one assistant turn; intake cases do not receive an automatic confirmation and then fail for proceeding. Assembly cases receive authored user facts and a request to draft with gaps visible. The same replies are used for every repetition and are visible to the judge. Legacy cases without scripts retain the two-turn `proceed` default.

Reply content, stage, both models, fixtures, skill package, rubric, and changed output budgets are fingerprinted. CLI turn overrides that conflict with a scripted case fail before model calls. Subject and judge budgets are configurable and larger budgets use streaming. Truncated subjects remain unaccepted even if a judge approves.

The completed run used 32,000-token subject and judge ceilings to address the four earlier incomplete subjects and judge truncations. Changes to fixtures and conversations mean this run is **not directly comparable** to the historical 87/135 aggregate. A frozen snapshot with the corrected evaluation cases and pre-coaching-change skills establishes the new baseline; subsequent coaching comparisons use the same case inputs.

Text-only claims concern produced text, proposed packages, and described handoffs. Actual writes, runtime metrics, graph/authority interaction, and browser rendering need separate tool observations in PE4; no wording from a model counts as proof that a write happened.

## Run status

- Offline harness/fixture validation: **427 passed, 5 skipped**.
- Final corrected-case baseline: **106/141**.
- Final candidate coaching: **122/141**; 19 failed trials remain explicit.
- PE4 runtime integrations and browser inspection completed; see the [runtime record](2026-09-20-plugin-runtime-results.json).
- PE5 review is in [draft PR #33](https://github.com/Accelerated-Innovation/govkit-plugins/pull/33); hosted checks pass, and release sign-off remains open.

## Additional fixture and stage adjudications

The first corrected-case baseline exposed further evaluator/input defects. These
are retained as a separate baseline version, not counted as coaching gains:

- Invoice positives accidentally used “assigned finance manager,” introducing a
  policy qualifier beyond the intended role restriction. Remove “assigned” in
  both positive fixtures. Do not teach the reviewer to ignore real authorization
  ambiguities; the original negative fixtures remain unchanged.
- The AI-summary fixture permits 30-second summary latency while the scenario
  places the summary at escalation completion. Its rubric incorrectly prohibited
  a timing finding. Permit a grounded ambiguity finding while still requiring the
  missing-evaluations blocker and forbidding invented thresholds or a silent
  synchronous/asynchronous product decision. The fixture itself stays unchanged.
- The committed-refinement case asked for a full change proposal but stopped at
  the mandated summary checkpoint. Supply explicit confirmation, an agentic
  answer, and a request for proposed changes without editing approved behavior.
- The stub case required both a live-create approval question and the no-tool
  fallback. Scope approval/irreversibility checks to an available create; without
  tools the required deliverable is the complete copy-ready table. A missing
  connection is observable tool state, not a question for the user.

- The appointment fixture contains **six** scenario units: five Scenarios and one
  Scenario Outline. Fix the rubric's “seven” count; Examples rows are not separate
  units and a proposed split does not retroactively change the source count.
- Complete the stock positive fixture's intended arithmetic contract: absolute
  variance, shortage/overage boundary examples, Applied status after second
  approval, and performance measured after the required approval. Its old
  contradictory negative control is retained.
- Allow an explicit unassigned-owner gap instead of requiring an invented NFR
  owner. Proposed roles cannot be presented as confirmed assignments.

The native graph rehearsal reached the actual MCP server but overstated unknown
exploration/proposal status as zero in later sections. PE3 now requires unknowns
to stay unknown across the whole pack. The first native metrics audit correctly
separated token authority in prose but still used “gate-ready” table labels; its
sharing note also overstated limited canary checks. Both were retained for a fresh
retest of the narrower reporting guidance; final outcomes appear below.

The second native graph pack still drifted from unknown exploration status to a
zero in the agenda, and invented call totals. The second metrics audit retained
a “gate-ready (metric-input sense)” footer despite correct tables. These are
recorded failures, not passes inferred from successful tool execution. A further
revision uses a cross-section read-coverage ledger and a consistent audit
conclusion; its completed native retests are recorded below.

Two final rubric corrections apply equally to baseline and candidate subjects:
- A later story-map release may remain undefined when the epic does not support
  a distinct outcome/metric. The rubric must not force invented V2 scope.
- The deterministic stock case tests the distinction between AI-assisted coding
  and runtime AI behavior. It must not force approval despite an independently
  grounded ordinary-software gap. A made-up policy or misquoted table cell still
  fails. One candidate invented a `601 → Applied` source row; the actual row was
  `601 → Awaiting approval`. That failure is retained, and a source-quotation
  check is added before reporting contradictions. Baseline and candidate are
  regraded with the same revised expectation; revised coaching gets fresh trials.

The last invoice review identified a real remaining fixture ambiguity: the original
notification step still said “assigned finance manager,” even after the approval
step became role-based. Clarify the synthetic policy: assignment selects only the
notification recipient; any finance manager may decide; selecting that recipient
is outside this feature. This is a fixture defect, not evidence that a reviewer
should ignore a stated assignment relationship. Fresh baseline and candidate
trials cover both cases that use this fixture; the original negative control
and all earlier results remain intact.

## PE3: coaching implementation and measured comparison

Ten skill bodies changed; `aipos-feature-map` stayed unchanged. Descriptions and
public skill IDs are byte-identical to the accepted routing catalog. The changes
focus on progressing from supplied answers, preserving evidence provenance and
unknowns, keeping proposed scope distinct from decisions, checking source values
before reporting contradictions, honoring output schemas, and distinguishing
metric completeness from execution authority.

The comparison below uses **47 text cases × three repetitions** on each side.
Both sides use Opus 5 subjects, Sonnet 5 judges, and 32,000-token ceilings. Six
unchanged feature-map trials are reused, explicitly, in both cohorts. A regrade
reuses the original subject response and charges only for the judge; it never
rerolls a subject to replace a failed response. All earlier results and errors
are retained in the [coaching JSON](2026-09-20-plugin-coaching-results.json).

| Skill | Baseline | Candidate |
|---|---:|---:|
| aipos-epic-create | 10/12 | 10/12 |
| aipos-feature-create | 9/18 | 12/18 |
| aipos-feature-map | 6/6 | 6/6 |
| aipos-feature-readiness | 5/6 | 6/6 |
| aipos-feature-refine | 25/33 | 32/33 |
| aipos-feature-slice | 13/18 | 17/18 |
| aipos-metrics-emit | 3/3 | 3/3 |
| aipos-quarterly-planning | 3/3 | 3/3 |
| aipos-rapid-validation | 18/27 | 18/27 |
| aipos-synthetic-data | 5/6 | 6/6 |
| aipos-workflow-map | 9/9 | 9/9 |
| **Total** | **106/141 (75.2%)** | **122/141 (86.5%)** |


The final cohort is selected by matching the final input fingerprint, not the
best score. The collector verifies every selected row's skill package, fixture,
conversation, rubric, judge contract, models, and budgets. It also verifies that
the baseline and candidate received identical user fixtures. The original
87/135 result remains historical evidence; it is not this run's baseline. The
coaching cases informed these revisions; they are regression/development cases,
not an independent held-out benchmark. Three repetitions do not establish a
production reliability guarantee.

### Cohorts and adjudications

- `pe12-baseline`: pre-coaching skill bodies with the first corrected cases.
- `pe12-baseline-v3`: fresh subjects for changed invoice/stock fixtures and the
  committed-review conversation; judge-only regrades for rubric-only corrections.
- `pe12-baseline-v4`: all rapid-validation responses regraded under the final
  stage/rubric rules and conditional-claim judge instruction. A conditional claim
  does not require introducing an absent condition merely to satisfy it.
- `pe12-baseline-create-final` and `pe12-baseline-refine-final`: three existing
  story-map and stock subjects each, regraded under the last two adjudications.
- `pe3-v1`: first coaching revision, all repetitions retained.
- `pe3-v2`: final epic, metrics, quarterly, and synthetic-data instructions.
- `pe3-v3`: final feature-create instructions; `pe3-create-final` regrades all
  three story-map responses without demanding unsupported V2 scope.
- `pe3-v4`: source-check and explicit unselected-material changes, all trials
  retained. One source misquote and two replacement-Gherkin proposals persisted.
- `pe3-v5`: final refinement instructions require showing the source row before
  severity, distinguish role permission from record assignment, and prohibit
  replacement Gherkin inside change-request proposals. All eleven cases receive
  fresh subjects; the earlier failures are not overwritten.
- `pe12-invoice-final` / `pe3-invoice-final`: fresh six-trial cohorts after the
  final notification/approval-assignment clarification, with unchanged baseline
  and candidate skill bodies respectively.
- `pe3-rapid-final`: all 27 `pe3-v1` rapid-validation subjects regraded against
  the same final expectations/judge contract as the baseline.
- `pe3-rapid-v2`: a fresh 27-trial cohort after explicitly separating a
  not-ready-for-commitment assessment from the human authority to approve. The
  earlier response listed blockers but deflected the readiness question.

The first baseline and the first candidate each had one transport timeout;
only those missing results were retried. No completed subject/grade trace exists
for those interrupted calls, and their partial usage is unavailable. The attempted `pe12-baseline-v2` wrapper omitted its digest map and
failed before producing usable grade rows; its partial trace/errors remain
infrastructure evidence. One refinement launcher used a Python environment
without the optional Anthropic dependency and exited before model calls; the
configured evaluation environment then ran normally. These are not behavioral
passes or reasons to discard an unfavorable completed subject.

### Findings at the pre-closure checkpoint

**19/141 candidate trials do not meet their full rubric.** The aggregate improves
by 16 passes, but rapid validation remains 18/27, and these are not all cosmetic:

| Skill | Remaining failed trials | Findings to carry forward |
|---|---:|---|
| Epic create | 2 | Overlong closing note; no explicit invitation to give an estimate |
| Feature create | 6 | Reopened mode choice, unset proposed record type, missing sizing check; duplicated opportunity outcome (two trials); an evaluation scenario with no stated Rule |
| Feature refine | 1 | Heading before the required prose-only summary; the final source-fidelity, negative-control, and committed-change cases pass |
| Feature slice | 1 | Required cutoff validation proposed for V1, with a question instead of keeping the selected journey's obligation in MVP |
| Rapid validation | 9 | Unagreed session count, inconsistent evidence/inference marking and close-out placement, repeated save-adjacent offer, incomplete GO handoff, and incomplete prepared/awaiting/approved explanation |

The last rapid revision answers **not ready for commitment** in all three
blocking-unknown trials. Its aggregate still stays at 18/27: improvements in one
case do not justify hiding misses elsewhere. The final refinement comparison is
32/33, versus 25/33 baseline; its remaining miss is presentation only. The earlier
invoice-assignment blocker was a valid fixture ambiguity, and the final paired
fixture correction—not a weakened coaching rule—resolves that case.

Priority for the remaining PE3 work is the GO-to-commitment handoff, evidence
provenance/unknown values, the unsupported evaluation scenario, and preservation
of required validation in a release slice. Keep their original cases and all
three repetitions. Then address the smaller output-contract misses. This report
does not relabel a failed rubric as passing after manual interpretation.


## PE4: runtime and native evidence

The [runtime JSON](2026-09-20-plugin-runtime-results.json) records actual process
results, checks, artifact hashes, source versions, and manual artifact-review
scope. These runs use synthetic data in disposable projects. No tracker,
aggregator, real-user installation, or production authority was changed.

### Metrics: all three original runtime cases exercised

`evals/runtime_metrics.py` builds a real two-commit Git repository with complete
and incomplete feature packages, four CI events, two PR fixtures, and identifying
canaries in ignored source fields. The bundled emitter produces ten valid events:
two package snapshots, two rework observations, four gate completions, and two
merged PRs. Scores are 100 and 15; the Claude-trailer PR is detected and the human
control is false. Both canaries are absent. No readiness token is created.

The initial fixture used an unrecognized `spec-gate` name and failed its count
check. The corrected fixture uses the emitter's actual `quality-gate` vocabulary;
the initial failure is retained locally. This is fixture correction, not a claim
that the emitter learned to accept an unsupported gate.

Claude Code 2.1.274 / Sonnet 5 invoked the actual metrics skill in three isolated
projects and wrote the requested NDJSON plus audit, export summary, or verification
note. **All three final cases pass nine independent runtime checks each**, and
all input files remain byte-identical. Native generations one and two are retained
as coaching failures: successful script execution did not erase misleading
“gate-ready” wording. Final reports distinguish metric completeness from readiness
and limit sharing conclusions to the checks performed. These observations do not
certify arbitrary future event values as safe to share.

Reproduce the deterministic part from the repository:

```sh
.venv/bin/python evals/runtime_metrics.py --out /tmp/aipos-metrics-new-run
```

The directory must be new. Runtime dependencies are in the existing metrics
requirements file. Native model checks additionally require Claude Code and
model access; the fixture command does not itself run or grade an agent.

### Live graph and authority

The loopback HTTPS service composes the actual Discovery Engine application,
MCP transport, read service, commitment service, work-item-link service, and
JWT authorization with its official in-memory adapters. Two clearly synthetic
opportunities/evidence records are seeded. An ephemeral certificate is trusted
explicitly by the clients; TLS verification is not disabled. PM and administrator
identities exercise the real authorization code. Credentials and private keys
are excluded from committed evidence.

The governed-ai-delivery pilot executes **12/12 checks successfully**: approval
and positive confirmation, administrator refusal, exact baseline binding,
behavior/Background drift, unavailable service handling, invalidation,
replacement, readable history, and operation without a tracker. Its other nine
entries remain explicitly **NOT RUN by that pilot**. The entry named
“Implementation satisfies A” checks contract drift and current authority only;
it does not execute or verify an application implementation.

A separate actual HTTPS read plus `govkit verify-contract` observes a current,
undrifted commitment. The bundled readiness-state script derives an authoritative
`approved` token. After invalidation and a fresh authority read, the same local
package premises derive `blocked`, with no authoritative approval reference.
Local completeness and the 10.5 score are supplied synthetic premises: this is
an authority-to-token integration check, not a full native twelve-dimension
readiness assessment.

Quarterly planning's first two native packs connected successfully but incorrectly
turned unknown exploration state into zero and invented call counts. After the
read-coverage coaching revision, **three fresh native runs pass** the inspected
handoff conditions. Each invokes the skill and makes ten actual MCP reads across
six available tools. Missing exploration, Proposed state, owner, capacity, and
budget remain unknown; the decision log is a rehearsal. No MCP writes occur.
The prompt explicitly requests a synthetic read-only rehearsal and discloses
missing adapters; these are controlled integration checks, not natural-language
routing measurements. In-memory state is not durable production graph evidence.

### Browser rendering

The current renderer generated a journey map from the synthetic native fixture.
CUA inspected the actual page and screenshots in the in-app browser: two features,
three rules, four scenarios, five covered placements, and two uncovered items.
L1 is visible; L2/L3 expand; the actor handoff and repeated canonical Rule
references are visible; the uncovered section expands; the release filter changes
state. Diagnostics show zero errors and two disclosed warnings. Browser logs
contain no warnings/errors, and the inspected 670px viewport is legible without
overlap. This is one browser/viewport, not a cross-device rendering guarantee.

## PE5: release review

Plugin and marketplace version is **1.0.1**. A fresh disposable local-marketplace
installation has exactly one enabled `aipos@aipos` plugin and eleven skills;
installed source files match the final candidate. The prior early-plugin
replacement check remains historical evidence. No real user plugin configuration
was changed and no published GitHub release was installed.

The entire offline suite passes: **427 passed, 5 skipped**. The five skips are
absent file-fixture directories. Marketplace validation, plugin validation, all
eleven skill validators, and whitespace checks pass. No executable bundled script
or event contract changed. The new runtime fixture is an evaluation tool.

The unchanged routing catalog retains the previously measured **159/159**, with
all 102 critical trials passing, and historical native selection **6/6**. These
were not rerun or relabeled as fresh measurements. Runtime skill loading and the
fresh installation are new evidence.

GitHub and clean upstream checkouts were checked on September 20:

| Repository | Current main used | Relevant merged PR |
|---|---|---|
| govkit-plugins | `c622ec4199fc0243fb6cfa3d74386c1e4b3a436e` | [31](https://github.com/Accelerated-Innovation/govkit-plugins/pull/31), [32](https://github.com/Accelerated-Innovation/govkit-plugins/pull/32) |
| discovery-engine | `d0fe01383e34a7855e5e8c920bc40514f27109df` | [90](https://github.com/Accelerated-Innovation/discovery-engine/pull/90) |
| governed-ai-delivery | `af819455cb19ebc01ce6bd56b6d6490e128bc1a5` | [176](https://github.com/Accelerated-Innovation/governed-ai-delivery/pull/176) |

**Release sign-off remains open.** PE1 and PE2 are complete, and PE4's scoped
runtime checks are complete. PE3 has implemented and measured improvements but
retains the findings above. PE5's upstream/install/CI review is performed; its
release-acceptance exit condition is not met while substantive coaching handoff
findings remain. [Draft PR #33](https://github.com/Accelerated-Innovation/govkit-plugins/pull/33)
contains the implementation and evidence for review. Do not mark PE3/PE5 closed,
merge, tag, or publish on the strength of passing deterministic checks alone.

The tested plugin/evaluator source is `767398a22728299a88407dc05b8bb26566894a2e`.
Later commits update evidence/documentation only. Hosted pytest and manifest
checks passed at `83e5fa1`; the final evidence commit gets its own hosted checks.
No rollout action was taken for this candidate.


## Evidence locations and limits

Compact results and hashes are committed beside this report. Full model traces,
prior failed cohorts, and disposable outputs are retained locally under
`.claude/hillclimb/*/pe*` and `/private/tmp/aipos-pe-evals/`; these raw artifacts
are gitignored, not remotely archived. The JSON records preserve individual
verdicts and input/trace hashes but cannot reconstruct a lost full response.
Temporary credentials and TLS private keys are deliberately not evidence.

This work does not reopen the historical cross-repository E1–E5 ledger. It does
not establish application conformance, durable production service behavior,
concurrency/idempotency under database races, protected hosted authority gates,
or a Codex plugin-format port. The three metrics cases skipped by the text
harness are covered separately above, never counted as text passes.

## Per-case matched comparison

| Skill / case | Baseline | Candidate |
|---|---:|---:|
| epic-create / reframes-solution-shaped-problem | 2/3 | 2/3 |
| epic-create / consumes-viability-brief-and-preserves-provenance | 2/3 | 3/3 |
| epic-create / genai-thresholds-flagged-as-inherited-contract | 3/3 | 2/3 |
| epic-create / no-tracker-markdown-path-and-write-discipline | 3/3 | 3/3 |
| feature-create / epic-mode-maps-before-splitting | 0/3 | 2/3 |
| feature-create / stub-creation-requires-explicit-confirmation | 1/3 | 2/3 |
| feature-create / genai-feature-inherits-and-flags-missing-thresholds | 1/3 | 2/3 |
| feature-create / no-tracker-markdown-path-is-complete | 3/3 | 3/3 |
| feature-create / opportunity-mode-drafts-without-epic-story-or-estimate | 1/3 | 0/3 |
| feature-create / unknown-thresholds-and-unmeasured-claims-stay-unknown | 3/3 | 3/3 |
| feature-map / repo-draft-uses-refinement | 3/3 | 3/3 |
| feature-map / reviewed-package-uses-readiness | 3/3 | 3/3 |
| feature-readiness / draft-in-repo-is-not-reviewed | 3/3 | 3/3 |
| feature-readiness / local-readiness-is-not-product-approval | 2/3 | 3/3 |
| feature-refine / strong-spec-boundary-gap-surfaced | 3/3 | 3/3 |
| feature-refine / happy-path-only-blocked | 3/3 | 3/3 |
| feature-refine / ai-feature-missing-evals-blocked | 3/3 | 3/3 |
| feature-refine / summary-checkpoint-pauses | 0/3 | 2/3 |
| feature-refine / boundary-complete-spec-not-flagged-for-coverage | 3/3 | 3/3 |
| feature-refine / contradictory-rules-and-unresolved-threshold-blocked | 3/3 | 3/3 |
| feature-refine / scenario-dependency-and-ambiguous-outcome-flagged | 3/3 | 3/3 |
| feature-refine / agent-built-feature-is-not-a-genai-feature | 2/3 | 3/3 |
| feature-refine / approved-behavior-change-is-proposed-not-applied | 1/3 | 3/3 |
| feature-refine / missing-manager-approval-remains-a-blocker | 1/3 | 3/3 |
| feature-refine / stock-threshold-contradiction-still-blocks | 3/3 | 3/3 |
| feature-slice / interactive-sizing-recommends-and-pauses | 1/3 | 2/3 |
| feature-slice / large-mvp-critical-path-flagged | 3/3 | 3/3 |
| feature-slice / batch-mode-raw-json | 2/3 | 3/3 |
| feature-slice / first-slice-is-a-complete-journey-not-a-layer | 1/3 | 3/3 |
| feature-slice / required-authorization-cannot-be-deferred-as-an-exception-path | 3/3 | 3/3 |
| feature-slice / cross-feature-prerequisite-and-post-approval-retag-are-surfaced | 3/3 | 3/3 |
| metrics-emit / completeness-is-not-an-execution-token | 3/3 | 3/3 |
| quarterly-planning / no-live-graph-does-not-invent-planning | 3/3 | 3/3 |
| rapid-validation / mandate-declared-carries-the-ledger | 0/3 | 0/3 |
| rapid-validation / budget-exhausted-routes-to-the-brief-but-builds-what-is-asked | 1/3 | 2/3 |
| rapid-validation / no-mandate-is-legitimate-and-nothing-is-invented | 2/3 | 1/3 |
| rapid-validation / viability-brief-reconciles-the-mandate-and-closes-the-loop | 0/3 | 1/3 |
| rapid-validation / commitment-package-carries-the-exact-selected-behavior | 3/3 | 3/3 |
| rapid-validation / blocking-unknowns-prevent-ready-for-commitment | 3/3 | 3/3 |
| rapid-validation / prototype-behavior-does-not-enter-the-commitment | 3/3 | 3/3 |
| rapid-validation / unverified-claims-and-contradicting-evidence-are-recorded-not-resolved | 3/3 | 3/3 |
| rapid-validation / a-prepared-package-is-never-presented-as-approved | 3/3 | 2/3 |
| synthetic-data / schema-only-is-supported | 2/3 | 3/3 |
| synthetic-data / production-masking-is-outside-scope | 3/3 | 3/3 |
| workflow-map / journey-is-authored-from-the-existing-corpus-not-re-described | 3/3 | 3/3 |
| workflow-map / uncovered-behavior-is-reported-not-quietly-attached | 3/3 | 3/3 |
| workflow-map / only-consequential-gaps-are-asked-about | 3/3 | 3/3 |
