"""A Solution Design canvas is quoted from, so its numbers and its provenance must hold.

Two fixtures anchor this file:

* `example-as-drawn.json` is the hand-made example canvas that started this work, transcribed
  as drawn. It carries three arithmetic errors a reader would repeat: a -30% target on a move
  that is -33%, a "1 min saved" on a metric that moves 0.6, and 166 hours that is really 100.
  The verifier exists to catch exactly these.
* `triage-from-graph.json` is the same problem built the governed way from the mock graph:
  facts cite graph references, and what the graph does not hold is an evidence GAP wired to a
  ReOps to-do, a panel-5 assumption and a panel-6 plan item.

The remaining tests each break one rule of the contract and check that the verifier names it.
Each builds its input by mutating a copy of the good canvas, so a rule is tested by the failure
it prevents rather than by a helper that agrees with the code.
"""

from __future__ import annotations

import copy
import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "plugins/aipos/skills/aipos-solution-design/scripts/verify_canvas.py"
FIXTURES = ROOT / "tests/fixtures/canvas"


@pytest.fixture(scope="module")
def vc():
    spec = importlib.util.spec_from_file_location("verify_canvas", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load(name):
    return json.loads((FIXTURES / f"{name}.json").read_text())


@pytest.fixture()
def good():
    return load("triage-from-graph")


def codes(report):
    return {e["code"] for e in report.errors}


def warning_codes(report):
    return {w["code"] for w in report.warnings}


# --- the two anchors ---------------------------------------------------------


def test_the_example_as_drawn_fails_on_its_own_arithmetic(vc):
    report, computed = vc.verify(load("example-as-drawn"))
    assert {"TARGET_INCONSISTENT", "SAVING_INCONSISTENT", "IMPACT_INCONSISTENT"} <= codes(report)
    assert computed["metrics"]["m1"]["change_pct"] == pytest.approx(-33.33)
    assert computed["impact_at_scale"]["saving_per_unit"] == pytest.approx(0.6)
    assert computed["impact_at_scale"]["result"] == pytest.approx(100.0)
    messages = " ".join(e["message"] for e in report.errors)
    assert "= 100" in messages and "-33.33%" in messages


def test_the_example_as_drawn_surfaces_the_routing_outcome_with_no_baseline(vc):
    report, _ = vc.verify(load("example-as-drawn"))
    flagged = {w["path"] for w in report.warnings if w["code"] == "GAP_WITHOUT_TODO"}
    assert "panels.metrics[1].baseline" in flagged


def test_the_governed_canvas_passes_and_shows_formulas_not_numbers(vc, good):
    report, computed = vc.verify(good)
    assert report.errors == []
    impact = computed["impact_at_scale"]
    assert impact["result"] is None
    assert impact["formula"] == "GAP × GAP ÷ 60"
    assert set(impact["blocked_by"]) == {"panels.metrics[0].baseline", "footer.scale.volume"}
    assert computed["gaps"] == {"evidence": 3, "decision": 0}
    assert computed["proceed_available"] is False


# --- provenance --------------------------------------------------------------


def test_an_evidence_fact_must_cite_what_the_graph_returned(vc, good):
    good["panels"]["problem"]["impact"][0]["refs"] = ["zendesk:tkt-invented"]
    assert "REF_NOT_IN_GRAPH" in codes(vc.verify(good)[0])


def test_an_evidence_fact_without_references_is_refused(vc, good):
    good["panels"]["problem"]["impact"][0]["refs"] = []
    assert "E_WITHOUT_REF" in codes(vc.verify(good)[0])


def test_a_fact_without_a_mark_is_refused(vc, good):
    del good["panels"]["problem"]["impact"][0]["mark"]
    assert "FACT_UNMARKED" in codes(vc.verify(good)[0])


def test_a_decision_carries_no_provenance_mark(vc, good):
    good["goal"]["mark"] = "E"
    assert "DECISION_MARKED" in codes(vc.verify(good)[0])


def test_a_pm_remembered_figure_stays_an_assumption_beside_the_gap(vc, good):
    """D14: the PM's recollection is kept, never promoted to evidence, never computed with."""
    baseline = good["panels"]["metrics"][0]["baseline"]
    baseline["assumed"] = {"value": 1.8, "mark": "A", "said_by": "PM"}
    report, computed = vc.verify(good)
    assert report.errors == []
    assert computed["metrics"]["m1"]["change_pct"] is None

    baseline["assumed"]["mark"] = "E"
    assert "ASSUMED_MARK" in codes(vc.verify(good)[0])

    baseline["value"] = 1.8
    assert "GAP_HAS_VALUE" in codes(vc.verify(good)[0])


def test_filling_a_gap_from_the_graph_unlocks_the_numbers(vc, good):
    """What refresh-on-resume does: a baseline arrives in the graph and the formula resolves."""
    good["source"]["evidence_refs"].append({
        "provenance_reference": "reops:study-ts-07-result", "source_system": "reops",
        "source_type": "study_outcome", "occurred_at": "2026-10-01T00:00:00Z", "record_url": None})
    good["panels"]["metrics"][0]["baseline"] = {
        "kind": "fact", "status": "confirmed", "value": 1.8, "mark": "E",
        "refs": ["reops:study-ts-07-result"]}
    report, computed = vc.verify(good)
    m1 = computed["metrics"]["m1"]
    assert m1["target"] == pytest.approx(1.26) and m1["target_derived"] is True
    assert computed["proceed_available"] is True
    assert "TODO_STALE" in warning_codes(report), "the to-do that gathered it should be closed"
    assert "TODO_ORPHANED" not in codes(report)


# --- gap wiring ----------------------------------------------------------------


@pytest.mark.parametrize("break_it,code", [
    (lambda c: c["todos"].pop(0), "GAP_WITHOUT_TODO"),
    (lambda c: c["panels"]["assumptions"].pop(0), "GAP_WITHOUT_ASSUMPTION"),
    (lambda c: c["panels"]["assumptions"][0].update(retired_by=[]), "ASSUMPTION_NOT_RETIRED"),
])
def test_an_evidence_gap_is_wired_through_the_canvas_in_coach_mode(vc, good, break_it, code):
    break_it(good)
    assert code in codes(vc.verify(good)[0])


def test_workshop_mode_tolerates_unwired_gaps_but_still_names_them(vc, good):
    good["mode"] = "workshop"
    good["todos"].pop(0)
    report, _ = vc.verify(good)
    assert "GAP_WITHOUT_TODO" not in codes(report)
    assert "GAP_WITHOUT_TODO" in warning_codes(report)


def test_an_open_decision_blocks_coach_mode_until_gaps_are_accepted(vc, good):
    good["panels"]["validation"]["recommendation"]["owner"] = {
        "kind": "decision", "status": "gap", "value": None, "gap_type": "decision"}
    assert "DECISION_GAP" in codes(vc.verify(good)[0])
    good["gaps_accepted"] = True
    assert "DECISION_GAP" not in codes(vc.verify(good)[0])


def test_a_todo_must_point_at_a_real_field(vc, good):
    good["todos"].append({**good["todos"][0], "id": "t9", "field": "panels.nowhere"})
    assert "TODO_ORPHANED" in codes(vc.verify(good)[0])


# --- the decision --------------------------------------------------------------


def test_proceed_is_unavailable_while_the_primary_baseline_is_a_gap(vc, good):
    good["panels"]["validation"]["recommendation"]["decision"] = "proceed"
    assert "PROCEED_BLOCKED" in codes(vc.verify(good)[0])
    for allowed in ("pivot", "park"):
        good["panels"]["validation"]["recommendation"]["decision"] = allowed
        report, computed = vc.verify(good)
        assert "PROCEED_BLOCKED" not in codes(report)
    assert computed["aipos_decision"] == "no-go"


def test_canvas_decisions_map_to_the_aipos_vocabulary(vc):
    assert vc.DECISIONS == {"proceed": "go", "pivot": "revise", "park": "no-go"}


# --- evidence -----------------------------------------------------------------


def test_a_quote_is_verbatim_and_approved(vc, good):
    good["panels"]["evidence"]["voice"]["quote"] = "it takes forever to reach anyone"
    assert "QUOTE_NOT_VERBATIM" in codes(vc.verify(good)[0])

    good = load("triage-from-graph")
    good["panels"]["evidence"]["voice"]["approved_for_canvas"] = False
    assert "QUOTE_NOT_APPROVED" in warning_codes(vc.verify(good)[0])
    good["stage"] = "approved"
    assert "QUOTE_NOT_APPROVED" in codes(vc.verify(good)[0])


def test_a_snapshot_example_is_a_record_the_graph_returned_text_for(vc, good):
    good["panels"]["problem"]["snapshot"][0]["ref"] = "reops:int-0412"  # held, but no text
    assert "SNAPSHOT_WITHOUT_EXCERPT" in codes(vc.verify(good)[0])


def test_evidence_counts_and_dates_are_computed_from_the_graph_read(vc, good):
    _, computed = vc.verify(good)
    tiles = computed["evidence"]["tiles"]
    assert [t["count"] for t in tiles] == [3, 3, 1, 1]
    assert tiles[2]["undated"] == 1 and tiles[2]["latest"] is None
    assert tiles[0]["earliest"] == "2026-07-08" and tiles[0]["latest"] == "2026-07-14"


def test_unknown_dates_are_never_treated_as_old(vc, good):
    _, computed = vc.verify(good)
    undated_tile = computed["evidence"]["tiles"][2]
    assert undated_tile["aging"] is False


def test_aging_evidence_is_flagged_against_the_read_date(vc, good):
    for row in good["source"]["evidence_refs"]:
        if row["occurred_at"]:
            row["occurred_at"] = "2023-06-14T10:00:00Z"
    report, computed = vc.verify(good)
    assert computed["evidence"]["tiles"][0]["aging"] is True
    assert {"EVIDENCE_AGING", "ALL_EVIDENCE_AGING"} <= warning_codes(report)


def test_one_originating_source_is_named_whatever_the_count(vc, good):
    good["source"]["originating_sources"] = ["gong:call-7781"]
    report, computed = vc.verify(good)
    assert computed["evidence"]["single_source"] is True
    assert "SINGLE_SOURCE" in warning_codes(report)


def test_an_unsupported_graph_schema_version_stops_the_canvas(vc, good):
    good["source"]["schema_version"] = 2
    assert "SCHEMA_VERSION_UNSUPPORTED" in codes(vc.verify(good)[0])


# --- metrics -------------------------------------------------------------------


def test_exactly_one_primary_metric_and_it_is_an_outcome(vc, good):
    good["panels"]["metrics"][1]["primary"] = True
    assert "PRIMARY_METRIC" in codes(vc.verify(good)[0])
    good = load("triage-from-graph")
    good["panels"]["hypothesis"]["outcomes"] = ["m2"]
    assert "PRIMARY_NOT_OUTCOME" in codes(vc.verify(good)[0])


def test_direction_and_sign_agree(vc, good):
    good["panels"]["metrics"][0]["target_change_pct"]["value"] = 30
    assert "DIRECTION" in codes(vc.verify(good)[0])


def test_a_metric_needs_a_target(vc, good):
    del good["panels"]["metrics"][0]["target_change_pct"]
    assert "NO_TARGET" in codes(vc.verify(good)[0])


def test_options_come_in_twos_or_threes_with_tradeoffs(vc, good):
    good["panels"]["options"] = good["panels"]["options"][:1]
    assert "OPTION_COUNT" in codes(vc.verify(good)[0])
    good = load("triage-from-graph")
    good["panels"]["options"][0]["cons"] = []
    assert "OPTION_TRADEOFFS" in codes(vc.verify(good)[0])


# --- the command line -------------------------------------------------------


def test_cli_exit_codes_and_write(tmp_path):
    bad = subprocess.run([sys.executable, str(SCRIPT), str(FIXTURES / "example-as-drawn.json")],
                         capture_output=True, text=True, cwd=tmp_path)
    assert bad.returncode == 1 and json.loads(bad.stdout)["ok"] is False

    target = tmp_path / "canvas.json"
    target.write_text((FIXTURES / "triage-from-graph.json").read_text())
    ok = subprocess.run([sys.executable, str(SCRIPT), str(target), "--write"],
                        capture_output=True, text=True, cwd=tmp_path)
    assert ok.returncode == 0, ok.stdout
    written = json.loads(target.read_text())
    assert written["computed"]["impact_at_scale"]["formula"] == "GAP × GAP ÷ 60"
    # the computed block is output, never input: a second run ignores and rewrites it
    written["computed"]["impact_at_scale"]["result"] = 999
    target.write_text(json.dumps(written))
    again = json.loads(subprocess.run([sys.executable, str(SCRIPT), str(target)],
                                      capture_output=True, text=True).stdout)
    assert again["computed"]["impact_at_scale"]["result"] is None


# --- the reference and the script name the same rules ------------------------


def test_every_verifier_code_is_documented_and_every_documented_code_exists():
    """The skill reads canvas-schema.md to explain a failure to the PM. A code the doc does not
    list is one the skill cannot explain; a listed code the script never raises is a rule the
    PM is told about that nothing enforces."""
    import re

    source = SCRIPT.read_text()
    raised = set(re.findall(r'"([A-Z][A-Z_]{3,})"', source))
    doc = (SCRIPT.parents[1] / "references" / "canvas-schema.md").read_text()
    listed = set(re.findall(r"`([A-Z][A-Z_]+)`", doc.split("## Verifier codes", 1)[1]))
    assert raised, "the pattern found no codes — the test is not looking at anything"
    assert raised == listed, {"undocumented": sorted(raised - listed),
                              "unenforced": sorted(listed - raised)}
