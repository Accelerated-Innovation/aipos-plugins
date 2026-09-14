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
