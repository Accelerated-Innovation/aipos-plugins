# Routing cases

These cases test selection from the complete skill catalog before any skill body
is loaded. They complement the coaching cases under each skill's `evals/`.

`cases.json` records the prompt, available context, allowed primary action and
ordered handoffs (including required internal assessment delegates), whether a mistake crosses a critical boundary, and the case's
development or held-out split. `none` means the request is outside AIPOS;
`clarify` means missing context prevents a useful choice. A correct selection
does not prove that the selected skill executes correctly.

Descriptions come from actual `SKILL.md` frontmatter. Do not copy them here.
Keep held-out paraphrases out of description tuning. Read the
[ownership model](../../docs/workflow.md#ownership-and-handoffs)
when adding cases; one requested action should have one owner, with explicit
handoffs when the requested result needs more than one skill.

## Run and compare

Install `requirements-dev.txt` for YAML parsing and `requirements-evals.txt` for
live calls. Dry runs need no API credentials:

```bash
python evals/run_routing.py
python evals/run_routing.py --snapshot-out .claude/routing/baseline/inputs.json
python evals/run_routing.py --execute --model <model-id> --reps 3 --max-calls 141
python evals/run_routing.py --split heldout --execute --model <model-id> --max-calls 18
```

Live runs require both a chosen model and a hard call cap. The runner makes no
automatic retries and stops on the first API or malformed-result error. A call
cap is not a dollar limit; choose it and the output-token cap within the run
budget. Token usage is retained per result and raw response, including errors.

To measure the unchanged baseline after edits, use `--snapshot-in` with the
captured input file and a separate `--out` directory. Snapshots are run evidence,
not a second maintained skill catalog. Compare the same case IDs and model;
use the plan's rename map when comparing old and new primary skill identities.
Never rewrite historical traces or pass them off as results for current names.

Results and full requests/responses are saved under `.claude/routing/current/`
by default. Resume only reuses matching catalog, case, model, output budget,
repetition count, and evaluator contract fingerprints. Invalid or incomplete
responses remain errors, not successes. Skipping calls at the cap leaves missing
results in the denominator. Every critical case must pass in every repetition,
with at least 90% correct overall, before the selected run is accepted.

The subject sees only names, descriptions, and user context. Allowed outcomes
are compared directly; no model is asked to grade its own selection. Native
client selection and downstream behavior still need their own checks.
