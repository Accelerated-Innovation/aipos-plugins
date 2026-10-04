# Section rubrics

The quality bar per section, with the push script and the defects that actually show up. Read the
relevant rubric before asking the question, not after the answer disappoints.

If a Product Lead asks why you pushed back, show them the test it failed.

---

## A1 and A2 — the customer and their world

**Passes when** it names a role, describes that role's current state in their own terms, and either
cites evidence or marks an explicit gap.

**Always asked.** Never pre-confirmed from a linked opportunity, however well written that opportunity
is. Show the inherited framing, then test it.

### Testing an inherited framing

Opportunities arrive from sales calls, support tickets, CRM notes and leadership requests far more
often than from Product. Five questions, in this order:

1. *Whose words is this in, and what did they want when they wrote it?* A problem raised to justify a
   deal and one raised to reduce ticket load are different problems even when the sentence matches.
2. *Problem or symptom?* Ticket volume is a symptom. So is churn. Ask what is happening to the person
   that produces it.
3. *Problem or solution in disguise?* "They need a dashboard", "they want self-service".
4. *Does the evidence support the problem as stated?* Usually it supports that something is wrong,
   which is a weaker claim and a different one.
5. *Has anyone spoken to the person who has it?* For leadership-sourced opportunities the answer is
   often no, and that is the single most useful thing to establish here.

Record both versions and what changed. If the restatement materially changes the problem, say so: the
thing Step 4 accepted is not the thing being briefed, and the impact estimate rests on different
ground. Flag it to the accountable owner rather than re-gating silently.

**Push script**

> That is how it came to us from <group>. Before we build on it, whose problem is it in their words,
> and what is happening to them on a bad day?

**Common defects**

| Defect | Looks like | Fix |
|---|---|---|
| Symptom as problem | "Support tickets are up 40 percent" | Ask what the person is experiencing that generates the ticket |
| Solution in disguise | "They need a readiness dashboard" | Ask what they do today instead, and what goes wrong |
| Current state as absence | "They have no way to assess readiness" | Ask what they actually do now, because they do something |
| Segment not role | "Enterprise customers" | Ask who personally has the bad day |
| Borrowed evidence | Evidence for a related problem | Name the gap rather than stretching the evidence |

**On thin evidence.** Not a failure. In Learn mode it is the strongest candidate for the learning
question at L3: the weak evidence becomes the thing the build tests rather than something papered
over. In Commit mode it is a GAP with an owner and a next action.

---

## C1 — the change we are after

**Passes when** it names a beneficiary, states a change in their world, and survives a change of
approach.

**Tests**

1. *No solution in the statement.* Could we deliver this a completely different way and still call it
   done? If no, a solution is embedded.
2. *Names the beneficiary.* Who is different afterwards? "The business" is not a beneficiary.
3. *A change, not an activity.* "Advisers can see the full history" is a capability. "Advisers stop
   rekeying the same facts into three systems" is a change.

**Push script**

> That reads as the thing we would build. If we solved it a completely different way, what would
> still have to be true for you to call it a win?

**Common defects**

| Defect | Looks like | Fix |
|---|---|---|
| Solution as outcome | "A copilot for claims handlers" | Ask what the handler's day looks like afterwards |
| Capability as change | "Users can query across systems" | Ask what they stop doing |
| Unfalsifiable | "Transform how we serve clients" | Ask what would make us say it did not work |
| Two products in one | "and also" | Split. Two briefs, or one with the second in D5 adjacent |

---

## C3 — who absorbs the change

**Passes when** it names the roles whose work gets harder or different, distinct from the beneficiary
named in D0.

Agentic products move work more often than they remove it. The role that absorbs the change is
usually the one that sinks the rollout, and it is almost never in the first draft.

**Push script**

> That is who gains. Whose work gets harder, or just different, for that to happen?

**Defects**: naming only the beneficiary again; "nobody, it is purely additive", which is almost never
true of an agentic product; "everyone".

---

## C4 — success measures

**Passes when** at least one measure carries a baseline **and** the source of that baseline.

The baseline matters more than the target at this stage. A target with no baseline cannot be judged
later, and in practice nobody goes back to establish one once the build has started.

**Tests**

1. Is there a number for today, and does it say where it came from?
2. Would two people reading this measure it the same way?
3. Is the primary measure about the change in D2, or about the system's activity?

**Push script**

> What is that today? And where would I find that number?
> If the answer is "I'd have to check" — good, that is a gap with an owner, not a blocker.

**Common defects**

| Defect | Looks like | Fix |
|---|---|---|
| Activity as outcome | "Number of queries handled" | Ask what it would mean if that number were high and nothing improved |
| Estimated baseline | "About two days, I think" | Record as a GAP with an owner, not as a baseline |
| Target with no baseline | "Under 4 hours" | Ask under 4 hours from what |
| Unowned gap | A baseline nobody is fetching | Every evidence gap takes an owner and a next action |

A Product Lead who volunteers a remembered figure gets it recorded as an assumption beside the gap,
never used as a baseline. This page gets quoted.

---

## D1 — adjacent, not ours

**Passes when** both columns have entries, and the adjacent column contains things somebody will
genuinely ask for.

The adjacent column is where the next quarter's scope arguments are. Settling one costs a sentence
now and a week later.

**Push script**

> What is the first thing someone will ask for once they see this working, that we are not doing?

**Defects**: an empty adjacent column; adjacent items that nobody would ever ask for, which means
the real arguments are still unlisted; scope written as features rather than as territory.

---

## D2 — what this will not do

**Passes when** there is at least one non-goal that costs something to hold.

A non-goal nobody wants is not a guardrail. This section is the cheapest risk control in the brief:
stated here, each item becomes refusal behavior in the agent contract at Step 7 and a boundary case
in the evaluation set at Step 9. Left unstated, it arrives as an incident.

**Push script**

> What will people push for, that we should say no to now while it is cheap?

**Defects**: non-goals that are really "not yet" items (those belong in D5 adjacent); a list with
nothing contentious in it; non-goals phrased so vaguely that no scenario could test them.

---

## D3 — where humans stay in the loop

**Passes when** it names decisions a person keeps, and says what the agent does when it reaches one.

This is the line between an assistant and an actor, and it is a product decision rather than an
engineering one. It sets the escalation paths in the agent contract, and it is the first thing
Security and Compliance look for.

**Tests**

1. Which specific decisions does a person always make?
2. What does the agent do on reaching one — stop, ask, route, or act and flag?
3. Can a person take over mid-flow, and what do they see when they do?

**Push script**

> When it reaches that point, does it stop and ask, or act and tell someone afterwards? Those are
> very different products.

**Defects**: "a human reviews the output" with no statement of what happens if they do not; review
posture that contradicts the autonomous-action triage answer — if T2 is Yes and D7 says a person
approves everything, one of them is wrong and it is worth finding out which before the roster is
routed.

---

## D4 — what would make us pull it

**Passes when** both columns are populated and the "would make us pull it" column names behaviors,
not outages.

You are not writing evaluation criteria here — Step 9 does that. You are setting the intent they get
written against, so the bar comes from the product rather than from whatever was convenient to
measure.

**Push script**

> Forget accuracy for a second. What would it have to do, once, for you to want it turned off?

**Defects**: a pull-it column that only lists downtime and latency; "behaving well" restating the
outcome in D2 instead of describing conduct; nothing about what it does when it does not know.

---

## Cross-section coherence

Check these before opening the review round. Each is a contradiction a reviewer will find anyway.

| Check | Contradiction |
|---|---|
| C1 against C4 | The primary measure does not measure the change the outcome claims |
| C1 against D2 | A non-goal rules out the only plausible route to the outcome |
| D3 against T2 | Autonomous action is Yes but the posture says a person approves everything |
| D3 against D4 | The pull-it column names behavior the stated human checkpoint would have caught |
| D1 against C4 | A measure depends on something listed as adjacent and not ours |
| A4 against A6 | Stated as critical, but nothing much is at stake |
| A4 against A7 | Stated as critical, but nothing has ever been tried, built or paid for |
| T1 against C4 | A baseline comes from data the triage says the product does not touch |

When one fires, name both sides and ask which is wrong. Do not pick for them.

---

## A3 — how much it matters to them

**Passes when** it records what the customer has already tried, built or paid for, or states plainly
that they have done nothing.

This is the highest-signal question in the set and the easiest to answer badly. A problem can be real,
evidenced and expensive and still sit untouched for years because people have absorbed it. Asking how
important it is returns Very every time; asking what they have already done about it returns
behaviour.

**Push script**

> That is the pain. What have they actually done about it, with their own time or their own budget?

**Probes**: where does this sit against the other things on their plate this quarter; if they do
nothing does it get worse or stay stable; is anyone's budget or objectives attached to fixing it.

**A stated nothing passes the check and changes the vision.** It moves adoption from a secondary risk
to the dominant one, which should show in C4's measures and in the Step 11 plan. In Learn mode it is
usually the best learning question available: cheaper to test than capability, and it fails faster.

**Defects**: an opinion in place of behaviour; a workaround described but not counted as effort; the
Product Lead's own urgency reported as the customer's.

---

## A4 — what we know and what we do not

**Passes when** every claim carries a source or is marked as a gap.

A vision gets quoted, and once quoted the distinction between evidenced and assumed is invisible
unless it was written down here.

**Defects**: a confident claim with an empty source; evidence for a related problem borrowed for this
one; a gap with no owner, which means nothing closes it.

---

## Block B — the opportunity for us

**Passes when** B1 to B4 are present and **every figure carries a source or the absence of sizing is
recorded as a gap with an owner.**

This is the most fabricated block in any vision. TAM numbers get invented, competitive
differentiation drifts into marketing language, and nobody notices because it reads well. The whole
block is held to the same discipline as the measures.

**Push script**

> Where does that number come from? If we do not have one yet, that is a gap with an owner, not a
> figure.

**Defects**

| Defect | Looks like | Fix |
|---|---|---|
| Unsourced size | "$2.4B market" | Gap with an owner and a next action |
| Fit by assertion | "This is strategic for us" | Ask what we hold that others would have to buy |
| No consequence of inaction | B3 lists competitors and stops | Ask what happens in eighteen months if we do nothing |
| Why-now with no closing condition | "The market is moving" | Ask what closes the window; if nothing does, the honest answer is not yet |

**On "what we believe that others do not":** the one form of a principles section worth having,
because it is differentiating and testable. It lives in B3. A separate principles block reliably
becomes platitudes.

---

## C2 — the arc, and what MVP proves

**Passes when** both halves are present: where this goes over two to three years, and what MVP is
proving on the way there.

Without an arc, no scope decision downstream can be judged as a step or a retreat.

**Defects**: an arc that is a feature roadmap rather than a widening of the change; an MVP that proves
the thing is buildable rather than that the bet is right.

---

## F1 — the statement

**Passes when** there is one stem and three to five verb-first focus areas, each traceable to
something in blocks A to D.

Written last, never first. A vision that cannot be said in a breath gets paraphrased, and the
paraphrase becomes the real vision.

**Two tests worth running out loud**

- Every focus area traces back to a block. One that traces to nothing is an aspiration.
- Everything important in A to D traces forward to a focus area. If something major does not, ask
  whether the statement is really covering the product.

**Say what it becomes:** the scope test for every future increment on this product. That is what makes
it worth the time rather than a decorative summary.

**Defects**: a solution in the stem; focus areas that restate each other; six or more areas, which
means the product is two products; language nobody would say aloud.

---

## F1i — the statement check, increments only

**A No is a routing result, not a defect.** The parent statement no longer covers this, so it is a
revision of the parent vision rather than an increment. Stop and re-scope. Do not try to make it pass.

---

## B1i — why this increment, and why next

**Passes when** it names what this was chosen over.

An increment always competes with the other increments you could build on the same product, and that
comparison is almost never written down. It is most of what makes an increment reviewable.

**Push script**

> What else could we have built on this product with the same effort, and why does this beat it?
