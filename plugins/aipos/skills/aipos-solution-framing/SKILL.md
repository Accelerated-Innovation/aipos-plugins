---
name: aipos-solution-framing
description: "Frame a solution on a one-page Solution Framing canvas for one problem from the Product Definition Graph — problem, evidence, hypothesis, solution options, assumptions and risks, validation plan and recommendation — live in a workshop or with a PM, then render it as an image. Use for solution framing or solution design workshops, canvases and the Solution Blueprint. Epics belong to epic-create; designing or running the pilot or experiment a canvas calls for, and viability briefs, belong to rapid-validation."
---

# AIPOS Solution Framing — the one-page canvas

## Purpose

Coach a Product Manager — alone or with a room — through a **Solution Framing canvas**: one page
that frames a solution before anyone commits to building it — what problem we're solving, how we
know, what we think will fix it, what else we could do, what we're betting on, and how we'll find
out. It replaces the Solution Blueprint, one canvas per Initiative.

The canvas gets shared, and then it gets quoted. So this skill works to two standards at once: the
coaching pushes on quality the way `aipos-epic-create` does, and every fact and every number on the
page is traceable — facts to the Product Definition Graph (PDG), numbers to the verifier that computed
them.

## Position in the lifecycle

```
Exploration Decision → aipos-solution-framing → aipos-rapid-validation → (aipos-epic-create) → aipos-feature-create
                        the canvas             runs the panel-6 plan     optional epic          behavior
```

The canvas sits at the start of Pillar 2. Its panel-6 plan is what `aipos-rapid-validation` runs;
its recommendation (Proceed / Pivot / Park) maps to that skill's GO / REVISE / NO-GO. Panel 1's
statement and panel 3's metrics can seed an epic if one is wanted.

## Product strategy context

For a supplied Product Opportunity Brief, read `../../references/strategy-handoff.md`.
Reference its revision, relevant problem/outcome, and strategic choices; this
canvas owns initiative-level options. Product-level strategy creation or revision
belongs to `aipos-product-strategy`. A brief does not change this canvas’s source,
baseline, Proceed, or approval rules.

## Key terms

- **Canvas** — the six panels plus a footer, recorded in `canvas.json` and rendered as an image.
  `canvas.json` is the record; the image is a view of it.
- **Fact** — a claim about the world: evidence, a baseline, a volume, a date, an example. Comes from
  the graph and carries a provenance mark: `[E]` evidence-backed, `[I]` inferred, `[T]` transcribed
  by a person from a record the graph links.
- **Decision** — something the PM authors: wording, targets, options, owners, the plan, the
  recommendation. Carries no mark.
- **GAP** — something missing. `GAP · evidence` is a fact the graph doesn't hold; `GAP · decision` is
  a choice not yet made. Shown on the canvas as a chip.
- **Graph-backed** — an `[E]` fact, or an `[I]` fact inferred from graph references. `[T]` is not.

## Operating principle

**The graph is the source of truth for facts. The PM owns decisions. Numbers are computed, never
typed.**

1. **Never ask the PM for a fact.** If the graph doesn't hold it, it's a `GAP · evidence`, and the
   question becomes *"what evidence would settle it, and where would it come from?"* — which becomes
   a ReOps to-do, a panel-5 assumption and a panel-6 plan item. A figure the PM volunteers is kept as
   an assumption beside the GAP, never used in a calculation. Two bounded exceptions, both labelled:
   a value the PM reads from a record the graph links is `[T]` and computes but never unlocks
   Proceed; with no graph connected, the PM's account is the only source (see *Inputs*).
2. **Never type a number the verifier can compute.** Percent changes, derived targets, savings,
   impact at scale, evidence counts and dates come from `scripts/verify_canvas.py`. A GAP input
   renders as a formula, never a placeholder.
3. **Proceed is unavailable until the primary metric's baseline is graph-backed.** The canvas
   recommends to a named owner; it never records a decision as made.

The rubrics live in `references/` and are meant to be read. If the PM asks why something was pushed
back on, show them the test it failed.

## Scope

Use this skill for:

- Facilitating a Solution Framing canvas, live in a workshop or one-to-one
- Building the canvas from a PDG problem or opportunity — or from the PM's account when no graph is
  reachable
- Resuming a saved canvas, refreshing it from the graph, and closing its GAPs
- Rendering the canvas as an image and handing off its to-dos and tracker write-back

Do not use it for:

- Writing an epic or program brief (`aipos-epic-create`)
- Designing or running experiments, or writing the viability brief (`aipos-rapid-validation`)
- Deciding which problems deserve exploration capacity (`aipos-exploration-planning`)
- Authoring Rules, scenarios or acceptance criteria (`aipos-feature-create`)

## Inputs

Everything is optional. Accept any of:

- A `problem_id`, a problem or opportunity name, or nothing (the skill offers a picker from the graph)
- An existing canvas to resume or change
- A hand-made canvas to import and check — its figures go in as stated values the verifier checks; `references/facilitation.md` (*Checking a hand-made canvas*) lists what to check before offering changes

**With the graph** (`references/opportunity-source.md`): detected by tool signature — `get_problem`,
`list_evidence` and `get_lineage` on one server. Panels 1 and 2 become a confirm conversation.

**Without it**: say so once and continue on the PM's account (`source.kind: pm-interview`). Facts are
recorded `[I]` with whose account they are and are computed with, so the arithmetic is still checked;
panel 2 stays empty; Proceed stays unavailable; a later resume with the graph re-grounds them.

**Never invent** personas, evidence, quotes, examples, baselines, volumes or thresholds. A GAP is a
legitimate output; a plausible number is not, because this page gets quoted.

## Required references

| Reference | Use |
|---|---|
| `references/facilitation.md` | The steps, in order; workshop vs coach pacing; review, render, save, resume. Follow it. |
| `references/panel-rubrics.md` | The quality bar, push scripts and common defects for each panel, and the coherence checks. Read before each panel. |
| `references/opportunity-source.md` | Detecting the graph, choosing the problem, the read sequence, evidence text, errors, refresh on resume, and the no-graph path. Read at Step 0. |
| `references/canvas-schema.md` | What `canvas.json` holds, the fact/decision/GAP contract, and every verifier code. Read before writing the canvas. |
| `../../references/problem-framing.md` | The solution-in-problem test and the problem statement — with the exceptions `panel-rubrics.md` names. |
| `../../references/metrics-and-evaluation.md` | The three-part metric and GenAI evaluation criteria — with the exceptions `panel-rubrics.md` names. |

| Script | Use |
|---|---|
| `scripts/verify_canvas.py` | Run after every panel with `--write`, having set `through_panel`. Checks the panels reached; computes every displayed number. Exit 1 on errors. |
| `scripts/render_canvas.py` | Renders `canvas.html`, and `canvas.pdf` / `canvas.png` when a headless Chrome is available. Runs the verifier itself and draws numbers only from it. |

Scripts live in this skill's folder; canvases live in the project folder. Run from the project
folder, naming the script by its full path:
`python3 <this-skill-folder>/scripts/verify_canvas.py solution-framing/<slug>/canvas.json --write`.

If a reference is unavailable, continue from this file and say which rules you are applying from
memory. If the scripts cannot run, say so: the canvas can still be facilitated, but no number on it
is verified and it must not be rendered as final.

## Proceed protocol

Treat **proceed, continue, looks good, approved, yes, go** as confirming the most recent summary, and
continue without restating it. Where options were offered, accept the option's name, its number, or
**default**. Advance from the latest answer; don't repeat what was already answered.

**A bare "proceed" never approves the canvas or authorizes a write.** Approval is asked for by name
(*"Approve the canvas as it stands?"*). A tracker write takes an explicit, destination-named yes —
one per record, per write. Approving the canvas's content is not approval to write anywhere outside
the project folder.

## The flow

`references/facilitation.md` has the detail. In short:

| Step | What happens |
|---|---|
| 0 Set up | Mode; resume check; detect the graph and choose the problem; promotion check; summarise the read; GenAI check; title and goal |
| 1 Problem & Context | Personas (locked), pain points, current-state snapshot, impact, the statement |
| 2 Discovery Evidence | Tiles of what the graph establishes; breadth and age; one approved quote |
| 3 Hypothesis & Outcomes | Primary metric first; baselines from the graph or GAPs; targets; *If … then … without …* |
| 4 Solution Options | Two or three genuinely different options; pros and honest cons; what each moves |
| 5 Assumptions & Risks | Seeded from the GAPs; the data assumption; risks with mitigations |
| 6 Validation & Decision | Evidence first, then the test; every assumption retired; the recommendation and its owner |
| 7 Footer | Who benefits; success; impact at scale (computed) |
| 8 Review | Verifier clean; coherence; nothing provisional; approval asked for by name |
| 9 Render | HTML → PNG / PDF; look at it before handing it over |
| 10 Save and hand off | Project folder (always `todo.md`); ReOps intake drafts; tracker write-back when a ticket is linked |

**Modes.** *Workshop*: fast, one push per item, gaps shown as chips, draft renders any time.
*Coach*: one question at a time, full pushing, no final render with open decision gaps unless the PM
accepts them. Same canvas either way.

## GenAI detection

Switch on silently and announce once, using the keyword and behaviour list shared with
`aipos-epic-create` (AI, GenAI, LLM, RAG, embeddings, retrieval, classifier, summarisation, chatbot,
assistant, agent, generation, reasoning, model behaviour…):

> This involves model behaviour, so panel 6 will carry evaluation criteria — and anything built under
> this Initiative inherits them.

## Output format

In conversation, after each panel: a two-or-three-line summary, then the next question.

At the end:

````markdown
# Solution Framing — <title>

**Recommendation:** <Proceed | Pivot | Park | open> to <owner> — <one line why>
**Blocking the decision:** <the GAP that matters most, or "nothing">
**First to-do:** <action, via ReOps intake>

| Panel | Status |
|---|---|
| <each panel> | complete / GAPs: <n> / not covered |

**Files:** solution-framing/<slug>/canvas.json · canvas.png · canvas.pdf · todo.md
**Open questions and gaps:** <every GAP and open question>
**Next:** aipos-rapid-validation runs the panel-6 plan.
````

An empty gaps list is suspicious — say so if it happens.

## Guardrails

Do not:

- Ask the PM for a fact when the graph is connected, or record a remembered figure as evidence
- Type a number the verifier computes, or render a number from anywhere but `computed`
- Put a quote or a real record on the canvas without the PM's approval for that specific item
- Paraphrase a record the graph could not show you, or fetch evidence text a panel doesn't need
- Offer Proceed while the primary baseline isn't graph-backed, or present a recommendation as a
  decision made
- Write to a tracker without an explicit, destination-named yes; claim a file was attached; or write
  anything to the graph
- Overwrite an approved canvas
- Invent options and present them as the team's, or let a solution into the problem statement
- Ask more than one primary question at a time in coach mode

Always:

- Read and summarise the graph before panel 1, including what it doesn't hold
- Check for an existing promotion or canvas before starting
- Turn every evidence GAP into a to-do, an assumption and a plan item
- Run the verifier after every panel and before rendering
- Look at the rendered image before handing it over — and if only HTML was produced, say the
  layout is unchecked rather than implying you looked
- Name the next skill when handing off

## Related

| Skill | Owns | Relationship |
|---|---|---|
| `aipos-product-strategy` | Product vision, strategy, and results-driven revision | Supplies canonical brief references and relevant choices; receives findings that challenge strategy. Initiative artifacts retain their own scope and authority rules |
| `aipos-exploration-planning` | Which problems get exploration capacity | Reads the same graph with the same tools; its Exploration Decision is what usually precedes a canvas |
| `aipos-rapid-validation` | Experiments, evidence, the viability brief | Runs the canvas's panel-6 plan; consumes the recommendation as GO / REVISE / NO-GO |
| `aipos-epic-create` | Epics and program briefs | Shares the problem-framing and metrics references; can take panel 1 and panel 3 into an epic |
| `aipos-feature-create` | Rules and scenarios | Downstream, once a commitment is in view |
