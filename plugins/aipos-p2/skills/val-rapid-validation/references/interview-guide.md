# 1 — Interview guide

**Retires:** *Is the problem real and worth solving?*
**Produces:** a guide someone can run 5–8 times next week without you in the room.

Interviews are the cheapest evidence in the system and the easiest to run badly. A guide
that makes people agree with the PM produces confident, worthless data — and it is
expensive precisely because it *feels* like validation. Everything below exists to prevent
that.

## The discipline

Three rules carry most of the value. Explain them to the PM if they push back on the
shape of the guide — they usually push back because they want to describe the idea, and
that instinct is the thing to resist.

1. **Ask about the past, not the future.** "Would you use this?" measures politeness.
   "Walk me through the last time this happened" measures reality. People are unreliable
   narrators of their future selves and reasonably good ones about last Tuesday.
2. **Don't reveal the solution until the end.** Once someone knows what you're hoping to
   hear, you can't unhear their accommodation. Park the reveal in the final section, after
   all the behavioural questions are banked.
3. **Chase the specific.** "It's frustrating" is not data. "It cost me forty minutes on
   Thursday and I had to call the client back" is. Every core question needs a follow-up
   that drives at a number, a date, or a name.

## Interview the PM first

One question at a time.

1. **Who are we talking to, and how will we find them?** Push for a real recruiting path —
   existing customers, a sales list, a community, a panel. "Users" is not a recruiting
   plan. Get to a screener: what makes someone in-scope versus a waste of a slot.
2. **What do you believe is true that this would confirm or break?** This becomes the
   hypothesis. If they can't answer, the guide has no spine — work on this before moving on.
3. **What would you do differently if you're wrong?** This is the decision rule. If the
   answer is "carry on anyway", say so kindly and ask whether the interviews are worth
   running at all.
4. **How many, and by when?** Five to eight is the working default — enough for patterns,
   few enough to run in a week. More than a dozen before a first synthesis is usually
   avoidance.

## Output template

```markdown
# Interview guide — <problem in the user's terms>

## Evidence base
<the evidence-base header from evidence-intake.md>
**Mandate cost:** <plans n sessions of the <budget> interviews budgeted · run by <date>, inside the horizon of <date> · used so far <n> | none declared>

## Hypothesis
We believe <specific, falsifiable claim about a behaviour or cost>. [E/I/A]

## Decision rule
- **Confirmed if:** <what we'd need to hear, from how many, to proceed>
- **Broken if:** <what would make us stop or reframe>
- **What we'll do either way:** <the actual next action, both branches>

## Who we're talking to
- **Target:** <role, context, and what makes them relevant>
- **Screener:** <2–3 qualifying questions with in/out criteria>
- **Target n:** <number> · **By:** <date>
<If Target n exceeds the interviews budgeted, or By falls past the horizon, say so here and
name what drops first — sessions, or questions — rather than quietly overrunning.>

---

## Warm-up (3 min)
<1–2 questions establishing role and context. Low stakes, gets them talking.>

## The last time it happened (12 min) — the core
<3–4 past-behaviour questions. For each, a follow-up that drives at a number, a date,
or a name.>

Example shape:
- "Walk me through the last time you <situation>."
  - *Follow up:* How long did that take? What did you do next? Who else got involved?

## Magnitude and workaround (6 min)
<How often, what it costs, what they do instead today, what they've tried and abandoned.
The existing workaround is the real competitor — spend time here.>

## Reaction to the idea (5 min) — last, on purpose
<Describe the concept in one or two sentences, then listen. Watch for the difference
between polite interest and someone asking when they can have it.>

## Close (2 min)
- "What haven't I asked that I should have?"
- "Who else should I be talking to?"

---

## Question hygiene — for whoever runs this
- Ask, then stop talking. Silence is the interviewer's most useful tool.
- If they agree with you enthusiastically and immediately, probe. Fast agreement is
  usually politeness.
- Record what they *do* today, verbatim where you can. Their words are the raw material
  for everything downstream.
- Note anything that contradicts our hypothesis and resist explaining it away in the room.

## Synthesis prompt — after the interviews
- How many independently described the problem without being led to it? __ / __
- What was the actual cost, in their terms and numbers?
- What are they doing instead today, and what would make them stop?
- What surprised us — and does it change the hypothesis?
- **Verdict:** confirmed / broken / inconclusive → next artifact: ______
```

## GenAI angle

If the solution involves model behaviour, add one question to the magnitude section
probing what happens when a system gets it wrong today: *"When something automated gives
you a wrong answer, how do you find out — and what does that cost?"* Tolerance for error
is the thing that decides whether a GenAI feature is viable, and it is much easier to ask
about now than to discover after launch.

## Quality bar

Before handing it over, check:

- No question can be answered yes/no without a follow-up that opens it back up.
- No question contains the solution, except in the reaction section.
- The hypothesis is falsifiable — you can state the sentence that would break it.
- The decision rule has a real "no" branch.
- It fits the stated time budget when read aloud. Guides that overrun get truncated in the
  room, and it's always the magnitude questions that get cut.
