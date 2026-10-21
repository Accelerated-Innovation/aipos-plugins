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
    return checker.check_text((FIXTURES / f"{name}.agent-contract.md").read_text(encoding="utf-8"))


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
    text = (FIXTURES / "complete.agent-contract.md").read_text(encoding="utf-8").replace("- Owner: Sales operations lead\n", "")
    report = checker.check_text(text)
    assert report["status"] == "invalid"
    assert any(e["section"] == 0 and "Owner" in e["message"] for e in report["errors"])


def test_unknown_side_effects_are_not_accepted(checker):
    text = (FIXTURES / "complete.agent-contract.md").read_text(encoding="utf-8").replace(
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


def test_text_after_the_contract_is_not_read_as_part_of_it(checker):
    """Found by running the checker on a real eval response: a summary heading and its own table
    after section 6 were parsed as checkpoint rows. A contract ends at a non-contract heading."""
    text = (FIXTURES / "complete.agent-contract.md").read_text(encoding="utf-8")
    text = text.replace("| set_quote_status |", "| `set_quote_status` |")  # backticked names still match
    text += ("\n---\n\n## Status\n\n**Incomplete** — two open TBDs.\n\n"
             "| # | TBD | Owner |\n|---|---|---|\n| 1 | Policy source | Sales operations lead |\n")
    report = checker.check_text(text)
    assert report["status"] == "complete", report["errors"]


def test_only_the_first_table_in_a_section_is_the_sections_table(checker):
    text = (FIXTURES / "complete.agent-contract.md").read_text(encoding="utf-8").replace(
        "## 5. Escalation", "Reference only:\n\n| A | B |\n|---|---|\n| x | y |\n\n## 5. Escalation")
    # The stray table follows section 4's table, separated by prose; it must not be merged into it.
    assert checker.check_text(text)["status"] == "complete"


def test_a_tbd_in_an_optional_column_still_counts(checker):
    text = (FIXTURES / "complete.agent-contract.md").read_text(encoding="utf-8").replace(
        "| Quote references a non-standard contract term | Legal counsel | Stops and holds the quote | |",
        "| Quote references a non-standard contract term | Legal counsel | Stops and holds the quote | "
        "TBD — owner: Legal counsel; needed: the test for a non-standard term |")
    report = checker.check_text(text)
    assert report["status"] == "incomplete"
    assert [(t["section"], t["owner"]) for t in report["tbds"]] == [(5, "Legal counsel")]


def test_a_tbd_line_beside_a_sections_table_counts(checker):
    text = (FIXTURES / "complete.agent-contract.md").read_text(encoding="utf-8").replace(
        "## 3. Outputs",
        "TBD — owner: Sales operations lead; needed: which tool supplies the discount policy\n\n## 3. Outputs")
    report = checker.check_text(text)
    assert [(t["section"], t["owner"]) for t in report["tbds"]] == [(2, "Sales operations lead")]
    unowned = (FIXTURES / "complete.agent-contract.md").read_text(encoding="utf-8").replace(
        "## 3. Outputs", "TBD: the policy tool\n\n## 3. Outputs")
    assert any(e["section"] == 2 and "owner" in e["message"] for e in checker.check_text(unowned)["errors"])


def test_a_row_that_is_an_owned_tbd_needs_no_other_cells(checker):
    """An entry known to exist but not yet describable is one row carrying an owned TBD."""
    text = (FIXTURES / "complete.agent-contract.md").read_text(encoding="utf-8").replace(
        "| Quote references a non-standard contract term | Legal counsel | Stops and holds the quote | |",
        "| Quote references a non-standard contract term | Legal counsel | Stops and holds the quote | |\n"
        "| | | | TBD — owner: Sales operations lead; needed: what happens when an escalation goes unanswered |")
    report = checker.check_text(text)
    assert report["status"] == "incomplete", report["errors"]
    assert [(t["section"], t["owner"]) for t in report["tbds"]] == [(5, "Sales operations lead")]


def test_mentioning_a_tbd_is_not_declaring_one(checker):
    text = (FIXTURES / "complete.agent-contract.md").read_text(encoding="utf-8").replace(
        "| Approval recommendation | Deal desk manager | Summary with policy citations | |",
        "| Approval recommendation | Deal desk manager | Summary with policy citations | see the TBD in §2 |")
    assert checker.check_text(text)["status"] == "complete"


def test_personal_data_may_carry_a_detail_after_yes_or_no(checker):
    text = (FIXTURES / "complete.agent-contract.md").read_text(encoding="utf-8").replace(
        "| Quote record | CPQ system | yes |", "| Quote record | CPQ system | yes — customer name and contact |")
    assert checker.check_text(text)["status"] == "complete"
    bad = text.replace("yes — customer name and contact", "probably")
    assert checker.check_text(bad)["status"] == "invalid"


def test_bare_tbds_inside_an_owned_tbd_row_are_covered_by_its_owner(checker):
    text = (FIXTURES / "complete.agent-contract.md").read_text(encoding="utf-8").replace(
        "| read_quote | Load the quote under review | read | no | |",
        "| read_quote | Load the quote under review | read | no | |\n"
        "| TBD — owner: Sales operations lead; needed: whether the recommendation is written back | | TBD | TBD | |")
    report = checker.check_text(text)
    assert report["status"] == "incomplete", report["errors"]
    assert len(report["tbds"]) == 1
    # Outside such a row, a bare TBD is still an error.
    bare = (FIXTURES / "complete.agent-contract.md").read_text(encoding="utf-8").replace(
        "| read_quote | Load the quote under review | read | no | |", "| read_quote | Load the quote under review | TBD | no | |")
    assert checker.check_text(bare)["status"] == "invalid"


def test_a_row_of_empty_cells_is_not_a_table_separator(checker):
    text = (FIXTURES / "complete.agent-contract.md").read_text(encoding="utf-8").replace(
        "| Input | Source | Contains personal data | Notes |\n|---|---|---|---|",
        "| Input | Source | Contains personal data | Notes |\n| | | | |")
    report = checker.check_text(text)
    assert any(e["section"] == 1 for e in report["errors"]), report["errors"]


def test_a_repeated_section_number_is_invalid(checker):
    base = (FIXTURES / "complete.agent-contract.md").read_text(encoding="utf-8")
    outputs = base[base.index("## 3. Outputs"):base.index("## 4. Guardrails")]
    report = checker.check_text(base.replace("## 4. Guardrails", outputs + "## 4. Guardrails"))
    assert any(e["section"] == 3 and "more than once" in e["message"] for e in report["errors"])


def test_an_unconfirmed_write_must_say_who_decided(checker):
    base = (FIXTURES / "complete.agent-contract.md").read_text(encoding="utf-8")
    silent = base.replace("| set_quote_status | Mark the quote approved or returned | write | yes — Deal desk manager | |",
                          "| set_quote_status | Mark the quote approved or returned | write | no | |")
    report = checker.check_text(silent)
    assert any(e["section"] == 2 and "who decided" in e["message"] for e in report["errors"])
    owned = silent.replace("| set_quote_status | Mark the quote approved or returned | write | no | |",
                           "| set_quote_status | Mark the quote approved or returned | write | no | Decided by the sales operations lead |")
    owned = owned.replace("| Status change review | set_quote_status | Deal desk manager | The approve or return decision |\n", "")
    assert checker.check_text(owned)["status"] == "complete"


def test_a_checkpoint_names_its_tool_anywhere_in_before_but_not_as_a_fragment(checker):
    base = (FIXTURES / "complete.agent-contract.md").read_text(encoding="utf-8")
    prose = base.replace("| Email review | send_approval_email |", "| Email review | each `send_approval_email` call |")
    assert checker.check_text(prose)["status"] == "complete"
    fragment = base.replace("| Email review | send_approval_email |", "| Email review | send_approval |")
    assert any("send_approval_email" in e["message"] for e in checker.check_text(fragment)["errors"])


def test_an_unreadable_contract_exits_2(checker, tmp_path):
    script = skill_path("aipos-agent-contract") / "scripts" / "check_contract.py"
    missing = subprocess.run([sys.executable, str(script), str(tmp_path / "nope.md")],
                             capture_output=True, text=True, timeout=30)
    binary = tmp_path / "bad.md"; binary.write_bytes(b"\xff\xfe\x00bad")
    undecodable = subprocess.run([sys.executable, str(script), str(binary)],
                                 capture_output=True, text=True, timeout=30)
    for run in (missing, undecodable):
        assert run.returncode == 2 and "Cannot read" in run.stderr and "Traceback" not in run.stderr
