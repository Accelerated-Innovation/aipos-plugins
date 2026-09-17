"""Workflow references resolve to canonical behavior, or say why they cannot.

A workflow holds no behavior of its own. Every behavioral claim in it is a
reference into the Gherkin corpus, so a Rule shown at four steps is authored
once and referenced four times. These tests assert that property and the ways
it can fail — they do not assert how any skill words its instructions.

Increment 02 of the AIPOS behavior-contract plan
(docs/plans/2026-09-17-aipos-behavior-contract.md).
"""

import copy
import json

import pytest


@pytest.fixture(scope="session")
def workflow(workflows):
    return json.loads((workflows / "invoice-approval.workflow.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def resolved(workflow_resolve, workflow, features):
    return workflow_resolve.resolve(workflow, features)


def errors(result):
    return [d for d in result["diagnostics"] if d["level"] == "error"]


def codes(result):
    return {d["code"] for d in result["diagnostics"]}


def behavior_of(result, activity_id):
    act = next(a for a in result["views"]["l3"]["activities"] if a["id"] == activity_id)
    return act["behavior"]


# ------------------------------------------------------------------ the happy path

def test_the_reference_corpus_resolves_cleanly(resolved):
    assert errors(resolved) == []
    assert resolved["ok"] is True


# ------------------------------------------------------------------ distinct resolution

def test_the_same_local_slug_in_two_features_resolves_to_two_different_rules(resolved):
    """`@rule:invoice-approval-threshold` is authored in both inv_full and
    inv_partner. Each is unique *within its own file*, which is all the
    authoring standard requires — so the feature-key segment is the only thing
    that can tell them apart, and it must."""
    standard = [b for b in behavior_of(resolved, "approve") if b["kind"] == "rule"]
    partner = [b for b in behavior_of(resolved, "partner-approve") if b["kind"] == "rule"]

    assert len(standard) == 1 and len(partner) == 1
    assert standard[0]["slug"] == partner[0]["slug"] == "invoice-approval-threshold"
    assert standard[0]["featureKey"] != partner[0]["featureKey"]
    assert "finance manager" in standard[0]["name"]
    assert "partner-manager" in partner[0]["name"]


def test_an_unqualified_reference_is_refused_rather_than_guessed(workflow_resolve, features,
                                                                 workflow):
    """Without a feature key there is no way to choose between the two
    `invoice-approval-threshold` rules, and picking one would make the
    reference mean something nobody wrote."""
    wf = copy.deepcopy(workflow)
    wf["activities"][2]["behavior"] = ["inv_full#rule:invoice-approval-threshold"]

    result = workflow_resolve.resolve(wf, features)

    assert "malformed-ref" in codes(result)
    assert result["ok"] is False


# ------------------------------------------------------------------ reuse without duplication

def test_one_rule_referenced_from_several_places_is_authored_once(resolved, features):
    """The reuse property the whole format exists for: three references, one
    Rule in the corpus. If a workflow could carry its own copy, rewording the
    Rule would leave stale duplicates behind."""
    ref = "acme/FEATURE-inv_full#rule:invoice-approval-threshold"
    users = resolved["views"]["l3"]["referencedBy"][ref]

    assert sorted(users) == ["approve", "route", "route.evaluate-threshold"]

    inv_full = next(f for f in features if f["key"] == "FEATURE-inv_full")
    matching = [r for r in inv_full["rules"] if r["id"] == "invoice-approval-threshold"]
    assert len(matching) == 1


# ------------------------------------------------------------------ diagnostics locate themselves

def test_a_dangling_reference_names_the_activity_and_the_element(workflow_resolve, features,
                                                                 workflow):
    wf = copy.deepcopy(workflow)
    wf["activities"][2]["behavior"] = ["acme/FEATURE-inv_full#rule:no-such-rule"]

    result = workflow_resolve.resolve(wf, features)
    dangling = next(d for d in result["diagnostics"] if d["code"] == "dangling-ref")

    assert dangling["activity"] == "approve"
    assert dangling["element"] == "no-such-rule"
    assert dangling["file"]
    assert result["ok"] is False


def test_a_reference_to_a_missing_feature_names_the_feature(workflow_resolve, features, workflow):
    wf = copy.deepcopy(workflow)
    wf["activities"][2]["behavior"] = ["acme/FEATURE-not-here#rule:whatever"]

    result = workflow_resolve.resolve(wf, features)
    dangling = next(d for d in result["diagnostics"] if d["code"] == "dangling-ref")

    assert dangling["element"] == "FEATURE-not-here"
    assert dangling["activity"] == "approve"


def test_a_retired_identifier_dangles_rather_than_being_followed(workflow_resolve, features,
                                                                 workflow):
    """A retired slug is never reused, so a stale reference cannot silently
    land on whatever replaced it. Dangling is the intended outcome: repointing
    it is a decision about where the behavior now lives, not a lookup."""
    wf = copy.deepcopy(workflow)
    wf["activities"][2]["behavior"] = ["acme/FEATURE-inv_full#rule:invoices-of-10000-or-more"]

    result = workflow_resolve.resolve(wf, features)

    assert "dangling-ref" in codes(result)
    assert result["ok"] is False


def test_a_duplicate_slug_inside_one_feature_is_ambiguous_not_first_wins(workflow_resolve,
                                                                        features, workflow):
    """Resolving to whichever was ingested first would be silently wrong half
    the time."""
    corrupted = copy.deepcopy(features)
    inv_full = next(f for f in corrupted if f["key"] == "FEATURE-inv_full")
    clone = copy.deepcopy(inv_full["rules"][0])
    clone["rule"] = "A different rule wearing the same slug"
    inv_full["rules"].append(clone)

    result = workflow_resolve.resolve(workflow, corrupted)

    assert "duplicate-slug" in codes(result)
    assert "ambiguous-ref" in codes(result)
    assert result["ok"] is False


def test_two_features_claiming_one_key_make_every_reference_through_it_ambiguous(
        workflow_resolve, features, workflow):
    corrupted = copy.deepcopy(features)
    shadow = copy.deepcopy(next(f for f in corrupted if f["key"] == "FEATURE-inv_partner"))
    shadow["key"] = "FEATURE-inv_full"
    corrupted.append(shadow)

    result = workflow_resolve.resolve(workflow, corrupted)

    assert "duplicate-feature-key" in codes(result)
    assert result["ok"] is False


# ------------------------------------------------------------------ broken Gherkin

def test_broken_gherkin_stays_a_parse_error_and_never_an_empty_success(workflow_resolve,
                                                                      features, workflow):
    """The corpus fixture `broken_syntax` parses to zero rules. A reference
    into it must report the parse failure — reporting 'not found' would send
    someone to fix the reference instead of the spec, and reporting nothing at
    all would let a broken spec pass as an empty one."""
    wf = copy.deepcopy(workflow)
    wf["activities"][2]["behavior"] = ["acme/FEATURE-broken_syntax#rule:anything"]

    result = workflow_resolve.resolve(wf, features)
    diag = next(d for d in result["diagnostics"] if d["code"] == "unparsed-feature")

    assert "Rulez" in diag["message"]
    assert diag["activity"] == "approve"
    assert result["ok"] is False


# ------------------------------------------------------------------ identity migration

def test_a_derived_identifier_resolves_but_cannot_be_approved(workflow_resolve, features,
                                                              workflow):
    """legacy_simple authors no tags, so its ids are slugified from names.
    Readable — the map still renders — but a slug that changes when the name
    does cannot bind an approval, so it warns rather than failing."""
    wf = copy.deepcopy(workflow)
    wf["activities"][2]["behavior"] = [
        "acme/FEATURE-legacy_simple#scenario:export-customer-records-to-csv"
    ]

    result = workflow_resolve.resolve(wf, features)
    warning = next(d for d in result["diagnostics"] if d["code"] == "derived-identity")

    assert warning["level"] == "warning"
    assert result["ok"] is True, "a derived id is un-approvable, not unusable"
    assert behavior_of(result, "approve")[0]["idSource"] == "derived"


# ------------------------------------------------------------------ workflow structure

def test_an_unsupported_version_short_circuits_with_a_named_error(workflow_resolve, features,
                                                                  workflow):
    wf = copy.deepcopy(workflow)
    wf["version"] = 99
    wf["activities"][2]["behavior"] = ["acme/FEATURE-inv_full#rule:no-such-rule"]

    result = workflow_resolve.resolve(wf, features)

    assert codes(result) == {"unsupported-version"}
    assert "99" in result["diagnostics"][0]["message"]


@pytest.mark.parametrize(
    ("mutate", "expected"),
    [
        (lambda wf: wf["activities"][0].update(actor="nobody"), "unknown-actor"),
        (lambda wf: wf["activities"][0]["next"].append({"to": "nowhere"}), "dangling-transition"),
        (lambda wf: wf["activities"].append(copy.deepcopy(wf["activities"][0])),
         "duplicate-activity-id"),
        (lambda wf: wf["activities"][1]["steps"].append(
            copy.deepcopy(wf["activities"][1]["steps"][0])), "duplicate-step-id"),
    ],
)
def test_structural_defects_are_reported(workflow_resolve, features, workflow, mutate, expected):
    wf = copy.deepcopy(workflow)
    mutate(wf)

    assert expected in codes(workflow_resolve.resolve(wf, features))


# ------------------------------------------------------------------ the three views

def test_l1_is_the_customer_journey_with_no_gherkin_in_it(resolved):
    """L1 is the view someone outside the team reads. A Rule slug leaking into
    it is the failure mode."""
    l1 = resolved["views"]["l1"]

    assert l1["outcome"]
    assert [a["id"] for a in l1["activities"]] == [
        "submit", "route", "approve", "partner-approve"]
    assert "behavior" not in json.dumps(l1)
    assert "#rule:" not in json.dumps(l1)


def test_l2_shows_where_work_changes_hands(resolved):
    """Handoffs are where most real defects live, so L2 has to make them
    visible rather than leaving them implied by adjacency."""
    route = next(a for a in resolved["views"]["l2"]["activities"] if a["id"] == "route")
    handoff = route["steps"][0]["handoff"]

    assert handoff == {"from": "submitter", "to": "routing"}
    assert "#rule:" not in json.dumps(resolved["views"]["l2"])


def test_l3_carries_resolved_behavior_with_its_source_location(resolved):
    rule = next(b for b in behavior_of(resolved, "approve") if b["kind"] == "rule")

    assert rule["resolved"] is True
    assert rule["idSource"] == "tag"
    assert rule["file"] and rule["line"]
    assert rule["name"]


def test_workflow_order_is_not_release_scope_and_not_a_build_dependency(resolved):
    """Three separate vocabularies. `next` is the order a customer moves
    through the journey; MVP/V1 tags are a release view; neither is an
    implementation dependency. Conflating them is how a workflow diagram
    quietly becomes a project plan."""
    l1 = resolved["views"]["l1"]
    route = next(a for a in l1["activities"] if a["id"] == "route")

    assert [e["to"] for e in route["next"]] == ["approve", "partner-approve"]
    assert all("mvp" not in json.dumps(a).lower() for a in l1["activities"])

    partner = next(b for b in behavior_of(resolved, "partner-approve") if b["kind"] == "scenario")
    assert "@mvp" in partner["tags"]


# ------------------------------------------------------------------ external references

def test_design_references_are_carried_without_being_invented(resolved):
    """A design state lives outside the Gherkin corpus, so the resolver records
    that it was declared and marks it unresolved rather than fabricating a
    target it cannot see."""
    design = next(a for a in resolved["views"]["l3"]["activities"]
                  if a["id"] == "approve")["design"]

    assert len(design) == 1
    assert design[0]["external"] is True
    assert design[0]["resolved"] is False


# ------------------------------------------------------------------ review regressions

def test_a_reference_into_another_repository_never_binds_to_a_local_feature(
        workflow_resolve, features, workflow):
    """The worst available outcome is a confident `resolved: true` pointing at
    behavior from a different repository. Feature keys are unique per corpus,
    not globally, so two repositories can hold `FEATURE-inv_full` describing
    entirely different products."""
    wf = copy.deepcopy(workflow)
    wf["activities"][2]["behavior"] = [
        "other-repo/FEATURE-inv_full#rule:invoice-approval-threshold"
    ]

    result = workflow_resolve.resolve(wf, features)
    carried = behavior_of(result, "approve")[0]
    warning = next(d for d in result["diagnostics"] if d["code"] == "foreign-source")

    assert carried["resolved"] is False
    assert carried["reason"] == "foreign-source"
    assert carried["source"] == "other-repo"
    assert "name" not in carried, "nothing local may be attached to a foreign reference"
    assert warning["level"] == "warning", "a cross-repo reference is legitimate, not broken"


def test_a_design_reference_needs_no_gherkin_feature(workflow_resolve, features, workflow):
    """A design state lives in a design tool, not the Gherkin corpus. Demanding
    a matching feature would reject every valid design reference."""
    wf = copy.deepcopy(workflow)
    wf["activities"][2]["design"] = ["acme/DESIGN-library#design:approval-panel"]

    result = workflow_resolve.resolve(wf, features)
    design = next(a for a in result["views"]["l3"]["activities"]
                  if a["id"] == "approve")["design"][0]

    assert errors(result) == []
    assert design["external"] is True and design["resolved"] is False
    assert design["reason"] == "non-gherkin-kind"


@pytest.mark.parametrize("bad", [42, ["nested"], {"ref": "x"}, None, True])
def test_a_non_text_reference_is_a_diagnostic_not_a_crash(workflow_resolve, features,
                                                          workflow, bad):
    """Bad data in one entry must not take the whole command down."""
    wf = copy.deepcopy(workflow)
    wf["activities"][2]["behavior"] = [bad]

    result = workflow_resolve.resolve(wf, features)

    assert "malformed-ref" in codes(result)
    assert result["ok"] is False


def test_a_handoff_to_an_undeclared_actor_is_reported(workflow_resolve, features, workflow):
    """A handoff is what L2 exists to show. An unchecked endpoint renders into
    the collaboration view looking exactly as authoritative as a real one."""
    wf = copy.deepcopy(workflow)
    wf["activities"][1]["steps"][0]["handoff"] = {"from": "ghost", "to": "phantom"}

    result = workflow_resolve.resolve(wf, features)
    unknown = [d for d in result["diagnostics"] if d["code"] == "unknown-actor"]

    assert len(unknown) == 2
    assert all(d["step"] == "evaluate-threshold" for d in unknown)
    assert result["ok"] is False


def test_a_broken_sibling_file_does_not_hide_behavior_that_parsed(workflow_resolve, features,
                                                                  workflow):
    """repo_ingest merges every .feature in a directory into one record. One
    unparseable sibling must not suppress rules that ingested perfectly well
    from another file — that reports N symptoms and hides the behavior the
    reader came for."""
    corpus = copy.deepcopy(features)
    inv_full = next(f for f in corpus if f["key"] == "FEATURE-inv_full")
    inv_full["parseErrors"] = [
        {"file": "zz_broken.feature", "line": 6, "message": "got 'Rulez: not a keyword'"}
    ]

    result = workflow_resolve.resolve(workflow, corpus)
    rule = next(b for b in behavior_of(result, "approve") if b["kind"] == "rule")

    assert rule["resolved"] is True
    assert rule["file"] == "acceptance.feature"


def test_a_missing_slug_in_a_feature_with_parse_errors_names_the_parse_failure(
        workflow_resolve, features, workflow):
    """When the slug genuinely is not there and a sibling failed to parse, the
    likely cause is that it lives in the broken file. Saying 'not found' would
    send someone to fix the reference instead of the spec."""
    corpus = copy.deepcopy(features)
    inv_full = next(f for f in corpus if f["key"] == "FEATURE-inv_full")
    inv_full["parseErrors"] = [{"file": "zz_broken.feature", "message": "got 'Rulez'"}]
    wf = copy.deepcopy(workflow)
    wf["activities"][2]["behavior"] = ["acme/FEATURE-inv_full#rule:lives-in-the-broken-file"]

    result = workflow_resolve.resolve(wf, corpus)
    diag = next(d for d in result["diagnostics"] if d["code"] == "unparsed-feature")

    assert "Rulez" in diag["message"]
    assert "may be in the file that failed" in diag["message"]


# ------------------------------------------------------------------ coverage

def test_coverage_reports_behavior_no_step_touches(resolved):
    """The finding no diagram gives you. An unreferenced scenario is behavior
    the map implies does not exist, and nobody notices unless it is named."""
    cover = resolved["coverage"]
    uncovered = {(u["kind"], u["slug"]) for u in cover["uncovered"]}

    assert ("scenario", "partner-manager-unavailable") in uncovered
    assert ("rule", "configurable-thresholds") in uncovered
    assert ("rule", "invoice-approval-threshold") not in uncovered


def test_uncovered_behavior_is_a_warning_not_an_error(resolved):
    """A Rule may legitimately belong to a journey this workflow does not
    describe. Failing the run would make the honest answer indistinguishable
    from a broken one."""
    uncovered = [d for d in resolved["diagnostics"] if d["code"] == "uncovered-behavior"]

    assert uncovered
    assert all(d["level"] == "warning" for d in uncovered)
    assert resolved["ok"] is True


def test_covered_and_uncovered_together_account_for_the_parsed_corpus(resolved, features):
    """A coverage report that quietly drops elements would understate the gap,
    which is the one direction that matters."""
    cover = resolved["coverage"]
    total = sum(
        1 + len(r.get("scenarios") or [])
        for f in features if not f.get("parseErrors")
        for r in f.get("rules") or []
        if r.get("id")
    )

    assert len(cover["covered"]) + len(cover["uncovered"]) == total


def test_an_unparsed_feature_is_left_out_of_coverage(resolved):
    """Its elements did not parse, so "uncovered" would be meaningless — the
    parse failure is reported on its own."""
    every = resolved["coverage"]["covered"] + resolved["coverage"]["uncovered"]

    assert not [e for e in every if e["featureKey"] == "FEATURE-broken_syntax"]


def test_coverage_distinguishes_a_reference_with_no_corpus_element(workflow_resolve, features,
                                                                   workflow):
    """A dangling reference is not coverage — it is the opposite, and folding
    it into `covered` would make a broken map look complete."""
    wf = copy.deepcopy(workflow)
    wf["activities"][2]["behavior"] = ["acme/FEATURE-inv_full#rule:no-such-rule"]

    result = workflow_resolve.resolve(wf, features)

    assert "acme/FEATURE-inv_full#rule:no-such-rule" in result["coverage"]["referencedNotInCorpus"]
    assert not any(c["slug"] == "no-such-rule" for c in result["coverage"]["covered"])
