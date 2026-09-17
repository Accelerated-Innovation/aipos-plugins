#!/usr/bin/env python3
"""Resolve a workflow definition against an ingested feature corpus.

A `workflow.json` says how a customer outcome is reached: ordered activities,
who acts at each, and which Rules and scenarios govern them. It holds no
behavior of its own -- every behavioral claim is a *reference* into the
canonical Gherkin. That is the whole point: a Rule shown at four steps is
authored once and referenced four times, so rewording it cannot leave three
stale copies behind.

This module turns those references into resolved views and, where they do not
resolve, into diagnostics that name the workflow element and the feature file
involved. It reads `features.json` as produced by `repo_ingest.py` and never
parses Gherkin itself.

Read-only. It resolves and reports; it never edits a workflow or a spec, and
it never invents an identifier to make a reference succeed.

See ../../../references/workflow-source.md for the format and
../../../references/spec-identifiers.md for the identity rules.
"""

import json
import re
import sys

SUPPORTED_VERSIONS = (1,)

# <source-key>/<feature-key>#<kind>:<slug>
REF_RE = re.compile(
    r"^(?P<source>[a-z0-9][a-z0-9._-]*)/(?P<feature>[A-Za-z0-9_][A-Za-z0-9._-]*)"
    r"#(?P<kind>rule|scenario|design|nfr|evaluation|agent-authority):"
    r"(?P<slug>[a-z0-9]+(?:-[a-z0-9]+)*)$"
)

BEHAVIOR_KINDS = ("rule", "scenario")


# ------------------------------------------------------------------ diagnostics

def _diag(level, code, message, **where):
    """One diagnostic. `where` carries whatever locates it: activity, step, ref,
    file, element. A diagnostic a reader cannot locate is a rumour."""
    d = {"level": level, "code": code, "message": message}
    d.update({k: v for k, v in where.items() if v is not None})
    return d


# ------------------------------------------------------------------ corpus index

def index_corpus(features):
    """Build the lookup a reference resolves through.

    Returns `(index, diagnostics)`. The index maps a feature key to a record
    holding its rules and scenarios by slug. Duplicate feature keys are *not*
    silently merged -- two features answering to one key make every reference
    through that key ambiguous, and the caller is told so rather than handed
    whichever one happened to be ingested last.
    """
    index, diagnostics, duplicates = {}, [], {}

    for feat in features:
        key = feat.get("key") or ""
        if key in index:
            duplicates.setdefault(key, [index[key]["sourcePath"]]).append(feat.get("sourcePath"))
            continue

        rules, scenarios = {}, {}
        for rule in feat.get("rules") or []:
            _record(rules, rule.get("id"), rule, feat, "rule", diagnostics)
            for sc in rule.get("scenarios") or []:
                _record(scenarios, sc.get("id"), sc, feat, "scenario", diagnostics)

        index[key] = {
            "key": key,
            "sourcePath": feat.get("sourcePath"),
            "title": feat.get("title"),
            "rule": rules,
            "scenario": scenarios,
            "parseErrors": list(feat.get("parseErrors") or []),
        }

    for key, paths in duplicates.items():
        diagnostics.append(_diag(
            "error", "duplicate-feature-key",
            f"Feature key {key!r} is claimed by more than one feature ({', '.join(p for p in paths if p)}). "
            f"Every reference through this key is ambiguous until one is renamed.",
            element=key,
        ))

    return index, diagnostics


def _record(bucket, slug, node, feat, kind, diagnostics):
    """Register one rule/scenario by slug, reporting a within-feature collision.

    Slugs are required to be unique within their feature. When they are not,
    both entries are kept out of the happy path: resolving to an arbitrary one
    would make the reference mean something nobody wrote.
    """
    if not slug:
        return
    if slug in bucket:
        diagnostics.append(_diag(
            "error", "duplicate-slug",
            f"{kind} slug {slug!r} appears more than once in feature {feat.get('key')!r}. "
            f"Slugs are unique within a feature; a reference to this one cannot be resolved.",
            file=node.get("file"), element=slug, feature=feat.get("key"),
        ))
        bucket[slug] = None  # poisoned: present, but never resolvable
        return
    bucket[slug] = node


# ------------------------------------------------------------------ reference resolution

def parse_ref(ref):
    """Split a qualified reference, or return None when it is not one."""
    m = REF_RE.match(ref or "")
    return m.groupdict() if m else None


def resolve_ref(ref, index, *, where):
    """Resolve one qualified reference. Returns `(resolved_or_None, diagnostics)`.

    `where` locates the reference for every diagnostic this produces, so a
    dangling link reports the activity that carries it rather than only the
    string that failed.
    """
    parts = parse_ref(ref)
    if parts is None:
        return None, [_diag(
            "error", "malformed-ref",
            f"{ref!r} is not a qualified reference. Expected "
            f"<source-key>/<feature-key>#<kind>:<slug>. An unqualified slug cannot say "
            f"which feature it means.",
            ref=ref, **where,
        )]

    feature_key, kind, slug = parts["feature"], parts["kind"], parts["slug"]
    feat = index.get(feature_key)
    if feat is None:
        return None, [_diag(
            "error", "dangling-ref",
            f"{ref!r} names feature {feature_key!r}, which is not in the corpus.",
            ref=ref, element=feature_key, **where,
        )]

    if feat["parseErrors"]:
        # A file that failed to parse yields no elements. Left alone, every
        # reference into it would be reported as dangling — which is true but
        # useless, because it buries the one cause under N symptoms and invites
        # someone to "fix" the references instead of the spec.
        first = feat["parseErrors"][0]
        detail = first.get("message", first) if isinstance(first, dict) else first
        return None, [_diag(
            "error", "unparsed-feature",
            f"{ref!r} points into feature {feature_key!r}, whose Gherkin does not parse: "
            f"{detail}. Fix the spec; a reference into an unparsed file resolves to nothing, "
            f"and an empty result is not a passing one.",
            ref=ref, file=first.get("file") if isinstance(first, dict) else feat.get("sourcePath"),
            element=feature_key, **where,
        )]

    if kind not in BEHAVIOR_KINDS:
        # design/nfr/evaluation/agent-authority live outside the Gherkin corpus.
        # They are carried through as declared rather than invented here.
        return {"ref": ref, "kind": kind, "slug": slug, "featureKey": feature_key,
                "resolved": False, "external": True}, []

    bucket = feat[kind]
    if slug not in bucket:
        return None, [_diag(
            "error", "dangling-ref",
            f"{ref!r} names {kind} {slug!r}, which feature {feature_key!r} does not declare. "
            f"A retired, split or merged identifier is never reused, so an old reference "
            f"dangles here by design — repoint it deliberately rather than guessing.",
            ref=ref, file=feat.get("sourcePath"), element=slug, **where,
        )]

    node = bucket[slug]
    if node is None:
        return None, [_diag(
            "error", "ambiguous-ref",
            f"{ref!r} resolves to more than one {kind} named {slug!r} in feature "
            f"{feature_key!r}.",
            ref=ref, file=feat.get("sourcePath"), element=slug, **where,
        )]

    diagnostics = []
    if node.get("idSource") == "derived":
        diagnostics.append(_diag(
            "warning", "derived-identity",
            f"{ref!r} resolves through an identifier derived from the element's name, which "
            f"changes when the name does. Readable, but it cannot be approved into an AIPOS "
            f"baseline until an explicit @{kind}:{slug} tag is authored.",
            ref=ref, file=node.get("file"), element=slug, **where,
        ))

    return {
        "ref": ref, "kind": kind, "slug": slug, "featureKey": feature_key,
        "name": node.get("rule") if kind == "rule" else node.get("name"),
        "idSource": node.get("idSource"), "file": node.get("file"),
        "line": node.get("line"), "tags": node.get("tags") or [],
        "resolved": True, "external": False,
    }, diagnostics


# ------------------------------------------------------------------ workflow

def validate_workflow(workflow):
    """Structural checks on the workflow itself, before any reference is touched."""
    diagnostics = []

    version = workflow.get("version")
    if version not in SUPPORTED_VERSIONS:
        supported = ", ".join(str(v) for v in SUPPORTED_VERSIONS)
        return [_diag(
            "error", "unsupported-version",
            f"Workflow version {version!r} is not supported by this build "
            f"(understands {supported}). A newer workflow is newer, not malformed.",
        )]

    actor_ids = {a.get("id") for a in workflow.get("actors") or []}
    activities = workflow.get("activities") or []
    seen = set()

    for act in activities:
        aid = act.get("id")
        if aid in seen:
            diagnostics.append(_diag(
                "error", "duplicate-activity-id",
                f"Activity id {aid!r} is used more than once. Step ids are what the baseline "
                f"and the map both point at, so they cannot repeat.",
                activity=aid,
            ))
        seen.add(aid)

        if act.get("actor") and act["actor"] not in actor_ids:
            diagnostics.append(_diag(
                "error", "unknown-actor",
                f"Activity {aid!r} names actor {act['actor']!r}, which is not declared.",
                activity=aid,
            ))

        step_ids = set()
        for step in act.get("steps") or []:
            sid = step.get("id")
            if sid in step_ids:
                diagnostics.append(_diag(
                    "error", "duplicate-step-id",
                    f"Step id {sid!r} is used more than once in activity {aid!r}.",
                    activity=aid, step=sid,
                ))
            step_ids.add(sid)
            for role in ("actor",):
                if step.get(role) and step[role] not in actor_ids:
                    diagnostics.append(_diag(
                        "error", "unknown-actor",
                        f"Step {sid!r} names actor {step[role]!r}, which is not declared.",
                        activity=aid, step=sid,
                    ))

    for act in activities:
        for edge in act.get("next") or []:
            target = edge.get("to")
            if target not in seen:
                diagnostics.append(_diag(
                    "error", "dangling-transition",
                    f"Activity {act.get('id')!r} transitions to {target!r}, which is not an "
                    f"activity in this workflow.",
                    activity=act.get("id"),
                ))

    return diagnostics


def resolve(workflow, features):
    """Resolve `workflow` against ingested `features`.

    Returns `{"workflow", "views": {"l1","l2","l3"}, "diagnostics", "ok"}`.
    `ok` is true only when no diagnostic is an error — warnings (a derived
    identifier, say) do not make a workflow unusable, they make it
    un-approvable, which is a different thing decided elsewhere.
    """
    diagnostics = list(validate_workflow(workflow))
    if any(d["code"] == "unsupported-version" for d in diagnostics):
        return {"workflow": workflow.get("workflow_key"), "views": {}, "ok": False,
                "diagnostics": diagnostics}

    index, corpus_diags = index_corpus(features)
    diagnostics.extend(corpus_diags)

    activities = []
    for act in workflow.get("activities") or []:
        where = {"activity": act.get("id")}
        behavior, design = [], []

        for ref in act.get("behavior") or []:
            got, ds = resolve_ref(ref, index, where=where)
            diagnostics.extend(ds)
            if got:
                behavior.append(got)

        for ref in act.get("design") or []:
            got, ds = resolve_ref(ref, index, where=where)
            diagnostics.extend(ds)
            if got:
                design.append(got)

        steps = []
        for step in act.get("steps") or []:
            sw = {"activity": act.get("id"), "step": step.get("id")}
            step_behavior = []
            for ref in step.get("behavior") or []:
                got, ds = resolve_ref(ref, index, where=sw)
                diagnostics.extend(ds)
                if got:
                    step_behavior.append(got)
            steps.append({**{k: v for k, v in step.items() if k != "behavior"},
                          "behavior": step_behavior})

        activities.append({**{k: v for k, v in act.items()
                              if k not in ("behavior", "design", "steps")},
                           "steps": steps, "behavior": behavior, "design": design})

    resolved = {**workflow, "activities": activities}
    return {
        "workflow": workflow.get("workflow_key"),
        "views": {"l1": view_l1(resolved), "l2": view_l2(resolved), "l3": view_l3(resolved)},
        "diagnostics": diagnostics,
        "ok": not any(d["level"] == "error" for d in diagnostics),
    }


# ------------------------------------------------------------------ views

def view_l1(resolved):
    """L1 — the customer journey. Activities, order, and who owns each.

    No system internals and no Gherkin: this is the view someone outside the
    team can read.
    """
    return {
        "outcome": resolved.get("outcome"),
        "actors": resolved.get("actors") or [],
        "activities": [
            {"id": a.get("id"), "name": a.get("name"), "actor": a.get("actor"),
             "next": a.get("next") or []}
            for a in resolved["activities"]
        ],
    }


def view_l2(resolved):
    """L2 — human / system / tool collaboration inside each activity.

    Adds the steps and the handoffs between actors. A handoff is where work
    changes hands, which is where most real defects live.
    """
    out = []
    for a in resolved["activities"]:
        steps = [{"id": s.get("id"), "name": s.get("name"), "actor": s.get("actor"),
                  "kind": s.get("kind"), "handoff": s.get("handoff")}
                 for s in a["steps"]]
        out.append({"id": a.get("id"), "name": a.get("name"), "actor": a.get("actor"),
                    "next": a.get("next") or [], "steps": steps})
    return {"outcome": resolved.get("outcome"), "activities": out}


def view_l3(resolved):
    """L3 — the behavior governing each step, by reference.

    Every entry points at canonical Gherkin. A Rule referenced from several
    activities appears once per reference here and exactly once in the corpus;
    `referencedBy` makes that reuse visible instead of looking like duplication.
    """
    referenced_by = {}
    for a in resolved["activities"]:
        for b in a["behavior"]:
            referenced_by.setdefault(b["ref"], []).append(a.get("id"))
        for s in a["steps"]:
            for b in s["behavior"]:
                referenced_by.setdefault(b["ref"], []).append(f"{a.get('id')}.{s.get('id')}")

    return {
        "outcome": resolved.get("outcome"),
        "activities": [
            {"id": a.get("id"), "name": a.get("name"),
             "behavior": a["behavior"], "design": a["design"],
             "steps": [{"id": s.get("id"), "name": s.get("name"), "behavior": s["behavior"]}
                       for s in a["steps"]]}
            for a in resolved["activities"]
        ],
        "referencedBy": referenced_by,
    }


# ------------------------------------------------------------------ cli

def main():
    if len(sys.argv) != 3:
        print("usage: workflow_resolve.py <workflow.json> <features.json>", file=sys.stderr)
        return 2
    workflow = json.load(open(sys.argv[1], encoding="utf-8"))
    features = json.load(open(sys.argv[2], encoding="utf-8"))
    result = resolve(workflow, features)
    json.dump(result, sys.stdout, indent=2)
    print()
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
