#!/usr/bin/env python3
"""Run a skill in a real Claude Code session and check what it CALLED, not what it said.

Model-graded evals (`run_evals.py`) send `SKILL.md` as a system prompt with no tools, so they
can grade an explanation but cannot show tool behaviour: "never proposes", "never applies a
correction", "never starts an ingestion run". A response that says it did not write proves
nothing about whether it wrote. This runner gives the skill the real host and real tools —
`claude -p --bare` with this checkout's plugin loaded by `--plugin-dir` and the mock read
server from `evals/mock_pdg` attached — and checks two independent records of tool use:

  * the session's stream-json events (every tool_use the model emitted, allowed or not), and
  * the mock server's call log (every tools/call that reached it).

A canary (see `evals/mock_pdg/server.py`) is a tool advertised so that declining it is
observable. A case fails if a forbidden tool appears in either record, if a required read is
missing, if the expected skill was not loaded, or if the loaded plugin is not this checkout.

Dry run is the default and calls nothing. `--execute` needs `--model` and spends money: each
case is a full agentic session. Auth is whatever `claude --bare` accepts (ANTHROPIC_API_KEY or
an apiKeyHelper); OAuth logins are not read in bare mode. Results land in `.claude/traces/`.

    python evals/run_traces.py                                   # dry run, every case
    python evals/run_traces.py --case opportunity-package-declines-write-canaries \\
        --execute --model claude-opus-5 --max-budget-usd 2
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "evals" / "traces" / "cases.json"
PLUGIN = ROOT / "plugins" / "aipos"
MOCK = ROOT / "evals" / "mock_pdg" / "server.py"
SERVER = "opportunity-engine-mock"
DEFAULT_OUT = ROOT / ".claude" / "traces"
#: Tools a case may use without listing them. Anything else is denied by the host, and a denied
#: attempt still shows in the stream — which is the point.
BASE_ALLOWED = ["Skill", "Read", "Glob", "Grep", f"mcp__{SERVER}"]
CASE_KEYS = {"id", "skill", "prompt", "invoke", "follow_ups", "files", "mock", "max_turns", "expect", "note"}
EXPECT_KEYS = {"skill_loaded", "forbidden_tools", "required_tools", "forbidden_builtin_tools"}
MOCK_KEYS = {"fixture", "canary_tools", "evidence_text", "links"}


# ----------------------------------------------------------------------------- cases


def load_cases(path: Path = CASES) -> list[dict]:
    cases = json.loads(path.read_text())["cases"]
    seen = set()
    for case in cases:
        problems = validate_case(case)
        if problems:
            raise ValueError(f"trace case {case.get('id')!r}: {'; '.join(problems)}")
        if case["id"] in seen:
            raise ValueError(f"duplicate trace case id {case['id']!r}")
        seen.add(case["id"])
    return cases


def validate_case(case: dict) -> list[str]:
    problems = []
    for key in ("id", "skill", "prompt", "expect"):
        if not case.get(key):
            problems.append(f"missing {key}")
    if set(case) - CASE_KEYS:
        problems.append(f"unknown keys {sorted(set(case) - CASE_KEYS)}")
    expect = case.get("expect") or {}
    if set(expect) - EXPECT_KEYS:
        problems.append(f"unknown expect keys {sorted(set(expect) - EXPECT_KEYS)}")
    mock = case.get("mock") or {}
    if set(mock) - MOCK_KEYS:
        problems.append(f"unknown mock keys {sorted(set(mock) - MOCK_KEYS)}")
    if case.get("skill") and expect.get("skill_loaded") not in (None, case["skill"]):
        problems.append("expect.skill_loaded must name the case's skill")
    canaries = set(mock.get("canary_tools") or [])
    if canaries - set(expect.get("forbidden_tools") or []):
        problems.append("every canary must also be a forbidden tool")
    if case.get("invoke", "natural") not in ("natural", "slash"):
        problems.append("invoke must be 'natural' or 'slash'")
    if not isinstance(case.get("follow_ups", []), list):
        problems.append("follow_ups must be a list")
    if case.get("skill") and not (PLUGIN / "skills" / case["skill"] / "SKILL.md").is_file():
        problems.append(f"no skill {case['skill']} in {PLUGIN}")
    return problems


# ----------------------------------------------------------------------------- evaluation


def _short(tool_name: str) -> str:
    """mcp__<server>__get_problem -> get_problem; built-ins pass through."""
    prefix = f"mcp__{SERVER}__"
    return tool_name[len(prefix):] if tool_name.startswith(prefix) else tool_name


def tool_uses(events: list[dict]) -> list[dict]:
    uses = []
    for event in events:
        if event.get("type") != "assistant":
            continue
        for block in (event.get("message") or {}).get("content") or []:
            if isinstance(block, dict) and block.get("type") == "tool_use":
                uses.append({"name": block.get("name"), "input": block.get("input") or {}})
    return uses


def skills_loaded(uses: list[dict]) -> set[str]:
    loaded = set()
    for use in uses:
        if use["name"] == "Skill":
            name = str(use["input"].get("skill") or use["input"].get("command") or "")
            loaded.add(name.split(":", 1)[-1].lstrip("/").split()[0] if name else name)
    return loaded


def init_event(events: list[dict]) -> dict | None:
    return next((e for e in events if e.get("type") == "system" and e.get("subtype") == "init"), None)


def evaluate(events: list[dict], calls: list[dict], expect: dict, *, plugin_path: Path = PLUGIN,
             invoke: str = "natural") -> dict:
    """Judge one run from its records. Pure: no I/O, so pytest can pin every rule.

    `invoke="natural"` requires the model to have loaded the skill through the Skill tool.
    `invoke="slash"` means the runner sent `/aipos:<skill>` as the prompt, which the host expands
    without a tool event; the evidence is then that the session advertised that command.
    """
    violations = []
    init = init_event(events)
    if init is None:
        violations.append("no init event: the session did not start")
    else:
        aipos = [p for p in init.get("plugins") or [] if p.get("name") == "aipos"]
        if len(aipos) != 1 or Path(aipos[0].get("path", "")).resolve() != plugin_path.resolve():
            violations.append(f"aipos plugin not loaded from this checkout: {aipos}")
        mock = [s for s in init.get("mcp_servers") or [] if s.get("name") == SERVER]
        if not mock or mock[0].get("status") != "connected":
            violations.append(f"mock server not connected: {mock}")

    uses = tool_uses(events)
    emitted = [_short(u["name"]) for u in uses]
    reached = [c.get("tool") for c in calls]
    loaded = skills_loaded(uses)

    wanted = expect.get("skill_loaded")
    if wanted and invoke == "slash":
        commands = {str(c).lstrip("/") for c in (init or {}).get("slash_commands") or []}
        if f"aipos:{wanted}" not in commands:
            violations.append(f"slash command aipos:{wanted} not available in the session")
        else:
            loaded.add(wanted)
    elif wanted and wanted not in loaded:
        violations.append(f"skill {wanted} was never loaded (loaded: {sorted(loaded)})")

    for name in expect.get("forbidden_tools") or []:
        if name in emitted:
            violations.append(f"forbidden tool {name} was called by the model")
        if name in reached:
            violations.append(f"forbidden tool {name} reached the server")
    for name in expect.get("forbidden_builtin_tools") or []:
        if name in emitted:
            violations.append(f"forbidden built-in {name} was called")
    for name in expect.get("required_tools") or []:
        if name not in reached:
            violations.append(f"required read {name} never reached the server")

    results = [e for e in events if e.get("type") == "result"]
    if not results:
        violations.append("no result event: the session did not finish")
    elif any(r.get("is_error") for r in results):
        violations.append(f"session ended in error: {[r.get('subtype') for r in results]}")

    return {
        "passed": not violations,
        "violations": violations,
        "emitted_tools": emitted,
        "server_calls": reached,
        "skills_loaded": sorted(loaded),
        "invoke": invoke,
        "model": (init or {}).get("model"),
        "cost_usd": sum(r.get("total_cost_usd") or 0 for r in results),
    }


# ----------------------------------------------------------------------------- running


def mcp_config(case: dict, call_log: Path) -> dict:
    mock = case.get("mock") or {}
    env = {"MOCK_PDG_CALL_LOG": str(call_log)}
    if mock.get("fixture"):
        env["MOCK_PDG_FIXTURE"] = str((ROOT / mock["fixture"]).resolve())
    if mock.get("canary_tools"):
        env["MOCK_PDG_CANARY_TOOLS"] = ",".join(mock["canary_tools"])
    if mock.get("evidence_text") is False:
        env["MOCK_PDG_EVIDENCE_TEXT"] = "off"
    if mock.get("links") is False:
        env["MOCK_PDG_LINKS"] = "off"
    return {"mcpServers": {SERVER: {"command": sys.executable, "args": [str(MOCK)], "env": env}}}


def command(prompt: str, *, model: str, config: Path, max_turns: int, budget: float | None,
            resume: str | None) -> list[str]:
    cmd = ["claude", "-p", prompt, "--bare", "--plugin-dir", str(PLUGIN),
           "--mcp-config", str(config), "--strict-mcp-config",
           "--output-format", "stream-json", "--verbose", "--model", model,
           "--max-turns", str(max_turns), "--permission-prompts", "none",
           "--allowedTools", *BASE_ALLOWED]
    if budget:
        cmd += ["--max-budget-usd", str(budget)]
    if resume:
        cmd += ["--resume", resume]
    return cmd


def first_prompt(case: dict) -> str:
    if case.get("invoke") == "slash":
        return f"/aipos:{case['skill']} {case['prompt']}"
    return case["prompt"]


def run_case(case: dict, *, model: str, out: Path, budget: float | None, timeout: float) -> dict:
    # Absolute, and outside the session's working directory: the mock runs elsewhere, and the
    # model must not be able to read the config that names the canaries.
    out = out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix=f"trace-{case['id']}-"))
    try:
        for rel in case.get("files") or []:
            src = ROOT / rel
            shutil.copy(src, work / src.name)
        call_log = out / "server_calls.jsonl"
        call_log.write_text("")
        config = out / "mcp.json"
        config.write_text(json.dumps(mcp_config(case, call_log)))
        events: list[dict] = []
        session = None
        for turn, prompt in enumerate([first_prompt(case), *(case.get("follow_ups") or [])]):
            cmd = command(prompt, model=model, config=config, max_turns=case.get("max_turns", 25),
                          budget=budget, resume=session)
            run = subprocess.run(cmd, cwd=work, capture_output=True, text=True, timeout=timeout,
                                 stdin=subprocess.DEVNULL)
            (out / f"stream.{turn}.jsonl").write_text(run.stdout)
            (out / f"stderr.{turn}.txt").write_text(run.stderr)
            turn_events = [json.loads(line) for line in run.stdout.splitlines() if line.strip()]
            events.extend(turn_events)
            init = init_event(turn_events)
            session = (init or {}).get("session_id") or session
            if run.returncode != 0 or session is None:
                break
        calls = [json.loads(line) for line in call_log.read_text().splitlines() if line.strip()]
        verdict = evaluate(events, calls, case["expect"], invoke=case.get("invoke", "natural"))
        verdict.update({"case": case["id"], "skill": case["skill"], "requested_model": model,
                        "at": datetime.now(timezone.utc).isoformat(timespec="seconds")})
        (out / "verdict.json").write_text(json.dumps(verdict, indent=2))
        return verdict
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--cases", type=Path, default=CASES)
    parser.add_argument("--case", action="append", help="case id (repeatable)")
    parser.add_argument("--skill", help="only cases for this skill")
    parser.add_argument("--execute", action="store_true", help="run real sessions (costs money)")
    parser.add_argument("--model", help="required with --execute")
    parser.add_argument("--reps", type=int, default=1)
    parser.add_argument("--max-budget-usd", type=float, default=None, help="per session")
    parser.add_argument("--timeout", type=float, default=900)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)

    cases = load_cases(args.cases)
    if args.case:
        unknown = set(args.case) - {c["id"] for c in cases}
        if unknown:
            parser.error(f"unknown case(s): {sorted(unknown)}")
        cases = [c for c in cases if c["id"] in args.case]
    if args.skill:
        cases = [c for c in cases if c["skill"] == args.skill]
    if not cases:
        parser.error("no cases selected")

    if not args.execute:
        print(f"DRY RUN — {len(cases)} case(s) x {args.reps} rep(s); nothing was called.")
        for case in cases:
            print(f"  {case['id']} [{case['skill']}] turns={1 + len(case.get('follow_ups') or [])} "
                  f"canaries={(case.get('mock') or {}).get('canary_tools') or []} "
                  f"forbidden={case['expect'].get('forbidden_tools') or []}")
        first = cases[0]
        print("First command:", " ".join(command(first_prompt(first), model=args.model or "<model>",
                                                 config=Path("<tmp>/mcp.json"),
                                                 max_turns=first.get("max_turns", 25),
                                                 budget=args.max_budget_usd, resume=None)))
        return 0
    if not args.model:
        parser.error("--execute requires --model")
    if shutil.which("claude") is None:
        parser.error("the claude CLI is not on PATH")

    verdicts = []
    for case in cases:
        for rep in range(args.reps):
            out = args.out / case["id"] / f"rep{rep}"
            verdict = run_case(case, model=args.model, out=out, budget=args.max_budget_usd,
                               timeout=args.timeout)
            verdicts.append(verdict)
            mark = "PASS" if verdict["passed"] else "FAIL"
            print(f"{mark}  {case['id']} rep{rep}  model={verdict['model']}  "
                  f"calls={verdict['server_calls']}  ${verdict['cost_usd']:.2f}")
            for violation in verdict["violations"]:
                print(f"      - {violation}")
    passed = sum(v["passed"] for v in verdicts)
    print(f"{passed}/{len(verdicts)} trace run(s) passed. Traces: {args.out}")
    return 0 if passed == len(verdicts) else 1


if __name__ == "__main__":
    sys.exit(main())
