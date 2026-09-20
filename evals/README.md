# Running the model-graded evals

Every skill ships `evals/evals.json`: cases with a prompt, optional attached files, and an
`expected_output` written as concrete checkable claims. **This directory is what executes them.**

Before it existed, 29 cases across 6 skills were graded by nothing. That mattered more here than
it would in most repos, because this repo's product *is* coaching behaviour encoded in `SKILL.md`
prose — and the deterministic suite cannot test it by design. From
[CONTRIBUTING](../CONTRIBUTING.md): *"a test that matched a heading or a phrase in a `SKILL.md`
would pass while the tool silently broke."*

## Running one

**Python 3.11+ is required** for live runs (`asyncio.timeout` and the Anthropic SDK).
The deterministic suite does not need the SDK and also supports older Python versions.

```bash
python -m pip install -r requirements-evals.txt

python evals/run_evals.py --list                                    # skills with cases
python evals/run_evals.py --skill aipos-feature-create             # dry run, free
python evals/run_evals.py --skill aipos-feature-create --execute   # real calls, real money
python evals/run_evals.py --skill aipos-feature-refine --case 9 --execute   # one case
```

**`--execute` is required to spend anything.** Without it the runner assembles every request,
prints the first one, and calls nothing — which is enough to check the wiring after changing a
skill.

Credentials resolve the usual way: `ANTHROPIC_API_KEY`, or `ANTHROPIC_AUTH_TOKEN`, or an
`ant auth login` profile. You do not need to pass a key.

## Conversation stages and output budgets

Cases can declare `follow_ups` and `evaluation_stage`:

```json
{
  "follow_ups": ["The primary user is an adjuster. Draft with unknown thresholds marked TBD."],
  "evaluation_stage": "Draft after persona confirmation, before any file or tracker write."
}
```

An empty reply list means one assistant turn. Each authored reply is sent verbatim
between assistant turns; the judge sees those role boundaries, the fixtures, and
the intended stage. All shipped cases declare their stage. An intake-only case
must not be graded as though it had completed a full interview.

Legacy cases without `follow_ups` retain two turns with a bare `proceed` by default.
`--turns` can change that legacy count; it cannot contradict a scripted case's
count. Invalid scripts fail before model calls. Replies and stage are fingerprinted,
so changing them cannot silently reuse a grade.

The default subject ceiling is 16,000 tokens. Set `--subject-max-tokens 32000`
and `--judge-max-tokens 32000` for longer packages; larger ceilings use streaming.
A truncated subject remains unaccepted even when its judge verdict is favorable.
Both budgets are recorded, and budget changes invalidate cached comparisons.

## How a case is graded

1. **Subject call** — the **whole skill package** becomes the system prompt: `SKILL.md` plus
   every reference its own text tells the subject to read. `aipos-feature-create` names six,
   and says of one that it *"is what the gates judge your Gherkin against"* — sending only
   `SKILL.md` would have the subject work from memory and the judge grade the memory. The
   case's `files` and `prompt` follow in the user turn.
2. **Judge call** — a second model reads the prompt, the response and the `expected_output`
   rubric, and returns a structured verdict: `passed`, `score`, `met`, `missed`, `reasoning`.

Structured outputs, not "reply with only JSON" — free-text JSON fails on unescaped quotes in
reasoning often enough to matter.

**The judge defaults to a different model than the subject** (`claude-sonnet-5` judging
`claude-opus-5`), and the runner refuses `--execute` when the two match. A model grading its own
output agrees with itself more than it should. Override either with `--model` / `--judge-model`;
the judge is a real cost/quality tradeoff and belongs to whoever is paying.

The system block is identical for every case in a skill, so it is cached: the first case pays
the write, the rest read it at a fraction of the price. That is why the dry run reports the
skill package and the per-case input separately — adding them together would overstate a
multi-case run several times over.

## Cases this harness cannot run

Some cases need inputs it cannot supply. The three original `aipos-metrics-emit` cases point at a
governed repository at `/tmp/testrepo` and expect tools to inspect it; this runner has neither.

The newer completeness-versus-token coaching case has self-contained inputs and can run.

For runtime metrics, build and exercise a real disposable git repository locally:

```bash
python evals/runtime_metrics.py --out /tmp/aipos-metrics-new-run
```

The output directory must not already exist. The check runs the bundled emitter,
verifies scores, counts, AI-assisted PR detection, absence of planted identifiers,
and absence of a readiness token. It does not call a model or send events anywhere.
A native skill run against that fixture is separate evidence: inspect both tool
calls and written artifacts, including the limits of sharing/readiness claims.

Those runtime-dependent cases are **skipped with the reason printed**, not run and recorded as failures:

```
SKIP  gate-readiness-audit: needs /tmp/testrepo — no runtime target and no tools,
      so its rubric cannot be exercised
```

A skip is not a pass and the summary says so. Grading them anyway would blame the skill for a
gap in the harness.

## Re-running after a change

Resume is keyed on `(case, rep)` **and a fingerprint of everything that decides what the grade
means** — the skill package, the case fixtures, the rubric, and both model ids. Change any of
them and the recorded result is stale, so the case runs again and the run says how many were
invalidated.

Without that, editing a `SKILL.md` and re-running would skip every case and present the old
grade as current — which would make the harness worse than useless for the one job it has.

## What a real run cost

Measured on `aipos-rapid-validation`, 4 cases, `claude-opus-5` judged by `claude-sonnet-5`:
**$0.95 at one turn**, 92–237 seconds per case, 2.2k–11.4k output tokens per turn. The skill
package cached at 24,780 tokens per case after the first.

**There is no trustworthy two-turn figure here.** The $1.07 previously published for the default
two turns was measured while the runner summed only the *final* turn's usage, so it omitted the
first turn entirely. The accounting was fixed in #23; the number was never re-measured, and
correcting it by arithmetic would be inventing a measurement. The real two-turn cost is higher
than $1.07 by roughly the first turn's tokens — re-run with `--reps 1` on this case set if you
need the figure, and replace this paragraph with what it reports.

Budget from output length, not case count: the longest case cost triple the shortest, because a
skill that produces a full artifact writes far more than one that stops to ask a question.

## What a passing run does and does not prove

It proves the skill produced the behaviour the rubric describes, **once, under that model at that
effort**. That is evidence, not proof:

- A model-graded verdict is a judgement, and a judge can be wrong in the same direction as the
  subject.
- **One run is one sample, and the noise is larger than you would guess.** One case scored
  0.50 / 0.571 / 0.71 / 0.43 across four runs against an *unchanged* skill and an *unchanged*
  rubric — a 0.28 spread from variance alone, wide enough to manufacture a regression that is
  not there. It did: a single post-change run read 0.43 and looked like damage; `--reps 3`
  returned 0.71 / 0.77 / 0.71, identical to before.
  **Use `--reps 3` before concluding a change helped or hurt.** A single-run comparison is a
  coin toss wearing a decimal point.
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

A truncated subject turn makes the conversation incomplete even if the judge
approves the combined answer. Such rows are not passing results. New rows keep
the judge's raw verdict in `judge_passed`; summaries also exclude historical
`status: truncated` rows whose older `passed` field recorded only that verdict.
Resuming an entirely cached run still reports its failures and returns a failing
exit code when appropriate; it does not call a model again.

## Reporting a run

Per CONTRIBUTING: **never report an eval as passing unless it actually ran.** When you run one,
say which cases ran, the subject and judge models, and the results. `results.jsonl` carries
`model` and `usage` per row (including the judge's) so spend can be worked out afterwards; the
runner deliberately does not compute cost, so a model swap cannot carry a stale rate.

## Why this is not a required PR check

The merge gate stays `claude plugin validate` + `pytest tests -q`: offline, key-free, fast.

An LLM-judged gate is non-deterministic. A required check that fails occasionally for no reason
trains people to re-run until green — and `aipos-feature-refine` already says why that is
corrosive: *"false gates teach teams to ignore real ones."* A secrets-dependent check also cannot
run on fork PRs at all.

So the eval job is `workflow_dispatch` — run it deliberately, and paste the result into the PR
when a change touches coaching behaviour.

## Regrade an existing conversation

When judge instructions change, reuse the actual subject conversation without
paying to generate a replacement answer:

```bash
python evals/run_evals.py --skill aipos-feature-create \
  --regrade-from consolidation --variant conversation-judge-v2 \
  --model claude-opus-5 --judge-model claude-sonnet-5 --reps 3 --execute
```

This calls only the judge. The source and destination variants must differ.
The source skill package, input fixtures, subject model, turn count, and user
follow-ups must still match; otherwise the runner refuses reuse and a fresh
subject run is required. Original results and traces remain intact. New rows
record subject provenance and zero new subject usage, with the original usage
retained separately. A judge-input contract change invalidates cached grades.

Earlier versions concatenated assistant turns without the user's intervening
reply. This made legitimate multi-turn pauses look like uninterrupted responses.
Do not compare those historical coaching pass rates to conversation-aware grades
as if only the skill had changed.

For a recorded `judge-truncated` error, use `--judge-max-tokens 32000` in a
separate variant. The output ceiling is recorded and a changed ceiling
invalidates the grade fingerprint. Use `--regrade-from` when a completed source
conversation exists; an attempt that failed before saving its conversation
needs a fresh subject. Keep the original error visible, and do not rerun a
completed behavioral failure merely to obtain a passing answer.
