#!/usr/bin/env python3
"""Check an agent contract's structure against the shared schema.

The schema is `references/agent-contract.md` at the plugin root. This checks what a reader and a
downstream skill rely on finding — the header, the six sections in order, the required table
columns, allowed values, owned TBDs, and a checkpoint for every human-confirmed tool. It never
judges whether the content is true; that stays with the reviewers.

    python3 check_contract.py <file>.agent-contract.md [--require-complete]

Prints a JSON report. Exit 0: structurally valid (complete or incomplete). Exit 1: incomplete
and --require-complete was given. Exit 2: invalid. Standard library only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SECTIONS = {1: "Inputs", 2: "Tools", 3: "Outputs", 4: "Guardrails", 5: "Escalation",
            6: "Human checkpoints"}
COLUMNS = {
    1: ["Input", "Source", "Contains personal data"],
    2: ["Tool", "Purpose", "Side effect", "Human confirms"],
    3: ["Output", "Recipient", "Format"],
    4: ["Rule", "Kind", "Enforced by"],
    5: ["Trigger", "Goes to (human role)", "Agent meanwhile"],
    6: ["Checkpoint", "Before", "Approver (role)", "What they approve"],
}
HEADER_FIELDS = ["Agent ID", "Owner", "Status", "Revision"]
SIDE_EFFECTS = {"read", "write", "external send"}
KINDS = {"must never", "must always"}
YES_NO = {"yes", "no"}
DASH = r"\s*[—–-]\s*"
TBD_FULL = re.compile(r"TBD" + DASH + r"owner:\s*(?P<owner>[^;|]+?)\s*;\s*needed:\s*(?P<needed>[^|]+?)\s*$")
CONFIRM_YES = re.compile(r"^yes" + DASH + r"(?P<role>.+)$", re.IGNORECASE)
HEADING = re.compile(r"^##\s+(?P<number>\d+)\.\s+(?P<title>.+?)\s*$")


def _cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _is_rule(cells: list[str]) -> bool:
    return all(re.fullmatch(r":?-{3,}:?", c) for c in cells if c)


def _split_sections(text: str) -> tuple[list[str], list[tuple[int, str, list[str]]]]:
    header, sections, current = [], [], None
    for line in text.splitlines():
        match = HEADING.match(line)
        if match:
            current = (int(match["number"]), match["title"], [])
            sections.append(current)
        elif current is None:
            header.append(line)
        else:
            current[2].append(line)
    return header, sections


def _table(lines: list[str]) -> tuple[list[str], list[list[str]]] | None:
    rows = [_cells(line) for line in lines if line.strip().startswith("|")]
    if len(rows) < 2 or not _is_rule(rows[1]):
        return None
    return rows[0], rows[2:]


def _tbd(cell: str, section: int, tbds: list, errors: list, where: str) -> bool:
    """True when the cell is a TBD (owned or not). Owned TBDs are collected; others are errors."""
    if "TBD" not in cell:
        return False
    match = TBD_FULL.search(cell)
    if match:
        tbds.append({"section": section, "owner": match["owner"].strip(),
                     "needed": match["needed"].strip(), "where": where})
    else:
        errors.append({"section": section,
                       "message": f"{where}: TBD without an owner and what is needed "
                                  "(write 'TBD — owner: <role>; needed: <what>')"})
    return True


def check_text(text: str) -> dict:
    errors: list[dict] = []
    warnings: list[str] = []
    tbds: list[dict] = []
    tools: list[dict] = []
    header_lines, sections = _split_sections(text)

    header = {}
    for line in header_lines:
        match = re.match(r"^\s*[-*]\s*([^:]+):\s*(.*)$", line)
        if match:
            header[match[1].strip()] = match[2].strip()
    for field in HEADER_FIELDS:
        if not header.get(field):
            errors.append({"section": 0, "message": f"header is missing '{field}'"})
    if header.get("Status") and header["Status"] not in {"draft", "reviewed"}:
        errors.append({"section": 0, "message": "header Status must be 'draft' or 'reviewed'"})

    seen = [number for number, _, _ in sections]
    for number in SECTIONS:
        if number not in seen:
            errors.append({"section": number, "message": f"section {number}. {SECTIONS[number]} is missing"})
    highest = 0
    for number, title, _ in sections:
        if number not in SECTIONS:
            errors.append({"section": number, "message": f"unknown section '{number}. {title}'"})
            continue
        if title != SECTIONS[number]:
            errors.append({"section": number,
                           "message": f"section {number} must be titled '{SECTIONS[number]}', not '{title}'"})
        if number < highest:
            errors.append({"section": number, "message": f"section {number} is out of order"})
        highest = max(highest, number)

    confirmed: list[str] = []
    checkpoints_before: set[str] = set()
    for number, _, body in sections:
        if number not in SECTIONS:
            continue
        content = [line for line in body if line.strip()]
        if not content:
            errors.append({"section": number, "message": "section is empty; fill it or write an owned TBD"})
            continue
        table = _table(body)
        if table is None:
            # A whole-section TBD is allowed; anything else needs the table.
            if not any(_tbd(line, number, tbds, errors, "section") for line in content):
                errors.append({"section": number, "message": "section needs its table or an owned TBD"})
            continue
        head, rows = table
        index = {name: head.index(name) for name in COLUMNS[number] if name in head}
        for name in COLUMNS[number]:
            if name not in index:
                errors.append({"section": number, "message": f"table is missing the '{name}' column"})
        if len(index) < len(COLUMNS[number]):
            continue
        if not rows:
            errors.append({"section": number, "message": "table has no rows; add rows or replace it with an owned TBD"})
        for row in rows:
            row = row + [""] * (len(head) - len(row))
            label = row[0] or "(unnamed row)"
            values = {name: row[i] for name, i in index.items()}
            for name, value in values.items():
                where = f"{label} / {name}"
                if _tbd(value, number, tbds, errors, where):
                    continue
                if not value:
                    noun = {"Side effect": "side effect", "Human confirms": "confirmation status",
                            "Trigger": "trigger", "Goes to (human role)": "human role"}.get(name, name)
                    errors.append({"section": number, "message": f"{label}: missing {noun}"})
            _check_values(number, label, values, errors)
            if number == 2:
                tools.append(_tool(values))
                if tools[-1]["confirmation"]["value"] == "yes":
                    confirmed.append(values["Tool"])
            if number == 6 and values["Before"] and "TBD" not in values["Before"]:
                checkpoints_before.add(values["Before"].strip("` "))

    for tool in confirmed:
        if tool.strip("` ") not in checkpoints_before:
            errors.append({"section": 6, "message": f"{tool} is human-confirmed but has no checkpoint row "
                                                    "naming it in 'Before'"})

    status = "invalid" if errors else ("incomplete" if tbds else "complete")
    if status == "incomplete" and header.get("Status") == "reviewed":
        warnings.append("Status is 'reviewed' but TBDs remain")
    return {"status": status, "errors": errors, "warnings": warnings, "tbds": tbds,
            "sections": [{"number": n, "title": t} for n, t, _ in sections if n in SECTIONS],
            "tools": tools, "header": header}


def _check_values(number: int, label: str, values: dict, errors: list) -> None:
    def bad(message):
        errors.append({"section": number, "message": f"{label}: {message}"})

    if number == 1:
        value = values["Contains personal data"]
        if value and "TBD" not in value and value.lower() not in YES_NO:
            bad("'Contains personal data' must be yes, no or an owned TBD")
    elif number == 2:
        effect = values["Side effect"]
        if effect and "TBD" not in effect:
            unknown = [e for e in (p.strip().lower() for p in effect.split(",")) if e not in SIDE_EFFECTS]
            if unknown:
                bad(f"unknown side effect {unknown}; use read, write or external send")
        confirm = values["Human confirms"]
        if confirm and "TBD" not in confirm and confirm.lower() != "no" and not CONFIRM_YES.match(confirm):
            bad("'Human confirms' must be 'yes — <role>', 'no' or an owned TBD")
    elif number == 4:
        kind = values["Kind"]
        if kind and "TBD" not in kind and kind.lower() not in KINDS:
            bad("'Kind' must be 'must never' or 'must always'")


def _tool(values: dict) -> dict:
    effect, confirm = values["Side effect"], values["Human confirms"]
    effects = [] if (not effect or "TBD" in effect) else [e.strip().lower() for e in effect.split(",")]
    match = CONFIRM_YES.match(confirm) if confirm else None
    if match:
        confirmation = {"value": "yes", "role": match["role"].strip()}
    elif confirm.lower() == "no":
        confirmation = {"value": "no", "role": None}
    elif "TBD" in confirm:
        confirmation = {"value": "TBD", "role": None}
    else:
        confirmation = {"value": None, "role": None}
    return {"tool": values["Tool"], "side_effects": effects, "confirmation": confirmation}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("contract", type=Path)
    parser.add_argument("--require-complete", action="store_true",
                        help="exit 1 when the contract is valid but still has TBDs")
    args = parser.parse_args(argv)
    report = check_text(args.contract.read_text(encoding="utf-8"))
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if report["status"] == "invalid":
        return 2
    if report["status"] == "incomplete" and args.require_complete:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
