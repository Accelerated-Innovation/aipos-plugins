"""Every bundled script has to run where it is installed — increment 15.

Skills install into somebody else's project, one plugin at a time, with no
sibling source trees and no guarantee that a neighbour skill came along.
`test_plugin_boundaries.py` already holds the cross-*plugin* line. This
holds two more that only matter once scripts exist:

- **Third-party imports are declared, not assumed.** `govkit-feature-map`
  ships a `requirements.txt` because it needs a Gherkin parser. A script in
  another skill that quietly imports the same parser works perfectly in
  this source tree — where the dependency is installed for the tests — and
  fails in the project it was installed into.
- **Scripts do not hard-code sibling script paths.** Skills in one plugin ship
  together, but callers may invoke scripts from an unrelated working directory.

Both are asserted from the source rather than by importing, so a script
that is broken *at import time* is still checked.
"""

from __future__ import annotations

import ast
import importlib.util
import pathlib
import sys
import sysconfig

import pytest

from skill_paths import skill_path, skill_paths

ROOT = pathlib.Path(__file__).resolve().parents[1]

#: Skills allowed third-party imports, and the file that declares them.
DECLARED = {
    skill: skill_path(skill) / "scripts" / "requirements.txt"
    for skill in ("govkit-feature-map", "govkit-metrics-emit", "govkit-synthetic-data")
}

_STDLIB_DIR = pathlib.Path(sysconfig.get_paths()["stdlib"]).resolve()


def is_stdlib(name: str) -> bool:
    """Whether `name` resolves to the standard library of this interpreter.

    Resolved by location rather than `sys.stdlib_module_names`, which needs
    3.10 and this repository's tests run on 3.9 as well. A module counts as
    stdlib when it is built in, or when its file sits under the
    interpreter's stdlib directory and not in site-packages.
    """
    if name in sys.builtin_module_names:
        return True
    try:
        spec = importlib.util.find_spec(name)
    except (ImportError, ValueError):
        return False
    if spec is None:
        return False
    origin = spec.origin
    # `built-in` and `frozen` are markers, not paths. Resolving them as
    # paths put them outside the stdlib directory and made `os` — frozen
    # since 3.11 — look like a third-party import. This passed locally on
    # 3.9, where `os` is an ordinary file, and failed the 3.11 CI job:
    # a portability check verified on one interpreter.
    if origin in (None, "built-in", "frozen"):
        return True
    resolved = pathlib.Path(origin).resolve()
    return _STDLIB_DIR in resolved.parents and "site-packages" not in resolved.parts


def scripts():
    return sorted(p for skill in skill_paths().values() for p in skill.glob("scripts/*.py"))


def test_there_are_scripts_to_check():
    """The glob is the claim. If it stopped matching, everything below
    would pass over an empty list."""
    assert len(scripts()) >= 6


@pytest.mark.parametrize("path", scripts(), ids=lambda p: f"{p.parents[1].name}/{p.name}")
def test_a_script_imports_only_stdlib_or_a_declared_dependency(path):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    skill = path.parents[1].name

    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            imported.add(node.module.split(".")[0])

    third_party = sorted(name for name in imported if not is_stdlib(name))
    if not third_party:
        return

    requirements = DECLARED.get(skill)
    assert requirements, (
        f"{skill}/{path.name} imports {third_party} and its skill declares no "
        "requirements.txt. A script that quietly imports a dependency works here, "
        "where the tests installed it, and fails in the project it ships to."
    )
    declared = requirements.read_text(encoding="utf-8").lower()
    for name in third_party:
        assert name.replace("_", "-") in declared or name in declared, (
            f"{skill}/{path.name} imports {name!r}, which {requirements.name} "
            "does not declare"
        )


@pytest.mark.parametrize("path", scripts(), ids=lambda p: f"{p.parents[1].name}/{p.name}")
def test_a_script_does_not_reach_into_another_skill(path):
    """Scripts stay self-contained within their own skill directory.

    **Not** because a sibling skill might be missing — the installable
    unit is the plugin, so `/plugin install govkit@aipos` brings every
    skill under it and a sibling is always present. I first wrote the
    opposite here, and it was wrong: that reasoning belongs to
    `test_plugin_boundaries.py`, where a user really can have one plugin
    without another.

    The reason that survives is narrower. A script is invoked with
    whatever working directory the caller has, so a hard-coded relative
    path into a sibling is fragile in a way a documented invocation is
    not — which is why two SKILL.md files legitimately call sibling
    scripts (`govkit-workflow-map` runs `govkit-feature-map`'s ingester)
    and no script hard-codes one. Instructions are the documented place
    for that coupling; a module-level path is not.

    Matched on **path shapes and imports**, not on the name appearing
    anywhere. The first version flagged four files for mentioning a
    sibling in a comment — including the one explaining why the token
    record preserves the fields `govkit-metrics-emit` reads, which is
    exactly the kind of cross-reference that should be written down. A
    dependency is a path or an import; a sentence is not.
    """
    text = path.read_text(encoding="utf-8")
    own = path.parents[1].name
    siblings = [p.name for p in path.parents[2].iterdir() if p.is_dir() and p.name != own]

    for other in siblings:
        for shape in (f"/{other}/", f"'{other}'", f'"{other}"'):
            assert shape not in text, (
                f"{own}/{path.name} references the sibling skill {other!r} as "
                f"{shape} — the script depends on a relative sibling path rather than "
                "a stable invocation from the project directory"
            )

    tree = ast.parse(text, filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [a.name for a in getattr(node, "names", [])]
            if isinstance(node, ast.ImportFrom) and node.module:
                names.append(node.module)
            for name in names:
                flat = name.replace("_", "-")
                assert not any(other in flat for other in siblings), name


@pytest.mark.parametrize(
    "path",
    [p for p in scripts() if p.name in {"readiness_state.py", "change_package.py"}],
    ids=lambda p: p.name,
)
def test_the_new_governance_scripts_need_nothing_installed(path):
    """Stated separately from the general rule because it is a property
    worth keeping rather than a coincidence: these two run on a bare
    interpreter, so adopting the behavior-contract workflow adds no
    installation step."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert is_stdlib(alias.name.split(".")[0]), alias.name
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            assert is_stdlib(node.module.split(".")[0]), node.module
