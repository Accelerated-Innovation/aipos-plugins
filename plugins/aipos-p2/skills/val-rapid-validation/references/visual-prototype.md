# 3 — Visual prototype

**Retires:** *Will the solution actually solve it?* — the target-experience half.
**Produces:** a prototype brief, and on request the working prototype itself.

## Two modes — ask which

> Do you want the brief on its own, or the brief and then the working prototype?

**Brief only** is right when someone else builds, or when the PM wants to circulate the
plan before anyone spends time. **Brief then build** is right when the PM wants something
testable today. Write the brief either way — it is what makes the prototype testable
rather than merely impressive, and it is the thing that outlives the prototype.

## Interview the PM

One question at a time, proposing rather than asking wherever evidence already answers it.

1. **Target persona.** If the evidence carries a persona set, propose the
   highest-confidence one and ask them to confirm or swap. If the set spans genuinely
   different populations, say so and ask whether to test one or carry a role switch — a
   breadth claim nobody tests is a breadth claim nobody should rely on.
2. **The riskiest assumption.** Propose it, informed by the evidence. This is the single
   most important line in the brief: *if the prototype can't move this, the idea shouldn't
   move forward.* Everything in the build serves it.
3. **The core scenario (JTBD).** One job, one flow. Not a product. Ask: "What is the one
   job the user is trying to get done that this prototype should let them complete?"
4. **Success criteria.** Validated / invalidated / inconclusive, in observable terms. Push
   past "they liked it".
5. **Scope.** What must be on screen, and what is deliberately absent.

## Output template

```markdown
# Prototype brief — <opportunity>

## Evidence base
<the evidence-base header from evidence-intake.md>
**Mandate cost:** <build effort in the mandate's units · the sessions it consumes · tested by <date>, inside the horizon of <date> | none declared>

**Problem:** <one line, in the user's terms> [E/I/A]
**Target persona:** <role> [E/I/A]
**Riskiest assumption under test:** <the one thing that decides whether this proceeds>
**Core scenario (JTBD):** <one job, stated as the user would state it>

## Screens / flow to build
1. <entry state>
2. <...>
5. <outcome state — what confirms the job is done>

## Data to show
<Every field that must appear, grounded in the evidence and realistic for the domain.
Wrong-sounding data destroys a test faster than ugly styling.>

## Test content design
<The composition of the sample data is the experiment, not decoration. Say what mix and
why — e.g. how many genuinely urgent items, how many routine, and any deliberately hard
cases. See "designing the content" below.>

## Success criteria
- **Validated:** <observable behaviour, not stated preference>
- **Invalidated:** <what failure actually looks like in the room>
- **Inconclusive:** <the honest middle — completes the task, weak intent>

## Out of scope
<Integrations, admin, configuration, analytics, adjacent roles — anything that will eat
build time without moving the riskiest assumption.>

## Evaluation considerations
<GenAI-specific watch-points, if applicable.>

**Build handoff:** Generate an interactive prototype (working HTML), not a static mockup,
so the scenario can actually be completed in a test.
```

## Designing the content

The sample data decides what the test can detect. Some deliberate composition, sized to
the artifact:

- **A realistic bulk.** Most items should be unremarkable. A screen where everything is
  urgent teaches nothing about triage.
- **At least one hard case** where the right answer requires attention — a detail buried
  mid-item rather than in the headline.
- **Realistic names, numbers and vocabulary for the domain.** A lawyer will disengage from
  a legal tool populated with "Client A / Matter 1". Domain-plausible content is what buys
  you honest reactions.

## GenAI: design for trust, not just completion

When the prototype surfaces model output — a summary, a ranking, a recommendation — task
completion is **not** evidence the system worked. A user who accepts a confidently wrong
answer has completed the task and told you nothing good.

Build in the instrumentation to tell the difference:

- **Show confidence and rationale.** Every model call displays how sure it is and why.
  Legibility is the thing under test; users can't calibrate trust in a black box.
- **Plant one confidently wrong output.** A recommendation that is high-confidence,
  plausibly reasoned, and incorrect — where the correction is available if the user looks.
  This is the only reliable way to detect rubber-stamping.
- **Include one genuinely ambiguous case** with low confidence and a hedged output. Watch
  whether uncertainty changes behaviour or gets ignored.
- **Make the source available but not default.** Put the original — transcript, document,
  raw record — one click away. Whether users reach for it is data: never opening it
  suggests overtrust; opening it every time suggests the AI layer isn't removing a step.
- **Log the session for the observer.** Which recommendations were accepted, which
  overridden, whether the source was opened, and how the two planted cases went. Keep it
  behind a control the participant doesn't touch.
- **Make the log exportable.** State is in memory and dies with the tab. Whoever runs the
  session is usually not the PM, so the log needs a copy-to-clipboard or download-as-file
  control in the observer panel, plus a participant field so sessions can be told apart. A
  log that can only be read on the runner's screen does not reach the person making the
  Validation Decision.
- **Tell the runner how to save it, on the page.** The person running session 4 will not
  have read this reference or the chat it came from. Put a short note in the prototype
  itself: the shortcut that opens the observer panel, fill the participant ID *before*
  starting, export at the end, and an explicit warning that closing or reloading the tab
  erases the session. Say who the file goes to. A shortcut only the builder knows is a
  session lost.

  **Placement is a real trade-off, so make it deliberately rather than by default.** A note
  visible on every screen is the one the runner can't miss — but the participant sees it
  too, and someone who knows they're being logged behaves more carefully than they would
  at their desk. In a test about trust, manufacturing extra care is the specific
  contamination you can least afford. The safer default is to show it only on the entry and
  completion screens: the runner reads it during setup and again when saving, and it is
  absent while the participant is working. Show it everywhere only when the runner is
  inexperienced and the risk of a lost log outweighs the risk of a careful participant.

  Write it as **two different notes, not the same text twice.** On entry it is a setup
  instruction — open the panel, enter the participant ID *now*, the panel stays hidden from
  here, nothing is saved automatically. On the completion screen it is a save prompt —
  reopen, export, closing the tab loses it, send the file to the PM. The completion screen
  is where a runner is most likely to close a finished-feeling task, so that is where the
  warning has to be blunt.

Overtrust and undertrust are both failures and they call for opposite fixes. Record which
one happened, not just pass/fail.

## If building

- **Self-contained single HTML file.** Inline the CSS and JS; no build step, no CDN
  dependency that can fail in a room with bad wifi. It has to open by double-clicking.
- **No browser storage APIs** — keep state in memory.
- **Interactive end to end.** Every screen in the brief reachable, every primary action
  doing something. A dead button is where a test stops being a test.
- **Credible, restrained styling** unless the PM wants deliberate low fidelity. The
  participant should react to the workflow, not the paint.
- **Verify before delivering.** Click through every screen and both the accept and the
  override path, check the console is clean, and confirm the planted cases behave as
  designed. A prototype that breaks in front of a participant costs a session you can't
  rerun.
- **Save all three to the record.** Brief, prototype, and — after each round — the exported
  session logs. See `references/record-writeback.md`. The brief without the prototype is a
  plan nobody ran; the prototype without the brief is a demo, and six weeks later nobody
  remembers which cases were planted.

## Quality bar

- The riskiest assumption is one sentence, and every screen serves it.
- Success criteria describe behaviour you could observe from across the room.
- Out of scope is longer than the PM's first instinct.
- A stranger could run the test from this brief without asking you a question.
