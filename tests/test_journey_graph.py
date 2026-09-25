"""The journey graph answers two questions, and every fact behind them is computed here.

  1. Which scenarios specify this journey?
  2. Which journeys are affected if this feature changes?

The viewer only lays the graph out. These tests pin what the graph says, so the
diagram cannot drift from the resolver or from the fallback tables. They assert
behavior, never the wording of a skill.
"""

import copy
import json

import pytest

INV_FULL = "f:acme/FEATURE-inv_full"
INV_PARTNER = "f:acme/FEATURE-inv_partner"
ROUTING_BY_AMOUNT = "acme/FEATURE-inv_full#scenario:approval-routing-by-amount"
MANAGER_REJECTS = "acme/FEATURE-inv_full#scenario:manager-rejects-with-reason"
PARTNER_REQUIRED = "acme/FEATURE-inv_partner#scenario:partner-approval-required"
PARTNER_AWAY = "acme/FEATURE-inv_partner#scenario:partner-manager-unavailable"
FULL_THRESHOLD = "acme/FEATURE-inv_full#rule:invoice-approval-threshold"
CONFIGURABLE = "acme/FEATURE-inv_full#rule:configurable-thresholds"


def _load_workflow(workflows, name):
    return json.loads((workflows / f"{name}.workflow.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def invoice(workflows):
    return _load_workflow(workflows, "invoice-approval")


@pytest.fixture(scope="session")
def setup(workflows):
    return _load_workflow(workflows, "threshold-setup")


@pytest.fixture(scope="session")
def graph(journey_graph, workflow_resolve, features, invoice, setup):
    return journey_graph.build(features, [workflow_resolve.resolve(invoice, features),
                                          workflow_resolve.resolve(setup, features)])


@pytest.fixture(scope="session")
def single(journey_graph, workflow_resolve, features, invoice):
    return journey_graph.build(features, [workflow_resolve.resolve(invoice, features)])


def node(graph, nid):
    matches = [n for n in graph["nodes"] if n["id"] == nid]
    assert len(matches) == 1, f"{nid!r} appears {len(matches)} times"
    return matches[0]


def edges(graph, kind, **match):
    return [e for e in graph["edges"]
            if e["kind"] == kind and all(e.get(k) == v for k, v in match.items())]


# ------------------------------------------------------------------ question 2

def test_a_feature_shared_by_two_journeys_is_one_node_with_an_edge_from_each(graph):
    node(graph, INV_FULL)  # exactly once
    users = {e["source"] for e in edges(graph, "uses", target=INV_FULL)}
    assert users == {"j:invoice-approval/a:route", "j:invoice-approval/a:approve",
                     "j:threshold-setup/a:set-threshold",
                     "j:threshold-setup/a:confirm-routing"}


def test_changing_a_feature_names_every_journey_it_affects(graph):
    by_feature = graph["index"]["journeysByFeature"]
    assert by_feature[INV_FULL] == ["invoice-approval", "threshold-setup"]
    assert by_feature[INV_PARTNER] == ["invoice-approval"]
    assert by_feature["f:acme/FEATURE-legacy_simple"] == []


def test_the_affected_activities_are_named_not_just_the_journeys(graph):
    assert graph["index"]["activitiesByFeature"][INV_PARTNER] == [
        "j:invoice-approval/a:partner-approve"]


def test_step_level_references_count_toward_their_activity(journey_graph, workflow_resolve,
                                                           features, invoice):
    """A Rule referenced only from a step still means the activity uses its feature."""
    wf = copy.deepcopy(invoice)
    route = next(a for a in wf["activities"] if a["id"] == "route")
    route["behavior"] = []
    g = journey_graph.build(features, [workflow_resolve.resolve(wf, features)])
    via = edges(g, "uses", source="j:invoice-approval/a:route", target=INV_FULL)
    assert len(via) == 1
    assert via[0]["via"] == [{"ref": FULL_THRESHOLD, "step": "evaluate-threshold"}]


# ------------------------------------------------------------------ question 1

def test_the_scenarios_that_specify_a_journey_are_the_ones_it_references(graph):
    got = graph["index"]["scenariosByJourney"]["invoice-approval"]
    assert got["referenced"] == sorted([ROUTING_BY_AMOUNT, MANAGER_REJECTS, PARTNER_REQUIRED])


def test_referencing_a_rule_does_not_place_the_scenarios_beneath_it(graph):
    """invoice-approval names the partner Rule and one of its two scenarios. The
    other scenario is reported separately, never counted as specifying the journey."""
    got = graph["index"]["scenariosByJourney"]["invoice-approval"]
    assert PARTNER_AWAY not in got["referenced"]
    assert got["underReferencedRule"] == [PARTNER_AWAY]
    assert node(graph, PARTNER_AWAY)["placement"] == "under-referenced-rule"


def test_each_journey_gets_its_own_answer(graph):
    got = graph["index"]["scenariosByJourney"]["threshold-setup"]
    assert got["referenced"] == [ROUTING_BY_AMOUNT]
    assert got["underReferencedRule"] == []  # configurable-thresholds has no scenarios


def test_a_scenario_records_every_place_that_references_it(graph):
    refs = node(graph, ROUTING_BY_AMOUNT)["refs"]
    assert {(r["journey"], r["activity"]) for r in refs} == {
        ("invoice-approval", "route"), ("threshold-setup", "confirm-routing")}


# ------------------------------------------------------------------ coverage

def test_uncovered_matches_the_resolver_for_a_single_journey(single, workflow_resolve,
                                                             features, invoice):
    resolved = workflow_resolve.resolve(invoice, features)
    assert set(single["uncovered"]) == {u["ref"] for u in resolved["coverage"]["uncovered"]}


def test_uncovered_across_journeys_is_what_no_journey_references(graph, single):
    """configurable-thresholds is uncovered by invoice-approval alone but covered
    once threshold-setup is on the page. The page-wide finding is the union."""
    assert CONFIGURABLE in single["uncovered"]
    assert CONFIGURABLE not in graph["uncovered"]
    assert node(graph, CONFIGURABLE)["placement"] == "referenced"


def test_each_journey_keeps_its_own_coverage_counts(graph, workflow_resolve, features, setup):
    own = workflow_resolve.resolve(setup, features)["coverage"]
    j = next(j for j in graph["journeys"] if j["id"] == "threshold-setup")
    assert j["coverage"]["covered"] == len(own["covered"])
    assert j["coverage"]["uncovered"] == len(own["uncovered"])


def test_every_corpus_scenario_is_on_the_graph_even_when_no_journey_uses_it(graph, features):
    ids = {n["id"] for n in graph["nodes"] if n["kind"] == "scenario"}
    for f in features:
        for r in f.get("rules") or []:
            for s in r.get("scenarios") or []:
                if s.get("id"):
                    assert f"acme/{f['key']}#scenario:{s['id']}" in ids


# ------------------------------------------------------------------ L1

def test_activities_keep_customer_order_and_branch_conditions(graph):
    nxt = edges(graph, "next", source="j:invoice-approval/a:route")
    assert {(e["target"], e["condition"]) for e in nxt} == {
        ("j:invoice-approval/a:approve", "standard invoice"),
        ("j:invoice-approval/a:partner-approve", "partner invoice")}


def test_a_journey_starts_at_the_activities_nothing_leads_to(graph):
    assert [e["target"] for e in edges(graph, "starts", source="j:invoice-approval")] == [
        "j:invoice-approval/a:submit"]


def test_handoffs_come_only_from_what_steps_record(graph):
    """submit -> route changes actor, but no step there records a handoff, so
    none is drawn. The one recorded on evaluate-threshold is."""
    assert node(graph, "j:invoice-approval/a:submit")["handoffs"] == []
    assert node(graph, "j:invoice-approval/a:route")["handoffs"] == [
        {"step": "evaluate-threshold", "stepName": "Evaluate the approval threshold",
         "from": "submitter", "to": "routing"}]


def test_activities_carry_their_actor(graph):
    assert node(graph, "j:invoice-approval/a:route")["actor"] == {
        "id": "routing", "name": "Routing service", "kind": "system"}


def test_a_transition_to_nowhere_stays_visible(journey_graph, workflow_resolve, features,
                                               invoice):
    wf = copy.deepcopy(invoice)
    wf["activities"][0]["next"] = [{"to": "vanished"}]
    g = journey_graph.build(features, [workflow_resolve.resolve(wf, features)])
    e = edges(g, "next", source="j:invoice-approval/a:submit")
    assert e[0]["dangling"] is True
    assert node(g, e[0]["target"])["kind"] == "missing"


# ------------------------------------------------------------------ unresolved

def test_a_design_reference_is_an_unresolved_node_not_a_feature(graph):
    n = node(graph, "x:acme/FEATURE-inv_full#design:approval-panel")
    assert n["kind"] == "unresolved" and n["reason"] == "non-gherkin-kind"
    assert edges(graph, "unresolved", source="j:invoice-approval/a:approve",
                 target=n["id"])


def test_a_dangling_reference_is_drawn_where_it_was_written(journey_graph, workflow_resolve,
                                                            features, invoice):
    """The resolver drops a dangling reference from its views and reports it as a
    diagnostic. The graph puts it back, as an unresolved node on its activity."""
    wf = copy.deepcopy(invoice)
    wf["activities"][2]["behavior"].append("acme/FEATURE-inv_full#rule:retired-rule")
    g = journey_graph.build(features, [workflow_resolve.resolve(wf, features)])
    n = node(g, "x:acme/FEATURE-inv_full#rule:retired-rule")
    assert n["reason"] == "dangling-ref"
    assert edges(g, "unresolved", source="j:invoice-approval/a:approve", target=n["id"])
    assert "acme/FEATURE-inv_full#rule:retired-rule" not in {
        x["id"] for x in g["nodes"] if x["kind"] == "rule"}


def test_a_foreign_reference_never_binds_to_a_local_feature(journey_graph, workflow_resolve,
                                                            features, invoice):
    wf = copy.deepcopy(invoice)
    wf["activities"][2]["behavior"] = ["globex/FEATURE-inv_full#rule:invoice-approval-threshold"]
    g = journey_graph.build(features, [workflow_resolve.resolve(wf, features)])
    assert node(g, "x:globex/FEATURE-inv_full#rule:invoice-approval-threshold")[
        "reason"] == "foreign-source"
    assert not edges(g, "uses", source="j:invoice-approval/a:approve")


# ------------------------------------------------------------------ L3 detail

def test_a_scenario_carries_what_its_detail_panel_shows(graph):
    sc = node(graph, MANAGER_REJECTS)
    assert [s["keyword"] for s in sc["steps"]] == ["Given", "When", "Then", "And"]
    assert sc["steps"][0]["dataTable"][0] == ["invoice", "amount", "vendor"]
    assert "Duplicate of INV-2118" in sc["steps"][1]["docString"]["content"]
    assert [b["text"] for b in sc["background"]] == ["the finance period is open",
                                                     "a finance manager is on duty"]
    assert sc["source"]["path"].endswith("inv_full/acceptance.feature")
    assert "href" not in sc["source"]


def test_examples_travel_with_an_outline(graph):
    sc = node(graph, ROUTING_BY_AMOUNT)
    assert sc["examples"][0]["header"] == ["amount", "status", "approver"]
    assert len(sc["examples"][0]["rows"]) == 3


def test_a_source_link_is_written_only_when_a_base_url_is_given(
        journey_graph, workflow_resolve, features, invoice):
    g = journey_graph.build(features, [workflow_resolve.resolve(invoice, features)],
                            base_url="https://example.test/acme/blob/abc123/")
    src = node(g, MANAGER_REJECTS)["source"]
    assert src["href"] == f"https://example.test/acme/blob/abc123/{src['path']}#L{src['line']}"


# ------------------------------------------------------------------ refusals

def test_two_journeys_with_one_key_are_refused_not_merged(journey_graph, workflow_resolve,
                                                          features, invoice):
    r = workflow_resolve.resolve(invoice, features)
    with pytest.raises(journey_graph.JourneyGraphError, match="invoice-approval"):
        journey_graph.build(features, [r, r])


def test_journeys_resolved_against_different_sources_are_refused(
        journey_graph, workflow_resolve, features, invoice):
    other = copy.deepcopy(invoice)
    other["workflow_key"], other["source_key"] = "elsewhere", "globex"
    with pytest.raises(journey_graph.JourneyGraphError, match="different sources"):
        journey_graph.build(features, [workflow_resolve.resolve(invoice, features),
                                       workflow_resolve.resolve(other, features)])


def test_an_unsupported_workflow_is_a_journey_with_errors_not_a_crash(
        journey_graph, workflow_resolve, features, invoice):
    wf = copy.deepcopy(invoice)
    wf["version"] = 99
    g = journey_graph.build(features, [workflow_resolve.resolve(wf, features)])
    j = g["journeys"][0]
    assert j["ok"] is False and j["errors"] == 1
    assert not [n for n in g["nodes"] if n["kind"] == "activity"]


def test_the_graph_is_json_serialisable(graph):
    assert json.loads(json.dumps(graph)) == graph
