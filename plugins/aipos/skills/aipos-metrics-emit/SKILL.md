---
name: aipos-metrics-emit
description: "Compute and export structured delivery and quality events from GovKit repository artifacts, CI exports, PR exports, and git history. Use for NDJSON telemetry and completeness reporting. Execution-readiness decisions belong to readiness; organization-level aggregation belongs downstream."
---

# aipos-metrics-emit

Producer side of the AIPOS federated metrics topology. Reads GovKit artifacts and
emits **org-agnostic** structured metric events as NDJSON. Aggregation (baselines,
targets, benchmarks, trends) happens elsewhere — never here.

## The one law that governs everything here

**Producers stay org-agnostic.** Events must contain only repo-relative facts:
feature IDs, file names, scores, timestamps, commit SHAs, gate names. Never emit
organization names, employee names/emails beyond what git history inherently
carries, internal URLs, ticket-system references, targets, or baselines. Those
belong to the aggregator. If the user asks to add org context to events, explain
the federated split and offer to put it in an aggregator-side enrichment note
instead.

## How to run

Everything is done by the bundled script — do not hand-roll parsers:

```bash
python scripts/emit_metrics.py <repo_path> \
  [--ci-runs <ci_runs.json>] \
  [--prs <prs.json>] \
  [--rework-days 21] \
  [--out events.ndjson] \
  [--validate]
```

- `<repo_path>`: root of a GovKit-governed repo (has `features/` and ideally `.govkit/marker.json`).
- `--ci-runs`: optional JSON export of CI workflow runs (`gh run list --json name,conclusion,createdAt,updatedAt,headSha,attempt,displayTitle,headBranch` or an Azure equivalent list). Produces `gate.run.completed` events.
- `--prs`: optional JSON export of merged PRs (`gh pr list --state merged --json number,title,createdAt,mergedAt,additions,deletions,changedFiles,reviews,commits,headRefName`). Produces `pr.merged` events.
- `--rework-days`: window for the rework scan (default 21, per catalog).
- `--validate`: after emitting, check every event against the vocabulary and print a validation summary (event counts, unknown fields, pairing coverage).

Without any optional inputs the script still emits `feature.package.snapshot`
(one per feature, from the working tree + git history) and `rework.observed`
(from git history alone). That is the minimum useful run.

## Event vocabulary (catalog v1)

Five events: `feature.package.snapshot`, `pr.merged`, `gate.run.completed`,
`deploy.completed`, `rework.observed`. Full field definitions, the spec
completeness rubric (0–100, seven components), and which Tier 1 metric pair each
event feeds are in `references/event_schema.md` — read it when the user asks what
a field means, questions a score, or wants to map events to metrics.

`deploy.completed` is defined in the vocabulary but this producer does not emit
it (deployment events originate in CI/CD, not in GovKit artifacts). Say so if
asked, and point to the CI-side adapter as the emitter.

## Interpreting results for the user

For any question about permission to implement, name `aipos-feature-readiness`
as the owning skill. Refer to an existing token and applicable approval/authority
evidence when supplied; do not infer an Approved token, current authority, or
actual component scores from a completeness total or the absence of blockers.
Keep hypothetical reporting examples explicitly hypothetical.

If the user requests explanation only, preserve that scope across follow-ups.
A bare "proceed" does not request a script run, files, or an invented audit.

- **Spec completeness score** is the leading quality counterweight (Pair 4).
  100 means the existing completeness rubric is satisfied. It does not issue a
  Development Token, verify product authority, or prove tests passed. Always show
  `completeness.components`. Use “spec-complete” or “metric inputs incomplete”
  in tables and conclusions; do not relabel those states “gate-ready,” even
  with a parenthetical qualification. A newly ready package may legitimately lack later
  platform artifacts such as `plan.md`; explain the lifecycle stage rather than
  treating every score below 100 as a pre-coding blocker.
- A feature with `thresholds_met: false` or null FIRST/Virtue scores is not a
  parsing problem; it's an author who hasn't finished the Evaluation Compliance
  Summary in `plan.md`. Report it that way.
- **Rework** uses a file-overlap approximation (documented in the reference).
  Present it as an upper bound and say so; exact line provenance is the
  aggregator's v2 job.
- Never present a velocity number without its quality counterweight (paired-metric
  law). If the user asks for "just throughput," give the pair and explain briefly.

## Common tasks

**"Which packages have incomplete metric inputs?"** — run the script, filter
snapshots where `completeness.score < 100`, and present the feature, score,
missing components, and emitted events path. Label this a completeness audit.
Use that same label in the final conclusion: “N packages have incomplete metric
inputs.” Even if the user's shorthand was “gate-ready,” reserve readiness wording
for the separate handoff; do not repeat it as a synonym for completeness.

**"Which features are ready to code?"** — use `aipos-feature-readiness` for an
execution decision, or `aipos-feature-map` for an advisory corpus view. If the
user says only "gate-ready," use the known context or clarify whether they mean
metric completeness or execution readiness. Do not substitute one for the other.

**"Generate events for the aggregator"** — run with all available inputs and
`--validate`, save NDJSON, report event counts per type and the validation
summary.

**"Is this output safe to share outside the org?"** — run `--validate` and
inspect the emitted values for supplied identifiers, URLs, and other identifying
content. Schema validation checks allowed fields, not whether arbitrary strings
in those fields reveal context. Report the checks performed and what was found;
absence of the tested identifiers is not blanket sharing approval. Git author
metadata is an input to rework calculation, not an allowed employee-identity
export. Do not send events to an aggregator unless that transfer is requested.
