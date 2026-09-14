# Plan: Carry the Exploration Decision into Rapid Validation

**Date:** 2026-09-14
**Scope:** `plugins/aipos-p2` — `val-rapid-validation` (SKILL.md, `references/evidence-intake.md`,
the seven artifact references, `references/record-writeback.md`), a new `evals/`; `plugins/aipos-p1`
— the handoff paragraph in `pdg-quarterly-planning/SKILL.md` and the plugin README; root README.
**Status legend:** `[ ]` not started · `[~]` in progress · `[x]` done
**Status: implemented — aipos-p2 0.2.0 (#13), aipos-p1 0.1.1 (#14).** `claude plugin validate .` and `pytest tests` pass. The model-graded `evals.json` cases were **not** run; no behavioural result is claimed. Qodo's three findings on #13 (ambiguous "no mandate" wording; plans counted as spend; duration horizons with no decision date) were fixed before merge, and #14 gained a `Decided:` line in the decision log for the third.

## Context

Pillar 1 ends at the **Exploration Decision**: for each candidate problem an accountable owner
decides *explore* with a declared **budget** (e.g. five interviews) and **horizon** (e.g. two
weeks), *decline*, or *defer*. The decision log entry carries owner, budget, horizon, evidence
cited, a draft status, and the governed door a human records it through.

Pillar 2 (`val-rapid-validation`) begins there, and the READMEs say so. But the skill has no
intake for a decision. Its `evidence-intake.md` knows three paths — a tracker record, material
the PM shares, nothing — all of which are about *evidence for the problem*. Nothing reads the
budget or horizon, no artifact states what it costs against them, and the viability brief never
reconciles the validation work done against the capacity that was approved. Qodo flagged this on
PR #12; the fix there corrected Pillar 1's handoff text to stop claiming Pillar 2 picks the
constraints up. This plan makes the claim true.

## Findings confirmed against the checkout

1. **No decision intake.** `evidence-intake.md` asks one question ("Do you have evidence to
   work from…") with three answers. An Exploration Decision fits none of them: it is not
   evidence about the problem, it is a mandate about how much to spend finding out.
2. **Budget and horizon are invisible after the handoff.** `grep` across the seven artifact
   references finds only local notions: the feasibility spike's own timebox ("two to five
   days, hard stop"), the demand test's duration column (Days / Weeks), and the interview
   guide's read-aloud "time budget". None is tied to a declared budget or horizon.
3. **The viability brief does not close the loop.** Its "Validation work completed" table
   lists artifacts and results, and "After the decision" offers a write-back to the tracker
   opportunity. It never says whether validation stayed within the mandate, and the Validation
   Decision never reaches the Exploration Decision record, so Pillar 1's next session cannot
   see the outcome of what it funded.
4. **Stale claims remain.** `plugins/aipos-p1/README.md` ("An explored problem enters Rapid
   Validation carrying its budget and horizon") still describes the behaviour PR #12's skill
   text retracted. The root README's Pillar 2 blurb does not mention the mandate at all.
5. **No evals for aipos-p2.** The skill ships with no `evals/` directory, so nothing exercises
   the intake behaviour once it exists.

## Design decisions

**D1 — The mandate is an input, not a fourth evidence path.** Add an **exploration mandate**
block to intake, read *alongside* whichever evidence path applies. Fields: decision ref or the
pasted log entry, owner, budget (in its own units), horizon (a date or a duration from the
decision date), evidence cited, and where the decision is recorded. Ask once, plainly:

> Is this under an Exploration Decision from planning? If so, paste the log entry or name the
> record. If not, we'll work unbounded and say so.

Absent a mandate the header says `Mandate: none declared [A]`. The skill never invents a
budget, exactly as it never invents a number.

**D2 — Budget and horizon constrain the plan; they do not gate the work.** Pillar 2 stays
deliberately ungoverned. The skill never refuses an artifact for being over budget. It *reports*:
each artifact states its cost in the mandate's units, the header carries a running ledger, and
an artifact whose decision rule cannot be reached inside the remaining budget or horizon says
so and names the cheaper alternative. The PM owns the call to exceed; the skill makes the
exceedance visible.

**D3 — The ledger lives in the evidence-base header.** The four-line header in
`evidence-intake.md` gains one line:

```markdown
**Mandate:** <OPP-5 explore · owner J. Diaz · budget 5 interviews + 1 spike (2d) · horizon 2026-10-15 · used 2/5 interviews, 0/1 spike | none declared [A]>
```

One line, so the first thing a reader sees still fits on a screen. Every artifact carries it,
so six weeks later anyone can tell whether the work was inside its mandate.

**D4 — Exhaustion routes to the decision.** When the budget is spent or the horizon has passed,
the skill's default recommendation becomes artifact 7, the viability brief: make the call with
what exists, and *revise* is a legitimate answer. Silently continuing to build artifacts past
the horizon is the failure this plan exists to prevent. The PM can still ask for more; the skill
says once what that costs against the mandate and continues.

**D5 — The viability brief reconciles and closes the loop.** "Validation work completed" gains
a budget column (declared vs used). The decision paragraph states whether the mandate held.
"After the decision" adds the second half of the loop: record the Validation Decision against
the Exploration Decision it answers, through the same governed door Pillar 1 named, so the next
planning session's funnel signals see it. Same rule as every write: prompt every time, write only
on an explicit yes, and where the skill cannot write, hand the PM the exact text and destination.

**D6 — Pillar 2 reads the mandate as text; it does not gain an MCP dependency.** The mandate
arrives as a pasted log entry, a field on the tracker record the PM names (Path A), or the
PM's answer. Reading the Product Definition Graph stays Pillar 1's job. If a connector happens
to expose the decision record, use it the way Path A already uses a tracker; never require it.

**D7 — Pillar 1's handoff names the intake it hands to.** The PR #12 wording ("that skill has
no intake for decisions and enforces no budget") is replaced once D1 lands: hand the log entry
to `val-rapid-validation`'s mandate intake; the receiving skill carries the budget and horizon
in every artifact's header and reconciles them in the viability brief; the owner still holds the
line, because Pillar 2 reports and never gates.

**D8 — Two PRs, one per plugin.** PRs are this repository's change log, and the change has a
plugin boundary through it. PR 1: `aipos-p2` (the substance, including its own README). PR 2: `aipos-p1`
handoff text, the `aipos-p1` README, root README. PR 2 lands after PR 1 so no README describes behaviour that
does not exist yet.

## Work items

### A. Intake and header (`aipos-p2`)

- [x] **A1** `references/evidence-intake.md`: add a "The exploration mandate" section after
  "The three paths" — the one question, the field list, what to do with a decision ref vs a
  pasted entry vs nothing, and the rule that a missing mandate is `[A]` and never invented.
- [x] **A2** Same file, "The evidence-base header": add the `**Mandate:**` line and its two
  forms (declared with running ledger · none declared `[A]`). Update the example.
- [x] **A3** `SKILL.md` Step 2: name the mandate alongside the three evidence paths. Step 1
  routing table: add a row — "We've spent the budget / the horizon has passed" → 7, viability
  brief. Step 4 "Close the loop": item 2 also states the artifact's cost against the mandate
  and the ledger after it.
- [x] **A4** `SKILL.md` "How to behave throughout": one bullet — report against the mandate,
  never gate on it; an artifact whose decision rule cannot be reached inside what remains says
  so and names the cheaper route.

### B. Cost lines in the seven artifact references (`aipos-p2`)

Each output template gains one line under its evidence-base header, in the mandate's own units.
Keep each to a line; the point is visibility, not ceremony.

- [x] **B1** `interview-guide.md`: sessions planned vs interviews budgeted; if planned exceeds
  budgeted, say which questions drop first.
- [x] **B2** `problem-sizing.md`: desk time; no budget units usually apply — say "no mandate
  cost" rather than inventing one.
- [x] **B3** `visual-prototype.md`: build effort and the horizon date it must be tested by.
- [x] **B4** `demand-test.md`: the duration column already exists — add the horizon check: a
  Weeks-class test inside a two-week horizon is the exact case D2 makes visible.
- [x] **B5** `feasibility-spike.md`: the existing timebox is the cost; add "fits inside the
  horizon: yes / no, by <n> days".
- [x] **B6** `eval-stub-brief.md`: eval set construction effort, if any; otherwise "no mandate
  cost".
- [x] **B7** `viability-brief.md`: see C.

### C. Closing the loop (`aipos-p2`)

- [x] **C1** `viability-brief.md` output template: "Validation work completed" gains a
  `Budget used` column and a totals row against the declared budget and horizon. The decision
  paragraph states whether the mandate held and, if not, by how much and why that was the
  right call.
- [x] **C2** `viability-brief.md` "After the decision": add the write-back of the Validation
  Decision *against the Exploration Decision* — decision, confidence, budget used, the
  artifacts as evidence refs — through the door Pillar 1 named. Prompt; write only on yes;
  hand off by exact text where the skill cannot write.
- [x] **C3** `record-writeback.md`: one short section on the decision record as a second
  destination distinct from the opportunity record, and the naming convention for it.

### D. Pillar 1 side and documentation (`aipos-p1`, root)

- [x] **D1** `pdg-quarterly-planning/SKILL.md` handoff paragraph (the PR #12 wording): replace
  with D7's description. Decision log template: add an optional `Record ref:` line for the id
  the door produces once a human has walked through it, so Pillar 2 can cite it. Also a
  `Decided:` date line, so a horizon stated as a duration has a start date to count from.
- [x] **D2** `plugins/aipos-p1/README.md` "The handoff": describe the real behaviour — the
  mandate is carried in every Pillar 2 artifact header and reconciled in the viability brief;
  the owner holds the line.
- [x] **D3** `plugins/aipos-p2/README.md`: mention the mandate intake and the loop closure
  under "What it does"; add the exhaustion phrase to "When to use it".
- [x] **D4** Root README Pillar 2 blurb: one clause on picking up the Exploration Decision's
  budget and horizon and reporting against them.

### E. Evaluations, versions, validation

- [x] **E1** New `plugins/aipos-p2/skills/val-rapid-validation/evals/evals.json` with fixture
  files under `evals/files/`, model-graded and optional per repo convention:
  1. *Mandate declared* — a pasted decision entry plus Path B notes; the interview guide's
     header carries the ledger, sessions planned do not exceed the budget, nothing is invented.
  2. *Budget exhausted* — five of five interviews used, PM asks for a demand test; the skill
     builds it, states the exceedance once, and recommends the viability brief.
  3. *No mandate* — Path C, no decision; header says `none declared [A]`; no budget appears
     anywhere in the artifact.
  4. *Viability brief reconciles* — completed work plus a mandate; the brief's table totals
     against the budget, the decision paragraph says whether the mandate held, and the
     after-decision prompt offers the write-back against the Exploration Decision by exact
     text.
- [x] **E2** `claude plugin validate .` passes; `pytest tests` unaffected (no scripts change).
- [x] **E3** Versions: `aipos-p2` 0.1.0 → 0.2.0 (new intake); `aipos-p1` patch bump for the
  handoff text; `marketplace.json` descriptions only if they name the behaviour.

## Non-goals

- No gating, no refusal, no enforcement. Pillar 2 reports against the mandate; the owner and
  Pillar 1's governed doors enforce it.
- No MCP read of the Product Definition Graph from Pillar 2, and no new required connector.
- No Gherkin, NFRs, or evaluation schemas from Pillar 2 — the Build-to-Learn boundary is
  untouched.
- No change to the seven-artifact menu or its numbering.

## Key file map

| Concern | File |
|---|---|
| Intake question, mandate block, header | `plugins/aipos-p2/skills/val-rapid-validation/references/evidence-intake.md` |
| Routing, close-the-loop step, behaviour rules | `plugins/aipos-p2/skills/val-rapid-validation/SKILL.md` |
| Reconciliation and loop closure | `plugins/aipos-p2/skills/val-rapid-validation/references/viability-brief.md` |
| Second write-back destination | `plugins/aipos-p2/skills/val-rapid-validation/references/record-writeback.md` |
| Pillar 1 handoff wording, `Record ref:` line | `plugins/aipos-p1/skills/pdg-quarterly-planning/SKILL.md` (lines ~28–33, ~130–140) |
| Stale README claim | `plugins/aipos-p1/README.md` "The handoff" |
