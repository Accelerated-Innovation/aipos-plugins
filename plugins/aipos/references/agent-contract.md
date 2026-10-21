# Agent contract — shared schema

> **Shared reference.** One copy, written by `aipos-agent-contract` and read by every skill that
> consumes an agent contract. From a skill folder the path is `../../references/agent-contract.md`;
> under an installed plugin it is also `${CLAUDE_PLUGIN_ROOT}/references/agent-contract.md`.
> Consumers cite this file; they do not restate it.

One contract per agent: what it takes in, what it can touch, what it produces, what it must never
do, when it hands control to a person, and where a person must approve before it continues.
`aipos-agent-contract` writes contracts in this shape. Skills that read them cite this file and
do not restate it:

| Consumer | Reads the contract for |
|---|---|
| Dialogue flows (step 8; `aipos-dialogue-flow` when installed) | Turns that call a tool, hit a guardrail, escalate or wait at a checkpoint |
| `aipos-feature-create` (GenAI mode, `eval_criteria.yaml`) | Eval cases that exercise each tool, guardrail and escalation trigger |
| AI risk review (`aipos-risk-review` when installed) | Side effects, confirmation status, personal-data inputs and open TBDs |
| `aipos-workflow-create` | The agent actor in `workflow.json` names its contract; the contract owns tools and limits, the workflow owns the journey |

A consumer that finds a `TBD` treats it as an open gap with that owner. It never fills the gap
itself, and never reads a TBD as permission.

## File

Markdown, one file per agent, named `<agent-id>.agent-contract.md` (default location
`docs/agents/`). It opens with a header block, then the six sections below **in this order and
with these exact headings**, so a checker and a reader find the same things in the same place.

```markdown
# Agent contract: <agent name>

- Agent ID: <stable id; the workflow.json actor id when there is one>
- Owner: <accountable human role>
- Status: draft | reviewed
- Revision: <n> (<YYYY-MM-DD>)

## 1. Inputs
## 2. Tools
## 3. Outputs
## 4. Guardrails
## 5. Escalation
## 6. Human checkpoints
```

## TBD — never invent

A fact or decision nobody has supplied is written as:

```
TBD — owner: <role or named person>; needed: <the decision or fact that closes it>
```

The owner is who can close it, not who noticed it. When the user has not said who that is, the
owner is the contract's Owner. A whole section the user cannot fill is one TBD line under its
heading; a single unknown cell is a TBD in that cell. An invented tool, side effect, escalation
path or approver is a defect — worse than a TBD, because it reads as decided.

## 1. Inputs

| Input | Source | Contains personal data | Notes |
|---|---|---|---|

`Contains personal data` is `yes`, `no` or a TBD.

## 2. Tools

| Tool | Purpose | Side effect | Human confirms | Notes |
|---|---|---|---|---|

- **Side effect** is one or more of `read`, `write`, `external send`, comma-separated.
  `write` changes state in a system the organization owns; `external send` reaches a person or
  system outside the agent's boundary (email, message, payment, API call to a third party). A
  tool whose effect is unknown is a TBD — never `read` by default.
- **Human confirms** is `yes — <role>` (a person approves each call before it takes effect),
  `no` (the call takes effect without a person), or a TBD. `no` on a `write` or
  `external send` is a decision someone made: say who in Notes. Never assume a send is safe.

## 3. Outputs

| Output | Recipient | Format | Notes |
|---|---|---|---|

## 4. Guardrails

| Rule | Kind | Enforced by |
|---|---|---|

`Kind` is `must never` or `must always`. `Enforced by` names the mechanism — tool permission,
policy check, validation, model instruction — or is a TBD. A rule enforced only by model
instruction says so; risk review weighs it differently.

## 5. Escalation

| Trigger | Goes to (human role) | Agent meanwhile | Notes |
|---|---|---|---|

Every row names a concrete trigger (an observable condition, not "when unsure") and the human
**role** it goes to. "Agent meanwhile" says whether it waits, stops, or continues with a safe
default. No decided path is a TBD — never a generic "escalate to a human".

## 6. Human checkpoints

| Checkpoint | Before | Approver (role) | What they approve |
|---|---|---|---|

A checkpoint is a planned approval in the normal path, unlike an escalation, which is an
exception. A tool marked `Human confirms: yes — <role>` has a matching checkpoint row.

## Completeness

A contract is **complete** when all six sections are present with content, every tool row has a
side effect and a confirmation status, every escalation row has a trigger and a human role, and
no TBD remains. A contract with TBDs is **incomplete**, not wrong: it is reviewable, and its TBDs
are the to-do list. `aipos-agent-contract` bundles `scripts/check_contract.py`, which checks
structure only — sections, required columns, allowed values, TBD owners, and the
confirm-to-checkpoint match. Whether the content is true stays with the reviewers.
