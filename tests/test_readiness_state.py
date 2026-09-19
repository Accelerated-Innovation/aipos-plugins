"""A Development Token is derived, not granted — increment 14.

Until now the token was the whole decision: local blockers and an advisory
score, and "Approved" meant a person could start coding. Under a behavior
contract that is only ever half the question. The other half — *is this
scope approved, and does that approval still hold* — lives in the decision
service and cannot be read from the repository at all.

So the token becomes a **derived execution-readiness record that references
the product approval**, and the states stay apart:

- **prepared** — a package exists locally; nobody has decided anything
- **approved for exact scope** — a commitment binds this exact baseline
- **locally executable** — the local readiness gate finds no blockers
- **authority verified** — a *fresh* read says that approval still authorizes
- **implementation verified** — the behavior was afterwards shown to work

The acceptance criteria this file exists to hold: a stale approval cannot
yield an authoritative green result, and local preparation is never
presented as a recorded approval.
"""

from __future__ import annotations

import datetime

import pytest

NOW = datetime.datetime(2026, 9, 19, 12, 0, tzinfo=datetime.timezone.utc)


def facts(state_mod, **over):
    """A package that is locally clean and currently authorized."""
    base = dict(
        package_complete=True,
        blockers=[],
        commitment_id="cmt-1234",
        binds_this_baseline=True,
        authority=True,
        authority_checked_at=NOW - datetime.timedelta(minutes=5),
        implementation_verified=False,
        now=NOW,
    )
    base.update(over)
    return state_mod.Facts(**base)


# --- the states are distinct ------------------------------------------------


def test_a_local_package_with_no_decision_is_prepared_not_approved(readiness_state):
    """The failure this prevents: a team reads "Approved" on a token and
    believes a product decision was made. Nothing local can make that true.
    """
    result = readiness_state.assess(facts(
        readiness_state, commitment_id=None, binds_this_baseline=False,
        authority=None, authority_checked_at=None,
    ))

    assert readiness_state.State.PREPARED in result.states
    assert readiness_state.State.APPROVED_FOR_SCOPE not in result.states
    assert readiness_state.State.AUTHORITY_VERIFIED not in result.states


def test_local_cleanliness_alone_is_executable_not_authorized(readiness_state):
    """Locally executable and authority verified are orthogonal, and the
    common mistake is to collapse them: a clean package is *ready to run*,
    which says nothing about whether anyone approved the behavior."""
    result = readiness_state.assess(facts(
        readiness_state, commitment_id=None, binds_this_baseline=False,
        authority=None, authority_checked_at=None,
    ))

    assert readiness_state.State.LOCALLY_EXECUTABLE in result.states
    assert readiness_state.State.AUTHORITY_VERIFIED not in result.states


def test_a_recorded_commitment_that_binds_this_baseline_is_approved_for_scope(
    readiness_state,
):
    result = readiness_state.assess(facts(readiness_state))

    assert readiness_state.State.APPROVED_FOR_SCOPE in result.states


def test_a_commitment_binding_something_else_does_not_approve_this_scope(
    readiness_state,
):
    """"Approved for *exact* scope". A commitment that exists but binds a
    different baseline is somebody else's decision, and counting it is the
    borrowed-approval failure the digest comparison exists to catch."""
    result = readiness_state.assess(facts(readiness_state, binds_this_baseline=False))

    assert readiness_state.State.APPROVED_FOR_SCOPE not in result.states


def test_implementation_verified_is_its_own_state(readiness_state):
    """Ready to implement, automated, and verified passing are three
    different things. This gate runs nothing, so it can never assert the
    third from its own evidence."""
    before = readiness_state.assess(facts(readiness_state))
    after = readiness_state.assess(facts(readiness_state, implementation_verified=True))

    assert readiness_state.State.IMPLEMENTATION_VERIFIED not in before.states
    assert readiness_state.State.IMPLEMENTATION_VERIFIED in after.states


# --- the derived token ------------------------------------------------------


def test_a_clean_and_currently_authorized_package_is_approved(readiness_state):
    result = readiness_state.assess(facts(readiness_state))

    assert result.decision == "approved"
    assert result.authoritative is True


def test_a_blocker_blocks_regardless_of_authority(readiness_state):
    result = readiness_state.assess(facts(readiness_state, blockers=["no evidence path"]))

    assert result.decision == "blocked"


def test_a_withdrawn_approval_blocks_a_locally_perfect_package(readiness_state):
    """The invalidation path, at the start of work rather than at merge."""
    result = readiness_state.assess(facts(readiness_state, authority=False))

    assert result.decision == "blocked"
    assert "authoriz" in result.reason.lower()


def test_an_unreachable_decision_service_is_not_an_authoritative_green(readiness_state):
    """Undetermined is neither approval nor rejection. It must not block a
    developer from preparing — but the result it produces cannot be the one
    a protected boundary would accept."""
    result = readiness_state.assess(facts(
        readiness_state, authority=None, authority_checked_at=None,
    ))

    assert result.authoritative is False
    assert result.decision != "blocked"


def test_a_stale_check_cannot_yield_an_authoritative_green(readiness_state):
    """The acceptance criterion, in one test. A check from last week proves
    what was true last week; an approval can be withdrawn in between, and a
    token that keeps saying yes is exactly the cached-authority failure the
    whole contract exists to prevent."""
    fresh = readiness_state.assess(facts(readiness_state))
    stale = readiness_state.assess(facts(
        readiness_state,
        authority_checked_at=NOW - datetime.timedelta(days=7),
    ))

    assert fresh.authoritative is True
    assert stale.authoritative is False
    assert "stale" in stale.reason.lower()


def test_freshness_is_measured_against_the_supplied_clock(readiness_state):
    """No hidden `utcnow()`. A check that reads the wall clock cannot be
    tested for the boundary it enforces, and this one is a boundary."""
    just_inside = readiness_state.assess(facts(
        readiness_state,
        authority_checked_at=NOW - readiness_state.FRESHNESS + datetime.timedelta(seconds=30),
    ))
    just_outside = readiness_state.assess(facts(
        readiness_state,
        authority_checked_at=NOW - readiness_state.FRESHNESS - datetime.timedelta(seconds=30),
    ))

    assert just_inside.authoritative is True
    assert just_outside.authoritative is False


def test_a_check_dated_in_the_future_is_not_trusted(readiness_state):
    """A clock skew or a hand-edited record should not buy freshness."""
    result = readiness_state.assess(facts(
        readiness_state, authority_checked_at=NOW + datetime.timedelta(hours=1),
    ))

    assert result.authoritative is False


# --- a project with no decision service -------------------------------------


def test_a_project_without_a_pdg_still_gets_a_token(readiness_state):
    """Most projects using GovKit have no decision service. The token keeps
    working for them exactly as before — it simply never claims to carry a
    product approval."""
    result = readiness_state.assess(facts(
        readiness_state, commitment_id=None, binds_this_baseline=False,
        authority=None, authority_checked_at=None,
    ), contract=False)

    assert result.decision == "approved"
    assert result.carries_product_approval is False


def test_a_token_never_claims_the_approval_it_did_not_read(readiness_state):
    """`carries_product_approval` is the field that stops a token being
    filed as evidence that somebody approved the behavior."""
    contracted = readiness_state.assess(facts(readiness_state))
    uncontracted = readiness_state.assess(facts(
        readiness_state, commitment_id=None, binds_this_baseline=False,
        authority=None, authority_checked_at=None,
    ), contract=False)

    assert contracted.carries_product_approval is True
    assert uncontracted.carries_product_approval is False


# --- the record written to disk ---------------------------------------------


def test_the_record_names_the_approval_it_derives_from(readiness_state):
    """A derived record that does not say what it derives from is just an
    assertion. The commitment id and the time it was read are what make the
    token auditable after the fact."""
    record = readiness_state.to_record(readiness_state.assess(facts(readiness_state)),
                                       feature_id="AI-124")

    assert record["kind"] == "execution_readiness"
    assert record["product_approval"]["commitment_id"] == "cmt-1234"
    assert record["product_approval"]["verified_at"].startswith("2026-09-19")


def test_the_record_keeps_the_existing_fields_metrics_read(readiness_state):
    """`govkit-metrics-emit` reads `decision`, and refinement lead time and
    blocked-token rate are computed from it. Renaming or dropping it to make
    room for the new fields would silently zero both."""
    record = readiness_state.to_record(readiness_state.assess(facts(readiness_state)),
                                       feature_id="AI-124")

    assert record["feature_id"] == "AI-124"
    assert record["decision"] in {"approved", "approved_with_edits", "blocked"}
    assert "blockers" in record


def test_an_uncontracted_record_says_so_rather_than_omitting_it(readiness_state):
    """Absent would read as "not recorded yet" to a later reader. Explicit
    `null` says the question was asked and the project has no answer."""
    record = readiness_state.to_record(
        readiness_state.assess(facts(
            readiness_state, commitment_id=None, binds_this_baseline=False,
            authority=None, authority_checked_at=None,
        ), contract=False),
        feature_id="AI-124",
    )

    assert "product_approval" in record
    assert record["product_approval"] is None


# --- batch mode -------------------------------------------------------------


def test_batch_results_are_advisory_and_say_so(readiness_state):
    """Batch scores a corpus; it decides nothing. A badge that looks like a
    decision is one somebody will cite as if it were."""
    result = readiness_state.assess(facts(readiness_state), batch=True)

    assert result.advisory is True
    assert result.authoritative is False


def test_batch_mode_writes_no_record(readiness_state):
    result = readiness_state.assess(facts(readiness_state), batch=True)

    with pytest.raises(readiness_state.NotADecision):
        readiness_state.to_record(result, feature_id="AI-124")
