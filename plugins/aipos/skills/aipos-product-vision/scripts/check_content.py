#!/usr/bin/env python3
"""Content lint for flow-content.json.

One rule, learned the hard way: every question carries at least one worked example
showing the SHAPE of a good answer. A definition is not an example. The first
question a person meets is the one that most needs scaffolding.

Usage: python3 check_content.py [path]   Exit 1 if any question is missing one.
"""
import json, os, sys

path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "flow-content.json")
d = json.load(open(path, encoding="utf-8"))
missing = []

for bk, bv in d.get("blocks", {}).items():
    for q in bv.get("questions", []):
        if q.get("control") == "yes_no_with_note":
            continue
        if not q.get("examples"):
            missing.append("%s %s (%s)" % (bk, q["id"], q.get("label", "")))
for t in d.get("triage_questions", []):
    if not t.get("detail_examples"):
        missing.append("T %s (%s)" % (t["id"], t.get("label", "")))

dense = []
def check_dense(label, examples):
    for e in examples or []:
        if len(e.split()) > 35 and "\n" not in e and " · " not in e:
            dense.append("%s: %d words, no line break or separator" % (label, len(e.split())))

for bk, bv in d.get("blocks", {}).items():
    for q in bv.get("questions", []):
        check_dense("%s %s" % (bk, q["id"]), q.get("examples"))
for t in d.get("triage_questions", []):
    check_dense("T %s" % t["id"], t.get("detail_examples"))

if dense:
    print("WARN  %d example(s) may not scan - a shape hiding inside prose:" % len(dense))
    for x in dense:
        print("  " + x)

no_nudge = []
for bk, bv in d.get("blocks", {}).items():
    for q in bv.get("questions", []):
        if q.get("quality_tests") and not q.get("specificity"):
            no_nudge.append("%s %s" % (bk, q["id"]))
local_limits = []
for bk, bv in d.get("blocks", {}).items():
    for q in bv.get("questions", []):
        if "nudge_limit" in (q.get("specificity") or {}):
            local_limits.append("%s %s" % (bk, q["id"]))
import re
skill = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "SKILL.md")
known = {q["id"] for bv in d.get("blocks", {}).values() for q in bv.get("questions", [])}
known |= {t["id"] for t in d.get("triage_questions", [])}
stale = []
if os.path.exists(skill):
    text = open(skill, encoding="utf-8").read()
    for m in set(re.findall(r"\b([A-F]\d{1,2}[A-Za-z]*|LQd|LQ|KC|T\d)\b", text)):
        if m not in known:
            stale.append(m)
if stale:
    print("FAIL  SKILL.md references question ids that no longer exist: %s" % ", ".join(sorted(stale)))
    print("      Describe blocks by purpose and point at questions.py; do not list questions here.")
    sys.exit(1)

# A rule that lives only in the data drifts out of the skill, and vice versa (F-12).
# generated_artifacts is the one rule that governs output rather than questions, so it has
# no question id to catch it - check the cross-reference directly.
if d.get("generated_artifacts") and os.path.exists(skill):
    if "evidence mark" not in text.lower():
        print("FAIL  flow-content.json defines generated_artifacts but SKILL.md does not carry the rule.")
        print("      Anything generated from the vision carries its evidence marks - say so in How to ask.")
        sys.exit(1)
if "generated_artifacts" not in d:
    print("FAIL  generated_artifacts missing from flow-content.json.")
    print("      Without it, a session brief can assert what the record marks inferred.")
    sys.exit(1)

TOO_EARLY = ("how much", "what would it move", "how big", "estimate", "size of the",
             "what is it worth", "expected uplift", "by how much", "who owns", "who signs",
             "who approves", "what is the budget")
too_early = []
for bk, bv in d.get("blocks", {}).items():
    for q in bv.get("questions", []):
        if "learn:new" not in q.get("asked_in", []) and "learn:increment" not in q.get("asked_in", []):
            continue
        fields = [f for f in (q.get("fields") or [])
                  if "asked_in" not in f or any(k.startswith("learn:") for k in f["asked_in"])]
        text = " ".join([q.get("prompt", "")] + [f.get("prompt", "") for f in fields]).lower()
        hits = [p for p in TOO_EARLY if p in text]
        if hits:
            too_early.append("%s %s asks %s" % (bk, q["id"], ", ".join(hits)))
if too_early:
    print("WARN  %d Learn-mode question(s) asking for something not needed yet:" % len(too_early))
    for x in too_early:
        print("  " + x)
    print("  Ask WHICH. Sizing, owners and approvals belong in Commit mode.")

if local_limits:
    print("FAIL  nudge_limit is global and lives in nudge_protocol. Remove it from:")
    for x in local_limits:
        print("  " + x)
    sys.exit(1)

if no_nudge:
    print("WARN  %d question(s) with a quality test but no nudge:" % len(no_nudge))
    for x in no_nudge:
        print("  " + x)

if missing:
    print("FAIL  %d question(s) with no worked example:" % len(missing))
    for m in missing:
        print("  " + m)
    sys.exit(1)
print("PASS  every question carries a worked example")
