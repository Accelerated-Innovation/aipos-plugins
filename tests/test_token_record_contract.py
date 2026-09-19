"""The token record and the event that reads it must not drift — 14C.

`govkit-feature-readiness` writes `.govkit/tokens/<feature-id>.json`.
`govkit-metrics-emit` reserves `refinement.token.issued` to read it, and
names the fields it will take. Those are two skills, two files and two
authors-in-time, with nothing between them but a sentence in a reference
document.

Increment 14A very nearly broke it: the first version of `to_record`
dropped `score`, `draft_version` and `ts` while its documentation said
every original field was unchanged. The review caught that. This test is so
the next one does not need to.

It reads the reserved field list out of the reference document rather than
restating it, because a copy here would drift from the contract exactly as
easily as the code did.
"""

from __future__ import annotations

import datetime
import pathlib
import re

import pytest

from skill_paths import skill_path

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCHEMA = (skill_path("govkit-metrics-emit")
          / "references" / "event_schema.md")

NOW = datetime.datetime(2026, 9, 19, 12, 0, tzinfo=datetime.timezone.utc)


def reserved_fields() -> set:
    """The field names `refinement.token.issued` says it will read."""
    text = SCHEMA.read_text(encoding="utf-8")
    section = text.split("## refinement.token.issued")[1].split("\n## ")[0]
    line = next(ln for ln in section.splitlines() if ln.startswith("Fields"))
    # Everything in backticks on the Fields line and its continuation.
    tail = section[section.index(line):].split("\n\n")[0]
    return {name.strip("[]") for name in re.findall(r"`([a-z_]+)(?:\[\])?`", tail)}


def test_the_reference_actually_names_fields(readiness_state):
    """Guard the guard. If the parse above silently returned nothing, every
    assertion below would pass against an empty set."""
    assert len(reserved_fields()) >= 5


def test_every_reserved_field_is_present_in_the_record(readiness_state):
    record = readiness_state.to_record(
        readiness_state.assess(readiness_state.Facts(
            package_complete=True, blockers=[], score=10.5,
            commitment_id="cmt-1", binds_this_baseline=True, authority=True,
            authority_checked_at=NOW, implementation_verified=False, now=NOW,
        )),
        feature_id="AI-124", draft_version="draft-1", ts=NOW,
    )

    missing = reserved_fields() - set(record)
    assert not missing, f"the token record no longer carries {sorted(missing)}"


def test_a_blocked_record_carries_them_too(readiness_state):
    """A blocked token is exhaust — it feeds the blocked-token rate — so
    the event can read it, and the fields cannot be conditional on the
    happy path."""
    record = readiness_state.to_record(
        readiness_state.assess(readiness_state.Facts(
            package_complete=True, blockers=["no evidence path"], score=6.0,
            commitment_id=None, binds_this_baseline=False, authority=None,
            authority_checked_at=None, implementation_verified=False, now=NOW,
        )),
        feature_id="AI-125", draft_version="draft-1", ts=NOW,
    )

    assert not reserved_fields() - set(record)
    assert record["decision"] == "blocked"


@pytest.mark.parametrize("decision", ["approved", "approved_with_edits", "blocked"])
def test_the_decision_vocabulary_matches_what_the_event_declares(decision):
    """The event declares `approved|approved_with_edits|blocked`. The map's
    score records spell the same decisions `Approved` / `Approved with
    edits` / `Blocked`, which is a real and separate hazard — but the token
    record must match the event that reads it."""
    section = SCHEMA.read_text(encoding="utf-8").split("## refinement.token.issued")[1]

    assert decision in section.split("\n## ")[0]


def test_the_contract_still_declares_all_six_fields():
    """The guard above only checked that *something* parsed, so deleting a
    field from the reference document shrank the expected set and every
    other test kept passing against the shorter one.

    This is the one place the six are written down twice on purpose: the
    other tests derive their expectation from the document, and this pins
    the document itself. A contract test whose expectation moves with the
    thing it tests is not a contract test.
    """
    assert reserved_fields() == {
        "feature_id", "decision", "score", "blockers", "draft_version", "ts",
    }
