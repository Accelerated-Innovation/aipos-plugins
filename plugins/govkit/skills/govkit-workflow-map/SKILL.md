---
name: govkit-workflow-map
description: "Author or update workflow.json describing a customer journey, actors, branches, and handoffs, with references to canonical behavior. Use for journey structure and coverage gaps. Delegate rendering of existing workflow source to feature-map."
---

# GovKit Workflow Map — Authoring the Workflow Source

## Purpose

Produce the **one file** a customer journey is defined in, and keep it the only place that
definition lives.

A workflow says how an outcome is reached: the activities in order, who acts at each, where work
changes hands, and which Rules govern what happens. It holds **no behavior of its own** — every
behavioral claim is a reference into canonical Gherkin. That is the whole design. A Rule that
applies at four steps is authored once and referenced four times, so rewording it cannot leave
three stale copies behind in a picture nobody remembered to update.

**You never ask anyone to maintain a diagram.** L1, L2 and L3 are generated projections of
`workflow.json`, rendered by `govkit-feature-map`. If a view is wrong, the source is wrong; fix
the source and regenerate.

## Position in the lifecycle

Pillar 2 work: this is how a journey gets described before there is a commitment to anything in
it. The map is what makes "is this the whole journey?" a question someone can actually answer,
and `govkit-feature-slice` then selects which of that behavior a release contains.

The map is not an approval and never implies one. A rendered view showing a Rule proves the Rule
exists, not that anyone committed to it.

## Scope

Use this skill for:

- Authoring `workflow.json` from evidence, an opportunity, specs, or a conversation
- Adding activities, steps, actors or handoffs to an existing workflow
- Pointing workflow steps at the Rules and scenarios that govern them
- Finding behavior in the corpus that no step in the journey touches

Do not use it for:

- Writing Rules or scenarios — that is `govkit-feature-create`
- Deciding which behavior ships in which release — that is `govkit-feature-slice`
- Rendering the views — that is `govkit-feature-map`
- Drawing or editing a diagram by hand. There is no diagram to edit; there is a source file

## Required references

| Reference | Use |
|---|---|
| `../../references/workflow-source.md` | **The format.** Shape, the three views, diagnostics, cross-repository rules, and why order is not release scope. Read before writing any `workflow.json`. |
| `../../references/spec-identifiers.md` | The `@rule:` / `@scenario:` convention and the qualified reference form. Read before writing a reference. |

## Inputs

Everything is optional. Accept any of:

- An opportunity or problem reference and its evidence
- An existing feature corpus (`features.json`, or a directory of feature packages)
- An existing `workflow.json` to extend
- A description of the process in the user's own words
- Interview notes, a recorded walkthrough, a prototype

If there is a feature corpus, read it first. The Rules and scenarios that already exist are the
best available statement of what the journey does, and referencing them is cheaper and more
accurate than asking someone to re-describe behavior they have already written down.

## Process

### Step 1 — Name the outcome

One sentence on what the customer gets when the journey completes. Not what the system does —
what the person ends up with.

A workflow whose outcome cannot be stated in a sentence is usually two workflows.

### Step 2 — Declare the actors

Everyone and everything that acts: people by role, systems, agents, tools. Each gets an `id`, a
`name` and a `kind` (`human` · `system` · `agent`).

A role name is a real answer. **Do not invent a named persona** — grounding is the point, and a
fabricated person with invented goals is the opposite of grounding.

### Step 3 — Lay out the activities

The ordered, branching path a customer moves along. Each activity gets a stable `id` — it is what
a baseline and a map both point at, so it cannot repeat and should not be renamed casually.

Order is what a **customer experiences**. It is not build order and not release scope; a late
activity can ship first, and a `@v2` scenario can sit on an untagged activity. Keeping those
three apart is how a workflow map avoids quietly becoming a project plan.

Branches carry a `condition` saying what decides them. A branch with no stated condition is a
question nobody has answered.

### Step 4 — Add the steps and the handoffs

Inside each activity, the human / system / agent collaboration. The part worth the effort is the
**handoff** — `{"from": ..., "to": ...}` — because work changing hands is where most real defects
live, and a map that leaves it implied by adjacency hides exactly that.

### Step 5 — Reference the behavior

Point each activity and step at the Rules and scenarios that govern it, using the qualified form
`<source-key>/<feature-key>#rule:<slug>`.

Three rules, all of which the resolver enforces:

- **Reference; never restate.** If you find yourself typing what a Rule says into the workflow,
  stop — that is the second copy the format exists to prevent.
- **Reuse is expected.** A Rule referenced from four steps is correct and is not duplication.
  The L3 view shows it once with everywhere it is referenced.
- **Never invent an identifier.** A slug you cannot see in the corpus is a dangling reference
  that looks authoritative. Name the behavior in the author's words and say no identifier exists.

### Step 6 — Resolve, and report what is uncovered

Resolving needs two inputs: the workflow you just wrote, and the corpus as `features.json`.

**Produce the corpus first if it does not exist.** `features.json` is the ingested form of a
feature directory, not something a user keeps lying around:

```bash
python <plugin>/skills/govkit-feature-map/scripts/repo_ingest.py features/ -o features.json
python <plugin>/skills/govkit-feature-map/scripts/workflow_resolve.py \
    workflow.json features.json
```

Run these from the **project** directory, with `<plugin>` the installed plugin root — the
scripts ship inside the plugin, the inputs live in the project, and the two are not in the same
place. Substitute the real path rather than copying a placeholder.

**When there is no corpus at all** — a journey described only in conversation, with no feature
package written yet — resolution and coverage do not apply. Say so plainly rather than
manufacturing a `features.json`: the workflow's references are unverified until the behavior
they name exists. That is a normal state for a first draft, not a failure, but it must be
reported, because an unverified reference looks exactly like a verified one in the rendered view.

Where the corpus does exist, report both halves of what the resolver returns:

- **Diagnostics** — dangling and ambiguous references, unknown actors, transitions to nowhere,
  unparsed features. Errors are fixed before the map is worth reading.
- **Coverage** — behavior in the corpus that **no step touches**. This is the finding people
  actually need and the one no diagram ever gives them: an unreferenced scenario is behavior the
  map implies does not exist.

Uncovered behavior is a finding, **not an error**. A Rule may legitimately belong to a journey
this workflow does not describe. Say which case you think it is and let the user decide — and do
not silently attach an orphan scenario to the nearest plausible step to make the number go down.

**A `partial-coverage` warning means the count is a floor.** That feature had Gherkin that did
not parse, so what is listed as uncovered is only what was readable; there may be more. Report
it as a floor rather than a total.

### Step 7 — Ask only what changes the journey

Close with the gaps, and be selective. Ask about:

- A branch whose condition nobody has stated
- An activity with no actor, or a handoff to an actor nobody declared
- Behavior that exists in the corpus and fits no step you can see
- A step everyone describes differently

Do not ask for cosmetic completeness — a missing `name` you can infer, an activity ordering that
is obvious from the evidence, a step's `kind`. A skill that asks twelve questions to finish a
map teaches people to stop running it.

## Output format

````markdown
# Workflow — <outcome, in one line>

## Activities
| # | Activity | Actor | Next | Behavior refs |
|---|---|---|---|---|

## Handoffs
- <activity.step>: <from> → <to>

## Coverage
- Referenced: <n> rule(s) and scenario(s)
- **Uncovered**: <element, feature, and whether it looks like another journey or a real gap — or None>

## Diagnostics
- <errors first, then warnings, each naming the activity or step and the file — or None>

## Questions
1. <only gaps that would change the journey>
````

Then write `workflow.json` and say where it went. Rendering is `govkit-feature-map`'s job.

## Guardrails

Do not:

- Write behavior into the workflow instead of referencing it
- Invent a `@rule:` / `@scenario:` identifier, a persona, an actor, or a branch condition
- Duplicate a Rule because it applies in several places
- Ask the user to maintain a diagram, or produce one as an artifact to be hand-edited
- Attach uncovered behavior to a nearby step to make coverage look complete
- Treat `next` as build order, release scope, or a dependency graph
- Present a rendered view as an approval, or a covered Rule as a committed one
- Ask a question whose answer would not change the journey

Always:

- Read the existing corpus before asking anyone to describe behavior again
- Give every activity and step a stable id
- State a branch's condition, or record that nobody has given one
- Report uncovered behavior explicitly, including when there is none
- Say which file you wrote and that the views regenerate from it

## Related

- `govkit-feature-create` — authors the Rules and scenarios this map references
- `govkit-feature-slice` — selects which of the mapped behavior a release contains
- `govkit-feature-map` — renders the L1 / L2 / L3 views from `workflow.json`
- `../../references/workflow-source.md` — the format
