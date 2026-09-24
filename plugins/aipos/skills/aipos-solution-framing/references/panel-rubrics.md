# Panel rubrics — the quality bar for each part of the canvas

> A canvas filled with confident vagueness is worse than a blank one: it gets shared, and then
> it gets quoted. These rubrics are what the facilitation pushes on, panel by panel. They are
> meant to be shown — if the PM asks why a line was pushed back on, show the test it failed.

The mechanics (field types, marks, GAP wiring, what the verifier computes) live in
`canvas-schema.md`. This file is about **quality**: what a good answer looks like and what to
say when it isn't one.

## Contents

- [The one rule that changes the coaching](#the-one-rule-that-changes-the-coaching)
- [Panel 1 — Problem & Context](#panel-1--problem--context)
- [Panel 2 — Discovery Evidence](#panel-2--discovery-evidence)
- [Panel 3 — Hypothesis & Expected Outcomes](#panel-3--hypothesis--expected-outcomes)
- [Panel 4 — Solution Options](#panel-4--solution-options)
- [Panel 5 — Assumptions & Risks](#panel-5--assumptions--risks)
- [Panel 6 — Validation & Decision](#panel-6--validation--decision)
- [Footer](#footer)
- [Across the panels — coherence](#across-the-panels--coherence)
- [Before approval](#before-approval)

## The one rule that changes the coaching

**The graph is the source of truth for facts; the PM owns decisions.**

This skill borrows heavily from `aipos-epic-create`, with one deliberate reversal. Epic-create
pushes the PM for a number and accepts an estimate ("even an order of magnitude helps"). Here,
**never ask the PM to supply a fact.** A baseline, a volume, a date, an example, a count — if
the graph does not hold it, it is a `GAP · evidence`, and the coaching question changes from
*"what's the number?"* to:

> We don't have that in the graph yet. What evidence would settle it — and where would it come from?

The answer becomes the to-do: the measure, the source type, the window, the ReOps intake route.
A precise to-do gets done; "go gather evidence" does not. Push once for precision:

| PM says | Ask |
|---|---|
| "We'd need to look at tickets" | Which measure, over what window? "4 weeks of first-time routing" is a to-do; "look at tickets" is a wish |
| "Ops has that number" | Which record? If it's a study or a report, the to-do is getting *that* into the graph through ReOps |
| "Everyone knows it's about two minutes" | I'll keep that as an assumption beside the GAP — it won't be used in any calculation until the graph has it |

If the PM volunteers a figure anyway, keep it — as `assumed` with mark `[A]`, displayed beside the
GAP, never computed with. Their knowledge is not thrown away, and the graph stays authoritative.

One exception: if the value sits in a record the graph links but can't show as text, the PM may read
it from that record's `record_url`. It is recorded `[T]` (transcribed) — it computes, but it does not
unlock Proceed (`opportunity-source.md`, *Transcribed values*). Without a graph at all, the PM's
account is the only source and is recorded `[I]` — see *No graph* in the same file.

Decisions — wording, targets, options, owners, the plan, the recommendation — are the PM's, and
this is where the coaching pushes hardest. Proposing a decision as a draft is fine and often
helpful; mark it `provisional` until the PM confirms it. Nothing provisional can be approved.

**Evidence text is access-logged.** `get_evidence_text` is a person-adjacent disclosure on the
engine. Fetch an excerpt only when a panel needs exact words — a current-state example (panel 1)
or a quote (panel 2) — and never paste more than the fragment the canvas uses.

---

## Panel 1 — Problem & Context

**From the graph:** the problem title, personas with confidence, the evidence behind pain points
and impact, and 2–3 records for the current-state snapshot. **From the PM:** the problem statement
wording and which persona is primary.

Apply `../../../references/problem-framing.md` for the solution-in-problem test,
root-cause probing, persona rules, benefits and the final-statement check — **but not its
"Quantifying impact" push scripts** ("roughly how long, and how often?"). Those ask the PM for a
fact. Here, impact comes from the graph; where it doesn't, ask what evidence would show the impact
and make it a GAP with a to-do. Canvas-specific additions:

**Quality bar**

- [ ] Pain points (1–3) are things the graph shows people struggling with — from the problem's
      title (`[I]`, the engine's extraction) or from excerpts read for the snapshot (`[E]`). Not
      features, not wishes, not paraphrases of records nobody read.
- [ ] The snapshot shows 2–3 **real** records the graph returned text for — anonymised, labelled
      in a few words each. Invented "example tickets" never appear, however illustrative.
- [ ] Impact carries a number only where the graph holds one. "Tickets bounce between teams
      before anyone owns them" `[E]` beats "high handle time" with no source.
- [ ] One primary persona, chosen from the graph's persona list; others named. Locked once
      confirmed.
- [ ] The statement reads: *the problem of [X] affects [Y], resulting in [Z], and solving it will
      lead to [benefits]* — and [Z] points at impact facts or says plainly what isn't in the graph.

**Push scripts**

> The graph lists [Support Agent 0.91, Team Lead 0.74, Enterprise Admin 0.52]. Which of them
> suffers most — the one the canvas should be built around?

> That reads like the solution — "no auto-categorisation". If we built it, who stops struggling,
> and with what?

**Common defects**

| Defect | Example | Fix |
|---|---|---|
| Solution as pain point | "No AI triage" | Recover the difficulty; move the solution to panel 4 |
| Illustrative data | Made-up ticket examples | Use graph records with text, or show none |
| Adjective impact | "Lower CSAT" with no source | An `[E]` consequence, or an evidence GAP with a to-do |
| Everyone suffers | "Users" | Name the two or three roles the graph shows most |

## Panel 2 — Discovery Evidence

**All from the graph.** The PM chooses which evidence to feature and approves any quote.

**Quality bar**

- [ ] 1–4 tiles, each a source type the graph actually holds (interviews, tickets, calls, studies).
- [ ] Each tile's **finding says what the graph establishes** — linkage, dates, source type, and
      the words of any excerpt. An unreadable record establishes that it exists and is linked, not
      what it says: "Three interview notes from July 2026 are linked to this problem", not
      "Agents said manual categorisation is the primary pain".
- [ ] Counts, date ranges and aging are computed by the verifier. Never type "6 agents
      interviewed" — the graph may hold three notes, and the tile will say three.
- [ ] Breadth is judged by originating sources, not ref count. Five refs from one call is one
      source; say so.
- [ ] A quote is a verbatim fragment of a redacted excerpt, with its provenance reference, and the
      PM has approved it for a shareable canvas. Attribute it to its source and date ("customer
      call, June 2026") — excerpts say "Speaker 2", and the graph does not say who that was.
- [ ] Aging evidence (older than 18 months against the read date) is named. A null date is
      **unknown**, not old — say "date unknown", never treat it as stale.

**Push scripts**

> The graph links three interview notes, but their text isn't readable through it. I'll say they
> exist and when; if you want what they *said* on the canvas, that's a to-do to get the
> synthesis into the graph.

> All five of these trace back to one call on 27 August. That's one source, however many rows it
> produced — worth knowing before anyone reads the count as breadth.

> This quote goes on a page that will be shared. Happy for "it takes too long to get to the right
> team" to appear, attributed to a customer call from June 2026?

**Common defects:** transcribed counts; findings that paraphrase unreadable records; a quote
stitched from two excerpts; a strong-looking tile resting on 2022 evidence with no aging note.

## Panel 3 — Hypothesis & Expected Outcomes

**From the graph:** baselines. **From the PM:** the hypothesis, the targets, the observation
method, which metric is primary.

Apply `../../../references/metrics-and-evaluation.md` for the three-part metric and
choosing metrics — **except its "pushing for numbers" section**, which this skill replaces with
the evidence-GAP question above.

**The hypothesis form**

> If we **[capability, at the moment it matters]**, then we can **[outcome tied to the primary
> metric]** without **[the cost we refuse to pay]**.

- [ ] *If* names a capability, not a product ("suggest the right category at intake", not "launch
      TriageAI").
- [ ] *Then* names outcomes that appear as metrics.
- [ ] *Without* names a real counter-harm — agent effort, accuracy, trust — and that harm has a
      counter-metric or a panel-5 risk. "Without any downside" is not a clause.
- [ ] The hypothesis is falsifiable by the panel-6 plan. If no result of the pilot could prove it
      wrong, it is a slogan.

**Metrics**

- [ ] At most three outcomes, exactly one primary. The primary is the one the decision turns on.
- [ ] Each metric: baseline (graph fact or GAP), target (absolute or % — a PM decision), and an
      observation method someone owns.
- [ ] The target is a decision the PM makes knowingly: "−30% from a baseline we don't have yet" is
      legitimate and stays honest because the verifier renders it as a formula until the baseline
      arrives.
- [ ] On a percentage metric, "+20%" is ambiguous — relative (60% → 72%) or percentage points
      (60% → 80%)? Ask once and record it as `target_change_kind`.

**Push scripts**

> What's the one number the decision to proceed turns on? That's the primary.

> "Improve routing" — improve from what? The graph has no routing baseline. What measure would
> establish it, and over what window?

> "Without increasing agent effort" — how would we notice if we did? That's a counter-metric or a
> risk with a mitigation.

## Panel 4 — Solution Options

**All decisions.** This is where solutions belong — and the panel exists so the first idea is
compared, not assumed.

**Quality bar**

- [ ] **Two or three genuinely different options.** Different in mechanism, in who acts, or in how
      much is automated — not in degree. "Suggest the top 1" vs "suggest the top 3" is one option
      with a parameter.
- [ ] The test: *would choosing between these change what we build, who does the work, or what we
      risk?* If not, they are one option.
- [ ] Where credible, one option is non-AI or "do less" (rules, a process or form change, training).
      It anchors what the AI option is worth; if the rules option would get 80% of the value,
      that is the most important thing the canvas can show.
- [ ] Each option: a one-line approach; a preview of **what the user sees** (1–3 concrete lines);
      at least one pro and one honest con — the con that would make you not pick it; and which
      outcome metrics it moves.
- [ ] Every serious con has a matching risk in panel 5.
- [ ] A recommended option is optional. If chosen, the reason ties to the riskiest assumption, and
      the panel-6 pilot tests *that* option.

**Generating options.** If the PM arrived with one solution, it becomes option A, recorded as
theirs. Then ask for alternatives before offering any:

> If option A turned out not to be feasible, what would you do instead?

> What's the version where a person stays fully in control? And the version with no AI at all?

Claude may propose an option to fill a gap in the spread — say so, mark it `provisional`, and let
the PM confirm, change or drop it. Never present a proposed option as one the team considered.

**Common defects:** three flavours of the same idea; cons that are really pros ("so powerful
people may rely on it"); an option that moves no metric; the recommended option decided before
the options were written.

## Panel 5 — Assumptions & Risks

**Mostly decisions, seeded by the graph's gaps.**

**Quality bar**

- [ ] **Every evidence GAP appears here as an assumption**, stated as what we are assuming is true
      ("the current misroute rate is material") — `from_gap` points at it. This is where a hole in
      the graph becomes a testable bet.
- [ ] A data assumption is always present — that the data the options need exists, is
      representative, and can be used — with its source named. (This is where the old Blueprint's
      "data/context needs" panel lives now.)
- [ ] Assumptions are things that could be false and would change the decision. "The team is
      committed" is not one.
- [ ] Every assumption is retired by a panel-6 plan item.
- [ ] Risks are paired with mitigations. A risk with no credible mitigation is recorded as
      **unmitigated**, plainly — not given a mitigation that amounts to "monitor it".
- [ ] Walk the categories if the PM stalls: data, model/accuracy, adoption and trust,
      compliance/privacy, cost, operational load. Adoption and compliance are the two most
      often forgotten.

**Push scripts**

> What would have to be true for option A to work that we haven't checked?

> "Monitor accuracy" — what happens when the monitor fires? That's the mitigation.

## Panel 6 — Validation & Decision

**All decisions**, except that the verifier decides whether Proceed is available.

**Quality bar**

- [ ] Each plan item is an action with an owner and a date, and names the assumptions it retires.
- [ ] The evidence-gathering items (from the to-dos) come first — they are cheap and they unlock
      the numbers.
- [ ] The pilot, if there is one, tests the recommended option against the primary metric, with a
      comparison (control teams, before/after) and a duration.
- [ ] The primary metric shows baseline → target — or its formula while the baseline is a GAP.
- [ ] **The recommendation is a recommendation.** Proceed / Pivot / Park with a named decision
      owner and a one-line rationale. The canvas never shows a decision as made; it shows what is
      recommended to whom.
- [ ] **Proceed is unavailable unless the primary metric's baseline is graph-backed.** A GAP, a
      figure the PM remembers, or an inference resting on a note all block it. Say why on the
      canvas. Pivot (reassess the approach) and Park (defer) remain available, and "not yet —
      gather the baseline first" is a legitimate outcome, not a failure.
- [ ] GenAI mode: evaluation criteria with thresholds, and say out loud that work under this
      Initiative inherits them (see `../../../references/metrics-and-evaluation.md`).

**Mapping:** Proceed → GO, Pivot → REVISE, Park → NO-GO (defer), so `aipos-rapid-validation`'s
viability brief can consume the recommendation without translation.

**Push scripts**

> Who actually makes this call? The canvas names them; it doesn't make it for them.

> Which result from the pilot would make you choose Pivot instead of Proceed? Write that down now,
> before the result is in.

## Footer

- [ ] **Who benefits** — the personas from panel 1, not a new list.
- [ ] **Success looks like** — one line that mirrors the primary and secondary outcomes.
- [ ] **Impact at scale** — computed: primary-metric saving × volume × unit conversion. With a GAP
      input it shows as a formula (`0.6 × GAP ÷ 60`), never a placeholder number. A hand-typed
      impact figure is the canvas's most-quoted number and its most common error.

## Across the panels — coherence

Check these before approval. Each break is one line to the PM, not a lecture.

| Check | Break looks like |
|---|---|
| Benefits (panel 1) mirror the metrics (panel 3) | A benefit no metric measures, or a metric no benefit motivates |
| Every option moves at least one outcome | An option that moves nothing is a distraction |
| The recommended option moves the primary metric | Recommending the option that doesn't touch the number the decision turns on |
| Every evidence GAP → assumption → plan item → to-do | A GAP that nothing will ever close |
| Every serious con (panel 4) has a risk (panel 5) | The reason not to pick an option, unrecorded |
| The *without* clause has a counter-metric or risk | A promise nothing checks |
| Who benefits = panel-1 personas | A new beneficiary appearing only in the footer |

## Before approval

The canvas is ready to approve when:

1. The verifier reports no errors (`verify_canvas.py --write`).
2. Every panel meets its quality bar, or the PM has accepted the specific gaps (coach mode).
3. The open questions list is not empty — or, if it is, you have said that an empty list usually
   means the canvas wasn't examined hard enough.
4. Personas are locked and every quote is approved.

Then summarise in three lines: what the canvas recommends and to whom, the one GAP that most
blocks the decision, and the first to-do.
