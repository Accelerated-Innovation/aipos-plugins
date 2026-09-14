# aipos-p2

Rapid Validation (AIPOS Pillar 2): test the riskiest assumptions *before* committing
production engineering capacity. One skill, seven validation artifacts, one primary output —
the **Validation Decision**: go, no-go, or revise.

## What it does

The `val-rapid-validation` skill helps a Product Manager build the evidence that answers
Pillar 2's core question — *can this solution create useful, safe, measurable value before we
invest in full production buildout?* — at the cheapest point in the lifecycle, where testing
an assumption costs days instead of sprints.

The artifact menu is organised by the three questions the Validation Decision must answer:

| Question | Artifacts |
|---|---|
| Is the problem real and worth solving? | Interview guide · Problem sizing |
| Will the solution actually solve it? | Visual prototype brief · Demand test · GenAI eval stub & brief |
| Is it feasible and economic? | Feasibility spike |
| Make the call | Viability brief (carries the Validation Decision) |

Every artifact carries a hypothesis, an experiment, and a decision rule — what the PM will do
differently depending on the result. Every claim is provenance-marked: `[E]` evidence-backed,
`[I]` inferred, `[A]` assumption. The skill never invents evidence, personas, metrics, or
quotes; a missing number becomes a marked assumption, never a plausible-looking figure.

When validation runs under an **Exploration Decision** from Pillar 1 (`aipos-p1`), the skill
reads it as the *exploration mandate* — owner, budget, horizon — and carries it in every
artifact's header as a running ledger. Each artifact states its cost in the mandate's own
units; when the budget is spent or the horizon has passed, the default next step is the
viability brief. The skill reports against the mandate and never gates on it: the owner holds
the line. The viability brief reconciles the work done against the budget and, on an explicit
yes, closes the loop by recording the Validation Decision against the Exploration Decision so
the next planning session sees what it funded. Having no mandate is legitimate — most
hunches have none — and the skill says `none declared` rather than inventing one.

What it does **not** do: it is Build-to-**Learn**, deliberately ungoverned relative to
delivery. It emits no Gherkin, no NFRs, no evaluation schemas, no build-ready specifications —
those are born *at* the Validation Decision, in Build-to-Earn territory (see the companion
`govkit` plugin, which picks up exactly there). It also never writes to a system of record
without a previewed, explicit yes.

### When to use it

- "Is this worth building?" / "we need to validate before we commit"
- "How do we know people actually want this?"
- "Size this opportunity" / "leadership wants to know if it's big enough"
- "Can we actually build this?" / "does the data even exist?"
- "It's a GenAI feature and 'good' is fuzzy — what would prove it works?"
- "We've done the discovery work — should we kill this or build it?"
- "Prep me for user interviews"
- "We've spent the exploration budget" / "the horizon is up — what do we know?"

**When not to use it:** once the Validation Decision is *go* and you need acceptance
criteria, NFRs, or a readiness gate — that is `govkit`, not this plugin.

## Installation

```bash
claude plugin marketplace add Accelerated-Innovation/govkit-plugins   # once per machine
claude plugin install aipos-p2@aipos
```

### Prerequisites

None required — the skill is plain markdown with no scripts or packages. Optional: an Aha!
MCP connector, used only for evidence intake from a record and for the prompted write-back of
finished artifacts. Everything also works from pasted material or from nothing but a hunch.

## Usage

Describe your situation or name an artifact; the skill opens with the artifact menu and
routes you. It asks one primary question at a time, reads whatever evidence you give it
before asking for facts, and defaults forward on "proceed" / "looks good". Each finished
artifact is delivered as a file, states which of the three questions it moves and what
remains unevidenced, prompts (never assumes) a save to the record, and names the next
artifact — validation is a sequence, not a menu visit.

## Examples

### Example: Route a hunch to the right artifact

- **Prompt:** `We have a hunch that our support agents waste a lot of time searching old tickets for similar cases, but we have no data. How should we validate this before committing engineering?`
- **Expected:** The validation artifact menu, with a routed recommendation to start at the
  "is the problem real?" question (interview guide, then problem sizing), a stated
  hypothesis for the first artifact, and one primary question back to the PM — no invented
  metrics, personas, or quotes anywhere.
- **Safe to auto-run:** yes
- **Inputs:** none.

### Example: Size a problem from pasted evidence

- **Prompt:** `Build a problem sizing from this: we have 40 support agents; a shadowing session with 6 of them measured 35-50 minutes per agent per day spent searching old tickets; loaded cost is about $38/hour. Assume nothing else.`
- **Expected:** A problem-sizing artifact written to a file, with the measured inputs marked
  `[E]`, every extrapolation marked `[I]` or `[A]`, a sensitivity pass on the assumptions, a
  decision rule stating what result would justify proceeding — followed by a prompt (not an
  action) to save it to the record and a pointer to the next artifact.
- **Safe to auto-run:** no
- **Inputs:** none beyond the inline figures; writes the artifact file to the working
  directory.

### Example: Make the call with a viability brief

- **Prompt:** `We've finished the interviews, sizing, demand test, and feasibility spike for the ticket-search assistant. Build the viability brief and help me make the go / no-go / revise call.`
- **Expected:** A viability brief that synthesises the existing evidence with provenance
  marks, answers the three validation questions, carries an explicit go / no-go / revise
  Validation Decision with its rationale, and *names* (without writing) the handoff inputs
  Build-to-Earn will need — problem statement, MVP scope, evaluation criteria, guardrail
  requirements. Ends with the prompted record write-back offer.
- **Safe to auto-run:** no
- **Inputs:** the prior artifacts (pasted, attached, or on an Aha! record); writes the brief
  to a file.

## Limits and gotchas

- **It will refuse to write specs.** Asking for Gherkin or NFRs here gets a polite redirect:
  specs are born at the Validation Decision, not before it. Use `govkit` after a *go*.
- **Missing evidence stays missing.** The skill would rather ship an artifact full of `[A]`
  marks with a sensitivity analysis than one plausible fabricated baseline.
- **Write-back requires a fresh, explicit yes every time** — an earlier "sounds good" is
  never standing approval. It also cannot create Aha! attachments itself; it hands that step
  to the PM by filename.
- The artifacts are working documents written as files, not just chat output — expect files
  in your working directory.
- A demand test without a sized problem produces a number nobody can interpret; the skill
  will build what you ask for, but it says once what's missing and why it weakens the result.
- **It reports against an exploration mandate; it never enforces one.** Over budget or past
  the horizon, it says so once, names the cheaper route, and builds what you asked for.
  Enforcement lives with the decision owner and Pillar 1's governed doors.

## Components

| Kind | Name | What it does |
|---|---|---|
| Skill | `val-rapid-validation` | The menu, routing, behaviour rules, and the four-step loop (pick → intake → build → close) |
| Reference | `evidence-intake.md` | Three intake paths (Aha! record, pasted material, nothing), the exploration mandate read alongside them, the evidence-base header with its mandate ledger, and provenance marking |
| Reference | `record-writeback.md` | The prompted, explicit-yes save-to-record protocol, including the decision record as the viability brief's second destination |
| Evals | `evals/evals.json` | Four model-graded cases: mandate declared, budget exhausted, no mandate, viability brief reconciles and closes the loop |
| References | `interview-guide.md` … `viability-brief.md` | One per artifact: interview steps, output template, quality bar |

## Version history

| Version | Change |
|---|---|
| 0.1.0 | Initial release: seven validation artifacts and the Validation Decision workflow. |
| 0.2.0 | Exploration mandate intake: reads the Pillar 1 Exploration Decision (owner, budget, horizon), carries it as a ledger in every artifact header, states each artifact's cost, routes to the viability brief on exhaustion, reconciles in the brief, and offers the write-back that closes the loop to the decision record. Reports, never gates. First eval cases. |
