# Contributing to AIPOS

Thanks for helping improve AIPOS. This repo is a [Claude Code plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces); most contributions are new or improved **skills** inside the single `aipos` plugin.

## Repository layout

```
.claude-plugin/marketplace.json   # marketplace catalog (one aipos entry)
plugins/aipos/                    # all thirteen aipos-* skills
  .claude-plugin/plugin.json      # plugin manifest (bump version on release)
  references/                     # plugin-wide references shared by several skills
  skills/<skill-name>/SKILL.md    # one folder per skill; loads automatically
templates/skill-template/         # copy this to start a new skill
tests/                            # deterministic checks for the bundled skill scripts
viewers/journey/                  # source of the journey diagram viewer (never shipped)
```

Guidance that more than one skill depends on belongs in `plugins/aipos/references/`, not copied into each skill. A skill reaches it with a relative path — `../../references/<file>.md`. `plugins/aipos/references/gherkin-authoring-standard.md` is the worked example: one Gherkin authoring standard, cited by five skills, restated by none.

## Adding or changing a skill

1. Create `plugins/aipos/skills/aipos-<your-skill-name>/SKILL.md`, copying [`templates/skill-template/SKILL.md`](templates/skill-template/SKILL.md) as a starting point.
2. Keep the frontmatter `description` specific — it is the only text Claude sees when deciding whether to load the skill, so state the requested action, useful input context, result, and nearest competing boundary. Avoid broad noun-only triggers.
3. Put any supporting material in the skill folder: `references/` for rubrics/checklists the skill reads at runtime, `evals/` for evaluation cases and sample inputs.
4. Skills load automatically from a plugin's `skills/` directory — you don't need to register them anywhere.

For selection changes, use the [skill ownership model](docs/workflow.md#ownership-and-handoffs)
and add contrasting prompts to [the routing cases](evals/routing/README.md).
Routing cases test which skill loads; per-skill cases test its behavior after loading.

## Before you open a PR

Validate the marketplace and plugin manifests, and run the deterministic checks:

```bash
claude plugin validate .
claude plugin validate plugins/aipos

python -m pip install -r requirements-dev.txt
python -m pytest tests -q
```

The `pytest` suite covers the bundled Python scripts — Gherkin ingestion fidelity (`repo_ingest.py`) and the feature-map renderer (`render_map.py`). It asserts behavior and semantic preservation, never instructional wording: a test that matched a heading or a phrase in a `SKILL.md` would pass while the tool silently broke. It runs offline and calls no model.

Each skill's `evals/evals.json` is a separate, **model-graded** pass. Those cases need a model and are not part of the deterministic gate; when you run them, say which cases ran and what the results were. Never report an eval as passing unless it actually ran.

`evals/run_evals.py` is what runs them:

```bash
python -m pip install -r requirements-evals.txt
python evals/run_evals.py --skill aipos-feature-create             # dry run, free
python evals/run_evals.py --skill aipos-feature-create --execute   # real calls, real money
```

`--execute` is required to spend anything. The skill's `SKILL.md` becomes the system prompt and a **different** model grades the response against the case's `expected_output`. Results and full traces land in `.claude/hillclimb/<skill>/<variant>/` (gitignored) — read the traces, not just the score. Details and the limits of what a passing run proves: [`evals/README.md`](evals/README.md).

It is deliberately **not** a required check. The merge gate stays offline and key-free; the eval job is `workflow_dispatch`. Run it when a change touches coaching behaviour and paste the result into the PR.

### The journey viewer

`aipos-map-render` draws its L1 / L2 / L3 journey diagram with React Flow. The viewer's source lives in [`viewers/journey/`](viewers/journey/) and is built into one committed bundle in `plugins/aipos/skills/aipos-map-render/scripts/assets/`, which the renderer inlines so every map stays a single offline file. Users never need Node; contributors changing the viewer do:

```bash
cd viewers/journey
npm ci
npm test               # vitest: levels, scope and highlighting
npm run build          # rewrites scripts/assets/ — commit the result
npm run check-bundle   # fails if the committed bundle is not what the source builds
node check-page.mjs <map.html> [screenshot-dir]   # drives a rendered map in Chrome
```

The bundle, its CSS and `THIRD_PARTY_NOTICES.txt` are build output: review them as generated code and never edit them by hand. Every fact the diagram shows is computed in Python by `journey_graph.py` and tested in `pytest`; the viewer only lays it out and handles selection. When the graph model changes, regenerate the viewer's test fixture with `python tests/test_render_journeys.py --write-viewer-fixture` — a pytest fails until you do. Keep dependencies pinned and permissively licensed, and keep the bundle under the ceiling `tests/test_render_journeys.py` sets.

Then check:

- [ ] `claude plugin validate .` passes.
- [ ] `python -m pytest tests -q` passes.
- [ ] If the change touches `viewers/journey/`, `npm test` and `npm run check-bundle` pass there, and you looked at a rendered map with `check-page.mjs`.
- [ ] If the change touches coaching behaviour (a `SKILL.md`, a reference it reads, or an eval case), ran `evals/run_evals.py` for the affected skill and reported which cases ran, the models used, and the results — or said plainly that it was not run.
- [ ] JSON files (`marketplace.json`, `plugin.json`, any `evals.json`) are valid and consistent (names, descriptions, keywords).
- [ ] Bumped `version` in the affected plugin's `.claude-plugin/plugin.json` if the change is user-visible. See the [rollout guide](docs/rollout.md#later-updates) for marketplace refresh and installed-plugin update commands.
- [ ] Updated the [README](README.md) and any relevant `references/` if behavior changed.

## Continuous integration

Every pull request runs three jobs from [`.github/workflows/validate.yml`](.github/workflows/validate.yml): `claude plugin validate` (static structural validation of the manifests), `pytest` against `tests/`, and the journey viewer's `npm test` plus a rebuild that fails if the committed bundle is stale. All must pass before merge, and none needs an API key or network access at test time beyond installing pinned packages.

## Commit and PR conventions

- Keep commits focused and messages descriptive.
- Describe the user-facing effect of the change in the PR body, not just the files touched.
- One skill or one coherent change per PR where practical.

## Releases

A version is released when the PR that bumps it merges: the marketplace installs from `main`, so users receive it on their next `claude plugin marketplace update`. Record each one:

1. Add an update section to [`docs/rollout.md`](docs/rollout.md) in the bumping PR — renames, moved files, and anything else an existing user must act on.
2. After it merges, tag the merge commit `vX.Y.Z` (matching `plugin.json`) and publish a GitHub release from that section:

   ```bash
   git switch main && git pull --ff-only
   git tag -a vX.Y.Z -m "aipos X.Y.Z"
   git push origin vX.Y.Z
   gh release create vX.Y.Z --title "aipos X.Y.Z" --notes-file <notes.md>
   ```

Tags do not change what users install; they mark what each version was, so versions can be diffed, referenced, and restored.

## License

By contributing, you agree that your contributions are licensed under the [MIT License](LICENSE).
