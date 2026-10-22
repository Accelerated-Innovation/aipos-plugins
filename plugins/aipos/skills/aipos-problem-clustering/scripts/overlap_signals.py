#!/usr/bin/env python3
"""Turn captured graph reads into a draft cluster review with overlap signals.

Input: a `cluster-reads.v1` capture — the source and capture time, read coverage, and per problem
the `get_problem`, `list_evidence` and `get_lineage` responses (optionally redacted excerpts from
`get_evidence_text`). Output: a `cluster-review.v1` draft holding the problems, their evidence
references, and the overlaps a reviewer should look at:

  shared_evidence  two problems cite the same provenance reference
  shared_origin    two problems trace to the same originating source
  shared_persona   two problems name the same persona

Signals are where to look, not verdicts. Five problems extracted from one call share an origin and
can still be five problems; the reviewer decides, citing evidence. Suggestions are added to the
review by the skill, never by this script.

    python3 overlap_signals.py reads.json -o review.json

Standard library only.
"""

from __future__ import annotations

import argparse
import json
import sys
from itertools import combinations
from pathlib import Path

READS = "cluster-reads.v1"
REVIEW = "cluster-review.v1"


def _problem(entry: dict) -> dict:
    problem, evidence, lineage = entry["problem"], entry["evidence"], entry["lineage"]
    for name, payload in (("problem", problem), ("lineage", lineage)):
        if payload.get("schema_version") != 1:
            raise ValueError(f"{problem.get('problem_id')}: {name} schema_version "
                             f"{payload.get('schema_version')!r} is not 1; stop rather than guess")
    for item in evidence.get("items", []):
        if item.get("schema_version") != 1:
            raise ValueError(f"{problem['problem_id']}: evidence schema_version {item.get('schema_version')!r} is not 1")
    if evidence.get("problem_id") != problem["problem_id"] or lineage.get("problem_id") != problem["problem_id"]:
        raise ValueError(f"{problem['problem_id']}: evidence or lineage belongs to another problem")
    return {
        "problem_id": problem["problem_id"],
        "title": problem["title"],
        "composite_score": problem["composite_score"],
        "personas": [{"name": p["name"], "confidence": p["confidence"]} for p in problem["personas"]],
        # The engine exposes no workflow tags: None is "unknown", an empty list would claim "none".
        "workflow_tags": None,
        "evidence": [{k: item.get(k) for k in ("provenance_reference", "source_system", "source_type",
                                               "occurred_at", "record_url")}
                     for item in evidence.get("items", [])],
        "originating_sources": list(lineage.get("originating_sources", [])),
    }


def _signals(problems: list[dict]) -> list[dict]:
    found = []
    for a, b in combinations(problems, 2):
        pair = [a["problem_id"], b["problem_id"]]
        refs_a = {e["provenance_reference"] for e in a["evidence"]}
        refs_b = {e["provenance_reference"] for e in b["evidence"]}
        for kind, shared in (
            ("shared_evidence", refs_a & refs_b),
            ("shared_origin", set(a["originating_sources"]) & set(b["originating_sources"])),
            ("shared_persona", {p["name"] for p in a["personas"]} & {p["name"] for p in b["personas"]}),
        ):
            if shared:
                found.append({"kind": kind, "problems": pair, "refs": sorted(shared)})
    return found


def build_review(reads: dict) -> dict:
    if reads.get("contract") != READS:
        raise ValueError(f"expected a {READS} capture")
    problems = [_problem(entry) for entry in reads["problems"]]
    ids = [p["problem_id"] for p in problems]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate problem ids in the capture")
    return {
        "contract": REVIEW,
        "draft": True,
        "source": reads["source"],
        "coverage": reads["coverage"],
        "problems": problems,
        "signals": _signals(problems),
        "suggestions": [],
        "excerpts": list(reads.get("excerpts", [])),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("reads", type=Path)
    parser.add_argument("-o", "--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        review = build_review(json.loads(args.reads.read_text(encoding="utf-8")))
    except (ValueError, KeyError, TypeError) as exc:
        print(f"Cannot build review: {exc}", file=sys.stderr)
        return 1
    args.output.write_text(json.dumps(review, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(str(args.output.resolve()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
