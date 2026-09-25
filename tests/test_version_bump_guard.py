"""A plugin change without a version bump never reaches existing users.

Claude Code updates an installed plugin only when its version changes, so the
CI guard fails a PR that edits a plugin and keeps its version. These tests pin
the guard's decisions, and run it against a throwaway git repository so the
git plumbing is exercised too.
"""

import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".github" / "scripts" / "check_version_bump.py"


@pytest.fixture(scope="module")
def guard():
    spec = importlib.util.spec_from_file_location("check_version_bump", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_only_files_inside_a_plugin_count(guard):
    assert guard.changed_plugins([
        "plugins/aipos/skills/x/SKILL.md", "plugins/aipos/.claude-plugin/plugin.json",
        "docs/rollout.md", "plugins/README.md", "viewers/journey/src/App.jsx",
    ]) == ["aipos"]


@pytest.mark.parametrize("base, head, ok", [
    ("1.3.0", "1.3.1", True),
    ("1.3.0", "1.4.0", True),
    ("1.9.0", "1.10.0", True),       # numeric, not string, comparison
    ("1.3.0", "1.3.0", False),       # the silent non-release
    ("1.3.1", "1.3.0", False),       # a decrease strands users on the higher copy
    (None, "0.1.0", True),           # a plugin new on this branch
])
def test_a_change_needs_a_strictly_higher_version(guard, base, head, ok):
    assert (guard.verdict("aipos", base, head) is None) is ok


def test_a_version_that_is_not_plain_semver_is_refused(guard):
    assert "MAJOR.MINOR.PATCH" in guard.verdict("aipos", "1.3.0", "1.3.1-beta")


def _repo(tmp_path):
    def git(*args):
        subprocess.run(["git", *args], cwd=tmp_path, check=True, capture_output=True)

    def write(path, text):
        p = tmp_path / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")

    def version(v):
        write("plugins/aipos/.claude-plugin/plugin.json", json.dumps({"name": "aipos", "version": v}))

    git("init", "-q", "-b", "main")
    git("config", "user.email", "t@example.test")
    git("config", "user.name", "t")
    version("1.3.0")
    write("plugins/aipos/skills/a/SKILL.md", "one")
    write("docs/notes.md", "one")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    git("switch", "-q", "-c", "work")
    return git, write, version


def _run(tmp_path):
    return subprocess.run([sys.executable, str(SCRIPT), "main"], cwd=tmp_path,
                          capture_output=True, text=True)


def test_ci_fails_a_skill_edit_without_a_bump(tmp_path):
    git, write, _ = _repo(tmp_path)
    write("plugins/aipos/skills/a/SKILL.md", "two")
    git("commit", "-qam", "edit")
    run = _run(tmp_path)
    assert run.returncode == 1
    assert "1.3.0 -> 1.3.0" in run.stderr


def test_ci_passes_a_skill_edit_with_a_bump(tmp_path):
    git, write, version = _repo(tmp_path)
    write("plugins/aipos/skills/a/SKILL.md", "two")
    version("1.3.1")
    git("commit", "-qam", "edit and bump")
    run = _run(tmp_path)
    assert run.returncode == 0, run.stderr
    assert "1.3.0 -> 1.3.1" in run.stdout


def test_ci_ignores_changes_outside_plugins(tmp_path):
    git, write, _ = _repo(tmp_path)
    write("docs/notes.md", "two")
    git("commit", "-qam", "docs")
    run = _run(tmp_path)
    assert run.returncode == 0
    assert "no plugin files changed" in run.stdout
