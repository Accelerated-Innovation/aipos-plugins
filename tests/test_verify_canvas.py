"""A Solution Framing canvas is quoted from, so its numbers and its provenance must hold.

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
SCRIPT = ROOT / "plugins/aipos/skills/aipos-solution-framing/scripts/verify_canvas.py"
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
    (lambda c: (c["panels"]["assumptions"][0].update(retired_by=[]),
                [p.update(retires=[r for r in p["retires"] if r != "a1"])
                 for p in c["panels"]["validation"]["plan"]]), "ASSUMPTION_NOT_RETIRED"),
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


# --- found in review: the D14 guarantees must hold for hostile input too -----


@pytest.mark.parametrize("baseline", [
    {"kind": "fact", "status": "confirmed", "value": 1.8, "mark": "A", "refs": []},
    {"kind": "fact", "status": "provisional", "value": 1.8, "mark": "I", "refs": [], "note": "PM said"},
    {"kind": "decision", "status": "confirmed", "value": 1.8},
], ids=["assumed-as-fact", "inferred-from-a-note", "baseline-as-decision"])
def test_proceed_cannot_rest_on_a_baseline_the_graph_did_not_supply(vc, good, baseline):
    good["panels"]["metrics"][0]["baseline"] = baseline
    good["panels"]["validation"]["recommendation"]["decision"] = "proceed"
    report, computed = vc.verify(good)
    assert "PROCEED_BLOCKED" in codes(report)
    assert computed["proceed_available"] is False
    assert codes(report) & {"FACT_ASSUMED", "I_WITHOUT_BASIS", "WRONG_KIND"}


def test_the_example_as_drawn_cannot_recommend_proceed(vc):
    report, computed = vc.verify(load("example-as-drawn"))
    assert "PROCEED_BLOCKED" in codes(report)
    assert "OWNER_MISSING" in codes(report)


def test_a_missing_fact_cannot_be_typed_as_a_decision_to_skip_its_wiring(vc, good):
    baseline = good["panels"]["metrics"][1]["baseline"]
    baseline["gap_type"] = "decision"
    good["gaps_accepted"] = True
    assert "GAP_TYPE" in codes(vc.verify(good)[0])


@pytest.mark.parametrize("junk", [
    "Tickets arrive uncategorized",
    {"kind": "fact", "value": "x", "mark": "E", "refs": ["zendesk:made-up"]},
], ids=["bare-string", "status-less-dict"])
def test_content_that_is_not_shaped_like_a_field_is_still_checked(vc, good, junk):
    good["panels"]["problem"]["pain_points"][0] = junk
    assert "NOT_A_FIELD" in codes(vc.verify(good)[0])


def test_a_number_stored_as_text_is_refused_not_silently_dropped(vc, good):
    good["source"]["evidence_refs"].append({"provenance_reference": "reops:x", "source_system": "reops",
        "source_type": "study_outcome", "occurred_at": None, "record_url": None})
    good["panels"]["metrics"][0]["baseline"] = {"kind": "fact", "status": "confirmed", "value": "1.8",
                                                "mark": "E", "refs": ["reops:x"]}
    assert "NOT_NUMERIC" in codes(vc.verify(good)[0])


def test_numbers_in_prose_are_flagged_because_nothing_checks_them(vc, good):
    good["footer"]["success"]["value"] = "Save 166 hours a month"
    assert "NUMBER_IN_PROSE" in warning_codes(vc.verify(good)[0])


def test_a_wrong_unit_conversion_is_refused(vc, good):
    good["footer"]["scale"]["per_unit_factor"] = 1
    assert "FACTOR_MISMATCH" in codes(vc.verify(good)[0])
    good["footer"]["scale"]["per_unit_factor"] = 0
    assert "FACTOR_INVALID" in codes(vc.verify(good)[0])


def test_impact_at_scale_needs_a_per_unit_primary_metric(vc, good):
    good["panels"]["metrics"][0]["primary"] = False
    good["panels"]["metrics"][1]["primary"] = True
    good["panels"]["hypothesis"]["outcomes"] = ["m1", "m2"]
    assert "IMPACT_UNIT" in codes(vc.verify(good)[0])


def test_arithmetic_on_zero_and_negative_baselines(vc):
    base = load("example-as-drawn")
    metric = base["panels"]["metrics"][0]
    metric.pop("target_change_pct")
    metric["baseline"]["value"], metric["target"]["value"] = 0, 5
    report, computed = vc.verify(base)
    assert "DIRECTION" in codes(report), "a decrease from 0 to 5 is still the wrong direction"
    assert computed["impact_at_scale"]["blocked_by"] == [], "zero is a value, not a GAP"

    metric["direction"] = "increase"
    metric["baseline"]["value"], metric["target"]["value"] = -5, -3
    metric["target_change_pct"] = {"kind": "decision", "status": "confirmed", "value": 40}
    report, computed = vc.verify(base)
    assert computed["metrics"]["m1"]["change_pct"] == pytest.approx(40.0)
    assert "TARGET_INCONSISTENT" not in codes(report)


def test_percent_metrics_distinguish_relative_change_from_points(vc, good):
    good["source"]["evidence_refs"].append({"provenance_reference": "zendesk:agg-1", "source_system": "zendesk",
        "source_type": "report", "occurred_at": "2026-09-01T00:00:00Z", "record_url": None})
    good["panels"]["metrics"][1]["baseline"] = {"kind": "fact", "status": "confirmed", "value": 60,
                                                "mark": "E", "refs": ["zendesk:agg-1"]}
    assert vc.verify(good)[1]["metrics"]["m2"]["target"] == pytest.approx(72)
    good["panels"]["metrics"][1]["target_change_kind"] = "points"
    assert vc.verify(good)[1]["metrics"]["m2"]["target"] == pytest.approx(80)
    good["panels"]["metrics"][1]["baseline"]["value"] = 90
    assert "OUT_OF_RANGE" in codes(vc.verify(good)[0])
    del good["panels"]["metrics"][1]["target_change_kind"]
    assert "PCT_KIND" in codes(vc.verify(good)[0])


def test_duplicate_refs_do_not_inflate_a_tile(vc, good):
    good["panels"]["evidence"]["tiles"][3]["refs"] = ["gong:call-5530"] * 5
    report, computed = vc.verify(good)
    assert computed["evidence"]["tiles"][3]["count"] == 1
    assert "DUPLICATE_REF" in warning_codes(report)


@pytest.mark.parametrize("break_it", [
    lambda c: c.update(panels=[]),
    lambda c: c["panels"]["metrics"].append(None),
    lambda c: c["source"].update(evidence_refs=None),
    lambda c: c.update(todos={}),
    lambda c: c.update(footer=None),
    lambda c: c["panels"].update(validation=None),
    lambda c: c["panels"]["evidence"]["voice"].update(quote=None),
    lambda c: c["source"].update(read_at=20260922),
    lambda c: c["footer"]["scale"].update(per_unit_factor="1/60"),
], ids=["panels-list", "null-metric", "null-refs", "todos-dict", "null-footer",
        "null-validation", "null-quote", "int-date", "string-factor"])
def test_malformed_input_is_reported_never_a_crash(vc, good, break_it):
    break_it(good)
    report, _ = vc.verify(good)
    assert report.errors


def test_a_canvas_that_is_not_an_object_is_reported(vc):
    report, _ = vc.verify([])
    assert codes(report) == {"MALFORMED"}


def test_an_empty_quote_is_not_verbatim_of_anything(vc, good):
    good["panels"]["evidence"]["voice"]["quote"] = ""
    assert "QUOTE_EMPTY" in codes(vc.verify(good)[0])


def test_a_speaker_role_the_graph_never_gave_is_flagged(vc, good):
    good["panels"]["evidence"]["voice"]["speaker_role"] = "Enterprise Admin"
    assert "SPEAKER_UNSOURCED" in warning_codes(vc.verify(good)[0])


def test_real_records_shown_as_examples_are_approved_too(vc, good):
    good["panels"]["problem"]["snapshot"][0]["approved_for_canvas"] = False
    assert "SNAPSHOT_NOT_APPROVED" in warning_codes(vc.verify(good)[0])
    good["stage"] = "approved"
    assert "SNAPSHOT_NOT_APPROVED" in codes(vc.verify(good)[0])


def test_excerpts_belong_to_the_problem_and_are_few(vc, good):
    good["source"]["excerpts"].append({"provenance_reference": "gong:elsewhere", "text": "x"})
    assert "EXCERPT_NOT_IN_GRAPH" in codes(vc.verify(good)[0])
    good = load("triage-from-graph")
    good["source"]["excerpts"] = good["source"]["excerpts"] * 2
    assert "EXCERPT_CAP" in warning_codes(vc.verify(good)[0])


def test_provisional_content_cannot_be_approved(vc, good):
    good["goal"]["status"] = "provisional"
    assert "PROVISIONAL_AT_APPROVAL" not in codes(vc.verify(good)[0])
    good["stage"] = "approved"
    assert "PROVISIONAL_AT_APPROVAL" in codes(vc.verify(good)[0])


def test_the_primary_baseline_todo_comes_first(vc, good):
    good["todos"] = good["todos"][1:] + good["todos"][:1]
    assert "TODO_ORDER" in warning_codes(vc.verify(good)[0])


# --- found in the second review: progressive checking and [T] --------------


def partial(through_panel):
    """The governed canvas cut back to what exists after a given panel."""
    c = load("triage-from-graph")
    c["through_panel"] = through_panel
    panels = c["panels"]
    if through_panel < 3:
        panels["hypothesis"], panels["metrics"] = {}, []
    if through_panel < 4:
        panels["options"], panels["recommended_option"] = [], None
    if through_panel < 5:
        panels["assumptions"], panels["risks"] = [], []
    if through_panel < 6:
        panels["validation"] = {"plan": [], "recommendation": {"decision": None}}
    if through_panel < 7:
        c["footer"] = {}
    c["todos"] = [t for t in c["todos"] if through_panel >= 3 or not t["field"].startswith("panels.metrics")]
    c["todos"] = [t for t in c["todos"] if through_panel >= 7 or not t["field"].startswith("footer")]
    c["open_questions"] = []
    return c


@pytest.mark.parametrize("through_panel", [1, 2, 3, 4, 5, 6, 7])
def test_a_canvas_in_progress_is_not_failed_for_panels_not_yet_reached(vc, through_panel):
    report, computed = vc.verify(partial(through_panel))
    assert report.errors == [], [e["code"] for e in report.errors]
    assert computed["through_panel"] == through_panel


def test_a_canvas_cannot_be_approved_before_review(vc):
    c = partial(6)
    c["stage"] = "approved"
    assert "INCOMPLETE_AT_APPROVAL" in codes(vc.verify(c)[0])


def test_a_transcribed_figure_computes_but_does_not_unlock_proceed(vc, good):
    """A person keyed it in from a record the graph links: traceable, not graph-supplied."""
    study = next(r for r in good["source"]["evidence_refs"]
                 if r["provenance_reference"] == "reops:study-ts-07")
    study["record_url"] = "https://fixture.invalid/reops/study-ts-07"
    good["panels"]["metrics"][0]["baseline"] = {
        "kind": "fact", "status": "confirmed", "value": 1.8, "mark": "T", "refs": ["reops:study-ts-07"],
        "note": "read from the study record_url by the PM, 2026-09-22"}
    good["todos"].pop(0)
    good["panels"]["assumptions"][0]["from_gap"] = None
    report, computed = vc.verify(good)
    assert computed["metrics"]["m1"]["target"] == pytest.approx(1.26)
    assert computed["proceed_available"] is False
    good["panels"]["validation"]["recommendation"]["decision"] = "proceed"
    assert "PROCEED_BLOCKED" in codes(vc.verify(good)[0])
    del good["panels"]["metrics"][0]["baseline"]["note"]
    assert "T_WITHOUT_RECORD" in codes(vc.verify(good)[0])


def test_a_record_with_no_url_cannot_be_transcribed_from(vc, good):
    """The fixture's time study comes back with record_url null: nothing to read the figure from,
    so a [T] value citing it is refused and the baseline has to stay a GAP."""
    good["panels"]["metrics"][0]["baseline"] = {
        "kind": "fact", "status": "confirmed", "value": 1.8, "mark": "T", "refs": ["reops:study-ts-07"],
        "note": "read from the study by the PM, 2026-09-22"}
    good["todos"].pop(0)
    good["panels"]["assumptions"][0]["from_gap"] = None
    assert "T_WITHOUT_URL" in codes(vc.verify(good)[0])


def test_the_unit_conversion_is_derived_when_not_given(vc, good):
    del good["footer"]["scale"]["per_unit_factor"]
    good["footer"]["scale"]["result_unit"] = "agent-hours/month"
    report, computed = vc.verify(good)
    assert computed["impact_at_scale"]["per_unit_factor"] == pytest.approx(1 / 60)
    assert "FACTOR_MISMATCH" not in codes(report)
    good["footer"]["scale"]["per_unit_factor"] = 1
    assert "FACTOR_MISMATCH" in codes(vc.verify(good)[0]), "'agent-hours' is still hours"


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
