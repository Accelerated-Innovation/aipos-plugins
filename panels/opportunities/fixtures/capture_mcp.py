"""Capture the panel's MCP fixtures from discovery-engine's real MCP server.

Each case is a `tools/call` made through the MCP SDK's in-process client against the engine's
`build_mcp_server`, seeded with the engine's own test fixture (`tests/unit/engine/_mcp_fixtures.py`).
What lands in `fixtures/mcp/` is therefore the `CallToolResult` a host receives on the wire,
errors included, rather than a REST envelope rewritten by hand.

Run it from a discovery-engine checkout, with that repository's virtualenv:

    cd ../discovery-engine
    PYTHONPATH=. .venv/bin/python ../aipos-plugins/panels/opportunities/fixtures/capture_mcp.py \
        ../aipos-plugins/panels/opportunities/fixtures/mcp

Nothing here ships; the panel never imports it.
"""

from __future__ import annotations

import asyncio
import json
import pathlib
import subprocess
import sys

from mcp import Client

from src.engine.adapters.store.in_memory_opportunity_score_store import (
    InMemoryOpportunityScoreStore,
)
from src.engine.api.mcp.server import build_mcp_server
from src.engine.services.engine_read_service import EngineReadService
from tests.unit.engine._mcp_fixtures import EngineFixture, pm_token

# (file stem, tool, arguments, token, scored)
CASES = [
    ("list-opportunities", "list_opportunities", {"offset": 0, "limit": 20}, "pm", True),
    ("list-opportunities-first-of-two", "list_opportunities", {"offset": 0, "limit": 1}, "pm", True),
    ("list-opportunities-second-of-two", "list_opportunities", {"offset": 1, "limit": 1}, "pm", True),
    ("list-opportunities-empty", "list_opportunities", {"offset": 0, "limit": 20}, "pm", False),
    ("get-problem", "get_problem", {"problem_id": "p-1"}, "pm", True),
    ("list-evidence", "list_evidence", {"problem_id": "p-1"}, "pm", True),
    ("get-problem-p-2", "get_problem", {"problem_id": "p-2"}, "pm", True),
    ("list-evidence-p-2", "list_evidence", {"problem_id": "p-2"}, "pm", True),
    ("error-problem-not-found", "get_problem", {"problem_id": "missing"}, "pm", True),
    ("error-insufficient-scope", "list_opportunities", {"offset": 0, "limit": 20}, "viewer", True),
    ("error-invalid-token", "list_opportunities", {"offset": 0, "limit": 20}, "invalid", True),
]


def _server(token_kind: str, *, scored: bool):  # noqa: ANN202
    fixture = EngineFixture()
    reads = fixture.read_service
    if not scored:
        reads = EngineReadService(
            query=fixture.query, scores=InMemoryOpportunityScoreStore(), links=fixture.link_store
        )
    token = "not-a-jwt" if token_kind == "invalid" else pm_token(token_kind)
    return build_mcp_server(
        query=reads, links=fixture.link_service, evidence_text=fixture.evidence_text, token=token
    )


async def main(out: pathlib.Path) -> None:
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
    ).stdout.strip()
    out.mkdir(parents=True, exist_ok=True)
    for stem, tool, arguments, token_kind, scored in CASES:
        async with Client(_server(token_kind, scored=scored)) as client:
            result = await client.call_tool(tool, arguments)
        wire = result.model_dump(mode="json", by_alias=True, exclude_none=True)
        wire.pop("resultType", None)  # SDK-side bookkeeping, not part of the JSON-RPC result
        record = {
            "captured_from": {
                "repository": "Accelerated-Innovation/discovery-engine",
                "commit": commit,
                "server": "src/engine/api/mcp/server.py build_mcp_server",
                "seed": "tests/unit/engine/_mcp_fixtures.py EngineFixture"
                + ("" if scored else ", no opportunity scores"),
                "token": {"pm": "pm role", "viewer": "viewer role", "invalid": "not a JWT"}[
                    token_kind
                ],
                "capture": "panels/opportunities/fixtures/capture_mcp.py",
            },
            "request": {"name": tool, "arguments": arguments},
            "result": wire,
        }
        (out / f"{stem}.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        print(f"{stem}.json  isError={wire.get('isError', False)}")


if __name__ == "__main__":
    asyncio.run(main(pathlib.Path(sys.argv[1])))
