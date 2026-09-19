"""Locate shipped skills uniquely, independent of their enclosing plugin name."""

from pathlib import Path

PLUGINS = Path(__file__).resolve().parents[1] / "plugins"


def skill_paths(plugins=PLUGINS):
    found = {}
    for entry in sorted(plugins.glob("*/skills/*/SKILL.md")):
        name = entry.parent.name
        if name in found:
            raise ValueError(f"duplicate skill {name}")
        found[name] = entry.parent
    if not found:
        raise ValueError("no skills discovered")
    return found


def skill_path(name, plugins=PLUGINS):
    try:
        return skill_paths(plugins)[name]
    except KeyError as error:
        raise ValueError(f"missing skill {name}") from error
