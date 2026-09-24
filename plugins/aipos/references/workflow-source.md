# Workflow source (`workflow.json`)

> **Shared reference.** Read by `aipos-map-render` and by any Pillar 2 skill that
> authors or renders a workflow. From a skill folder: `../../references/workflow-source.md`.
> Companion to [`spec-identifiers.md`](spec-identifiers.md) and
> [`gherkin-authoring-standard.md`](gherkin-authoring-standard.md).

## What this file is for

A workflow says **how a customer outcome is reached**: the activities in order, who acts at
each, where work changes hands, and which Rules govern what happens.

It holds **no behavior of its own**. Every behavioral claim in it is a *reference* into the
canonical Gherkin. That is the entire design: a Rule that applies at four steps is authored
once and referenced four times, so rewording it cannot leave three stale copies behind in a
diagram nobody remembered to update.

The diagram is a **generated projection** of this file. Nobody maintains a second picture by
hand, and this repository builds no diagram editor.

## Three levels, one definition

L1, L2 and L3 are **views of the same file**, not three files:

| View | Answers | Contains |
|---|---|---|
| **L1** | What does the customer go through? | Outcome, actors, activities, order and branches |
| **L2** | Who and what collaborates at each step? | The above plus steps, actor kinds, and handoffs |
| **L3** | Which behavior governs it? | The above plus resolved Rules, scenarios and design references |

L1 deliberately contains no Gherkin. It is the view someone outside the team reads, and a rule
slug leaking into it is the failure mode.

**These are not the other two L-vocabularies.** Workflow detail L1/L2/L3 is not GovKit adoption
L3/L4/L5 (how much governance payload a project installs) and not MVP/V1/V2 (a release view).
Where a document uses more than one, it says which.

## Shape

```jsonc
{
  "version": 1,
  "workflow_key": "invoice-approval",
  "source_key": "acme",                  // which repository this workflow's local refs mean
  "outcome": "A submitted invoice reaches a decision the finance team can stand behind.",

  "actors": [
    { "id": "submitter",       "name": "Invoice submitter", "kind": "human" },
    { "id": "routing",         "name": "Routing service",   "kind": "system" },
    { "id": "retrieval-agent", "name": "Evidence agent",    "kind": "agent" }
  ],

  "activities": [
    {
      "id": "route",                       // unique; what a baseline and a map both point at
      "name": "Route for approval",
      "actor": "routing",

      "next": [                            // workflow ORDER — see the warning below
        { "to": "approve",         "condition": "standard invoice" },
        { "to": "partner-approve", "condition": "partner invoice" }
      ],

      "behavior": [                        // qualified refs into canonical Gherkin
        "acme/FEATURE-inv_full#rule:invoice-approval-threshold",
        "acme/FEATURE-inv_full#scenario:approval-routing-by-amount"
      ],
      "design": ["acme/FEATURE-inv_full#design:approval-panel"],

      "steps": [                           // L2: collaboration inside the activity
        {
          "id": "evaluate-threshold",
          "name": "Evaluate the approval threshold",
          "actor": "routing",
          "kind": "system",                // human | system | agent | tool
          "handoff": { "from": "submitter", "to": "routing" },
          "behavior": ["acme/FEATURE-inv_full#rule:invoice-approval-threshold"]
        }
      ]
    }
  ]
}
```

`version` is an integer. An unsupported version is a **named error** that short-circuits — a
newer workflow is newer, not malformed, and reporting field errors against a shape you do not
understand is confidently wrong.

`source_key` names the repository this workflow's own references belong to. It is what lets a
resolver tell a local reference from a cross-repository one; see *Cross-repository references*
below.

## Order is not scope, and not a build dependency

`next` is the order a **customer** moves through the journey. Three separate things are
routinely confused here, and conflating them is how a workflow diagram quietly becomes a
project plan:

| Vocabulary | Lives in | Means |
|---|---|---|
| Workflow order | `next` in this file | The sequence and branches a customer experiences |
| Release scope | `@mvp` / `@v1` / `@v2` tags on scenarios | A planning *view* over selected behavior |
| Implementation dependency | Not modelled here | What must be built before what |

An activity late in a journey can ship first. A scenario tagged `@v2` can sit on an activity
tagged nothing at all. Neither fact belongs in `next`.

## References

```
<source-key>/<feature-key>#<kind>:<slug>
```

`kind` ∈ `rule` · `scenario` · `design` · `nfr` · `evaluation` · `agent-authority`.

- **`source-key`** names the repository or package, so behavior spanning applications resolves.
- **`feature-key`** is `features.json`'s `key` — the identity the ingestion contract already
  guarantees is unique.
- **`slug`** is the authored `@rule:` / `@scenario:` tag. See
  [`spec-identifiers.md`](spec-identifiers.md).

The feature-key segment is not decoration. Two features may legitimately carry the same local
slug — uniqueness is only required *within* a file — so an unqualified `#rule:invoice-approval-threshold`
cannot say which one it means, and the resolver refuses it rather than guessing.

`rule` and `scenario` references resolve against the Gherkin corpus. The other kinds —
`design`, `nfr`, `evaluation`, `agent-authority` — live outside it, so their feature need not
appear in the corpus at all. They are carried through **marked unresolved**: recording that
something was declared is honest, and inventing a target the resolver cannot see is not.

### Cross-repository references

Feature keys are unique *within a corpus*, not globally. Two repositories can both hold a
`FEATURE-inv_full` describing entirely different products.

So a reference whose `source-key` is not this workflow's `source_key` is **carried through
unresolved**, with a `foreign-source` warning — never bound to a local feature that happens to
share a key. Binding it would produce the worst outcome available: a confident `resolved: true`
pointing at behavior from a different repository.

It is a **warning**, not an error. Behavior spanning applications is legitimate; this corpus is
simply not where that half of it resolves.

## Diagnostics

Every diagnostic names the workflow element and, where one exists, the feature file — a finding
a reader cannot locate is a rumour.

| Code | Level | Means |
|---|---|---|
| `unsupported-version` | error | Newer than this build understands; short-circuits |
| `malformed-ref` | error | Not a qualified reference |
| `dangling-ref` | error | Names a feature or slug that does not exist |
| `unparsed-feature` | error | The slug is absent **and** that feature has Gherkin that does not parse — it may be in the file that failed |
| `foreign-source` | **warning** | Names another repository; carried through unresolved |
| `ambiguous-ref` | error | The slug occurs more than once in that feature |
| `duplicate-feature-key` | error | Two features claim one key |
| `duplicate-slug` | error | Two elements in one feature share a slug |
| `duplicate-activity-id` / `duplicate-step-id` | error | Ids must be unique; they are what others point at |
| `unknown-actor` | error | An activity, step, or **handoff endpoint** names an undeclared actor |
| `dangling-transition` | error | `next` points at no activity in this workflow |
| `derived-identity` | **warning** | Resolves, but through a name-derived id — see below |

**Broken Gherkin stays a parse error.** Reporting a reference into an unparsed spec as "not
found" would send someone to fix the reference instead of the spec, and reporting nothing at
all would let a broken spec pass as an empty one.

The scope of that is deliberately narrow. `repo_ingest` merges every `.feature` in a directory
into one record, so one unparseable sibling must **not** suppress rules that ingested perfectly
well from another file — that reports N symptoms and hides the behavior the reader came for.
A reference that resolves, resolves; the parse failure is reported on its own, and it still
fails the run.

**A derived identity warns rather than fails.** It resolves, so the map still renders — but a
slug derived from an element's name changes when the name does, so it cannot bind an approval.
Readable is not the same as approvable.

## Identifier lifecycle

A retired, split or merged identifier is **never reused**
([`spec-identifiers.md`](spec-identifiers.md)), so a reference to one **dangles**. That is the
intended outcome, not a gap:

- **Retired** — the behavior is gone. There is nothing to point at.
- **Split** — one child keeps the original slug and resolves; if neither child is recognisably
  the original, both are new and the old reference dangles.
- **Merged** — the survivor keeps one slug; references to the other dangle.

Auto-following a retired slug to "whatever replaced it" would silently repoint an approved
reference at behavior nobody approved. Repointing is a decision about where the behavior now
lives, made by a person. Failing loudly is what forces that decision to happen.

## Plugin boundaries

This reference and the resolver that reads it live in the **`aipos` plugin**, and a skill in
another plugin must not reach across for them.

Plugins install independently. A relative path that climbs out of one and into a sibling
resolves correctly in this source tree — where every plugin sits under `plugins/` — and breaks
the moment a user installs one without the other. There is no dependency mechanism that would
make the neighbour's presence a guarantee.

So: a skill that needs the workflow format lives in the plugin that owns it, or receives
already-resolved data. Copying the reference into a second plugin is not the alternative — a
copied reference is one nobody maintains. `tests/test_plugin_boundaries.py` enforces both.
