"""The engine's release contract, checked on the built opportunities panel.

discovery-engine serves `panels/opportunities/dist/opportunities.html` as `ui://aipos/opportunities`
once a release is pinned there (feature 27, ADR-AIG-039). It binds the file only if it fits the
contract in its `docs/backend/api-contract/ui_handoff.md`, "MCP App panels". The engine's
load-time scan is a tripwire; this test is the primary control
(docs/plans/2026-10-23-opportunities-panel.md, "The contract test").

Each rule is a function over the file's bytes, so the same function is also run on planted
violations below: every check is proven able to fail, not only seen to pass. The freshness of
`dist/` against its source is checked by `node build.mjs --check` in validate.yml, which needs
the panel's locked Node dependencies.
"""

from __future__ import annotations

import html.parser
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
PANEL = ROOT / "panels" / "opportunities" / "dist" / "opportunities.html"

#: The byte ceiling for the complete, uncompressed file. PROPOSED, not yet the engine's: the
#: engine's `src/engine/composition.py` `MAX_BUNDLE_BYTES` is 256,000 today, and the SDK panel
#: needs it raised (plan, "Required engine bundle-budget change"). This must equal the engine's
#: value before a release is pinned; change both together.
MAX_BYTES = 1_048_576

#: The tools this panel may call: discovery-engine `src/engine/api/mcp/panels.py`,
#: `PANELS["opportunities"].allowed_tools`.
ALLOWED_TOOLS = frozenset({"list_opportunities", "get_problem", "list_evidence"})

#: Mirrors discovery-engine `src/engine/api/mcp/panels.py` `ENGINE_TOOL_NAMES`: every tool the
#: engine can advertise. Update the two together; a name missing here is one the engine refuses.
ENGINE_TOOL_NAMES = frozenset(
    {
        "list_problems",
        "get_problem",
        "get_lineage",
        "list_evidence",
        "list_opportunities",
        "get_work_item_links",
        "get_evidence_text",
        "get_demo_portfolio",
        "list_demo_opportunities",
        "get_demo_opportunity",
        "find_similar_problems",
        "get_decision_thread",
        "propose_problem",
        "attach_intent",
        "record_exploration_decision",
    }
)


def size_problems(data: bytes) -> list[str]:
    return [] if len(data) <= MAX_BYTES else [f"{len(data)} bytes exceeds {MAX_BYTES}"]


def utf8_problems(data: bytes) -> list[str]:
    try:
        data.decode("utf-8")
    except UnicodeDecodeError as exc:
        return [f"not valid UTF-8: {exc}"]
    return []


def _names(data: bytes, tool: str) -> bool:
    """Whether `tool` occurs as a whole identifier, exactly as the engine's scan decides it."""
    return bool(
        re.search(rb"(?<![A-Za-z0-9_])" + re.escape(tool.encode()) + rb"(?![A-Za-z0-9_])", data)
    )


def tool_name_problems(data: bytes) -> list[str]:
    forbidden = sorted(t for t in ENGINE_TOOL_NAMES - ALLOWED_TOOLS if _names(data, t))
    missing = sorted(t for t in ALLOWED_TOOLS if not _names(data, t))
    return [f"names forbidden tool {t}" for t in forbidden] + [
        f"does not name allowed tool {t}" for t in missing
    ]


class _Markup(html.parser.HTMLParser):
    """Collects what in the static markup could load something, and the inline CSS and JS."""

    LOADING = {"src", "srcset", "data", "poster", "background", "action", "formaction"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.problems: list[str] = []
        self.css: list[str] = []
        self.js: list[str] = []
        self._in: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {name: value or "" for name, value in attrs}
        for name, value in values.items():
            if name in self.LOADING and value and not value.startswith("data:"):
                self.problems.append(f"<{tag} {name}={value!r}> loads from outside the file")
            if name == "href" and value and not value.startswith(("#", "data:")):
                self.problems.append(f"<{tag} href={value!r}> points outside the file")
            if name == "style":
                self.css.append(value)
        if tag == "link":
            self.problems.append(f"<link {values}>: no linked resources, stylesheets or fonts")
        if tag == "base":
            self.problems.append("<base> changes where relative URLs resolve")
        if tag == "meta" and values.get("http-equiv", "").lower() == "refresh":
            self.problems.append("<meta http-equiv=refresh> navigates away")
        if tag in {"style", "script"}:
            self._in = tag

    def handle_endtag(self, tag: str) -> None:
        if tag == self._in:
            self._in = None

    def handle_data(self, data: str) -> None:
        if self._in == "style":
            self.css.append(data)
        elif self._in == "script":
            self.js.append(data)


_CSS_RULES = [
    (re.compile(r"@import\b", re.I), "@import"),
    (re.compile(r"@font-face\b", re.I), "@font-face (no web fonts)"),
    (re.compile(r"url\(\s*(?![\"']?data:)", re.I), "url() to something other than data:"),
]
#: Network and loading APIs. A panel reaches the engine only through the host bridge (postMessage).
_JS_RULES = [
    (re.compile(r"(?<![\w$])fetch\s*\("), "fetch("),
    (re.compile(r"\bnew\s+XMLHttpRequest\b"), "XMLHttpRequest"),
    (re.compile(r"\bnew\s+WebSocket\b"), "WebSocket"),
    (re.compile(r"\bnew\s+EventSource\b"), "EventSource"),
    (re.compile(r"\bsendBeacon\s*\("), "navigator.sendBeacon"),
    (re.compile(r"\bimportScripts\s*\("), "importScripts"),
    (re.compile(r"\bnew\s+(?:Shared)?Worker\s*\("), "a worker"),
    (re.compile(r"(?<![\w$.])import\s*\("), "dynamic import()"),
    (re.compile(r"""\.(?:src|href)\s*=\s*["'`]https?://"""), "assigning an external src/href"),
]


def external_request_problems(data: bytes) -> list[str]:
    markup = _Markup()
    markup.feed(data.decode("utf-8", errors="replace"))
    problems = list(markup.problems)
    for css in markup.css:
        problems += [f"CSS uses {label}" for pattern, label in _CSS_RULES if pattern.search(css)]
    for js in markup.js:
        problems += [f"script uses {label}" for pattern, label in _JS_RULES if pattern.search(js)]
    return problems


CHECKS = [size_problems, utf8_problems, tool_name_problems, external_request_problems]


@pytest.fixture(scope="module")
def built() -> bytes:
    assert PANEL.is_file(), "build the panel: node panels/opportunities/build.mjs"
    return PANEL.read_bytes()


@pytest.mark.parametrize("check", CHECKS, ids=lambda c: c.__name__)
def test_the_built_panel_meets_the_contract(built: bytes, check) -> None:
    assert check(built) == []


def test_the_panel_is_one_html_document_with_inline_script_and_style(built: bytes) -> None:
    markup = _Markup()
    markup.feed(built.decode("utf-8"))
    assert built.lstrip().lower().startswith(b"<!doctype html>")
    assert len(markup.js) == 1 and len(markup.js[0]) > 1000, "one inline, bundled script"
    assert markup.css and "--panel-bg" in markup.css[0], "the panel stylesheet is inline"


# --- Every check can fail ----------------------------------------------------------------------

MINIMAL = (
    b"<!doctype html><html><head><style>body{color:red}</style></head><body>"
    b"<script>call('list_opportunities');call('get_problem');call('list_evidence')</script>"
    b"</body></html>"
)


def test_the_minimal_page_passes_every_check() -> None:
    for check in CHECKS:
        assert check(MINIMAL) == [], check.__name__


@pytest.mark.parametrize("size", [MAX_BYTES - 1, MAX_BYTES])
def test_a_file_at_or_under_the_ceiling_fits(size: int) -> None:
    assert size_problems(b"x" * size) == []


def test_a_file_one_byte_over_the_ceiling_does_not_fit() -> None:
    assert size_problems(b"x" * (MAX_BYTES + 1)) == [f"{MAX_BYTES + 1} bytes exceeds {MAX_BYTES}"]


def test_invalid_utf8_is_refused() -> None:
    assert utf8_problems(MINIMAL + b"\xff")


@pytest.mark.parametrize("tool", sorted(ENGINE_TOOL_NAMES - ALLOWED_TOOLS))
def test_a_planted_forbidden_tool_name_is_found(tool: str) -> None:
    planted = MINIMAL.replace(b"</script>", b"/* " + tool.encode() + b" */</script>")
    assert tool_name_problems(planted) == [f"names forbidden tool {tool}"]


def test_a_tool_name_inside_a_longer_identifier_is_not_a_hit() -> None:
    planted = MINIMAL.replace(b"</script>", b"var get_evidence_textual=1;xget_lineage=2</script>")
    assert tool_name_problems(planted) == []


def test_an_allowed_tool_the_panel_no_longer_names_is_reported() -> None:
    assert tool_name_problems(MINIMAL.replace(b"get_problem", b"other")) == [
        "does not name allowed tool get_problem"
    ]


@pytest.mark.parametrize(
    "planted",
    [
        b'<script src="https://cdn.example.com/x.js"></script>',
        b'<img src="https://example.com/a.png">',
        b'<link rel="stylesheet" href="https://fonts.example.com/css">',
        b'<a href="https://example.com/">x</a>',
        b'<base href="https://example.com/">',
        b'<meta http-equiv="refresh" content="0;url=https://example.com/">',
        b'<form action="https://example.com/"></form>',
        b"<style>@import 'https://example.com/a.css';</style>",
        b"<style>@font-face{font-family:P;src:url(data:font/woff2;base64,AA)}</style>",
        b"<style>body{background:url(https://example.com/a.png)}</style>",
        b'<div style="background:url(//example.com/a.png)"></div>',
        b"<script>fetch('https://example.com/')</script>",
        b"<script>window.fetch('/x')</script>",
        b"<script>new XMLHttpRequest()</script>",
        b"<script>new WebSocket('wss://example.com')</script>",
        b"<script>new EventSource('/s')</script>",
        b"<script>navigator.sendBeacon('/b')</script>",
        b"<script>import('https://example.com/m.js')</script>",
        b"<script>new Worker('w.js')</script>",
        b"<script>img.src = 'https://example.com/p.gif'</script>",
    ],
)
def test_a_planted_external_request_is_found(planted: bytes) -> None:
    page = MINIMAL.replace(b"</body>", planted + b"</body>")
    assert external_request_problems(page), planted


def test_data_urls_and_json_schema_identifiers_are_not_requests() -> None:
    # The bundled SDK carries JSON Schema $schema URIs as plain strings, and zod's `.url()`
    # validator; neither loads anything.
    page = MINIMAL.replace(
        b"</body>",
        b'<img src="data:image/png;base64,AA">'
        b"<style>i{background:url(data:image/svg+xml;utf8,x)}</style>"
        b'<script>var s="https://json-schema.org/draft/2020-12/schema";z.string().url()</script>'
        b"</body>",
    )
    assert external_request_problems(page) == []
