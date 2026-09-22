"""A copied plugin resolves resources without the repository's old layout."""

import re
import shutil
import subprocess
import sys

import pytest
import yaml

from skill_paths import skill_path, skill_paths

RESOURCE = re.compile(r"`((?:\.\./)*(?:[a-z0-9-]+/)*(?:references|scripts)/[A-Za-z0-9_./-]+\.(?:md|py|txt))`")


def resources(skill):
    root = skill.parent.parent.resolve()
    result = []
    for relative in RESOURCE.findall((skill / "SKILL.md").read_text()):
        target = (skill / relative).resolve()
        target.relative_to(root)  # refuses escaped and symlinked resources
        if not target.is_file():
            raise ValueError(f"missing resource: {relative}")
        result.append(target)
    return result


def test_unique_skills_have_matching_frontmatter_and_resolvable_resources():
    paths = skill_paths()
    assert len(paths) == 12
    for name, path in paths.items():
        front = yaml.safe_load((path / "SKILL.md").read_text().split("---", 2)[1])
        assert front["name"] == name
        assert isinstance(front["description"], str) and front["description"].strip()
        resources(path)


def test_locator_rejects_missing_and_duplicate_skills(tmp_path):
    for plugin in ("one", "two"):
        skill = tmp_path / plugin / "skills" / "duplicate"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text("content")
    with pytest.raises(ValueError, match="duplicate"):
        skill_paths(tmp_path)
    with pytest.raises(ValueError, match="missing skill"):
        skill_path("nonexistent")


def test_resource_check_rejects_missing_and_escaped_paths(tmp_path):
    skill = tmp_path / "plugin/skills/probe"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text("Read `references/absent.md`.")
    with pytest.raises(ValueError, match="missing resource"):
        resources(skill)
    outside = tmp_path / "references"
    outside.mkdir()
    (outside / "external.md").write_text("outside plugin")
    (skill / "SKILL.md").write_text("Read `../../../references/external.md`.")
    with pytest.raises(ValueError):
        resources(skill)


def test_copied_plugin_runs_from_an_unrelated_project(tmp_path):
    source = skill_path("aipos-feature-map").parent.parent
    installed = tmp_path / "installed"
    shutil.copytree(source, installed, ignore=shutil.ignore_patterns("__pycache__"))
    project = tmp_path / "unrelated-project"
    package = project / "features/example"
    package.mkdir(parents=True)
    (package / "acceptance.feature").write_text(
        'Feature: Example\n  Scenario: One\n    Given a request\n    When it is accepted\n    Then it succeeds\n')
    for skill in (installed / "skills").iterdir():
        if (skill / "SKILL.md").is_file():
            resources(skill)
    script = installed / "skills/aipos-feature-map/scripts/repo_ingest.py"
    proc = subprocess.run([sys.executable, str(script), "features", "-o", "features.json"],
                          cwd=project, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    assert (project / "features.json").is_file()
