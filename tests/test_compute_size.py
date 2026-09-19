"""Slicing arithmetic must keep agreeing with the record after ingestion changed shape.

compute_size cross-checks a verdict's taggedSlice against the feature record. If that
check reads only a scenario's own tags, a slice declared on the Feature or the Rule looks
like an invented tag and every such scenario warns.
"""

import json
import pathlib
import subprocess
import sys

from skill_paths import skill_path

SCRIPT = skill_path("govkit-feature-slice") / "scripts" / "compute_size.py"


def sizing_for(feat):
    return {
        "key": feat["key"],
        "scenarios": [
            {
                "rule": r["rule"] or None,
                "name": sc["name"],
                "dimensions": {"dataState": 2, "integration": 1, "uiSteps": 2},
                "notes": {"dataState": "n", "integration": "n", "uiSteps": "n"},
                "taggedSlice": slice_tag(sc),
                "recommendedSlice": slice_tag(sc) or "v1",
                "sliceRationale": "fixture",
                "splitHint": None,
            }
            for r in feat["rules"] for sc in r["scenarios"]
        ],
    }


def slice_tag(sc):
    for source in (sc.get("tags") or [], sc.get("effectiveTags") or []):
        for t in source:
            n = t.lstrip("@").lower()
            if n in ("mvp", "v1", "v2"):
                return n
    return None


def run(tmp_path, feat):
    sizing = tmp_path / "sizing.json"
    features = tmp_path / "features.json"
    out = tmp_path / "computed.json"
    sizing.write_text(json.dumps(sizing_for(feat)))
    features.write_text(json.dumps([feat]))
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), str(sizing), "--features", str(features),
         "-o", str(out)],
        capture_output=True, text=True)
    return proc, (json.loads(out.read_text()) if out.exists() else None)


def test_inherited_slice_tag_does_not_look_like_an_invented_verdict(ingested, tmp_path):
    feat = ingested["inv_full"]
    # The rejection scenario has no slice tag of its own; @v1 comes from the Feature.
    rejection = feat["rules"][0]["scenarios"][1]
    assert not any(t.lstrip("@") in ("mvp", "v1", "v2") for t in rejection["tags"])
    proc, computed = run(tmp_path, feat)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "WARN" not in proc.stdout
    assert computed["features"][feat["key"]]["rollup"]["slicePoints"]["v1"] > 0


def test_a_scenario_own_tag_still_wins_over_an_inherited_one(ingested, tmp_path):
    feat = ingested["inv_full"]
    outline = feat["rules"][0]["scenarios"][0]
    assert "@mvp" in outline["tags"] and "@v1" in outline["inheritedTags"]
    assert slice_tag(outline) == "mvp"
    proc, computed = run(tmp_path, feat)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert computed["features"][feat["key"]]["rollup"]["slicePoints"]["mvp"] > 0
