# Facilitation

The stages in order, with pacing, resume and the review round. Follow this file.

## Step 0, set up

1. **Resume check.** Look for `product-vision/<slug>/vision.json` before asking anything. If one
   exists, say where it stands and offer to resume, review or revise. Never restart a record that
   already has a draft in it.

2. **The scope test.** Asked first, because it decides which questions get asked at all. It is a
   test, not a selection — incremental is the cheaper answer and therefore the one people reach for.

   | Question | |
   |---|---|
   | Does it serve the same user as the parent product? | |
   | Does it change who buys it, or why? | |
   | Could it stand alone as its own product? | |
   | **Does the parent vision's statement still cover it?** | the decisive one |

   No parent, or it could stand alone → **new**. Same user and buyer, statement still covers it →
   **increment**; link and read the parent vision before asking anything else. Contradicts the
   statement, or changes who it is for → **revision**; open the parent in revision mode rather than
   starting a new record.

   An increment that quietly contains a new product is how a product sprawls without anyone deciding
   to. Apply the test rather than taking the answer.

3. **Mode intent.** Record an intent only. Commit mode is the default. **The grant is a named step
   after triage and is the only thing that sets the mode.** Never offer Learn mode here.

4. **Link the lineage.** An accepted opportunity for a new vision, or the parent vision for an
   increment. For a new vision with no accepted opportunity — roadmap intent, or a retrospective
   write-up — record `no_opportunity_note` saying so. That is a legitimate state and the note is what
   keeps it visible rather than quiet.

5. **Detect the graph** by tool signature. Say once whether it is connected.

6. **Name two people**: the Product Lead, and the accountable owner. Only the owner can grant Learn
   Mode or ratify, and at `tier_3` they must be named before the round opens, so asking now saves a
   round.

7. **Pick pacing.** Coach or workshop. Say that the record can be paused at any point and resumes
   exactly where it left off.

## The blocks, in order

Ask from `data/flow-content.json`. Do not improvise prompts: the wording is shared with the AIOS
screen and drift between them is a bug. Each question carries an `asked_in` list; ask only what the
current mode and scope combination lists.

| Order | Block | Pacing note |
|---|---|---|
| 1 | **A** the customer and the problem | Push hardest here. Most defects downstream start in a thin A2 or an unexamined A5 |
| 2 | **B** the opportunity for us | Every figure sourced or marked a gap. This is the block that gets fabricated |
| 3 | **C** the direction | C1 first within the block. Baseline before target in C4 |
| 4 | **D** the boundaries | The adjacent list and the pull-it list are where the value is |
| 5 | **E** triage | Show who each question engages before asking it |
| 6 | the grant | Learn mode only, and only here |
| 7 | **F** the statement | Authored last, from everything above |

**A3 deserves its own note.** It is the highest-signal question in the set and the easiest to answer
badly. Do not ask how important the problem is — the answer is always Very. Ask what they have
already tried, built or paid for. A stated "nothing, they live with it" is a real finding: it moves
adoption from a secondary risk to the dominant one, and that should show up in C4 and in the Step 11
plan.

**Block A is always asked**, even when an opportunity is linked. A5 shows the inherited framing and
tests it; it never replaces the review. Opportunities arrive from sales calls, support tickets, CRM
notes and leadership requests far more often than from Product, so symptoms and solutions routinely
arrive looking like problems.

### Running triage

For each question, **show who it engages before asking it.** The "why we're asking" text names the
reviewer. This is the difference between a policy that feels legible and one that feels like an
ambush at review time.

Present Not Sure neutrally. It is a real answer, it routes conservatively, and it leaves a note.

After the last triage question, run the verifier and present the tier and roster **as a result** - and
**translate it**. The verifier's table is for the record. Nobody deciding anything should have to read
`blocking shape` and remember what it means.

Say who must respond, who gets a say, and who is told - in those words. Say what each reviewer can
actually do, in a clause, at the moment they appear. Never say computed roster, engagement level or
right; they are the machine's words. Lead with what happens, not with which rule fired.

> Your answers put this in the middle risk band. Four people have to respond before it can be
> finalised, two more get a say. Must respond: you, Engineering - who can change where the product is
> aimed - Security and Data and Privacy, who can narrow it or rule an approach out. Get a say:
> Marketing, and Compliance. Told about it: Sales.

Then, and only then, the rule that produced it, in one line:

> Three triggers are live, so this routes as tier_2, Elevated. That puts Security and Data Privacy on
> a blocking review alongside Engineering. Compliance is advisory because the regulated-domain answer
> was No.

Name the rule. Never present the roster as a proposal and never ask whether it looks right.

### Block F, the statement

Written last, never first. Everything above is the working-out; this is what people repeat, and a
vision that cannot be said in a breath gets paraphrased by others until their paraphrase is the real
vision.

One stem naming who it serves and what changes, then three to five verb-first focus areas, each
traceable to something in blocks A to D. If a focus area traces to nothing, it is an aspiration
rather than a vision. If something important in A to D traces to no focus area, ask whether the
statement is really covering the product.

Say what it becomes: the scope test for every future increment on this product.

## Learn mode

Entered only by a grant from the named accountable owner. Never offer it to a Product Lead, and never
treat "this is just a quick spike" as a request for it. What you can do is put the request to the
owner.

Learn mode is a peer of Commit mode, not a cut-down version of it. Say that plainly when it comes up,
because the moment it is heard as "the brief you write when you want less scrutiny", it starts
attracting the wrong work.

### Getting the grant

1. **Run triage first.** The mode changes what gets written and who reviews it. It does not change
   what the product is, and the owner needs the risk picture to decide.
2. **Show the computed roster**, and specifically who the grant routes past. The verifier prints this
   under ROUTED PAST BY THE GRANT.
3. **Ask the owner by name**, and take a reason and a review-by date in the same answer. The review-by
   date is not an expiry; it is a date on which they get asked again.

> Marcus, this routes tier_2 on the triage: Security and Data Privacy would both be blocking
> reviewers. A Learn mode grant drops them to inform. Grant it? If so, what is the reason, and by what
> date will you look at it again?

### What Learn mode asks

D2, D6 and D7, then the two questions this mode asks in place of a direction and a baseline:

- **LQ, the learning question** — what is this build going to answer? One question, answerable by the
  review-by date.
- **KC, the kill condition** — what result would make you stop? Name the finding, not the feeling.

Push on KC the way you would push on C1 in Commit mode. It is what this mode is rigorous about: less
about where the product is going, more about when the work ends. A kill condition like "if it does not
work" is not one. "Below 70 percent exact-source accuracy after two approaches" is.

The blocks a Learn-mode vision does not ask print as **n/a**. They are not missing and they are not owed
later. Leave them visible so the owner can see what the grant set aside.

### During the build

Run the verifier as usual. On every Learn mode run, report live promotion signals **to the accountable
owner**, not just into the record:

> Two signals are live on this brief: the review-by date passed on 20 September, and it is now running
> against production data. Promoting to Commit mode is your call. If it continues as learning, I will
> record that against the signals.

Never promote on a signal. Never let a Learn mode brief reach ratified with a signal unacknowledged
(check L6 will hold it, but say why rather than letting the check speak for you).

### Promoting to a Product Vision

Promotion happens when **intent changes**, not when the work gets bigger. The question has been
answered and this is heading for a commitment.

**Promote alongside Step 11, not after it.** The moment a build starts looking like it will work, open
the promotion: the Commit mode sections fill while the experiments are still running, so nothing waits
on anything. This matters more than it sounds. Promotion imposed after a successful proof of concept
lands process at the exact moment momentum is highest, and a mode that punishes success is a mode
people stop using honestly.

There is a reframe worth using out loud: the build **earned** the sections it did not have to write.
D4's baselines now come from the thing you actually made rather than from a week-one estimate.
Promotion is harvesting what the build produced, not catching up on paperwork.

Promotion keeps blocks A, C1, D2, D3, LQ, KC and every raise and disposition, opens blocks B, C and D
in full and block F, and **re-runs triage and the scope test** — intent changing usually means the risk profile moved, which is often why the
promotion is happening. It is one-way.

### Step 12

A Learn-mode vision cannot be the basis of a GO. Say so when the question arises, and say why: Step 12
reads the sections Learn mode does not ask for.

NO-GO and REVISE need no promotion. And most Learn-mode visions never reach Step 12 at all, because
they answered their question or hit their kill condition and stopped. That is the success case, not a
failure of the mode.

## Increments

An increment inherits the customer, the market case, the arc and the boundaries from the parent
vision. Link and read the parent before asking anything.

What is asked instead: **A1i** the unmet need inside an existing user base, **A2i** what production
shows — increments arrive with the best evidence in the system and often the worst framing of it —
**B1i** the incremental value and what it was chosen over, **C2i** where it sits in the parent's arc,
and **F1i**, the statement check.

**F1i answered No is a routing result, not a defect.** It means this is a revision of the parent
vision rather than an increment. Stop and re-scope rather than trying to fix it.

The prioritisation question in B1i is the one that is almost never written down: an increment always
competes with the other increments you could build on the same product, and saying what this beat is
most of what makes it reviewable.

## Revision mode

Open with the existing brief, never a blank page:

> This brief was ratified as version 1.0 on 14 June. This pass is a review, so we start from what is
> there and change what the evidence has moved. What has production told us?

- Never overwrite the ratified version. A new version supersedes it and both stay readable
- Every change carries a rationale and the signal behind it, usually from Step 19
- **Re-run triage.** A change of direction can change the tier and therefore the roster. Skipping
  this is how a brief ends up at tier_3 with a tier_1 roster
- Unchanged sections keep their dispositions and are not re-reviewed. Only changed sections go back
  to the reviewers whose sections they touch

## Pausing

Pausing never costs a round and never loses position. Say so when offering it. If a Product Lead
goes quiet mid-round, the brief sits in `in_review` with the open checks named in `todo.md` — do not
mark anything complete to tidy the record.
