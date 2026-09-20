"""Semantic-preservation tests for the repo feature adapter.

These assert what the ingested record *means*, not how any skill words its instructions.
Every one of them fails against the line-scanning parser this replaced.
"""

import json
from skill_paths import skill_path
import subprocess
import sys


def scenarios(feat):
    return [sc for r in feat["rules"] for sc in r["scenarios"]]


def by_name(feat, name):
    return next(sc for sc in scenarios(feat) if sc["name"] == name)


def rule_named(feat, text):
    return next(r for r in feat["rules"] if r["rule"] == text)


# ------------------------------------------------------------------ backgrounds

def test_feature_background_is_preserved_with_its_steps(ingested):
    bg = ingested["inv_full"]["background"]
    assert bg is not None
    assert bg["steps"] == ["Given the finance period is open"]


def test_rule_background_stays_scoped_to_its_own_rule(ingested):
    feat = ingested["inv_full"]
    threshold = rule_named(feat, "Invoices of $10,000 or more require finance manager approval")
    configurable = rule_named(feat, "Approval thresholds are configurable per legal entity")
    assert threshold["background"]["steps"] == ["Given a finance manager is on duty"]
    # A rule background that leaked onto the whole feature would silently add state to
    # scenarios it does not belong to; those then pass for the wrong reason.
    assert configurable["background"] is None
    assert "a finance manager is on duty" not in json.dumps(feat["background"])


# ------------------------------------------------------------------ outlines

def test_outline_is_distinguishable_from_a_plain_scenario(ingested):
    feat = ingested["inv_full"]
    assert by_name(feat, "Invoice amount decides the approval path")["type"] == "scenario_outline"
    assert by_name(feat, "Manager rejects a high-value invoice with a reason")["type"] == "scenario"


def test_examples_values_survive_ingestion(ingested):
    sc = by_name(ingested["inv_full"], "Invoice amount decides the approval path")
    ex = sc["examples"][0]
    assert ex["name"] == "Around the manager-approval threshold"
    assert ex["header"] == ["amount", "status", "approver"]
    amounts = [row[0] for row in ex["rows"]]
    # The exact-threshold row is the one a boundary review exists to find.
    assert amounts == ["$9,999.99", "$10,000.00", "$12,500.00"]
    assert ex["rows"][1][1] == "Pending manager approval"


def test_authored_scenarios_and_executable_examples_are_counted_separately(ingested):
    feat = ingested["inv_full"]
    assert feat["scenarioCount"] == 2          # what a person reviews
    assert feat["exampleCount"] == 4           # 3 outline rows + 1 plain scenario


# ------------------------------------------------------------------ step detail

def test_step_data_table_is_preserved(ingested):
    sc = by_name(ingested["inv_full"], "Manager rejects a high-value invoice with a reason")
    table = next(d["dataTable"] for d in sc["stepDetails"] if "dataTable" in d)
    assert table[0] == ["invoice", "amount", "vendor"]
    assert table[1] == ["INV-2210", "$15,000.00", "Northwind Ltd"]


def test_doc_string_is_preserved(ingested):
    sc = by_name(ingested["inv_full"], "Manager rejects a high-value invoice with a reason")
    doc = next(d["docString"] for d in sc["stepDetails"] if "docString" in d)
    assert "Duplicate of INV-2118" in doc["content"]


def test_flat_step_strings_keep_their_existing_shape(ingested):
    sc = by_name(ingested["inv_full"], "Invoice amount decides the approval path")
    assert sc["steps"][0] == "Given a finance analyst has submitted an invoice for <amount>"
    assert sc["steps"][1].startswith("When ")


def test_source_locations_are_recorded(ingested):
    feat = ingested["inv_full"]
    sc = by_name(feat, "Manager rejects a high-value invoice with a reason")
    assert sc["file"] == "acceptance.feature"
    assert isinstance(sc["line"], int) and sc["line"] > 0
    assert isinstance(rule_named(feat, "Approval thresholds are configurable per legal entity")["line"], int)


# ------------------------------------------------------------------ tags

def test_scenario_own_tags_are_unchanged(ingested):
    """The `tags` field is the existing downstream contract: the scenario's own tags."""
    sc = by_name(ingested["inv_full"], "Invoice amount decides the approval path")
    assert sc["tags"] == ["@mvp", "@functional", "@scenario:approval-routing-by-amount"]


def test_feature_and_rule_tags_are_inherited_into_effective_tags(ingested):
    sc = by_name(ingested["inv_full"], "Manager rejects a high-value invoice with a reason")
    assert sc["tags"] == ["@scenario:manager-rejects-with-reason"]
    # @rule:... from the Rule first (most specific), then @feature and @v1 from the Feature.
    assert sc["inheritedTags"] == ["@rule:invoice-approval-threshold", "@feature", "@v1"]
    assert sc["effectiveTags"][:3] == ["@rule:invoice-approval-threshold", "@feature", "@v1"]
    assert "@scenario:manager-rejects-with-reason" in sc["effectiveTags"]


RULE_OVERRIDES_FEATURE = """@v1
Feature: Slice precedence

  @mvp
  Rule: The first rule ships early
    Scenario: Inherits the rule's slice
      Given a thing
      When it happens
      Then it worked

  Rule: The second rule takes the file default
    Scenario: Inherits the feature's slice
      Given a thing
      When it happens
      Then it worked
"""


def test_a_rule_slice_beats_the_feature_default(repo_ingest, render_map):
    """A slice on the Rule is more specific than one on the Feature, and both the
    inherited order and slice resolution have to agree on that."""
    _, _, rules, _ = repo_ingest.parse_feature_file(RULE_OVERRIDES_FEATURE, "f.feature")
    early, default = rules[0]["scenarios"][0], rules[1]["scenarios"][0]
    assert early["inheritedTags"][0] == "@mvp"
    assert render_map.scen_slice(early) == "mvp"
    assert render_map.scen_slice(default) == "v1"


TAGGED_EXAMPLES = """@v1
Feature: Examples carry their own tags

  @functional
  Scenario Outline: Amount decides the path
    Given an invoice of <amount>
    Then the status is <status>

    @boundary
    Examples: At the threshold
      | amount     | status  |
      | $10,000.00 | Pending |

    @v2
    Examples: Later cases
      | amount     | status   |
      | $1.00      | Approved |
"""


def test_examples_block_tags_get_their_own_effective_tags(repo_ingest):
    """Tags on an Examples: block apply to that block's rows only. They must not leak
    into the scenario's effectiveTags, and each block must report what a --tags run
    would match for its rows."""
    _, _, rules, _ = repo_ingest.parse_feature_file(TAGGED_EXAMPLES, "f.feature")
    sc = rules[0]["scenarios"][0]
    assert "@boundary" not in sc["effectiveTags"] and "@v2" not in sc["effectiveTags"]
    boundary, later = sc["examples"]
    assert boundary["effectiveTags"] == ["@v1", "@functional", "@boundary"]
    assert later["effectiveTags"] == ["@v1", "@functional", "@v2"]


def test_feature_tags_are_reported_on_the_feature(ingested):
    assert ingested["inv_full"]["featureTags"] == ["@feature", "@v1"]


def test_delivery_tag_vocabulary_still_resolves_the_same_way(ingested, render_map):
    """Existing behaviour: an @mvp on the scenario wins; the closed vocabulary is
    unchanged; a slice declared one level up now reaches its scenarios."""
    feat = ingested["inv_full"]
    assert render_map.scen_slice(by_name(feat, "Invoice amount decides the approval path")) == "mvp"
    assert render_map.scen_slice(by_name(feat, "Manager rejects a high-value invoice with a reason")) == "v1"
    # Identifier tags are outside the delivery vocabulary and never resolve as a slice.
    assert render_map.scen_slice({"tags": ["@rule:x", "@scenario:y"]}) == ""
    # Old records with only `tags` keep working.
    assert render_map.scen_slice({"tags": ["@v2", "@edge-case"]}) == "v2"


# ------------------------------------------------------------------ identifiers

def test_authored_identifiers_are_read_from_tags(ingested):
    feat = ingested["inv_full"]
    rule = rule_named(feat, "Invoices of $10,000 or more require finance manager approval")
    assert (rule["id"], rule["idSource"]) == ("invoice-approval-threshold", "tag")
    sc = by_name(feat, "Invoice amount decides the approval path")
    assert (sc["id"], sc["idSource"]) == ("approval-routing-by-amount", "tag")


def test_identifiers_are_derived_when_absent_and_marked_as_such(ingested):
    sc = by_name(ingested["legacy_simple"], "Export customer records to CSV")
    assert sc["idSource"] == "derived"
    assert sc["id"] == "export-customer-records-to-csv"


def test_authored_identifier_survives_a_rename(repo_ingest):
    """Renaming a scenario must not change what evaluations and evidence point at."""
    before = repo_ingest.parse_feature_file(
        'Feature: F\n  @scenario:approval-routing-by-amount\n'
        '  Scenario: Invoice amount decides the approval path\n    Given x\n')
    after = repo_ingest.parse_feature_file(
        'Feature: F\n  @scenario:approval-routing-by-amount @mvp\n'
        '  Scenario: Amount decides which approval path an invoice takes\n    Given x\n')
    a = before[2][0]["scenarios"][0]
    b = after[2][0]["scenarios"][0]
    assert a["name"] != b["name"]
    assert a["id"] == b["id"] == "approval-routing-by-amount"


# ------------------------------------------------------------------ rules

def test_a_declared_rule_with_no_scenarios_is_kept(ingested):
    """The old parser dropped it, so an entirely uncovered rule was invisible to the
    rule-coverage dimension -- the one place it most needed to show up."""
    feat = ingested["inv_full"]
    empty = rule_named(feat, "Approval thresholds are configurable per legal entity")
    assert empty["scenarios"] == []
    assert feat["ruleCount"] == 2


def test_ungrouped_scenarios_land_under_one_unnamed_rule(ingested):
    feat = ingested["legacy_simple"]
    assert feat["ruleCount"] == 1
    assert feat["rules"][0]["rule"] == ""
    assert feat["scenarioCount"] == 2


# ------------------------------------------------------------ existing behaviour

def test_simple_feature_ingestion_is_unchanged(ingested):
    """The pre-existing contract for a plain feature package, field by field."""
    feat = ingested["legacy_simple"]
    assert feat["title"] == "Bulk customer export"
    assert feat["produces"] == ["customer-export-file"]
    assert feat["openQuestions"] == [
        "Which customer fields are included in the export?"]
    assert feat["rules"][0]["scenarios"][0]["steps"] == [
        "Given I am on the customer list page",
        'When I select customers and click "Export"',
        "Then a CSV file downloads with the selected customer records",
    ]
    assert feat["exampleCount"] == feat["scenarioCount"] == 2


def test_nfr_table_with_extra_columns_still_parses(ingested):
    nfr = ingested["inv_full"]["nfr"]
    assert [n["id"] for n in nfr] == ["N1", "N2"]
    assert nfr[0]["threshold"] == "p95 < 2s"
    assert nfr[0]["evidence"] == "Performance test report"


# ------------------------------------------------------------------ diagnostics

def test_invalid_gherkin_yields_diagnostics_not_a_partial_feature(ingested):
    feat = ingested["broken_syntax"]
    assert feat["parseErrors"], "a syntax error must be reported"
    err = feat["parseErrors"][0]
    assert err["file"] == "acceptance.feature"
    assert err["line"] == 6 and err["column"] == 3
    assert "Rulez" in err["message"]
    # The scenario before the error must NOT be reported as if the file were fine.
    assert feat["rules"] == []
    assert feat["scenarioCount"] == 0
    assert "did not parse" in feat["specNote"]


def test_cli_exits_nonzero_and_names_the_source_location(corpus, tmp_path):
    out = tmp_path / "features.json"
    proc = subprocess.run(
        [sys.executable,
         str(skill_path("aipos-feature-map") / "scripts/repo_ingest.py"),
         str(corpus / "broken_syntax"), "-o", str(out)],
        capture_output=True, text=True)
    assert proc.returncode == 3
    assert "acceptance.feature:6:3" in proc.stderr
    # The corpus is still written so one bad spec cannot make the rest unmappable.
    assert json.loads(out.read_text())


# ------------------------------------------------------------------ merge

def test_merge_replaces_tracker_spec_when_the_repo_file_failed_to_parse(repo_ingest, ingested):
    """A failed parse contributes no scenarios. The merged record must say so instead of
    keeping the tracker's stale scenarios next to the parse diagnostic."""
    repo = dict(ingested["broken_syntax"])
    assert repo["parseErrors"] and repo["rules"] == []
    tracker = [{
        "key": repo["key"], "status": "In Delivery", "workstream": "Finance",
        "rules": [{"rule": "Old rule", "scenarios": [{"name": "Stale scenario", "tags": []}]}],
        "ruleCount": 1, "scenarioCount": 1, "exampleCount": 1,
    }]
    merged = repo_ingest.merge(tracker, [repo])[0]
    assert merged["rules"] == [] and merged["scenarioCount"] == 0
    assert merged["ruleCount"] == 0 and merged["exampleCount"] == 0
    assert merged["parseErrors"] == repo["parseErrors"]
    # The tracker still owns what the repo cannot know.
    assert merged["status"] == "In Delivery" and merged["workstream"] == "Finance"
    assert merged["source"] == "tracker+repo"


def test_merge_still_keeps_tracker_scenarios_when_the_repo_has_no_feature_files(repo_ingest):
    tracker = [{"key": "X-1", "rules": [{"rule": "r", "scenarios": [{"name": "s"}]}],
                "scenarioCount": 1, "ruleCount": 1}]
    repo = [{"key": "X-1", "rules": [], "ruleCount": 0, "scenarioCount": 0,
             "parseErrors": [], "sourcePath": "features/x-1", "nfr": [{"id": "N1"}]}]
    merged = repo_ingest.merge(tracker, repo)[0]
    assert merged["scenarioCount"] == 1 and merged["rules"][0]["rule"] == "r"
    assert merged["nfr"] == [{"id": "N1"}]
