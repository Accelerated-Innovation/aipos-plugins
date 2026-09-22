"""The render is a view of canvas.json and must never say more than the verifier does.

These run without a browser (CI has none): they check the HTML the renderer writes, which is
what the PDF and PNG are made from. The first test exists because an early render showed
"1 hours/month" for a computed 100 — a formatting bug that turned the canvas's most-quoted
number into a wrong one. Looking at the image caught it; this keeps it caught.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import re
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "plugins/aipos/skills/aipos-solution-design/scripts"
FIXTURES = ROOT / "tests/fixtures/canvas"


@pytest.fixture(scope="module")
def rc():
    spec = importlib.util.spec_from_file_location("render_canvas", SCRIPTS / "render_canvas.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load(name):
    return json.loads((FIXTURES / f"{name}.json").read_text())


def render(rc, canvas):
    report, computed = rc.load_verifier().verify(canvas)
    brand = json.loads((SCRIPTS / "brand.json").read_text())
    return rc.render_html(canvas, computed, report, brand)


def text_of(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def test_whole_numbers_keep_their_zeros(rc):
    assert [rc.num(x, 0) for x in (100.0, 1000, 10.0, 0.0)] == ["100", "1,000", "10", "0"]
    assert [rc.num(x) for x in (0.6, 1.20, -33.333)] == ["0.6", "1.2", "−33.33"]


def test_impact_at_scale_shows_the_computed_figure(rc):
    page = text_of(render(rc, load("example-as-drawn")))
    assert "100 hours/month" in page
    assert "166" not in page, "the stated figure the verifier rejected never reaches the page"


def test_derived_numbers_come_from_a_fresh_verify_not_the_file(rc):
    canvas = load("example-as-drawn")
    canvas["computed"] = {"impact_at_scale": {"result": 999, "result_unit": "hours/month"}}
    assert "999" not in render(rc, canvas)


def test_gaps_render_as_chips_and_formulas_never_numbers(rc):
    html = render(rc, load("triage-from-graph"))
    assert 'class="gap' in html
    assert "GAP × GAP ÷ 60" in text_of(html)


@pytest.mark.parametrize("name,expected", [
    ("triage-from-graph", {"synthetic", "draft"}),
    ("example-as-drawn", {"unverified", "pm", "draft"}),
])
def test_banners_say_what_the_canvas_is(rc, name, expected):
    canvas = load(name)
    report, _ = rc.load_verifier().verify(canvas)
    assert {k for k, _ in rc.banners(canvas, report)} == expected


def test_an_approved_real_canvas_carries_no_banner(rc):
    canvas = load("triage-from-graph")
    canvas["stage"] = "approved"
    canvas["source"]["server"] = "opportunity-engine"
    canvas["source"]["problem_id"] = "p-123"
    canvas["source"]["title"] = "Tickets are routed to the wrong team"
    report, _ = rc.load_verifier().verify(canvas)
    assert rc.banners(canvas, report) == []


def test_proceed_is_drawn_unavailable_with_its_reason(rc):
    html = render(rc, load("triage-from-graph"))
    assert re.search(r'class="btn disabled"><b>Proceed', html)
    assert "Unavailable: the primary metric" in html
    drawn = render(rc, load("example-as-drawn"))
    assert re.search(r'class="btn chosen disabled"><b>Proceed', drawn), \
        "a recommended-but-blocked Proceed is drawn as blocked, not as chosen"


def test_a_recommendation_is_never_drawn_as_a_decision(rc):
    page = text_of(render(rc, load("example-as-drawn")))
    assert "Recommended to" in page
    prose = page.lower().replace("decided by", "").replace("not yet decided", "")
    assert not re.search(r"\b(decided|approved)\b", prose)


def test_content_is_escaped(rc):
    canvas = load("triage-from-graph")
    canvas["goal"]["value"] = "<script>alert(1)</script>"
    html = render(rc, canvas)
    assert "<script>" not in html and "&lt;script&gt;" in html


def test_provenance_marks_reach_the_page(rc):
    html = render(rc, load("triage-from-graph"))
    assert 'class="mark mark-E"' in html


def test_cli_writes_html_without_a_browser(tmp_path):
    target = tmp_path / "canvas.json"
    target.write_text((FIXTURES / "triage-from-graph.json").read_text())
    run = subprocess.run([sys.executable, str(SCRIPTS / "render_canvas.py"), str(target), "--no-image"],
                         capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    result = json.loads(run.stdout)
    assert result["written"] == ["canvas.html"] and (tmp_path / "canvas.html").is_file()
