# Product strategy entry point — 1.2.0 candidate

Date: 2026-09-24. Base: `979599f9079b76bec3ba1798affea2de0ccef556` (1.1.0).
Status: implemented and locally checked; proposed for a 1.2.0 limited release.
Not released or installed.

## Design and scope

`aipos-product-strategy` owns a concise Product Opportunity Brief for starting,
assessing, and revising commercial or internal product strategy. It works with
an idea, supplied evidence, or a current brief without requiring a graph,
tracker, customer base, measurements, or backlog. It maintains one canonical
brief with revision/section references and distinguishes evidence, reports,
inferences, assumptions, proposals, and adopted choices.

The skill delegates experiments and findings, initiative canvases, portfolio
research allocation, and optional epics to their current owners. It receives
research and product results for strategy revision; it does not implement
analytics or full roadmapping. One initial measurable outcome can suffice.
Unknown baselines can motivate learning. Strategy agreement, learning authority,
investment evidence, and production-scope approval are separate states.

The [source note](../../plugins/aipos/skills/aipos-product-strategy/references/sources.md)
attributes Pichler's and Cagan's principles and distinguishes the AIPOS synthesis.
Shared framing/metrics references are reused with explicit product-strategy
adaptations. The [shared handoff](../../plugins/aipos/references/strategy-handoff.md)
is consumed by all five relevant skills; downstream strategy copies are avoided.

Integration updates the catalog, workflow, entry examples, rollout instructions,
related skills, and both manifests to 1.2.0 / thirteen skills. Historical release
and evaluation records remain unchanged. The existing untracked `.python-version`
is preserved. No application code, canvas verifier, decision service, installed
plugin, or production system is changed.

## Evaluation coverage

Twelve new behavioral cases cover an idea-only commercial product, an internal
product, solution-shaped intake, mixed evidence, competing segments, contradictory
results, a missing baseline, premature build approval, assessment without rewrite,
canvas source compatibility, a named experiment, and an authored follow-up that
leaves choices open. Three bundled fixtures provide mixed research and a strategy
with contradictory pilot results. Thirteen new routing cases include contrasts
with canvas, experiment, epic, and graph planning owners, plus four held-out cases.

## Verification

| Check | Result |
|---|---|
| Offline suite | 567 passed, 5 skipped; skips are existing skills without fixture directories |
| Marketplace and plugin | Both `claude plugin validate` checks passed |
| Skill structure | Skill-creator `quick_validate.py` passed |
| Routing dry run | 13 skills, 72 cases discovered; no model calls |
| Behavioral dry run | All 12 new cases assembled, plus all cases of the four handoff skills; no model calls |
| Independent native routing smoke | All 13 new cases matched expected routes, one selection each, including four held-out cases |
| Independent native behavior smoke | Two responses inspected: idea-only brief/build-authority distinction; canonical strategy revision after contradictory results |
| Anthropic routing | One bounded attempt failed authentication before a completed model call; zero completions, no pass claimed |
| Anthropic behavioral evaluation | Not executed because Anthropic authentication is unavailable |
| Native installation / connected graph and tracker workflows | Not run; no installation or external writes requested |

The [smoke evidence](../evaluations/2026-09-24-product-strategy-smoke.json) retains
source hashes, raw routing inputs/selections, behavioral prompts/responses, and
observations. Native smoke checks are not the repository's independent
subject/judge evaluation, a repeated comparison, or a full-catalog regression run.
No coaching change was made in response to held-out route results.

When credentials are available, run the repository routing harness against all
72 cases with its explicit call cap and repeat count, and the new skill's full
behavioral suite with different subject and judge models. Review traces and
report missing/failed results separately; dry-run assembly does not prove behavior.

## Limited-release scope decision

Keep the skill as implemented. Address the integration gaps below during a
limited release or in subsequent updates; they do not block using the skill to
create, assess, or revise a Product Opportunity Brief. Existing evidence,
baseline, and approval boundaries remain in force at downstream handoffs.

During the limited release, exercise an idea-only start, an existing-strategy
assessment, and a revision after new findings. Capture where users get stuck,
which handoffs work, and which require manual support. Prioritize the integration
follow-ups from those observations. An unavailable graph-backed baseline still
blocks canvas Proceed under the existing rules.

Use the limited release to complete native installation and connected-workflow
checks. Run the full routing and behavioral evaluations when credentials are
available, and review those results before deciding on broader rollout. The
current local and native smoke results support a pilot; they do not establish
full evaluation coverage or end-to-end integration readiness.

This scope decision does not change the publication or installation status above.

## Remaining integration gaps

1. **Canvas decision language.** The pre-experiment canvas maps Proceed/Pivot/Park
   to the viability brief's GO/REVISE/NO-GO. This addition carries decision type,
   timing, and authority explicitly rather than changing that mapping. Follow-up:
   clarify experiment recommendations versus production-investment recommendations
   in both contracts and their evaluations, preserving existing approval authority.
2. **Graph baseline access.** Attributable supplied research can inform the product
   brief, but a no-graph canvas and a `[T]` baseline still cannot unlock Proceed.
   Follow-up: inspect the ReOps-to-graph evidence-text/measurement adapter and test
   the route from an actual study finding to a readable, graph-backed baseline.
   Do not merely relabel supplied evidence to bypass the verifier.
3. **First-evidence intake.** The skill names the recording handoff, preserving
   source IDs and reporting unknown destinations. The owning system must execute
   ingestion; saving a brief or findings locally does not create graph evidence.

These follow-ups are bounded integration work. Canvas approval/baseline rules,
production behavior ownership, and readiness authority are unchanged here.
