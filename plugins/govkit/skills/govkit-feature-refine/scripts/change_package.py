#!/usr/bin/env python3
"""Build a reapproval request that cannot approve anything.

WHY THIS EXISTS
    The refine skill's "committed behavior" mode already says the right
    thing in prose: review approved text, never rewrite it, turn every
    finding into a proposal a human decides on. This is the artifact those
    proposals become — the thing an authorized owner actually acts on.

    The acceptance criterion is one sentence: *AI can prepare a reapproval
    package without granting itself authority.* Everything below exists to
    make the second half structurally true rather than politely observed.

WHAT IT REFUSES, AND WHY EACH ONE
    - **No field can express an approval.** A package is a request. If it
      can carry something that reads as a decision, something downstream
      eventually reads it as one — and the thing that wrote it was an agent.
    - **No claim of submission.** This script talks to nothing. "Not
      submitted" is the only honest value, so it is the only value.
    - **Both sides of every diff.** You cannot decide on a change you
      cannot see; a proposal with only the new text asks the approver to
      trust that the old text was worse.
    - **Evidence stated, even when absent.** "none — this is a judgement"
      is an acceptable answer; a silent blank is not. The difference is
      whether the approver knows they are taking somebody's word for it.
    - **A reinstated exclusion is named.** An excluded item stays excluded
      until somebody decides otherwise, and a proposal that quietly re-adds
      one is indistinguishable afterwards from behavior someone chose.

WHAT IT DOES NOT DO
    It does not compute the replacement baseline's digest. That is supplied.
    Computing it here would make this script decide what is being approved
    as well as describe it, and the canonicalisation has exactly one
    implementation, which is not this one.
"""

from __future__ import annotations

import re

#: Anything that reads as a decision. Checked against supplied keys *and*
#: nested ones, because the risk is not a caller who reads this list — it is
#: a caller who does not.
_DECISION_SHAPED = re.compile(
    r"approv|authoriz|decision|decided|sign_?off|go_?ahead|user_said|consent",
    re.IGNORECASE,
)

_DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")

REQUIRED = ("ref", "current", "proposed", "why", "evidence")

HOW_TO_DECIDE = (
    "Record this decision through the authenticated decision service. A "
    "statement in a conversation is not an approval of a concrete changed "
    "scope, and nothing in this package may be edited to become one."
)


class Incomplete(ValueError):
    """The request is not something an approver could act on."""


class NotAnApproval(ValueError):
    """Something tried to put a decision inside a request for one."""


def _reject_decision_shaped(payload, where="extra") -> None:
    if isinstance(payload, dict):
        for key, value in payload.items():
            if _DECISION_SHAPED.search(str(key)):
                raise NotAnApproval(
                    f"{where}.{key} reads as a decision. A change package is a "
                    "request; the decision is recorded elsewhere, by someone "
                    "with the authority to make it."
                )
            _reject_decision_shaped(value, f"{where}.{key}")
    elif isinstance(payload, list):
        for index, value in enumerate(payload):
            _reject_decision_shaped(value, f"{where}[{index}]")


def build(
    *,
    replaces_commitment: str,
    changes: list,
    requested_baseline_digest: str,
    dependencies: list | None = None,
    extra: dict | None = None,
) -> dict:
    """Assemble the package, or refuse and say which part is missing."""
    if extra:
        _reject_decision_shaped(extra)

    if not replaces_commitment:
        raise Incomplete(
            "a reapproval request must name the commitment it would replace; "
            "without it this is a new approval wearing the wrong label"
        )

    if not _DIGEST.match(requested_baseline_digest or ""):
        raise Incomplete(
            "requested_baseline_digest must be sha256:<64 lowercase hex> — it is "
            "the handle the decision service binds, and a wrong one produces a "
            "commitment bound to nothing"
        )

    if not changes:
        raise Incomplete("a package with no changes asks for a decision about nothing")

    prepared = []
    reinstated = []
    for index, change in enumerate(changes):
        _reject_decision_shaped(change, f"changes[{index}]")
        missing = [field for field in REQUIRED
                   if not str(change.get(field) or "").strip()]
        if missing:
            raise Incomplete(
                f"changes[{index}] ({change.get('ref', 'no ref')}) is missing "
                f"{', '.join(missing)}"
            )
        if str(change["current"]).strip() == str(change["proposed"]).strip():
            raise Incomplete(
                f"changes[{index}] ({change['ref']}) proposes the text it already "
                "has; reformatting is not a decision anyone needs to make"
            )
        entry = {field: change[field] for field in REQUIRED}
        exclusion = change.get("reinstates_exclusion")
        if exclusion:
            entry["reinstates_exclusion"] = exclusion
            reinstated.append(exclusion)
        prepared.append(entry)

    return {
        "kind": "reapproval_request",
        "replaces_commitment": replaces_commitment,
        "requested_baseline_digest": requested_baseline_digest,
        "changes": prepared,
        "reinstates_exclusions": reinstated,
        "dependencies": list(dependencies or []),
        # Never fabricate writeback success. This script reaches nothing.
        "submitted": False,
        "decision": None,
        "how_to_decide": HOW_TO_DECIDE,
    }


def main(argv: list | None = None) -> int:
    import argparse
    import json
    import pathlib
    import sys

    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--replaces", required=True,
                    help="the commitment id this request would replace")
    ap.add_argument("--changes", required=True, type=pathlib.Path,
                    help="JSON array of proposed changes")
    ap.add_argument("--requested-digest", required=True,
                    help="sha256:<64 hex> of the proposed replacement baseline")
    ap.add_argument("--dependency", action="append", default=[])
    ap.add_argument("--out", required=True, type=pathlib.Path)
    a = ap.parse_args(argv)

    try:
        changes = json.loads(a.changes.read_text(encoding="utf-8"))
    except (OSError, ValueError) as unreadable:
        print(f"  could not read {a.changes}: {unreadable}", file=sys.stderr)
        return 2

    try:
        package = build(
            replaces_commitment=a.replaces,
            changes=changes,
            requested_baseline_digest=a.requested_digest,
            dependencies=a.dependency,
        )
    except (Incomplete, NotAnApproval) as refused:
        # Nothing is written. A half-formed request on disk is worse than
        # none: somebody finds it and submits it.
        print(f"  refused: {refused}", file=sys.stderr)
        return 1

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")
    print(f"  {len(package['changes'])} proposed change(s) -> {a.out}")
    print(f"  not submitted. {HOW_TO_DECIDE}")
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
