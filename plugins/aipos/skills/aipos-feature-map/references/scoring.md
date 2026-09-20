# Batch scoring the corpus

Scoring is delegated to `aipos-feature-refine`, which owns the Gherkin Quality Rubric. This file covers only the orchestration: how to fan out, what to send each agent, and what has to come back.

Do not restate the rubric here or in a subagent prompt. Point agents at the rubric files and let them read. A paraphrased rubric drifts from the real one, and the map's whole credibility rests on the scores meaning what the rubric says they mean.

## Which rubric

GovKit gates twice. Pick by where the corpus sits, not by convenience:

- **Unreviewed drafts, in any storage location** — `aipos-feature-refine` batch mode, 10 dimensions, Approved at >= 8/10. This is what the rest of this file documents.
- **Reviewed repo packages being assessed for execution** — `aipos-feature-readiness` batch mode, 12 dimensions, Approved at ~10/12 and Blocked below 8.5. It additionally judges package completeness, source traceability, repo fit and AI coding agent safety.

Use the review state and the requested assessment, not tracker versus repository
location. Feature-create writes unreviewed drafts into repositories. If review
state is unknown, expose that gap and clarify the assessment; do not treat a file
path as evidence of approval. A corpus view cannot complete the missing review.

Record which rubric produced the badges in the map's lede. A 7.5 does not mean the same thing on the two scales, and a reader who assumes the wrong one will misjudge the release.

Both scales have a verified path: `verify_scores.py` defaults to the 10-dimension refine scale, and `--scale readiness` validates 12-dimension readiness verdicts (rubric order, 1.0/0.5/0.0 bands, sums, and the 10 / 8.5 decision bands). For an execution-readiness assessment of reviewed repo packages, fan out exactly as below but point agents at `aipos-feature-readiness`'s SKILL.md (Batch mode section and schema) and its `references/govkit-readiness-rubric.md` instead, then verify with `--scale readiness`. Batch readiness verdicts are advisory badges — they never issue tokens and never write the token record.

## Contents

- [Split first](#split-first)
- [Fan out](#fan-out)
- [The subagent prompt](#the-subagent-prompt)
- [Collect](#collect)
- [Verify](#verify)
- [Handling a feature whose spec lives elsewhere](#handling-a-feature-whose-spec-lives-elsewhere)
- [Sizing the corpus (optional)](#sizing-the-corpus-optional)

## Split first

Write each feature to its own file before spawning anything:

```python
import json, os
os.makedirs("split", exist_ok=True)
for f in json.load(open("features.json")):
    json.dump(f, open(f"split/{f['key']}.json", "w"), indent=1, ensure_ascii=False)
```

A corpus file is often 100KB+. Handing every agent the whole thing wastes most of their context on features they are not scoring and measurably degrades the verdict they produce. Per-feature files are typically ~10KB.

## Fan out

One subagent per feature, all spawned in the same turn so they run concurrently. Use `general-purpose` agents.

Batching several features into one agent is the tempting shortcut and the one to avoid: verdict quality drops for every feature in the batch, because the model is holding four specs and reconciling ten dimensions across all of them. Eleven agents scoring one feature each beats three agents scoring four each, and finishes sooner.

## The subagent prompt

Adapt this per feature. The parts that matter are marked.

```
Apply the GovKit Gherkin Quality Rubric to score ONE feature spec. This is batch
scoring to produce a badge on a diagram — do NOT run any interactive Stage 1/Stage 2
pause, do not ask questions, do not rewrite Gherkin. Score only.

Read these first:
- <plugin>/skills/aipos-feature-refine/references/gherkin-quality-rubric.md
- <plugin>/skills/aipos-feature-refine/SKILL.md   (blocker list, decision bands,
                                                    and the Batch mode section)
- <plugin>/skills/aipos-feature-refine/references/qa-evidence-checklist.md

Then read the feature: split/<KEY>.json

Field mapping: `rules[].rule` = business rules; `rules[].scenarios[]` = Gherkin;
`nfr[]` = NFRs with threshold/evidence/gap; `nfrTbd[]` = unset thresholds;
`evals[]` = evaluation criteria with pass_threshold and gate; `openQuestions[]`;
`dod[]`; `scope[]`/`outOfScope[]`; `userContext` = intent; `privacy`.

Score all 10 dimensions at exactly 1.0, 0.5 or 0.0 using the rubric's bands. Apply
the SKILL.md critical blocker list verbatim. Be precise about "Scenario depends on
unresolved questions" — judge whether each open question actually gates the scenarios
or is a non-blocking refinement; do not auto-block every feature that has open
questions. Ground every blocker and edit in specific content from the feature. Never
invent business rules or thresholds.

Decision rule: any critical blocker present -> "Blocked". Otherwise score >= 8 ->
"Approved"; 7 to under 8 -> "Approved with edits"; under 7 -> "Blocked".

Return ONLY a raw JSON object (no prose, no markdown fence) matching the Batch mode
schema in aipos-feature-refine's SKILL.md. Give 3-6 edits, ranked. blockers is []
if none.
```

Three lines in that prompt are doing real work:

- **"do NOT run any interactive Stage 1/Stage 2 pause"** — `aipos-feature-refine` defaults to a summary-then-confirm conversation. Without this the agent stops and waits for a human who is not there.
- **"do not auto-block every feature that has open questions"** — open questions are ubiquitous in real specs. Most are non-blocking refinements. Without this instruction, everything comes back Blocked and the badge stops discriminating.
- **"Return ONLY a raw JSON object"** — agents otherwise wrap JSON in prose or a fence, and you spend the next step writing parsers.

## Collect

Assemble into `scores.json`:

```jsonc
{
  "_meta": {
    "rubric": "GovKit Gherkin Quality Rubric (aipos-feature-refine)",
    "mode": "batch scoring — no interactive 3 Amigos refinement was run",
    "scale": "10 dimensions at 1.0 / 0.5 / 0.0; total 10",
    "gate": "The critical blocker list is the gate. The score is advisory.",
    "bands": "no blocker and >=8 Approved; 7 to <8 Approved with edits; else Blocked"
  },
  "features": {
    "AI-124": { /* the agent's verdict object */ }
  }
}
```

Keep `_meta`. Six months later somebody will open this file without the conversation that produced it, and the difference between a batch score and a refined one needs to survive.

## Verify

```bash
python scripts/verify_scores.py scores.json --features features.json
```

Run it every time, before rendering. Non-zero exit means do not render.

The failure it exists for: an agent reports a total that does not match its own dimensions. In practice this happens on roughly one feature in ten, and it is invisible by inspection — 8.5 reported against dimensions summing to 8.0 looks entirely reasonable until you add them up, and it is the difference between "Approved" and a conversation the team should have had.

It also catches invalid band values, missing or reordered dimensions, decisions inconsistent with blockers, and features that were never scored at all.

When it fails, prefer re-running that feature's agent over `--fix-sums`. A wrong total often means the agent was uncertain about the underlying dimensions too, and mechanically correcting the arithmetic preserves a verdict that was shaky for other reasons.

## Handling a feature whose spec lives elsewhere

If a feature's spec is not in the ingested record — it lives in a repo, a linked doc, a wiki — first try to ingest it (see `ingestion-contract.md`; the repo adapter and `--merge` exist for exactly this). Score the real spec whenever you can reach it.

When you genuinely cannot, tell the agent so explicitly in its prompt, and instruct it to set `notAssessable: true` and to say in the summary that the score rates reviewability of *this record*, not the quality of the spec. Ask for at least one edit addressing how a spec that lives elsewhere can be made reviewable by Product and QA without duplicating it — CI-generated living documentation and a commit-pinned link are the usual answers.

The renderer surfaces the flag next to the badge. Without it, the map tells the reader that the team with the most disciplined spec practice has the worst spec in the portfolio.

## Sizing the corpus (optional)

When the user wants size badges — how big each feature is, where the Large scenarios hide, what the MVP slice costs — sizing is delegated to `aipos-feature-slice`, which owns the Scenario Complexity Matrix and the MoSCoW slice definitions. Same principle as quality scoring: do not restate its rubric here or in a prompt.

Size and quality are different questions and their verdicts never mix: a feature can be Approved and huge, or Blocked and tiny. Badge them separately.

**Check the tags first.** If the corpus already carries `@small`/`@medium`/`@large` and `@mvp`/`@v1`/`@v2` scenario tags (ingestion preserves them on `scenarios[].tags`), the sizing was already decided — render from the tags and skip the fan-out entirely. Band counts come straight from size tags; only per-slice *points* need a sizing run.

**Otherwise fan out**, same pattern as quality scoring — split files, one feature per agent, all spawned in one turn, raw JSON back:

```
Apply the GovKit Scenario Complexity Matrix to size ONE feature's scenarios. This is
batch sizing for a feature map — non-interactive. Do not pause, do not ask questions,
do not apply tags, do not write anything back. Size and recommend only.

Read these first:
- <plugin>/skills/aipos-feature-slice/SKILL.md        (Batch mode section and schema)
- <plugin>/skills/aipos-feature-slice/references/slicing-rubric.md

Then read the feature: split/<KEY>.json
Field mapping: `rules[].scenarios[]` = the Gherkin; `rules[].scenarios[].tags[]` =
existing tags — read taggedSlice from them, never invent it.

Judge the three dimensions per scenario as integers 1-3 with grounded notes. Emit NO
points, bands, or totals — the caller computes those. Return ONLY a raw JSON object
matching the Batch output schema in aipos-feature-slice's SKILL.md.
```

Collect the verdicts into `sizing.json` (`{"features": {"<KEY>": <verdict>}}`), then compute and verify in one step:

```bash
python ../aipos-feature-slice/scripts/compute_size.py sizing.json --features features.json
```

The script owns all arithmetic — points, bands, rollups, per-slice points, Large-on-MVP risk flags — and exits non-zero on any invalid judgment. The agents emit judgments only; a schema with no total field cannot carry a wrong total. Pass the computed output to the renderer.

**Recommendations are not decisions.** Batch sizing recommends slices; nobody confirmed them. The renderer badges size from computed bands, but groups and filters by *tagged* slices only — a `recommendedSlice` appears on the card as a recommendation, clearly labeled, and the map's lede says whether slices were tagged by the team or recommended by batch sizing. A map that renders unconfirmed recommendations as a release plan has made the team's decision for them.
