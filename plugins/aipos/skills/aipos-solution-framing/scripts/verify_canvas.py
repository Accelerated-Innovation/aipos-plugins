#!/usr/bin/env python3
"""Check a Solution Framing canvas and compute every number the canvas displays.

The canvas is a shareable one-page artifact, so its numbers get quoted. This script is the
reason they can be: nothing on the rendered canvas is typed by hand if it can be derived.
Percent changes, derived targets, per-unit savings, impact at scale, evidence counts, date
ranges and aging are computed here from the canvas's own inputs and the graph read it records;
a stated figure that disagrees with the computed one is an error, not a style note.

It also enforces the provenance contract (references/canvas-schema.md):

  * every content position holds a field of the right kind — facts where the world is
    described, decisions where the PM authors — so nothing escapes the checks by its shape
  * facts carry a provenance mark; an `[E]` fact cites references the graph returned; on an
    engine-sourced canvas an `[I]` fact's basis is graph references, not a note
  * a missing fact is an evidence GAP, wired through the canvas: a to-do that gathers it, a
    panel-5 assumption that names it, and a panel-6 plan item that retires it
  * Proceed is available only when the primary metric's baseline is graph-backed
  * quotes and current-state examples are verbatim graph excerpts the PM approved

It reports; it never crashes. Malformed input becomes a MALFORMED or type error.

Usage:
  verify_canvas.py canvas.json            # report only (JSON to stdout); exit 1 on errors
  verify_canvas.py canvas.json --write    # also write the `computed` block back into the file

Standard library only.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

CANVAS_VERSION = 1
SUPPORTED_GRAPH_SCHEMA = 1
DEFAULT_AGING_MONTHS = 18
EXCERPT_CAP = 5
PCT_TOLERANCE = 0.5          # percentage points
RESULT_TOLERANCE = 0.01      # 1% relative

MARKS = {"E", "I", "T", "A"}
FINAL_PANEL = 8          # 1–6 panels, 7 footer, 8 review: the canvas is complete


def through(canvas: dict) -> int:
    """How far the facilitation has got. Checks for later panels wait until they are reached,
    so running the verifier after panel 1 does not report panel 6 as missing."""
    value = canvas.get("through_panel", FINAL_PANEL)
    return value if isinstance(value, int) and not isinstance(value, bool) else FINAL_PANEL
STATUSES = {"confirmed", "provisional", "gap"}
GAP_TYPES = {"evidence", "decision"}
DECISIONS = {"proceed": "go", "pivot": "revise", "park": "no-go"}
CHANGE_KINDS = {"relative", "points"}

#: Metric unit -> hours, for checking an impact-at-scale conversion factor.
TO_HOURS = {"sec": 1 / 3600, "secs": 1 / 3600, "second": 1 / 3600, "seconds": 1 / 3600, "s": 1 / 3600,
            "min": 1 / 60, "mins": 1 / 60, "minute": 1 / 60, "minutes": 1 / 60,
            "hour": 1, "hours": 1, "hr": 1, "hrs": 1, "h": 1, "day": 24, "days": 24}


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


def D(node: object) -> dict:
    return node if isinstance(node, dict) else {}


def L(node: object) -> list:
    return node if isinstance(node, list) else []


def is_field(node: object) -> bool:
    return isinstance(node, dict) and node.get("kind") in {"fact", "decision"} and "status" in node


def is_num(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


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


def present(field: object) -> bool:
    return is_field(field) and field.get("status") != "gap"


def number(field: object) -> float | None:
    """A field's numeric value, or None when it is a GAP, absent or not numeric."""
    if not present(field):
        return None
    value = field.get("value")
    return float(value) if is_num(value) else None


def graph_backed(field: object, graph_refs: set) -> bool:
    """Evidence a decision may rest on: an [E] fact, or an [I] fact whose basis is graph refs.

    A transcribed [T] fact is not graph-backed: a person keyed it in from a record the graph
    links. It is traceable and it computes, but Proceed waits for the graph to carry the value."""
    if not present(field) or field.get("kind") != "fact":
        return False
    refs = L(field.get("refs"))
    return field.get("mark") in {"E", "I"} and bool(refs) and all(r in graph_refs for r in refs)


def parse_date(value: object) -> dt.date | None:
    if not isinstance(value, str) or not value:
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


def is_percent_unit(unit: object) -> bool:
    return isinstance(unit, str) and "%" in unit


# ----------------------------------------------------------------------------- positions


def positions(canvas: dict):
    """Every place the contract puts content, with the kind of field it must hold.

    Yields (path, node, kind, required, panel). Checking by position — not by discovering dicts that
    look like fields — is what stops a plain string or a status-less dict slipping past."""
    panels = D(canvas.get("panels"))
    problem, evidence = D(panels.get("problem")), D(panels.get("evidence"))
    hypothesis, validation = D(panels.get("hypothesis")), D(panels.get("validation"))
    footer = D(canvas.get("footer"))
    yield "title", canvas.get("title"), "decision", True, 0
    yield "goal", canvas.get("goal"), "decision", True, 0
    for i, node in enumerate(L(problem.get("pain_points"))):
        yield f"panels.problem.pain_points[{i}]", node, "fact", True, 1
    for i, node in enumerate(L(problem.get("impact"))):
        yield f"panels.problem.impact[{i}]", node, "fact", True, 1
    for key in ("problem", "affects", "resulting_in", "benefits"):
        yield f"panels.problem.statement.{key}", D(problem.get("statement")).get(key), "decision", True, 1
    for i, tile in enumerate(L(evidence.get("tiles"))):
        yield f"panels.evidence.tiles[{i}].finding", D(tile).get("finding"), "fact", True, 2
    for key in ("if", "then", "without"):
        yield f"panels.hypothesis.{key}", hypothesis.get(key), "decision", True, 3
    for i, metric in enumerate(L(panels.get("metrics"))):
        metric = D(metric)
        yield f"panels.metrics[{i}].baseline", metric.get("baseline"), "fact", True, 3
        yield f"panels.metrics[{i}].target", metric.get("target"), "decision", False, 3
        yield f"panels.metrics[{i}].target_change_pct", metric.get("target_change_pct"), "decision", False, 3
        yield f"panels.metrics[{i}].observation", metric.get("observation"), "decision", True, 3
    for i, option in enumerate(L(panels.get("options"))):
        yield f"panels.options[{i}].approach", D(option).get("approach"), "decision", True, 4
    for i, item in enumerate(L(validation.get("plan"))):
        yield f"panels.validation.plan[{i}].owner", D(item).get("owner"), "decision", True, 6
    recommendation = D(validation.get("recommendation"))
    yield ("panels.validation.recommendation.owner", recommendation.get("owner"), "decision",
           recommendation.get("decision") is not None, 6)
    yield "footer.success", footer.get("success"), "decision", True, 7
    if footer.get("scale") is not None:
        yield "footer.scale.volume", D(footer.get("scale")).get("volume"), "fact", True, 7


NUMERIC_POSITIONS = re.compile(r"(baseline|target|target_change_pct|scale\.volume)$")
PROSE_POSITIONS = re.compile(r"^(title|goal|footer\.success|panels\.problem\.statement\..+|panels\.hypothesis\..+)$")


def check_positions(canvas: dict, report: Report) -> None:
    reached = through(canvas)
    for path, node, kind, required, panel_no in positions(canvas):
        if node is None:
            if required and panel_no <= reached:
                report.error("MISSING", path, f"a {kind} field is required here")
            continue
        if not is_field(node):
            report.error("NOT_A_FIELD", path,
                         f"content here is a {kind} field object ({{kind, status, value…}}), "
                         f"not a bare {type(node).__name__}")
            continue
        if node.get("kind") != kind:
            report.error("WRONG_KIND", path,
                         f"this position holds a {kind}"
                         + (" — the world as the graph shows it, not an authored value"
                            if kind == "fact" else " — authored by the PM, not evidenced"))
        if NUMERIC_POSITIONS.search(path) and present(node) and not is_num(node.get("value")):
            report.error("NOT_NUMERIC", path, f"expected a number, got {node.get('value')!r}")
        if PROSE_POSITIONS.match(path) and present(node) and isinstance(node.get("value"), str) \
                and re.search(r"\d", node["value"]):
            report.warn("NUMBER_IN_PROSE", path,
                        "a number in prose is never checked — put it in a metric, where it is computed")


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
    reached = canvas.get("through_panel", FINAL_PANEL)
    if not isinstance(reached, int) or isinstance(reached, bool) or not 0 <= reached <= FINAL_PANEL:
        report.error("MALFORMED", "through_panel", f"an integer 0–{FINAL_PANEL}")
    elif canvas.get("stage") == "approved" and reached < FINAL_PANEL:
        report.error("INCOMPLETE_AT_APPROVAL", "through_panel",
                     "a canvas is approved only after review (through_panel 8)")
    for key in ("todos", "open_questions"):
        if key in canvas and not isinstance(canvas[key], list):
            report.error("MALFORMED", key, f"'{key}' is a list")


def check_source(source: dict, report: Report) -> None:
    kind = source.get("kind")
    if kind not in {"opportunity-engine", "pm-interview"}:
        report.error("SOURCE_KIND", "source.kind", "kind must be 'opportunity-engine' or 'pm-interview'")
    for key in ("evidence_refs", "originating_sources", "excerpts", "personas"):
        if key in source and not isinstance(source[key], list):
            report.error("MALFORMED", f"source.{key}", "must be a list")
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
    if kind == "pm-interview" and L(source.get("evidence_refs")):
        report.error("SOURCE_KIND", "source.evidence_refs",
                     "a pm-interview canvas holds no graph references; set kind to opportunity-engine")
    refs = {D(r).get("provenance_reference") for r in L(source.get("evidence_refs"))}
    excerpts = L(source.get("excerpts"))
    for index, excerpt in enumerate(excerpts):
        if D(excerpt).get("provenance_reference") not in refs:
            report.error("EXCERPT_NOT_IN_GRAPH", f"source.excerpts[{index}]",
                         "an excerpt is for a reference this problem's evidence holds")
    if len(excerpts) > EXCERPT_CAP:
        report.warn("EXCERPT_CAP", "source.excerpts",
                    f"{len(excerpts)} excerpts read; evidence text is access-logged — "
                    f"fetch only what a panel needs (default cap {EXCERPT_CAP})")


def check_fields(canvas: dict, graph_refs: set, report: Report) -> list:
    """Field-level provenance. Returns the list of (path, field) for later checks."""
    engine = D(canvas.get("source")).get("kind") == "opportunity-engine"
    approved = canvas.get("stage") == "approved"
    # Where each graph reference can be read by a person. Transcription needs somewhere to read
    # from: a record the graph returned without a record_url can only be brought into the graph.
    record_urls = {D(r).get("provenance_reference"): D(r).get("record_url")
                   for r in L(D(canvas.get("source")).get("evidence_refs"))}
    fields = list(walk_fields(canvas))
    for path, f in fields:
        status, kind, mark = f.get("status"), f.get("kind"), f.get("mark")
        refs = L(f.get("refs"))
        if status not in STATUSES:
            report.error("FIELD_STATUS", path, f"status must be one of {sorted(STATUSES)}")
            continue
        if status == "provisional" and approved:
            report.error("PROVISIONAL_AT_APPROVAL", path,
                         "confirm or change this before approving — the canvas shows it as settled")
        if status == "gap":
            if f.get("value") is not None:
                report.error("GAP_HAS_VALUE", path,
                             "a GAP carries no value; a PM's remembered figure goes in 'assumed'")
            if f.get("gap_type") not in GAP_TYPES:
                report.error("GAP_TYPE", path, "a GAP is typed 'evidence' or 'decision'")
            elif kind == "fact" and f.get("gap_type") != "evidence":
                report.error("GAP_TYPE", path, "a missing fact is an evidence GAP — it is gathered, not decided")
            elif kind == "decision" and f.get("gap_type") != "decision":
                report.error("GAP_TYPE", path, "a missing decision is a decision GAP")
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
        if mark not in MARKS:
            report.error("FACT_UNMARKED", path, "every fact carries [E], [I] or [A]")
            continue
        if mark == "A":
            report.error("FACT_ASSUMED", path,
                         "an assumption is not a fact: make this an evidence GAP and keep the "
                         "figure in 'assumed'")
            continue
        if mark == "T":
            if not refs or not f.get("note"):
                report.error("T_WITHOUT_RECORD", path,
                             "a transcribed [T] fact cites the graph record it was read from and "
                             "notes who read it, from which record_url, when")
            unreadable = [r for r in refs if r in record_urls and not record_urls[r]]
            if unreadable:
                report.error("T_WITHOUT_URL", path,
                             f"transcribed from {unreadable}, which the graph returned with no "
                             "record_url — there is nothing to read it from, so it stays a GAP")
        missing = [r for r in refs if r not in graph_refs]
        if missing:
            report.error("REF_NOT_IN_GRAPH", path, f"references not returned by the graph read: {missing}")
        if mark == "E" and not refs:
            report.error("E_WITHOUT_REF", path, "an [E] fact cites the graph references behind it")
        if mark == "I":
            if engine and not refs:
                report.error("I_WITHOUT_BASIS", path,
                             "on an engine-sourced canvas an [I] fact is inferred from graph "
                             "references — a note alone is the PM's word, which is a GAP")
            elif not refs and not f.get("note"):
                report.error("I_WITHOUT_BASIS", path, "an [I] fact names its basis (refs or a note)")
    return fields


def check_gap_wiring(canvas: dict, fields: list, report: Report) -> None:
    strict = canvas.get("mode") == "coach"
    reached = through(canvas)
    panels = D(canvas.get("panels"))
    todos = {D(t).get("id"): D(t) for t in L(canvas.get("todos"))}
    assumptions = {D(a).get("id"): D(a) for a in L(panels.get("assumptions"))}
    plan = {D(p).get("id"): D(p) for p in L(D(panels.get("validation")).get("plan"))}

    for path, f in fields:
        if f.get("status") != "gap":
            continue
        if f.get("gap_type") == "decision":
            if strict and reached >= FINAL_PANEL and not canvas.get("gaps_accepted"):
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
        if not named and reached >= 5:
            report.either(strict, "GAP_WITHOUT_ASSUMPTION", path,
                          "an evidence GAP becomes a panel-5 assumption (from_gap == this path)")
        for assumption in named if reached >= 6 else []:
            retiring = {i for i in L(assumption.get("retired_by")) if i in plan}
            retiring |= {pid for pid, item in plan.items() if assumption.get("id") in L(item.get("retires"))}
            if not retiring:
                report.either(strict, "ASSUMPTION_NOT_RETIRED", f"assumption {assumption.get('id')}",
                              "the assumption is retired by a panel-6 validation plan item")

    by_path = dict(fields)
    open_todos = [t for t in todos.values() if t.get("status") == "open"]
    for todo in todos.values():
        target = todo.get("field")
        match = by_path.get(target)
        if match is None:
            report.error("TODO_ORPHANED", f"todo {todo.get('id')}", f"no field at {target!r}")
        elif todo.get("status") == "open" and match.get("status") != "gap":
            report.warn("TODO_STALE", f"todo {todo.get('id')}",
                        "its field is no longer a GAP — close the to-do")
    primary_index = next((i for i, m in enumerate(L(panels.get("metrics"))) if D(m).get("primary")), None)
    if primary_index is not None and open_todos:
        primary_path = f"panels.metrics[{primary_index}].baseline"
        if any(t.get("field") == primary_path for t in open_todos) and open_todos[0].get("field") != primary_path:
            report.warn("TODO_ORDER", "todos",
                        "the primary metric's baseline blocks the decision — its to-do goes first")


def compute_metrics(canvas: dict, report: Report) -> dict:
    panels = D(canvas.get("panels"))
    strict = canvas.get("mode") == "coach"
    out = {}
    metrics = [D(m) for m in L(panels.get("metrics"))]
    primaries = [m for m in metrics if m.get("primary")]
    if through(canvas) < 3 and not metrics:
        return out
    if len(primaries) != 1:
        report.error("PRIMARY_METRIC", "panels.metrics", "exactly one metric is primary")
    outcomes = L(D(panels.get("hypothesis")).get("outcomes"))
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
        direction, unit = m.get("direction"), m.get("unit")
        change_kind = m.get("target_change_kind", "relative")
        entry = {"change_abs": None, "change_pct": None, "target": target, "target_derived": False,
                 "declared_pct": declared, "change_kind": change_kind, "formula": None, "blocked_by": []}
        if direction not in {"decrease", "increase"}:
            report.error("DIRECTION", path, "direction is 'decrease' or 'increase'")
        if target is None and declared is None:
            report.error("NO_TARGET", path, "a metric states a target — absolute or % change")
            entry["blocked_by"].append(f"{path}.target")
        if declared is not None:
            if change_kind not in CHANGE_KINDS:
                report.error("PCT_KIND", f"{path}.target_change_kind", "'relative' or 'points'")
            elif is_percent_unit(unit) and "target_change_kind" not in m:
                report.either(strict, "PCT_KIND", f"{path}.target_change_kind",
                              "on a % metric, say whether the change is relative or percentage "
                              "points — +20% of 60% is 72%, +20 points is 80%")
            if direction == "decrease" and declared >= 0 or direction == "increase" and declared <= 0:
                report.error("DIRECTION", f"{path}.target_change_pct",
                             f"a {direction!r} metric's % change has the matching sign")
        if base is None:
            entry["blocked_by"].append(f"{path}.baseline")
        elif target is None and declared is not None:
            target = base + declared if change_kind == "points" else base * (1 + declared / 100)
            entry.update(target=round(target, 6), target_derived=True)

        if base is not None and target is not None:
            change = target - base
            entry["change_abs"] = round(change, 6)
            if direction == "decrease" and change >= 0:
                report.error("DIRECTION", path, "a 'decrease' target is below its baseline")
            if direction == "increase" and change <= 0:
                report.error("DIRECTION", path, "an 'increase' target is above its baseline")
            if base == 0:
                report.warn("ZERO_BASELINE", f"{path}.baseline", "percent change undefined on a zero baseline")
                entry["formula"] = f"{fmt(target)} - {fmt(base)}"
            else:
                pct = change / abs(base) * 100
                entry.update(change_pct=round(pct, 2),
                             formula=f"({fmt(target)} - {fmt(base)}) / {fmt(abs(base))}")
            if declared is not None and not entry["target_derived"]:
                if change_kind == "points":
                    if abs(declared - change) > PCT_TOLERANCE:
                        report.error("TARGET_INCONSISTENT", f"{path}.target_change_pct",
                                     f"stated {fmt(declared)} points but {fmt(target)} - {fmt(base)} "
                                     f"= {fmt(change)}")
                elif entry["change_pct"] is not None and abs(declared - entry["change_pct"]) > PCT_TOLERANCE:
                    report.error("TARGET_INCONSISTENT", f"{path}.target_change_pct",
                                 f"stated {fmt(declared)}% but {entry['formula']} = "
                                 f"{fmt(entry['change_pct'])}%")
            if is_percent_unit(unit) and not 0 <= target <= 100:
                report.error("OUT_OF_RANGE", path, f"a percentage target of {fmt(target)} is outside 0–100")
        elif base is None and declared is not None:
            sign = "+" if declared >= 0 else "−"
            how = f"baseline {sign} {fmt(abs(declared))} points" if change_kind == "points" \
                else f"baseline × (1 {sign} {fmt(abs(declared))}%)"
            entry["formula"] = f"baseline GAP; target = {how}"
        else:
            b = fmt(base) if base is not None else "GAP"
            t = fmt(target) if target is not None else "GAP"
            entry["formula"] = f"({t} - {b}) / {b}"
        out[m.get("id")] = entry
    return out


def compute_impact(canvas: dict, metrics: dict, report: Report) -> dict:
    panels, scale = D(canvas.get("panels")), D(canvas.get("footer")).get("scale")
    if scale is None:
        return {}
    if not isinstance(scale, dict):
        report.error("MALFORMED", "footer.scale", "scale is an object")
        return {}
    primary = next((D(m) for m in L(panels.get("metrics")) if D(m).get("primary")), None)
    entry = {"saving_per_unit": None, "result": None, "formula": None, "blocked_by": [],
             "result_unit": scale.get("result_unit"), "volume_unit": scale.get("volume_unit"),
             "per_unit_factor": None}
    if primary is None:
        return entry
    if is_percent_unit(primary.get("unit")):
        report.error("IMPACT_UNIT", "footer.scale",
                     "impact at scale multiplies a per-unit saving by volume; the primary metric is "
                     "a percentage, so there is no per-unit saving to multiply")
        return entry
    unit = str(primary.get("unit", "")).strip().lower()
    result_unit = str(scale.get("result_unit", "")).strip().lower()
    to_hours = "hour" in result_unit or result_unit.startswith("hr")
    factor = scale.get("per_unit_factor")
    if factor is None:
        if unit in TO_HOURS and to_hours:
            factor = TO_HOURS[unit]
        else:
            factor = 1
            if unit and result_unit:
                report.warn("FACTOR_ASSUMED", "footer.scale.per_unit_factor",
                            f"no conversion given from {primary.get('unit')} to "
                            f"{scale.get('result_unit')}; assuming 1")
    if not is_num(factor) or factor <= 0:
        report.error("FACTOR_INVALID", "footer.scale.per_unit_factor",
                     f"a positive number (e.g. 1/60 as 0.016666…), got {factor!r}")
        return entry
    if unit in TO_HOURS and to_hours:
        expected = TO_HOURS[unit]
        if abs(factor - expected) > 1e-9 * max(expected, 1):
            report.error("FACTOR_MISMATCH", "footer.scale.per_unit_factor",
                         f"{primary.get('unit')} → {scale.get('result_unit')} converts by "
                         f"{factor_text(expected).strip() or '× 1'}, not {factor_text(factor).strip() or '× 1'}")

    entry["per_unit_factor"] = factor
    change = metrics.get(primary.get("id"), {})
    if change.get("change_abs") is not None:
        entry["saving_per_unit"] = round(abs(change["change_abs"]), 6)
    else:
        entry["blocked_by"].extend(change.get("blocked_by", []))
    volume = number(scale.get("volume"))
    if volume is None:
        entry["blocked_by"].append("footer.scale.volume")
    saving_s = fmt(entry["saving_per_unit"]) if entry["saving_per_unit"] is not None else "GAP"
    volume_s = fmt(volume) if volume is not None else "GAP"
    entry["formula"] = f"{saving_s} × {volume_s}{factor_text(factor)}"
    if entry["saving_per_unit"] is not None and volume is not None:
        entry["result"] = round(entry["saving_per_unit"] * volume * factor, 2)

    stated_saving = scale.get("stated_saving_per_unit")
    if is_num(stated_saving) and entry["saving_per_unit"] is not None \
            and abs(stated_saving - entry["saving_per_unit"]) > 1e-9:
        report.error("SAVING_INCONSISTENT", "footer.scale.stated_saving_per_unit",
                     f"stated {fmt(stated_saving)} per unit, but the primary metric moves "
                     f"{fmt(number(primary.get('baseline')))} → {fmt(change['target'])} = "
                     f"{fmt(entry['saving_per_unit'])}")
    stated = scale.get("stated_result")
    if is_num(stated):
        if entry["result"] is None:
            report.error("IMPACT_UNSUPPORTED", "footer.scale.stated_result",
                         f"a result is stated but its inputs are GAPs: {entry['blocked_by']}")
        elif abs(stated - entry["result"]) > RESULT_TOLERANCE * max(abs(entry["result"]), 1e-9):
            report.error("IMPACT_INCONSISTENT", "footer.scale.stated_result",
                         f"stated {fmt(stated)} but {entry['formula']} = {fmt(entry['result'])}")
    return entry


def compute_evidence(canvas: dict, report: Report) -> dict:
    source, panels = D(canvas.get("source")), D(canvas.get("panels"))
    approved = canvas.get("stage") == "approved"
    rows = {D(r).get("provenance_reference"): D(r) for r in L(source.get("evidence_refs"))}
    as_of = parse_date(source.get("read_at")) or dt.date.today()
    aging_months = canvas.get("aging_months", DEFAULT_AGING_MONTHS)
    if not is_num(aging_months) or aging_months <= 0:
        report.error("MALFORMED", "aging_months", "a positive number of months")
        aging_months = DEFAULT_AGING_MONTHS
    tiles = []
    for index, tile in enumerate(L(D(panels.get("evidence")).get("tiles"))):
        path = f"panels.evidence.tiles[{index}]"
        listed = [r for r in L(D(tile).get("refs")) if isinstance(r, str)]
        refs = list(dict.fromkeys(listed))
        if len(refs) != len(listed):
            report.warn("DUPLICATE_REF", path, "a reference listed twice is counted once")
        unknown = [r for r in refs if r not in rows]
        if unknown:
            report.error("REF_NOT_IN_GRAPH", path, f"tile cites references the graph did not return: {unknown}")
        dates = [parse_date(rows[r].get("occurred_at")) for r in refs if r in rows]
        dated = [d for d in dates if d]
        latest = max(dated) if dated else None
        aging = bool(latest and months_between(latest, as_of) > aging_months)
        tiles.append({"count": len(refs), "undated": len(dates) - len(dated),
                      "earliest": min(dated).isoformat() if dated else None,
                      "latest": latest.isoformat() if latest else None, "aging": aging})
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
    originating = L(source.get("originating_sources"))
    single = len(set(originating)) == 1 and len(rows) >= 1
    if single:
        report.warn("SINGLE_SOURCE", "source.originating_sources",
                    "all evidence traces to one originating source — breadth is one, whatever the count")

    excerpts = {D(e).get("provenance_reference"): D(e) for e in L(source.get("excerpts"))}
    evidence = D(panels.get("evidence"))
    voice = evidence.get("voice")
    if voice is not None:
        voice = D(voice)
        ref, quote = voice.get("provenance_reference"), voice.get("quote")
        excerpt = excerpts.get(ref)
        if not isinstance(quote, str) or len(quote.strip()) < 3:
            report.error("QUOTE_EMPTY", "panels.evidence.voice", "a quote has words in it")
        elif excerpt is None:
            report.error("QUOTE_WITHOUT_EXCERPT", "panels.evidence.voice",
                         "a quote comes from a get_evidence_text excerpt recorded in source.excerpts")
        elif quote not in str(excerpt.get("text", "")):
            report.error("QUOTE_NOT_VERBATIM", "panels.evidence.voice",
                         "the quote is a verbatim substring of the redacted excerpt")
        if voice.get("speaker_role"):
            report.warn("SPEAKER_UNSOURCED", "panels.evidence.voice.speaker_role",
                        "the graph does not attribute a speaker's role — attribute the quote to its "
                        "source and date instead")
        if not voice.get("approved_for_canvas"):
            report.either(approved, "QUOTE_NOT_APPROVED", "panels.evidence.voice",
                          "the PM approves each quote before it goes on the canvas")
    for index, snap in enumerate(L(D(panels.get("problem")).get("snapshot"))):
        snap, path = D(snap), f"panels.problem.snapshot[{index}]"
        if snap.get("ref") not in excerpts:
            report.error("SNAPSHOT_WITHOUT_EXCERPT", path,
                         "a current-state example is a real record the graph returned text for")
        if not snap.get("approved_for_canvas"):
            report.either(approved, "SNAPSHOT_NOT_APPROVED", path,
                          "the PM approves each real record shown on a shareable canvas")
    return {"tiles": tiles, "evidence_refs": len(rows), "undated": len(all_dates) - len(dated),
            "originating_sources": len(set(originating)), "single_source": single,
            "all_aging": all_aging, "as_of": as_of.isoformat(), "aging_months": aging_months}


def check_panels(canvas: dict, report: Report) -> None:
    panels = D(canvas.get("panels"))
    strict = canvas.get("mode") == "coach"
    approved = canvas.get("stage") == "approved"
    source = D(canvas.get("source"))
    personas = D(D(panels.get("problem")).get("personas"))
    names = {D(p).get("name") for p in L(source.get("personas"))}
    if source.get("kind") == "opportunity-engine" and personas.get("primary") not in names:
        report.warn("PERSONA_NOT_IN_GRAPH", "panels.problem.personas.primary",
                    "the primary persona is not one the graph returned — confirm it deliberately")
    if approved and not personas.get("locked"):
        report.error("PERSONAS_UNLOCKED", "panels.problem.personas", "personas are locked before approval")

    reached = through(canvas)
    options = [D(o) for o in L(panels.get("options"))]
    if reached >= 4 and not 2 <= len(options) <= 3:
        report.either(strict, "OPTION_COUNT", "panels.options", "two or three genuinely different options")
    for index, option in enumerate(options if reached >= 4 else []):
        if not L(option.get("pros")) or not L(option.get("cons")):
            report.either(strict, "OPTION_TRADEOFFS", f"panels.options[{index}]",
                          "every option names at least one pro and one con")
    recommended = panels.get("recommended_option")
    if recommended is not None and recommended not in {o.get("id") for o in options}:
        report.error("UNKNOWN_OPTION", "panels.recommended_option", f"no option {recommended!r}")

    for index, risk in enumerate(L(panels.get("risks"))):
        if not D(risk).get("mitigation"):
            report.warn("RISK_UNMITIGATED", f"panels.risks[{index}]",
                        "recorded as unmitigated — say so plainly on the canvas")

    recommendation = D(D(panels.get("validation")).get("recommendation"))
    decision = recommendation.get("decision")
    if decision is not None and decision not in DECISIONS:
        report.error("DECISION_VALUE", "panels.validation.recommendation.decision",
                     f"one of {sorted(DECISIONS)} or null")
    if decision is not None and not present(recommendation.get("owner")):
        report.error("OWNER_MISSING", "panels.validation.recommendation.owner",
                     "a recommendation names who makes the decision")
    if reached >= FINAL_PANEL and not L(canvas.get("open_questions")):
        report.warn("NO_OPEN_QUESTIONS", "open_questions",
                    "an empty gaps list usually means the canvas was not examined hard enough")
    if reached >= 6 and canvas.get("genai") and not L(D(panels.get("validation")).get("genai_criteria")):
        report.either(strict, "GENAI_CRITERIA", "panels.validation.genai_criteria",
                      "GenAI mode: panel 6 carries evaluation criteria that work under this "
                      "Initiative inherits")


def proceed_guard(canvas: dict, fields: list, graph_refs: set, report: Report) -> dict:
    panels = D(canvas.get("panels"))
    primary = next((D(m) for m in L(panels.get("metrics")) if D(m).get("primary")), None)
    blocked = []
    if primary is None:
        blocked.append("there is no primary metric")
    else:
        baseline = primary.get("baseline")
        if not present(baseline):
            blocked.append("the primary metric's baseline is a GAP")
        elif not graph_backed(baseline, graph_refs):
            blocked.append("the primary metric's baseline is not backed by the graph")
    decision = D(D(panels.get("validation")).get("recommendation")).get("decision")
    if decision == "proceed" and blocked:
        report.error("PROCEED_BLOCKED", "panels.validation.recommendation.decision",
                     "Proceed is unavailable: " + "; ".join(blocked))
    gaps = {"evidence": 0, "decision": 0}
    for _, f in fields:
        if f.get("status") == "gap" and f.get("gap_type") in gaps:
            gaps[f["gap_type"]] += 1
    return {"through_panel": through(canvas), "proceed_available": not blocked, "proceed_blocked_by": blocked,
            "aipos_decision": DECISIONS.get(decision), "gaps": gaps}


# ----------------------------------------------------------------------------- entry


def verify(canvas: object) -> tuple[Report, dict]:
    report = Report()
    if not isinstance(canvas, dict):
        report.error("MALFORMED", "", "a canvas is a JSON object")
        return report, {}
    computed: dict = {}

    def stage(name, fn, *args):
        """Run one check; a crash on malformed input becomes a reported error, never a traceback."""
        try:
            return fn(*args)
        except Exception as exc:  # noqa: BLE001 - reporting is the contract
            report.error("MALFORMED", name, f"could not check ({type(exc).__name__}: {exc})")
            return None

    stage("top", check_top, canvas, report)
    source = D(canvas.get("source"))
    stage("source", check_source, source, report)
    graph_refs = {D(r).get("provenance_reference") for r in L(source.get("evidence_refs"))}
    stage("positions", check_positions, canvas, report)
    fields = stage("fields", check_fields, canvas, graph_refs, report) or []
    stage("gaps", check_gap_wiring, canvas, fields, report)
    stage("panels", check_panels, canvas, report)
    metrics = stage("metrics", compute_metrics, canvas, report) or {}
    computed["metrics"] = metrics
    computed["impact_at_scale"] = stage("impact", compute_impact, canvas, metrics, report) or {}
    computed["evidence"] = stage("evidence", compute_evidence, canvas, report) or {}
    computed.update(stage("decision", proceed_guard, canvas, fields, graph_refs, report) or {})
    return report, computed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("canvas", type=Path)
    parser.add_argument("--write", action="store_true", help="write the computed block back")
    args = parser.parse_args(argv)
    try:
        canvas = json.loads(args.canvas.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        json.dump({"ok": False, "errors": [{"code": "MALFORMED", "path": "",
                                            "message": f"cannot read canvas: {exc}"}],
                   "warnings": [], "computed": {}}, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 1
    report, computed = verify(canvas)
    if args.write and isinstance(canvas, dict):
        canvas["computed"] = computed
        args.canvas.write_text(json.dumps(canvas, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    json.dump({"ok": not report.errors, "errors": report.errors, "warnings": report.warnings,
               "computed": computed}, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
