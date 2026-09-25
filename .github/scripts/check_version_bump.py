#!/usr/bin/env python3
"""Fail a pull request that changes a plugin without raising its version.

Claude Code updates an installed plugin only when its version changes: a
commit that edits a plugin but keeps `plugin.json`'s version never reaches
anyone who already has that version, while fresh installs pick it up. One
version number then means two different plugins. See
https://code.claude.com/docs/en/plugins/host-marketplace#release-a-new-version

Usage (from CI, with the base branch fetched):

    python .github/scripts/check_version_bump.py origin/main

Exit 0 when every changed plugin's version increased, or no plugin changed.
Exit 1 with one line per plugin that changed without an increase.
"""

import json
import re
import subprocess
import sys

PLUGINS_DIR = "plugins"
SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def parse(version):
    """A version as a comparable tuple, or None when it is not plain semver."""
    m = SEMVER.match(version or "")
    return tuple(int(p) for p in m.groups()) if m else None


def changed_plugins(paths):
    """Plugin directory names touched by a list of changed paths."""
    names = set()
    for p in paths:
        parts = p.split("/")
        if len(parts) >= 3 and parts[0] == PLUGINS_DIR:
            names.add(parts[1])
    return sorted(names)


def verdict(name, base_version, head_version):
    """None when the change is releasable, else the reason it is not.

    A plugin that is new on this branch (no base version) needs only a valid
    version. Anything else must strictly increase: an unchanged version is
    the silent non-release this check exists for, and a decrease would leave
    existing users on the higher cached copy.
    """
    head = parse(head_version)
    if head is None:
        return f"{name}: plugin.json version {head_version!r} is not MAJOR.MINOR.PATCH"
    if base_version is None:
        return None
    base = parse(base_version)
    if base is None or head > base:
        return None
    return (f"{name}: files under {PLUGINS_DIR}/{name}/ changed but its version stayed "
            f"{base_version} -> {head_version}. Bump .claude-plugin/plugin.json, or users "
            f"who already have {base_version} never receive this change.")


def _git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, check=False)


def _version_at(ref, name):
    path = f"{PLUGINS_DIR}/{name}/.claude-plugin/plugin.json"
    shown = _git("show", f"{ref}:{path}")
    if shown.returncode != 0:
        return None
    return json.loads(shown.stdout).get("version")


def main(argv):
    if len(argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    base = argv[1]
    merge_base = _git("merge-base", base, "HEAD")
    if merge_base.returncode != 0:
        print(f"error: cannot find a merge base with {base}; fetch it first", file=sys.stderr)
        return 2
    diff = _git("diff", "--name-only", merge_base.stdout.strip(), "HEAD", "--", PLUGINS_DIR)
    names = changed_plugins(diff.stdout.split())
    if not names:
        print("no plugin files changed")
        return 0

    problems = []
    for name in names:
        head_version = _version_at("HEAD", name)
        if head_version is None:
            continue  # plugin deleted on this branch; nothing to release
        reason = verdict(name, _version_at(merge_base.stdout.strip(), name), head_version)
        if reason:
            problems.append(reason)
        else:
            print(f"{name}: {_version_at(merge_base.stdout.strip(), name)} -> {head_version}")

    for p in problems:
        print(f"error: {p}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
