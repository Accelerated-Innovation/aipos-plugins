#!/usr/bin/env python3
"""
Verify a scores.json against the GovKit rubric's own arithmetic and decision rules.

This is a hard gate, not a lint. Batch scoring is done by language models reading a
rubric, and the single most common defect is a reported total that does not match its
own dimensions -- which silently moves a feature across a decision band. Catch it here,
before it becomes a badge somebody trusts.

Usage:
    python verify_scores.py scores.json [--features features.json] [--fix-sums]
                            [--scale refine|readiness]

--scale picks the rubric the verdicts came from: "refine" (default) is
aipos-feature-refine's 10-dimension scale (Approved >= 8); "readiness" is
aipos-feature-readiness's 12-dimension scale (Approved >= 10, Blocked < 8.5).

Exit codes:
    0  every check passed
    1  at least one check failed (details on stdout)
    2  could not read or parse the input
"""

import argparse
import json
import sys

SCALES = {
    # aipos-feature-refine: 10-dimension Gherkin Quality Rubric.
    "refine": {
        "dimensions": [
            "Outcome and scope",
            "Business language",
            "Rule coverage",
            "Example specificity",
            "Scenario structure",
            "Observable outcomes",
            "Implementation neutrality",
            "Edge cases and permissions",
            "NFR alignment",
            "Evaluation and evidence alignment",
        ],
        "approved": 8.0,
        "with_edits": 7.0,
    },
    # aipos-feature-readiness: 12-dimension repo-side readiness rubric.
    "readiness": {
        "dimensions": [
            "Feature package completeness",
            "Source traceability",
            "Gherkin syntax and structure",
            "Behavior clarity",
            "Observable outcomes",
            "Rule and edge-case coverage",
            "NFR readiness",
            "Evaluation criteria readiness",
            "Repo fit",
            "Test and evidence execution path",
            "AI coding agent safety",
            "Handoff quality",
        ],
        "approved": 10.0,
        "with_edits": 8.5,
    },
}
VALID_SCORES = {0.0, 0.5, 1.0}
DECISIONS = {"Approved", "Approved with edits", "Blocked"}


def expected_decision(score, n_blockers, scale):
    """The rubric's rule: blockers gate, the score only bands what is left."""
    if n_blockers > 0:
        return "Blocked"
    if score >= scale["approved"]:
        return "Approved"
    if score >= scale["with_edits"]:
        return "Approved with edits"
    return "Blocked"


def check(scores, features=None, scale_name="refine"):
    failures, warnings = [], []
    scale = SCALES[scale_name]
    n_dims = len(scale["dimensions"])
    feats = scores.get("features", scores)

    if not feats:
        failures.append("scores.json contains no features")
        return failures, warnings

    for key, v in feats.items():
        if key.startswith("_"):
            continue
        p = f"{key}:"

        dims = v.get("dimensions") or []
        if len(dims) != n_dims:
            failures.append(
                f"{p} has {len(dims)} dimensions, expected {n_dims} "
                f"({scale_name} scale -- wrong --scale?)"
            )
            continue

        for i, d in enumerate(dims):
            if d.get("score") not in VALID_SCORES:
                failures.append(
                    f"{p} dimension {i+1} score {d.get('score')!r} is not 1.0, 0.5 or 0.0"
                )
            if d.get("name") != scale["dimensions"][i]:
                warnings.append(
                    f"{p} dimension {i+1} is {d.get('name')!r}, rubric order expects "
                    f"{scale['dimensions'][i]!r}"
                )
            if not (d.get("note") or "").strip():
                warnings.append(f"{p} dimension {i+1} has no note")

        actual = round(sum(float(d.get("score", 0)) for d in dims), 2)
        stated = v.get("score")
        if stated is None:
            failures.append(f"{p} has no score")
        elif round(float(stated), 2) != actual:
            failures.append(
                f"{p} score is stated as {stated} but its dimensions sum to {actual}"
            )

        blockers = v.get("blockers", [])
        if not isinstance(blockers, list):
            failures.append(f"{p} blockers is not a list")
            blockers = []

        decision = v.get("decision")
        if decision not in DECISIONS:
            failures.append(f"{p} decision {decision!r} is not one of {sorted(DECISIONS)}")
        else:
            want = expected_decision(actual, len(blockers), scale)
            if decision != want:
                failures.append(
                    f"{p} decision is {decision!r} but score {actual} with "
                    f"{len(blockers)} blocker(s) requires {want!r}"
                )

        edits = v.get("edits", [])
        if not edits:
            warnings.append(f"{p} has no edits; even an Approved draft usually has some")
        if not (v.get("summary") or "").strip():
            warnings.append(f"{p} has no summary")

        # A near-zero score that is not flagged is almost always an unreviewable
        # record rather than a genuinely terrible spec. Say so rather than badging it.
        if actual <= 1.0 and not v.get("notAssessable"):
            warnings.append(
                f"{p} scored {actual} without notAssessable set -- if the spec lives "
                f"outside this record, set the flag so the badge does not misread it"
            )

    if features:
        fkeys = {f["key"] for f in features}
        skeys = {k for k in feats if not k.startswith("_")}
        for missing in sorted(fkeys - skeys):
            failures.append(f"{missing}: present in features.json but never scored")
        for extra in sorted(skeys - fkeys):
            failures.append(f"{extra}: scored but absent from features.json")

    return failures, warnings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scores")
    ap.add_argument("--features", help="cross-check that every feature was scored")
    ap.add_argument(
        "--fix-sums",
        action="store_true",
        help="rewrite each stated score from its dimensions and re-derive the decision",
    )
    ap.add_argument(
        "--scale",
        choices=sorted(SCALES),
        default="refine",
        help="which rubric produced the verdicts: refine (10 dims, default) or "
        "readiness (12 dims, bands 10 / 8.5)",
    )
    a = ap.parse_args()

    try:
        scores = json.load(open(a.scores))
        features = json.load(open(a.features)) if a.features else None
    except Exception as exc:  # noqa: BLE001
        print(f"could not read input: {exc}")
        return 2

    scale = SCALES[a.scale]
    if a.fix_sums:
        feats = scores.get("features", scores)
        changed = []
        for key, v in feats.items():
            if key.startswith("_") or len(v.get("dimensions") or []) != len(scale["dimensions"]):
                continue
            actual = round(sum(float(d.get("score", 0)) for d in v["dimensions"]), 2)
            want = expected_decision(actual, len(v.get("blockers", [])), scale)
            if v.get("score") != actual or v.get("decision") != want:
                changed.append(f"  {key}: {v.get('score')} {v.get('decision')!r} -> {actual} {want!r}")
                v["score"], v["decision"] = actual, want
        json.dump(scores, open(a.scores, "w"), indent=1, ensure_ascii=False)
        print("corrected:" if changed else "nothing to correct")
        print("\n".join(changed))

    failures, warnings = check(scores, features, a.scale)

    for w in warnings:
        print(f"WARN  {w}")
    for f in failures:
        print(f"FAIL  {f}")

    n = len([k for k in scores.get("features", scores) if not k.startswith("_")])
    if failures:
        print(f"\n{len(failures)} failure(s) across {n} feature(s). Do not render this.")
        return 1
    print(f"\nOK: {n} feature(s) verified, {len(warnings)} warning(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
