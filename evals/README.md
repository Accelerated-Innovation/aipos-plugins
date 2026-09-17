# Running the model-graded evals

Every skill ships `evals/evals.json`: cases with a prompt, optional attached files, and an
`expected_output` written as concrete checkable claims. **This directory is what executes them.**

Before it existed, 29 cases across 6 skills were graded by nothing. That mattered more here than
it would in most repos, because this repo's product *is* coaching behaviour encoded in `SKILL.md`
prose — and the deterministic suite cannot test it by design. From
[CONTRIBUTING](../CONTRIBUTING.md): *"a test that matched a heading or a phrase in a `SKILL.md`
would pass while the tool silently broke."*

## Running one

```bash
python -m pip install -r requirements-evals.txt

python evals/run_evals.py --list                                    # skills with cases
python evals/run_evals.py --skill govkit-feature-create             # dry run, free
python evals/run_evals.py --skill govkit-feature-create --execute   # real calls, real money
python evals/run_evals.py --skill govkit-feature-refine --case 9 --execute   # one case
```

**`--execute` is required to spend anything.** Without it the runner assembles every request,
prints the first one, and calls nothing — which is enough to check the wiring after changing a
skill.

Credentials resolve the usual way: `ANTHROPIC_API_KEY`, or `ANTHROPIC_AUTH_TOKEN`, or an
`ant auth login` profile. You do not need to pass a key.

## How a case is graded

1. **Subject call** — the skill's `SKILL.md` becomes the system prompt, the case's `files` are
   attached, the case's `prompt` is the user turn. What comes back is what the skill would say.
2. **Judge call** — a second model reads the prompt, the response and the `expected_output`
   rubric, and returns a structured verdict: `passed`, `score`, `met`, `missed`, `reasoning`.

Structured outputs, not "reply with only JSON" — free-text JSON fails on unescaped quotes in
reasoning often enough to matter.

**The judge defaults to a different model than the subject** (`claude-sonnet-5` judging
`claude-opus-5`), and the runner refuses `--execute` when the two match. A model grading its own
output agrees with itself more than it should. Override either with `--model` / `--judge-model`;
the judge is a real cost/quality tradeoff and belongs to whoever is paying.

## What a passing run does and does not prove

It proves the skill produced the behaviour the rubric describes, **once, under that model at that
effort**. That is evidence, not proof:

- A model-graded verdict is a judgement, and a judge can be wrong in the same direction as the
  subject.
- One run is one sample. `--reps 3` gives a sense of variance; a case that passes two runs in
  three is telling you something.
- The rubric is only as good as its author. A case that passes a rubric which measures the wrong
  thing has measured the wrong thing.

**Read the traces.** Every case writes its full exchange to
`.claude/hillclimb/<skill>/<variant>/traces/`. A score you have not looked behind is a number,
not evidence.

## Output

Under `.claude/hillclimb/<skill>/<variant>/` — gitignored, so runs never land in a commit:

| File | Holds |
|---|---|
| `results.jsonl` | one row per case: grade, `passed`, `missed`, latency, `model`, `usage`, `judge_model`, `judge_usage`, retries |
| `traces/<case>_rep<k>.json` | the full exchange — system prompt, attachments, response, rubric, verdict |
| `errors.jsonl` | attempts that failed *before* producing a gradeable answer, with a failure class |

`errors.jsonl` is deliberately separate. A plumbing failure written into `results.jsonl` would
occupy that case's slot, so a resume would skip it forever and a timeout would be scored as a
model failure.

Rows are appended and flushed as each case finishes, and a resume is keyed on `(case, rep)` — a
crash mid-run costs only the cases still in flight.

## Reporting a run

Per CONTRIBUTING: **never report an eval as passing unless it actually ran.** When you run one,
say which cases ran, the subject and judge models, and the results. `results.jsonl` carries
`model` and `usage` per row (including the judge's) so spend can be worked out afterwards; the
runner deliberately does not compute cost, so a model swap cannot carry a stale rate.

## Why this is not a required PR check

The merge gate stays `claude plugin validate` + `pytest tests -q`: offline, key-free, fast.

An LLM-judged gate is non-deterministic. A required check that fails occasionally for no reason
trains people to re-run until green — and `govkit-feature-refine` already says why that is
corrosive: *"false gates teach teams to ignore real ones."* A secrets-dependent check also cannot
run on fork PRs at all.

So the eval job is `workflow_dispatch` — run it deliberately, and paste the result into the PR
when a change touches coaching behaviour.
