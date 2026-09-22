#!/usr/bin/env python3
"""Check a Solution Design canvas and compute every number the canvas displays.

The canvas is a shareable one-page artifact, so its numbers get quoted. This script is the
reason they can be: nothing on the rendered canvas is typed by hand if it can be derived.
Percent changes, per-unit savings, impact at scale, evidence counts, date ranges and aging are
computed here from the canvas's own inputs and the graph read it records; a stated figure that
disagrees with the computed one is an error, not a style note.

It also enforces the provenance contract (references/canvas-schema.md):

  * facts carry a provenance mark; an `[E]` fact cites references the graph actually returned
  * decisions carry no mark — they are authored, not evidenced
  * an evidence GAP is wired through the canvas: a to-do that gathers it, a panel-5 assumption
    that names it, and a panel-6 plan item that retires that assumption
  * Proceed is unavailable while the primary metric's baseline is a GAP
  * a quote on the canvas is a verbatim substring of an excerpt the graph returned, approved
    for the canvas by the PM

Usage:
  verify_canvas.py canvas.json            # report only (JSON to stdout); exit 1 on errors
  verify_canvas.py canvas.json --write    # also write the `computed` block back into the file

Standard library only.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

CANVAS_VERSION = 1
SUPPORTED_GRAPH_SCHEMA = 1
DEFAULT_AGING_MONTHS = 18
PCT_TOLERANCE = 0.5          # percentage points
RESULT_TOLERANCE = 0.01      # 1% relative

MARKS = {"E", "I", "A"}
STATUSES = {"confirmed", "provisional", "gap"}
GAP_TYPES = {"evidence", "decision"}
DECISIONS = {"proceed": "go", "pivot": "revise", "park": "no-go"}


class Report:
    def __init__(self) -> None:
        self.errors: list[dict] = []
        self.warnings: list[dict] = []

    def error(self, code: str, path: str, message: str) -> None:
        self.errors.append({"code": code, "path": path, "message": message})

    def warn(self, code: str, path: str, message: str) -> None:
        self.warnings.append({"code": code, "path": path, "message": message})

    def either(self, strict: bool, code: str, path: str, message: str) -> None:
        (self.error if strict else self.warn)(code, path, message)


# ----------------------------------------------------------------------------- helpers


def is_field(node: object) -> bool:
    return isinstance(node, dict) and node.get("kind") in {"fact", "decision"} and "status" in node


def walk_fields(node: object, path: str = ""):
    """Yield (path, field) for every field object, in document order."""
    if is_field(node):
        yield path, node
        return
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "computed":
                continue
            yield from walk_fields(value, f"{path}.{key}" if path else key)
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from walk_fields(value, f"{path}[{index}]")


def number(field: dict | None) -> float | None:
    if not is_field(field) or field.get("status") == "gap":
        return None
    value = field.get("value")
    return float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else None


def parse_date(value: str | None) -> dt.date | None:
    if not value:
        return None
    try:
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except ValueError:
        try:
            return dt.date.fromisoformat(value[:10])
        except ValueError:
            return None


def months_between(earlier: dt.date, later: dt.date) -> int:
    months = (later.year - earlier.year) * 12 + (later.month - earlier.month)
    return months - (1 if later.day < earlier.day else 0)


def fmt(value: float) -> str:
    return f"{value:,.2f}".rstrip("0").rstrip(".")


def factor_text(factor: float) -> str:
    """Render a unit conversion the way a person reads it: 1/60 is "÷ 60", not "× 0.02"."""
    if factor == 1:
        return ""
    inverse = 1 / factor
    if factor < 1 and abs(inverse - round(inverse)) < 1e-9:
        return f" ÷ {int(round(inverse))}"
    return f" × {fmt(factor)}"


# ----------------------------------------------------------------------------- checks


def check_top(canvas: dict, report: Report) -> None:
    if canvas.get("canvas_version") != CANVAS_VERSION:
        report.error("CANVAS_VERSION", "canvas_version",
                     f"expected {CANVAS_VERSION}, got {canvas.get('canvas_version')!r}")
    if canvas.get("mode") not in {"workshop", "coach"}:
        report.error("MODE", "mode", "mode must be 'workshop' or 'coach'")
    if canvas.get("stage") not in {"draft", "approved"}:
        report.error("STAGE", "stage", "stage must be 'draft' or 'approved'")
    for key in ("source", "panels", "footer"):
        if not isinstance(canvas.get(key), dict):
            report.error("MISSING", key, f"'{key}' object is required")


def check_source(source: dict, report: Report) -> None:
    kind = source.get("kind")
    if kind not in {"opportunity-engine", "pm-interview"}:
        report.error("SOURCE_KIND", "source.kind", "kind must be 'opportunity-engine' or 'pm-interview'")
    if kind == "opportunity-engine":
        version = source.get("schema_version")
        if version != SUPPORTED_GRAPH_SCHEMA:
            report.error("SCHEMA_VERSION_UNSUPPORTED", "source.schema_version",
                         f"graph schema_version {version!r} is not supported "
                         f"(expected {SUPPORTED_GRAPH_SCHEMA}); stop rather than guess its shape")
        if not source.get("problem_id"):
            report.error("MISSING", "source.problem_id", "an engine-sourced canvas names its problem_id")
        if not parse_date(source.get("read_at")):
            report.error("MISSING", "source.read_at", "record when the graph was read")
    if kind == "pm-interview" and source.get("evidence_refs"):
        report.error("SOURCE_KIND", "source.evidence_refs",
                     "a pm-interview canvas holds no graph references; set kind to opportunity-engine")


def check_fields(canvas: dict, graph_refs: set, report: Report) -> list:
    """Field-level provenance. Returns the list of (path, field) for later checks."""
    fields = list(walk_fields(canvas))
    for path, f in fields:
        status, kind, mark = f.get("status"), f.get("kind"), f.get("mark")
        refs = f.get("refs") or []
        if status not in STATUSES:
            report.error("FIELD_STATUS", path, f"status must be one of {sorted(STATUSES)}")
            continue
        if status == "gap":
            if f.get("value") is not None:
                report.error("GAP_HAS_VALUE", path,
                             "a GAP carries no value; a PM's remembered figure goes in 'assumed'")
            if f.get("gap_type") not in GAP_TYPES:
                report.error("GAP_TYPE", path, "a GAP is typed 'evidence' or 'decision'")
            if f.get("gap_type") == "evidence" and kind != "fact":
                report.error("GAP_TYPE", path, "only a fact can be an evidence GAP")
            assumed = f.get("assumed")
            if assumed is not None and (not isinstance(assumed, dict) or assumed.get("mark") != "A"):
                report.error("ASSUMED_MARK", path,
                             "a figure volunteered for a GAP is recorded as an [A] assumption")
            continue
        if f.get("value") in (None, "", []):
            report.error("EMPTY_FIELD", path, "a non-GAP field has a value; otherwise mark it a GAP")
        if kind == "decision":
            if mark is not None or refs:
                report.error("DECISION_MARKED", path,
                             "decisions are authored, not evidenced — no provenance mark or refs")
            continue
        # facts
        if mark not in MARKS:
            report.error("FACT_UNMARKED", path, "every fact carries [E], [I] or [A]")
            continue
        if mark == "E":
            if not refs:
                report.error("E_WITHOUT_REF", path, "an [E] fact cites the graph references behind it")
            missing = [r for r in refs if r not in graph_refs]
            if missing:
                report.error("REF_NOT_IN_GRAPH", path,
                             f"references not returned by the graph read: {missing}")
        if mark == "I" and not refs and not f.get("note"):
            report.error("I_WITHOUT_BASIS", path, "an [I] fact names its basis (refs or a note)")
    return fields


def check_gap_wiring(canvas: dict, fields: list, report: Report) -> None:
    strict = canvas.get("mode") == "coach"
    todos = {t.get("id"): t for t in canvas.get("todos", [])}
    panels = canvas.get("panels", {})
    assumptions = {a.get("id"): a for a in panels.get("assumptions", [])}
    plan = {p.get("id"): p for p in panels.get("validation", {}).get("plan", [])}

    for path, f in fields:
        if f.get("status") != "gap":
            continue
        if f.get("gap_type") == "decision":
            if strict and not canvas.get("gaps_accepted"):
                report.error("DECISION_GAP", path,
                             "coach mode: an open decision blocks the final render unless the PM "
                             "accepts the remaining gaps")
            continue
        todo = todos.get(f.get("todo"))
        if not todo or todo.get("field") != path:
            report.either(strict, "GAP_WITHOUT_TODO", path,
                          "an evidence GAP has a to-do that gathers it (to-do.field == this path)")
        elif todo.get("intake_route") != "reops":
            report.warn("INTAKE_ROUTE", path, "evidence to-dos currently route through ReOps intake")
        named = [a for a in assumptions.values() if a.get("from_gap") == path]
        if not named:
            report.either(strict, "GAP_WITHOUT_ASSUMPTION", path,
                          "an evidence GAP becomes a panel-5 assumption (from_gap == this path)")
        for assumption in named:
            retired = [plan[i] for i in assumption.get("retired_by", []) if i in plan]
            if not retired:
                report.either(strict, "ASSUMPTION_NOT_RETIRED", f"assumption {assumption.get('id')}",
                              "the assumption is retired by a panel-6 validation plan item")

    for todo in todos.values():
        target = todo.get("field")
        match = next((f for p, f in fields if p == target), None)
        if match is None:
            report.error("TODO_ORPHANED", f"todo {todo.get('id')}", f"no field at {target!r}")
        elif todo.get("status") == "open" and match.get("status") != "gap":
            report.warn("TODO_STALE", f"todo {todo.get('id')}",
                        "its field is no longer a GAP — close the to-do")


def compute_metrics(panels: dict, report: Report) -> dict:
    out = {}
    metrics = panels.get("metrics", [])
    primaries = [m for m in metrics if m.get("primary")]
    if len(primaries) != 1:
        report.error("PRIMARY_METRIC", "panels.metrics", "exactly one metric is primary")
    outcomes = panels.get("hypothesis", {}).get("outcomes", [])
    if len(outcomes) > 3:
        report.error("TOO_MANY_OUTCOMES", "panels.hypothesis.outcomes", "at most three expected outcomes")
    ids = {m.get("id") for m in metrics}
    for ref in outcomes:
        if ref not in ids:
            report.error("UNKNOWN_METRIC", "panels.hypothesis.outcomes", f"no metric {ref!r}")
    if primaries and primaries[0].get("id") not in outcomes:
        report.error("PRIMARY_NOT_OUTCOME", "panels.hypothesis.outcomes",
                     "the primary metric is one of the expected outcomes")

    for index, m in enumerate(metrics):
        path = f"panels.metrics[{index}]"
        base, target = number(m.get("baseline")), number(m.get("target"))
        declared = number(m.get("target_change_pct"))
        direction = m.get("direction")
        entry = {"change_abs": None, "change_pct": None, "target": target, "target_derived": False,
                 "declared_pct": declared, "formula": None, "blocked_by": []}
        if target is None and declared is None:
            report.error("NO_TARGET", path, "a metric states a target — absolute or % change")
            entry["blocked_by"].append(f"{path}.target")
        if declared is not None:
            if direction == "decrease" and declared >= 0 or direction == "increase" and declared <= 0:
                report.error("DIRECTION", f"{path}.target_change_pct",
                             f"a {direction!r} metric's % change has the matching sign")
        if base is None:
            entry["blocked_by"].append(f"{path}.baseline")
        elif target is None and declared is not None:
            target = base * (1 + declared / 100)
            entry.update(target=round(target, 6), target_derived=True)
        if base is not None and target is not None:
            if base == 0:
                report.warn("ZERO_BASELINE", f"{path}.baseline", "percent change undefined on a zero baseline")
            else:
                change = target - base
                pct = change / base * 100
                entry.update(change_abs=round(change, 6), change_pct=round(pct, 2),
                             formula=f"({fmt(target)} - {fmt(base)}) / {fmt(base)}")
                if direction == "decrease" and change >= 0:
                    report.error("DIRECTION", path, "a 'decrease' target is below its baseline")
                if direction == "increase" and change <= 0:
                    report.error("DIRECTION", path, "an 'increase' target is above its baseline")
                if declared is not None and not entry["target_derived"] \
                        and abs(declared - entry["change_pct"]) > PCT_TOLERANCE:
                    report.error("TARGET_INCONSISTENT", f"{path}.target_change_pct",
                                 f"stated {fmt(declared)}% but {entry['formula']} = "
                                 f"{fmt(entry['change_pct'])}%")
        elif base is None and declared is not None:
            entry["formula"] = f"baseline GAP; target = baseline × (1 {'+' if declared >= 0 else '−'} {fmt(abs(declared))}%)"
        else:
            b = fmt(base) if base is not None else "GAP"
            t = fmt(target) if target is not None else "GAP"
            entry["formula"] = f"({t} - {b}) / {b}"
        out[m.get("id")] = entry
    return out


def compute_impact(canvas: dict, metrics: dict, report: Report) -> dict:
    panels, scale = canvas.get("panels", {}), canvas.get("footer", {}).get("scale")
    if not scale:
        return {}
    primary = next((m for m in panels.get("metrics", []) if m.get("primary")), None)
    entry = {"saving_per_unit": None, "result": None, "formula": None, "blocked_by": [],
             "result_unit": scale.get("result_unit"), "volume_unit": scale.get("volume_unit")}
    if primary is None:
        return entry
    change = metrics.get(primary.get("id"), {})
    if change.get("change_abs") is not None:
        entry["saving_per_unit"] = round(abs(change["change_abs"]), 6)
    else:
        entry["blocked_by"].extend(change.get("blocked_by", []))
    volume = number(scale.get("volume"))
    if volume is None:
        entry["blocked_by"].append("footer.scale.volume")
    factor = scale.get("per_unit_factor", 1)
    saving_s = fmt(entry["saving_per_unit"]) if entry["saving_per_unit"] is not None else "GAP"
    volume_s = fmt(volume) if volume is not None else "GAP"
    factor_s = factor_text(factor)
    entry["formula"] = f"{saving_s} × {volume_s}{factor_s}"
    if entry["saving_per_unit"] is not None and volume is not None:
        entry["result"] = round(entry["saving_per_unit"] * volume * factor, 2)

    stated_saving = scale.get("stated_saving_per_unit")
    if stated_saving is not None and entry["saving_per_unit"] is not None \
            and abs(stated_saving - entry["saving_per_unit"]) > 1e-9:
        base_v, target_v = number(primary.get("baseline")), change.get("target")
        report.error("SAVING_INCONSISTENT", "footer.scale.stated_saving_per_unit",
                     f"stated {fmt(stated_saving)} per unit, but the primary metric moves "
                     f"{fmt(base_v)} → {fmt(target_v)} = {fmt(entry['saving_per_unit'])}")
    stated = scale.get("stated_result")
    if stated is not None:
        if entry["result"] is None:
            report.error("IMPACT_UNSUPPORTED", "footer.scale.stated_result",
                         f"a result is stated but its inputs are GAPs: {entry['blocked_by']}")
        elif abs(stated - entry["result"]) > RESULT_TOLERANCE * max(abs(entry["result"]), 1e-9):
            report.error("IMPACT_INCONSISTENT", "footer.scale.stated_result",
                         f"stated {fmt(stated)} but {entry['formula']} = {fmt(entry['result'])}")
    return entry


def compute_evidence(canvas: dict, report: Report) -> dict:
    source, panels = canvas.get("source", {}), canvas.get("panels", {})
    rows = {r.get("provenance_reference"): r for r in source.get("evidence_refs", [])}
    as_of = parse_date(source.get("read_at")) or dt.date.today()
    aging_months = canvas.get("aging_months", DEFAULT_AGING_MONTHS)
    tiles = []
    for index, tile in enumerate(panels.get("evidence", {}).get("tiles", [])):
        path = f"panels.evidence.tiles[{index}]"
        refs = tile.get("refs", [])
        unknown = [r for r in refs if r not in rows]
        if unknown:
            report.error("REF_NOT_IN_GRAPH", path, f"tile cites references the graph did not return: {unknown}")
        dates = [parse_date(rows[r].get("occurred_at")) for r in refs if r in rows]
        dated = [d for d in dates if d]
        latest = max(dated) if dated else None
        aging = bool(latest and months_between(latest, as_of) > aging_months)
        tiles.append({
            "count": len(refs),
            "undated": len(dates) - len(dated),
            "earliest": min(dated).isoformat() if dated else None,
            "latest": latest.isoformat() if latest else None,
            "aging": aging,
        })
        if aging:
            report.warn("EVIDENCE_AGING", path,
                        f"newest evidence on this tile is {latest.isoformat()}, older than "
                        f"{aging_months} months — name it in open questions")
    all_dates = [parse_date(r.get("occurred_at")) for r in rows.values()]
    dated = [d for d in all_dates if d]
    all_aging = bool(dated) and all(months_between(d, as_of) > aging_months for d in dated)
    if all_aging:
        report.warn("ALL_EVIDENCE_AGING", "source.evidence_refs",
                    "every dated piece of evidence is aging — say so to the PM once")
    originating = source.get("originating_sources", [])
    single = len(originating) == 1 and len(rows) >= 1
    if single:
        report.warn("SINGLE_SOURCE", "source.originating_sources",
                    "all evidence traces to one originating source — breadth is one, whatever the count")

    voice = panels.get("evidence", {}).get("voice")
    excerpts = {e.get("provenance_reference"): e for e in source.get("excerpts", [])}
    if voice:
        ref = voice.get("provenance_reference")
        excerpt = excerpts.get(ref)
        if excerpt is None:
            report.error("QUOTE_WITHOUT_EXCERPT", "panels.evidence.voice",
                         "a quote comes from a get_evidence_text excerpt recorded in source.excerpts")
        elif voice.get("quote", "") not in excerpt.get("text", ""):
            report.error("QUOTE_NOT_VERBATIM", "panels.evidence.voice",
                         "the quote is a verbatim substring of the redacted excerpt")
        if not voice.get("approved_for_canvas"):
            report.either(canvas.get("stage") == "approved", "QUOTE_NOT_APPROVED",
                          "panels.evidence.voice", "the PM approves each quote before it goes on the canvas")
    for index, snap in enumerate(panels.get("problem", {}).get("snapshot", [])):
        if snap.get("ref") not in excerpts:
            report.error("SNAPSHOT_WITHOUT_EXCERPT", f"panels.problem.snapshot[{index}]",
                         "a current-state example is a real record the graph returned text for")
    return {"tiles": tiles, "evidence_refs": len(rows), "undated": len(all_dates) - len(dated),
            "originating_sources": len(originating), "single_source": single,
            "all_aging": all_aging, "as_of": as_of.isoformat(), "aging_months": aging_months}


def check_panels(canvas: dict, report: Report) -> None:
    panels = canvas.get("panels", {})
    strict = canvas.get("mode") == "coach"
    approved = canvas.get("stage") == "approved"
    personas = panels.get("problem", {}).get("personas", {})
    names = {p.get("name") for p in canvas.get("source", {}).get("personas", [])}
    if canvas.get("source", {}).get("kind") == "opportunity-engine" and personas.get("primary") not in names:
        report.warn("PERSONA_NOT_IN_GRAPH", "panels.problem.personas.primary",
                    "the primary persona is not one the graph returned — confirm it deliberately")
    if approved and not personas.get("locked"):
        report.error("PERSONAS_UNLOCKED", "panels.problem.personas", "personas are locked before approval")

    options = panels.get("options", [])
    if not 2 <= len(options) <= 3:
        report.either(strict, "OPTION_COUNT", "panels.options", "two or three genuinely different options")
    for index, option in enumerate(options):
        if not option.get("pros") or not option.get("cons"):
            report.either(strict, "OPTION_TRADEOFFS", f"panels.options[{index}]",
                          "every option names at least one pro and one con")
    recommended = panels.get("recommended_option")
    if recommended is not None and recommended not in {o.get("id") for o in options}:
        report.error("UNKNOWN_OPTION", "panels.recommended_option", f"no option {recommended!r}")

    for index, risk in enumerate(panels.get("risks", [])):
        if not risk.get("mitigation"):
            report.warn("RISK_UNMITIGATED", f"panels.risks[{index}]",
                        "recorded as unmitigated — say so plainly on the canvas")

    decision = panels.get("validation", {}).get("recommendation", {}).get("decision")
    if decision is not None and decision not in DECISIONS:
        report.error("DECISION_VALUE", "panels.validation.recommendation.decision",
                     f"one of {sorted(DECISIONS)} or null")
    if not canvas.get("open_questions"):
        report.warn("NO_OPEN_QUESTIONS", "open_questions",
                    "an empty gaps list usually means the canvas was not examined hard enough")
    if canvas.get("genai") and not panels.get("validation", {}).get("genai_criteria"):
        report.either(strict, "GENAI_CRITERIA", "panels.validation.genai_criteria",
                      "GenAI mode: panel 6 carries evaluation criteria that work under this "
                      "Initiative inherits")


def proceed_guard(canvas: dict, fields: list, report: Report) -> dict:
    panels = canvas.get("panels", {})
    primary = next((m for m in panels.get("metrics", []) if m.get("primary")), None)
    blocked = []
    if primary is not None:
        baseline = primary.get("baseline")
        if not is_field(baseline) or baseline.get("status") == "gap":
            blocked.append("the primary metric's baseline is a GAP")
    decision = panels.get("validation", {}).get("recommendation", {}).get("decision")
    if decision == "proceed" and blocked:
        report.error("PROCEED_BLOCKED", "panels.validation.recommendation.decision",
                     "Proceed is unavailable: " + "; ".join(blocked))
    gaps = {"evidence": 0, "decision": 0}
    for _, f in fields:
        if f.get("status") == "gap" and f.get("gap_type") in gaps:
            gaps[f["gap_type"]] += 1
    return {"proceed_available": not blocked, "proceed_blocked_by": blocked,
            "aipos_decision": DECISIONS.get(decision), "gaps": gaps}


# ----------------------------------------------------------------------------- entry


def verify(canvas: dict) -> tuple[Report, dict]:
    report = Report()
    check_top(canvas, report)
    source = canvas.get("source", {}) if isinstance(canvas.get("source"), dict) else {}
    check_source(source, report)
    graph_refs = {r.get("provenance_reference") for r in source.get("evidence_refs", [])}
    fields = check_fields(canvas, graph_refs, report)
    check_gap_wiring(canvas, fields, report)
    check_panels(canvas, report)
    metrics = compute_metrics(canvas.get("panels", {}), report)
    computed = {
        "metrics": metrics,
        "impact_at_scale": compute_impact(canvas, metrics, report),
        "evidence": compute_evidence(canvas, report),
        **proceed_guard(canvas, fields, report),
    }
    return report, computed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("canvas", type=Path)
    parser.add_argument("--write", action="store_true", help="write the computed block back")
    args = parser.parse_args(argv)
    canvas = json.loads(args.canvas.read_text(encoding="utf-8"))
    report, computed = verify(canvas)
    if args.write:
        canvas["computed"] = computed
        args.canvas.write_text(json.dumps(canvas, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    json.dump({"ok": not report.errors, "errors": report.errors, "warnings": report.warnings,
               "computed": computed}, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
