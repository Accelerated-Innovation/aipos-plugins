#!/usr/bin/env python3
"""Derive execution readiness from local facts and a decision read.

WHY THIS EXISTS
    A Development Token used to be the whole decision: no critical blockers,
    a good enough score, start coding. Under a behavior contract that is half
    the question. The other half — *is this exact scope approved, and does
    that approval still hold* — lives in the decision service and cannot be
    read from the repository at all.

    So the token becomes a **derived execution-readiness record that
    references the product approval**, rather than a substitute for one. The
    states stay apart because collapsing them is how a local check ends up
    filed as evidence that somebody approved the behavior:

        prepared                 a package exists; nobody decided anything
        approved for scope       a commitment binds *this exact* baseline
        locally executable       the local gate finds no blockers
        authority verified       a *fresh* read says the approval still holds
        implementation verified  the behavior was afterwards shown to work

    They are not a ladder. Locally executable and authority verified are
    independent, and the common mistake is to treat a clean package as an
    approved one.

WHAT IT REFUSES
    A stale reading cannot produce an authoritative green. A check from last
    week proves what was true last week, and an approval can be withdrawn in
    between — the cached-authority failure the contract exists to prevent,
    displaced from the merge boundary to the start of work.

NO CLOCK OF ITS OWN
    `Facts.now` is supplied. A freshness rule that reads the wall clock
    cannot be tested at the boundary it enforces, and this is a boundary.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from enum import Enum

#: How long an authority reading stays good enough to call a result
#: authoritative. Short, because its only job is to bound the window between
#: reading and acting; anything longer is a cache pretending to be a check.
FRESHNESS = datetime.timedelta(hours=1)


class State(str, Enum):
    PREPARED = "prepared"
    APPROVED_FOR_SCOPE = "approved_for_scope"
    LOCALLY_EXECUTABLE = "locally_executable"
    AUTHORITY_VERIFIED = "authority_verified"
    IMPLEMENTATION_VERIFIED = "implementation_verified"


#: The rubric's bands. The blocker list is the gate and the score is
#: advisory context — but "advisory" never meant ignored: a package below
#: 8.5 is too weak to act on whatever its blocker list says.
APPROVE_AT = 10.0
EDITS_AT = 8.5


class NotADecision(RuntimeError):
    """Raised when something advisory is asked to become a record."""


@dataclass(frozen=True)
class Facts:
    """Everything the derivation is allowed to look at.

    `authority` is three-valued on purpose: True verified, False withdrawn or
    never granted, and None *could not determine*. Collapsing None into False
    reports an outage as a rejection; collapsing it into True is worse.
    """

    package_complete: bool
    blockers: list
    #: The rubric's 12-dimension advisory score. `None` means "not scored",
    #: which is not the same as "scored well" — the bands below say so
    #: rather than assuming the best.
    score: float | None
    commitment_id: str | None
    binds_this_baseline: bool
    authority: bool | None
    authority_checked_at: datetime.datetime | None
    implementation_verified: bool
    now: datetime.datetime


@dataclass
class Readiness:
    states: set = field(default_factory=set)
    decision: str = "blocked"
    reason: str = ""
    authoritative: bool = False
    advisory: bool = False
    carries_product_approval: bool = False
    score: float | None = None
    commitment_id: str | None = None
    verified_at: datetime.datetime | None = None
    blockers: list = field(default_factory=list)


def _fresh(facts: Facts) -> bool:
    at = facts.authority_checked_at
    if at is None:
        return False
    age = facts.now - at
    # A reading dated in the future is clock skew or a hand-edited record.
    # Neither should buy freshness.
    return datetime.timedelta(0) <= age <= FRESHNESS


def assess(facts: Facts, *, contract: bool = True, batch: bool = False) -> Readiness:
    """Derive the states and the token decision.

    `contract=False` is a project with no decision service — most projects
    using GovKit. Nothing changes for them except that the token never
    claims to carry a product approval.

    `batch=True` scores a corpus. It decides nothing, and says so.
    """
    result = Readiness(blockers=list(facts.blockers), score=facts.score)

    if facts.package_complete:
        result.states.add(State.PREPARED)
    # Completeness is step 1 of the readiness process, not decoration.
    # Wired only to PREPARED, an incomplete package with an empty blocker
    # list produced an approved, authoritative token.
    if facts.package_complete and not facts.blockers:
        result.states.add(State.LOCALLY_EXECUTABLE)
    if facts.implementation_verified:
        result.states.add(State.IMPLEMENTATION_VERIFIED)

    # "Approved for *exact* scope". A commitment that exists but binds a
    # different baseline is somebody else's decision, and counting it is the
    # borrowed-approval failure the digest comparison exists to catch.
    approved_for_scope = bool(facts.commitment_id) and facts.binds_this_baseline
    if approved_for_scope:
        result.states.add(State.APPROVED_FOR_SCOPE)
        result.commitment_id = facts.commitment_id

    fresh = _fresh(facts)
    if approved_for_scope and facts.authority is True and fresh:
        result.states.add(State.AUTHORITY_VERIFIED)
        result.verified_at = facts.authority_checked_at

    if facts.blockers:
        result.decision = "blocked"
        result.reason = f"{len(facts.blockers)} critical blocker(s) in the local package"
    elif not facts.package_complete:
        result.decision = "blocked"
        result.reason = "the feature package is incomplete"
    elif facts.score is not None and facts.score < EDITS_AT:
        result.decision = "blocked"
        result.reason = f"advisory score {facts.score} is below {EDITS_AT}"
    elif facts.score is None:
        result.decision = "approved_with_edits"
        result.reason = "no advisory score was supplied, so this is not a full pass"
    elif facts.score < APPROVE_AT:
        result.decision = "approved_with_edits"
        result.reason = f"advisory score {facts.score} is below {APPROVE_AT}"
    elif not contract:
        result.decision = "approved"
        result.reason = "no decision service is configured for this project"
    elif not approved_for_scope:
        # AUTHORITY_VERIFIED already required this; the decision did not, so
        # a fresh `True` about somebody else's commitment read as approval.
        result.decision = "approved_with_edits"
        result.reason = (
            "no recorded commitment binds this exact baseline, so nothing "
            "approves this scope"
        )
    elif facts.authority is False:
        result.decision = "blocked"
        result.reason = (
            "the decision service does not currently authorize this baseline"
        )
    elif facts.authority is None:
        result.decision = "approved_with_edits"
        result.reason = (
            "authority could not be read, so this is execution readiness only "
            "and not an authoritative result"
        )
    elif not fresh:
        result.decision = "approved_with_edits"
        result.reason = (
            "the authority reading is stale, so this is execution readiness "
            "only; re-check before relying on it"
        )
    else:
        result.decision = "approved"
        result.reason = "no blockers, and the approval currently authorizes this scope"

    if contract:
        result.authoritative = (
            State.AUTHORITY_VERIFIED in result.states
            and State.LOCALLY_EXECUTABLE in result.states
            and result.decision == "approved"
        )
        result.carries_product_approval = State.AUTHORITY_VERIFIED in result.states
    else:
        # Nothing was read, so nothing can be claimed. `authoritative` stays
        # False: it means "a protected boundary would accept this", and no
        # boundary accepts a result derived from local files alone.
        result.authoritative = False
        result.carries_product_approval = False

    if batch:
        # A corpus view. Advisory scores are not decisions, and a badge that
        # looks like one is a badge somebody will cite as if it were.
        result.advisory = True
        result.authoritative = False

    return result


def to_record(
    result: Readiness,
    *,
    feature_id: str,
    draft_version: str | None = None,
    ts: datetime.datetime | None = None,
) -> dict:
    """The `.govkit/tokens/<feature-key>.json` record.

    The existing fields are kept exactly: `govkit-metrics-emit` reads
    `decision`, and refinement lead time and blocked-token rate are computed
    from it, so renaming it to make room for the new fields would silently
    zero both.

    `product_approval` is explicit `null` rather than absent when there is
    none. Absent reads as "not recorded yet"; null says the question was
    asked and this project has no answer.
    """
    if result.advisory:
        raise NotADecision(
            "batch mode produces advisory scores for a corpus, not decisions; "
            "no token record is written"
        )

    approval = None
    if result.carries_product_approval and result.commitment_id:
        approval = {
            "commitment_id": result.commitment_id,
            "verified_at": result.verified_at.isoformat() if result.verified_at else None,
        }

    return {
        "feature_id": feature_id,
        "decision": result.decision,
        # Carried through unchanged. The original record had all three and
        # `govkit-metrics-emit` reserves them for the token event; dropping
        # them while the documentation said every original field was
        # unchanged is a claim that survives review because nobody diffs a
        # JSON example.
        "score": result.score,
        "blockers": list(result.blockers),
        "draft_version": draft_version,
        "ts": (ts or result.verified_at).isoformat() if (ts or result.verified_at) else None,
        # Says what this record *is*, so it cannot be filed as evidence that
        # somebody approved the behavior.
        "kind": "execution_readiness",
        "authoritative": result.authoritative,
        "product_approval": approval,
        "states": sorted(s.value for s in result.states),
        "reason": result.reason,
    }


# ---------------------------------------------------------------------------
# Command line
# ---------------------------------------------------------------------------
#
# Without this the module is a checker only the tests call. The skill tells
# an agent to derive the states and write the token record, and following
# that instruction has to execute these safeguards rather than reimplement
# them in prose — which is how the two drift apart.


_AUTHORITY = {"verified": True, "withdrawn": False, "unknown": None}


def _moment(value: str | None) -> datetime.datetime | None:
    if not value:
        return None
    parsed = datetime.datetime.fromisoformat(value)
    # Naive input is read as UTC rather than rejected: a hand-written
    # timestamp is the common case, and comparing naive to aware raises.
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=datetime.timezone.utc)
    return parsed


def main(argv: list | None = None) -> int:
    import argparse
    import json
    import pathlib
    import sys

    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--feature-id", required=True)
    ap.add_argument("--out", required=True, type=pathlib.Path,
                    help="where to write the token record "
                         "(conventionally .govkit/tokens/<feature-key>.json)")
    ap.add_argument("--score", type=float, default=None,
                    help="the rubric's advisory score; omitted is 'not scored'")
    ap.add_argument("--blocker", action="append", default=[],
                    help="a critical blocker, repeatable")
    ap.add_argument("--package-complete", action="store_true")
    ap.add_argument("--draft-version", default=None)
    ap.add_argument("--commitment", default=None,
                    help="the commitment id recorded for this baseline")
    ap.add_argument("--binds-baseline", action="store_true",
                    help="the commitment binds THIS baseline's digest")
    ap.add_argument("--authority", choices=sorted(_AUTHORITY), default="unknown")
    ap.add_argument("--checked-at", default=None,
                    help="when the authority reading was taken")
    ap.add_argument("--now", default=None, help="clock override, for tests")
    ap.add_argument("--no-contract", action="store_true",
                    help="this project has no decision service")
    ap.add_argument("--batch", action="store_true",
                    help="advisory corpus scoring; writes no record")
    a = ap.parse_args(argv)

    now = _moment(a.now) or datetime.datetime.now(datetime.timezone.utc)
    result = assess(
        Facts(
            package_complete=a.package_complete,
            blockers=list(a.blocker),
            score=a.score,
            commitment_id=a.commitment,
            binds_this_baseline=a.binds_baseline,
            authority=_AUTHORITY[a.authority],
            authority_checked_at=_moment(a.checked_at),
            implementation_verified=False,
            now=now,
        ),
        contract=not a.no_contract,
        batch=a.batch,
    )

    for state in sorted(s.value for s in result.states):
        print(f"  {state}")
    print(f"  decision: {result.decision} — {result.reason}")
    print(f"  authoritative: {result.authoritative}")

    try:
        record = to_record(result, feature_id=a.feature_id,
                           draft_version=a.draft_version, ts=now)
    except NotADecision as advisory:
        print(f"  {advisory}", file=sys.stderr)
        return 2

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(f"  wrote {a.out}")

    # A blocked token is exhaust too — it feeds the blocked-token rate — so
    # the record is written either way, and the exit code is what tells a
    # caller which happened.
    return 0 if result.decision == "approved" else 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
