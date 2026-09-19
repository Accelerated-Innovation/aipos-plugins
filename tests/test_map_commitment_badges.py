"""The map has to say which commitment is blocked — increment 14C.

A feature map is where somebody looks to find out where delivery stands.
Until now the strongest thing a card could say was a Development Token
decision, which is a *local* readiness verdict. Under a behavior contract
the more urgent fact is often elsewhere: this feature's commitment was
invalidated, so nothing here can merge until it is reapproved — and a map
that cannot show that sends people to read CI logs instead.

Two acceptance criteria meet here: *maps identify which commitment is
blocked*, and *batch map badges remain advisory and visibly labeled*.

Asserted against rendered HTML, per this repository's convention and for
the reason `test_render_map.py` states: a renderer that drops what
ingestion preserved is the same defect with an extra step.
"""

import re

import pytest


def strip_tags(s):
    return re.sub(r"<[^>]+>", " ", s)


def scored(decision="Approved", **commitment):
    """One feature's score record, optionally carrying commitment state.

    Note the vocabulary: map score records use `"Approved"`, while the
    token record written by `govkit-feature-readiness` uses `"approved"`.
    Two spellings of one decision is its own small hazard, recorded here
    rather than silently normalised by a test.
    """
    record = {
        "decision": decision,
        "score": 10.0,
        "blockers": [],
        "edits": [],
        "summary": "ready",
        "dimensions": [],
    }
    if commitment:
        record["commitment"] = commitment
    return record


def render(render_map, feats, scores):
    return render_map.render(feats, scores, {}, {})


# --- which commitment, and whether it is blocked ----------------------------


def test_a_blocked_commitment_is_named_on_the_card(render_map, ingested):
    """"Blocked" without an identifier sends somebody to guess. The whole
    value is being able to go and look at *that* commitment."""
    feature = ingested["inv_full"]
    out = render(render_map, [feature], {feature["key"]: scored(
        commitment_id="cmt-42761531", authorizes_work=False,
        reason="COMMITMENT_INVALIDATED",
    )})

    text = strip_tags(out)
    assert "cmt-42761531" in text
    assert "COMMITMENT_INVALIDATED" in text


def test_a_blocked_commitment_is_distinguishable_from_a_blocked_token(
    render_map, ingested
):
    """They are different failures with different fixes. A blocked token
    means the package is not ready; a blocked commitment means the approval
    is gone, and editing the package will not help."""
    feature = ingested["inv_full"]
    out = render(render_map, [feature], {feature["key"]: scored(
        decision="Approved",
        commitment_id="cmt-999", authorizes_work=False, reason="COMMITMENT_SUPERSEDED",
    )})

    text = strip_tags(out).lower()
    assert "commitment" in text
    # The token itself still reads approved — the card must not rewrite one
    # verdict into the other.
    assert "approved" in text


def test_a_current_commitment_is_shown_without_alarm(render_map, ingested):
    """A healthy commitment is the common case. Rendering it as a warning
    trains people to ignore the colour that matters."""
    feature = ingested["inv_full"]
    # A read time is part of a healthy record now: an untimed `True` is
    # deliberately not the confident green (see the untimed test below).
    out = render(render_map, [feature], {feature["key"]: scored(
        commitment_id="cmt-1", authorizes_work=True, reason=None,
        checked_at="2026-09-19T12:00:00Z",
    )})

    assert "cmt-1" in strip_tags(out)
    # Asserted on the rendered element, not on the string appearing
    # anywhere. A word search catches the filter legend's "Token blocked";
    # a bare `"cmt-block" not in out` catches the stylesheet, which defines
    # every class the page can use. Absence assertions against a whole
    # document need an anchor, and this is the third one in this file that
    # did not have one.
    assert 'class="cmt cmt-ok"' in out
    assert 'class="cmt cmt-block"' not in out


def test_an_unverifiable_commitment_is_not_shown_as_authorized(render_map, ingested):
    """Could-not-determine, all the way to the pixel. A map that renders an
    outage as a green chip is the cached-authority failure with a nicer
    font."""
    feature = ingested["inv_full"]
    out = render(render_map, [feature], {feature["key"]: scored(
        commitment_id="cmt-2", authorizes_work=None, reason="unreachable",
    )})

    text = strip_tags(out).lower()
    assert "unverified" in text or "could not" in text


def test_a_feature_with_no_commitment_renders_no_chip(render_map, ingested):
    """Most projects have none, and their maps must not grow an empty
    column that implies something is missing.

    Asserted on the chip's own class rather than the word: the page's
    existing advisory note already says "not a commitment", so a word
    search here would fail for the wrong reason and keep failing.
    """
    feature = ingested["inv_full"]
    out = render(render_map, [feature], {feature["key"]: scored()})

    assert 'class="cmt' not in out


# --- advisory, visibly ------------------------------------------------------


def test_the_commitment_chip_says_when_it_was_read(render_map, ingested):
    """A map is a snapshot rendered at some past moment. Without the time,
    a green chip is indistinguishable from a fresh check — which is the
    stale-authority problem, moved into a dashboard."""
    feature = ingested["inv_full"]
    out = render(render_map, [feature], {feature["key"]: scored(
        commitment_id="cmt-3", authorizes_work=True, checked_at="2026-09-19T12:00:00Z",
    )})

    assert "2026-09-19" in strip_tags(out)


def test_the_map_says_its_authority_view_is_a_snapshot(render_map, ingested):
    """Stated once, near the badges, rather than assumed. The map cannot
    re-check anything, and a reader has no way to know that from a chip."""
    feature = ingested["inv_full"]
    out = render(render_map, [feature], {feature["key"]: scored(
        commitment_id="cmt-4", authorizes_work=True, checked_at="2026-09-19T12:00:00Z",
    )})

    text = strip_tags(out).lower()
    assert "snapshot" in text
    assert "not a gate" in text or "does not gate" in text


# --- what the first version got wrong ---------------------------------------


def test_authority_with_no_read_time_is_not_shown_as_authorized(render_map, ingested):
    """The chip argued that a green badge without a timestamp is
    indistinguishable from a fresh check — and then rendered exactly that
    when `checked_at` was absent.

    A reading whose freshness cannot be assessed is not a verified one.
    14A settled this for the token: past the window it is execution
    readiness only. The pixel has to agree.
    """
    feature = ingested["inv_full"]
    out = render(render_map, [feature], {feature["key"]: scored(
        commitment_id="cmt-5", authorizes_work=True,
    )})

    assert 'class="cmt cmt-ok"' not in out
    assert "cmt-5" in strip_tags(out)
    assert "read time unknown" in strip_tags(out).lower()


def test_authority_with_a_read_time_still_reads_as_authorized(render_map, ingested):
    """The fix must not make the healthy case unrepresentable."""
    feature = ingested["inv_full"]
    out = render(render_map, [feature], {feature["key"]: scored(
        commitment_id="cmt-6", authorizes_work=True, checked_at="2026-09-19T12:00:00Z",
    )})

    assert 'class="cmt cmt-ok"' in out


@pytest.mark.parametrize(
    "commitment",
    ["a string", 42, ["a", "list"], None],
)
def test_a_malformed_commitment_block_does_not_abort_the_render(
    render_map, ingested, commitment
):
    """Score files are agent-produced. `c.get` on a string raises
    AttributeError and takes the whole page with it — one bad record and
    nobody sees any of the map."""
    feature = ingested["inv_full"]
    record = scored()
    record["commitment"] = commitment

    out = render(render_map, [feature], {feature["key"]: record})

    assert "<html" in out.lower()
    assert 'class="cmt' not in out


def test_an_unhashable_authority_value_does_not_abort_the_render(render_map, ingested):
    """`CMTCLS.get(["yes"])` raises TypeError, not a KeyError — a dict
    lookup is only total over hashable keys, which is easy to forget when
    the values are supposed to be True/False/None."""
    feature = ingested["inv_full"]
    out = render(render_map, [feature], {feature["key"]: scored(
        commitment_id="cmt-7", authorizes_work=["yes"],
    )})

    assert "<html" in out.lower()
    text = strip_tags(out).lower()
    assert "unverified" in text
