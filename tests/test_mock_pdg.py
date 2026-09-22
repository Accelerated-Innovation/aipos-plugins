"""The mock opportunity-engine server must stay indistinguishable from the real one in shape.

The skill that reads the Product Definition Graph is built against this mock before a live
engine is reachable. If the mock's shapes drift from the engine's, the skill is built against
something that does not exist and breaks on first contact — silently, because every test here
would still be talking to the mock.

So the expected field sets below are copied from discovery-engine
`src/engine/api/schemas.py` (ProblemSummaryResponse, ProblemDetailResponse, LineageResponse,
EvidenceRefResponse, ScoredOpportunityResponse, ScoreComponentsResponse, WorkItemLinkResponse,
ProblemLinksResponse, EvidenceExcerptResponse). When the engine's contract changes, change them
here first and let the failures say what the mock must follow.

The second concern is containment: this is fixture data and must never pass for evidence.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SERVER = ROOT / "evals" / "mock_pdg" / "server.py"
FIXTURE = ROOT / "evals" / "mock_pdg" / "fixtures" / "default.json"

PROBLEM_SUMMARY = {"problem_id", "title", "composite_score", "lineage_ref", "personas", "schema_version"}
PROBLEM_DETAIL = {"problem_id", "title", "composite_score", "evidence_references", "personas",
                  "lineage_ref", "schema_version"}
PERSONA = {"name", "confidence"}
LINEAGE = {"problem_id", "source_evidence_refs", "originating_sources", "schema_version"}
EVIDENCE_REF = {"provenance_reference", "source_system", "source_type", "external_record_id",
                "occurred_at", "record_url", "schema_version"}
OPPORTUNITY = {"problem_id", "title", "composite_score", "components", "strategic_weight",
               "weight_config_version", "links", "schema_version"}
COMPONENTS = {"evidence_strength", "revenue_impact", "persona_breadth", "recency", "validation_signal"}
LINK = {"link_id", "problem_id", "link_type", "target_system", "target_type", "external_record_id",
        "external_reference", "record_url", "container_ref", "linked_by", "linked_at", "status",
        "outcome_emitted", "schema_version"}
PROBLEM_LINKS = {"problem_id", "promoted", "links", "total", "schema_version"}
EXCERPT = {"provenance_reference", "source_system", "excerpt", "origin", "redaction_applied",
           "anchored", "truncated", "schema_version"}
PAGE = {"items", "total", "offset", "limit"}

TRIAGE = "fixture:prb-ticket-triage"


@pytest.fixture(scope="module")
def mock():
    spec = importlib.util.spec_from_file_location("mock_pdg_server", SERVER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def graph(mock, monkeypatch):
    monkeypatch.delenv("MOCK_PDG_LINKS", raising=False)
    monkeypatch.delenv("MOCK_PDG_EVIDENCE_TEXT", raising=False)
    return mock.Graph(mock.load_fixture(FIXTURE))


def all_problem_ids(graph):
    return [p["problem_id"] for p in graph.problems]


# --- shapes ------------------------------------------------------------------


def test_paged_lists_have_the_engine_shapes(graph):
    problems = graph.list_problems()
    assert set(problems) == PAGE
    for row in problems["items"]:
        assert set(row) == PROBLEM_SUMMARY
        assert all(set(p) == PERSONA for p in row["personas"])
    opportunities = graph.list_opportunities()
    assert set(opportunities) == PAGE
    for row in opportunities["items"]:
        assert set(row) == OPPORTUNITY
        assert set(row["components"]) == COMPONENTS
        assert all(set(link) == LINK for link in row["links"])


@pytest.mark.parametrize("tool,shape", [
    ("get_problem", PROBLEM_DETAIL),
    ("get_lineage", LINEAGE),
    ("get_work_item_links", PROBLEM_LINKS),
])
def test_per_problem_tools_have_the_engine_shapes(graph, tool, shape):
    for pid in all_problem_ids(graph):
        assert set(getattr(graph, tool)(pid)) == shape


def test_evidence_rows_have_the_engine_shape(graph):
    for pid in all_problem_ids(graph):
        result = graph.list_evidence(pid)
        assert set(result) == {"problem_id", "items", "total"}
        assert result["total"] == len(result["items"])
        assert all(set(row) == EVIDENCE_REF for row in result["items"])


def test_an_excerpt_has_the_engine_shape_and_the_only_origin_the_engine_has(graph):
    excerpt = graph.get_evidence_text("gong:call-5530", problem_id=TRIAGE)
    assert set(excerpt) == EXCERPT
    assert excerpt["origin"] == "source"
    assert excerpt["anchored"] is True
    assert graph.get_evidence_text("gong:call-5530")["anchored"] is False


# --- one graph, no disagreement ----------------------------------------------


def test_every_tool_agrees_about_a_problems_evidence(graph):
    """The engine derives all of these from one graph; the mock must not let them diverge."""
    for pid in all_problem_ids(graph):
        detail = graph.get_problem(pid)["evidence_references"]
        lineage = graph.get_lineage(pid)["source_evidence_refs"]
        listed = [row["provenance_reference"] for row in graph.list_evidence(pid)["items"]]
        assert detail == lineage == listed


def test_an_opportunity_is_a_scored_problem_one_to_one(graph):
    problems = [r["problem_id"] for r in graph.list_problems(limit=100)["items"]]
    opportunities = [r["problem_id"] for r in graph.list_opportunities(limit=100)["items"]]
    assert problems == opportunities
    assert len(set(problems)) == len(problems)


def test_ranking_is_highest_composite_first(graph):
    scores = [r["composite_score"] for r in graph.list_problems(limit=100)["items"]]
    assert scores == sorted(scores, reverse=True)


def test_promoted_keys_off_active_promoted_links_only(graph):
    promoted = graph.get_work_item_links("fixture:prb-invoice-dup")
    assert promoted["promoted"] is True
    assert {link["status"] for link in promoted["links"]} == {"active", "severed"}
    row = next(r for r in graph.list_opportunities(limit=100)["items"]
               if r["problem_id"] == "fixture:prb-invoice-dup")
    assert all(link["status"] == "active" for link in row["links"])
    assert graph.get_work_item_links(TRIAGE)["promoted"] is False


# --- the edge cases the skill must handle, present on purpose -----------------


def test_the_fixture_carries_every_edge_case_the_plan_names(graph):
    rows = [row for pid in all_problem_ids(graph) for row in graph.list_evidence(pid)["items"]]
    assert any(row["occurred_at"] is None for row in rows), "null occurred_at (unknown, not old)"
    assert any(row["record_url"] is None for row in rows), "null record_url"
    aging = [row["occurred_at"] for row in graph.list_evidence("fixture:prb-month-end")["items"]]
    assert {d[:4] for d in aging if d} == {"2022", "2023", "2024"}, "2022-2024 aging split"

    origins = {}
    for pid in all_problem_ids(graph):
        for source in graph.get_lineage(pid)["originating_sources"]:
            origins.setdefault(source, set()).add(pid)
    assert max(len(pids) for pids in origins.values()) == 5, "five ranked rows, one source"

    versions = {r["schema_version"] for r in graph.list_opportunities(limit=100)["items"]}
    assert versions == {1, 2}, "a newer schema_version row a consumer must refuse"


def test_the_triage_problem_holds_no_volume_and_no_routing_baseline(graph):
    """The canvas example's 10,000 tickets/month and its routing baseline are NOT in the graph,
    so a skill reading this fixture must produce evidence GAPs for them rather than numbers."""
    texts = []
    for row in graph.list_evidence(TRIAGE)["items"]:
        try:
            texts.append(graph.get_evidence_text(row["provenance_reference"], TRIAGE)["excerpt"])
        except Exception:  # noqa: BLE001 - unreadable sources are part of the case
            pass
    joined = " ".join(texts)
    assert "10,000" not in joined and "10000" not in joined
    assert "%" not in joined


# --- errors the skill must distinguish ---------------------------------------


def test_errors_carry_the_engine_codes(graph, mock):
    cases = [
        (lambda: graph.get_problem("fixture:nope"), "PROBLEM_NOT_FOUND"),
        (lambda: graph.list_problems(limit=0), "VALIDATION_ERROR"),
        (lambda: graph.list_problems(limit=101), "VALIDATION_ERROR"),
        (lambda: graph.list_opportunities(offset=-1), "VALIDATION_ERROR"),
        (lambda: graph.get_evidence_text(["gong:call-5530"]), "VALIDATION_ERROR"),
        (lambda: graph.get_evidence_text("no-colon"), "VALIDATION_ERROR"),
        (lambda: graph.get_evidence_text("gong:not-held"), "EVIDENCE_TEXT_UNAVAILABLE"),
        (lambda: graph.get_evidence_text("zendesk:tkt-88417"), "EVIDENCE_TEXT_UNAVAILABLE"),
        (lambda: graph.get_evidence_text("reops:int-0412"), "EVIDENCE_TEXT_UNAVAILABLE"),
    ]
    for call, code in cases:
        with pytest.raises(mock.ToolFailure) as caught:
            call()
        assert caught.value.code == code


def test_links_can_be_unconfigured_without_meaning_not_promoted(graph, mock, monkeypatch):
    monkeypatch.setenv("MOCK_PDG_LINKS", "off")
    with pytest.raises(mock.ToolFailure) as caught:
        graph.get_work_item_links(TRIAGE)
    assert caught.value.code == "LINKS_UNAVAILABLE"


def test_unconfigured_evidence_text_is_not_advertised_at_all(mock, monkeypatch):
    names = {t["name"] for t in mock.advertised_tools()}
    assert len(names) == 7
    monkeypatch.setenv("MOCK_PDG_EVIDENCE_TEXT", "off")
    names = {t["name"] for t in mock.advertised_tools()}
    assert "get_evidence_text" not in names and len(names) == 6


# --- containment -------------------------------------------------------------


def test_nothing_served_can_pass_for_real_evidence(graph):
    for row in graph.list_problems(limit=100)["items"]:
        assert row["problem_id"].startswith("fixture:")
        assert row["title"].startswith("[SYNTHETIC]")
    fixture = json.loads(FIXTURE.read_text())
    for problem in fixture["problems"]:
        for row in problem["evidence"]:
            if row.get("record_url"):
                assert row["record_url"].startswith("https://fixture.invalid/")
            if row.get("excerpt"):
                assert "[SYNTHETIC]" in row["excerpt"]["text"]
        for link in problem.get("links", []):
            assert link["record_url"].startswith("https://fixture.invalid/")


def test_documentation_keys_are_never_served(graph):
    payloads = [graph.list_problems(limit=100), graph.list_opportunities(limit=100)]
    payloads += [graph.get_problem(pid) for pid in all_problem_ids(graph)]
    assert "_case" not in json.dumps(payloads)
    assert "excerpt" not in json.dumps([graph.list_evidence(p) for p in all_problem_ids(graph)])


# --- the transport -----------------------------------------------------------


def test_it_speaks_mcp_over_stdio():
    """One real round trip through the process, as a client would drive it."""
    messages = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize",
         "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                    "clientInfo": {"name": "pytest", "version": "0"}}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
         "params": {"name": "get_problem", "arguments": {"problem_id": TRIAGE}}},
        {"jsonrpc": "2.0", "id": 4, "method": "tools/call",
         "params": {"name": "get_problem", "arguments": {"problem_id": "fixture:nope"}}},
    ]
    stdin = "\n".join(json.dumps(m) for m in messages) + "\n"
    run = subprocess.run([sys.executable, str(SERVER)], input=stdin, capture_output=True,
                         text=True, timeout=30, cwd="/")
    replies = {r["id"]: r for r in map(json.loads, run.stdout.splitlines())}
    assert set(replies) == {1, 2, 3, 4}, "a notification must never be answered"
    assert replies[1]["result"]["serverInfo"]["name"] == "opportunity-engine-mock"
    assert len(replies[2]["result"]["tools"]) == 7
    found = replies[3]["result"]
    assert found["isError"] is False
    assert json.loads(found["content"][0]["text"]) == found["structuredContent"]
    assert set(found["structuredContent"]) == PROBLEM_DETAIL
    missing = replies[4]["result"]
    assert missing["isError"] is True
    assert missing["content"][0]["text"].startswith("PROBLEM_NOT_FOUND: ")


def test_every_evidence_text_disclosure_is_logged_including_refusals(graph, mock, monkeypatch, tmp_path):
    """The engine access-logs each read; evals use the mock's log to check a skill fetched only
    the excerpts a panel needed."""
    log = tmp_path / "access.jsonl"
    monkeypatch.setenv("MOCK_PDG_ACCESS_LOG", str(log))
    graph.get_evidence_text("gong:call-5530", problem_id=TRIAGE)
    with pytest.raises(mock.ToolFailure):
        graph.get_evidence_text("reops:int-0412", problem_id=TRIAGE)
    entries = [json.loads(line) for line in log.read_text().splitlines()]
    assert [(e["provenance_reference"], e["returned"], e["code"]) for e in entries] == [
        ("gong:call-5530", True, None), ("reops:int-0412", False, "EVIDENCE_TEXT_UNAVAILABLE")]
    assert graph.list_evidence(TRIAGE) and len(log.read_text().splitlines()) == 2, \
        "only evidence text is logged"
