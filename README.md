# AIPOS skills

One plugin for evidence-based discovery, rapid validation, and governed AI-assisted
delivery, from [Accelerated Innovation](https://acceleratedinnovation.com).

AIPOS (AI Product Operating System) groups the work into pillars. The plugin keeps
all eleven skills together because behavior authoring, review, journey definition,
and scope selection support several pillars. Each skill owns a specific action
and hands off when the requested work changes.

## Install

In a terminal with Claude Code installed:

```bash
claude plugin marketplace add Accelerated-Innovation/aipos-plugins
claude plugin install aipos@aipos
```

The marketplace and plugin are both named `aipos`, in the `aipos-plugins`
repository (renamed from `govkit-plugins`; the old URL redirects). Start a new
Claude Code session after installation. For an early
installation of `aipos-p1`, `aipos-p2`, or `govkit`, follow the short
[replacement instructions](docs/rollout.md).

This repository uses Claude's `.claude-plugin` packaging. It does not currently
provide a Codex plugin manifest.

## Start with the work you need

Describe the action and provide the relevant evidence or artifacts:

| Request | Skill |
|---|---|
| “Review the live opportunity graph for next quarter's research choices.” | `aipos-quarterly-planning` |
| “Design a demand test for this opportunity.” | `aipos-rapid-validation` |
| “Draft acceptance criteria from these findings.” | `aipos-feature-create` |
| “Review these existing criteria with Product, QA, and Engineering.” | `aipos-feature-refine` |
| “Select the smallest useful release from these scenarios.” | `aipos-feature-slice` |
| “Check this reviewed repo package before implementation.” | `aipos-feature-readiness` |

See the [complete skill catalog and prerequisites](plugins/aipos/README.md) for
journey authoring, dashboards, optional epics, synthetic data, and metrics.

## How the pillars connect

P1 reviews live evidence and drafts exploration decisions. P2 tests assumptions
and progressively defines, reviews, and selects behavior for a commitment package.
The accountable authority decides whether to approve that exact scope. P3 checks
the reviewed repository package for execution readiness, then supports test data
and delivery observation.

An evidence-backed opportunity can go directly to Rules and scenarios. Epics,
user stories, estimates, and a decision service are optional. Existing work can
enter at the appropriate stage; this is not a compulsory sequence of eleven calls.

The [workflow guide](docs/workflow.md) explains ownership, handoffs, and examples.
Product approval, local execution readiness, current authority, and implementation
evidence remain distinct. A dashboard badge or completeness score grants none of
those by itself.

## Develop and verify

Read [CONTRIBUTING.md](CONTRIBUTING.md). Offline tests validate packaging and the
bundled scripts. [Routing evaluations](evals/routing/README.md) test selection from
the descriptions; [behavior evaluations](evals/README.md) test a loaded skill's
coaching. Model results must be reported separately from offline test passes.

The [implementation plan](docs/plans/2026-09-19-aipos-plugin-consolidation.md)
records the consolidation work and outstanding release checks.

Licensed under [MIT](LICENSE).
