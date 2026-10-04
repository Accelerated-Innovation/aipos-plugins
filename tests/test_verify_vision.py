"""A Product Vision's mode, roster and readiness are computed, so the computation is the contract.

The skill's own facilitation is coaching and is graded by the model-run evals. What is checkable
deterministically is the part a person never recomputes by hand: which questions a mode and scope
ask for, who the risk triage routes the vision to, and whether it is ready.

Two things anchor this file:

* `tests/fixtures/vision/*.json` are whole vision records, one per axis combination plus the
  failure cases the checks exist for — a fabricated figure, a missing urgency, a mis-scoped
  increment, a Learn-mode grant with no reason, a drifted statement. Each declares its own
  `_expect_exit`, because a fixture that passes with warnings and one that fails are different
  outcomes and were confused for each other once.
* `scripts/check_content.py` is the lint over `flow-content.json`. Its rules were each learned
  from a question that went wrong, so running it here keeps them from being quietly deleted.

The suite ran red for several turns during the skill's first real use, unnoticed, because it was
run by hand. That is why it is in the repository gate rather than in a shell script beside it.
"""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import pytest

from skill_paths import skill_path

SKILL = skill_path("aipos-product-vision")
SCRIPTS = SKILL / "scripts"
FIXTURES = sorted((pathlib.Path(__file__).resolve().parent / "fixtures" / "vision").glob("*.json"))


def run(script, *args):
    return subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, args)],
                          capture_output=True, text=True)


def test_there_are_fixtures_to_check():
    """A glob that stopped matching would pass this file forever."""
    assert len(FIXTURES) >= 8


@pytest.mark.parametrize("path", FIXTURES, ids=lambda p: p.stem)
def test_a_fixture_verifies_to_its_declared_outcome(path):
    """Exit 0 is ready, 1 is a check failing, 2 is a malformed record. Each fixture says which
    it is, so a fixture that starts passing is as loud as one that starts failing."""
    expected = json.loads(path.read_text(encoding="utf-8")).get("_expect_exit", 0)
    proc = run("verify_vision.py", path, "--json")
    assert proc.returncode == expected, (
        f"{path.name}: expected exit {expected}, got {proc.returncode}\n{proc.stdout}\n{proc.stderr}")


@pytest.mark.parametrize("path", FIXTURES, ids=lambda p: p.stem)
def test_the_verifier_reports_a_roster_and_a_readiness_number(path):
    """The record is what travels, so the two computed fields it travels with have to be there
    whatever the outcome — including on a record that failed its checks."""
    proc = run("verify_vision.py", path, "--json")
    assert proc.returncode in (0, 1), proc.stderr
    report = json.loads(proc.stdout)
    assert report["mode"] in ("learn", "commit")
    assert report["scope"] in ("new", "increment", "revision")
    assert isinstance(report["roster"], list)
    readiness = report["readiness"]
    assert isinstance(readiness["meter_percent"], (int, float))
    assert 0 <= readiness["meter_percent"] <= 100
    assert isinstance(readiness["ready"], bool)
    assert report["tier"]["tier"].startswith("tier_")


@pytest.mark.parametrize("path", FIXTURES, ids=lambda p: p.stem)
def test_the_todo_names_actions_rather_than_counts(path):
    """`--todo` exists because the first report was four numbers and no instruction. It must
    still run on every record, including a clean one."""
    proc = run("verify_vision.py", path, "--todo")
    assert proc.returncode in (0, 1), proc.stderr
    assert proc.stdout.strip()


def test_questions_print_for_every_axis_combination():
    """Asking from a block description instead of this script asks Commit-mode questions in a
    Learn-mode vision, which is the failure the script prevents."""
    seen = {}
    for mode in ("learn", "commit"):
        for scope in ("new", "increment"):
            proc = run("questions.py", mode, scope)
            assert proc.returncode == 0, proc.stderr
            seen[(mode, scope)] = proc.stdout
            assert proc.stdout.strip()
    assert seen[("learn", "new")] != seen[("commit", "new")], (
        "Learn and Commit asked the same questions - the mode is not reaching the filter")
    assert seen[("commit", "increment")] != seen[("commit", "new")], (
        "new and increment asked the same questions - the scope is not reaching the filter")


def test_an_unrecognised_argument_is_refused_rather_than_defaulted():
    """It used to fall through to commit:new and print a plausible question set under a nonsense
    heading, which is the one failure a facilitator would not catch by reading the output."""
    for args in (("--mode", "learn"), ("banana", "new"), ("learn", "sideways"),
                 ("learn", "new", "extra")):
        proc = run("questions.py", *args)
        assert proc.returncode == 2, f"{args} was accepted: {proc.stdout}"
        assert "usage" in proc.stderr.lower()


def test_the_content_lint_passes():
    """Every question carries a worked example, no question carries its own nudge limit, SKILL.md
    references no question id that no longer exists, and the evidence-marks rule is in both the
    data and the skill."""
    proc = run("check_content.py")
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_the_data_files_are_valid_json_and_versioned():
    """Three data files are the skill's contract with a future AIOS screen. A screen reads them
    directly, so a malformed one breaks a surface this repository cannot see."""
    for name in ("flow-content.json", "engagement-policy.json", "readiness-rules.json"):
        data = json.loads((SKILL / "data" / name).read_text(encoding="utf-8"))
        assert isinstance(data, dict) and data, name
        assert any(k.endswith("version") for k in data), f"{name} declares no version"
