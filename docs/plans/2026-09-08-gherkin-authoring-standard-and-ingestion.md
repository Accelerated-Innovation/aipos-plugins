# Plan: Business-Readable Gherkin, Semantic Ingestion, and Scenario-Level Handoff

**Date:** 2026-09-08
**Scope:** `plugins/govkit` — `govkit-feature-create`, `govkit-feature-refine`,
`govkit-feature-readiness`, `govkit-feature-slice`, `govkit-feature-map`, their references,
scripts, evaluation fixtures, and the CI workflow.
**Status legend:** `[ ]` not started · `[~]` in progress · `[x]` done
**Status: implemented — govkit 0.8.0.** Deterministic checks pass (`pytest tests`, 31 tests;
`claude plugin validate .`). The model-graded `evals.json` cases were **not** run in this pass —
they need a model, and no cross-agent or behavioral-pilot result is claimed.

## Findings confirmed against the checkout

All five hypotheses hold:

1. **Rule blocks are asserted at creation and relaxed at refinement.**
   `govkit-feature-create` Step F7 requires "one `Rule:` block per business rule" and
   `references/gherkin-tagging.md` check 10 enforces it, but `govkit-feature-refine`
   Step 6 says "Keep Feature, Rule, and Scenario structure *when useful*". A refinement
   pass can legally flatten what creation required, and nothing downstream notices.

2. **The feature-map reader is lossy.** `repo_ingest.py:parse_feature_file` is a
   line-prefix scanner. `Background:`, `Examples:`, `|` table rows and `"""` doc strings
   all hit one branch that sets `in_desc = False` and `continue`s — the content is
   discarded. Feature-level tags are explicitly cleared (`pending_tags = []`), rule-level
   tags likewise, so tag inheritance is lost. `Scenario Outline:` is parsed as a plain
   scenario, so outlines and their expansions are indistinguishable. There are no source
   locations, and malformed Gherkin yields a partial feature with no diagnostic.

3. **The "strong" invoice fixture has a real coverage gap.**
   `evals/files/feature-invoice-approval-strong.md` states "Invoices of $10,000 or more
   require finance manager approval" and illustrates $12,500, $15,000 and $4,200 — never
   $10,000 itself. Eval 1 expects `Approved` "with at most minor wording edits", which
   trains the reviewer to suppress a legitimate boundary finding.

4. **Readiness handoff is coarse.** The rubric's dimension 10 asks whether an evidence
   path exists; the report format's `Scenario readiness` table has a single free-text
   `Evidence path` column. Nothing carries the verification boundary, the fixtures, the
   existing step definitions, or the command that will produce the evidence.

5. **A GenAI example conflates registers.**
   `gherkin-tagging.md`'s `@evaluation` example asserts, in one scenario, that a *single*
   generated summary is fully traceable **and** that "the groundedness score is at least
   0.95 across the evaluation set" — one instance mixed with an aggregate over a dataset.

Two further findings, recorded because the work touches them:

6. `repo_ingest.py:parse_feature_file` drops a `Rule:` that has no scenarios
   (`flush_rule` appends only when `cur_rule["scenarios"]` is non-empty), so a declared
   but entirely uncovered rule is invisible to the rule-coverage dimension.
7. `compute_size.py` cross-checks a verdict's `taggedSlice` against the record's
   `tags` only (lines 173–186); it will need to read inherited tags once they exist.

## Design decisions

**D1 — One shared standard, at plugin level.** New
`plugins/govkit/references/gherkin-authoring-standard.md`, installed with the plugin and
reachable from every skill folder as `../../references/`. Not a new skill; not duplicated
into five `references/` folders. Skill-local references keep their existing jobs
(`gherkin-tagging.md` owns tags, `gherkin-quality-rubric.md` owns scoring) and cite the
standard instead of restating it.

**D2 — `gherkin-official` (PyPI) replaces the hand parser.** MIT-licensed, maintained by
the Cucumber team, pure-Python, single dependency (`typing-extensions`). Verified locally
at 39.0.0: `Parser().parse(text)` returns a `GherkinDocument` dict carrying tags with
locations, rule and feature backgrounds, `Scenario Outline` keyword, `examples[]` with
`tableHeader`/`tableBody`, step `dataTable` and `docString`, and every node's
`location`. Invalid input raises `CompositeParserException` whose `.errors` carry
`{line, column}` and a message. Pinned in `scripts/requirements.txt`; installed in CI.

**D3 — Additive ingestion contract.** Existing consumers read `rules[].scenarios[].steps`
(list of strings), `tags`, `ruleCount`, `scenarioCount`. All keep their current meaning.
New information arrives in new fields (`effectiveTags`, `stepDetails`, `examples`,
`background`, `type`, `line`, `exampleCount`, `parseErrors`). Two changes are deliberate,
documented, and covered by regression tests rather than silent: a `Rule:` with no
scenarios is now preserved, and downstream slice logic reads `effectiveTags` (so a slice
tag on a `Feature:` or `Rule:` finally reaches its scenarios, which is what Gherkin means).

**D4 — Identifiers are tags, not a new file format.** `@rule:<slug>` on a `Rule:`,
`@scenario:<slug>` on a scenario. Gherkin already allows tags in both places, the closed
delivery-tag vocabulary is untouched, unknown tags are already preserved verbatim, and a
package with no identifiers keeps working (ingestion derives a slug from the name and
marks it `derived`). No migration is required of anyone.

**D5 — Readiness gains a handoff section, not a new scale.** The 12 dimensions and the
bands stay. Dimension 10 and 12 checks get sharper, and the report format grows a
per-scenario verification-plan table. "Ready to implement", "automated" and "verified
passing" become three explicitly separate states.

**D6 — Determinism in CI.** New `tests/` run under `pytest` with no model calls and no
network. The existing `claude plugin validate` job stays. Model-graded `evals.json` cases
remain optional and are reported as run-or-not-run, never as evidence by default.

## Work items

### A. Shared authoring standard

- [x] **A1** Write `plugins/govkit/references/gherkin-authoring-standard.md`: BRIEF
  principles in original wording; explicit-`Rule` convention with the "optional in
  standard Gherkin / missing grouping ≠ missing decision / never invent a policy" rule;
  scenario anatomy (illustrates a stated rule, meaningful context and trigger, observable
  outcomes); coverage judgment (boundaries, negative paths, permissions, exceptions —
  without a combinatorial catalog); the three provenance registers (confirmed
  requirement / proposed illustrative data / unresolved product decision); automation
  suitability; deterministic checks vs aggregate GenAI evaluation; the worked
  below/exact/above threshold example.
- [x] **A2** Write `plugins/govkit/references/spec-identifiers.md`: the `@rule:` /
  `@scenario:` convention, stability under rename and retag, split semantics, the
  fallback for packages that carry no identifiers, and how identifiers connect rules,
  scenarios, NFRs, evaluations and evidence.
- [x] **A3** Point the five skills at both references from their "Required references"
  tables and load them at the step where they matter. Remove duplicated guidance rather
  than adding a second copy.

### B. Skill-level corrections

- [x] **B1** `govkit-feature-refine` Step 6: replace "Keep Feature, Rule, and Scenario
  structure when useful" with the preserve-and-restore-Rule default, including the
  legacy distinction and the never-invent-a-policy rule.
- [x] **B2** `govkit-feature-create` Step F7 and `gherkin-tagging.md`: cite the standard,
  keep the Rule requirement, and split the conflated `@evaluation` example into a
  deterministic behavior check and a dataset evaluation with dataset / method / threshold
  / execution context / evidence.
- [x] **B3** Add to both skills and to `gherkin-quality-rubric.md`: an AI coding agent
  building ordinary software does not make the product feature GenAI.
- [x] **B4** `govkit-feature-slice`: splitting and retagging must preserve rule
  association, background scoping, examples, outcomes and identifiers; a generic tag
  category never by itself defers risk-critical behavior.

### C. Ingestion

- [x] **C1** Rewrite `parse_feature_file` on `gherkin-official`; add
  `scripts/requirements.txt` (pinned) and an actionable ImportError message.
- [x] **C2** Preserve rule association, scenario type, feature and rule backgrounds,
  Examples tables, step data tables, doc strings, tags with inheritance, and source
  locations. Keep authored `scenarioCount`; add `exampleCount` for expanded rows.
- [x] **C3** Invalid syntax produces `parseErrors` with file/line/column/message, no
  partial rules from the failed file, a visible `specNote`, and a distinct exit code.
- [x] **C4** `render_map.py`: render backgrounds, Examples tables, step tables and doc
  strings; badge outlines; read `effectiveTags` for slice grouping and chips; show
  `exampleCount` alongside `scenarioCount`.
- [x] **C5** `compute_size.py`: cross-check `taggedSlice` against effective tags.
- [x] **C6** Update `references/ingestion-contract.md` and `references/rendering.md`.

### D. Readiness and traceability

- [x] **D1** Extend the readiness report with a per-scenario verification plan: behavior
  and rule verified, existing tests/step definitions plus proposed additions, verification
  boundary (domain/service · API · UI · evaluation · justified manual), fixtures,
  controlled time, isolation and dependency handling, known validation command and
  expected evidence, and an explicit "still to be established" column.
- [x] **D2** Separate "ready to implement" from "automated" and "verified passing";
  state that new step definitions and passing tests are not preconditions for the token.
- [x] **D3** Sharpen rubric dimensions 10 and 12 without changing the scale or bands.
- [x] **D4** Preserve the lifecycle note that `plan.md` and `architecture_preflight.md`
  come after the token.

### E. Evaluations and CI

- [x] **E1** `tests/test_repo_ingest.py` (pytest, no model calls): feature and rule
  backgrounds; outlines, Examples values, step tables, doc strings; tag inheritance and
  unchanged delivery-tag behavior; invalid Gherkin diagnostics; unchanged ingestion of an
  existing simple feature; identifier extraction and derivation.
- [x] **E2** `tests/test_render_map.py`: preserved information reaches the HTML.
- [x] **E3** Revise `feature-invoice-approval-strong.md` expectations so the missing
  exact-$10,000 boundary is a legitimate finding, and add a boundary-complete companion
  fixture with the below/exact/above outline.
- [x] **E4** New refine fixtures and eval cases: contradictory rules with an unresolved
  threshold; scenario dependency with an ambiguous outcome; ordinary software built with
  an AI coding agent (must not attract GenAI evaluation requirements).
- [x] **E5** CI: add a `pytest` job alongside `claude plugin validate`, installing pinned
  requirements. Deterministic; no API key.
- [x] **E6** CONTRIBUTING/README: how to run the deterministic checks; note that
  `evals.json` cases are model-graded and optional.

## Non-goals

- No new skills; no change to the delivery-tag vocabulary; no change to score scales.
- No proprietary service, paid account, specific coding agent, or model API anywhere in
  the core workflow or its automated checks.
- The optional BDD book is background reading only. Nothing in the repository quotes it
  or depends on access to it.
