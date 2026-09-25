"""The rendered page carries the journey diagram, and still works without it.

The diagram is a React Flow bundle inlined into the page, fed by the graph
journey_graph.py builds. These tests hold the page to its promises: one file
with no network dependencies, the same facts in the diagram and the tables, and
the tables alone when the bundle or script is missing.

Regenerate the viewer's test fixture after changing the graph model:

    python tests/test_render_journeys.py --write-viewer-fixture
"""

import json
import os
import pathlib
import re
import subprocess
import sys

import pytest

from skill_paths import skill_path

ROOT = pathlib.Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"
SCRIPTS = skill_path("aipos-map-render") / "scripts"
ASSETS = SCRIPTS / "assets"
VIEWER_FIXTURE = ROOT / "viewers/journey/test/fixtures/two-journeys.graph.json"

#: The bundle is inlined into every page that has a journey. Past this it
#: stops being a reasonable attachment; see the plan's increment 0.
BUNDLE_CEILING = 550 * 1024


def _two(workflow_resolve, features, workflows):
    out = []
    for name in ("invoice-approval", "threshold-setup"):
        wf = json.loads((workflows / f"{name}.workflow.json").read_text(encoding="utf-8"))
        out.append(workflow_resolve.resolve(wf, features))
    return out


@pytest.fixture(scope="module")
def two(workflow_resolve, features, workflows):
    return _two(workflow_resolve, features, workflows)


@pytest.fixture(scope="module")
def assets(render_map):
    got = render_map.viewer_assets()
    assert got, "the committed viewer bundle is missing from scripts/assets"
    return got


@pytest.fixture(scope="module")
def page(render_map, features, two, assets):
    return render_map.render(features, {}, {}, {}, two, assets)


def embedded(page):
    m = re.search(r'<script type="application/json" id="journey-data">(.*?)</script>', page, re.S)
    assert m, "no embedded journey data"
    return json.loads(m.group(1))


# ------------------------------------------------------------------ the page

def test_the_diagram_is_fed_the_same_graph_the_python_model_builds(page, journey_graph,
                                                                   features, two):
    assert embedded(page)["graph"] == journey_graph.build(features, two)


def test_the_page_makes_no_network_requests(page):
    """One file, opened offline six months later. No external script, stylesheet,
    font or import may be referenced; strings inside the bundle are not requests."""
    assert not re.search(r"<script[^>]+\bsrc=", page)
    assert not re.search(r"<link[^>]+\bhref=", page)
    assert not re.search(r"@import|url\(\s*['\"]?https?:", page)


def test_the_tables_stay_on_the_page(page):
    assert '<details class="wftables" open>' in page
    for journey in ("invoice-approval", "threshold-setup"):
        assert f'id="wfj-{journey}"' in page


def test_several_journeys_add_the_feature_to_journeys_table(page):
    """Question 2 has to be answerable without the diagram, too."""
    table = page.split("Features and the journeys that use them", 1)[1].split("</table>", 1)[0]
    row = next(r for r in table.split("<tr>") if "Invoice approval routing" in r)
    assert "<td>2</td>" in row
    assert "invoice-approval" in row and "threshold-setup" in row


def test_one_journey_renders_as_before(render_map, features, two, assets):
    doc = render_map.render(features, {}, {}, {}, two[0], assets)
    assert 'id="journey-root"' in doc
    assert "Features and the journeys that use them" not in doc
    assert "<h2 id=\"workflow\">The journey</h2>" in doc


def test_no_workflow_means_no_bundle(render_map, features):
    doc = render_map.render(features, {}, {}, {})
    assert "journey-root" not in doc and "journey viewer" not in doc


def test_a_missing_bundle_degrades_to_the_tables(render_map, features, two):
    doc = render_map.render(features, {}, {}, {}, two, None)
    assert "journey-root" not in doc
    assert '<details class="wftables" open>' in doc


def test_spec_text_cannot_close_the_embedding_script(render_map, journey_graph, features, two,
                                                     assets):
    hostile = json.loads(json.dumps(features))
    for f in hostile:
        for r in f.get("rules") or []:
            for s in r.get("scenarios") or []:
                s["name"] = "</script><script>alert(1)</script>"
    doc = render_map.render(hostile, {}, {}, {}, two, assets)
    names = {n["name"] for n in embedded(doc)["graph"]["nodes"] if n["kind"] == "scenario"}
    assert names == {"</script><script>alert(1)</script>"}


def test_a_source_base_url_reaches_the_diagram(render_map, features, two, assets):
    doc = render_map.render(features, {}, {}, {"sourceBaseUrl": "https://example.test/blob/abc/"},
                            two, assets)
    hrefs = [n["source"]["href"] for n in embedded(doc)["graph"]["nodes"]
             if n["kind"] == "scenario" and n.get("source")]
    assert hrefs and all(h.startswith("https://example.test/blob/abc/") for h in hrefs)


# ------------------------------------------------------------------ the CLI

def _cli(tmp_path, features, resolved_list):
    fp = tmp_path / "features.json"
    fp.write_text(json.dumps(features), encoding="utf-8")
    args = [sys.executable, str(SCRIPTS / "render_map.py"), "-f", str(fp), "-o", str(tmp_path / "m.html")]
    for i, r in enumerate(resolved_list):
        p = tmp_path / f"r{i}.json"
        p.write_text(json.dumps(r), encoding="utf-8")
        args += ["-w", str(p)]
    return subprocess.run(args, capture_output=True, text=True, cwd=tmp_path)


def test_the_cli_takes_several_workflows(tmp_path, features, two):
    run = _cli(tmp_path, features, two)
    assert run.returncode == 0, run.stderr
    assert "invoice-approval" in run.stdout and "threshold-setup" in run.stdout
    assert 'id="journey-root"' in (tmp_path / "m.html").read_text(encoding="utf-8")


def test_the_cli_refuses_two_journeys_with_one_key(tmp_path, features, two):
    run = _cli(tmp_path, features, [two[0], two[0]])
    assert run.returncode == 1
    assert "invoice-approval" in run.stderr
    assert not (tmp_path / "m.html").exists()


# ------------------------------------------------------------------ the bundle

def test_the_bundle_stays_under_its_ceiling():
    size = (ASSETS / "journey-viewer.js").stat().st_size
    assert size < BUNDLE_CEILING, f"journey-viewer.js is {size // 1024} KB"


def test_every_bundled_package_has_its_notice():
    banner = (ASSETS / "journey-viewer.js").read_text(encoding="utf-8").split("*/", 1)[0]
    notices = (ASSETS / "THIRD_PARTY_NOTICES.txt").read_text(encoding="utf-8")
    listed = re.findall(r"^ \* (\S+)@(\S+) \(", banner, re.M)
    assert len(listed) >= 5
    for name, version in listed:
        assert f"{name} {version} " in notices


def viewer_fixture_graph():
    """The graph the viewer's vitest suite reads, built from the test fixtures
    with paths relative to tests/ so it is the same on every machine."""
    sys.path.insert(0, str(SCRIPTS))
    import journey_graph
    import repo_ingest
    import workflow_resolve
    cwd = os.getcwd()
    os.chdir(TESTS)
    try:
        features = repo_ingest.walk("fixtures/corpus", "dir", "")
        return journey_graph.build(
            features, _two(workflow_resolve, features, pathlib.Path("fixtures/workflows")))
    finally:
        os.chdir(cwd)


def test_the_viewer_fixture_matches_the_python_model():
    committed = json.loads(VIEWER_FIXTURE.read_text(encoding="utf-8"))
    assert committed == viewer_fixture_graph(), (
        "viewers/journey/test/fixtures/two-journeys.graph.json is stale. Regenerate it with "
        "`python tests/test_render_journeys.py --write-viewer-fixture`.")


if __name__ == "__main__":
    if sys.argv[1:] == ["--write-viewer-fixture"]:
        VIEWER_FIXTURE.write_text(json.dumps(viewer_fixture_graph(), indent=1, ensure_ascii=False)
                                  + "\n", encoding="utf-8")
        print(f"wrote {VIEWER_FIXTURE.relative_to(ROOT)}")
    else:
        print(__doc__)
