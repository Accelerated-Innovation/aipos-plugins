# Evidence intake

Every artifact in this skill starts here. The job is to find out what is actually known
before writing anything that implies knowledge.

## The three paths

If the request has not already answered it, ask once:

> Do you have evidence to work from — an Aha! record or similar, notes and transcripts you
> can share, or are we starting from your read of the situation?

### Path A — A record in a tracker

The PM names an Aha! opportunity, a Jira issue, a Linear ticket, a Productboard item.

Read it before asking anything. If there is a connector available, use it; if not, ask the
PM to paste the record. Then summarise back what you found and ask them to correct it. Do
not ask for facts already on the record — that is the fastest way to signal you didn't read
it.

**Aha! Discovery evidence-triage records** have a specific shape worth knowing. They carry a
promoted-from-triage block with a composite score and five components:

| Component | Low value means |
|---|---|
| `evidence_strength` | The problem itself still needs confirming |
| `revenue_impact` | No dollar value has been attached yet |
| `persona_breadth` | Pain is concentrated in one role — or breadth is untested |
| `recency` | The evidence is aging |
| `validation_signal` | **Nothing has been tested with a user yet** |

Read the components as a risk map and say so out loud — it tells the PM where the artifact
should focus. A near-zero `validation_signal` is the signature of an opportunity that has
never met a real user; almost anything in this skill will move it. A low `evidence_strength`
means start at artifact 1 or 2, not at a prototype.

Also read the persona list and its breadth. If ten personas span two genuinely different
populations, say so — narrowing to one without naming the choice throws away the strongest
signal on the record.

**Evidence refs are often read-only.** Triage engines commonly link out to source calls or
tickets you cannot open. Say so rather than implying you read them: *"13 refs across 13
sources, read-only from the engine — I have the problem statement and the score shape, not
the underlying quotes."* Then mark accordingly.

### Path B — Material the PM shares

Interview notes, call transcripts, support tickets, survey exports, a sales deck, an
analytics screenshot.

Read all of it before writing. Pull out: recurring phrases in the user's own words,
concrete numbers with their source, named roles, and anything that contradicts the PM's
framing. That last one earns its keep — a contradiction the PM hasn't noticed is the most
valuable thing you can hand back.

Quote sparingly and exactly. A real quote in a user's own words is worth more in an
interview guide or viability brief than any paraphrase, and paraphrase is where invention
creeps in.

### Path C — Nothing

This is legitimate and common. Do not treat it as a failure or make the PM feel behind.

Interview them instead: what they've observed, who they think has the problem, what they
believe is true but haven't checked. Capture it as **assumption**, which is exactly what it
is — and assumptions are the raw material of validation, not a defect.

Then say once, without lecturing:

> Worth knowing: with no evidence behind it, the strongest thing this artifact can do is
> make your assumptions explicit and testable. If you want something that carries weight
> with other people, artifacts 1 and 2 are how you get there.

If the PM asked for a **prototype brief or a viability brief** on Path C, be more direct.
A prototype brief with invented personas produces a test that validates nothing, and a
viability brief with no evidence is an opinion in a document's clothing. Offer the
interview guide or problem sizing first. If they still want to proceed, proceed — but the
evidence-base header has to say plainly that this rests on the PM's judgment alone.

## The exploration mandate

Separately from the evidence, ask once whether this validation has a mandate, unless already stated:

> Is this under an Exploration Decision from planning? If so, paste the log entry or name
> the record. If not, we'll work unbounded and say so.

An Exploration Decision is Pillar 1's output (`aipos-quarterly-planning`): an accountable
owner decided *explore* for this problem with a declared **budget** (in its own units —
"five interviews", "one two-day spike") and a **horizon** (a date, or a duration from the
decision date). It is not evidence about the problem. It is the capacity the organisation
agreed to spend finding out, and it travels with every artifact so that six weeks later
anyone can tell whether the work stayed inside it.

Read it from whichever of these exists, in this order:

1. **A decision ref** — the id the governed door produced when a human recorded the
   decision. If a connector can read that record, read it the way Path A reads a tracker;
   never require one.
2. **The pasted log entry** — the `Problem / Decision / Owner / Budget / Horizon /
   Evidence cited / Status / Record via` block from the planning session. A `Status:
   draft — not yet recorded` entry is still a mandate; say it is unrecorded.
3. **The PM's answer** — owner, budget and horizon in their words, marked `[A]` if nobody
   recorded them anywhere.

Take from it: **owner**, **budget** with its units, the **decision date** (the log's
`Decided` line, or the session date the PM names), **horizon** as a date, the **evidence
cited** (so Path A or B can start from the same material Pillar 1 graded), and **where
the decision is recorded**. Planning often states the horizon as a duration — "two
weeks". A duration is only a deadline once it is added to the decision date, so derive
the date and carry that (`horizon 2026-10-15`). If the decision date is not known,
carry the duration verbatim, mark the horizon `[A]`, and say on every Mandate cost line
that horizon fit cannot be judged until the date is supplied — never pick a plausible
start date to make the arithmetic work. If any other part is missing, mark it `[A]`.
Never invent a budget or a horizon — a mandate is a number someone agreed to, and a
plausible-looking one that nobody agreed to is exactly the fabrication the provenance
marks exist to prevent.

**Having no mandate is legitimate.** Most validation that starts from a hunch has none.
When the PM says there is none, write `none declared [A]` in the header and carry on; do
not lecture, and do not manufacture a budget to fill the line. When there *is* one, in any
of the three forms above, carry it — a supplied mandate is never replaced with
`none declared`.

**The mandate constrains the plan, never the work.** Pillar 2 is deliberately ungoverned.
The skill never refuses an artifact for exceeding the budget or the horizon. It *reports*:
every artifact states its cost against the mandate, the header carries the running ledger,
and an artifact whose decision rule cannot be reached inside what remains says so and names
the cheaper route. The PM owns the call to exceed. The skill's job is to make sure the
exceedance is visible when they make it, not to stop them.

**When the budget is spent or the horizon has passed**, the default recommendation is
artifact 7, the viability brief: make the call with what exists. *Revise* is a legitimate
answer there, and a brief that says "the mandate is exhausted, here is what we know and
what would settle it" is a better outcome than quietly building an eighth artifact past the
date someone agreed to. If the PM still wants another artifact, build it, and say once what
it costs against the mandate.

## Provenance marking

Every artifact marks its claims. This is the single most useful convention in the skill:
without it, a document built from a hunch is visually indistinguishable from one built from
thirteen customer calls, and six weeks later nobody can tell which they're holding.

| Marker | Meaning |
|---|---|
| `[E]` | **Evidence-backed** — an observation or report supported by a named source you actually read, within that source's limits |
| `[I]` | **Inferred** — an interpretation or extrapolation, yours or an attributed source's; the underlying observation does not establish it |
| `[A]` | **Assumption** — an untested premise, estimate, or proposed choice, whoever supplied it |

Mark at the claim level, not the section level. Inside one paragraph a sized market may be
`[E]` while the adoption rate applied to it is `[A]` — and that distinction is the whole
value of the estimate.

Attribute the source **and** classify the claim. A lead's notes can establish observed
task durations `[E]`; the lead's explanation of the cause is
still `[I]`, and their unmeasured weekly cost estimate is `[A]`. A citation establishes
that someone made a claim, not that the claim is true. Keep reported estimates labelled
as estimates; never turn them into measured savings. Keep unknown quantities unknown in
the artifact body, calculations and closing recommendation, not just the header.

Put each quantitative claim's supplied source identifier in the same sentence or
table row as the value and its provenance marker. For example, `[E] (source: <id>,
as reported in the supplied summary)` distinguishes a supported summary from an
independent read of the underlying record. A list of evidence IDs elsewhere is not
that mapping. Preserve it when repeating the value; never invent an ID where none
was supplied — use the source's actual name or describe the provenance limit.

Do not mark decorative or structural text. Mark claims someone could act on or be wrong
about.

## The evidence-base header

Every artifact opens with this block. It takes five lines and it is the first thing a
reader should see.

```markdown
## Evidence base
**Source:** <record and access limits | supplied interview transcripts | PM interview only>
**What's backed:** <the problem statement, the persona set>
**What isn't:** <the urgency claim, every number in the sizing>
**Mandate:** <decision ref · owner · agreed budget and units · decision date · horizon · actual use · proposed consumption | none declared [A]>
Claims below are marked [E] evidence-backed, [I] inferred, [A] assumption.
```

The `Mandate` line is the running ledger. Declared form: the decision ref, the owner, the
budget in its units, the decision date, the horizon date, what has been **used** so far,
and what this artifact **plans** to consume. Undeclared form: `none declared [A]`, nothing
else. One line either way, so the header still fits on a screen.

**Used means consumed by work that has actually run** — sessions held, test days elapsed,
spike days spent. Most artifacts here are plans: an interview guide, a demand test, a
prototype brief, a spike plan describe work that has not happened yet. **A plan reserves;
it does not spend.** An interview guide with five sessions planned and none held reads
`used 0/5 · plans 5`, and the ledger moves to `used 5/5` only when the sessions are run.
Exhaustion — and the routing to the viability brief that follows it — is judged on `used`.
A plan that would carry `used` past the budget is over-plan, not over-spent: it says so on
its Mandate cost line, and the PM decides. Each artifact's own cost goes on the
`Mandate cost` line directly beneath the header (each artifact reference shows where),
phrased as a plan until the work has run and as spend once it has.

Write it honestly, including when the honest version is unflattering. An artifact that
admits it rests on assumption is useful. One that hides it is a liability that gets more
dangerous the further it travels from the person who wrote it.
