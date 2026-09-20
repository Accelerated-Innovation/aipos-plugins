---
name: aipos-synthetic-data
description: "Generate repeatable synthetic datasets and seeded Faker generators from feature scenarios or an explicit schema. Use for fixtures, boundary cases, sample records, and load data. State whether coverage is scenario-derived or schema-derived; production-data masking is outside scope."
---

# GovKit Synthetic Data Skill

## Purpose

Turn an approved feature package into the synthetic data its scenarios need: a seeded Python Faker script committed next to the feature, plus the generated data files, plus a manifest that maps every dataset back to the scenario it exercises.

The script is the deliverable, not just the data. Data files rot; a seeded script regenerates them identically in CI, survives schema tweaks with a one-line edit, and shows reviewers exactly how every value was produced. Faker output is inherently synthetic — no value is ever copied from a real person or record — which is what makes this safe in a government context.

## Tool-agnostic design

Like the other GovKit skills, this one runs regardless of team tooling. The target project may be C#, Java, Go, or anything else — that does not matter, because the boundary between the generator and the project is **data files, not code**. The generator needs only `python` and `faker`; the project consumes CSV, JSONL, or SQL like it would consume any other test asset.

## Key terms

- **Feature package** — the repo files that carry the approved spec: `/features/<work-item-id>/` containing `acceptance.feature`, `nfrs.md`, `eval_criteria.yaml`.
- **Data profile** — the entity/field/constraint model extracted from the package before any data is generated (see process step 2).
- **Coverage map** — the manifest table linking each generated dataset to the scenario(s) it serves and the case type (happy, boundary, negative, volume).

## Scope

Use it for:

- Generating scenario-derived test data for a feature package
- Producing seeded, regenerable Faker scripts committed to the repo
- Volume/load datasets when NFRs specify throughput or scale thresholds
- Refreshing or extending data after the feature package changes

Do not use it for:

- Inventing business rules, valid ranges, or field formats the package doesn't state (ask the human — same guardrail as the rest of GovKit)
- Anonymizing or masking real production data (that is a different discipline; this skill never touches real records)
- Validating the feature package itself (use the readiness skill)
- Writing step definitions or implementation code

## Inputs

Read the feature package:

```text
/features/<work-item-id>/
  acceptance.feature     (required — the source of scenarios and coverage)
  nfrs.md                (volumes, performance thresholds → volume datasets)
  eval_criteria.yaml     (distributions, thresholds → data shape constraints)
```

If `acceptance.feature` is missing, stop and say so — without scenarios there is nothing to derive coverage from. If the user has no feature package at all and just wants bulk data from a schema they describe, you can still help: skip to step 3 with their schema as the data profile, and say clearly that coverage is schema-driven, not scenario-derived.

## Process

### 1. Parse the feature package

Read `acceptance.feature`. From each scenario, extract:

- **Entities and fields** — nouns in Given/When/Then steps, columns in data tables and Examples tables
- **Constraints** — explicit values, ranges, formats, and states the steps assert
- **Relationships** — references between entities ("the citizen's application", "cases assigned to the reviewer")

From `nfrs.md`, extract volume requirements (e.g., "handles 10,000 concurrent applications" → a volume dataset of that size). From `eval_criteria.yaml`, extract any distribution or threshold that constrains data shape (e.g., "95% of records complete" → generate 5% with missing optional fields).

### 2. Build and confirm the data profile

Write out the profile before generating anything: each entity, its fields, the type and Faker provider for each field, constraints, and cross-entity relationships.

Where the package is silent — a field's valid range, an ID format, a state machine — do not guess. List the gaps and ask the human, or record an explicit assumption in the manifest if the human has delegated that call. Invented business rules in test data are worse than none: they encode a wrong spec into every test that uses the data.

Consult `references/faker-patterns.md` for provider selection, locale, custom providers for domain formats (case numbers, agency codes), relational integrity, and edge-case injection techniques.

### 3. Plan coverage from the scenarios

For each scenario, decide which datasets it needs. Default coverage per scenario:

| Case type | What it is | Cardinality |
|---|---|---|
| Happy | Values squarely inside every constraint | Zero, one, and many records (empty set, single record, and a batch) |
| Boundary | Values at the exact edges the steps assert (min, max, length limits, date cutoffs) | One record per boundary |
| Negative | Values that violate one constraint at a time, each labeled with which constraint it breaks | One record per violated constraint |
| Volume | NFR-driven scale (only when NFRs specify it) | The NFR's number |

The zero/one/many spread on happy-path data matters because collection-handling bugs cluster at exactly those cardinalities. Negative records violate one rule each so a failing test points at one rule.

Pick output formats by consumer, not by habit: CSV for tabular/bulk-load data, JSONL for API and document-shaped records, SQL inserts when the feature seeds a relational database, and Gherkin Examples tables when the team wants data pasted directly back into `acceptance.feature`. Ask if unclear; CSV + JSONL is the safe default.

### 4. Write the generator script

Create `/features/<work-item-id>/test_data/generate_test_data.py`, starting from `scripts/generator_template.py` (copy it, don't reference it — the committed script must stand alone). Requirements the template already handles, preserve them:

- **Deterministic**: single seed constant, set via `Faker.seed()` AND `random.seed()`, overridable by `--seed`. Same seed → byte-identical output.
- **Standalone**: stdlib + `faker` only. No project imports, no other packages.
- **Self-describing**: `--help` works; header comment names the work item, seed, and faker version.
- **Format writers**: CSV, JSONL, SQL insert emitters included; use only the ones this feature needs.

Label the output synthetic without changing its data contract. For a closed or
explicit user schema, keep the records to exactly those fields; put the synthetic
marker in the manifest, filename, sidecar, or a format-supported comment outside
the records. An extra `_synthetic` field or CSV column is allowed only when the
schema permits it or the user approves that extension. Never add a business rule
or record field just to satisfy a labeling convention.

### 5. Run, verify, and write the manifest

Run the script twice; diff the outputs. Byte-identical or it's not done — nondeterminism here silently breaks test reproducibility later. Then spot-check: constraints hold, negative records violate exactly the rule they claim, volumes match.

Commit alongside the data a `MANIFEST.md` containing:

```markdown
# Synthetic Test Data — <work-item-id>
Generated by generate_test_data.py | seed: <N> | faker: <version> | python: <version>
ALL DATA IS SYNTHETIC (Python Faker). No real records were used or referenced.

## Coverage map
| Dataset file | Scenario(s) | Case type | Records | Notes |
|---|---|---|---|---|

## Assumptions
<every rule not stated in the feature package, and who approved it>

## Regenerate
python generate_test_data.py --seed <N>
```

## Output layout

```text
/features/<work-item-id>/test_data/
  generate_test_data.py
  MANIFEST.md
  data/
    <entity>_happy.csv / .jsonl
    <entity>_boundary.jsonl
    <entity>_negative.jsonl
    <entity>_volume.csv        (only when NFR-driven)
    seed_<db>.sql              (only when SQL requested)
```

## Guardrails

Do not:

- Invent business rules, formats, or ranges the package doesn't state
- Use, copy, or derive values from real production data
- Emit data without the synthetic marker and manifest
- Leave the generator nondeterministic or dependent on the target project's code

Always:

- Trace every dataset to a scenario (or to a stated NFR/schema request)
- Record every assumption in the manifest with an owner
- Verify determinism by regenerating and diffing before calling it done
- Keep the script runnable with nothing but `pip install faker`
