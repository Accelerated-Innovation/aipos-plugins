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

**Experiments and commitment preparation.** This skill owns evidence and experiments.
It delegates canonical Gherkin, NFRs, and production evaluation schemas to
`aipos-feature-create`, with review by `aipos-feature-refine`. Those specifications
can develop during Pillar 2 and become part of the exact scope considered for
approval. Preparing the package does not grant approval.

**Write-back is prompted, never automatic.** Nothing is written to a system of record
without an explicit yes. See `references/record-writeback.md`.

## Installing

Install the single `aipos@aipos` plugin; see the [installation guide](../../../../README.md#install).
The skill itself is markdown with no runtime package dependencies.
