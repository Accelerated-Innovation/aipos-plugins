"""A plugin may not reach into another installed plugin.

In this repository every plugin sits under `plugins/`, so a relative path that
climbs out of one and into another resolves fine here and looks correct in
review. It is not correct: plugins install independently, a user may have one
without the other, and there is no dependency mechanism that would make the
neighbour's presence a guarantee. The path that works in this source tree is
exactly the path that breaks in the installed layout.

So the rule is structural rather than stylistic, and this test is what keeps
it true as skills are added.

Increment 02 of the AIPOS behavior-contract plan
(docs/plans/2026-09-17-aipos-behavior-contract.md).
"""

import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
PLUGINS = ROOT / "plugins"

# Relative paths as they appear in skill prose and script docstrings:
# `../../references/x.md`, `../../../references/y.md`.
RELATIVE_PATH_RE = re.compile(r"(?:\.\./)+[A-Za-z0-9_][A-Za-z0-9_./-]*")

TEXT_SUFFIXES = {".md", ".py", ".json", ".txt", ".yaml", ".yml"}

PLUGIN_NAMES = frozenset(p.name for p in PLUGINS.iterdir() if p.is_dir())


def _plugin_files():
    for plugin_dir in sorted(p for p in PLUGINS.iterdir() if p.is_dir()):
        for path in sorted(plugin_dir.rglob("*")):
            if path.is_file() and path.suffix in TEXT_SUFFIXES:
                yield plugin_dir, path


def _crosses_into_another_plugin(plugin_dir, path, relative):
    """True when `relative`, resolved from `path`'s directory, lands in a *different* plugin.

    Deliberately narrower than "leaves the plugin". Reference files document
    the path a *skill folder* would use to reach them — `../../references/x.md`
    — and resolving that from the reference's own directory climbs out of
    `plugins/` entirely, to a directory that is not a plugin at all. That is
    prose about another file's path, not a link this file follows, and failing
    it would be a false positive that teaches people to work around the test.

    What is never acceptable is a path that resolves *into a sibling plugin*,
    because that is the one that resolves here and breaks once installed. So
    the first segment is compared against the real plugin names — landing on
    `plugins/references/`, which is not a plugin and does not exist, is prose
    over-climbing, not a reach into a neighbour.
    """
    target = (path.parent / relative).resolve()
    try:
        inside = target.relative_to(PLUGINS.resolve())
    except ValueError:
        return False  # outside plugins/ altogether — not a cross-plugin reach
    other = inside.parts[0] if inside.parts else ""
    return other in PLUGIN_NAMES and other != plugin_dir.name


ALL_FILES = list(_plugin_files())


def test_the_scan_actually_looked_at_something():
    """A boundary test that silently matched no files would pass forever."""
    assert len(ALL_FILES) > 10


@pytest.mark.parametrize(
    ("plugin_dir", "path"),
    ALL_FILES,
    ids=[str(p.relative_to(PLUGINS)) for _, p in ALL_FILES],
)
def test_no_file_reaches_into_another_plugin(plugin_dir, path):
    text = path.read_text(encoding="utf-8", errors="replace")
    offenders = sorted({
        rel for rel in RELATIVE_PATH_RE.findall(text)
        if _crosses_into_another_plugin(plugin_dir, path, rel)
    })

    assert not offenders, (
        f"{path.relative_to(ROOT)} reaches into another plugin from {plugin_dir.name!r}: "
        f"{offenders}. "
        f"Plugins install independently — a relative path that climbs out of one resolves "
        f"in this source tree and breaks once installed. Keep the resource inside the "
        f"plugin that owns it, or put the skill that needs it in the same plugin."
    )


def test_shared_references_stay_canonical_in_the_plugin_that_owns_them():
    """The govkit plugin owns the shared references; nothing duplicates them.

    The alternative to reaching across plugins is copying, and a copied
    reference is one nobody maintains — the failure this repo already avoids
    for the Gherkin authoring standard, which five skills cite and none
    restates.
    """
    owned = {p.name for p in (PLUGINS / "govkit" / "references").glob("*.md")}
    assert "spec-identifiers.md" in owned
    assert "workflow-source.md" in owned

    duplicates = [
        p for p in PLUGINS.rglob("references/*.md")
        if p.name in owned and p.parent != PLUGINS / "govkit" / "references"
    ]
    assert not duplicates, f"shared reference copied instead of cited: {duplicates}"
