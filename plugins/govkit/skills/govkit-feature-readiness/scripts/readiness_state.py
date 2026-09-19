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
    result = Readiness(blockers=list(facts.blockers))

    if facts.package_complete:
        result.states.add(State.PREPARED)
    if not facts.blockers:
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
    elif not contract:
        result.decision = "approved"
        result.reason = "no decision service is configured for this project"
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
        result.authoritative = State.AUTHORITY_VERIFIED in result.states and not facts.blockers
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


def to_record(result: Readiness, *, feature_id: str) -> dict:
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
        "blockers": list(result.blockers),
        # Says what this record *is*, so it cannot be filed as evidence that
        # somebody approved the behavior.
        "kind": "execution_readiness",
        "authoritative": result.authoritative,
        "product_approval": approval,
        "states": sorted(s.value for s in result.states),
        "reason": result.reason,
    }
