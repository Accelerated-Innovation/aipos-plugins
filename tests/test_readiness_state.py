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
        score=10.5,
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
    """`aipos-metrics-emit` reads `decision`, and refinement lead time and
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


# --- what the derivation was ignoring ---------------------------------------
#
# Five review findings, all the same species: the states were derived
# carefully and the *decision* was derived from a subset of them.


def test_authority_without_a_bound_commitment_does_not_approve(readiness_state):
    """`AUTHORITY_VERIFIED` required `approved_for_scope`; the decision did
    not. A fresh `authority=True` for a commitment that binds something else
    therefore produced `approved` with a reason saying the approval covers
    this scope — and `to_record` persisted it while omitting the very state
    that would have contradicted it."""
    result = readiness_state.assess(facts(readiness_state, binds_this_baseline=False))

    assert result.decision != "approved"
    assert result.authoritative is False


def test_no_commitment_at_all_does_not_approve_under_a_contract(readiness_state):
    result = readiness_state.assess(facts(readiness_state, commitment_id=None))

    assert result.decision != "approved"


def test_an_incomplete_package_is_never_a_green_token(readiness_state):
    """Package completeness is step 1 of the readiness process, and it was
    wired only to the `PREPARED` state — so an incomplete package with an
    empty blocker list produced an approved, authoritative token."""
    result = readiness_state.assess(facts(readiness_state, package_complete=False))

    assert result.decision == "blocked"
    assert result.authoritative is False
    assert readiness_state.State.LOCALLY_EXECUTABLE not in result.states


def test_the_score_bands_from_the_rubric_are_applied(readiness_state):
    """The decision model is blockers *and* score. Deriving from blockers
    alone let any blocker-free package through, including ones below 8.5
    that the rubric requires to be blocked."""
    strong = readiness_state.assess(facts(readiness_state, score=10.5))
    edits = readiness_state.assess(facts(readiness_state, score=9.0))
    weak = readiness_state.assess(facts(readiness_state, score=8.0))

    assert strong.decision == "approved"
    assert edits.decision == "approved_with_edits"
    assert weak.decision == "blocked"


def test_a_missing_score_does_not_silently_pass(readiness_state):
    """`None` is "not scored", which is not the same as "scored well". The
    gate says so rather than assuming the best."""
    result = readiness_state.assess(facts(readiness_state, score=None))

    assert result.decision == "approved_with_edits"
    assert "score" in result.reason.lower()


def test_the_record_keeps_score_draft_version_and_timestamp(readiness_state):
    """The original record carried these and `aipos-metrics-emit` reserves
    them for the token event. Dropping them while the documentation said
    every original field was unchanged is the kind of claim that survives
    review because nobody diffs a JSON example."""
    record = readiness_state.to_record(
        readiness_state.assess(facts(readiness_state, score=10.5)),
        feature_id="AI-124", draft_version="draft-1", ts=NOW,
    )

    assert record["score"] == 10.5
    assert record["draft_version"] == "draft-1"
    assert record["ts"].startswith("2026-09-19")


# --- it has to be runnable --------------------------------------------------


def test_the_script_has_a_command_line_entry_point(readiness_state):
    """A checker only the tests call is the dead-code failure: the skill
    instructs an agent to derive the states and write the record, and
    without an entry point following that instruction executes none of the
    safeguards."""
    assert callable(getattr(readiness_state, "main", None))


def test_running_it_writes_the_token_record(readiness_state, tmp_path):
    out = tmp_path / "AI-124.json"
    code = readiness_state.main([
        "--feature-id", "AI-124", "--score", "10.5",
        "--commitment", "cmt-1234", "--binds-baseline",
        "--authority", "verified", "--checked-at", NOW.isoformat(),
        "--now", NOW.isoformat(), "--package-complete",
        "--out", str(out),
    ])

    import json
    written = json.loads(out.read_text(encoding="utf-8"))
    assert code == 0
    assert written["decision"] == "approved"
    assert written["product_approval"]["commitment_id"] == "cmt-1234"


def test_running_it_on_a_blocked_package_still_writes_and_exits_nonzero(
    readiness_state, tmp_path
):
    """A blocked token is exhaust too — it feeds the blocked-token rate — so
    the record is written either way. The exit code is what tells a caller
    which happened."""
    out = tmp_path / "AI-125.json"
    code = readiness_state.main([
        "--feature-id", "AI-125", "--score", "10.5", "--package-complete",
        "--blocker", "no evidence path for scenario:x",
        "--authority", "unknown", "--now", NOW.isoformat(),
        "--out", str(out),
    ])

    import json
    assert code != 0
    assert json.loads(out.read_text(encoding="utf-8"))["decision"] == "blocked"


def test_batch_mode_refuses_to_write_from_the_command_line(readiness_state, tmp_path):
    out = tmp_path / "AI-126.json"
    code = readiness_state.main([
        "--feature-id", "AI-126", "--score", "10.5", "--package-complete",
        "--authority", "verified", "--commitment", "cmt-1", "--binds-baseline",
        "--checked-at", NOW.isoformat(), "--now", NOW.isoformat(),
        "--batch", "--out", str(out),
    ])

    assert code != 0
    assert not out.exists()
