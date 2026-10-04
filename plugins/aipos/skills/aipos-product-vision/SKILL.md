---
name: aipos-product-vision
description: "Facilitate a Product Vision or a Learn-mode vision through draft, routed stakeholder review and ratification — the customer and their pain, the opportunity for us, the direction and arc, the boundaries, and the statement that travels. Use for PMLC Step 6, Define Your Product Vision, for an increment on an existing product, for a proof of concept or low-risk build, and for the Step 20 re-entry that revises an existing vision. Engagement is routed from risk, and readiness is computed. The company-wide AI Vision belongs to ai-vision-builder; the per-problem canvas belongs to aipos-solution-framing; the product-level strategy and its Product Opportunity Brief belong to aipos-product-strategy."
---

# AIPOS Product Vision — draft, route, ratify

## Purpose

Take a problem worth solving and turn it into the artifact the rest of the cycle is built and judged
against: who it is for and what is hard for them, what the opportunity is worth to us, where the
product is going, what sits outside it, where people stay in the loop, and the statement people
repeat when nobody from this room is present.

It is PMLC Step 6. Reaching ratified is a handoff into Step 7. It is **not** approval to build.

## Two axes

These are orthogonal. **Mode decides depth. Scope decides inheritance.** Never collapse them into one
list of options.

### Mode — are we exploring, or committing?

**One artifact, two modes.** The record is a Product Vision in both. Promotion opens the remaining
blocks on the same record; it does not produce a different document.

| | **Learn mode** | **Commit mode** |
|---|---|---|
| Intent | We are exploring whether this product or feature is worth building. **Stopping is a success** | We intend to build this |
| Entered by | **A grant from the named accountable owner**, after triage, with a reason and a review-by date | Default |
| Rigorous about | When the work ends | Where the product is going |
| Carries | A learning question and a kill condition | An arc, measures with baselines, and the statement |
| Step 12 | **Cannot clear it** | Required to clear it |
| Rounds | 2 | 3, 4 or 5 by tier |

Learn mode is **not a reduced Product Vision**. It is the same artifact earlier in its life: the
blocks that only matter at commitment are not asked yet, and two that only matter in exploration are.

**Learn mode is for product or feature exploration, and nothing else.** A technical spike with no
candidate product or feature behind it is not Step 6 — it belongs at the team and work-management
level. If there is nothing a vision could eventually be written about, this is the wrong skill, and
the right answer to "can we just put the spike through Learn mode" is no.

### Scope — new, increment, or revision?

Decided by the Step 0 **test**, not by selection:

1. Does it serve the same user as the parent product?
2. Does it change who buys it, or why?
3. Could it stand alone as its own product?
4. **Does the parent vision's statement still cover it?**

No parent, or it could stand alone → **new**. Same user and buyer, statement still covers it →
**increment**. Contradicts the statement, or changes who it is for → **revision** of the parent.

An increment inherits the customer, the market case, the arc and the boundaries, and asks instead
what is newly unmet, what production shows, what the increment is worth, and why it is next. That is
roughly ten questions against twenty-two.

### Say this precisely, because the vocabulary is close to yours

**Both modes are authored at Step 6, and both sit inside Build-to-Learn.** Commit mode names an
*intent* to commit. A Product Vision has not cleared the Validation Decision and will not for another
six steps. Never let Commit mode be read as Build-to-Earn.

## The blocks

**Never list or ask questions from this file.** Run `scripts/questions.py <mode> <scope>` and ask
from its output. This file describes what each block is for; the question set, its wording and its
order live in `data/flow-content.json`, and a hand-maintained copy here drifts within days.

| Block | What it is for |
|---|---|
| **A** Understanding Your Target Customer and Their Current Reality | Who has the problem, what it is, how much it matters to them, what they do today, what is at stake, what they have already tried, and what of all that we actually know |
| **B** The Opportunity for Us | Why this matters to the business, named by category and ranked. Commit mode then sizes and positions the top one |
| **C** The Direction and the Arc | The change in the customer's world, where it goes over time, who absorbs it, how we would know |
| **D** The Boundaries | What sits just outside, what it will never do, what stays a person's call, what would make us pull it |
| **E** Triage | Seven risk questions. Computes the tier and the roster. **Never skipped, in any mode or scope** |
| **F** Your Product Vision Statement | The stem and three to five focus areas, authored last. Commit mode only |
| **L** Exploration | What is still open, what we need to learn, what would stop us. Learn mode only |

Three things carry most of the weight.

**The priority question and the prior-attempts question are a pair.** One is what they say, the other
is what they did. Asked alone, "how important is this" returns Very every time. The gap between the
two is the finding, and the verifier reports it: *stated as critical, nothing ever tried* means
adoption is the dominant risk, not capability.

**Block B is the most fabricated section in any vision.** In Commit mode a figure without a source is
a GAP, not a figure, and check V4 enforces it. In Learn mode the rule is clarity then dimension, not
precision: name the kind of benefit, size it only where there is a basis.

**The statement earns its keep twice** — once as the thing people repeat, and once as the scope test
every future increment is run against.

## Operating principle

**Risk routes the roster. The record computes readiness. A named person grants, ratifies and
promotes.**

0. **Never put work into Learn mode.** Only the named accountable owner grants it, and only after
   triage, with the computed roster in front of them. Offering it as a convenience is how it becomes
   the default.
1. **Never decide who should review.** The roster comes from `scripts/verify_vision.py` reading
   `data/engagement-policy.json`, which Security and Compliance own.
2. **Never assert readiness.** Every check is computed. There is no handle to drag.
3. **Never inherit a problem unexamined.** Opportunities arrive from sales calls, support tickets,
   CRM notes and leadership requests far more often than from Product. Block A is always asked, even
   when an opportunity is linked. A5 shows the inherited framing; it never replaces the review of it.
4. **Ratified is a handoff, not a build decision.** Say so, in both modes.

## Scope of this skill

Use it for a new Product Vision, an increment, a Learn-mode vision, a revision pass from Step 20, and
the review round and ratification for any of those.

Do not use it for:

- The company-wide AI Vision (`ai-vision-builder`). Block F borrows that skill's statement *format*
  at product scope; the inputs differ, so the authoring is not delegated.
- The per-problem Solution Framing canvas (`aipos-solution-framing`) — one problem, one cycle, with
  options and a validation plan. **If you are asking a PM to compare solution options, you are in the
  wrong skill.**
- Experiments and the viability brief (`aipos-rapid-validation`), epics (`aipos-epic-create`), or
  Rules and scenarios (`aipos-feature-create`).
- The proposed solution, how it would be built, how it would be tested, how it would be monetized or
  supported. Those have owners downstream, and pulling them in is how a vision becomes a spec.
- **Technical spikes.** Exploration of a product or feature belongs in Learn mode. A spike with no
  candidate product or feature behind it is team and work-management work, not Step 6.

## Required references

| Reference | Use |
|---|---|
| `references/facilitation.md` | Step 0 including the scope test, the blocks in order, the grant, the review round, promotion, revision. Follow it. |
| `references/section-rubrics.md` | The quality bar, push scripts and defects per block. Read before each block. |
| `references/vision-schema.md` | What `vision.json` holds, the raise and disposition contract, every check id. |
| `references/engagement-model.md` | Rights, engagement levels, routing, the Learn mode grant, promotion signals. Read at triage. |
| `../../references/problem-framing.md` | The solution-in-problem test, shared with the other aipos skills. |
| `../../references/metrics-and-evaluation.md` | The three-part metric and GenAI evaluation criteria. |

| Data | Use |
|---|---|
| `data/flow-content.json` | Every question, its why-we're-asking, examples and controls, with `asked_in` per combination. Ask from here; do not improvise prompts. |
| `data/engagement-policy.json` | Triggers, tiers, reviewers, rights, the grant rule. Owned by Security and Compliance. Read, never edit. |
| `data/readiness-rules.json` | Every check, its severity, and which combinations ask it. |

| Script | Use |
|---|---|
| `scripts/verify_vision.py` | Run after triage, after every review response, and before ratification. Computes mode, scope, tier, roster, readiness and promotion signals. Exit 1 on a blocking failure. |
| `scripts/questions.py` | Prints the exact question set for a mode and scope. **Run it at Step 0 and ask from its output**, never from the block tables in this file - they list every question, including ones the current combination does not ask. |
| `scripts/check_all.sh` | **Run after every change to `data/` or `scripts/`.** Content lint plus the fixture suite. A check added without fixture data turns the whole suite red, and it is easy to miss for several changes. |
| `scripts/check_content.py` | Content lint. Fails if any question lacks a worked example; warns on dense examples and on quality tests with no nudge. Run after editing `flow-content.json`. |

Run from the project folder:
`python3 <this-skill-folder>/scripts/verify_vision.py product-vision/<slug>/vision.json --write`.

If a reference is unavailable, continue from this file and say which rules you are applying from
memory. **If the verifier cannot run, say so and stop short of ratification** — nothing should be
called ready when no roster was routed and no readiness computed.

## How to ask

These are learned from running the skill, and each one came from an answer that went wrong. They are
also in `data/flow-content.json` under `content_rule`, so a screen and this skill cannot diverge.

**Ask from `questions.py`, never from a block description.** Reading a block and asking its questions
in order will ask Commit-mode questions in a Learn-mode vision.

**One thing per question.** A question carrying three or four things produces a run-on answer with
the parts missing, and makes hedging easy. If it needs more than one labelled line to answer, it is
more than one question.

**Read the worked example before asking.** Every question has one. The prompt alone reliably produces
a list of product capabilities instead of a description of a person.

**Plain words, and keep the subject on the right party.** "Challenges or opportunities" and "explore
solving" make a question feel like a form. "What are *you* trying to solve" invites the answer to
drift back to the product.

**When an answer misses, give the shape — not the goal.** "Describe the change, not the product" is a
goal and does not help. "[The role] [does something specific] instead of [what they do today]" is a
shape, and it does.

**Name the concrete decision points.** Do not ask abstractly what a person should decide; name the
three or four places in *this* product where it bites and ask which of them a person must own.

**Say why you are asking. Never say what comes next.** Announcing the following step makes the person
manage the flow instead of answering, and announcing a conditional step invites them to answer it
early.

**Translate the verifier before saying it.** Its output is a record, not a script. Say who must
respond, who gets a say and who is told, and what each can actually do. Never read out "computed
roster", "engagement" or "blocking shape" as labels.

**Clarity then dimension, not precision** — in Learn mode. A wrong number at exploration stage is
worse than no number, because it gets quoted.

**Step two has two motions. Do not collapse them.** Engineering is core team: they get an
**Engineering Vision Ideation** — a session brief, where the vision changes in the room and the output
is a changed vision rather than returned comments. Everyone else gets a **review request**, written
for the reader rather than the record, with no skill vocabulary in it at all. Sending a review request
to your own tech lead is the tell that the two were collapsed. `flow-content.json` →
`review.two_mechanisms` has both.

**Anything generated from the vision carries its evidence marks.** A8 records every claim as known,
inferred or a gap. A session brief, a review request, a summary or a paste into a chat that drops
those marks is strictly worse than the record it came from, because it turns an assumption into a
finding at the exact moment the claim leaves the room. Known claims state plainly and name the
source; inferred claims hedge the sentence and say so; gaps that bear on the reader's decision stay
in. Mark claims, not every line. `flow-content.json` -> `generated_artifacts`.

**Check the copy against the house voice.** Warm and direct, about the reader, commas rather than em
dashes, Title Case headlines, sentence case body, no emoji. "Four things to close before review" is
the system reporting its state; "we're ready to move on, and before we do there are three quick
questions" is the same information in the house voice.

## Nudge protocol

**Ask for clarity. Do not require it if it does not yet exist.**

When an answer trips its specificity test, **nudge exactly once**, using that question's own nudge
text from `flow-content.json`. Name what is missing and show the shape. Then stop.

**The ceiling is one, globally.** Never nudge twice, never rephrase the nudge to try again, and never
treat a held answer as non-compliance. Accept whatever comes back, including the same answer
unchanged.

If it is still general, record it and mark a gap saying plainly what we do not know yet. **The
absence of clarity at this stage is information, not a failure to correct** — it tells you what the
exploration has to find out, and in Learn mode it is usually a strong learning-question candidate. A
vague answer nudged once is honest. A vague answer ground out of someone over three attempts reads as
evidence later when it is not.

Count nudges on the record. A question needing a nudge on most visions is badly phrased; that is a
finding about the prompt, not about the people answering it.

## Proceed protocol

Treat **proceed, continue, looks good, yes, go** as confirming the most recent summary. Advance from
the latest answer.

**A bare "proceed" never grants Learn mode, never promotes, never closes a blocking raise and never
ratifies.** Each of those is asked for by name, of the named accountable owner. A tracker write takes
an explicit, destination-named yes, one per record, per write.

## The flow

`references/facilitation.md` has the detail.

| Step | What happens |
|---|---|
| 0 Set up | Resume check · **the scope test** · mode intent (default Commit) · link the opportunity or the parent vision · name the Product Lead and the accountable owner · pacing |
| 1 Block A | A1, A2, A3, A4, and A5 when something was inherited. Push hardest here |
| 2 Block B | The case for us. Every figure sourced or marked a gap |
| 3 Block C | C1 before everything else in the block. Baseline before target |
| 4 Block D | Boundaries, non-goals, human-in-the-loop, pull-it condition |
| 5 Triage | Show who each question engages **before** asking it |
| 6 The grant | Learn mode only, and only here. Show the roster and who it routes past, then ask the owner by name |
| 7 Block F | The statement, authored last from everything above |
| 8 Open the round | Verifier, dispatch, each invitation stating that reviewer's right |
| 9 Raises and dispositions | Every blocking raise answered. Constraints need acknowledgement to reject |
| 10 Readiness | Run the verifier. Report checks, never a feeling. Another round, or escalate |
| 11 Ratify | Present to the named owner. Record in their name |
| 12 Hand off | Version it, say what carries into Steps 7, 9, 12, 13, and say plainly this is not approval to build |

**Modes of pacing.** *Coach*: one question at a time, full pushing. *Workshop*: faster, gaps as chips.

## Promotion and Step 12

A Learn-mode vision becomes a Product Vision when **intent changes**. The owner decides; the verifier
computes promotion signals (risk profile changed, real users, production data, review-by passed,
spend committed) and reports them without acting. Check **L6** holds one thing only: a Learn-mode vision
cannot sit *ratified* with a live signal the owner has not acknowledged.

**Promote alongside Step 11, not after it** — the blocks fill while the experiments run, and the
measures come from what the build showed rather than a week-one estimate. The build *earned* the
sections it did not have to write. Promotion keeps everything, re-runs triage and scope, and is
one-way.

**A Learn-mode vision cannot be the basis of a GO at Step 12.** Structural, not a setting: Step 12 reads
D1, D4 and C4 with sourced baselines, which a Learn-mode vision does not ask for, and its REVISE path
re-enters at Step 7. NO-GO and REVISE need no promotion, and most Learn-mode visions never reach Step 12
at all — they answered their question and stopped, which is the success case. The rule belongs to
`aipos-rapid-validation`.

## Output format

In conversation, after each block: two or three lines of summary, then the next question.

````markdown
# <Product Vision | Learn-mode vision> — <title>

**Mode:** <Commit | Learn, granted by <owner> on <date>, review by <date>>
**Scope:** <new | increment of <parent> | revision of <version>>
**Status:** <draft | in_review | ratified> · version <v>
**Risk tier:** <tier> (<label>), from <live triggers>
**Readiness:** <n>% · <READY | n blocking open> · checks asked for <combination>
**Blocking it:** <the check or raise that matters most, or "nothing">
**Promotion signals:** <Learn mode only: each live signal, or "none live">

| Block | Status |
|---|---|
| <each block> | complete / GAPs: <n> / not asked |

| Reviewer | Right | Engagement | Responded | Open raises |
|---|---|---|---|---|

**Files:** product-vision/<slug>/vision.json · todo.md
**Open gaps:** <every GAP>
**Next:** <Step 7 | the owner's ratification | round N | re-scope as a revision>
````

An empty gaps list on a first draft is suspicious — say so if it happens.

## Guardrails

Do not:

- Suggest Learn mode, ask for the grant before triage, or carry a grant into a new record
- Grant Learn mode for a technical spike, or describe the two modes as two artifacts
- Take "increment" as an answer rather than applying the scope test
- Treat an inherited opportunity as confirmable rather than testable
- Accept a figure in block B with no source, or round a readiness number up
- Close a blocking raise from a constrain reviewer on the Product Lead's say-so
- Record a grant, a promotion or a ratification, or treat a bare "proceed" as any of them
- Describe a ratified vision as approval to build, or as having cleared Step 12
- State a claim in a generated artifact more confidently than the record states it
- Describe a Learn-mode vision as a reduced vision, or its unasked blocks as missing or owed
- Let Commit mode be read as Build-to-Earn
- Pull the solution, the build, the test mechanics, monetization or support into this artifact
- Write the statement before blocks A to D are answered
- Ask more than one primary question at a time in coach mode

Always:

- Ask from `questions.py` output for the current combination. Reading a block and asking its questions in order will ask Commit-mode questions in a Learn-mode vision
- Say why you are asking. **Never say what comes next** - it makes the person manage the flow instead of answering, and announcing a conditional step invites them to answer it early
- Ask **one question at a time**. A question carrying three or four things produces a run-on answer with parts missing, and makes hedging easy
- Read the question **and its worked example** from `flow-content.json` before asking it. The example is what tells someone the shape of answer wanted; the prompt alone reliably produces a list of product capabilities instead of a person
- Run the scope test first, and link the parent vision before asking anything on an increment
- Ask block A even when an opportunity is linked
- Show who a triage question engages before asking it
- Present tier and roster as computed results, naming the rule that produced them
- Run the verifier after triage, after every review response, and before ratification
- Report live promotion signals to the accountable owner, not just into the record
- Say which mode and scope the record is in whenever it is handed on
- Escalate rather than open another round once the ceiling is reached

## Related

| Skill | Owns | Relationship |
|---|---|---|
| `ai-vision-builder` | The company-wide AI Vision and its statement format | Block F borrows the format at product scope |
| `aipos-product-strategy` | The product-level strategy and its Product Opportunity Brief | Sets the strategic choices a vision is written inside; this skill owns the Step 6 artifact and its review |
| `aipos-exploration-planning` | Which problems get exploration capacity | Its Exploration Decision usually precedes this |
| `aipos-solution-framing` | The per-problem canvas, options, validation plan | Downstream and narrower; inherits the boundaries and non-goals as constraints |
| `aipos-rapid-validation` | Experiments and the viability brief | Owns Step 12 and the rule that a GO needs a Product Vision |
| `aipos-epic-create` | Epics and program briefs | Takes A1, C1 and C4 into the epic at Step 13 |
| `aipos-feature-create` | Rules and scenarios | Inherits D2 as refusal behaviour and D4 as evaluation intent |
