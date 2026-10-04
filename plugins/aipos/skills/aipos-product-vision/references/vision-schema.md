# vision.json schema

The record. Everything the skill and a screen show is a view of it; nothing is stored twice.

Location: `product-vision/<slug>/vision.json`. The verifier writes a `computed` block with `--write`;
nothing else writes computed values.

## Top level

```json
{
  "schema_version": "2.0",
  "slug": "claims-triage",
  "title": "Claims triage agent",
  "pass_type": "new",
  "scope": "new",
  "status": "draft",
  "version": "0.6",
  "supersedes": null,
  "product_lead": { "name": "Dana Okoye" },
  "accountable_owner": { "name": "Marcus Hale", "role": "Director of Product" },
  "opportunity_ref": { "id": "OPP-241", "accepted": true, "source": "pdg" },
  "no_opportunity_note": null,
  "parent_vision_ref": null,
  "blocks": {},
  "measures": [],
  "triage": {},
  "learn_mode": null,
  "reviews": [],
  "gaps": [],
  "changes": [],
  "rounds": 0,
  "confidence": null,
  "ratified_by": null,
  "ratified_at": null,
  "computed": {}
}
```

| Field | Notes |
|---|---|
| `pass_type` | `new` or `revision`. The pass, not the mode. A revision requires `supersedes` |
| `scope` | `new`, `increment` or `revision`, recorded by the Step 0 test. **Not a selection** |
| `status` | `draft` → `in_review` → `ratified`. Only a named person reaches ratified |
| `opportunity_ref` / `no_opportunity_note` | One or the other. A new vision with no accepted opportunity is legitimate; the note is what keeps it visible |
| `parent_vision_ref` | Required when scope is `increment` (check S1) |
| `learn_mode` | Its **presence** puts the record in Learn mode. Its validity is check L1 |
| `rounds` | Review rounds opened, not reviewers contacted |
| `confidence` | The Product Lead's 0–100 self-report. Shown to the owner, never gates |
| `computed` | Written by the verifier only. Never hand-edited |

## blocks

Keyed by question id from `data/flow-content.json`, so the skill and a screen write the same shape.
A missing key is not-yet-answered, and the check that reads it fails — unless the current mode and
scope combination does not ask it, in which case the check reports `n/a`.

```json
"blocks": {
  "A1": "Leaders working to adopt and scale AI across their business or area of responsibility.",
  "A2": "More than one, and we build for the business leader rather than the AI specialist.",
  "A3": "They see the opportunity AI presents but are not sure what is needed to use it responsibly.",
  "A4": { "value": "critical", "why": "They see AI's potential to transform the business, and the risk of doing it poorly." },
  "A5": "They ask ChatGPT or Claude, search the web, or go to IT.",
  "A6": "Competitive exposure if they are slow, and personal credibility if they get it wrong.",
  "A7": { "value": "no", "how": null, "basis": "inferred" },
  "A8": [
    { "claim": "They go to ChatGPT and the internet today", "basis": "known", "source": "Discovery sessions, Q3" },
    { "claim": "Personal credibility is what is at stake", "basis": "inferred", "source": null },
    { "claim": "Nobody has made a formal attempt", "basis": "gap", "source": null }
  ],
  "A9": { "as_it_came": "…", "as_product_states_it": "…", "source_group": "…", "what_changed": "…" },
  "B00": { "outcome": "Growth and Customer Experience", "none_committed": false },
  "B0": {
    "categories": [
      { "id": "revenue", "value": "yes", "why": "A high-margin way to generate revenue." },
      { "id": "market_position", "value": "yes", "why": "A robust set of accelerators positions us as experts." },
      { "id": "other", "value": "yes", "name": "Land and expand", "why": "A strong first engagement." }
    ],
    "ranking": ["revenue", "market_position", "other"]
  },
  "B1": { "figures": [{ "value": "1.8M annual handling cost", "source": "FY26 ops budget" }],
          "gap": null },
  "C2": { "arc": "Year one …", "mvp_proves": "That situational retrieval is good enough that …" },
  "F1": { "stem": "…", "focus_areas": ["…", "…", "…"] },
  "F2": true
}
```

`B1` with no figures carries `gap: {text, owner}` instead — V4 fails an unowned gap, because a gap
with no owner is a note rather than a plan to close it.

| Block key | Shape |
|---|---|
| `A1`, `A2`, `A3`, `A5`, `A6` | strings |
| `A4` | object `{value, why}`; `value` is `critical`, `high`, `medium`, `low` or `not_sure`. Both halves required by V12 |
| `A7` | object `{value, how, basis}`; a `yes` needs `how` and a `basis` of `known` or `inferred` (V2) |
| `A8` | list of `{claim, basis, source}`. `basis` is `known`, `inferred` or `gap`; a `known` claim needs a `source` (V3). **This is the evidence record every generated artifact carries forward** |
| `A9` | object `{as_it_came, as_product_states_it, source_group, what_changed}`; present only when something was inherited |
| `A10`, `A11` | strings; increments only |
| `B00` | object `{outcome, none_committed}`; one or the other (V14) |
| `B0` | object `{categories[], ranking[]}`; every category in `flow-content.json` carries a `value`, the Yes set is ranked when there is more than one, and the top three carry a `why`. A Yes on `other` also needs `name` (V13) |
| `B1` | object with `figures[]` each carrying a `source`, or `gap: {text, owner}`. **A figure with no source fails V4, and so does an unowned gap** |
| `B2`, `B3`, `B4`, `B5`, `B0L` | strings |
| `C1`, `C3`, `C5`, `D3` | strings |
| `C2` | object `{arc, mvp_proves}`; both halves required by V7 |
| `D1`, `D2`, `D4` | lists |
| `F1` | object `{stem, focus_areas[]}`; three to five areas, enforced by V8 |
| `F2` | boolean; increments only — does the parent's statement still cover this. **`false` is a routing result, not a defect**, and re-scopes as a revision |
| `LQd` | object `{categories[], primary}`; Learn mode. More than one Yes needs a `primary` (L7) |

## measures

```json
"measures": [
  { "id": "M1", "primary": true, "measure": "Time from claim submitted to decision",
    "baseline": "2.1 days", "baseline_source": "Q3 ops export, claims_cycle_time.csv",
    "target": "Under 4 hours for 80 percent", "by_when": "End of pilot", "horizon": "near_term" }
]
```

Check R3 needs at least one measure with **both** `baseline` and `baseline_source`. `horizon` is
`near_term` or `vision` — the measure that tells you this increment worked is rarely the one that
tells you the vision is being realised.

## triage, reviews, raises, gaps

Unchanged in shape from v1. `triage` values are `yes`, `not_sure` or `no`; `not_sure` routes as `yes`
and generates a `GAP · triage` automatically.

```json
"reviews": [{
  "reviewer_id": "security",
  "responder": { "name": "Priya Raman" },
  "responded_at": "2026-10-14",
  "raises": [{
    "id": "RS-1", "severity": "blocking", "section_ref": "D3",
    "text": "Auto-settle above threshold has no second control.",
    "disposition": {
      "type": "accepted", "change_ref": "D3 rewritten", "rationale": null,
      "deferred_to_step": null, "reviewer_acknowledged": true, "owner_override": false
    }
  }]
}]
```

`accepted` needs `change_ref`; `rejected` needs `rationale`; `deferred` needs both `rationale` and
`deferred_to_step`. Rejecting a **blocking** raise from a `constrain` reviewer needs
`reviewer_acknowledged` or `owner_override` (check R9).

```json
"gaps": [{ "id": "GAP-reviewer-accept", "kind": "evidence",
           "text": "No evidence reviewers would accept agent summaries.",
           "owner": "Dana Okoye", "next_action": "Three reviewer interviews by 17 Oct" }]
```

## learn_mode

Present only on a Learn-mode vision. **Its presence is what sets the mode**, so an empty or unsigned
block does not quietly pass as a grant — the record is in Learn mode and L1 fails loudly.

```json
"learn_mode": {
  "granted_by": { "name": "Marcus Hale" },
  "granted_at": "2026-10-01",
  "grant_reason": "Two-week spike to find out whether retrieval is good enough to design around.",
  "review_by": "2026-10-17",
  "learning_question": "Can retrieval reach 70 percent exact-source accuracy on the sample set?",
  "kill_condition": "Below 70 percent after two approaches, the method is wrong and we stop.",
  "real_users": false, "production_data": false, "spend_committed": false,
  "signal_acknowledgements": {
    "S4": { "by": "Marcus Hale", "at": "2026-10-18", "note": "Seen. Two more weeks, same scope." }
  }
}
```

`granted_by.name` must match `accountable_owner.name` or L1 fails, naming both. Promotion removes this
block and keeps everything else; promotion is one-way.

## computed, written by the verifier

Carries `mode`, `scope`, `artifact` (Product Vision or Learn-mode vision), `policy_version`,
`policy_maturity`, `rules_version`, `tier`, `roster`, `routed_past`, `promotion_signals`,
`triage_gaps`, `readiness` and `warnings`. `readiness.combination` says which of
`commit:new`, `commit:increment`, `learn:new`, `learn:increment` the checks were asked for.

## Checks

Defined in `data/readiness-rules.json`, which also carries each check's `asked_in` list. The verifier
implements the tests; the data decides which combinations ask them.

| Id | Severity | Checks |
|---|---|---|
| R1 | blocking | The change is stated |
| R2 | blocking | Lineage is linked |
| R3 | blocking | A primary measure has a sourced baseline |
| R4 | blocking | Boundaries are stated |
| R5 | blocking | Human-in-the-loop posture is stated |
| R6 | blocking | Triage is settled |
| R7 | blocking | Every blocking reviewer has responded |
| R8 | blocking | Every blocking raise is dispositioned |
| R9 | blocking | Rejected blocking constraints are acknowledged |
| R10 | blocking | An accountable owner is named |
| R16 | blocking | Ratification is the accountable owner's act |
| R18 | blocking | A revision names what it supersedes |
| V1 | blocking | The customer is named and their world described |
| V2 | blocking | Customer urgency is evidenced behaviourally |
| V3 | blocking | Evidence and gaps are separated |
| V4 | blocking | The prize is sized, or the gap is named |
| V5 | blocking | Strategic fit and competitive position are stated |
| V6 | advisory | Why now names what closes the window |
| V7 | blocking | The arc and what MVP proves are stated |
| V8 | blocking | The statement exists and is well formed |
| V9 | advisory | Who absorbs the change is named |
| V10 | advisory | The pull-it condition is stated |
| S1 | blocking | The parent vision is linked |
| S2 | blocking | The parent statement still covers this |
| S3 | blocking | Why this increment, and why next |
| S4 | advisory | Production signal is stated |
| L1 | blocking | The grant is recorded |
| L2 | blocking | A review-by date is set |
| L3 | blocking | The learning question is stated |
| L4 | blocking | A kill condition is stated |
| L5 | blocking | Non-goals are stated |
| L6 | blocking | Live promotion signals are acknowledged |
| R13 | advisory | Evidence gaps have owners |
| R14 | advisory | Advisory raises are answered |
| R15 | advisory | Change rationale is present in revision mode |

Exit 0 means every **asked** blocking check passed. The meter counts asked checks only; a check the
combination does not ask reports `n/a`, stays visible, and is not owed later.

## What the schema deliberately does not hold

- **A roster anyone chose.** It is computed; storing a chosen one would let the two drift.
- **A readiness number anyone typed.** Only `computed.readiness` exists.
- **A mode field.** Mode is derived from the presence of `learn_mode`, so nothing can be in Learn
  Mode without a recorded grant to point at.
- **An approval flag the skill can set.** `ratified_by` is a person's name or it is null.
