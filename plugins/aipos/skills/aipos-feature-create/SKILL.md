---
name: aipos-feature-create
description: "Author new Rules, Gherkin scenarios, and feature packages from opportunities or feature briefs; decompose an epic; or materialize an approved baseline unchanged. Use for creating specifications. Existing-spec review belongs to refine; application implementation is outside this skill."
---

# GovKit Feature Create — Story Mapping and Feature Authoring

## Purpose

Coach a Product Manager through the work that happens *before* refinement: turning what is known
about an opportunity into behavior someone can actually review.

Four modes, one skill:

- **Opportunity mode** *(the AIPOS default)* — draft Rules and scenarios from an evidence-backed
  opportunity. No epic, no user story, no estimate.
- **Baseline mode** — materialize behavior an approved commitment already selected, without
  changing it.
- **Epic mode** *(legacy)* — lightweight story mapping to derive a feature set from a tracker epic.
- **Feature mode** — flesh out a single feature: structured description, tagged Gherkin, NFRs,
  Definition of Done, privacy.

You coach. You do not dictate. The PM makes every decision; this skill makes those decisions explicit and hard to skip.

## Position in the lifecycle

This skill is a **generator**: its output is Draft 0, the raw artifact that `aipos-feature-refine` then reviews with Product, QA, and Engineering. Draft 0 is deliberately not approved and this skill never claims otherwise — it never issues, recommends, or implies a Development Token.

```
aipos-feature-create → Draft 0 → aipos-feature-refine → Draft 1 → aipos-feature-readiness → Development Token
```

The rest of GovKit assumes something already produced Draft 0 (Aha!, an LLM, a human author). This skill is that something, for teams that don't have a generator or want one that writes the GovKit package shape directly.

**Where the commitment sits.** In AIPOS the hard commitment is the Pillar 2 exit: behavior is
drafted and refined *before* it, and what the commitment binds is a versioned selection of
Rules and scenarios. So substantive behavioral refinement belongs here and in
`aipos-feature-refine`, ahead of the decision — not after it, where changing it costs a new
decision. A Development Token remains an execution-readiness record downstream of that product
approval, never a substitute for it.

## Tool-agnostic design

Same abstract roles the other GovKit skills use:

| Role | What it means | Examples |
|---|---|---|
| **Tracker** | Wherever the epic and feature records live | Jira, Aha!, Azure DevOps, Linear, a markdown file, nothing at all |
| **Repo** | Where the feature package is written | `features/<key>/` in the working directory |

Named tools appear only as adapter examples. **The skill works with no tracker at all** — the conversation plus a markdown feature package is the complete, supported path, not a degraded fallback.

## Key terms

- **Backbone** — the 4–7 left-to-right user activities that make up the workflow an epic serves. Features hang off it.
- **Slice** — a horizontal cut across the backbone that delivers a usable outcome: MVP, V1, or V2. Slices span stages; they are not layers.
- **Feature stub** — name, epic link, release, type, owner, one-sentence description. Nothing else. Stubs exist for planning and traceability, not for review.
- **Feature package** — the repo artifacts a fleshed-out feature produces: `feature_source.md`, `acceptance.feature`, `nfrs.md`, and (GenAI only) `eval_criteria.yaml`.
- **Draft 0** — this skill's output. Unreviewed by definition.
- **GenAI mode** — evaluation-driven authoring, switched on automatically when the work involves model-generated behavior.

## Operating principle

**Explicit beats implicit; the PM decides; nothing is created silently.**

Three rules follow from that, and they are not negotiable:

1. **Ask one primary question at a time.** A wall of questions gets a wall of shrugs. One question, then default forward.
2. **Never create or modify a record without explicit approval.** Feature stubs are records other people will see and automations may fire on. Creating them is the single most outward-facing thing any GovKit skill does — see `references/tracker-adapters.md`, and confirm the whole set in one preview before creating any of it.
3. **Never claim the output is reviewed.** Draft 0 is a starting point for a refinement conversation. Say so when you hand it over.

This skill is transparent about how it works. Its rubrics live in `references/` and are meant to be read — if the PM asks why a feature was sliced a certain way or why a tag was applied, show them the rule.

## Scope

Use this skill for:

- Drafting Rules and scenarios from an evidence-backed opportunity, with no epic and no tracker
- Materializing behavior an approved baseline already selected
- Breaking an epic into features via story mapping (legacy route)
- Proposing and creating feature stubs
- Authoring a single feature's stories, description, Gherkin, NFRs, DoD, and privacy notes
- Writing a repo feature package that the rest of GovKit can read
- Creating or updating tracker records, after explicit confirmation

Do not use it for:

- Reviewing or scoring an existing spec's quality (`aipos-feature-refine`)
- Issuing a Development Token or validating a repo package (`aipos-feature-readiness`)
- Re-sizing or re-slicing existing scenarios per-scenario (`aipos-feature-slice`)
- Mapping a corpus that already exists (`aipos-feature-map`)
- Writing implementation code, step definitions, or tests
- Validating whether the epic is worth building at all — that is Pillar 2 (`aipos-rapid-validation`)

## Inputs

Everything is optional. Accept any of:

- An opportunity or problem reference from the Product Definition Graph, with its evidence links
- An approved commitment baseline (`commitments/<key>/baseline.json`)
- An epic record (pasted, from a file, or fetched via a tracker MCP) — legacy route
- A feature record or stub to flesh out
- A rough description in the PM's own words, with no record anywhere
- Existing personas, success metrics, NFRs, or epic-level evaluation criteria

Normalize into this working structure:

```yaml
mode: opportunity | baseline | epic | feature
source:
  tracker: jira | aha | markdown | none      # `none` is the AIPOS default, not a gap
  opportunity_ref: optional                   # PDG identifier; referenced, never restated
  decision_thread_ref: optional
  baseline: optional                          # path to an approved baseline
  epic_key: optional                          # legacy
  feature_key: optional
epic:
  name, elevator_pitch, user_problems, success_metrics, evidence,
  initial_scope, nfrs, personas, evaluation_criteria    # all optional
feature:
  name, description, release, type, owner, epic_link,
  acceptance_criteria, nfrs, definition_of_done         # all optional
genai: true | false
destination: repo | tracker | both
```

If a field is missing, record the gap and ask for it when you need it. **Never invent personas,
success metrics, evidence, or thresholds** — an assumption stated as an assumption is fine; a
plausible-looking fabricated metric is not.

**An epic, a user story and a point estimate are not prerequisites.** In opportunity and baseline
mode none of the three is requested, produced, or required, and their absence is never reported
as a gap. Asking a PM to write an epic so a skill can proceed is the exact prerequisite this
route removes.

**Unknowns stay unknown.** A missing threshold, an unmeasured metric, an evidence claim nobody
has checked — each is recorded in the unresolved register with what would settle it, and carried
into the draft as written. A specific-looking number nobody chose reads downstream as a decision
somebody made, which is worse than a blank.

## Required references

| Reference | Use |
|---|---|
| `../../references/gherkin-authoring-standard.md` | **The shared Gherkin authoring standard.** BRIEF, explicit rules, scenario isolation, provenance, automation suitability, deterministic checks vs aggregate evaluations. Read before Step F6 and F7 — it is what the gates judge your Gherkin against. |
| `../../references/spec-identifiers.md` | The `@rule:` / `@scenario:` identifier convention. Read before writing Gherkin. |
| `references/story-mapping.md` | Backbone construction, horizontal slicing, feature candidate patterns, the overlap and vertical-slice checks. Read before Epic mode. |
| `references/feature-template.md` | The feature package templates: `feature_source.md` structure, `nfrs.md` table, DoD checklist, privacy section, `eval_criteria.yaml`. Read before Feature mode. |
| `references/gherkin-tagging.md` | Gherkin structure rules, the tag vocabulary, automatic tag assignment, and the validation checks. Read before writing any Gherkin. |
| `references/tracker-adapters.md` | Create and update protocols per tracker, and the repo-package writer. Read before writing anything anywhere. |

If a reference is unavailable, continue from the guidance in this file and say which rules you are applying from memory.

## Proceed protocol

The PM should not have to fight the skill to move forward.

Treat **"proceed", "continue", "looks good", "approved", "yes", "go"** as confirmation of the most recent summary — move on without re-asking. Where options were presented, accept the option name, its number, or **"default"** (which selects the recommended path).

Only pause when ambiguity genuinely exists, or when the next step is a write.

**The one exception:** a bare "proceed" is never sufficient authorization to create or modify tracker records. Those require the explicit, destination-named confirmation in `references/tracker-adapters.md` — every time, no matter how many times the PM has already said yes.

## Mode detection

Detect the mode from what you were given and say which one you picked. Do not make the PM answer a routing question.

Four modes. **Opportunity mode is the default for AIPOS work**; epic mode is the legacy
compatibility route, kept because plenty of teams still work that way.

**Opportunity signals** — an opportunity or problem reference from the Product Definition Graph,
evidence links or interview notes, a validation or viability brief, prototype behavior to
describe, or a request to "turn this into a spec" with no tracker record anywhere. Say:

> Working from the opportunity. I'll draft the Rules and scenarios the evidence supports, mark
> what we don't know yet, and reference the PDG rather than restating the business case.

**Baseline signals** — an approved commitment, a `baseline.json`, or a request to "materialize",
"materialize the approved specification", or "set up the package for this commitment". Say:

> That behavior is already approved. I'll materialize exactly what the baseline selected —
> anything missing becomes a change question, not an edit.

A request to implement application code belongs to the coding workflow. This
mode only prepares the approved specification package; do not substitute it for
the implementation the user requested.

**Epic signals** — elevator pitch, user problems, success metrics, a list of things the product should eventually do, or a request to "break this down". Say:

> Looks like we're at the epic level. I'll map the workflow and derive a clean set of feature stubs — say the word if you'd rather work on one specific feature.

**Feature signals** — an epic link, a release, a feature type, acceptance criteria, a Definition of Done, or a request to "write this feature". Say:

> Looks like we're working on a single feature. I'll anchor the intent, define the stories, and turn them into acceptance criteria and delivery constraints.

**Neither** — a bare description with no structure. Judge by scope: if it spans a workflow, treat
it as an opportunity; if it is one capability, treat it as a feature. Say which you chose and why
in one line. Do not route to epic mode by default — an epic is a tracker artifact, and asking for
one the PM does not have is the prerequisite this route exists to remove.

Then proceed. Do not force a confirmation gate on the routing decision.

## GenAI detection

**Inherit first.** If an epic package exists and its header says `GenAI: yes` (written by `aipos-epic-create`), GenAI mode is on — the epic already decided; do not re-detect or re-announce beyond one line. Detection below is for features with no epic, or epics that predate the flag.

Switch on GenAI mode when you see model-generated behavior, in either mode.

**Keywords:** AI, GenAI, LLM, GPT, RAG, embeddings, vector search, retrieval, classifier, summarization, chatbot, assistant, agent, hallucination, groundedness, reasoning, safety, prompt, model, model behavior, OpenAI, Claude, Azure, Bedrock.

**Descriptions:** text generation · natural-language answers or interpretation · summarization or rewriting · retrieval of documents or passages · reasoning or decision-making · personalized responses or recommendations · transcript analysis · multi-step automation.

(This keyword and behavior list is shared verbatim with `aipos-epic-create` — change one, change both.)

**What does not count.** Using an AI coding agent to *build* the feature does not make the feature GenAI. The question is what the shipped product does at runtime. Ordinary software written with a coding agent needs ordinary test evidence, and demanding evaluation datasets for it is a false gate.

When detected, say once:

> This involves GenAI behavior, so I'll carry the stated evaluation requirements and flag any missing quality policy or thresholds. Tell me if you'd rather not.

Proceed in GenAI mode unless the PM explicitly disables it. Tag supported model behavior
`@genai`; derive `@evaluation` scenarios only from stated quality Rules or applicable
inherited criteria (`references/gherkin-tagging.md`). Review evaluation NFR categories
and produce a draft `eval_criteria.yaml` (`references/feature-template.md`). Missing
quality policy is a gap to resolve, not permission to invent acceptance behavior.

**The agentic-behavior question.** Once GenAI mode is on, ask the PM explicitly, once — the same question `aipos-feature-refine` asks at its checkpoint:

> One explicit check: agentic behavior — yes or no? Meaning: will this feature use AI agents that act autonomously (planning, multi-step tool use, orchestration of multiple agents, or agent-to-agent handoffs), as opposed to no AI at all or a single-shot AI call?

Record the answer as `multi_agent: true|false` in `eval_criteria.yaml`. **Never infer it from the spec, even when the answer looks obvious** — the team's explicit answer is the record. If the PM defers, leave `multi_agent` unset and list the question as an open gap. Asking here means refine confirms the flag instead of discovering it missing, and batch scoring downstream can read it from the record.

**Inheritance.** If the parent epic carries evaluation criteria, show them briefly and say:

> These evaluation expectations already exist at the epic level. I'll apply the relevant ones here and adjust as needed.

Apply only the subset that is actually relevant to this feature, and name which ones you dropped. Inherited thresholds are the epic's numbers — carry them across unchanged, and never invent a threshold to fill a gap the epic left.

---

# Opportunity mode — drafting behavior from evidence

**The default AIPOS route.** An opportunity from the Opportunity Engine, its evidence, and
whatever conversations and prototype behavior exist become Draft 0: Rules and scenarios good
enough for a refinement conversation, and honest about what is not yet known.

No epic. No user stories. No point estimate. None of the three is asked for, and their absence
is not a gap.

### Step O1 — Reference, do not restate

Record the opportunity and decision-thread identifiers and move on. The problem, the evidence
and the rationale live in the PDG and have an owner there. Copying the business case into a
feature package creates a second editable copy that drifts from the first, and the drift is
invisible because both look authoritative.

Pull through only what the *behavior* needs: a feature-local observable outcome,
the affected parties, and the constraints the evidence implies. Reference the
opportunity's existing outcome where that already expresses the result; do not
add a second editable business-case section. Rule-to-evidence tables carry source
references and the inference made, not copies of interview counts or telemetry
findings maintained in the PDG.

### Step O2 — Name the outcome and the actors

Use `outcome_ref` when the opportunity already owns the outcome. Add a feature-local
observable effect only if it is distinct; do not copy or paraphrase the canonical outcome
into another editable Outcome, Summary or business-case section. Name who is involved.
If the PDG carries personas, use them; if not, a role name is a real answer. **Do not invent a named
persona with invented goals** — the point is grounding, and a fabricated persona is the opposite.

### Step O3 — Derive the Rules from the evidence

Rules are the policies that decide what happens, and they are what the whole downstream
organizes around. Work from what the evidence and the PM actually say.

For each rule: one line in the PM's own words, a stable `@rule:<slug>` identifier per
`../../references/spec-identifiers.md`, and the evidence reference that supports it where one
exists.

**Where the evidence does not support a rule, say so rather than writing one.** A rule nobody
stated, sitting in a Draft 0, is read downstream as a decision somebody made. "The PM has not
said what happens above the limit" is a finding; an invented limit is a fabrication.

Evidence of a problem can motivate a policy proposal without establishing that policy.
A Rule described as inferred, unconfirmed or awaiting a product choice stays in the
unresolved register, outside acceptance Gherkin. Draft the supported portion now;
missing policy does not require withholding the whole Draft 0.

Ask each rule's **boundary** — a threshold, window, limit or count is where the business most
often disagrees with itself. If the boundary is unknown, it goes in the unresolved register with
the number left blank, not filled in with something plausible.

### Step O4 — Draft scenarios against the Rules

Per `../../references/gherkin-authoring-standard.md`, with `@scenario:<slug>` identifiers.
Every scenario illustrates a stated Rule. If no stated Rule explains it, keep the proposed
policy or test idea in the unresolved register, outside `acceptance.feature`. A warning,
TBD threshold or unrelated parent Rule does not make an unsupported scenario valid.
For an opportunity Draft 0, keep incomplete scenario candidates in the unresolved
register alongside their Rule, source and missing decision/parameter. The acceptance
file contains only scenarios whose policy and expected outcome are established; it
does not contain placeholder scenarios. This changes where the unknown is recorded,
not whether the draft can proceed. Preserve the stated Rule and the coverage gap.

Check the inference behind each `Then`: could a different behavior also satisfy the
source Rule? If so, choosing between those behaviors is a product decision, not an
illustrating example. Do not choose a lifecycle transition, permission or recovery
policy merely because it would be a plausible way to enforce the Rule.

Where behavior comes from a **prototype**, say so and treat it as a proposal. A prototype
demonstrating something is not a decision to build it, and behavior that reaches a spec because
"the prototype did it" is exactly how unapproved scope arrives.

### Step O5 — Constraints that actually apply

NFRs, and — **only when the product itself contains runtime AI behavior** — its evaluation
criteria and agent tool authority.

Ordinary software written by a coding agent does **not** need model-quality evaluations. The
question is whether the *product* makes a judged, non-deterministic decision at runtime, not
whether an AI helped write it. Applying GenAI evaluation machinery to a CRUD form produces
ceremony nobody reads and teaches people the gates are noise.

### Step O6 — The unresolved register

Close with what is not known, each with what would settle it, and whether it could change
included behavior. A question that could change behavior, an expected outcome or a constraint
**blocks commitment**; an internal implementation choice does not.

This register is the deliverable, not an apology for one. A Draft 0 that names six real unknowns
is more useful than one that quietly answers them.

### Step O7 — Write the package

Write the feature package per `references/feature-template.md`, then hand off to
`aipos-feature-refine`. Draft 0 is not approved and this skill never implies otherwise.

Which shared Feature-mode steps run:

| Step | Opportunity mode |
|---|---|
| F5 Structured description, F8 NFRs, F9 DoD, F10 Privacy, F11 Overlap, F12 Write | Run |
| F1 Personas | Runs only if the PDG carries them; a role name is a real answer |
| F2 Intent and size | Runs as a sanity check, **without** a point estimate |
| F3/F4 User stories | Do not run — Rules and scenarios carry the scope |
| F6 Business rules, F7 Acceptance criteria | Replaced by O3 and O4 above |

---

# Baseline mode — materializing approved behavior

An approved commitment already decided what gets built. This mode writes the package for it and
**changes nothing about what was approved**.

### Step B1 — Read the baseline, do not re-derive it

Resolve the selected Rules and scenarios from the baseline's references. Materialize them as
written.

**Do not improve them.** Not the wording of an approved `Then`, not an `Examples` row, not a
missing edge case you can see. The baseline's digest binds the exact text; changing it under a
matching digest is the drift the whole contract exists to catch, and doing it helpfully does not
make it less so.

### Step B2 — Missing behavior is a question, not a fix

When the approved selection has a genuine gap — a recovery path nobody specified, an
authorization step the Rule implies but no scenario covers — **write the change request, not the
behavior**:

> The approved baseline has no scenario for <case>. I have not added one. Here is the proposed
> change: <affected Rule/scenario IDs>, <old behavior → new behavior>, <why>, <what evidence
> supports it>. This needs a decision before it can be built.

The same applies to anything the prototype did that the baseline excluded. If the baseline lists
`automatic-send-on-high-confidence` as an exclusion and someone asks for automatic sending, the
answer is a proposed change referencing that exclusion — never a quietly edited spec.

### Step B3 — Say what is approved and what is not

The package states which behavior the baseline selected, which it excluded and why, and which
of its own contents are derived rather than approved (tests, implementation notes, structure).
A reader must be able to tell the committed behavior from the packaging around it.

### Step B4 — Write the package, then stop

Write the feature package per `references/feature-template.md`, then **end**. Baseline mode is
complete here.

**Feature mode does not run after this.** Not F6 and not F7 above all: "enumerate the business
rules this feature enforces" and "write the acceptance criteria" would re-elicit behavior a
commitment already decided, and re-eliciting approved behavior is how it gets reworded into
something subtly different by a conversation nobody recorded as a change.

Which shared steps run, and which never do:

| Step | Baseline mode |
|---|---|
| F5 Structured description | Runs — describes the package, not the behavior |
| F8 NFRs, F9 DoD, F10 Privacy | Run **only** for constraints the baseline did not select; approved ones are materialized as written |
| F11 Overlap check | Runs |
| F12 Summary and write | Runs |
| F1 Personas, F2 Intent and size | Do not run — settled at commitment |
| F3/F4 User stories | Do not run |
| **F6 Business rules, F7 Acceptance criteria** | **Never run.** The baseline already decided them |

---

# Epic mode — story mapping and stubs *(legacy compatibility route)*

Kept deliberately: teams working from a tracker epic still get the full story-mapping path, and
nothing about it changes. It is no longer the default — see Opportunity mode above.

Goal: a workflow-aligned, non-overlapping feature set that represents a usable journey, supports MVP slicing, and avoids vertical over-engineering.

### Step E1 — Read the epic

Read silently: name, elevator pitch, user problems, success metrics, evidence, initial scope, NFRs, personas, evaluation criteria. Detect GenAI relevance. Note what is missing rather than filling it in.

### Step E2 — Build the backbone

Say what you are doing and why, in one line:

> I'll outline the user journey first, so features come out as usable slices rather than technical layers.

Identify the primary persona, then propose **4–7 left-to-right user activities** as a simple ordered list, per `references/story-mapping.md`. Then:

> Here's the proposed workflow backbone. I'll proceed unless you'd like adjustments.

Keep the backbone centered on the primary persona's path to the outcome. Show other actors at the handoff they support, rather than adding their separate administrative journeys to the backbone. Refine only if asked.

### Step E3 — Propose horizontal slices

> Now the smallest end-to-end slice that delivers measurable value.

Propose an MVP slice, and optionally V1 and V2. **When an epic package exists, start from its confirmed Initial Scope / MVP** — propose slices as a refinement of that scope, not a rederivation, and flag any divergence from it explicitly. Every slice must span multiple backbone stages, deliver a usable outcome, and tie to a stated success metric. A slice that touches one stage is a layer, not a slice — rework it. If a later
idea has no supported outcome or metric, keep it in open questions rather than
presenting it as a defined V1/V2 slice. Do not invent a metric to complete it.

### Step E4 — Propose feature candidates

A numbered list. Each candidate carries a short action-oriented name, a **one-line scope boundary** stating what it owns, and its slice.

Every listed candidate, including deferred candidates, needs the same ownership boundary; a blocked/status note does not replace what it owns and does not own. Coach toward clear boundaries, durable responsibilities, minimal overlap, and no vertical capability-only features.

### Step E5 — Integrity checks

Run both checks from `references/story-mapping.md` before proposing anything for creation:

- **Overlap.** Two features claiming the same responsibility: *"These two look like they overlap on <responsibility>. I'd suggest giving <A> ownership and having <B> consume it, so each has a clean boundary."*
- **Vertical-only.** Deep capability that never spans enough workflow to deliver user value: *"This is a lot of depth without enough of the journey to be usable on its own. I'd suggest widening the scope."*

Resolve before proceeding. An unresolved overlap becomes two teams building the same thing.

### Step E6 — Defaults

State recommended defaults for release, feature type, and owner:

> I'll apply these defaults unless you prefer otherwise.

Allow per-feature overrides.

### Step E7 — Create the stubs

**Recommend creating the MVP slice's stubs now and deferring V1/V2.** Stubs for features two slices out are inventory: they age, they get renamed, and their presence invites premature work. Offer the deferral as the default; the PM can override and create the full set — their call, one line, no argument.

Present the **whole set now** as a table with exactly the six stub fields:
name, epic link, release, type, owner, and a one-sentence description. Reuse
confirmed candidates and defaults; show an unresolved value as a gap rather
than inventing it or asking the user to approve an unseen table.

If tracker tools are absent, say so and deliver that same copy-ready table;
do not ask the user to establish tool availability or imply a write happened.
If a tracker create remains possible and is not already authorized for this
exact preview and destination, state the permanent-key/deletion limitation
from `references/tracker-adapters.md` and ask one explicit question covering
the whole set. Resolve missing required values before that final approval.
An authorization already covering the reviewed set persists; do not ask again.

Stubs carry **nothing else**. No acceptance criteria, no NFRs, no Definition of Done, no privacy text — those are Feature mode's job, and a stub padded with unreviewed detail is worse than an empty one because it looks finished.

Destination follows `references/tracker-adapters.md`: a repo directory per stub by default, tracker records only after the explicit confirmation.

Close with the confirmed backbone, the confirmed slices, the final feature list, and where each one landed. Then stop — do not roll straight into Feature mode.

---

# Feature mode — authoring one feature

Goal: one feature defined well enough that a refinement conversation has something real to work on.

### Step F1 — Personas

If the epic carries personas, list them and default one as primary from context:

> I'll treat <persona> as the primary persona unless you'd prefer another. Personas keep the stories, scenarios, and any GenAI behavior grounded in someone specific.

If no personas exist, ask for one. Do not invent a persona — "the user" is a real answer and a marked gap; a fabricated named persona with invented goals is not.

### Step F2 — Intent and size

Ask, in plain language: *what should this feature deliver?*

Then check size: *does this feel like it finishes in about two sprints?* If it sounds larger:

> This may be bundling several features. I'd suggest splitting it, but we can carry on if that's deliberate.

Proceed on the PM's answer. Size is their call; naming the risk is yours.

### Step F3 — Primary user story *(legacy route only)*

**Skip this step in opportunity and baseline mode.** Rules and scenarios carry the scope there,
and a story adds a restatement to maintain. Kept for teams whose tracker expects one.

Anchor scope with one story:

```
As a <primary persona>, I need <capability> so that <outcome>.
```

The outcome is the part that matters — "so that the form submits" is a restatement, not an outcome. Draft it, then proceed unless the PM adjusts.

### Step F4 — Secondary user stories *(legacy route only)*

Ask whether other personas or outcomes need stories. Draft each. Zero is a valid answer — and in
opportunity and baseline mode, zero is the only answer, because the step does not run.

### Step F5 — Structured description

Draft section by section per `references/feature-template.md`: Summary · Functional Scope · Out of Scope · Dependencies · Produces / Consumes · Key User Flows.

**Out of Scope is not optional.** It is the section that prevents the most rework, and the one PMs skip most often.

**Produces / Consumes** are the named artifacts this feature emits and depends on, in kebab-case — they come almost verbatim from the Epic-mode scope boundaries ("A owns it, B consumes it") and they are what `aipos-feature-map` builds its dependency chain from. A feature with no entries in either is rare; ask once.

### Step F6 — Business rules

Before any Gherkin, enumerate the business rules this feature enforces:

> What are the rules here — the policies that decide what happens? Things like "invoices of $10,000 or more require manager approval."

Rules are the one thing the PM knows and a coding agent must never invent, and the entire downstream organizes around them: refine's rule-coverage dimension, Example Mapping's Rules cards, `eval_criteria.yaml`'s `rule_link`, the readiness gate, and the feature map's cards all group by rule. A feature usually has two to five; one is common; zero means the feature is pure mechanics and worth a second look.

For each rule, capture one line in the PM's own words, and give it a stable identifier — `@rule:<slug>` per `../../references/spec-identifiers.md` — so evaluations, NFRs and evidence can point at the decision rather than at its current wording.

For each rule, ask what the rule's **boundary** is. A rule with a threshold, limit, window or count has one, and the boundary is where the business most often disagrees with itself. "At or above $10,000" needs an example at exactly $10,000, not only comfortably above and comfortably below.

Where a scenario will exist that no stated rule explains, that is a missing rule — surface it now, not at refinement. **Never write a rule the PM did not state.** A plausible policy in a Draft 0 is read downstream as a decision somebody made.

### Step F7 — Acceptance criteria

> We'll write the acceptance criteria as executable behavior specs — fully-formed Gherkin with structured tags, so CI and evaluation can filter on them.

Generate complete, syntactically valid Gherkin per `../../references/gherkin-authoring-standard.md` (what good looks like) and `references/gherkin-tagging.md` (tags and validation): `Feature:` header, persona intent block, **one `Rule:` block per business rule from Step F6** with its scenarios grouped beneath, `Background:` scoped correctly — feature-level only when genuinely shared by every scenario, rule-level when shared by one rule's — atomic scenarios, no implementation detail.

Four things from the standard are worth stating here because they are what the gates check first:

- **Every scenario illustrates a stated rule, establishes a meaningful context and one trigger, and asserts observable outcomes.** Several related outcomes of one trigger are fine. Without a supporting Rule, keep the proposal in the unresolved register, outside accepted Gherkin; merely flagging the missing Rule is insufficient.
- **Every scenario is independently executable.** Never write "the invoice from the previous scenario"; put the state in this scenario's own `Given`.
- **Cover the boundary, the negative path, permissions and exceptions where they matter — then stop.** An exhaustive combinatorial catalog drives readers away from the document, which costs more understanding than the extra cases buy. Use `Scenario Outline` for real data variation of one behavior.
- **Mark what is derived.** You may derive illustrating examples from a confirmed rule; say in the summary that the values are proposed for confirmation. You may not invent a policy, a threshold, a permission model, or anyone's approval. A missing parameter of a stated outcome may be `<TBD — …>` plus an open question, making the scenario non-executable. An undecided outcome or inferred policy stays outside acceptance Gherkin in the unresolved register.

**Assign tags automatically.** Derive the delivery-phase tag from the feature's slice and the classification tags from each scenario's behavior. Do not make the PM pick tags. Ask only when the feature's slice is unclear, a scenario spans delivery phases, or the intent genuinely cannot be classified.

Run the validation checks in `references/gherkin-tagging.md` and fix what fails before presenting — a missing tag is a defect to correct, not a question to ask. Then present the **full Gherkin** plus a one-line tag coverage summary (`4 scenarios · 4 @mvp · 3 @functional, 1 @edge-case`), so the tagging is visible even though it was automatic.

> I'll use this as the acceptance criteria unless you'd like refinements.

### Step F8 — Non-functional requirements

Inherit a constraint's applicability together with its threshold. A control
triggered by external sharing stays conditional when external sharing is excluded;
do not enforce it against internal use in Gherkin or YAML merely to populate an
evaluation table. Retain the original criterion, trigger, threshold, and scope
status, with the future workflow that must activate it. Check that the narrative,
scenarios, NFR table, and evaluation file all express the same applicability.

Walk the **same ten areas the gates review** — Performance · Security · Privacy · Reliability · Observability · Accessibility · Data quality · Compliance · Cost · Supportability — into the `nfrs.md` table from `references/feature-template.md`. Most features need constraints in three to five of them; walk all ten and record "not applicable" silently for the rest rather than skipping the walk. (Scalability concerns land under Performance or Reliability.) These are `aipos-feature-refine` Step 7's and `aipos-feature-readiness` dimension 7's exact categories — a gap you leave here is a finding there.

In GenAI mode also capture: latency constraints, token cost expectations, model and vendor constraints, observability requirements, and evaluation cadence.

Before presenting the assembled package, reconcile the final NFR table against
all ten categories. Keep an applicable row, an explicit not-applicable entry,
or an unresolved gap for each; an earlier draft's row does not count if it was
dropped from the final artifact. Do not claim “ten areas covered” without that check.

Every NFR row carries an **owner** — the person or role who will produce its evidence. The gates score on it, and an unowned NFR is never measured.

An NFR without a threshold is a wish. If the PM doesn't have the number, write the requirement with the threshold marked as an open gap rather than inventing one — `aipos-feature-readiness` blocks on unmeasurable NFRs, and a gap it can see beats a number it can't trust.

### Step F9 — Definition of Done

Generate the checklist from `references/feature-template.md`, including the conditional items: security checks (if applicable), performance checks (if applicable), GenAI evaluation thresholds met (GenAI mode), documentation updated.

### Step F10 — Privacy impact

Ask: *does this feature process personal or sensitive data?*

If yes, draft the mitigation text and add `@nfr-privacy` coverage to the Gherkin. If a privacy scenario is missing, add it — this is one of `aipos-feature-readiness`'s named blockers.

### Step F11 — Overlap check

Compare against sibling features under the same epic, when you can see them. Flag and resolve overlap the same way Epic mode does.

### Step F12 — Summary and write

Summarize: feature name · primary story · secondary stories · description · business rules · Gherkin · NFRs · DoD · privacy · GenAI evaluation notes (including the `multi_agent` answer) · size assessment.

Then ask what to write, and where:

> Which of these should I write, and where — the repo package, the tracker record, or both? You can say "all" or list specific sections.

Write **only** what is explicitly approved, following `references/tracker-adapters.md`. Close by naming the next step: this is Draft 0, and `aipos-feature-refine` reviews it.

---

## Output format

Epic mode delivers:

````markdown
# Story Map — <epic name>

## Primary persona
## Workflow backbone
1. <activity> → 2. <activity> → …

## Slices
| Slice | Outcome delivered | Backbone stages spanned | Success metric |

## Feature candidates
| # | Name | Owns (scope boundary) | Slice |

## Integrity checks
- Overlap: <finding, or None>
- Vertical-only: <finding, or None>

## Defaults
Release · Type · Owner

## Stub preview
| Name | Epic | Release | Type | Owner | Description |
|---|---|---|---|---|---|

<destination and tool availability; the one outstanding whole-set decision, if any>
````

Feature mode delivers the feature package from `references/feature-template.md`: `feature_source.md` (stories, description, DoD, privacy), `acceptance.feature`, `nfrs.md`, and in GenAI mode `eval_criteria.yaml`.

## Guardrails

Do not:

- Create or modify any record without the explicit, destination-named confirmation — a bare "proceed" never covers a write
- Create multiple features without confirming the whole set in one preview first
- Invent personas, success metrics, evidence, quotes, thresholds, or evaluation numbers
- Invent business rules, or put a scenario no stated rule explains into `acceptance.feature`, even with a warning
- Write a scenario that depends on another scenario having run first
- Present a derived example as a confirmed requirement, or an unresolved placeholder as ready for execution
- Switch on GenAI mode because a coding agent is building the feature
- Set `multi_agent` without the PM's explicit yes/no answer
- Put acceptance criteria, NFRs, or DoD on a stub
- Present Draft 0 as reviewed, approved, or token-ready
- Ask the PM to choose Gherkin tags that can be derived
- Emit any delivery-phase tag other than `@mvp`, `@v1`, `@v2` — the vocabulary is closed, and `aipos-feature-slice` and `aipos-feature-map` discard anything else without an error
- Emit Gherkin that fails the validation checks in `references/gherkin-tagging.md`
- Ask more than one primary question at a time
- Overwrite an existing field without showing what is being replaced

Always:

- Say which mode you detected, in one line, and move on
- Ground the backbone in a real user journey, not in system architecture
- Give every feature candidate a one-line scope boundary
- Run the overlap and vertical-only checks before proposing creation
- Mark gaps as gaps — an open question is a legitimate output
- Show the full Gherkin with a tag coverage summary
- Name the next skill in the chain when handing off

## Related

| Skill | Owns | Relationship |
|---|---|---|
| `aipos-rapid-validation` | Experiments and commitment preparation | Supplies evidence for progressive behavior authoring during P2 and receives selected, reviewed behavior for the commitment package. An epic or prior go decision is not required to draft specifications |
| `aipos-epic-create` | The epic itself | Runs immediately before. Its field names are this skill's `epic:` input contract, and its personas and evaluation criteria are what Epic mode inherits — read its `epics/<key>/epic.md` rather than asking the PM to restate it |
| `aipos-feature-refine` | Spec quality and the 3 Amigos review | Consumes this skill's Draft 0. This skill creates; refine judges. Never self-review here |
| `aipos-feature-slice` | Per-scenario sizing and re-slicing | Owns the `@mvp`/`@v1`/`@v2` vocabulary. This skill assigns the delivery tag from the feature's confirmed slice; slice re-decides it per scenario with the Complexity Matrix |
| `aipos-feature-readiness` | The repo-side Development Token gate | Its blocker list is what this skill writes toward — missing thresholds, absent privacy paths, and missing eval criteria are its named blockers |
| `aipos-feature-map` | The corpus view | Reads the feature packages this skill writes, via the same `features/<key>/` layout |
