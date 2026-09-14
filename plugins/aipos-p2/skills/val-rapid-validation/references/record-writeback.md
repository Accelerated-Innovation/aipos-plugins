# Record write-back

Every artifact ends with an offer to put it on the tracker record. This exists because the
artifact's job is not to be read once in a chat window — it is to be findable six weeks later
by someone who wasn't in the conversation.

**Prompt every time. Write only on an explicit yes.** Never write to a system of record
unprompted, and never treat a general "sounds good" earlier in the session as standing
approval for a later write.

## The three pieces

Offer all three in one prompt, naming which apply. Most artifacts warrant all three; some
warrant two.

### 1. Attachment — the artifact itself

**This is the important one.** The full file, attached to the record. A comment describes an
artifact; an attachment *is* the artifact. An interview guide whose questions live only in
the PM's downloads folder cannot be run by the person taking session 4, which defeats the
point of writing it.

**Constraint you must state plainly: you cannot create attachments.** The Aha! connector can
read attachments but has no upload tool. So the offer is a named handoff, not a claim:

> "Attach `opp2-interview-guide.md` to OPP-2 — I can't upload files to the record myself."

Give the exact filename. "Attach the file" gets forgotten; a named file gets done.

**Fallback when nobody will upload:** post the full artifact as a second comment. It is ugly
and it will be long, but an ugly complete record beats a tidy incomplete one. Offer this
explicitly rather than letting the artifact quietly fail to land.

### 2. Comment — the index

A summary comment that lets someone scanning the activity feed understand what exists and
what it concluded, without opening anything. It should carry:

- the artifact name, its number, and the date
- the hypothesis or the question it was built to answer
- the decision rule or verdict
- the evidence-base line — especially when the honest version is unflattering
- what it does **not** retire
- anything that must be corrected before the artifact is used
- the next artifact

Keep it an index, not a duplicate of the file. If the comment and the attachment say the same
thing at the same length, the comment is wasted.

### 3. To-do — only when there is a named next action

**Do not create a to-do by default.** A to-do that isn't a specific action with an owner
trains people to ignore the queue, and then the ones that matter get ignored too.

The test: *does this artifact end with someone needing to do something specific?*

| Artifact | To-do? | The action |
|---|---|---|
| 1 Interview guide | Yes | Run n sessions by a date |
| 2 Problem sizing | Yes | Go measure the inputs that dominate the result |
| 3 Visual prototype | Yes | Run it in the sessions; attach the session logs after |
| 4 Demand test | Yes | Launch the test, with the stop date |
| 5 Feasibility spike | Yes | The spike itself, timeboxed |
| 6 Eval stub & brief | Usually not | It is a definition others consume |
| 7 Viability brief | No | It *is* the decision — a to-do here is a decision nobody made |

Write the to-do body as the actions themselves, ordered by how much each moves the result,
not as a description of the artifact.

## Naming

These get re-run. Three sizings six months apart are indistinguishable on a record unless the
filenames say otherwise.

```
<record>-<artifact>.md          e.g. opp2-problem-sizing.md
<record>-<artifact>-<date>.md   when a re-run supersedes an earlier version
```

Date every comment in its first line. When an artifact supersedes an earlier one, say so in
the comment and name what changed — a record with two sizings and no indication of which is
current is worse than a record with one.

## The decision record

When validation ran under an Exploration Decision, the viability brief has a second
destination beyond the opportunity record: the decision record itself, reached through the
governed door Pillar 1 named in the decision log's `Record via` line. The opportunity gets
the artifacts; the decision record gets the outcome — the Validation Decision, its
confidence, the budget used against the budget declared, and the evidence by filename.

This is what lets the next planning session see that what it funded came back with an
answer. Offer it in the same prompt as the three pieces above, as a fourth item, only for
the viability brief. Name the destination exactly (the ref, the door). If the door is not
something the skill can write through — most are not — hand the PM the entry text verbatim
and say where it goes. An entry the PM pastes is a closed loop; an entry the skill
describes is not.

Name it like the artifacts: `<record>-validation-decision.md`, dated on re-runs.

## Prototypes specifically

A prototype is three files, and all three belong on the record:

1. the **brief** — what is under test and how it will be judged
2. the **prototype itself** — the HTML, so anyone can open it
3. the **session logs** — after each round, exported from the observer panel

The brief without the prototype is a plan nobody ran. The prototype without the brief is a
demo, and six weeks later nobody remembers which cases were planted or what would have
counted as failure. Attach them together, always.
