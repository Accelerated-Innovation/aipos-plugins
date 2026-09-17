"""Structural integrity of the model-graded eval cases.

These cases are graded by a model, not by pytest, and nothing here asserts
whether a skill coaches well — that is what the eval run is for, and a test
matching phrases in an `expected_output` would pass while the coaching silently
broke.

What is checkable deterministically is whether a case can *run at all*. An
eval naming a fixture file that no longer exists does not fail loudly: it
grades a prompt with a missing attachment and quietly produces a worse result
than the case was written to measure. That is the failure this module catches.

Increment 03 of the AIPOS behavior-contract plan
(docs/plans/2026-09-17-aipos-behavior-contract.md).
"""

import json
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
PLUGINS = ROOT / "plugins"

EVAL_FILES = sorted(PLUGINS.rglob("evals/evals.json"))


def _cases(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    return data, data.get("evals", [])


def test_every_skill_with_an_evals_dir_has_cases():
    """A scan that matched nothing would pass forever."""
    assert len(EVAL_FILES) >= 5


@pytest.mark.parametrize("path", EVAL_FILES, ids=[p.parent.parent.name for p in EVAL_FILES])
def test_eval_file_is_well_formed(path):
    data, cases = _cases(path)

    assert data.get("skill_name") == path.parent.parent.name
    assert cases, f"{path} declares no cases"
    for case in cases:
        assert case.get("name"), f"{path}: a case has no name"
        assert case.get("prompt"), f"{path}: {case.get('name')} has no prompt"
        assert case.get("expected_output"), f"{path}: {case.get('name')} has no expected_output"


@pytest.mark.parametrize("path", EVAL_FILES, ids=[p.parent.parent.name for p in EVAL_FILES])
def test_case_ids_and_names_are_unique(path):
    _data, cases = _cases(path)

    ids = [c.get("id") for c in cases]
    names = [c.get("name") for c in cases]

    assert len(set(ids)) == len(ids), f"{path}: duplicate case ids {ids}"
    assert len(set(names)) == len(names), f"{path}: duplicate case names"


@pytest.mark.parametrize("path", EVAL_FILES, ids=[p.parent.parent.name for p in EVAL_FILES])
def test_every_bundled_fixture_exists(path):
    """The one that actually bites: a renamed or deleted fixture degrades the
    eval silently instead of failing it.

    Only *relative* entries are bundled fixtures. An absolute path is a runtime
    target the eval sets up for itself — `govkit-metrics-emit` points its cases
    at a governed repo at `/tmp/testrepo` — and asserting that exists in a
    checkout would be asserting something this repository does not own.
    """
    _data, cases = _cases(path)
    missing = [
        (c.get("name"), rel)
        for c in cases
        for rel in c.get("files", [])
        if not pathlib.PurePosixPath(rel).is_absolute() and not (path.parent / rel).is_file()
    ]

    assert not missing, f"{path}: cases reference fixtures that do not exist: {missing}"


@pytest.mark.parametrize("path", EVAL_FILES, ids=[p.parent.parent.name for p in EVAL_FILES])
def test_no_fixture_is_orphaned(path):
    """An unreferenced fixture is usually a case that was renamed away from it,
    which means the case it belonged to is no longer being exercised."""
    files_dir = path.parent / "files"
    if not files_dir.is_dir():
        pytest.skip("skill has no fixture files")

    _data, cases = _cases(path)
    referenced = {
        rel for c in cases for rel in c.get("files", [])
        if not pathlib.PurePosixPath(rel).is_absolute()
    }
    on_disk = {f"files/{p.name}" for p in files_dir.iterdir() if p.is_file()}

    assert not (on_disk - referenced), f"{path}: unreferenced fixtures {sorted(on_disk - referenced)}"
