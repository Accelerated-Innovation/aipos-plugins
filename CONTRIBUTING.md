# Contributing to GovKit Plugins

Thanks for helping improve GovKit. This repo is a [Claude Code plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces); most contributions are new or improved **skills** inside the `govkit` or `aipos-p2` plugins.

## Repository layout

```
.claude-plugin/marketplace.json   # marketplace catalog (lists both plugins)
plugins/<plugin>/                 # govkit/ or aipos-p2/
  .claude-plugin/plugin.json      # plugin manifest (bump version on release)
  references/                     # plugin-wide references shared by several skills
  skills/<skill-name>/SKILL.md    # one folder per skill; loads automatically
templates/skill-template/         # copy this to start a new skill
tests/                            # deterministic checks for the bundled skill scripts
```

Guidance that more than one skill depends on belongs in `plugins/<plugin>/references/`, not copied into each skill. A skill reaches it with a relative path — `../../references/<file>.md`. `plugins/govkit/references/gherkin-authoring-standard.md` is the worked example: one Gherkin authoring standard, cited by five skills, restated by none.

## Adding or changing a skill

1. Create `plugins/<plugin>/skills/<your-skill-name>/SKILL.md`, copying [`templates/skill-template/SKILL.md`](templates/skill-template/SKILL.md) as a starting point.
2. Keep the frontmatter `description` specific — it is the only text Claude sees when deciding whether to load the skill, so include the trigger words a user would actually type.
3. Put any supporting material in the skill folder: `references/` for rubrics/checklists the skill reads at runtime, `evals/` for evaluation cases and sample inputs.
4. Skills load automatically from a plugin's `skills/` directory — you don't need to register them anywhere.

## Before you open a PR

Validate the marketplace and plugin manifests, and run the deterministic checks:

```bash
claude plugin validate .

python -m pip install -r requirements-dev.txt
python -m pytest tests -q
```

The `pytest` suite covers the bundled Python scripts — Gherkin ingestion fidelity (`repo_ingest.py`) and the feature-map renderer. It asserts behavior and semantic preservation, never instructional wording: a test that matched a heading or a phrase in a `SKILL.md` would pass while the tool silently broke. It runs offline and calls no model.

Each skill's `evals/evals.json` is a separate, **model-graded** pass. Those cases need a model and are not part of the deterministic gate; when you run them, say which cases ran and what the results were. Never report an eval as passing unless it actually ran.

Then check:

- [ ] `claude plugin validate .` passes.
- [ ] `python -m pytest tests -q` passes.
- [ ] JSON files (`marketplace.json`, `plugin.json`, any `evals.json`) are valid and consistent (names, descriptions, keywords).
- [ ] Bumped `version` in the affected plugin's `.claude-plugin/plugin.json` if the change is user-visible. Users pick up updates with `/plugin marketplace update aipos`.
- [ ] Updated the [README](README.md) and any relevant `references/` if behavior changed.

## Continuous integration

Every pull request runs two jobs from [`.github/workflows/validate.yml`](.github/workflows/validate.yml): `claude plugin validate` (static structural validation of the manifests) and `pytest` against `tests/`. Both must pass before merge, and neither needs an API key or network access at test time.

## Commit and PR conventions

- Keep commits focused and messages descriptive.
- Describe the user-facing effect of the change in the PR body, not just the files touched.
- One skill or one coherent change per PR where practical.

## License

By contributing, you agree that your contributions are licensed under the [MIT License](LICENSE).
