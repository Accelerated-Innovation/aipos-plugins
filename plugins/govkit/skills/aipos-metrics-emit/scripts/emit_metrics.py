#!/usr/bin/env python3
"""aipos-metrics-emit: org-agnostic Tier 1 metric event producer.

Reads GovKit exhaust (feature packages, .govkit/marker.json, git history,
optional CI-run / PR JSON exports) and emits NDJSON events per the AIPOS
tier1_metrics_catalog v1 vocabulary.

Design law: org-agnostic. Only repo-relative facts leave this script.
"""
import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML required: pip install pyyaml --break-system-packages")

PRODUCER = "aipos-metrics-emit/1.0.0"
CATALOG_VERSION = "1.0.0"
SCHEMA_VERSION = 1

KNOWN_GATES = {
    "eval-gate", "deepeval-gate", "promptfoo-gate", "ui-eval-gate",
    "quality-gate", "ui-quality-gate", "l3-quality-gate", "l3-ui-quality-gate",
    "guardrails-check", "multi-agent-gate", "repo-scope-check",
    "data-common-gate", "databricks-gate", "dbt-gate",
}

EVENT_FIELDS = {
    "feature.package.snapshot": {
        "feature_id", "commit_sha", "ts", "artifacts_present", "artifacts_valid",
        "gherkin_scenario_count", "nfr_heading_count", "evaluation_prediction",
        "eval_criteria_summary", "completeness", "marker_level",
    },
    "pr.merged": {
        "pr_id", "feature_id", "ts_opened", "ts_ready", "ts_first_review",
        "ts_merged", "lines_added", "lines_deleted", "files_changed",
        "ai_assisted", "review_count", "reviewer_types",
    },
    "gate.run.completed": {
        "feature_id", "gate_name", "run_attempt", "conclusion",
        "ts_start", "ts_end", "commit_sha",
    },
    "deploy.completed": {"deploy_id", "env", "ts", "status", "commit_shas"},
    "rework.observed": {
        "commit_sha_origin", "ts_origin", "lines_added", "lines_reworked_21d",
        "rework_author_same", "feature_id", "method",
    },
}

ENVELOPE_FIELDS = {"event", "producer", "catalog_version", "schema_version"}

AI_TRAILER_RE = re.compile(
    r"co-authored-by:.*\b(claude|copilot|cursor|windsurf|codex|agent|bot)\b", re.I
)


def git(repo: Path, *args: str) -> str:
    out = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True, text=True, check=False,
    )
    return out.stdout.strip() if out.returncode == 0 else ""


def envelope(event_name: str, payload: dict) -> dict:
    return {
        "event": event_name,
        "producer": PRODUCER,
        "catalog_version": CATALOG_VERSION,
        "schema_version": SCHEMA_VERSION,
        **payload,
    }


# ---------------------------------------------------------------- marker
def read_marker(repo: Path) -> dict:
    for candidate in (repo / ".govkit" / "marker.json", repo / ".govkit"):
        if candidate.is_file():
            try:
                return json.loads(candidate.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                return {}
    return {}


# ---------------------------------------------------------- feature parse
def count_gherkin_scenarios(path: Path) -> int:
    if not path.is_file():
        return 0
    n = 0
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        s = line.strip()
        if s.startswith("#"):
            continue
        if re.match(r"Scenario( Outline)?:", s):
            n += 1
    return n


def count_nfr_headings(path: Path) -> int:
    if not path.is_file():
        return 0
    text = path.read_text(encoding="utf-8", errors="replace")
    return len(re.findall(r"^#{1,4}\s+\S", text, flags=re.M))


def extract_evaluation_prediction(plan_path: Path):
    """Pull the evaluation_prediction YAML block out of plan.md."""
    if not plan_path.is_file():
        return None
    text = plan_path.read_text(encoding="utf-8", errors="replace")
    for m in re.finditer(r"```ya?ml\s*\n(.*?)```", text, flags=re.S):
        block = m.group(1)
        if "evaluation_prediction" not in block:
            continue
        try:
            data = yaml.safe_load(block)
        except yaml.YAMLError:
            return None
        if isinstance(data, dict) and isinstance(
                data.get("evaluation_prediction"), dict):
            return data["evaluation_prediction"]
    return None


def read_eval_criteria(path: Path):
    if not path.is_file():
        return None
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8", errors="replace"))
    except yaml.YAMLError:
        return None
    return data if isinstance(data, dict) else None


def completeness(feature_dir: Path, pred, criteria, marker_level) -> dict:
    """Spec completeness rubric — tier1_metrics_catalog pair-4 (0-100)."""
    pred = pred if isinstance(pred, dict) else None
    comps = []

    def add(name, points, ok, reason):
        comps.append({"name": name, "points": points,
                      "awarded": points if ok else 0, "reason": reason})

    scen = count_gherkin_scenarios(feature_dir / "acceptance.feature")
    add("gherkin_scenarios", 20, scen >= 1,
        f"{scen} scenario(s) in acceptance.feature")

    nfr = count_nfr_headings(feature_dir / "nfrs.md")
    add("nfrs", 10, nfr >= 1, f"{nfr} heading(s) in nfrs.md")

    add("evaluation_prediction_block", 15, pred is not None,
        "evaluation_prediction parsed from plan.md" if pred is not None
        else "plan.md missing or evaluation_prediction block absent/invalid")

    thr = bool(pred and pred.get("thresholds_met") is True)
    add("thresholds_met", 15, thr,
        f"thresholds_met={pred.get('thresholds_met') if pred else None}")

    fa = pred.get("first", {}).get("average") if pred else None
    va = pred.get("virtues", {}).get("average") if pred else None
    ok_scores = isinstance(fa, (int, float)) and isinstance(va, (int, float)) \
        and fa >= 4.0 and va >= 4.0
    add("score_minima", 15, ok_scores, f"first.average={fa}, virtues.average={va}")

    crit_list = (criteria or {}).get("llm_evaluation", {}).get("criteria", []) \
        if isinstance((criteria or {}).get("llm_evaluation"), dict) else []
    mode = (criteria or {}).get("mode")
    ok_crit = bool(criteria) and mode in ("llm", "deterministic", "none") and \
        (mode != "llm" or len(crit_list) >= 1)
    add("eval_criteria", 15, ok_crit,
        f"mode={mode}, criteria={len(crit_list)}" if criteria
        else "eval_criteria.yaml missing or invalid")

    needs_preflight = str(marker_level) == "5"
    has_preflight = (feature_dir / "architecture_preflight.md").is_file()
    add("architecture_preflight", 10,
        has_preflight if needs_preflight else True,
        f"required={needs_preflight}, present={has_preflight}")

    score = sum(c["awarded"] for c in comps)
    return {"score": score, "max": 100, "components": comps}


def snapshot_events(repo: Path, marker: dict):
    features_dir = repo / "features"
    if not features_dir.is_dir():
        return
    level = marker.get("level")
    # Fallback anchor for a feature with no path-specific commit yet (e.g. an
    # uncommitted working-tree feature): use repo HEAD so commit_sha / ts stay
    # non-null strings per the event vocabulary. They stay None only when the
    # repo has no commits at all, which validate() then flags.
    head_sha = git(repo, "rev-parse", "HEAD")
    head_ts = git(repo, "show", "-s", "--format=%cI", "HEAD")
    for fdir in sorted(p for p in features_dir.iterdir() if p.is_dir()):
        rel = f"features/{fdir.name}"
        sha = git(repo, "log", "-1", "--format=%H", "--", rel) or head_sha or None
        ts = git(repo, "log", "-1", "--format=%cI", "--", rel) or head_ts or None
        artifacts = ["acceptance.feature", "nfrs.md", "plan.md",
                     "eval_criteria.yaml", "architecture_preflight.md",
                     "agent_topology.md"]
        present = {a: (fdir / a).is_file() for a in artifacts}
        pred = extract_evaluation_prediction(fdir / "plan.md")
        criteria = read_eval_criteria(fdir / "eval_criteria.yaml")
        valid = {
            "acceptance.feature": count_gherkin_scenarios(fdir / "acceptance.feature") >= 1,
            "plan.md": pred is not None,
            "eval_criteria.yaml": criteria is not None,
        }
        crit_list = (criteria or {}).get("llm_evaluation", {}).get("criteria", []) \
            if isinstance((criteria or {}).get("llm_evaluation"), dict) else []
        yield envelope("feature.package.snapshot", {
            "feature_id": fdir.name,
            "commit_sha": sha,
            "ts": ts,
            "artifacts_present": present,
            "artifacts_valid": valid,
            "gherkin_scenario_count": count_gherkin_scenarios(fdir / "acceptance.feature"),
            "nfr_heading_count": count_nfr_headings(fdir / "nfrs.md"),
            "evaluation_prediction": {
                "first_average": (pred or {}).get("first", {}).get("average"),
                "virtues_average": (pred or {}).get("virtues", {}).get("average"),
                "thresholds_met": (pred or {}).get("thresholds_met"),
            } if pred else None,
            "eval_criteria_summary": {
                "mode": (criteria or {}).get("mode"),
                "criteria_count": len(crit_list),
                "tools": sorted({c.get("tool") for c in crit_list if c.get("tool")}),
                "enforce_first": (criteria or {}).get("unit_tests", {}).get("enforce_FIRST"),
                "enforce_virtues": (criteria or {}).get("code_quality", {}).get("enforce_virtues"),
            } if criteria else None,
            "completeness": completeness(fdir, pred, criteria, level),
            "marker_level": level,
        })


def load_json_list(path: Path, label: str) -> list:
    """Read a user-supplied JSON array (optional --ci-runs / --prs input).

    Optional inputs must not abort the run with a traceback: on any read or
    parse problem, or if the top level is not a JSON array, exit 2 with a
    clear message instead.
    """
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        print(f"error: cannot read {label} file '{path}': {exc}", file=sys.stderr)
        sys.exit(2)
    except json.JSONDecodeError as exc:
        print(f"error: {label} file '{path}' is not valid JSON: {exc}",
              file=sys.stderr)
        sys.exit(2)
    if not isinstance(data, list):
        print(f"error: {label} file '{path}' must be a JSON array, not "
              f"{type(data).__name__}", file=sys.stderr)
        sys.exit(2)
    return data


# ------------------------------------------------------------- gate runs
def gate_events(runs: list):
    for r in runs:
        raw = (r.get("name") or r.get("workflowName") or "").strip()
        base = raw.lower().removesuffix(".yml").removesuffix(".yaml")
        if base not in KNOWN_GATES:
            continue
        blob = " ".join(str(r.get(k, "")) for k in
                        ("displayTitle", "headBranch", "title"))
        m = re.search(r"features?/([A-Za-z0-9_\-]+)", blob)
        yield envelope("gate.run.completed", {
            "feature_id": m.group(1) if m else None,
            "gate_name": base,
            "run_attempt": r.get("attempt") or r.get("runAttempt") or 1,
            "conclusion": r.get("conclusion") or r.get("result"),
            "ts_start": r.get("createdAt") or r.get("startTime"),
            "ts_end": r.get("updatedAt") or r.get("finishTime"),
            "commit_sha": r.get("headSha") or r.get("sourceVersion"),
        })


# ------------------------------------------------------------------ PRs
def pr_events(prs: list):
    for pr in prs:
        commits = pr.get("commits") or []
        texts = []
        for c in commits:
            texts.append(str(c.get("messageHeadline", "")))
            texts.append(str(c.get("messageBody", "")))
        ai = bool(AI_TRAILER_RE.search("\n".join(texts)))
        reviews = pr.get("reviews") or []
        rtypes = sorted({
            "agent" if "[bot]" in str((rv.get("author") or {}).get("login", ""))
            else "human"
            for rv in reviews
        })
        first_review = min(
            (rv.get("submittedAt") for rv in reviews if rv.get("submittedAt")),
            default=None,
        )
        blob = f"{pr.get('title','')} {pr.get('headRefName','')}"
        m = re.search(r"features?/([A-Za-z0-9_\-]+)", blob)
        yield envelope("pr.merged", {
            "pr_id": pr.get("number"),
            "feature_id": m.group(1) if m else None,
            "ts_opened": pr.get("createdAt"),
            "ts_ready": pr.get("readyAt") or pr.get("createdAt"),
            "ts_first_review": first_review,
            "ts_merged": pr.get("mergedAt"),
            "lines_added": pr.get("additions"),
            "lines_deleted": pr.get("deletions"),
            "files_changed": pr.get("changedFiles"),
            "ai_assisted": ai,
            "review_count": len(reviews),
            "reviewer_types": rtypes,
        })


# --------------------------------------------------------------- rework
def rework_events(repo: Path, window_days: int):
    """File-overlap approximation of 21-day rework (upper bound).

    lines_reworked = deletions applied by later commits (within the window)
    to files the origin commit added lines to, capped at origin additions.
    Exact line provenance is aggregator-side v2.
    """
    log = git(repo, "log", "--reverse", "--format=C|%H|%cI|%ae", "--numstat")
    if not log:
        return
    commits = []
    cur = None
    for line in log.splitlines():
        if line.startswith("C|"):
            _, sha, ts, email = line.split("|", 3)
            cur = {"sha": sha, "ts": ts, "author": email, "files": {}}
            commits.append(cur)
        elif cur is not None and "\t" in line:
            a, d, fname = line.split("\t", 2)
            if a == "-":
                continue
            cur["files"][fname] = {"added": int(a), "deleted": int(d)}
    for i, c in enumerate(commits):
        try:
            t0 = datetime.fromisoformat(c["ts"])
        except ValueError:
            continue
        horizon = t0 + timedelta(days=window_days)
        added = sum(f["added"] for f in c["files"].values())
        if added == 0:
            continue
        reworked = 0
        same_author = False
        for later in commits[i + 1:]:
            try:
                t1 = datetime.fromisoformat(later["ts"])
            except ValueError:
                continue
            if t1 > horizon:
                break
            overlap = set(c["files"]) & set(later["files"])
            for fname in overlap:
                reworked += min(c["files"][fname]["added"],
                                later["files"][fname]["deleted"])
                if later["author"] == c["author"]:
                    same_author = True
        feature = None
        for fname in c["files"]:
            m = re.match(r"features/([A-Za-z0-9_\-]+)/", fname)
            if m:
                feature = m.group(1)
                break
        yield envelope("rework.observed", {
            "commit_sha_origin": c["sha"],
            "ts_origin": c["ts"],
            "lines_added": added,
            "lines_reworked_21d": min(reworked, added),
            "rework_author_same": same_author,
            "feature_id": feature,
            "method": "file-overlap-approximation",
        })


# ------------------------------------------------------------- validate
def validate(events: list) -> dict:
    summary = {"total": len(events), "by_event": {}, "errors": []}
    for i, e in enumerate(events):
        name = e.get("event")
        summary["by_event"][name] = summary["by_event"].get(name, 0) + 1
        if name not in EVENT_FIELDS:
            summary["errors"].append(f"event {i}: unknown event '{name}'")
            continue
        allowed = EVENT_FIELDS[name] | ENVELOPE_FIELDS
        unknown = set(e) - allowed
        if unknown:
            summary["errors"].append(
                f"event {i} ({name}): unknown fields {sorted(unknown)}")
        missing_env = ENVELOPE_FIELDS - set(e)
        if missing_env:
            summary["errors"].append(
                f"event {i} ({name}): missing envelope {sorted(missing_env)}")
        if name == "feature.package.snapshot":
            for key in ("commit_sha", "ts"):
                if not e.get(key):
                    summary["errors"].append(
                        f"event {i} ({name}): missing or empty '{key}'")
    summary["valid"] = not summary["errors"]
    return summary


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("repo", type=Path)
    ap.add_argument("--ci-runs", type=Path)
    ap.add_argument("--prs", type=Path)
    ap.add_argument("--rework-days", type=int, default=21)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--validate", action="store_true")
    args = ap.parse_args()

    if not args.repo.is_dir():
        sys.exit(f"repo not found: {args.repo}")

    marker = read_marker(args.repo)
    events = list(snapshot_events(args.repo, marker))
    events.extend(rework_events(args.repo, args.rework_days))
    if args.ci_runs:
        events.extend(gate_events(load_json_list(args.ci_runs, "--ci-runs")))
    if args.prs:
        events.extend(pr_events(load_json_list(args.prs, "--prs")))

    ndjson = "\n".join(json.dumps(e, sort_keys=False) for e in events)
    if args.out:
        args.out.write_text(ndjson + "\n", encoding="utf-8")
        print(f"wrote {len(events)} events -> {args.out}", file=sys.stderr)
    else:
        print(ndjson)

    if args.validate:
        summary = validate(events)
        print(json.dumps(summary, indent=2), file=sys.stderr)
        if not summary["valid"]:
            sys.exit(2)


if __name__ == "__main__":
    main()
