# Faker Patterns for GovKit Synthetic Data

Provider selection, domain formats, relational integrity, and edge-case injection. Read this while building the data profile (process step 2) and writing record builders (step 4).

## Contents

- Common providers by field type
- Determinism rules
- Domain formats and custom providers
- Weighted and state-dependent values
- Relational integrity across entities
- Injecting boundary and negative values
- Locale

## Common providers by field type

| Field | Provider | Note |
|---|---|---|
| Person name | `fake.name()`, `first_name()`, `last_name()` | |
| Email | `fake.email()` | domain is fake; use `fake.company_email()` for org-style |
| Phone | `fake.phone_number()` | format varies; normalize if the spec fixes a format |
| Street address | `fake.street_address()`, `fake.address()` | `address()` contains newlines — avoid in CSV |
| City/State/ZIP | `fake.city()`, `fake.state_abbr()`, `fake.zipcode()` | |
| SSN-format ID | `fake.ssn()` | synthetic by construction; fine per project ruling, keep the `_synthetic` marker |
| EIN | `fake.ein()` | |
| Date in range | `fake.date_between(start_date="-2y", end_date="today")` | always bound both ends |
| Timestamp | `fake.date_time_between(...)` | serialize ISO-8601 |
| UUID | `fake.uuid4()` | deterministic under `Faker.seed()` |
| Money | `round(random.uniform(lo, hi), 2)` | prefer `random` over `fake.pydecimal` for readable control |
| Free text | `fake.sentence()`, `fake.paragraph()` | cap length if the spec has field limits |
| Company/agency | `fake.company()` | see custom providers for real-format agency codes |

## Determinism rules

The whole value of the committed script is identical regeneration. These are the ways it silently breaks:

1. Seed both generators: `Faker.seed(n)` then `random.seed(n)` — Faker's class-level seed does not cover direct `random.*` calls.
2. Never call `datetime.now()` / `date.today()` in record builders — "today" changes daily. `fake.date_between(end_date="today")` has the same problem: prefer explicit end dates (`end_date=date(2026, 7, 7)`) frozen at authoring time.
3. Generation order is part of determinism — build datasets in a fixed order; don't generate from dict/set iteration whose order isn't guaranteed.
4. `json.dumps(..., sort_keys=True)` and fixed CSV column order keep byte-identical diffs.
5. Record the faker version in the manifest; provider output can change between major versions. If CI regenerates, pin `faker==X.Y.Z`.

## Domain formats and custom providers

Feature packages often use domain identifiers Faker has no provider for (case numbers, permit IDs, agency codes). Use `fake.bothify` / `fake.numerify` with the format from the package:

```python
case_number = fake.bothify("CASE-####-??").upper()   # CASE-4821-XK
permit_id   = fake.numerify("P-2026-%%%%%%")          # P-2026-483920
```

If the format isn't stated in the package, that's a data-profile gap — ask, don't invent (a plausible-looking wrong format will pass tests that should fail).

For a reusable domain vocabulary, register a provider:

```python
from faker.providers import DynamicProvider

agency_provider = DynamicProvider(
    provider_name="agency_code",
    elements=["DMV", "DHS", "DOL", "HUD"],  # from the package or the human
)
fake.add_provider(agency_provider)
fake.agency_code()
```

## Weighted and state-dependent values

When eval criteria specify distributions ("95% complete", "80% approved"):

```python
status = random.choices(
    ["approved", "denied", "pending"], weights=[80, 15, 5], k=1)[0]
```

When one field constrains another (a denied application has a denial reason, an approved one doesn't), branch inside the builder so every record is internally consistent — scenario steps assert on combinations, not lone fields:

```python
rec["status"] = random.choice(["approved", "denied"])
rec["denial_reason"] = fake.sentence() if rec["status"] == "denied" else None
```

## Relational integrity across entities

Generate parents first, then draw foreign keys from the actual parent IDs:

```python
citizens = [build_citizen(fake) for _ in range(50)]
citizen_ids = [c["id"] for c in citizens]
applications = [build_application(fake, random.choice(citizen_ids))
                for _ in range(200)]
```

Never `fake.uuid4()` a foreign key independently — orphaned references make relational loads fail for reasons unrelated to the feature. If a scenario needs an orphan (a negative case), create it deliberately and label it `_violates="citizen_fk"`.

## Injecting boundary and negative values

Build a valid record first, then overwrite the one field under test — this keeps every other field valid, so the test isolates one rule:

```python
rec = build_example_record(fake)
rec.update(_case="name_max_length", full_name="X" * 100)   # boundary: exactly at limit
rec.update(_violates="name_max_length", full_name="X" * 101)  # negative: one past it
```

Boundary values come from the scenarios' asserted limits, not from guesses. Typical families when the package states them: length limits (at, one under, one over), date cutoffs (day-of, day-before, day-after), numeric ranges (min, max, min-1, max+1), required fields (present vs `None` vs empty string — these are three different bugs).

## Locale

Default `en_US`. If the feature serves multilingual populations and scenarios say so, generate a labeled slice with other locales (`Faker(["en_US", "es_ES"])` picks randomly; seed still applies). Non-ASCII names are themselves a useful edge case for encoding bugs — include a few even in en_US data via e.g. `"José", "Nguyễn"` literals in boundary sets when text handling is in scope.
