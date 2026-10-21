"""The agent-contract completeness checker reports structure, never content.

`aipos-agent-contract` bundles `scripts/check_contract.py` against the shared schema in
`plugins/aipos/references/agent-contract.md`. Downstream skills (dialogue flows, eval cases,
risk review) read contracts in that shape, so the checker has to catch the defects that make
a contract unusable to them: a missing section, a tool without a side effect or confirmation
status, an escalation without a trigger or human role, a TBD nobody owns, a confirmed tool with
no checkpoint. These tests assert the checker's verdicts on fixtures, not any wording.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest

from skill_paths import skill_path

FIXTURES = pathlib.Path(__file__).resolve().parent / "fixtures" / "agent_contract"


@pytest.fixture(scope="module")
def checker():
    script = skill_path("aipos-agent-contract") / "scripts" / "check_contract.py"
    spec = importlib.util.spec_from_file_location("check_contract", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check(checker, name):
    return checker.check_text((FIXTURES / f"{name}.agent-contract.md").read_text())


def test_a_complete_contract_is_complete(checker):
    report = check(checker, "complete")
    assert report["status"] == "complete", report["errors"]
    assert report["errors"] == [] and report["tbds"] == []
    assert [s["number"] for s in report["sections"]] == [1, 2, 3, 4, 5, 6]
    tools = {t["tool"]: t for t in report["tools"]}
    assert tools["send_approval_email"]["side_effects"] == ["external send"]
    assert tools["send_approval_email"]["confirmation"] == {"value": "yes", "role": "Deal desk manager"}
    assert tools["read_quote"]["confirmation"] == {"value": "no", "role": None}


def test_owned_tbds_make_a_contract_incomplete_not_invalid(checker):
    report = check(checker, "with-tbds")
    assert report["status"] == "incomplete"
    assert report["errors"] == []
    assert {(t["section"], t["owner"]) for t in report["tbds"]} == {
        (2, "Sales operations lead"), (5, "Sales operations lead")}
    assert all(t["needed"] for t in report["tbds"])


@pytest.mark.parametrize("fixture, section, fragment", [
    ("missing-section", 4, "missing"),
    ("out-of-order", 4, "order"),
    ("tool-without-side-effect", 2, "side effect"),
    ("tool-without-side-effect", 2, "confirm"),
    ("tbd-without-owner", 5, "owner"),
    ("escalation-without-role", 5, "role"),
    ("confirm-without-checkpoint", 6, "send_approval_email"),
])
def test_each_structural_defect_is_reported_where_it_is(checker, fixture, section, fragment):
    report = check(checker, fixture)
    assert report["status"] == "invalid"
    assert any(e["section"] == section and fragment in e["message"] for e in report["errors"]), \
        report["errors"]


def test_a_defect_elsewhere_does_not_hide_the_other_sections(checker):
    report = check(checker, "missing-section")
    assert {s["number"] for s in report["sections"]} == {1, 2, 3, 5, 6}
    assert [e["section"] for e in report["errors"]] == [4]


def test_the_header_block_is_required(checker):
    text = (FIXTURES / "complete.agent-contract.md").read_text().replace("- Owner: Sales operations lead\n", "")
    report = checker.check_text(text)
    assert report["status"] == "invalid"
    assert any(e["section"] == 0 and "Owner" in e["message"] for e in report["errors"])


def test_unknown_side_effects_are_not_accepted(checker):
    text = (FIXTURES / "complete.agent-contract.md").read_text().replace(
        "| read_quote | Load the quote under review | read |", "| read_quote | Load the quote under review | harmless |")
    report = checker.check_text(text)
    assert any(e["section"] == 2 and "side effect" in e["message"] for e in report["errors"])


def test_the_cli_reports_json_and_exit_codes(checker):
    script = skill_path("aipos-agent-contract") / "scripts" / "check_contract.py"

    def run(name, *flags):
        return subprocess.run([sys.executable, str(script), str(FIXTURES / f"{name}.agent-contract.md"), *flags],
                              capture_output=True, text=True, timeout=30)

    complete = run("complete")
    assert complete.returncode == 0 and json.loads(complete.stdout)["status"] == "complete"
    incomplete = run("with-tbds")
    assert incomplete.returncode == 0 and json.loads(incomplete.stdout)["status"] == "incomplete"
    assert run("with-tbds", "--require-complete").returncode == 1
    assert run("missing-section").returncode == 2
