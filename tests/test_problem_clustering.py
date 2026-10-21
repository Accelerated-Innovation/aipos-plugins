"""Cluster review: deterministic overlap signals and a board that cannot pretend to correct.

`aipos-problem-clustering` reviews candidate problems and suggests merges and splits. Two bundled
scripts carry the parts that must not depend on model judgment:

* `overlap_signals.py` turns captured graph reads into a draft review with the overlaps a reviewer
  should look at — shared evidence, shared origins, shared personas. Signals are not verdicts:
  five problems extracted from one call share an origin and are still five problems.
* `render_board.py` validates a review (every suggestion cites evidence the problems actually
  hold, at most five redacted excerpts, nothing marked applied) and renders the offline board.

These tests assert those properties on fixtures generated from `evals/mock_pdg`.
"""

from __future__ import annotations

import copy
import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest

from skill_paths import skill_path

FIXTURES = pathlib.Path(__file__).resolve().parent / "fixtures" / "cluster_review"
ROOT = pathlib.Path(__file__).resolve().parents[1]
RENEWAL = ["fixture:prb-renewal-quotes", "fixture:prb-pricing-approvals", "fixture:prb-redline-loss",
           "fixture:prb-renewal-risk", "fixture:prb-quote-templates"]


def load(name):
    script = skill_path("aipos-problem-clustering") / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def signals():
    return load("overlap_signals")


@pytest.fixture(scope="module")
def board():
    return load("render_board")


@pytest.fixture()
def reads():
    return json.loads((FIXTURES / "mock-reads.json").read_text())


@pytest.fixture()
def review(signals, reads):
    return signals.build_review(reads)


def suggestion(review, kind="merge", **extra):
    base = {"id": "s1", "kind": kind, "status": "suggested", "basis": "I",
            "rationale": "[SYNTHETIC] test rationale"}
    base.update(extra)
    review = copy.deepcopy(review)
    review["suggestions"].append(base)
    return review


# --- overlap signals --------------------------------------------------------------


def test_the_review_is_a_labelled_draft_carrying_its_provenance(review, reads):
    assert review["contract"] == "cluster-review.v1"
    assert review["draft"] is True
    assert review["source"] == reads["source"]
    assert review["coverage"] == reads["coverage"]
    assert review["suggestions"] == [] and review["excerpts"] == []
    assert [p["problem_id"] for p in review["problems"]] == [r["problem"]["problem_id"] for r in reads["problems"]]


def test_workflow_tags_are_unknown_not_empty(review):
    """The engine exposes no workflow tags; an empty list would read as 'none'."""
    assert all(p["workflow_tags"] is None for p in review["problems"])


def test_one_shared_origin_is_a_signal_across_all_five_renewal_rows(review):
    origin = [s for s in review["signals"] if s["kind"] == "shared_origin"]
    pairs = {frozenset(s["problems"]) for s in origin if s["refs"] == ["gong:call-7781"]}
    assert len(pairs) == 10  # every pair of the five
    assert all(set(p) <= set(RENEWAL) for p in pairs)


def test_shared_evidence_and_personas_are_separate_signals(review):
    kinds = {(s["kind"], frozenset(s["problems"])) for s in review["signals"]}
    pair = frozenset({"fixture:prb-renewal-quotes", "fixture:prb-quote-templates"})
    assert ("shared_evidence", pair) in kinds
    assert ("shared_persona", pair) in kinds  # both Account Executive
    assert ("shared_persona", frozenset({"fixture:prb-renewal-quotes", "fixture:prb-redline-loss"})) not in kinds


def test_signals_never_carry_a_verdict(review):
    for signal in review["signals"]:
        assert set(signal) == {"kind", "problems", "refs"}


def test_a_newer_schema_version_is_refused_not_guessed(signals, reads):
    reads["problems"][0]["problem"]["schema_version"] = 2
    with pytest.raises(ValueError, match="schema_version"):
        signals.build_review(reads)


def test_failed_reads_stay_visible(signals, reads):
    reads["coverage"]["failed"] = [{"problem_id": "fixture:prb-x", "tool": "list_evidence", "code": "PROBLEM_NOT_FOUND"}]
    assert signals.build_review(reads)["coverage"]["failed"][0]["code"] == "PROBLEM_NOT_FOUND"


# --- board validation --------------------------------------------------------------


def test_a_review_with_no_suggestions_renders(board, review):
    html = board.render(review)
    assert html.startswith("<!doctype html>")
    assert "/*DATA*/" not in html and "/*SCRIPT*/" not in html and "/*STYLE*/" not in html


def test_a_merge_must_cite_evidence_each_problem_holds(board, review):
    ok = suggestion(review, problems=RENEWAL[:2],
                    evidence={RENEWAL[0]: ["gong:call-7781"], RENEWAL[1]: ["gong:call-7781"]})
    board.validate(ok)
    invented = suggestion(review, problems=RENEWAL[:2],
                          evidence={RENEWAL[0]: ["gong:call-7781"], RENEWAL[1]: ["zendesk:tkt-nope"]})
    with pytest.raises(ValueError, match="not held"):
        board.validate(invented)
    one_sided = suggestion(review, problems=RENEWAL[:2], evidence={RENEWAL[0]: ["gong:call-7781"]})
    with pytest.raises(ValueError, match="evidence"):
        board.validate(one_sided)


def test_a_split_needs_two_sides_each_with_its_own_evidence(board, review):
    triage = "fixture:prb-ticket-triage"
    ok = suggestion(review, kind="split", problems=[triage], sides=[
        {"label": "Agents", "persona": "Support Agent", "evidence": ["zendesk:tkt-88121"]},
        {"label": "Admins", "persona": "Enterprise Admin", "evidence": ["gong:call-5530"]}])
    board.validate(ok)
    one = suggestion(review, kind="split", problems=[triage], sides=[
        {"label": "Agents", "evidence": ["zendesk:tkt-88121"]}])
    with pytest.raises(ValueError, match="two sides"):
        board.validate(one)


@pytest.mark.parametrize("status", ["applied", "merged", "done"])
def test_nothing_can_be_marked_applied(board, review, status):
    bad = suggestion(review, problems=RENEWAL[:2], status=status,
                     evidence={RENEWAL[0]: ["gong:call-7781"], RENEWAL[1]: ["gong:call-7781"]})
    with pytest.raises(ValueError, match="status"):
        board.validate(bad)


def test_excerpts_are_capped_redacted_and_traced(board, review):
    row = {"provenance_reference": "gong:call-5530", "problem_id": "fixture:prb-ticket-triage",
           "excerpt": "[SYNTHETIC] Agent: [NAME] said the ticket bounced twice.", "redaction_applied": True,
           "truncated": False}
    ok = copy.deepcopy(review); ok["excerpts"] = [row] * 5
    board.validate(ok)
    six = copy.deepcopy(review); six["excerpts"] = [row] * 6
    with pytest.raises(ValueError, match="five"):
        board.validate(six)
    unredacted = copy.deepcopy(review); unredacted["excerpts"] = [dict(row, redaction_applied=False)]
    with pytest.raises(ValueError, match="redact"):
        board.validate(unredacted)
    stray = copy.deepcopy(review); stray["excerpts"] = [dict(row, provenance_reference="gong:call-0000")]
    with pytest.raises(ValueError, match="not held"):
        board.validate(stray)


def test_provenance_is_required(board, review):
    naive = copy.deepcopy(review); naive["source"]["captured_at"] = "2026-10-21T18:00:00"
    with pytest.raises(ValueError, match="timezone"):
        board.validate(naive)
    unlabelled = copy.deepcopy(review); unlabelled["source"]["mode"] = "live-ish"
    with pytest.raises(ValueError, match="mode"):
        board.validate(unlabelled)
    undrafted = copy.deepcopy(review); undrafted["draft"] = False
    with pytest.raises(ValueError, match="draft"):
        board.validate(undrafted)


def test_hostile_text_cannot_escape_the_data_block(board, review):
    review = copy.deepcopy(review)
    review["problems"][0]["title"] = "</script><script>alert(1)</script> "
    html = board.render(review)
    assert "</script><script>alert(1)" not in html
    assert html.count("<script") == html.count("</script>")


def test_the_page_is_self_contained(board, review):
    html = board.render(review)
    for needle in ("http://", "https://", "src=\"//", "@import"):
        assert needle not in html.replace("https://fixture.invalid", "")


def test_the_cli_renders_and_refuses(tmp_path, signals, reads):
    scripts = skill_path("aipos-problem-clustering") / "scripts"
    reads_file = tmp_path / "reads.json"; reads_file.write_text(json.dumps(reads))
    review_file = tmp_path / "review.json"
    built = subprocess.run([sys.executable, str(scripts / "overlap_signals.py"), str(reads_file), "-o", str(review_file)],
                           capture_output=True, text=True, timeout=30)
    assert built.returncode == 0, built.stderr
    out = tmp_path / "board.html"
    rendered = subprocess.run([sys.executable, str(scripts / "render_board.py"), str(review_file), "-o", str(out)],
                              capture_output=True, text=True, timeout=30)
    assert rendered.returncode == 0, rendered.stderr
    assert out.read_text().startswith("<!doctype html>")
    bad = json.loads(review_file.read_text()); bad["draft"] = False
    review_file.write_text(json.dumps(bad))
    refused = subprocess.run([sys.executable, str(scripts / "render_board.py"), str(review_file), "-o", str(out)],
                             capture_output=True, text=True, timeout=30)
    assert refused.returncode == 1 and "draft" in refused.stderr


def test_packaged_assets_match_the_viewer_source():
    run = subprocess.run([sys.executable, str(ROOT / "viewers" / "cluster-review" / "build.py"), "--check"],
                         capture_output=True, text=True, timeout=30)
    assert run.returncode == 0, run.stdout + run.stderr


@pytest.mark.parametrize("basis", [None, "", "A", "e"])
def test_every_suggestion_says_whether_it_is_evidence_or_inference(board, review, basis):
    bad = suggestion(review, problems=RENEWAL[:2], basis=basis,
                     evidence={RENEWAL[0]: ["gong:call-7781"], RENEWAL[1]: ["gong:call-7781"]})
    with pytest.raises(ValueError, match="basis"):
        board.validate(bad)
