# Install or replace the initial AIPOS plugins

The new package is `aipos@aipos`, containing all eleven `aipos-*` skills. The
repository and marketplace source remain `Accelerated-Innovation/govkit-plugins`.
These commands apply once the consolidated candidate has been released to that
source. See the [release record](release-check.md) for current verification status.

## New installation

```bash
claude plugin marketplace add Accelerated-Innovation/govkit-plugins
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
contains eleven skills. Start a new session. Existing `.govkit/` artifacts and
feature packages need no conversion. There are no compatibility aliases or
migration scripts.

## Later updates

Refresh the marketplace and update the installed plugin at its installed scope:

```bash
claude plugin marketplace update aipos
claude plugin update aipos@aipos --scope user
```

Keep plugin and marketplace metadata consistent and bump the plugin version when
releasing a user-visible change. Historical plans and evaluation traces retain
the identities recorded when they were created.
