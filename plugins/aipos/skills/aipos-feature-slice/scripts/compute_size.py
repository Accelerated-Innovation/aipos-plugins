#!/usr/bin/env python3
"""
Compute scenario sizes and feature rollups from dimension judgments.

The split between judged and computed is deliberate: a language model judges the three
complexity dimensions, this script does all the arithmetic. A model that also sums its
own points will sooner or later report a total its dimensions do not support, and the
band is what release planning runs on. The sizing schema carries no totals at all, so
a wrong total cannot even be stated -- it can only be computed, here, correctly.

Usage:
    python compute_size.py sizing.json [-o sizing_computed.json] [--features features.json]

Input: one feature object ({"key": ..., "scenarios": [...]}), a {"features": {key: obj}}
map, or a JSON array of feature objects. Scenarios carry integer 1-3 judgments for
dataState, integration and uiSteps, plus optional taggedSlice / recommendedSlice.

Exit codes:
    0  computed and written; summary on stdout
    1  at least one validation failure (nothing written)
    2  could not read or parse the input
"""

import argparse
import json
import sys

DIMS = ("dataState", "integration", "uiSteps")
SLICES = ("mvp", "v1", "v2")


def band(points):
    """Small 3-4, Medium 5-7, Large 8-9."""
    if points <= 4:
        return "small"
    if points <= 7:
        return "medium"
    return "large"


def normalize(data):
    """Accept a single feature, a {"features": {...}} map, or an array."""
    if isinstance(data, list):
        return {f.get("key", f"feature-{i}"): f for i, f in enumerate(data)}, None
    if isinstance(data, dict) and "scenarios" in data:
        return {data.get("key", "feature"): data}, None
    if isinstance(data, dict) and "features" in data:
        return dict(data["features"]), data.get("_meta")
    return None, None


def validate(key, feat):
    failures, warnings = [], []
    p = f"{key}:"

    scenarios = feat.get("scenarios")
    if not scenarios:
        failures.append(f"{p} has no scenarios")
        return failures, warnings

    for i, s in enumerate(scenarios):
        name = s.get("name") or f"scenario {i + 1}"
        sp = f"{p} {name!r}:"
        if not s.get("name"):
            failures.append(f"{p} scenario {i + 1} has no name")

        dims = s.get("dimensions") or {}
        for d in DIMS:
            v = dims.get(d)
            # bool is an int subclass; a judgment of `true` is a schema error, not a 1
            if not isinstance(v, int) or isinstance(v, bool) or not 1 <= v <= 3:
                failures.append(f"{sp} {d} is {v!r}, expected an integer 1-3")
        for extra in set(dims) - set(DIMS):
            failures.append(f"{sp} unknown dimension {extra!r}")

        notes = s.get("notes") or {}
        for d in DIMS:
            if not (notes.get(d) or "").strip():
                warnings.append(f"{sp} {d} has no grounding note")

        for field in ("taggedSlice", "recommendedSlice"):
            v = s.get(field)
            if v is not None and v not in SLICES:
                failures.append(f"{sp} {field} {v!r} is not one of {list(SLICES)} or null")
        if s.get("recommendedSlice") and not (s.get("sliceRationale") or "").strip():
            warnings.append(f"{sp} recommendedSlice has no sliceRationale")

    return failures, warnings


def compute(feat):
    """Annotate scenarios and attach the feature rollup. Mutates and returns feat."""
    counts = {"small": 0, "medium": 0, "large": 0}
    slice_points = {"mvp": 0, "v1": 0, "v2": 0, "untagged": 0}
    total = 0
    risk_flags, split_candidates = [], []

    for s in feat["scenarios"]:
        pts = sum(s["dimensions"][d] for d in DIMS)
        b = band(pts)
        s["points"], s["band"] = pts, b
        s["splitRecommended"] = b == "large"

        tagged, recommended = s.get("taggedSlice"), s.get("recommendedSlice")
        s["effectiveSlice"] = tagged or recommended
        s["sliceSource"] = "tagged" if tagged else ("recommended" if recommended else None)

        counts[b] += 1
        total += pts
        slice_points[s["effectiveSlice"] or "untagged"] += pts
        if b == "large":
            split_candidates.append(s["name"])
            if s["effectiveSlice"] == "mvp":
                risk_flags.append(
                    f"{s['name']!r} is Large ({pts} pts) on the MVP critical path "
                    f"({s['sliceSource']} slice) -- split it or record an explicit risk acceptance"
                )

    feat["rollup"] = {
        "counts": counts,
        "totalPoints": total,
        "badge": (
            f"{counts['large']}L / {counts['medium']}M / {counts['small']}S "
            f"- {total} pts"
        ),
        "slicePoints": slice_points,
        "riskFlags": risk_flags,
        "splitCandidates": split_candidates,
    }
    return feat


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sizing")
    ap.add_argument("-o", "--out", help="output path (default: <input>_computed.json)")
    ap.add_argument("--features", help="cross-check that every feature was sized")
    a = ap.parse_args()

    try:
        data = json.load(open(a.sizing, encoding="utf-8"))
        features = json.load(open(a.features, encoding="utf-8")) if a.features else None
    except Exception as exc:  # noqa: BLE001
        print(f"could not read input: {exc}")
        return 2

    feats, meta = normalize(data)
    if feats is None:
        print("input is not a feature object, a features map, or an array of features")
        return 2

    failures, warnings = [], []
    for key, feat in feats.items():
        f, w = validate(key, feat)
        failures += f
        warnings += w

    if features:
        fkeys = {f["key"] for f in features}
        skeys = set(feats)
        for missing in sorted(fkeys - skeys):
            failures.append(f"{missing}: present in features.json but never sized")
        for extra in sorted(skeys - fkeys):
            warnings.append(f"{extra}: sized but absent from features.json")
        by_key = {f["key"]: f for f in features}
        for key in sorted(skeys & fkeys):
            want = by_key[key].get("scenarioCount")
            got = len(feats[key].get("scenarios") or [])
            if want is not None and want != got:
                warnings.append(
                    f"{key}: sized {got} scenario(s) but features.json says {want}"
                )
            # taggedSlice must mirror the record's tags -- a verdict that drops or
            # invents a tag silently un-decides (or decides) a release plan. Read the
            # effective tags: a slice declared on the Feature or the Rule applies to the
            # scenarios beneath it, and older records that carry only `tags` still work.
            def slice_of(s):
                # Most specific declaration wins: the scenario's own tag, then one
                # inherited from the Rule or the Feature.
                for source in (s.get("tags") or [],
                               s.get("effectiveTags") or s.get("tags") or []):
                    for t in source:
                        n = t.lstrip("@").lower()
                        if n in SLICES:
                            return n
                return None

            tag_of = {
                s.get("name"): slice_of(s)
                for r in by_key[key].get("rules") or []
                for s in r.get("scenarios") or []
            }
            for s in feats[key].get("scenarios") or []:
                if s.get("name") in tag_of and s.get("taggedSlice") != tag_of[s["name"]]:
                    warnings.append(
                        f"{key}: {s.get('name')!r} taggedSlice is {s.get('taggedSlice')!r} "
                        f"but the record's tags say {tag_of[s['name']]!r}"
                    )

    for w in warnings:
        print(f"WARN  {w}")
    for f in failures:
        print(f"FAIL  {f}")
    if failures:
        print(f"\n{len(failures)} failure(s). Nothing written -- fix the judgments first.")
        return 1

    for key, feat in feats.items():
        compute(feat)

    out = {"_meta": meta, "features": feats} if meta else {"features": feats}
    out_path = a.out or a.sizing.replace(".json", "") + "_computed.json"
    json.dump(out, open(out_path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

    for key, feat in feats.items():
        r = feat["rollup"]
        sp = r["slicePoints"]
        line = f"{key}: {r['badge']}"
        if any(v for k, v in sp.items() if k != "untagged"):
            line += (
                f"  (mvp {sp['mvp']} / v1 {sp['v1']} / v2 {sp['v2']}"
                f" / untagged {sp['untagged']})"
            )
        print(line)
        for flag in r["riskFlags"]:
            print(f"  RISK  {flag}")

    print(f"\nOK: {len(feats)} feature(s) computed, {len(warnings)} warning(s) -> {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
