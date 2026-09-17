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

def test_the_system_prompt_is_the_whole_skill_package(runner):
    """A skill is SKILL.md *and* the references it tells the subject to read.

    govkit-feature-create names six, and says of one that it "is what the
    gates judge your Gherkin against". Sending only SKILL.md would have the
    subject work from memory and the judge grade the memory — which measures
    nothing about the shipped package.
    """
    skill_dir = runner.discover_skills()["govkit-feature-create"]
    case = runner.load_cases(skill_dir)[0]

    system, _user = runner.build_subject_request(skill_dir, case)

    assert (skill_dir / "SKILL.md").read_text(encoding="utf-8") in system
    for required in ("gherkin-authoring-standard.md", "spec-identifiers.md",
                     "feature-template.md", "gherkin-tagging.md",
                     "story-mapping.md", "tracker-adapters.md"):
        assert f'path="' in system and required in system, f"{required} not attached"


def test_references_outside_the_plugin_are_not_shipped(runner, tmp_path):
    """Same boundary the plugin tests enforce: a plugin installs on its own,
    so a path climbing into a sibling is not a resource this skill has."""
    plugin = tmp_path / "plugins" / "fake"
    skill = plugin / "skills" / "probe"
    skill.mkdir(parents=True)
    (plugin / "references").mkdir()
    (plugin / "references" / "inside.md").write_text("INSIDE", encoding="utf-8")
    (tmp_path / "plugins" / "outside.md").write_text("OUTSIDE", encoding="utf-8")
    (skill / "SKILL.md").write_text(
        "See `../../references/inside.md` and `../../../references/outside.md`.",
        encoding="utf-8")

    resolved = runner.resolve_references(skill)

    assert [rel for rel, _ in resolved] == ["references/inside.md"]


def test_a_case_needing_an_unavailable_runtime_target_is_detected(runner):
    """govkit-metrics-emit points at a governed repo at /tmp/testrepo. This
    runner has no such repo and no tools, so the case cannot perform the
    behaviour its rubric grades — it must be skipped, not run and failed."""
    skill_dir = runner.discover_skills()["govkit-metrics-emit"]
    case = next(c for c in runner.load_cases(skill_dir) if c.get("files"))

    assert runner.unavailable_targets(skill_dir, case) == ["/tmp/testrepo"]


def test_a_fully_bundled_case_is_runnable(runner):
    skill_dir = runner.discover_skills()["govkit-feature-create"]
    case = next(c for c in runner.load_cases(skill_dir) if c.get("files"))

    assert runner.unavailable_targets(skill_dir, case) == []


def test_attached_files_are_inlined_with_the_prompt_last(runner):
    skill_dir = runner.discover_skills()["govkit-feature-create"]
    case = next(c for c in runner.load_cases(skill_dir) if c.get("files"))

    _system, user = runner.build_subject_request(skill_dir, case)

    attached = (skill_dir / "evals" / case["files"][0]).read_text(encoding="utf-8")
    assert attached.strip() in user
    assert user.rstrip().endswith(case["prompt"].rstrip())


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


def test_the_schema_carries_no_numeric_bounds(runner):
    """Structured outputs reject `minimum`/`maximum` on a number — a live 400
    that no dry run surfaces. The range is enforced in check_verdict()
    instead, so the schema must not reintroduce them."""
    score = runner.VERDICT_SCHEMA["properties"]["score"]

    assert "minimum" not in score and "maximum" not in score
    assert runner.check_verdict({"passed": True, "score": 1.5, "missed": []}) is not None


def test_subject_and_judge_default_to_different_models(runner):
    """A model grading its own output agrees with itself more than it should."""
    assert runner.DEFAULT_SUBJECT_MODEL != runner.DEFAULT_JUDGE_MODEL


# ------------------------------------------------------------------ staleness

class _Args:
    def __init__(self, model="claude-opus-5", judge_model="claude-sonnet-5"):
        self.model, self.judge_model = model, judge_model


def test_changing_the_skill_invalidates_a_recorded_grade(runner, tmp_path, monkeypatch):
    """The defect that would make this harness worse than useless: edit a
    SKILL.md, re-run, and every case is skipped as already done while the old
    grade is presented as current."""
    skill_dir = runner.discover_skills()["govkit-feature-slice"]
    case = runner.load_cases(skill_dir)[0]
    before = runner.input_digest(skill_dir, case, _Args())

    skill_md = skill_dir / "SKILL.md"
    original = skill_md.read_text(encoding="utf-8")
    try:
        skill_md.write_text(original + "\n\nAn added coaching rule.\n", encoding="utf-8")
        after = runner.input_digest(skill_dir, case, _Args())
    finally:
        skill_md.write_text(original, encoding="utf-8")

    assert before != after


@pytest.mark.parametrize(
    "args",
    [_Args(model="claude-sonnet-5"), _Args(judge_model="claude-haiku-4-5")],
    ids=["subject-model", "judge-model"],
)
def test_changing_either_model_invalidates_a_recorded_grade(runner, args):
    """A grade means 'this model, judged by that one'. Reusing it across a
    model swap silently compares two different things."""
    skill_dir = runner.discover_skills()["govkit-feature-slice"]
    case = runner.load_cases(skill_dir)[0]

    assert runner.input_digest(skill_dir, case, _Args()) != runner.input_digest(
        skill_dir, case, args)


def test_a_row_with_a_stale_digest_does_not_count_as_done(runner, tmp_path):
    results = tmp_path / "results.jsonl"
    runner.append_row(results, {"prompt_id": "c", "rep": 0, "input_digest": "OLD"})

    assert runner.load_completed(results, {"c_rep0": "NEW"}) == set()
    assert runner.load_completed(results, {"c_rep0": "OLD"}) == {"c_rep0"}


# ------------------------------------------------------------------ verdict sanity

@pytest.mark.parametrize(
    ("verdict", "why"),
    [
        ({"passed": True, "score": 1.5, "missed": []}, "score above 1"),
        ({"passed": True, "score": -0.2, "missed": []}, "negative score"),
        ({"passed": True, "score": "high", "missed": []}, "non-numeric score"),
        ({"passed": True, "score": 0.4, "missed": ["a claim"]}, "passed with a missed claim"),
        ({"passed": False, "score": 1.0, "missed": []}, "failed with everything met"),
    ],
)
def test_an_inconsistent_verdict_is_a_grader_error(runner, verdict, why):
    """A schema keeps the shape; it cannot keep the verdict self-consistent.
    Recording one of these would launder a bad grade into the results."""
    assert runner.check_verdict(verdict) is not None, why


def test_a_coherent_verdict_passes(runner):
    assert runner.check_verdict(
        {"passed": False, "score": 0.5, "missed": ["one claim"]}) is None
    assert runner.check_verdict({"passed": True, "score": 1.0, "missed": []}) is None
