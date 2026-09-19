"""Preparing a reapproval package without granting yourself authority — 14B.

Increment 03 gave the refine skill a "committed behavior" mode: review
approved text, never rewrite it, turn every finding into a proposal. That
lives in prose. This is the structured artifact those proposals become — the
thing an authorized owner actually decides on.

The acceptance criterion is one sentence: *AI can prepare a reapproval
package without granting itself authority.* Everything here exists to make
the second half structurally true rather than politely observed.

A note on the fixtures. In 14A nineteen tests passed while four defects were
live, because every one of them drove the code through a single helper
supplying a coherent set of facts — the tests agreed with the code because
both came from the same assumption. So these build their inputs case by
case, and several deliberately supply shapes a careless caller would.
"""

from __future__ import annotations

import pytest


def a_change(**over):
    change = {
        "ref": "support-app/response-approval#scenario:unapproved-blocked",
        "current": "Then the send is refused",
        "proposed": "Then the send is refused and the drafter is notified",
        "why": "the Rule implies notification but no scenario covers it",
        "evidence": "SUP-114, three tickets in the last quarter",
    }
    change.update(over)
    return change


# --- what a package must carry ----------------------------------------------


def test_a_package_names_the_commitment_it_would_replace(change_package):
    """A reapproval request that does not say what it replaces is a new
    approval wearing the wrong label. The replacement linkage is what lets
    the decision service supersede rather than duplicate."""
    package = change_package.build(
        replaces_commitment="cmt-1234",
        changes=[a_change()],
        requested_baseline_digest="sha256:" + "a" * 64,
    )

    assert package["replaces_commitment"] == "cmt-1234"
    assert package["requested_baseline_digest"] == "sha256:" + "a" * 64


def test_every_change_carries_both_sides_of_the_diff(change_package):
    """You cannot decide on a change you cannot see. A proposal with only
    the new text asks the approver to trust that the old text was worse."""
    with pytest.raises(change_package.Incomplete) as refused:
        change_package.build(
            replaces_commitment="cmt-1234",
            changes=[{k: v for k, v in a_change().items() if k != "current"}],
            requested_baseline_digest="sha256:" + "b" * 64,
        )

    assert "current" in str(refused.value)


def test_a_change_that_changes_nothing_is_refused(change_package):
    """Identical text is not a change, and a package full of them dilutes
    the ones that matter until nobody reads the list."""
    with pytest.raises(change_package.Incomplete):
        change_package.build(
            replaces_commitment="cmt-1234",
            changes=[a_change(proposed="Then the send is refused")],
            requested_baseline_digest="sha256:" + "c" * 64,
        )


def test_whitespace_is_not_a_change_either(change_package):
    """Reformatting is not a decision anyone needs to make."""
    with pytest.raises(change_package.Incomplete):
        change_package.build(
            replaces_commitment="cmt-1234",
            changes=[a_change(proposed="  Then the send is refused  ")],
            requested_baseline_digest="sha256:" + "d" * 64,
        )


def test_a_package_with_no_changes_is_refused(change_package):
    """Nothing to decide. An empty reapproval request still consumes an
    approver's attention and still produces a decision record."""
    with pytest.raises(change_package.Incomplete):
        change_package.build(
            replaces_commitment="cmt-1234",
            changes=[],
            requested_baseline_digest="sha256:" + "e" * 64,
        )


def test_missing_evidence_must_be_stated_rather_than_omitted(change_package):
    """"none — this is a judgement" is an acceptable answer and a silent
    blank is not. The difference is whether the approver knows they are
    being asked to take somebody's word for it."""
    with pytest.raises(change_package.Incomplete) as refused:
        change_package.build(
            replaces_commitment="cmt-1234",
            changes=[{k: v for k, v in a_change().items() if k != "evidence"}],
            requested_baseline_digest="sha256:" + "f" * 64,
        )

    assert "evidence" in str(refused.value)


def test_an_explicit_judgement_is_accepted(change_package):
    package = change_package.build(
        replaces_commitment="cmt-1234",
        changes=[a_change(evidence="none — this is a judgement")],
        requested_baseline_digest="sha256:" + "0" * 64,
    )

    assert package["changes"][0]["evidence"].startswith("none")


def test_reinstating_an_exclusion_has_to_say_so(change_package):
    """"An excluded item stays excluded" unless somebody decides otherwise.
    A proposal that quietly re-adds one is the same act as adding
    unapproved behavior, and is indistinguishable afterwards."""
    package = change_package.build(
        replaces_commitment="cmt-1234",
        changes=[a_change(reinstates_exclusion="bulk-send")],
        requested_baseline_digest="sha256:" + "1" * 64,
    )

    assert package["changes"][0]["reinstates_exclusion"] == "bulk-send"
    assert package["reinstates_exclusions"] == ["bulk-send"]


# --- what it structurally cannot say ----------------------------------------


@pytest.mark.parametrize(
    "field",
    ["approved", "decision", "authorized", "authorizes_work", "approved_by"],
)
def test_no_approval_can_be_expressed_in_a_package(change_package, field):
    """The point of the whole increment. A package is a *request*; if it can
    carry a field that reads as a decision, then somewhere downstream
    something will read it as one — and the thing that wrote it was an
    agent."""
    with pytest.raises(change_package.NotAnApproval):
        change_package.build(
            replaces_commitment="cmt-1234",
            changes=[a_change()],
            requested_baseline_digest="sha256:" + "2" * 64,
            extra={field: True},
        )


def test_a_package_records_that_it_has_not_been_submitted(change_package):
    """Never fabricate writeback success. This script talks to nothing, so
    the honest value is the only value it can write."""
    package = change_package.build(
        replaces_commitment="cmt-1234",
        changes=[a_change()],
        requested_baseline_digest="sha256:" + "3" * 64,
    )

    assert package["submitted"] is False
    assert package["decision"] is None


def test_the_package_says_where_the_decision_has_to_be_made(change_package):
    """A request nobody knows how to act on gets acted on informally, which
    is the failure mode this replaces."""
    package = change_package.build(
        replaces_commitment="cmt-1234",
        changes=[a_change()],
        requested_baseline_digest="sha256:" + "4" * 64,
    )

    assert "authenticated" in package["how_to_decide"].lower()


def test_conversational_assent_is_not_accepted_as_a_decision(change_package):
    """"sounds good, go ahead" in a chat window is not an approval of a
    concrete changed scope, and a package that could record it would make
    the two indistinguishable in the record."""
    with pytest.raises(change_package.NotAnApproval):
        change_package.build(
            replaces_commitment="cmt-1234",
            changes=[a_change()],
            requested_baseline_digest="sha256:" + "5" * 64,
            extra={"user_said": "sounds good, go ahead"},
        )


# --- the digest -------------------------------------------------------------


@pytest.mark.parametrize(
    "digest",
    ["", "sha256:short", "a" * 64, "sha256:" + "A" * 64, "md5:" + "a" * 32],
)
def test_a_malformed_replacement_digest_is_refused(change_package, digest):
    """It is the handle the decision service binds. A wrong one produces a
    commitment bound to nothing, which reads as approved and verifies
    against nothing."""
    with pytest.raises(change_package.Incomplete):
        change_package.build(
            replaces_commitment="cmt-1234",
            changes=[a_change()],
            requested_baseline_digest=digest,
        )


def test_the_package_does_not_compute_the_digest_itself(change_package):
    """It is supplied, and deliberately. Computing it here would mean this
    script decides what is being approved as well as describing it, and the
    canonicalisation already has exactly one implementation elsewhere."""
    assert not hasattr(change_package, "compute_digest")


# --- runnable ---------------------------------------------------------------


def test_it_has_a_command_line(change_package):
    assert callable(getattr(change_package, "main", None))


def test_running_it_writes_the_package(change_package, tmp_path):
    import json

    source = tmp_path / "changes.json"
    source.write_text(json.dumps([a_change()]), encoding="utf-8")
    out = tmp_path / "package.json"

    code = change_package.main([
        "--replaces", "cmt-1234", "--changes", str(source),
        "--requested-digest", "sha256:" + "6" * 64, "--out", str(out),
    ])

    written = json.loads(out.read_text(encoding="utf-8"))
    assert code == 0
    assert written["submitted"] is False
    assert written["replaces_commitment"] == "cmt-1234"


def test_a_refused_package_is_not_written(change_package, tmp_path):
    """A half-written request on disk is worse than none: somebody finds it
    and submits it."""
    import json

    source = tmp_path / "changes.json"
    source.write_text(json.dumps([a_change(proposed="Then the send is refused")]),
                      encoding="utf-8")
    out = tmp_path / "package.json"

    code = change_package.main([
        "--replaces", "cmt-1234", "--changes", str(source),
        "--requested-digest", "sha256:" + "7" * 64, "--out", str(out),
    ])

    assert code != 0
    assert not out.exists()
