# aipos-rapid-validation

A Claude skill for **Rapid Validation** — the AIPOS pillar that retires risk before an
organization commits production engineering capacity.

Its primary output is not a document set. It is the **Validation Decision**: go, no-go, or
revise. Every artifact here is evidence feeding that call.

## The three questions

| | Question | Artifacts |
|---|---|---|
| 1 | Is the problem real and worth solving? | Interview guide · Problem sizing |
| 2 | Will the solution actually solve it? | Visual prototype · Demand test · Eval stub & brief |
| 3 | Is it feasible and economic? | Feasibility spike |
| — | Make the call | Viability brief |

## Layout

```
aipos-rapid-validation/
├── SKILL.md                        entry point — menu, routing, behaviour rules
└── references/
    ├── evidence-intake.md          the three intake paths and provenance marking
    ├── record-writeback.md         saving artifacts back to the tracker
    ├── interview-guide.md          1
    ├── problem-sizing.md           2
    ├── visual-prototype.md         3
    ├── demand-test.md              4
    ├── feasibility-spike.md        5
    ├── eval-stub-brief.md          6
    └── viability-brief.md          7
```

`SKILL.md` is read first; each reference carries its own interview steps, output template
and quality bar, and is read only when that artifact is being built.

## Conventions worth knowing before you edit

**Provenance marking.** Every claim in every artifact is marked `[E]` evidence-backed,
`[I]` inferred, or `[A]` assumption. Without it, a document built from a hunch is visually
indistinguishable from one built from thirteen customer calls.

**Never invent evidence.** No plausible-looking figures, personas, metrics or quotes. A
missing number is written as an assumption and handled by the sensitivity pass.

**Build-to-Learn, not Build-to-Earn.** This skill emits no Gherkin, no NFRs, no evaluation
schemas, and no build-ready specifications. Those are born *at* the Validation Decision,
not before it.

**Write-back is prompted, never automatic.** Nothing is written to a system of record
without an explicit yes. See `references/record-writeback.md`.

## Installing

Copy the `aipos-rapid-validation/` directory into your Claude skills directory
(`/mnt/skills/user/` in the sandboxed environment, or the equivalent path for your setup).
No dependencies, no build step — the skill is plain markdown.
