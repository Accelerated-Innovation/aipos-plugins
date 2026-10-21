#!/usr/bin/env python3
"""Validate a cluster review and render the offline Cluster Review board.

The board is one self-contained HTML file opened in a browser — not an in-chat panel. It lets a
reviewer compare candidate problems and prepare corrections as pending hand-offs; it writes
nothing anywhere. This script refuses a review that could mislead:

  * the review is not a labelled draft with a source mode and a timezone-aware capture time;
  * a suggestion cites evidence its problems do not hold, or a split has fewer than two sides;
  * anything is marked other than `suggested` or `pending` (nothing here is ever applied);
  * more than five excerpts, an excerpt not marked redacted, over 1,500 characters, or not
    traced to a problem's evidence.

    python3 render_board.py review.json -o board.html

Standard library only.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

ASSETS = Path(__file__).resolve().parent / "assets"
CONTRACT = "cluster-review.v1"
MODES = {"connected", "supplied"}
STATUSES = {"suggested", "pending"}
BASES = {"E", "I"}
MAX_EXCERPTS = 5
MAX_EXCERPT_CHARS = 1500


def validate(review: dict) -> dict:
    if review.get("contract") != CONTRACT:
        raise ValueError(f"expected a {CONTRACT} review")
    if review.get("draft") is not True:
        raise ValueError("a cluster review is always a draft; set draft: true")
    source = review.get("source") or {}
    if source.get("mode") not in MODES:
        raise ValueError(f"source mode must be one of {sorted(MODES)}")
    if not isinstance(source.get("synthetic"), bool):
        raise ValueError("source.synthetic must say whether the records are synthetic")
    captured = datetime.fromisoformat(str(source.get("captured_at", "")).replace("Z", "+00:00"))
    if captured.tzinfo is None:
        raise ValueError("captured_at needs a timezone")

    held = {p["problem_id"]: {e["provenance_reference"] for e in p["evidence"]} | set(p["originating_sources"])
            for p in review["problems"]}
    for s in review.get("suggestions", []):
        label = s.get("id", "?")
        if s.get("status") not in STATUSES:
            raise ValueError(f"suggestion {label}: status {s.get('status')!r} — only suggested or pending; nothing is applied here")
        if s.get("basis") not in BASES:
            raise ValueError(f"suggestion {label}: basis must be E (the cited records show it) or I (inferred)")
        if not s.get("rationale"):
            raise ValueError(f"suggestion {label}: needs a rationale")
        problems = s.get("problems") or []
        unknown = [p for p in problems if p not in held]
        if unknown:
            raise ValueError(f"suggestion {label}: unknown problems {unknown}")
        if s.get("kind") == "merge":
            evidence = s.get("evidence") or {}
            if len(problems) < 2 or set(evidence) != set(problems) or not all(evidence[p] for p in problems):
                raise ValueError(f"suggestion {label}: a merge cites evidence for every problem it joins")
            for problem, refs in evidence.items():
                stray = sorted(set(refs) - held[problem])
                if stray:
                    raise ValueError(f"suggestion {label}: {stray} not held by {problem}")
        elif s.get("kind") == "split":
            sides = s.get("sides") or []
            if len(problems) != 1 or len(sides) < 2:
                raise ValueError(f"suggestion {label}: a split names one problem and at least two sides")
            for side in sides:
                if not side.get("label") or not side.get("evidence"):
                    raise ValueError(f"suggestion {label}: every side needs a label and its own evidence")
                stray = sorted(set(side["evidence"]) - held[problems[0]])
                if stray:
                    raise ValueError(f"suggestion {label}: {stray} not held by {problems[0]}")
        else:
            raise ValueError(f"suggestion {label}: kind must be merge or split")

    excerpts = review.get("excerpts", [])
    if len(excerpts) > MAX_EXCERPTS:
        raise ValueError(f"at most five excerpts per review; got {len(excerpts)}")
    for x in excerpts:
        if x.get("redaction_applied") is not True:
            raise ValueError(f"excerpt {x.get('provenance_reference')}: only redacted excerpts are shown")
        if len(x.get("excerpt", "")) > MAX_EXCERPT_CHARS:
            raise ValueError(f"excerpt {x.get('provenance_reference')}: over {MAX_EXCERPT_CHARS} characters")
        if x.get("provenance_reference") not in held.get(x.get("problem_id"), set()):
            raise ValueError(f"excerpt {x.get('provenance_reference')}: not held by {x.get('problem_id')}")
    return review


def _script_safe(data: str) -> str:
    return (data.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
            .replace("\u2028", "\\u2028").replace("\u2029", "\\u2029"))


def render(review: dict) -> str:
    validate(review)
    data = _script_safe(json.dumps(review, ensure_ascii=False, sort_keys=True))
    page = (ASSETS / "template.html").read_text(encoding="utf-8")
    for marker, value in (("/*STYLE*/", (ASSETS / "style.css").read_text(encoding="utf-8")),
                          ("/*DATA*/", data),
                          ("/*SCRIPT*/", (ASSETS / "board.mjs").read_text(encoding="utf-8"))):
        if page.count(marker) != 1:
            raise ValueError(f"template marker {marker} must appear once")
        page = page.replace(marker, value)
    return page


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("review", type=Path)
    parser.add_argument("-o", "--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.review.resolve() == args.output.resolve():
            raise ValueError("output cannot overwrite the review")
        html = render(json.loads(args.review.read_text(encoding="utf-8")))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(html, encoding="utf-8")
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(f"Cannot render board: {exc}", file=sys.stderr)
        return 1
    print(str(args.output.resolve()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
