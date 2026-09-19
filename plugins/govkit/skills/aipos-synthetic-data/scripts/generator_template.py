#!/usr/bin/env python3
"""Synthetic test data generator — <WORK-ITEM-ID>.

Generated for the GovKit feature package at /features/<WORK-ITEM-ID>/.
ALL OUTPUT IS SYNTHETIC (Python Faker). No real records were used.

Deterministic: the same --seed always produces byte-identical output.
Dependencies: python 3.9+ and `pip install faker` — nothing else.

Usage:
    python generate_test_data.py                 # default seed, all datasets
    python generate_test_data.py --seed 42
    python generate_test_data.py --outdir data/
"""

import argparse
import csv
import json
import random
from datetime import date, datetime
from pathlib import Path

from faker import Faker

DEFAULT_SEED = 20260707  # fixed so regeneration is reproducible; override with --seed
LOCALE = "en_US"


# ---------------------------------------------------------------------------
# Determinism setup — seed BOTH faker and stdlib random, in this order.
# ---------------------------------------------------------------------------
def make_faker(seed: int) -> Faker:
    Faker.seed(seed)
    random.seed(seed)
    return Faker(LOCALE)


# ---------------------------------------------------------------------------
# Serialization helpers
# ---------------------------------------------------------------------------
def _jsonable(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def write_jsonl(records: list, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for rec in records:
            f.write(json.dumps({k: _jsonable(v) for k, v in rec.items()},
                               sort_keys=True) + "\n")


def write_csv(records: list, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not records:
        # An intentionally empty dataset still gets written so loaders can
        # detect the zero-cardinality case. Supply columns explicitly if a
        # header row is required.
        path.write_text("", encoding="utf-8")
        return
    fields = list(records[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for rec in records:
            writer.writerow({k: _jsonable(v) for k, v in rec.items()})


def write_sql(records: list, table: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"-- SYNTHETIC DATA (Python Faker) for table {table}. Not real records.",
             "BEGIN;"]
    for rec in records:
        cols = ", ".join(rec.keys())
        vals = ", ".join(_sql_literal(v) for v in rec.values())
        lines.append(f"INSERT INTO {table} ({cols}) VALUES ({vals});")
    lines.append("COMMIT;")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _sql_literal(value) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, (date, datetime)):
        return f"'{value.isoformat()}'"
    return "'" + str(value).replace("'", "''") + "'"


# ---------------------------------------------------------------------------
# Record builders — REPLACE with entities from the feature package's
# data profile. Every record carries the synthetic marker.
# ---------------------------------------------------------------------------
def build_example_record(fake: Faker) -> dict:
    """One happy-path record. Field set comes from the data profile —
    every field traces to a Given/When/Then step or data table column."""
    return {
        "_synthetic": True,
        "id": fake.uuid4(),
        "full_name": fake.name(),
        "email": fake.email(),
        # Dates frozen at authoring time — never "today"/"now", which would
        # make regeneration drift day by day. Take the window from the spec.
        "submitted_on": fake.date_between(start_date=date(2025, 7, 7),
                                          end_date=date(2026, 7, 7)),
        "status": random.choice(["received", "in_review", "approved", "denied"]),
    }


def happy_records(fake: Faker, count: int) -> list:
    return [build_example_record(fake) for _ in range(count)]


def boundary_records(fake: Faker) -> list:
    """One record per boundary the scenarios assert (min/max/limits/cutoffs).
    Tag each with _case so a failing test names the boundary it hit."""
    records = []
    # Example: earliest allowed submission date
    rec = build_example_record(fake)
    rec.update(_case="submitted_on_min", submitted_on=date(2025, 7, 7))
    records.append(rec)
    return records


def negative_records(fake: Faker) -> list:
    """One record per violated constraint — exactly one violation each,
    named in _violates, so failures point at a single rule."""
    records = []
    rec = build_example_record(fake)
    rec.update(_violates="email_format", email="not-an-email")
    records.append(rec)
    return records


# ---------------------------------------------------------------------------
# Main — zero/one/many happy sets, boundary, negative, optional volume
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--outdir", type=Path, default=Path("data"))
    parser.add_argument("--volume", type=int, default=0,
                        help="record count for the NFR volume dataset (0 = skip)")
    args = parser.parse_args()

    fake = make_faker(args.seed)
    out = args.outdir

    # Zero / one / many — collection bugs cluster at these cardinalities.
    write_jsonl([], out / "example_happy_zero.jsonl")
    write_jsonl(happy_records(fake, 1), out / "example_happy_one.jsonl")
    write_jsonl(happy_records(fake, 25), out / "example_happy_many.jsonl")

    write_jsonl(boundary_records(fake), out / "example_boundary.jsonl")
    write_jsonl(negative_records(fake), out / "example_negative.jsonl")

    if args.volume:
        write_csv(happy_records(fake, args.volume), out / "example_volume.csv")

    print(f"Generated synthetic datasets in {out}/ (seed={args.seed})")


if __name__ == "__main__":
    main()
