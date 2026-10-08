#!/usr/bin/env python3
"""
verify_vision.py - the computed layer of the AIPOS Product Vision.

Reads vision.json and the policy data, then computes what must not be left to
judgment:

  1. mode and scope - the two axes. Mode decides depth, scope decides inheritance
  2. the risk tier, from the triage answers
  3. the reviewer roster, with each reviewer's right and engagement
  4. readiness, as named checks, each asked only in the mode/scope combinations
     that `readiness-rules.json` lists for it
  5. in Learn mode, the promotion signals the accountable owner needs to see

One artifact, two modes: the record is a Product Vision in both. Learn mode explores
whether a product or feature is worth building; Commit mode intends to build it.
Both are authored at Step 6 and both sit inside Build-to-Learn, so Commit mode names
an intent to commit, not a commitment already made.

Nothing here judges the quality of the writing. That is the skill's job, using
references/section-rubrics.md. This decides only what the record can decide.

Usage:
    python3 verify_vision.py <vision.json> [--write] [--json] [--data-dir DIR]

Exit codes:
    0  every blocking check passes
    1  one or more blocking checks fail
    2  a file could not be read or parsed
"""

import argparse
import json
import re
import os
import sys
from datetime import date, datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATA_DIR = os.path.join(os.path.dirname(HERE), "data")

AFFIRMATIVE = ("yes", "not_sure")          # not_sure routes as yes, per the policy
TRIAGE = ("sensitive_data", "autonomous_action", "external_users", "regulated_domain",
          "committed_spend", "brand_attribution", "workforce_impact")

SOLUTION_HINTS = ("dashboard", "portal", "chatbot", "copilot", "plugin", "api", "platform",
                  "integration", "button", "screen", "model", "llm", "rag", "pipeline")

# Phrasings that mean the product, not the change, is the subject of C1. Cheap to
# detect and the single most common defect in a vision statement.
PRODUCT_FRAMING = ("our product", "our solution", "our platform", "the product will",
                   "the solution will", "will help them", "will enable", "will allow them",
                   "helps them to", "provides them with", "gives them the ability")


class VerifierError(Exception):
    pass


def load_json(path, label):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        raise VerifierError("%s not found at %s" % (label, path))
    except json.JSONDecodeError as exc:
        raise VerifierError("%s is not valid JSON: %s" % (label, exc))


def filled(value):
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return len(value) > 0
    return True


# --------------------------------------------------------------------------
# the two axes
# --------------------------------------------------------------------------

def mode_of(vision):
    """Learn mode iff a grant block exists. Its validity is check L1, so an
    empty or unsigned block still puts the record in Learn mode and fails loudly."""
    return "learn" if vision.get("learn_mode") is not None else "commit"


def scope_of(vision):
    """new | increment | revision. Scope is a test, not a selection - the skill
    applies the four questions and records the result here."""
    scope = str(vision.get("scope", "new")).lower()
    return scope if scope in ("new", "increment", "revision") else "new"


# --------------------------------------------------------------------------
# tier and roster
# --------------------------------------------------------------------------

def triage_live(vision, trigger):
    return str((vision.get("triage") or {}).get(trigger, "")).lower() in AFFIRMATIVE


def compute_tier(vision, policy):
    f = lambda t: triage_live(vision, t)
    live = [t for t in ("sensitive_data", "autonomous_action",
                        "external_users", "regulated_domain") if f(t)]

    if f("regulated_domain") and (f("sensitive_data") or f("autonomous_action")):
        tier, rule = "tier_3", "regulated_domain AND (sensitive_data OR autonomous_action)"
    elif len(live) >= 3:
        tier, rule = "tier_3", "count(sensitive_data, autonomous_action, external_users, regulated_domain) >= 3"
    elif live:
        tier, rule = "tier_2", "sensitive_data OR autonomous_action OR regulated_domain OR external_users"
    else:
        tier, rule = "tier_1", "default"

    meta = policy.get("tiers", {}).get(tier, {})
    return {"tier": tier, "label": meta.get("label", tier), "matched_rule": rule,
            "live_triggers": live, "review_rounds_max": meta.get("review_rounds_max", 3)}


RANK = {"absent": 0, "inform": 1, "advisory": 2, "blocking": 3}


def compute_roster(vision, policy, tier):
    roster = []
    for reviewer in policy.get("reviewers", []):
        engagement = reviewer.get("by_tier", {}).get(tier, "absent")
        right = reviewer.get("right", "inform")
        reasons = ["tier %s baseline" % tier]

        for esc in reviewer.get("escalations", []):
            if triage_live(vision, esc.get("when", "")):
                target = esc.get("to", engagement)
                if RANK.get(target, 0) > RANK.get(engagement, 0):
                    engagement = target
                    reasons.append("escalated by %s" % esc["when"])
                if esc.get("right"):
                    right = esc["right"]
                    reasons.append("right raised to %s by %s" % (right, esc["when"]))

        if engagement == "absent" or reviewer.get("role") == "finalises":
            continue  # the accountable owner finalises rather than reviews
        roster.append({"reviewer_id": reviewer["id"], "name": reviewer.get("name", reviewer["id"]),
                       "right": right, "engagement": engagement, "why": "; ".join(reasons)})

    roster.sort(key=lambda r: (-RANK[r["engagement"]], r["name"]))
    return roster


def apply_mode_to_roster(roster, policy, mode):
    """Learn mode keeps Engineering and the owner blocking, everyone else to inform.

    Nothing is deleted. A reviewer the triage would have made blocking still
    appears, and is reported separately so the owner sees who the grant routes past.
    """
    if mode != "learn":
        return roster, []

    keep = set(policy.get("modes", {}).get("learn", {}).get("roster_override", []))
    effective, routed_past = [], []
    for entry in roster:
        item = dict(entry)
        if item["reviewer_id"] in keep:
            item["engagement"] = "blocking"
            item["why"] += "; held by the Learn mode grant"
        else:
            if entry["engagement"] in ("blocking", "advisory"):
                routed_past.append({"reviewer_id": entry["reviewer_id"], "name": entry["name"],
                                    "would_have_been": entry["engagement"]})
            item["engagement"] = "inform"
            item["why"] += "; dropped to inform by the Learn mode grant"
        effective.append(item)

    effective.sort(key=lambda r: (-RANK[r["engagement"]], r["name"]))
    return effective, routed_past


def triage_gaps(vision):
    return [{"id": "GAP-triage-%s" % t, "kind": "triage",
             "text": "Triage answer for %s is Not Sure. It routed conservatively as Yes. "
                     "Confirm a Yes or a No before finalizing." % t}
            for t, a in (vision.get("triage") or {}).items() if str(a).lower() == "not_sure"]


def compute_promotion_signals(vision, mode):
    """Reported, never enforced. Promotion is the accountable owner's decision."""
    if mode != "learn":
        return []

    lm = vision.get("learn_mode") or {}
    triage = vision.get("triage") or {}
    signals = []

    # S1 is a CHANGE signal, not a state signal. It compares against the triage as it
    # stood when the grant was made. Firing on any live trigger would fire on every
    # tier_2 Learn-mode vision the moment triage completes, which is noise - and an
    # owner who granted knowing about a trigger has not been surprised by it.
    at_grant = lm.get("triage_at_grant")
    live_now = {t for t, a in triage.items() if str(a).lower() in AFFIRMATIVE}
    if at_grant is None:
        pass  # no snapshot: say nothing rather than cry change we cannot evidence
    else:
        live_then = {t for t, a in at_grant.items() if str(a).lower() in AFFIRMATIVE}
        newly = sorted(live_now - live_then)
        if newly:
            signals.append({"id": "S1", "name": "Risk profile changed since the grant",
                            "detail": "Newly live: %s" % ", ".join(newly)})
    if lm.get("real_users"):
        signals.append({"id": "S2", "name": "Real users",
                        "detail": "People outside the build team are using it."})
    if lm.get("production_data"):
        signals.append({"id": "S3", "name": "Production or client data",
                        "detail": "It has moved off synthetic or sample data."})
    review_by = lm.get("review_by")
    if review_by:
        try:
            if date.fromisoformat(str(review_by)) < date.today():
                signals.append({"id": "S4", "name": "Review-by date passed",
                                "detail": "Granted window ended %s." % review_by})
        except ValueError:
            pass
    if lm.get("spend_committed") or str(triage.get("committed_spend", "")).lower() in AFFIRMATIVE:
        signals.append({"id": "S5", "name": "Spend committed",
                        "detail": "Budget, headcount or a contract beyond discovery."})

    acked = set(lm.get("signal_acknowledgements") or {})
    for s in signals:
        s["acknowledged"] = s["id"] in acked
    return signals


# --------------------------------------------------------------------------
# the check tests, keyed by id. Applicability comes from the data file.
# --------------------------------------------------------------------------

DISPOSITION_FIELDS = {          # documented in references/vision-schema.md
    "accepted": ("change_ref",),
    "rejected": ("rationale",),
    "deferred": ("rationale", "deferred_to_step"),
}


def benefit_category_ids(_cache={}):
    """The B0 categories, read from the content file so the check and the
    question cannot drift apart."""
    if not _cache:
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "data", "flow-content.json")
        with open(path, encoding="utf-8") as handle:
            content = json.load(handle)
        for question in content["blocks"]["B"]["questions"]:
            if question["id"] == "B0":
                _cache["ids"] = [c["id"] for c in question["categories"]]
    return _cache["ids"]


def is_date(value):
    """A date the rest of the script can compute with. L2 and S4 both read
    review_by; a value that only looks filled passes readiness and is then
    skipped by the date arithmetic, which is the worst of both."""
    try:
        date.fromisoformat(str(value))
        return True
    except (TypeError, ValueError):
        return False


def disposition_closes(raise_):
    """A raise is closed by a disposition of a documented type carrying that
    type's required fields. Truthiness alone let {"type": "dismissed"} - or a
    rejection with no rationale - close a blocking raise."""
    d = raise_.get("disposition")
    if not isinstance(d, dict):
        return False
    required = DISPOSITION_FIELDS.get(str(d.get("type", "")).lower())
    if required is None:
        return False
    return all(filled(d.get(field)) for field in required)


def build_tests(vision, roster, signals):
    blocks = vision.get("blocks", {}) or {}
    measures = vision.get("measures", []) or []
    triage = vision.get("triage") or {}
    lm = vision.get("learn_mode") or {}
    owner = (vision.get("accountable_owner") or {}).get("name", "")

    raises, responded, rights = [], set(), {r["reviewer_id"]: r["right"] for r in roster}
    for review in vision.get("reviews", []):
        # A response identifies a person and a date, and comes from someone the
        # triage actually routed to. An arbitrary timestamp used to clear R7.
        if (review.get("reviewer_id") in rights
                and filled((review.get("responder") or {}).get("name"))
                and is_date(review.get("responded_at"))):
            responded.add(review.get("reviewer_id"))
        for raise_ in review.get("raises", []):
            item = dict(raise_)
            item["reviewer_id"] = review.get("reviewer_id")
            raises.append(item)

    def b(key):
        return blocks.get(key)

    def sourced_measures():
        return [m for m in measures if filled(m.get("baseline")) and filled(m.get("baseline_source"))]

    def unsettled_triage():
        return [t for t, a in triage.items() if str(a).lower() == "not_sure"]

    def unanswered_triage():
        return [t for t in TRIAGE if str(triage.get(t, "")).lower() not in ("yes", "not_sure", "no")]

    def missing_blocking_reviewers():
        return [r["reviewer_id"] for r in roster
                if r["engagement"] == "blocking" and r["reviewer_id"] not in responded]

    def open_raises(sev):
        return [r for r in raises if r.get("severity") == sev and not disposition_closes(r)]

    def unacknowledged_rejections():
        out = []
        for r in raises:
            d = r.get("disposition") or {}
            if (r.get("severity") == "blocking" and d.get("type") == "rejected"
                    and rights.get(r.get("reviewer_id")) == "constrain"
                    and not (d.get("reviewer_acknowledged") or d.get("owner_override"))):
                out.append(r.get("id", "unnamed"))
        return out

    def evidence_ok():
        rows = b("A8") or []
        if not rows:
            return False, "A8 is empty."
        unmarked = [r.get("claim", "?") for r in rows
                    if str(r.get("basis", "")).lower() not in ("known", "inferred", "gap")]
        if unmarked:
            return False, "Unmarked: %s" % ", ".join(unmarked[:3])
        unsourced = [r.get("claim", "?") for r in rows
                     if str(r.get("basis", "")).lower() == "known" and not filled(r.get("source"))]
        return (not unsourced), ("Known with no source: %s" % ", ".join(unsourced[:3])) if unsourced else ""

    def prize_ok():
        val = b("B1")
        if not filled(val):
            return False, "B1 is empty."
        if isinstance(val, dict):
            figures = val.get("figures") or []
            bare = [f.get("value", "?") for f in figures if not filled(f.get("source"))]
            if bare:
                return False, "Figures with no source: %s" % ", ".join(str(x) for x in bare[:3])
            if not figures:
                gap = val.get("gap")
                gap = {"text": gap} if isinstance(gap, str) else (gap if isinstance(gap, dict) else {})
                if not filled(gap.get("text")):
                    return False, "No figures and no gap recorded."
                if not filled(gap.get("owner")):
                    return False, ("The sizing gap has no owner. An unowned gap is a note, not a "
                                   "plan to close it.")
            return True, ""
        return True, "Free text; the rubric judges whether a figure carries a source."

    def statement_ok():
        st = b("F1")
        if not isinstance(st, dict):
            return False, "No statement recorded."
        areas = st.get("focus_areas") or []
        if not filled(st.get("stem")):
            return False, "No stem."
        if not (3 <= len(areas) <= 5):
            return False, "%d focus areas; the format is three to five." % len(areas)
        return True, ""

    def revision_lineage_ok():
        if vision.get("pass_type") != "revision" and scope_of(vision) != "revision":
            return True, ""
        return (filled(vision.get("supersedes")),
                "Marked as a revision with nothing recorded as superseded.")

    def changed_without_rationale():
        if vision.get("pass_type") != "revision":
            return []
        return [c.get("block") for c in vision.get("changes", []) if not filled(c.get("rationale"))]

    def benefits_ok():
        """B0 is answered when every category the content file defines carries a
        value. all() over an empty list is True, so the previous nested lambda
        passed B0: {} - a blocking check satisfied by no answer at all."""
        val = b("B0")
        if not isinstance(val, dict):
            return False, "B0 is empty."
        rows = {c.get("id"): c for c in (val.get("categories") or []) if isinstance(c, dict)}
        missing = [cid for cid in benefit_category_ids()
                   if str(rows.get(cid, {}).get("value", "")).lower() not in ("yes", "not_sure", "no")]
        if missing:
            return False, "Unanswered: %s" % ", ".join(missing)
        yes = [cid for cid in benefit_category_ids() if rows[cid].get("value") == "yes"]
        if not yes:
            return False, "No category is a reason we would do this."
        ranking = [r for r in (val.get("ranking") or []) if r in rows]
        if len(yes) > 1 and set(ranking) != set(yes):
            return False, "The Yes set is unranked, or the ranking does not match it."
        for cid in (ranking or yes)[:3]:
            if not filled(rows[cid].get("why")):
                return False, "No reason behind %s." % cid
            if cid == "other" and not filled(rows[cid].get("name")):
                return False, "Other is a Yes with no benefit named."
        return True, ""

    def gaps_without_owners():
        return [g.get("id", "unnamed") for g in vision.get("gaps", [])
                if g.get("kind") == "evidence" and not (g.get("owner") and g.get("next_action"))]

    def grant_ok():
        granted_by = (lm.get("granted_by") or {}).get("name", "")
        if not (filled(granted_by) and filled(lm.get("granted_at")) and filled(lm.get("grant_reason"))):
            return False, "The grant is missing a grantor, a date or a reason."
        if granted_by.strip().lower() != owner.strip().lower():
            return False, ("Granted by %s but the accountable owner is %s. Only the owner grants "
                           "Learn mode." % (granted_by, owner or "unnamed"))
        if not isinstance(lm.get("triage_at_grant"), dict):
            return False, ("The grant records no triage snapshot. Without one, a risk trigger that "
                           "goes live afterwards produces no promotion signal.")
        return True, ""

    def ratification_ok():
        """Ratification is the accountable owner's act. grant_ok() ten lines
        above already held that line for the Learn grant; R16 did not hold it
        here, so anyone could ratify a record that reported ready."""
        if vision.get("status") != "ratified":
            return True, ""
        ratifier = (vision.get("ratified_by") or {}).get("name", "")
        if not filled(ratifier):
            return False, "Marked ratified with nobody named as the ratifier."
        if not filled(owner):
            return False, "Marked ratified with no accountable owner named."
        if ratifier.strip().lower() != owner.strip().lower():
            return False, ("Ratified by %s but the accountable owner is %s. Ratification is the "
                           "owner's act." % (ratifier, owner))
        return True, ""

    def signals_ok():
        if vision.get("status") != "ratified":
            n = len(signals)
            return True, ("%d live, acknowledgement required at ratification" % n) if n else ""
        unacked = [s["id"] for s in signals if not s.get("acknowledged")]
        return (not unacked), ("Unacknowledged: %s" % ", ".join(unacked)) if unacked else ""

    def lineage_ok():
        if scope_of(vision) == "increment":
            return filled((vision.get("parent_vision_ref") or {}).get("id")), ""
        opp = vision.get("opportunity_ref") or {}
        if filled(opp.get("id")):
            if opp.get("accepted") is True:
                return True, ""
            return False, ("Opportunity %s is linked but not marked accepted. The rule is an "
                           "accepted opportunity, or a note saying none exists." % opp.get("id"))
        return filled(vision.get("no_opportunity_note")), "No opportunity linked and no note explaining why."

    return {
        "R1":  lambda: (len(str(b("C1") or "").strip()) >= 40, ""),
        "R2":  lineage_ok,
        "R3":  lambda: (bool(sourced_measures()), "" if sourced_measures() else "No measure carries both a baseline and its source."),
        "R4":  lambda: (filled(b("D1")) and filled(b("D2")), ""),
        "R5":  lambda: (filled(b("D3")), ""),
        "R6":  lambda: (not unanswered_triage() and not unsettled_triage(),
                        ("Unsettled: %s" % ", ".join(sorted(unsettled_triage()))) if unsettled_triage()
                        else (("Unanswered: %s" % ", ".join(unanswered_triage())) if unanswered_triage() else "")),
        "R7":  lambda: (not missing_blocking_reviewers(),
                        ("Awaiting: %s" % ", ".join(missing_blocking_reviewers())) if missing_blocking_reviewers() else ""),
        "R8":  lambda: (not open_raises("blocking"), ("%d open" % len(open_raises("blocking"))) if open_raises("blocking") else ""),
        "R9":  lambda: (not unacknowledged_rejections(),
                        ("Unacknowledged: %s" % ", ".join(unacknowledged_rejections())) if unacknowledged_rejections() else ""),
        "R10": lambda: (filled(owner), ""),
        "R17": lambda: ((lambda ct: isinstance(ct, dict)
                         and (filled(ct.get("formed_with")) or filled(ct.get("absent_note"))))(
                         vision.get("core_team")), ""),
        "R13": lambda: (not gaps_without_owners(),
                        ("Without an owner: %s" % ", ".join(gaps_without_owners())) if gaps_without_owners() else ""),
        "R14": lambda: (not open_raises("advisory"), ("%d unanswered" % len(open_raises("advisory"))) if open_raises("advisory") else ""),
        "R15": lambda: (not changed_without_rationale(),
                        ("Without rationale: %s" % ", ".join(str(x) for x in changed_without_rationale()))
                        if changed_without_rationale() else ""),
        "R16": ratification_ok,
        "R18": revision_lineage_ok,

        "V1":  lambda: (filled(b("A1")) and filled(b("A5")), ""),
        "V2":  lambda: ((lambda a: isinstance(a, dict) and filled(a.get("value"))
                         and (a.get("value") != "yes"
                              or (filled(a.get("how")) and a.get("basis") in ("known", "inferred"))))(b("A7")), ""),
        "V11": lambda: (filled(b("A3")), ""),
        "V12": lambda: (isinstance(b("A4"), dict) and filled(b("A4").get("value"))
                        and filled(b("A4").get("why")), ""),
        "V3":  evidence_ok,
        "V13": benefits_ok,
        "V14": lambda: ((lambda x: isinstance(x, dict)
                         and (filled(x.get("outcome")) or x.get("none_committed") is True))(b("B00")), ""),
        "V4":  prize_ok,
        "V5":  lambda: (filled(b("B2")) and filled(b("B3")), ""),
        "V6":  lambda: (filled(b("B4")), ""),
        "V7":  lambda: (isinstance(b("C2"), dict) and filled(b("C2").get("arc")) and filled(b("C2").get("mvp_proves")), ""),
        "V8":  statement_ok,
        "V9":  lambda: (filled(b("C3")), ""),
        "V10": lambda: (filled(b("D4")), ""),

        "S1":  lambda: ((lambda pv: isinstance(pv, dict) and filled(pv.get("product"))
                         and (filled(pv.get("id"))
                              or pv.get("exists") is False
                              or (pv.get("lookup") == "information_unavailable"
                                  and filled(pv.get("reason")))))(
                         vision.get("parent_vision_ref")), ""),
        "S2":  lambda: ((vision.get("parent_vision_ref") or {}).get("exists") is False or b("F2") is True,
                        "" if b("F2") is True else "Answered No, or the parent has a statement and it was not checked."),
        "S3":  lambda: (filled(b("B5")), ""),
        "S4":  lambda: (filled(b("A11")), ""),

        "L7":  lambda: ((lambda x: isinstance(x, dict)
                         and any(c.get("value") == "yes" for c in (x.get("categories") or []))
                         and (sum(1 for c in (x.get("categories") or []) if c.get("value") == "yes") < 2
                              or filled(x.get("primary"))))(b("LQd")), ""),
        "L1":  grant_ok,
        "L2":  lambda: (is_date(lm.get("review_by")),
                        "" if is_date(lm.get("review_by")) else
                        "Not a date. A review-by the date arithmetic cannot read raises no signal."),
        "L3":  lambda: (filled(lm.get("learning_question")), ""),
        "L4":  lambda: (filled(lm.get("kill_condition")), ""),
        "L5":  lambda: (filled(b("D2")), ""),
        "L6":  signals_ok,
    }


def compute_readiness(vision, roster, tier_info, rules, mode, scope, signals):
    key = "%s:%s" % (mode, "new" if scope in ("new", "revision") else "increment")
    tests = build_tests(vision, roster, signals)
    results = []

    for spec in rules.get("checks", []):
        cid = spec["id"]
        asked = key in spec.get("asked_in", [])
        test = tests.get(cid)
        if test is None:
            continue
        if asked:
            try:
                passed, detail = test()
            except Exception as exc:                       # a malformed record is a failure, not a crash
                passed, detail = False, "could not be evaluated: %s" % exc
            if not passed and not detail:
                detail = spec.get("failure_message", "")
        else:
            passed, detail = True, "not asked in %s" % key
        results.append({"id": cid, "severity": spec["severity"], "name": spec["name"],
                        "passed": bool(passed), "asked": asked, "detail": detail})

    blocking = [c for c in results if c["severity"] == "blocking" and c["asked"]]
    counted = [c for c in results if c["asked"]]
    ready = all(c["passed"] for c in blocking)
    percent = round(100.0 * sum(1 for c in counted if c["passed"]) / len(counted)) if counted else 0

    rounds_max = tier_info["review_rounds_max"]
    return {
        "checks": results,
        "asked_total": len(counted),
        "not_asked_total": len(results) - len(counted),
        "blocking_total": len(blocking),
        "blocking_open": sum(1 for c in blocking if not c["passed"]),
        "meter_percent": percent,
        "ready": ready,
        "rounds_used": vision.get("rounds", 0),
        "rounds_max": rounds_max,
        "rounds_exhausted": vision.get("rounds", 0) >= rounds_max and not ready,
        "combination": key,
    }


def warnings_for(vision, mode, scope, signals):
    out = []
    c1 = str((vision.get("blocks") or {}).get("C1") or "").lower()
    framing = sorted({p for p in PRODUCT_FRAMING if p in c1}) or (["starts with \"our\""] if c1.startswith("our ") else [])
    if framing:
        out.append("C1 is phrased as what the product does (%s). The customer should be the subject and the "
                   "product should not appear. The script cannot judge the rewrite, only the framing."
                   % ", ".join(framing))
    # Word boundaries: "rag" matched inside "storage" and "api" inside "rapid",
    # which put a false warning in the author's own to-do list.
    hits = sorted({w for w in SOLUTION_HINTS
                   if re.search(r"\b%s\b" % re.escape(w), c1)})
    if hits:
        out.append("C1 mentions %s. Test it against the no-solution-in-statement rule; the script "
                   "cannot judge this." % ", ".join(hits))
    if mode == "learn" and signals:
        out.append("This vision is in Learn mode with %d live promotion signal(s). Promoting is %s's "
                   "decision, not this script's. Put the signals in front of them."
                   % (len(signals), (vision.get("accountable_owner") or {}).get("name", "the owner")))
    blocks = vision.get("blocks") or {}
    a3, a7 = blocks.get("A4"), blocks.get("A7")
    if (isinstance(a3, dict) and a3.get("value") in ("critical", "high")
            and isinstance(a7, dict) and a7.get("value") == "no"):
        out.append("A4 says %s but A7 says nothing has been tried, built or paid for. Adoption, not "
                   "capability, is the dominant risk here, and it should show in the measures and in the "
                   "Step 11 plan." % a3["value"])
    if scope == "increment" and blocks.get("F2") is False:
        out.append("The parent statement does not cover this. That is a routing result, not a defect: "
                   "re-scope it as a revision of the parent vision.")
    return out


def mode_label(mode):
    return "LEARN" if mode == "learn" else "COMMIT"


def render(computed, vision):
    mode, scope = computed["mode"], computed["scope"]
    tier, ready = computed["tier"], computed["readiness"]
    lines = []
    lines.append("Product Vision: %s" % vision.get("title", vision.get("slug", "untitled")))
    lines.append("Pass: %s   Status: %s   Version: %s"
                 % (vision.get("pass_type", "new"), vision.get("status", "draft"),
                    vision.get("version", "0.1")))
    lines.append("")
    if computed.get("policy_maturity") == "pilot":
        lines.append("POLICY  %s - pilot, not for client use" % computed.get("policy_version"))
        lines.append("")
    lines.append("MODE   %s mode" % mode_label(mode))
    if mode == "learn":
        lm = vision.get("learn_mode") or {}
        lines.append("       granted by %s on %s, review by %s"
                     % ((lm.get("granted_by") or {}).get("name", "UNRECORDED"),
                        lm.get("granted_at", "UNRECORDED"), lm.get("review_by", "UNSET")))
        lines.append("       cannot clear Step 12; promotion is the owner's call")
    else:
        lines.append("       intent to commit. Still inside Build-to-Learn until Step 12.")
    lines.append("SCOPE  %s" % scope.upper())
    if scope == "increment":
        lines.append("       parent: %s" % ((vision.get("parent_vision_ref") or {}).get("id", "UNLINKED")))
    lines.append("CHECKS asked for %s" % ready["combination"])
    lines.append("")
    lines.append("RISK TIER  %s (%s)" % (tier["tier"], tier["label"]))
    lines.append("  rule: %s" % tier["matched_rule"])
    lines.append("  live triggers: %s" % (", ".join(tier["live_triggers"]) or "none"))
    lines.append("")
    lines.append("ROSTER")
    for r in computed["roster"]:
        lines.append("  %-9s %-9s %-28s (%s)" % (r["engagement"], r["right"], r["name"], r["why"]))
    if computed.get("routed_past"):
        lines.append("")
        lines.append("ROUTED PAST BY THE GRANT")
        for r in computed["routed_past"]:
            lines.append("  %-28s would have been %s" % (r["name"], r["would_have_been"]))
    if computed.get("promotion_signals"):
        lines.append("")
        lines.append("PROMOTION SIGNALS  (reported for the accountable owner, never enforced)")
        for s in computed["promotion_signals"]:
            lines.append("  %-4s %-28s %s%s" % (s["id"], s["name"], s["detail"],
                                                "" if s.get("acknowledged") else "   [unacknowledged]"))
    lines.append("")
    lines.append("READINESS  %d%%   %s   (%d asked, %d not asked)"
                 % (ready["meter_percent"],
                    "READY" if ready["ready"] else "NOT READY, %d blocking open" % ready["blocking_open"],
                    ready["asked_total"], ready["not_asked_total"]))
    for c in ready["checks"]:
        mark = "n/a " if not c["asked"] else ("pass" if c["passed"] else "FAIL")
        flag = "!" if (c["severity"] == "blocking" and c["asked"] and not c["passed"]) else " "
        lines.append("  %s %-4s %-4s %-44s %s" % (flag, c["id"], mark, c["name"], c["detail"]))
    if computed["triage_gaps"]:
        lines.append("")
        lines.append("TRIAGE GAPS")
        for g in computed["triage_gaps"]:
            lines.append("  %s" % g["text"])
    if ready["rounds_exhausted"]:
        lines.append("")
        lines.append("ROUNDS EXHAUSTED  %d of %d used without readiness. Stop iterating and schedule a "
                     "decision session with %s."
                     % (ready["rounds_used"], ready["rounds_max"],
                        (vision.get("accountable_owner") or {}).get("name", "the accountable owner")))
    if computed["warnings"]:
        lines.append("")
        lines.append("WARNINGS, for the facilitator to judge")
        for w in computed["warnings"]:
            lines.append("  %s" % w)
    return "\n".join(lines)


def render_todo(computed, vision, rules):
    """Three lists, not one. What to close, what the owner must decide, what to carry.

    Checks, warnings and gaps that point at the same thing are one item. The counts
    people act on are the first two; the third is a record.
    """
    spec = {c["id"]: c for c in rules.get("checks", [])}
    ready = computed["readiness"]
    close, decide, carry, seen = [], [], [], set()

    # Checks the author cannot close: they are satisfied by the next stage happening,
    # not by anything on this screen. Listing them makes three things look like four.
    NEXT_STAGE = ("R7", "R8", "R9", "R16", "L6")

    for c in ready["checks"]:
        if not c["asked"] or c["passed"] or c["severity"] != "blocking":
            continue
        if c["id"] in NEXT_STAGE:
            continue
        meta = spec.get(c["id"], {})
        concerns = meta.get("concerns", c["id"])
        close.append((concerns,
                      meta.get("action") or meta.get("failure_message", c["name"]),
                      c["detail"]))
        seen.add(concerns)

    for w in computed.get("warnings", []):
        if w.startswith("C1 is phrased"):
            if "C1 the change" not in seen:
                close.append(("C1 the change",
                              "Rewrite the change with the customer as the subject and no product in it", ""))
                seen.add("C1 the change")
        elif "promotion signal" in w:
            decide.append(("promotion signals",
                           "Acknowledge the live promotion signal, or promote this to Commit mode", ""))
            seen.add("promotion signals")
        else:
            carry.append(("finding", w))

    for g in vision.get("gaps", []):
        key = g.get("concerns") or g.get("id", "")
        if any(k in seen for k in (key, g.get("concerns", "\x00"))):
            continue
        if g.get("kind") == "evidence" and g.get("id", "").startswith("GAP-A8"):
            continue
        subject = (g.get("text", "").split(".")[0] or "").strip()
        action = (g.get("next_action") or "").strip()
        if action and subject and not action.lower().startswith(subject.lower()[:12]):
            text = "%s. %s" % (subject, action[0].lower() + action[1:] if action else "")
        else:
            text = action or subject
        carry.append((g.get("id", ""), text))

    out = []
    if close:
        out.append("We're ready to move on. Before we do, there %s %d quick question%s to close.\n"
                   % ("is" if len(close) == 1 else "are", len(close),
                      "" if len(close) == 1 else "s"))
        for i, (concerns, do, detail) in enumerate(close, 1):
            out.append("%d. %s" % (i, do))
            if detail:
                out.append("   %s" % detail)
        out.append("")
    else:
        out.append("Nothing to close. Ready to move on.\n")

    if decide:
        out.append("Your call as accountable owner:\n")
        for _, do, _ in decide:
            out.append("  - %s" % do)
        out.append("")

    if carry:
        out.append("Carried forward, nothing to do now:\n")
        for key, text in carry:
            out.append("  - %s" % text)
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description="Verify an AIPOS Product Vision.")
    parser.add_argument("vision")
    parser.add_argument("--write", action="store_true", help="stamp the computed block into the record")
    parser.add_argument("--json", action="store_true", help="emit the computed block as JSON")
    parser.add_argument("--todo", action="store_true",
                        help="what to close before moving on, merged by what it concerns")
    parser.add_argument("--data-dir", default=DEFAULT_DATA_DIR)
    args = parser.parse_args()

    try:
        vision = load_json(args.vision, "vision")
        policy = load_json(os.path.join(args.data_dir, "engagement-policy.json"), "engagement policy")
        rules = load_json(os.path.join(args.data_dir, "readiness-rules.json"), "readiness rules")
    except VerifierError as exc:
        sys.stderr.write("error: %s\n" % exc)
        return 2

    mode, scope = mode_of(vision), scope_of(vision)
    tier_info = compute_tier(vision, policy)
    if mode == "learn":
        tier_info["review_rounds_max"] = (policy.get("modes", {}).get("learn", {})
                                          .get("review_rounds_max", tier_info["review_rounds_max"]))

    computed_roster = compute_roster(vision, policy, tier_info["tier"])
    roster, routed_past = apply_mode_to_roster(computed_roster, policy, mode)
    signals = compute_promotion_signals(vision, mode)
    readiness = compute_readiness(vision, roster, tier_info, rules, mode, scope, signals)

    computed = {
        "computed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "policy_version": policy.get("policy_version"),
        "policy_maturity": policy.get("maturity", "production"),
        "rules_version": rules.get("rules_version"),
        "mode": mode,
        "scope": scope,
        "artifact": "Product Vision",
        "mode_label": mode_label(mode),
        "tier": tier_info,
        "roster": roster,
        "routed_past": routed_past,
        "promotion_signals": signals,
        "triage_gaps": triage_gaps(vision),
        "readiness": readiness,
        "warnings": warnings_for(vision, mode, scope, signals),
    }

    if args.todo:
        print(render_todo(computed, vision, rules))
    else:
        print(json.dumps(computed, indent=2) if args.json else render(computed, vision))

    if args.write:
        vision["computed"] = computed
        with open(args.vision, "w", encoding="utf-8") as handle:
            json.dump(vision, handle, indent=2, ensure_ascii=False)
            handle.write("\n")

    return 0 if readiness["ready"] else 1


if __name__ == "__main__":
    sys.exit(main())
