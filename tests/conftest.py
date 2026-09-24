"""Make the bundled skill scripts importable from the tests.

The scripts live inside the plugin (they ship to users there), so the tests load them by
path rather than expecting an installed package.
"""

import importlib.util
import pathlib
import sys

import pytest

from skill_paths import skill_path

ROOT = pathlib.Path(__file__).resolve().parents[1]
FIXTURES = pathlib.Path(__file__).resolve().parent / "fixtures"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="session")
def repo_ingest():
    return _load("repo_ingest",
                 skill_path("aipos-map-render") / "scripts" / "repo_ingest.py")


@pytest.fixture(scope="session")
def render_map():
    return _load("render_map",
                 skill_path("aipos-map-render") / "scripts" / "render_map.py")


@pytest.fixture(scope="session")
def workflow_resolve():
    return _load("workflow_resolve",
                 skill_path("aipos-map-render") / "scripts" / "workflow_resolve.py")


@pytest.fixture(scope="session")
def workflows():
    return FIXTURES / "workflows"


@pytest.fixture(scope="session")
def corpus():
    return FIXTURES / "corpus"


@pytest.fixture(scope="session")
def ingested(repo_ingest, corpus):
    """The whole fixture corpus, ingested once, keyed by directory name."""
    feats = repo_ingest.walk(str(corpus), "dir", "")
    return {pathlib.Path(f["sourcePath"]).name: f for f in feats}


@pytest.fixture(scope="session")
def features(repo_ingest, corpus):
    """The corpus as the flat features.json list a resolver consumes."""
    return repo_ingest.walk(str(corpus), "dir", "")


@pytest.fixture(scope="session")
def readiness_state():
    return _load("readiness_state",
                 skill_path("aipos-feature-readiness") / "scripts" / "readiness_state.py")


@pytest.fixture(scope="session")
def change_package():
    return _load("change_package",
                 skill_path("aipos-feature-refine") / "scripts" / "change_package.py")
