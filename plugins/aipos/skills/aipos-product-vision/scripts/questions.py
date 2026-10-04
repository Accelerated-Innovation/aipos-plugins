#!/usr/bin/env python3
"""Print the exact question set for a mode and scope.

Exists because a facilitator reading the blocks will ask questions the current
combination does not ask. The filtered list is the skill's job, not theirs.

Usage: python3 questions.py <mode> <scope>     e.g. questions.py learn new
"""
import json
import os
import sys


MODES = ("commit", "learn")
SCOPES = ("new", "increment", "revision")


def choice_line(values):
    """Render a choice list as its labels, so the facilitator reads out the
    options rather than inventing them."""
    labels = []
    for v in values or []:
        labels.append(v.get("label", v.get("id", "")) if isinstance(v, dict) else str(v))
    return " / ".join(l for l in labels if l)


def follow_ups(question, key):
    """The prompts a facilitator still has to ask after the main one.

    The skill tells them to ask from this output and nothing else. Printing only
    the top-level prompt dropped A4's required reason, A7's how and basis, and
    D3's stop-ask-or-hand-off - each of them a required follow-up that a check
    then fails on.
    """
    lines = []
    if question.get("values"):
        lines.append(("choose", choice_line(question["values"]), ""))

    fu = question.get("follow_up") or {}
    when = fu.get("required_when")
    condition = (" [if %s]" % " or ".join(when)) if when else ("" if fu.get("required") else " [optional]")
    if fu.get("prompt"):
        lines.append(("then", fu["prompt"], condition))
    for field in fu.get("fields", []) or []:
        if not isinstance(field, dict):
            lines.append(("then", str(field), condition))
            continue
        suffix = condition
        if field.get("values"):
            suffix = "%s  (%s)" % (condition, choice_line(field["values"]))
        lines.append(("then", field.get("prompt", field.get("id", "")), suffix))

    for field in question.get("fields", []) or []:
        if not isinstance(field, dict):       # some blocks list field ids as plain strings
            lines.append(("then", str(field), ""))
            continue
        if "asked_in" in field and key not in field["asked_in"]:
            continue
        req = field.get("required_when")
        suffix = (" [if %s]" % " or ".join(req)) if req else ""
        if field.get("values"):
            suffix = "%s  (%s)" % (suffix, choice_line(field["values"]))
        lines.append(("then", field.get("prompt", field.get("id", "")), suffix))
    return lines


def main():
    # Validated rather than defaulted. An unrecognised argument used to fall through to
    # commit:new and print a plausible question set under a nonsense heading, which is the
    # one failure mode a facilitator would not notice.
    args = [a.lower() for a in sys.argv[1:]]
    mode = args[0] if args else "commit"
    scope = args[1] if len(args) > 1 else "new"
    if len(args) > 2 or mode not in MODES or scope not in SCOPES:
        sys.stderr.write("usage: questions.py [%s] [%s]\n" % ("|".join(MODES), "|".join(SCOPES)))
        return 2
    key = "%s:%s" % (mode, "new" if scope in ("new", "revision") else "increment")

    data = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    d = json.load(open(os.path.join(data, "flow-content.json"), encoding="utf-8"))

    out = ["Question set for %s" % key, ""]
    n = 0

    # Step 0 lives outside blocks and is easy to forget. The facilitator is told to
    # ask only from this output, so it has to be in it.
    step0 = d.get("step_0", {})
    s0, s0b = step0.get("scope_question"), step0.get("product_question")
    if s0 or s0b:
        out.append("0  Set up")
        if s0:
            n += 1
            out.append("   %-5s %s" % (s0["id"], s0["prompt"]))
            for kind, text, suffix in follow_ups(s0, key):
                out.append("   %-5s %s %s%s" % ("", kind, text, suffix))
        if s0b and key in s0b.get("asked_in", []):
            n += 1
            out.append("   %-5s %s  [if %s]" % (s0b["id"], s0b["prompt"], s0b["asked_when"]))
            for kind, text, suffix in follow_ups(s0b, key):
                out.append("   %-5s %s %s%s" % ("", kind, text, suffix))
        out.append("")

    for bk in sorted(d.get("blocks", {})):
        bv = d["blocks"][bk]
        asked = [q for q in bv.get("questions", []) if key in q.get("asked_in", [])]
        if not asked:
            continue
        out.append("%s  %s" % (bk, bv.get("title", bv.get("label", ""))))
        for q in asked:
            n += 1
            prompt = (q.get("prompt_commit") if mode == "commit" and q.get("prompt_commit")
                      else q.get("prompt", ""))
            mark = "  [if %s]" % q["asked_when"] if q.get("asked_when") else ""
            out.append("   %-5s %s%s" % (q["id"], prompt, mark))
            for kind, text, suffix in follow_ups(q, key):
                out.append("   %-5s %s %s%s" % ("", kind, text, suffix))
        out.append("")

    out.append("E  Triage")
    for t in d.get("triage_questions", []):
        n += 1
        out.append("   %-5s %s" % (t["id"], t["prompt"]))
        for kind, text, suffix in follow_ups(t, key):
            out.append("   %-5s %s %s%s" % ("", kind, text, suffix))
    out.append("")
    out.append("%d questions in %s" % (n, key))

    try:
        print("\n".join(out))
    except BrokenPipeError:      # piped to head, which is the normal way to read this
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
