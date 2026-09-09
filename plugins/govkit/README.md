# govkit

Governed, AI-assisted delivery for feature teams: eight skills that take work from a
problem-first epic through Draft 0 to gated, evidence-backed execution — epic authoring, story
mapping and feature authoring, refinement, sizing and release slicing, a repo-side readiness
gate, a corpus-wide feature map, synthetic test data, and delivery metrics.

## What it does

GovKit's premise is that AI-assisted coding is safe when the spec is a contract: Gherkin the
whole team understands, NFRs with thresholds, evaluation criteria with gates, and an explicit
go/no-go — the **Development Token** — before any coding agent starts. The skills cover that
lifecycle in order:

1. **`govkit-epic-create`** — the problem-first interview. Turns a validated opportunity (or a
   rough idea) into a complete epic: a problem statement with no solution smuggled into it,
   named personas, quantified impact, OKR alignment, three-to-five measurable success metrics,
   dated evidence, MVP scope with a real out-of-scope list, risks, and NFRs — plus GenAI
   evaluation criteria that every feature under the epic inherits. Where a Pillar 2 viability
   brief exists, this is the skill that writes out the handoff inputs it named.
2. **`govkit-feature-create`** — the generator. Breaks an epic into a workflow-aligned,
   non-overlapping feature set via lightweight story mapping (backbone → horizontal slices →
   feature candidates with scope boundaries), then authors one feature into Draft 0: user
   stories, structured description, auto-tagged Gherkin, NFRs, Definition of Done, and privacy
   impact. Writes the repo feature package by default; optionally creates or updates Jira or
   Aha! records after an explicit, destination-named confirmation. Applies evaluation-driven
   thinking to GenAI features automatically.
3. **`govkit-feature-refine`** — the 3 Amigos review of a generated Draft 0 (from
   `govkit-feature-create`, Aha!, an LLM, or a human). Scores against a 10-dimension quality
   rubric, finds blockers and evidence gaps, suggests rewritten Gherkin, and produces a
   Development Token *recommendation*. Also exposes a non-interactive batch mode that other
   callers use to score many features at once.
4. **`govkit-feature-slice`** — scenario sizing on the Scenario Complexity Matrix (Data &
   State, Integration, UI/UX at 1–3 points each) and MoSCoW release slicing onto `@mvp` /
   `@v1` / `@v2` Gherkin tags. Recommends; the PM decides. Proposes splits for Large (8–9
   point) scenarios and flags Large scenarios on the MVP critical path. Can write the tagged
   spec back to Jira or Aha! after an explicit confirmation.
5. **`govkit-feature-readiness`** — the repo-side 12-dimension gate that actually issues the
   Development Token once the package (`acceptance.feature`, `nfrs.md`, `eval_criteria.yaml`)
   is in the repository. No token, no coding.
6. **`govkit-synthetic-data`** — a seeded, repeatable Python Faker generator derived from the
   feature's Gherkin scenarios, plus committed data files.
7. **`govkit-metrics-emit`** — structured Tier 1 metric events (NDJSON) from a governed repo's
   exhaust: spec completeness, gate readiness, velocity/quality inputs.
8. **`govkit-feature-map`** — the cross-cutting corpus view: a self-contained HTML page with a
   producer/consumer chain diagram, one card per feature with its full spec, readiness badges
   from the refine or readiness rubric, and size badges with MVP/V1/V2 slice views. Ingests
   from Jira, Aha!, or a repo directory, and merges tracker records with repo-resident Gherkin.

What it does **not** do: write implementation code, create step definitions, replace Product /
QA / Engineering judgment, or write to a tracker without a previewed, explicitly confirmed
update. Batch scores are advisory — the blocker list is the gate, never the number.

`govkit-epic-create` and `govkit-feature-create` are the only skills that can bring new
records into existence; every other skill is update-in-place or read-only. Both preview the
full content before creating anything, and a bare "proceed" never authorizes a write.

### When to use it

Reach for govkit when you hear:

- "Write this epic" / "help me frame the problem" / "what are our success metrics?" → epic create
- "Break this epic down" / "what features do we need?" / "write this feature" → feature create
- "Review this spec / these acceptance criteria before we build" → refine
- "Is this ready for AI-assisted coding?" / "issue the token" → readiness
- "Slice this feature", "what's the MVP?", "how big is this?" → slice
- "Map this epic", "where is the release weakest?", "score all of these" → feature map
- "Generate test data for this feature" → synthetic data
- "Which features aren't gate-ready?" / "emit delivery metrics" → metrics

## Installation

```bash
claude plugin marketplace add Accelerated-Innovation/govkit-plugins   # once per machine
claude plugin install govkit@aipos
```

### Prerequisites

- **Python 3.11+** on PATH — the bundled scripts (map ingest/render/verify, sizing
  arithmetic, metrics emission, data generation) are plain Python.
- **PyYAML** (optional) — richer `eval_criteria.yaml` parsing during ingestion; a shallow
  fallback runs without it.
- **Faker** (`pip install faker`) — only for running generators produced by
  `govkit-feature-synthetic-data`.
- **Atlassian and/or Aha! MCP connectors** (optional) — required only for tracker ingestion
  and write-back; every skill also accepts pasted or file-based specs.

## Usage

The skills trigger from natural phrases (see above) — no slash commands. Run them in
lifecycle order: epic → features → refine → slice → repo handoff → readiness → synthetic
data → coding → metrics, with the feature map at any point as the portfolio view. Each skill
states its own handoff: the epic's field names are feature-create's input contract; feature
create produces Draft 0 and never self-reviews it; refine recommends the token, readiness
issues it; slice recommends tags, the PM confirms them.

## Examples

### Example: Turn a viability brief into an epic

- **Prompt:** `We got a go from validation on the assisted ticket search. Here's the viability brief — turn it into an epic.`
- **Expected:** The brief is read before any questions are asked, so the interview only
  covers what it doesn't answer. The Validation Decision and its "revise scope" caveat are
  recorded, provenance survives (measured findings stay measured, assumptions stay
  assumptions), un-agreed thresholds stay `TBD` in Open Questions, and GenAI evaluation
  criteria are set with an explicit note that every feature will inherit them.
- **Safe to auto-run:** yes
- **Inputs:** the viability brief; writes nothing until final assembly is approved.

### Example: Break an epic into features

- **Prompt:** `Here's our epic — "Faster claims triage for regional adjusters". Break it down into the features we'll need.`
- **Expected:** A workflow backbone of 4–7 user activities named from the adjuster's side,
  MVP/V1/V2 slices that each span multiple stages and name the success metric they move,
  then feature candidates with a one-line scope boundary apiece — followed by the overlap
  and vertical-only integrity checks and a stop presenting the set for confirmation. No
  records created, no files written.
- **Safe to auto-run:** yes
- **Inputs:** none — the epic is inline.

### Example: Author a feature into Draft 0

- **Prompt:** `Let's flesh out CLM-104, the assisted claim file summary. I want the full spec — stories, acceptance criteria, NFRs, definition of done.`
- **Expected:** GenAI mode switched on automatically (summarization), epic-level evaluation
  thresholds inherited unchanged, then a one-question-at-a-time pass through persona,
  intent and size, stories, description (including a populated Out of Scope), auto-tagged
  Gherkin with a tag coverage line, NFRs with thresholds, DoD, and privacy. Un-agreed
  thresholds appear as marked gaps, never as invented numbers. Output is labelled Draft 0
  and hands off to `govkit-feature-refine`.
- **Safe to auto-run:** no
- **Inputs:** none required; writes `features/<key>/` to the working directory.

### Example: Review a Draft 0 spec

- **Prompt:** `Review this Draft 0 feature spec before refinement. Feature: Invoice approval routing. Rule: Invoices of $10,000 or more require finance manager approval. Scenario: High-value invoice routes to manager approval - Given a finance analyst has submitted an invoice for $12,500, When the invoice enters the approval workflow, Then the invoice status is "Pending manager approval".`
- **Expected:** A short prose summary of the feature (paragraphs, no headings or bullets),
  then a stop that asks the team to confirm the summary and answer the explicit "agentic
  behavior: yes or no?" question before any score, blocker list, or token recommendation is
  shown.
- **Safe to auto-run:** yes
- **Inputs:** none — the spec is inline.

### Example: Size and slice a feature's scenarios

- **Prompt:** `Size the scenarios of this feature and recommend MVP/V1/V2 slices. Feature: Password reset. Scenario: User resets a forgotten password - Given a registered user requests a reset link, When they follow the link and set a new password, Then they can sign in with the new password. Scenario: Reset links expire - Given a reset link older than 24 hours, When the user follows it, Then the reset is refused and a new link is offered.`
- **Expected:** A sizing table with three dimension judgments (integers 1–3) per scenario,
  points equal to the sum of the dimensions, a Small/Medium/Large band, a recommended slice
  with a one-line rationale per scenario — then a pause asking the PM to confirm or correct
  the recommendations. No tags are applied and nothing is written anywhere.
- **Safe to auto-run:** yes
- **Inputs:** Python 3 on PATH (the skill runs its bundled `compute_size.py` for the
  arithmetic).

### Example: Build a feature map from a repo directory

- **Prompt:** `Map the feature specs under ./features into a feature map with readiness scoring.`
- **Expected:** A `features.json` ingested from the directory (with per-feature rule and
  scenario counts shown before scoring), batch rubric scores verified by
  `verify_scores.py`, and a self-contained `feature-map.html` with the chain diagram, one
  card per feature, readiness badges, and the artifact ledger.
- **Safe to auto-run:** no
- **Inputs:** a directory of feature packages (`acceptance.feature` and friends); writes
  JSON and HTML files to the working directory.

### Example: Write tagged Gherkin back to Jira

- **Prompt:** `Apply the slices we agreed and update PROJ-142's acceptance criteria in Jira.`
- **Expected:** The exact final field content shown verbatim, a one-line delta summary, the
  named destination ("the Acceptance Criteria field of PROJ-142 in Jira"), a single explicit
  yes/no question — and only after a yes, the write, followed by a read-back verification.
- **Safe to auto-run:** no
- **Inputs:** Atlassian MCP connected with write access to the project.

## Limits and gotchas

- **The blocker list is the gate; scores are advisory.** A feature can score 7.5/10 and
  still be Blocked. Badges and dashboards built from these scores carry that caveat on their
  face.
- **Epic evaluation criteria are a contract, not an aspiration.** A threshold set in
  `govkit-epic-create` is inherited by every feature and becomes a release gate at the
  readiness check. Set them deliberately.
- **Draft 0 is unreviewed by definition.** `govkit-feature-create` writes specs; it never
  reviews its own output, scores it, or implies a token. A generated feature that skips
  refinement is a generated feature nobody has read.
- **Record creation is one-way here.** `govkit-epic-create` and `govkit-feature-create` can
  create tracker records after an explicit confirmation, but no skill in this plugin deletes
  or re-parents one. Check the preview before saying yes.
- **Two rubric scales exist** — refine's 10 dimensions for tracker drafts, readiness's 12
  for repo packages. A 7.5 does not mean the same thing on both, and the map labels which
  one produced each badge.
- A spec that lives outside the ingested record scores near zero with a `notAssessable`
  flag — that means *unreviewable from this record*, not bad.
- Slice tags never land without the PM's confirmation; batch sizing recommendations render
  clearly marked as recommendations.
- The feature map writes local files (`features.json`, `scores.json`, `feature-map.html`);
  tracker write-back edits the record it read from and never creates or deletes records.
- Sizing points are complexity, not story points — don't feed them into sprint capacity math.

## Components

| Kind | Name | What it does |
|---|---|---|
| Skill | `govkit-epic-create` | Problem-first epic interview; epic package; inherited GenAI evaluation criteria |
| Skill | `govkit-feature-create` | Story mapping, feature stubs, and Draft 0 authoring; optional record creation |
| Skill | `govkit-feature-refine` | 3 Amigos review of Draft 0; token recommendation; batch scoring mode |
| Skill | `govkit-feature-slice` | Scenario sizing, MoSCoW slicing, `@mvp`/`@v1`/`@v2` tags, tracker write-back |
| Skill | `govkit-feature-readiness` | Repo-side 12-dimension gate; issues the Development Token |
| Skill | `govkit-feature-map` | Corpus map: chain, cards, readiness + size badges, slice filter |
| Skill | `govkit-synthetic-data` | Seeded Faker generator + data files from Gherkin scenarios |
| Skill | `govkit-metrics-emit` | Tier 1 NDJSON metric events from repo exhaust |
| Script | `compute_size.py` (slice) | All sizing arithmetic: points, bands, rollups, risk flags |
| Script | `repo_ingest.py`, `verify_scores.py`, `render_map.py` (map) | Ingest, score verification gate, HTML renderer |
| Reference | `references/gherkin-authoring-standard.md` (plugin-wide) | The shared Gherkin authoring standard every feature skill judges against |
| Reference | `references/spec-identifiers.md` (plugin-wide) | `@rule:` / `@scenario:` identifiers linking rules, scenarios, NFRs, evaluations and evidence |

## Version history

| Version | Change |
|---|---|
| 0.8.0 | One shared Gherkin authoring standard (`references/gherkin-authoring-standard.md`) that create, refine, readiness, slice and map all load instead of each carrying its own rules — BRIEF, explicit `Rule:` blocks as the GovKit convention, boundary coverage, scenario isolation, the confirmed / proposed / unresolved registers, and the line between a deterministic behavior check and an aggregate GenAI evaluation. Refine no longer flattens `Rule:` blocks it was meant to preserve. Ingestion moved from line-scanning to the official Cucumber parser (`gherkin-official`, MIT), so backgrounds, outlines, Examples, step tables, doc strings, tag inheritance and source locations survive into `features.json` and reach the map's cards; invalid Gherkin now produces `file:line:column` diagnostics instead of a partial feature. Optional `@rule:` / `@scenario:` identifiers survive rewording. Readiness gained a per-scenario verification plan and separates "ready to implement" from "automated" and "verified passing". Slicing gained a behavior-preservation checklist for splits. New: pinned script dependencies and a deterministic offline `pytest` suite in CI. |
| 0.7.0 | Shift-left contract alignment: authoring now walks the gates' ten NFR areas with owners, captures eval-criteria data/evidence/owner fields and the explicit `multi_agent` answer, elicits business rules and emits `Rule:`-grouped Gherkin, and writes structured `Produces`/`Consumes` sections that `repo_ingest.py` now parses into the feature map's chain. Readiness gained a batch mode, a `--scale readiness` verifier path, and a machine-readable token record (`.govkit/tokens/<key>.json`) that unlocks Tier 2 metrics. Write protocols consolidated to one canonical reference; GenAI detection lists unified with epic-level inheritance. |
| 0.6.0 | Added `govkit-epic-create`: problem-first epic authoring, the solution-in-problem test, three-part success metrics, and epic-level GenAI evaluation criteria that features inherit. Closes the handoff from Pillar 2's viability brief. |
| 0.5.0 | Added `govkit-feature-create`: epic story mapping, feature stubs, and Draft 0 authoring with automatic Gherkin tagging and GenAI evaluation criteria. First skill that can create tracker records, behind a whole-set preview and explicit confirmation. |
| 0.4.0 | Added `govkit-feature-slice`; size badges, sizing panel, and MVP/V1/V2 slice filter in the feature map; scenario tags preserved through ingestion. |
| 0.3.0 | Added `govkit-feature-map` with batch scoring; clarified that refine recommends and readiness issues the Development Token. |
| 0.1–0.2 | Initial skills: refine (with quality rubric and checklists), readiness, metrics-emit, synthetic-data. |
