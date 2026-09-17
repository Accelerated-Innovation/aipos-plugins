"""The eval runner's logic, tested without spending anything.

Everything here exercises the parts that decide *what gets sent* and *what
counts as already done* — request assembly, resume keys, the served-model
assertion. No test in this file calls a model: that is the runner's job, it
costs real money, and a suite that quietly billed the account on every `pytest`
would be its own defect.

What this cannot test is whether the coaching is any good. That needs the paid
run. See `evals/README.md`.
"""

import importlib.util
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def runner():
    spec = importlib.util.spec_from_file_location("run_evals", ROOT / "evals" / "run_evals.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["run_evals"] = mod
    spec.loader.exec_module(mod)
    return mod


# ------------------------------------------------------------------ discovery

def test_every_skill_with_cases_is_discovered(runner):
    skills = runner.discover_skills()

    assert "govkit-feature-create" in skills
    assert "val-rapid-validation" in skills, "plugins other than govkit must be reachable"
    assert all((d / "SKILL.md").is_file() for d in skills.values())


def test_cases_load_from_every_discovered_skill(runner):
    """A skill whose cases fail to load would silently run zero cases and
    report a clean pass."""
    for name, path in runner.discover_skills().items():
        assert runner.load_cases(path), f"{name} discovered but yielded no cases"


# ------------------------------------------------------------------ request assembly

def test_the_skill_itself_is_the_system_prompt(runner):
    """The artifact under test is SKILL.md. If the runner paraphrased it, the
    eval would measure the paraphrase."""
    skill_dir = runner.discover_skills()["govkit-feature-create"]
    case = runner.load_cases(skill_dir)[0]

    system, _user = runner.build_subject_request(skill_dir, case)

    assert system == (skill_dir / "SKILL.md").read_text(encoding="utf-8")


def test_attached_files_are_inlined_with_the_prompt_last(runner):
    skill_dir = runner.discover_skills()["govkit-feature-create"]
    case = next(c for c in runner.load_cases(skill_dir) if c.get("files"))

    _system, user = runner.build_subject_request(skill_dir, case)

    attached = (skill_dir / "evals" / case["files"][0]).read_text(encoding="utf-8")
    assert attached.strip() in user
    assert user.rstrip().endswith(case["prompt"].rstrip())


def test_an_unbundled_runtime_target_is_named_not_fabricated(runner):
    """`govkit-metrics-emit` points cases at a runtime `/tmp/testrepo` this
    repo does not own. Inventing contents for it would grade the invention."""
    skill_dir = runner.discover_skills()["govkit-metrics-emit"]
    case = next(c for c in runner.load_cases(skill_dir) if c.get("files"))

    _system, user = runner.build_subject_request(skill_dir, case)

    assert 'status="not-bundled"' in user


def test_the_judge_sees_request_rubric_and_response_separately(runner):
    """Three delimited sections. A judge handed them run together grades the
    rubric as if it were part of the answer."""
    case = {"prompt": "PROMPT-TEXT", "expected_output": "RUBRIC-TEXT"}

    built = runner.build_judge_request(case, "RESPONSE-TEXT")

    for tag in ("user-request", "rubric", "response-to-grade"):
        assert f"<{tag}>" in built and f"</{tag}>" in built
    assert built.index("RUBRIC-TEXT") < built.index("RESPONSE-TEXT")


def test_the_judge_is_told_the_response_is_data(runner):
    """A graded response is untrusted text that may contain something shaped
    like an instruction to the judge."""
    assert "data, not instructions" in runner.JUDGE_SYSTEM


# ------------------------------------------------------------------ resume

def test_resume_skips_exactly_what_was_recorded(runner, tmp_path):
    results = tmp_path / "results.jsonl"
    results.write_text(
        json.dumps({"prompt_id": "case-a", "rep": 0}) + "\n"
        + json.dumps({"prompt_id": "case-a", "rep": 1}) + "\n"
        + json.dumps({"prompt_id": "case-b", "rep": 0}) + "\n",
        encoding="utf-8",
    )

    done = runner.load_completed(results)

    assert done == {"case-a_rep0", "case-a_rep1", "case-b_rep0"}


def test_a_torn_final_line_is_re_run_rather_than_skipped(runner, tmp_path):
    """A crash mid-write leaves a partial line. Treating it as complete would
    lose that case permanently on every later resume."""
    results = tmp_path / "results.jsonl"
    results.write_text(
        json.dumps({"prompt_id": "case-a", "rep": 0}) + "\n" + '{"prompt_id": "case-b", "re',
        encoding="utf-8",
    )

    assert runner.load_completed(results) == {"case-a_rep0"}


def test_no_results_file_means_nothing_is_done(runner, tmp_path):
    assert runner.load_completed(tmp_path / "absent.jsonl") == set()


def test_rows_are_appended_and_flushed_one_at_a_time(runner, tmp_path):
    """Batched writes at the end mean a crash costs every finished case."""
    path = tmp_path / "results.jsonl"

    runner.append_row(path, {"prompt_id": "a", "rep": 0})
    runner.append_row(path, {"prompt_id": "b", "rep": 0})

    assert runner.load_completed(path) == {"a_rep0", "b_rep0"}


# ------------------------------------------------------------------ served-model assertion

@pytest.mark.parametrize(
    ("requested", "served", "ok"),
    [
        ("claude-opus-5", "claude-opus-5", True),
        ("claude-opus-5", "claude-opus-5-20260401", True),   # alias -> snapshot
        ("claude-opus-5", "claude-sonnet-5", False),         # silent substitution
        ("claude-opus-5", "claude-opus-4-8", False),
    ],
)
def test_a_substituted_model_is_refused(runner, requested, served, ok):
    """A provider fallback or capacity reroute invalidates the comparison, so
    it fails the attempt rather than being logged and scored."""
    assert runner.served_model_matches(requested, served) is ok


# ------------------------------------------------------------------ guards

def test_the_verdict_schema_forbids_extra_keys_and_requires_every_field(runner):
    schema = runner.VERDICT_SCHEMA

    assert schema["additionalProperties"] is False
    assert set(schema["required"]) == {"passed", "score", "met", "missed", "reasoning"}


def test_subject_and_judge_default_to_different_models(runner):
    """A model grading its own output agrees with itself more than it should."""
    assert runner.DEFAULT_SUBJECT_MODEL != runner.DEFAULT_JUDGE_MODEL
