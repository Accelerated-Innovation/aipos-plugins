import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def routing():
    spec = importlib.util.spec_from_file_location("run_routing", ROOT / "evals/run_routing.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def catalog():
    return [{"name": "author", "description": "Write new specs."},
            {"name": "review", "description": "Review existing specs."}]


@pytest.fixture
def case():
    return {"id": "c", "prompt": "Write a spec then review it.", "context": "No spec exists.",
            "critical": True, "split": "development",
            "allowed": [{"action": "skill", "skill": "author", "handoffs": ["review"]}]}


def test_subject_sees_descriptions_and_request_but_no_answer(routing, catalog, case):
    system, user = routing.build_request(catalog, case)
    assert all(c["description"] in system for c in catalog)
    assert json.loads(user) == {"context": case["context"], "request": case["prompt"]}
    assert "allowed" not in system + user
    assert "critical" not in system + user


def test_catalog_reads_folded_yaml_and_never_the_body(routing, tmp_path):
    skill = tmp_path / "plugin/skills/example"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text('---\nname: example\ndescription: >\n  First line\n  second line\n---\nSECRET BODY\n')
    assert routing.discover_catalog(tmp_path) == [{"name": "example", "description": "First line second line"}]


def test_catalog_refuses_folder_name_disagreement(routing, tmp_path):
    skill = tmp_path / "plugin/skills/example"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text('---\nname: another\ndescription: text\n---\n')
    with pytest.raises(ValueError, match="disagree"):
        routing.discover_catalog(tmp_path)


def test_duplicate_catalog_names_are_not_silently_overwritten(routing, catalog):
    with pytest.raises(ValueError, match="duplicate"):
        routing.validate_catalog(catalog + catalog)


def test_empty_catalog_is_not_a_pass(routing):
    with pytest.raises(ValueError, match="empty"):
        routing.validate_catalog([])


def test_missing_case_skill_fails_before_any_api_call(routing, catalog, case):
    case["allowed"][0]["skill"] = "absent"
    with pytest.raises(ValueError, match="primary"):
        routing.validate_cases([case], catalog)


def test_handoff_order_and_primary_owner_are_graded(routing, catalog, case):
    assert routing.grade(case["allowed"][0], case, catalog)
    assert not routing.grade({"action": "skill", "skill": "review", "handoffs": ["author"]}, case, catalog)
    assert not routing.grade({"action": "skill", "skill": "author", "handoffs": []}, case, catalog)


@pytest.mark.parametrize("action", ["none", "clarify"])
def test_no_skill_and_clarification_are_real_outcomes(routing, catalog, case, action):
    route = {"action": action, "skill": None, "handoffs": []}
    case["allowed"] = [route]
    assert routing.grade(route, case, catalog)
    with pytest.raises(ValueError):
        routing.grade({**route, "skill": "author"}, case, catalog)


def test_catalog_case_model_and_configuration_changes_invalidate_results(routing, catalog, case):
    before = routing.fingerprint(catalog, case, "model-a", 1000, 3)
    variants = [
        ([{**catalog[0], "description": "Changed"}, catalog[1]], case, "model-a", 1000, 3),
        (catalog, {**case, "prompt": "Changed"}, "model-a", 1000, 3),
        (catalog, case, "model-b", 1000, 3),
        (catalog, case, "model-a", 2000, 3),
        (catalog, case, "model-a", 1000, 1),
    ]
    assert all(routing.fingerprint(*args) != before for args in variants)


def test_stale_and_torn_results_are_not_reused(routing, tmp_path):
    path = tmp_path / "results.jsonl"
    routing.append(path, {"id": "a", "rep": 0, "fingerprint": "old", "passed": True})
    routing.append(path, {"id": "b", "rep": 0, "fingerprint": "current", "passed": False})
    with path.open("a") as f:
        f.write('{"id":')
    assert set(routing.read_results(path, {("a", 0): "new", ("b", 0): "current"})) == {("b", 0)}


def test_incomplete_or_critical_failure_cannot_pass_the_summary(routing):
    planned = {("a", 0), ("b", 0)}
    rows = {("a", 0): {"passed": True}}
    summary = routing.summarize(rows, planned, {"b"})
    assert summary["pass_rate"] == .5
    assert summary["missing"] == 1 and not summary["accepted"]
    assert summary["critical_failures_or_missing"] == ["b:rep0"]
    rows[("b", 0)] = {"passed": True}
    assert routing.summarize(rows, planned, {"b"})["accepted"]


def test_dry_run_snapshot_can_replay_without_a_plugin_tree(routing, tmp_path):
    snapshot = tmp_path / "inputs.json"
    assert routing.main(["--snapshot-out", str(snapshot)]) == 0
    assert routing.main(["--snapshot-in", str(snapshot), "--plugins", str(tmp_path / "absent")]) == 0


def test_execute_requires_an_explicit_model_and_call_cap(routing):
    with pytest.raises(SystemExit) as error:
        routing.main(["--execute"])
    assert error.value.code == 2


def test_unknown_case_does_not_silently_run_zero_cases(routing):
    with pytest.raises(SystemExit) as error:
        routing.main(["--case", "does-not-exist"])
    assert error.value.code == 2
