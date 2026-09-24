# AIPOS

Thirteen focused skills supporting product strategy, Continuous Discovery (P1), Rapid Validation (P2),
and Accelerated Development (P3) in one installation: `aipos@aipos`.

## Skill catalog

Pillars describe lifecycle use. They do not create separate copies of a skill.

| Skill | Use it for | Main boundary |
|---|---|---|
| [aipos-product-strategy](skills/aipos-product-strategy/SKILL.md) | Product vision and strategy: start, assess, or revise one Product Opportunity Brief | Graph optional; delegates experiments and initiative canvases; does not approve production scope |
| [aipos-quarterly-planning](skills/aipos-quarterly-planning/SKILL.md) | P1: evidence review, research gaps, exploration decision drafts | Requires live graph reads; does not record authoritative decisions |
| [aipos-solution-design](skills/aipos-solution-design/SKILL.md) | P2: a one-page Solution Design canvas, live in a workshop or with a PM, rendered as an image | Facts from the graph, decisions from the PM; recommends to a named owner, never decides |
| [aipos-rapid-validation](skills/aipos-rapid-validation/SKILL.md) | P2: experiments, evidence, viability briefs, commitment preparation | Delegates canonical behavior authoring; prepares rather than grants approval |
| [aipos-epic-create](skills/aipos-epic-create/SKILL.md) | Optional P2/P3 support: an explicitly requested epic or initiative | An epic is not a prerequisite for feature work |
| [aipos-feature-create](skills/aipos-feature-create/SKILL.md) | P2: new Rules, scenarios, and packages; P3: faithful baseline materialization | Draft 0 needs review; does not implement application code |
| [aipos-feature-refine](skills/aipos-feature-refine/SKILL.md) | P2 and change review: existing specs, 3 Amigos, ambiguity, evidence gaps | Recommends readiness; committed behavior changes require reapproval |
| [aipos-workflow-map](skills/aipos-workflow-map/SKILL.md) | P2 and maintenance: journey source, actors, branches, handoffs | References canonical behavior; delegates rendering |
| [aipos-feature-slice](skills/aipos-feature-slice/SKILL.md) | P2 and release changes: smallest shippable selection, prerequisites | Scope recommendation; optional complexity scores are not delivery forecasts |
| [aipos-feature-map](skills/aipos-feature-map/SKILL.md) | P2/P3: corpus views, dependencies, advisory assessment orchestration | Uses the owning assessment skill; does not issue tokens |
| [aipos-feature-readiness](skills/aipos-feature-readiness/SKILL.md) | P3: reviewed repo package, verification paths, Development Token | Local readiness is distinct from product approval and passing tests |
| [aipos-synthetic-data](skills/aipos-synthetic-data/SKILL.md) | Delivery support: seeded generators, scenario or schema-derived datasets | Does not mask production data or invent constraints |
| [aipos-metrics-emit](skills/aipos-metrics-emit/SKILL.md) | Delivery observation: structured events and completeness diagnostics | Completeness is distinct from authorization; aggregation is downstream |

## Prerequisites

- A host supporting Claude plugins; see the [installation guide](../../README.md#install).
- Product strategy can start with an idea, supplied research, or an existing brief;
  no graph, tracker, customers, measurements, or backlog is required. It owns the
  connection between product results and strategy revision, not analytics execution.
- Quarterly planning requires a live Product Definition Graph read connection.
  Equivalent MCP reads can provide opportunities, problems, lineage, evidence,
  linked work, and evidence text. Without it the skill reports what is missing.
- Solution design reads the same graph when it is connected and falls back to the PM's
  account when it is not (the canvas says so, and Proceed stays unavailable). Its verifier
  and renderer use the standard library; PDF and PNG output need a headless Chrome or
  Chromium (HTML is always produced). A mock read server with synthetic data lives in
  `evals/mock_pdg/` for development and evaluation.
- Validation can start with pasted evidence or a hunch. A P1 mandate is optional;
  when present its owner, budget, and horizon carry through the work.
- Tracker connectors are needed only for tracker reads or explicitly requested
  writes. Repository and pasted-input routes remain available.
- Use Python 3.11+ for bundled scripts. Install the requirements belonging to the
  script you run: [feature-map](skills/aipos-feature-map/scripts/requirements.txt)
  requires the Cucumber parser; [metrics](skills/aipos-metrics-emit/scripts/requirements.txt)
  requires PyYAML; [synthetic-data](skills/aipos-synthetic-data/scripts/requirements.txt)
  requires Faker. Readiness, change-package, and sizing scripts use the standard
  library. Model evaluation tooling has separate development dependencies.

## Workflow and contracts

The [workflow guide](../../docs/workflow.md) shows entry points and handoffs.
Shared Gherkin authoring, behavior identifiers, and workflow source guidance live
once in [references](references/). Skills keep their own rubrics and procedures.

The existing `.govkit/` paths, token record fields, event vocabulary, feature
package layouts, and scoring scales remain stable. `aipos-*` names identify the
skills; GovKit still names the delivery contracts those skills use.

Skills preserve evidence provenance, expose missing information, and follow their
specific write-back protocols. Refinement's 10 dimensions review draft quality;
readiness's 12 assess execution preparation. A draft stored in a repository is
still a draft. Map assessments are advisory and do not issue token records.

A project with a decision service must preserve the exact approved behavior and
check applicable authority. A project without one retains local readiness and
makes no claim of external approval. These skills do not write application code.
