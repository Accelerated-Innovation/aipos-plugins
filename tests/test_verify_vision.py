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


# --------------------------------------------------------------------------
# Each rule below is tested by the failure it prevents. All of these passed
# before the Qodo review on PR #48: the record was malformed and the check
# reported ready anyway, which is the only kind of verifier defect that
# matters — one that fails open.
# --------------------------------------------------------------------------

def load(name):
    return json.loads((pathlib.Path(__file__).resolve().parent / "fixtures" / "vision"
                       / name).read_text(encoding="utf-8"))


def report(vision, tmp_path):
    path = tmp_path / "vision.json"
    path.write_text(json.dumps(vision), encoding="utf-8")
    proc = run("verify_vision.py", path, "--json")
    assert proc.returncode in (0, 1), proc.stderr
    return json.loads(proc.stdout)


def failing(report_):
    return {c["id"] for c in report_["readiness"]["checks"] if c["asked"] and not c["passed"]}


def test_an_empty_learn_grant_stays_in_learn_mode_and_fails_loudly(tmp_path):
    """`learn_mode: {}` used to read as falsey and select Commit mode, so a
    half-started grant bypassed every Learn check — including the L1 failure
    that would have reported it — and produced a Commit report with the wrong
    question set and the wrong roster."""
    vision = load("vision-commit-new-ready.json")
    vision["learn_mode"] = {}
    out = report(vision, tmp_path)
    assert out["mode"] == "learn"
    assert "L1" in failing(out)


def test_an_unanswered_benefits_block_fails_its_blocking_check(tmp_path):
    """V13 was four nested lambdas, and `all()` over an empty list is True, so
    `B0: {}` satisfied a blocking check whose rule reads "B0 has a value for
    every category"."""
    vision = load("vision-commit-new-ready.json")
    for empty in ({}, {"categories": []}):
        vision["blocks"]["B0"] = empty
        assert "V13" in failing(report(vision, tmp_path))


def test_only_the_accountable_owner_can_ratify(tmp_path):
    vision = load("vision-commit-new-ready.json")
    vision["status"] = "ratified"
    vision["ratified_by"] = {"name": "Someone Else"}
    assert "R16" in failing(report(vision, tmp_path))
    vision["ratified_by"] = {"name": vision["accountable_owner"]["name"]}
    assert "R16" not in failing(report(vision, tmp_path))


def test_a_learn_grant_without_its_triage_snapshot_fails(tmp_path):
    """S1 compares the live triage against the snapshot taken when the grant was
    made. Without the snapshot it says nothing, so a risk trigger going live
    after a grant produced no signal at all — the opposite of what the snapshot
    was added for."""
    vision = load("vision-learn-new-ready.json")
    vision["learn_mode"].pop("triage_at_grant")
    assert "L1" in failing(report(vision, tmp_path))


def test_a_review_by_that_is_not_a_date_fails(tmp_path):
    vision = load("vision-learn-new-ready.json")
    vision["learn_mode"]["review_by"] = "sometime"
    assert "L2" in failing(report(vision, tmp_path))


def test_a_response_needs_a_named_responder_and_a_real_date(tmp_path):
    """A blocking reviewer's gate closed on a truthy timestamp and an ID,
    without the record naming who responded."""
    vision = load("vision-commit-new-ready.json")
    reviews = vision.get("reviews") or []
    assert reviews, "fixture carries no reviews"
    reviews[0].pop("responder", None)
    assert "R7" in failing(report(vision, tmp_path))
    reviews[0]["responder"] = {"name": "Priya Raman"}
    reviews[0]["responded_at"] = "whenever"
    assert "R7" in failing(report(vision, tmp_path))


def test_only_a_documented_disposition_closes_a_blocking_raise(tmp_path):
    """Any truthy disposition closed a raise, so `{"type": "dismissed"}` — or a
    rejection with no rationale — left the vision ready."""
    vision = load("vision-commit-new-ready.json")
    raises = [r for review in vision.get("reviews", []) for r in review.get("raises", [])
              if r.get("severity") == "blocking"]
    assert raises, "fixture carries no blocking raise"
    for bad in ({"type": "dismissed"}, {"type": "rejected"}, {"type": "accepted"}):
        raises[0]["disposition"] = bad
        assert "R8" in failing(report(vision, tmp_path)), bad


def test_a_linked_opportunity_has_to_be_accepted(tmp_path):
    vision = load("vision-commit-new-ready.json")
    vision["opportunity_ref"]["accepted"] = False
    assert "R2" in failing(report(vision, tmp_path))


def test_a_sizing_gap_needs_an_owner(tmp_path):
    """V4's rule is "a gap with an owner". An ownerless gap is a note, not a
    plan to close the most fabricated field in any vision."""
    vision = load("vision-commit-new-ready.json")
    vision["blocks"]["B1"] = {"figures": [], "gap": {"text": "No sizing yet."}}
    assert "V4" in failing(report(vision, tmp_path))
    vision["blocks"]["B1"]["gap"]["owner"] = "Dana Okoye"
    assert "V4" not in failing(report(vision, tmp_path))


def test_a_revision_names_what_it_supersedes(tmp_path):
    """Without a predecessor the record is read as a new vision by every check
    that branches on the combination, so the lineage is not merely missing — it
    changes which checks run."""
    vision = load("vision-revision.json")
    vision["supersedes"] = None
    assert "R18" in failing(report(vision, tmp_path))


def test_the_product_language_warning_respects_word_boundaries(tmp_path):
    """"rag" matched inside "storage" and "api" inside "rapid", which put a
    false warning in the author's own to-do list and taught them to distrust it."""
    vision = load("vision-commit-new-ready.json")
    vision["blocks"]["C1"] = ("Reviewers reach a decision from the precedent they need at hand, "
                              "rather than rapid guesswork over capital storage coverage.")
    assert not [w for w in report(vision, tmp_path)["warnings"] if "C1 mentions" in w]
    vision["blocks"]["C1"] = ("They open the dashboard and the chatbot answers from the api, "
                              "which is the whole point of the platform we are building here.")
    assert [w for w in report(vision, tmp_path)["warnings"] if "C1 mentions" in w]


def test_questions_print_their_required_follow_ups(tmp_path):
    """The skill says to ask from this output and nothing else, so a required
    follow-up missing from it is a question that never gets asked. A4's reason,
    A7's how and basis, and D3's stop-ask-or-hand-off were all absent."""
    out = run("questions.py", "commit", "new").stdout
    assert "Why?" in out, "A4's required reason is not printed"
    assert "If so, how?" in out, "A7's follow-up is not printed"
    assert "stop, ask, or hand off" in out, "D3's follow-up is not printed"
    assert "Critical / High Priority" in out, "A4's choices are not printed"
