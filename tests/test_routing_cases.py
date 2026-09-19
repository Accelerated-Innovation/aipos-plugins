"""Routing expectations refer to real capabilities, before a skill is loaded."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_routing_cases_cover_the_catalog_and_reference_real_skills():
    names = {p.parent.name for p in (ROOT / "plugins").glob("*/skills/*/SKILL.md")}
    cases = json.loads((ROOT / "evals/routing/cases.json").read_text())["cases"]
    assert names and cases
    assert len({c["id"] for c in cases}) == len(cases)
    for case in cases:
        assert case["prompt"].strip()
        assert case["split"] in {"development", "heldout"}
        assert isinstance(case["critical"], bool)
        assert case["allowed"]
        for route in case["allowed"]:
            assert route["action"] in {"skill", "clarify", "none"}
            if route["action"] == "skill":
                assert route["skill"] in names
                assert set(route["handoffs"]) <= names
            else:
                assert route["skill"] is None and not route["handoffs"]
    for name in names:
        positives = [c for c in cases if c["split"] == "development"
                     and any(r["skill"] == name for r in c["allowed"])]
        assert len(positives) >= 2, name
    assert any(c["split"] == "heldout" for c in cases)
    assert any(r["action"] == "none" for c in cases for r in c["allowed"])
    assert any(r["action"] == "clarify" for c in cases for r in c["allowed"])

