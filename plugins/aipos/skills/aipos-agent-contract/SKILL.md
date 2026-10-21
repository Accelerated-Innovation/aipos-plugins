---
name: aipos-agent-contract
description: "Write or review the contract for one AI agent: its inputs, tools with their side effects and human-confirmation status, outputs, guardrails, escalation triggers with the human role each goes to, and human checkpoints — with TBDs owned, never invented. Use when asked for an agent contract, or to define what an agent may do on its own, which actions need approval, and when it hands off to a person. Journey actors and handoffs belong to aipos-workflow-create; Gherkin scenarios and eval criteria to aipos-feature-create."
---

# AIPOS Agent Contract

Step 7 writes down, per agent, what it may touch and when it must stop. Dialogue flows (step 8),
eval cases (step 9) and the AI risk review all test against this contract, so a gap here becomes
a gap in each of them. The contract is a document for people to review, written in the shared
shape in `../../references/agent-contract.md` — read it before drafting; it is the schema this
skill fills and the checker enforces.

> "AI acts. Evidence informs. Humans govern." — AIPOS Canon

## Scope and handoffs

This skill owns one artifact: `<agent-id>.agent-contract.md`, one per agent.

- The journey — actors, steps, handoffs between people, systems and agents — belongs to
  `aipos-workflow-create`. An agent actor in `workflow.json` names its contract by agent ID;
  the contract does not redraw the journey.
- Gherkin scenarios and `eval_criteria.yaml` belong to `aipos-feature-create`, which reads the
  contract to cover each tool, guardrail and escalation trigger.
- Dialogue flows and the AI risk review read the contract as their input. When those skills
  are not installed, the contract is still what those reviews use.

The skill never decides the agent's authority. It records what the team decided, and makes
what nobody decided visible.

## Instructions

1. **Gather what is known.** Take the agent's name, its accountable owner (a role), and what the
   user supplies — notes, a workflow, a feature brief. Ask once, in one message, for the six
   areas the user has not covered: inputs, tools, outputs, guardrails, escalation, human
   checkpoints. If the user wants a draft now, draft now; do not hold the draft hostage to the
   questions.
2. **Classify every tool.** For each tool, record its side effect — `read`, `write` (changes state
   in an organization-owned system) or `external send` (reaches a person or system outside the
   agent's boundary: email, message, payment, third-party call) — and whether a person confirms
   each call. A send or a write is never assumed safe and never assumed confirmed. If the user
   has not said, the confirmation status is a TBD with an owner. An unknown effect is a TBD,
   never `read` by default.
3. **Make escalation concrete.** Each escalation names an observable trigger and the human role
   it goes to, plus what the agent does meanwhile. "Escalate to a human when unsure" is not a
   path: record what is missing as a TBD rather than accepting it or inventing a role.
4. **Pair checkpoints with confirmations.** Every tool marked `Human confirms: yes — <role>` has a
   checkpoint row naming that tool in `Before`.
5. **Write TBDs, never inventions.** Anything not supplied is
   `TBD — owner: <role>; needed: <what closes it>`. The owner is who can decide it — the
   contract's Owner when the user has not said. A whole unknown section is one TBD line. An
   invented tool, approver, threshold or escalation path is the worst defect a contract can
   have, because it reads as decided.
6. **Check it.** When the contract is written to a file, run
   `python3 scripts/check_contract.py <file>` (standard library only) and report its status:
   `complete`, `incomplete` (owned TBDs remain — list them as the to-do list), or `invalid`
   (structural errors — fix them first). When the contract stays in chat, apply the same rules
   by hand and say that the checker was not run. The checker validates structure; whether the
   content is true is for the reviewers.
7. **Hand off.** Close with who reads the contract next — dialogue flows, eval cases through
   `aipos-feature-create`, and the AI risk review — and the open TBDs each of them inherits.

## Output

Text in chat by default, in the shared shape. Write `<agent-id>.agent-contract.md` (default
`docs/agents/`) when the user asks for a file or names a repository location. No panel: the
contract is a document to review, not something to inspect visually.

## Examples

- "Write the agent contract for our quote-approval agent: tools, guardrails and escalation."
- "What may our claims-intake agent do on its own, and what needs a person to approve?"
- "Review this agent contract and tell me what's missing before risk review."

## Guardrails

- Never mark a `write` or `external send` as safe, read-only or unconfirmed unless the user said
  so; never invent who confirms it.
- Never invent an escalation path, trigger, approver role, threshold or tool.
- Never fill a TBD from general knowledge of what agents like this usually do.
- Never copy the schema into another file; cite `../../references/agent-contract.md`.
- Never describe the contract as approval to build or deploy the agent; it records authority,
  it does not grant it.
