#!/usr/bin/env python3
"""A stand-in for the Discovery Engine's `opportunity-engine` MCP read server — fixtures only.

Why this exists: skills that read the Product Definition Graph (PDG) have to be built and
exercised before a live engine is reachable. This server speaks the same seven read tools with
the same response shapes, so a skill cannot tell it from the real server except by its name —
going live is a configuration change, not a code change.

What it is not: a data source. Every identifier starts with `fixture:` or a fixture source
prefix, and every free-text value carries `[SYNTHETIC]`, so nothing it returns can be mistaken
for real evidence if it leaks into an artifact.

Contract mirrored (discovery-engine, `src/engine/api/schemas.py` and `src/engine/api/mcp/`):

  list_problems(offset=0, limit=20)        -> ProblemListResponse
  get_problem(problem_id)                  -> ProblemDetailResponse
  get_lineage(problem_id)                  -> LineageResponse
  list_evidence(problem_id)                -> ProblemEvidenceResponse
  list_opportunities(offset=0, limit=20)   -> OpportunityListResponse
  get_work_item_links(problem_id)          -> ProblemLinksResponse
  get_evidence_text(provenance_reference, problem_id=None) -> EvidenceExcerptResponse

Behaviour mirrored because skills must handle it:
  * offset >= 0 and 1 <= limit <= 100, else VALIDATION_ERROR
  * unknown problem -> PROBLEM_NOT_FOUND
  * get_evidence_text: one reference per call; a reference the problem set does not hold, or a
    source with no readable text -> EVIDENCE_TEXT_UNAVAILABLE
  * when evidence text is not configured the tool is *not advertised at all*
  * when links are not configured get_work_item_links is advertised but raises LINKS_UNAVAILABLE
  * errors are tool results with isError=true and text "<CODE>: <message>"

Configuration (environment):
  MOCK_PDG_FIXTURE         path to a fixture JSON (default: fixtures/default.json)
  MOCK_PDG_EVIDENCE_TEXT   "off" to stop advertising get_evidence_text
  MOCK_PDG_LINKS           "off" to make get_work_item_links raise LINKS_UNAVAILABLE
  MOCK_PDG_ACCESS_LOG      path of a JSON-lines file recording every get_evidence_text call,
                           as the engine access-logs each disclosure (refused reads included)

Transport: MCP over stdio, newline-delimited JSON-RPC 2.0. Standard library only, so it runs
anywhere Python 3.9+ does and never adds a dependency to the plugin.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

SERVER_NAME = "opportunity-engine-mock"
SERVER_VERSION = "0.1.0"
DEFAULT_PROTOCOL = "2025-06-18"
INSTRUCTIONS = (
    "MOCK of the Discovery Engine's read server. Serves SYNTHETIC fixtures in the real response "
    "shapes for development and evaluation. Nothing returned here is evidence."
)
MIN_LIMIT, MAX_LIMIT = 1, 100
HERE = Path(__file__).resolve().parent


class ToolFailure(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


# ----------------------------------------------------------------------------- data


def load_fixture(path: Path | None = None) -> dict:
    path = path or Path(os.environ.get("MOCK_PDG_FIXTURE") or HERE / "fixtures" / "default.json")
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


class Graph:
    """Derives every response from one list of problem records, as the engine derives them
    from one graph — so two tools can never disagree about the same problem."""

    def __init__(self, fixture: dict) -> None:
        self.problems = sorted(
            fixture["problems"], key=lambda p: (-p["composite_score"], p["problem_id"])
        )
        self.by_id = {p["problem_id"]: p for p in self.problems}
        self.known_refs = {e["provenance_reference"] for p in self.problems for e in p["evidence"]}

    def _problem(self, problem_id: object) -> dict:
        if not isinstance(problem_id, str) or not problem_id:
            raise ToolFailure("VALIDATION_ERROR", "problem_id is required")
        try:
            return self.by_id[problem_id]
        except KeyError:
            raise ToolFailure("PROBLEM_NOT_FOUND", f"Problem {problem_id!r} not found") from None

    @staticmethod
    def _page(offset: object, limit: object) -> tuple[int, int]:
        if not isinstance(offset, int) or isinstance(offset, bool) or offset < 0:
            raise ToolFailure("VALIDATION_ERROR", "offset must be greater than or equal to 0")
        if not isinstance(limit, int) or isinstance(limit, bool) or not MIN_LIMIT <= limit <= MAX_LIMIT:
            raise ToolFailure("VALIDATION_ERROR", f"limit must be between {MIN_LIMIT} and {MAX_LIMIT}")
        return offset, limit

    # --- shapes ---------------------------------------------------------------

    @staticmethod
    def _personas(p: dict) -> list:
        return [{"name": x["name"], "confidence": x["confidence"]} for x in p["personas"]]

    @staticmethod
    def _link(p: dict, link: dict) -> dict:
        return {"problem_id": p["problem_id"], **link}

    def _active_links(self, p: dict) -> list:
        return [self._link(p, x) for x in p.get("links", []) if x["status"] == "active"]

    # --- tools ----------------------------------------------------------------

    def list_problems(self, offset: int = 0, limit: int = 20) -> dict:
        offset, limit = self._page(offset, limit)
        window = self.problems[offset:offset + limit]
        return {
            "items": [
                {
                    "problem_id": p["problem_id"],
                    "title": p["title"],
                    "composite_score": p["composite_score"],
                    "lineage_ref": p["lineage_ref"],
                    "personas": self._personas(p),
                    "schema_version": p["schema_version"],
                }
                for p in window
            ],
            "total": len(self.problems),
            "offset": offset,
            "limit": limit,
        }

    def get_problem(self, problem_id: str) -> dict:
        p = self._problem(problem_id)
        return {
            "problem_id": p["problem_id"],
            "title": p["title"],
            "composite_score": p["composite_score"],
            "evidence_references": [e["provenance_reference"] for e in p["evidence"]],
            "personas": self._personas(p),
            "lineage_ref": p["lineage_ref"],
            "schema_version": p["schema_version"],
        }

    def get_lineage(self, problem_id: str) -> dict:
        p = self._problem(problem_id)
        return {
            "problem_id": p["problem_id"],
            "source_evidence_refs": [e["provenance_reference"] for e in p["evidence"]],
            "originating_sources": list(p["originating_sources"]),
            "schema_version": p["schema_version"],
        }

    def list_evidence(self, problem_id: str) -> dict:
        p = self._problem(problem_id)
        items = [
            {
                "provenance_reference": e["provenance_reference"],
                "source_system": e["source_system"],
                "source_type": e["source_type"],
                "external_record_id": e["external_record_id"],
                "occurred_at": e["occurred_at"],
                "record_url": e["record_url"],
                "schema_version": e.get("schema_version", 1),
            }
            for e in p["evidence"]
        ]
        return {"problem_id": p["problem_id"], "items": items, "total": len(items)}

    def list_opportunities(self, offset: int = 0, limit: int = 20) -> dict:
        offset, limit = self._page(offset, limit)
        window = self.problems[offset:offset + limit]
        return {
            "items": [
                {
                    "problem_id": p["problem_id"],
                    "title": p["title"],
                    "composite_score": p["composite_score"],
                    "components": dict(p["opportunity"]["components"]),
                    "strategic_weight": p["opportunity"]["strategic_weight"],
                    "weight_config_version": p["opportunity"]["weight_config_version"],
                    "links": self._active_links(p),
                    "schema_version": p["opportunity"].get("schema_version", p["schema_version"]),
                }
                for p in window
            ],
            "total": len(self.problems),
            "offset": offset,
            "limit": limit,
        }

    def get_work_item_links(self, problem_id: str) -> dict:
        if os.environ.get("MOCK_PDG_LINKS", "").lower() == "off":
            raise ToolFailure("LINKS_UNAVAILABLE", "Work-item links are not configured")
        p = self._problem(problem_id)
        links = [self._link(p, x) for x in p.get("links", [])]
        promoted = any(x["status"] == "active" and x["link_type"] == "promoted" for x in links)
        return {
            "problem_id": p["problem_id"],
            "promoted": promoted,
            "links": links,
            "total": len(links),
            "schema_version": p["schema_version"],
        }

    def get_evidence_text(self, provenance_reference: str, problem_id: str | None = None) -> dict:
        try:
            result = self._evidence_text(provenance_reference, problem_id)
        except ToolFailure as failure:
            _log_access(provenance_reference, problem_id, returned=False, code=failure.code)
            raise
        _log_access(provenance_reference, problem_id, returned=True, code=None)
        return result

    def _evidence_text(self, provenance_reference: object, problem_id: str | None) -> dict:
        # Anchoring mirrors the engine's `_anchor_terms`: an unknown problem degrades to an
        # unanchored excerpt rather than failing the disclosure.
        if not isinstance(provenance_reference, str):
            raise ToolFailure(
                "VALIDATION_ERROR",
                "get_evidence_text accepts exactly one provenance_reference, not a collection",
            )
        system, sep, external = provenance_reference.strip().partition(":")
        if not sep or not system or not external:
            raise ToolFailure(
                "VALIDATION_ERROR",
                f"Malformed provenance_reference {provenance_reference!r} — "
                "expected '<source_system>:<external_record_id>'",
            )
        if provenance_reference not in self.known_refs:
            raise ToolFailure(
                "EVIDENCE_TEXT_UNAVAILABLE", f"No evidence found for {provenance_reference!r}"
            )
        anchored = False
        if problem_id:
            anchored = problem_id in self.by_id
        for p in self.problems:
            for e in p["evidence"]:
                if e["provenance_reference"] == provenance_reference and e.get("excerpt"):
                    x = e["excerpt"]
                    return {
                        "provenance_reference": provenance_reference,
                        "source_system": e["source_system"],
                        "excerpt": x["text"],
                        "origin": "source",
                        "redaction_applied": x.get("redaction_applied", False),
                        "anchored": anchored,
                        "truncated": x.get("truncated", False),
                        "schema_version": 1,
                    }
        raise ToolFailure(
            "EVIDENCE_TEXT_UNAVAILABLE", f"No text available for {provenance_reference!r}"
        )


def _log_access(reference: object, problem_id: object, *, returned: bool, code: str | None) -> None:
    path = os.environ.get("MOCK_PDG_ACCESS_LOG")
    if not path:
        return
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps({"tool": "get_evidence_text", "provenance_reference": reference,
                                 "problem_id": problem_id, "returned": returned, "code": code}) + "\n")


# ----------------------------------------------------------------------------- tool catalog

_PAGED = {
    "type": "object",
    "properties": {
        "offset": {"type": "integer", "default": 0, "minimum": 0},
        "limit": {"type": "integer", "default": 20, "minimum": MIN_LIMIT, "maximum": MAX_LIMIT},
    },
}
_BY_PROBLEM = {
    "type": "object",
    "properties": {"problem_id": {"type": "string"}},
    "required": ["problem_id"],
}

TOOLS = [
    ("list_problems", "List ranked problems, highest composite score first.", _PAGED),
    ("get_problem", "Get one problem's detail, with its personas and evidence references.", _BY_PROBLEM),
    ("get_lineage", "Get the source evidence and originating sources a problem was extracted from.", _BY_PROBLEM),
    ("list_evidence", "List a problem's evidence as provenance references only — never quote or note text.", _BY_PROBLEM),
    ("list_opportunities", "List ranked opportunities with score components and active work-item links.", _PAGED),
    ("get_work_item_links", "Get a problem's work-item links and its derived promoted verdict.", _BY_PROBLEM),
    (
        "get_evidence_text",
        "Read a redacted excerpt for ONE evidence reference, from its source when reachable.",
        {
            "type": "object",
            "properties": {
                "provenance_reference": {"type": "string"},
                "problem_id": {"type": ["string", "null"], "default": None},
            },
            "required": ["provenance_reference"],
        },
    ),
]


def advertised_tools() -> list:
    evidence_text_on = os.environ.get("MOCK_PDG_EVIDENCE_TEXT", "").lower() != "off"
    return [
        {"name": name, "description": desc, "inputSchema": schema}
        for name, desc, schema in TOOLS
        if name != "get_evidence_text" or evidence_text_on
    ]


# ----------------------------------------------------------------------------- JSON-RPC


def handle(graph: Graph, message: dict) -> dict | None:
    method = message.get("method")
    msg_id = message.get("id")
    if msg_id is None:  # a notification — never answered
        return None

    def ok(result: dict) -> dict:
        return {"jsonrpc": "2.0", "id": msg_id, "result": result}

    if method == "initialize":
        requested = (message.get("params") or {}).get("protocolVersion") or DEFAULT_PROTOCOL
        return ok({
            "protocolVersion": requested,
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            "instructions": INSTRUCTIONS,
        })
    if method == "ping":
        return ok({})
    if method == "tools/list":
        return ok({"tools": advertised_tools()})
    if method == "tools/call":
        params = message.get("params") or {}
        name = params.get("name")
        args = params.get("arguments") or {}
        if name not in {t["name"] for t in advertised_tools()}:
            return {"jsonrpc": "2.0", "id": msg_id,
                    "error": {"code": -32602, "message": f"Unknown tool: {name}"}}
        try:
            payload = getattr(graph, name)(**args)
        except ToolFailure as failure:
            return ok({"content": [{"type": "text", "text": str(failure)}], "isError": True})
        except TypeError as exc:  # unexpected or missing arguments
            return ok({"content": [{"type": "text", "text": f"VALIDATION_ERROR: {exc}"}],
                       "isError": True})
        return ok({
            "content": [{"type": "text", "text": json.dumps(payload)}],
            "structuredContent": payload,
            "isError": False,
        })
    return {"jsonrpc": "2.0", "id": msg_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"}}


def main() -> None:
    graph = Graph(load_fixture())
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            reply = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}}
        else:
            reply = handle(graph, message)
        if reply is not None:
            sys.stdout.write(json.dumps(reply) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
