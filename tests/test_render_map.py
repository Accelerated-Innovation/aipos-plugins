"""The information ingestion preserves has to actually reach a reviewer.

A parser that keeps Examples tables and a renderer that drops them is the same defect
with an extra step, so these tests assert against the rendered HTML.
"""

import re


def html(render_map, feats):
    return render_map.render(feats, {}, {}, {})


def strip_tags(s):
    return re.sub(r"<[^>]+>", " ", s)


def test_feature_and_rule_backgrounds_render_with_their_scope_named(render_map, ingested):
    out = html(render_map, [ingested["inv_full"]])
    assert "Feature background" in out
    assert "Rule background" in out
    text = strip_tags(out)
    assert "the finance period is open" in text
    assert "a finance manager is on duty" in text


def test_examples_table_values_render(render_map, ingested):
    text = strip_tags(html(render_map, [ingested["inv_full"]]))
    for cell in ("$9,999.99", "$10,000.00", "$12,500.00", "Pending manager approval"):
        assert cell in text, cell
    assert "Around the manager-approval threshold" in text


def test_step_data_table_and_doc_string_render(render_map, ingested):
    text = strip_tags(html(render_map, [ingested["inv_full"]]))
    assert "Northwind Ltd" in text
    assert "Duplicate of INV-2118" in text


def test_outline_is_badged_and_example_count_is_shown(render_map, ingested):
    out = html(render_map, [ingested["inv_full"]])
    assert "st-outline" in out
    text = strip_tags(out)
    assert "2 scenarios" in " ".join(text.split())
    assert "4 examples" in " ".join(text.split())


def test_inherited_slice_tag_reaches_the_scenario_chip(render_map, ingested):
    out = html(render_map, [ingested["inv_full"]])
    # The rejection scenario carries no slice tag of its own; the Feature declares @v1.
    assert 'data-slice="v1"' in out
    assert 'data-slice="mvp"' in out
    # The release-slice filter bar appears because slices are present.
    assert "Release slice" in out or "fltbar" in out


def test_parse_errors_render_as_a_diagnostic_not_an_empty_spec(render_map, ingested):
    out = html(render_map, [ingested["broken_syntax"]])
    assert "did not parse" in strip_tags(out)
    assert "acceptance.feature" in out
    assert ":6" in out


def test_a_plain_feature_still_renders_its_steps(render_map, ingested):
    """No structured detail, no outlines, no backgrounds -- the existing common case."""
    out = html(render_map, [ingested["legacy_simple"]])
    text = " ".join(strip_tags(out).split())
    assert "Export customer records to CSV" in text
    assert "Given I am on the customer list page" in text
    assert "(no Rule declared)" in text
    assert "2 scenarios" in text
    # No example count is shown when it would just repeat the scenario count.
    assert "2 examples" not in text


FILE_A = """Feature: Part A
  Background:
    Given the setup for part A
  Rule: Rule A
    Scenario: Scenario A
      When A happens
      Then A worked
"""

FILE_B = """Feature: Part B
  Background:
    Given the setup for part B
  Rule: Rule B
    Scenario: Scenario B
      When B happens
      Then B worked
"""


def test_each_file_background_precedes_its_own_rules(render_map, repo_ingest, tmp_path):
    """Two .feature files in one package each have their own Background. The card must
    show each one ahead of that file's rules, not the first one above everything."""
    d = tmp_path / "split_pkg"
    d.mkdir()
    (d / "a.feature").write_text(FILE_A)
    (d / "b.feature").write_text(FILE_B)
    feat = repo_ingest.ingest_dir(str(d), "dir", "")
    assert len(feat["backgrounds"]) == 2
    text = " ".join(strip_tags(html(render_map, [feat])).split())
    order = [text.index(s) for s in
             ("setup for part A", "Scenario A", "setup for part B", "Scenario B")]
    assert order == sorted(order), text
    assert "Feature background · a.feature" in text
    assert "Feature background · b.feature" in text


# ------------------------------------------------------------------ workflow views (05B)

import copy  # noqa: E402
import importlib.util  # noqa: E402
import json  # noqa: E402
import pathlib  # noqa: E402
import re  # noqa: E402
import sys  # noqa: E402

import pytest  # noqa: E402

from skill_paths import skill_path

_SCRIPTS = skill_path("aipos-map-render") / "scripts"


@pytest.fixture(scope="module")
def _resolver():
    spec = importlib.util.spec_from_file_location("wfres", _SCRIPTS / "workflow_resolve.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["wfres"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def resolved_workflow(_resolver, repo_ingest, corpus, workflows):
    feats = repo_ingest.walk(str(corpus), "dir", "")
    wf = json.loads((workflows / "invoice-approval.workflow.json").read_text(encoding="utf-8"))
    return _resolver.resolve(wf, feats), feats


@pytest.fixture(scope="module")
def page(render_map, resolved_workflow):
    resolved, feats = resolved_workflow
    return render_map.render(feats, {}, {}, {}, resolved)


def _journey(page):
    return page.split('id="workflow"', 1)[1]


def test_all_three_views_render(page):
    for label in ("L1 &#8212; customer journey",
                  "L2 &#8212; who collaborates",
                  "L3 &#8212; the behavior that governs each step"):
        assert label in page


def test_l1_contains_no_gherkin_identifiers(page):
    """L1 is the view someone outside the team reads. A rule slug leaking into
    it is the failure mode."""
    l1 = _journey(page).split("L2 &#8212;")[0]

    assert "rule:" not in l1
    assert "scenario:" not in l1
    assert "Submit the invoice" in l1


def test_a_rule_at_several_steps_is_shown_as_reuse_elsewhere(page):
    """Authored once, referenced three times. Each row lists the OTHER
    locations — a row that names its own location turns one reference into
    apparent duplication, which is the opposite of what the column is for."""
    journey = _journey(page)

    # the `approve` activity row cites the other two locations, not itself
    assert "route, route.evaluate-threshold" in journey
    assert "route, route.evaluate-threshold, approve" not in journey


def test_a_row_never_cites_its_own_location_as_reuse(_resolver, render_map, resolved_workflow):
    """Matching on the resolver's location key, not a display name. The
    earlier version compared a step's name against `activity.step` paths, so
    every step row kept itself and every activity row kept everything."""
    resolved, feats = resolved_workflow
    ref = "acme/FEATURE-inv_full#rule:invoice-approval-threshold"
    locations = resolved["views"]["l3"]["referencedBy"][ref]
    assert set(locations) == {"route", "route.evaluate-threshold", "approve"}

    journey = _journey(render_map.render(feats, {}, {}, {}, resolved))
    cells = re.findall(r"<td>([^<]*)</td></tr>", journey)

    for cell in cells:
        cited = {c.strip() for c in cell.split(",") if c.strip() in locations}
        assert len(cited) < len(locations), f"row cites every location incl. its own: {cell!r}"


def test_l2_renders_actor_names_and_kinds_not_raw_ids(page):
    """L2 is the "who collaborates" view. Raw ids make it unreadable, and the
    actor catalog has to travel with the view for the renderer to have them."""
    l2 = _journey(page).split("L2 &#8212;")[1].split("L3 &#8212;")[0]

    assert "Invoice submitter" in l2
    assert "Routing service" in l2
    assert 'class="actor k-human"' in l2
    assert 'class="actor k-system"' in l2


def test_a_transition_to_no_such_activity_is_not_a_link(render_map, resolved_workflow):
    """A fragment with no destination looks navigable and silently does
    nothing; the resolver already calls this dangling."""
    resolved, feats = resolved_workflow
    wf = copy.deepcopy(resolved)
    route = next(a for a in wf["views"]["l1"]["activities"] if a["id"] == "route")
    route["next"] = [{"to": "nowhere", "condition": "never"}]

    journey = _journey(render_map.render(feats, {}, {}, {}, wf))

    assert "no such activity" in journey
    assert 'href="#wfa-nowhere"' not in journey


def test_cross_feature_links_point_at_anchors_that_exist(page):
    """A link into a feature card is only useful if the card is on the page."""
    targets = set(re.findall(r'href="#(FEATURE-[A-Za-z0-9_-]+)"', page))

    assert targets
    for key in targets:
        assert f'id="{key}"' in page, f"link to #{key} has no anchor"


def test_uncovered_behavior_is_shown_with_its_reason(page):
    journey = _journey(page)

    assert "Not touched by this journey" in journey
    assert "partner-manager-unavailable" in journey
    assert "implies does not exist" in journey


def test_the_page_claims_no_approval(page):
    """A local preview cannot verify that any decision was recorded, so it must
    not carry anything a reader could take for one."""
    journey = _journey(page)

    assert "Advisory view" in journey
    assert "nothing here is an approval" in journey
    assert not re.search(r'\b(approved|committed)\b', journey.split("Advisory view")[0])


def test_slice_chips_are_labelled_a_planning_view(page):
    assert "planning view over behavior, not a commitment" in page


def test_interactive_elements_are_native_and_keyboard_operable(page):
    """Every disclosure in the journey is a <details>/<summary>, which is
    focusable and operable with Enter/Space without any script. A div wearing
    role=button would not be."""
    journey = _journey(page)

    assert journey.count("<details") >= 3
    assert 'role="button"' not in page
    assert "tabindex=" not in page


def test_the_journey_reflows_at_narrow_width(page):
    """Tables are the one thing that cannot simply shrink."""
    queries = [page[m.start():m.start() + 400] for m in re.finditer(r"@media", page)]

    assert any("table.wf" in q for q in queries)
    assert 'name="viewport"' in page


def test_an_unresolved_reference_is_not_rendered_as_a_link(render_map, resolved_workflow):
    """A foreign-source or non-Gherkin reference resolves to nothing here.
    Linking it would send a reader to a card that does not exist and imply the
    behavior was verified."""
    resolved, feats = resolved_workflow
    doc = render_map.render(feats, {}, {}, {}, resolved)
    journey = _journey(doc)

    assert "declared outside the Gherkin corpus" in journey
    assert 'href="#acme/FEATURE-inv_full#design:approval-panel"' not in journey


def test_a_branch_without_a_condition_is_called_out(render_map, resolved_workflow, _resolver):
    """A fork nobody has explained is a question, and the view has to ask it
    rather than drawing two arrows and moving on."""
    resolved, feats = resolved_workflow
    wf = copy.deepcopy(resolved)
    route = next(a for a in wf["views"]["l1"]["activities"] if a["id"] == "route")
    route["next"] = [{"to": "approve"}, {"to": "partner-approve"}]

    journey = _journey(render_map.render(feats, {}, {}, {}, wf))

    assert "no stated condition" in journey


@pytest.mark.parametrize(
    "bad", [None, {}, {"views": {}}, {"views": {"l1": {}}, "coverage": {}, "diagnostics": []}],
    ids=["none", "empty", "no-views", "empty-views"],
)
def test_malformed_or_absent_workflow_does_not_break_the_page(render_map, resolved_workflow, bad):
    """The map's existing job must survive a workflow that is missing or
    malformed — the journey is an addition, not a dependency."""
    _resolved, feats = resolved_workflow

    doc = render_map.render(feats, {}, {}, {}, bad)

    assert doc.startswith("<!DOCTYPE html>")
    assert "Artifact ledger" in doc
    if not bad:
        assert 'id="workflow"' not in doc


def test_diagnostics_surface_errors_before_warnings(render_map, resolved_workflow):
    resolved, feats = resolved_workflow
    wf = copy.deepcopy(resolved)
    wf["diagnostics"] = [
        {"level": "warning", "code": "uncovered-behavior", "message": "a warning"},
        {"level": "error", "code": "dangling-ref", "message": "an error"},
    ]

    journey = _journey(render_map.render(feats, {}, {}, {}, wf))

    assert journey.index("an error") < journey.index("a warning")
    assert "1 error, 1 warning" in journey
