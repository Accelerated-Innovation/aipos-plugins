# Install or replace the initial AIPOS plugins

The new package is `aipos@aipos`, containing all thirteen `aipos-*` skills. The
repository and marketplace source are `Accelerated-Innovation/aipos-plugins`
(renamed from `govkit-plugins`; the old URL redirects).
Everything merged to `main` is released: the version in
`plugins/aipos/.claude-plugin/plugin.json` is the release, and each one is tagged
and listed on the [releases page](https://github.com/Accelerated-Innovation/aipos-plugins/releases).
The sections below say what an existing user must do when updating to a
version. The earlier [1.0.1 release record](release-check.md) is historical.

## Updating to 1.3.1

1.3.1 delivers `aipos-map-render` guidance that shipped after 1.3.0 without a
version bump, so installations updated to 1.3.0 before 2026-09-25 do not have it:
journey answers are given only after a render, a scenario under a referenced
Rule is placed through `aipos-workflow-create`, and readers are told how to get
both answers from the page. Nothing to do beyond updating; no files move.

## Product strategy (since 1.2.0)

`aipos-product-strategy` shipped in 1.2.0. Canvas decision language, graph
baseline access, and first-evidence intake are tracked follow-ups, not
prerequisites for using the brief workflow. Existing downstream evidence and
approval rules continue to apply. Its [verification record](plans/2026-09-24-aipos-product-strategy.md)
lists what was checked at release; full Anthropic model evaluations, native
installation, and connected-workflow checks were not run then.

## Updating to 1.3.0

1.3.0 renames four skills and adds interactive journey diagrams. Update as in
[Later updates](#later-updates), then start a new session.

| Before 1.3.0 | From 1.3.0 |
|---|---|
| `aipos-workflow-map` | `aipos-workflow-create` |
| `aipos-feature-map` | `aipos-map-render` |
| `aipos-quarterly-planning` | `aipos-exploration-planning` |
| `aipos-solution-design` | `aipos-solution-framing` |

There are no aliases. Anything that names an old skill — saved prompts, team
docs, hooks, scripts calling `skills/aipos-feature-map/scripts/...` — needs the
new name.

**Solution canvases move folders.** The canvas is now the *Solution Framing*
canvas, saved under `solution-framing/<slug>/` rather than `solution-design/<slug>/`.
To resume an existing canvas, move its folder first:

```bash
git mv solution-design solution-framing   # or plain mv if the folder is not tracked
```

Renders from 1.3.0 on say "Solution Framing" in the canvas header.

**Journey diagrams.** `aipos-map-render` draws L1 / L2 / L3 journey diagrams
from one or more workflows (`render_map.py -w` repeats), showing which scenarios
specify a journey and which journeys a feature change affects. The viewer ships
prebuilt; nothing extra to install. Maps rendered before 1.3.0 are unchanged
until re-rendered.

## New installation

```bash
claude plugin marketplace add Accelerated-Innovation/aipos-plugins
claude plugin install aipos@aipos
claude plugin list
claude plugin details aipos@aipos
```

Start a new session so it loads the updated catalog.

## Replace an early installation

Inspect `claude plugin list --json` to see which old plugins are installed and
at which scope. Uninstall only those present, using their original scope. For
user-scope installations:

```bash
claude plugin uninstall aipos-p1@aipos --scope user
claude plugin uninstall aipos-p2@aipos --scope user
claude plugin uninstall govkit@aipos --scope user
claude plugin marketplace update aipos
claude plugin install aipos@aipos --scope user
claude plugin list --json
claude plugin details aipos@aipos
```

Use `--scope project` or `--scope local` from the corresponding project when
that is where an old plugin was installed. Remove old entries at every scope in
which they remain enabled; do not retain old and new packages together.

Check that only `aipos@aipos` is enabled for this marketplace and its inventory
contains thirteen skills. Start a new session. Existing `.govkit/` artifacts and
feature packages need no conversion. There are no compatibility aliases or
migration scripts.

## Later updates

Refresh the marketplace and update the installed plugin at its installed scope:

```bash
claude plugin marketplace update aipos
claude plugin update aipos@aipos --scope user
```

Maintainers: every change under `plugins/` bumps the version in `plugin.json`,
which is what makes it reach installed users; see
[Releases](../CONTRIBUTING.md#releases). Historical plans and evaluation traces retain
the identities recorded when they were created.
