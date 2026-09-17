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
    """Split a qualified reference, or return None when it is not one.

    Non-text values are *data* errors, not crashes: a number or an object in a
    behavior array is a malformed reference, and a resolver that raises on one
    takes the whole command down instead of reporting the one bad entry.
    """
    if not isinstance(ref, str):
        return None
    m = REF_RE.match(ref)
    return m.groupdict() if m else None


def resolve_ref(ref, index, *, where, source_key=None):
    """Resolve one qualified reference. Returns `(resolved_or_None, diagnostics)`.

    `source_key` is the identity of the corpus being resolved against. A
    reference naming a *different* source is not resolvable here and is never
    bound locally — see below. `where` locates the reference in every
    diagnostic, so a dangling link reports the activity that carries it rather
    than only the string that failed.
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

    source, feature_key = parts["source"], parts["feature"]
    kind, slug = parts["kind"], parts["slug"]

    if source_key is not None and source != source_key:
        # Behavior spanning applications is legitimate, and this corpus is not
        # the place it resolves. Binding it to a local feature that happens to
        # share a key would be the worst outcome available: a confident
        # `resolved: true` pointing at behavior from a different repository.
        return {"ref": ref, "kind": kind, "slug": slug, "featureKey": feature_key,
                "source": source, "resolved": False, "external": True,
                "reason": "foreign-source"}, [_diag(
            "warning", "foreign-source",
            f"{ref!r} names source {source!r}; this corpus is {source_key!r}. Carried through "
            f"unresolved — a cross-repository reference resolves where that source is "
            f"available, and binding it to a local feature with the same key would point at "
            f"different behavior entirely.",
            ref=ref, element=feature_key, **where,
        )]

    if kind not in BEHAVIOR_KINDS:
        # design / nfr / evaluation / agent-authority live outside the Gherkin
        # corpus, so their feature need not appear in it. Checked before the
        # corpus lookup: requiring a Gherkin feature for a Figma frame would
        # reject every valid design reference.
        return {"ref": ref, "kind": kind, "slug": slug, "featureKey": feature_key,
                "source": source, "resolved": False, "external": True,
                "reason": "non-gherkin-kind"}, []

    feat = index.get(feature_key)
    if feat is None:
        return None, [_diag(
            "error", "dangling-ref",
            f"{ref!r} names feature {feature_key!r}, which is not in the corpus.",
            ref=ref, element=feature_key, **where,
        )]

    bucket = feat[kind]
    node = bucket.get(slug)

    if slug not in bucket:
        # A parse failure elsewhere in the same feature directory is the likely
        # cause worth naming -- but only when the slug is actually missing.
        # Rejecting every reference into the feature (which an earlier version
        # did) hides behavior that ingested perfectly well from a sibling file.
        if feat["parseErrors"]:
            detail = _first_error(feat)
            return None, [_diag(
                "error", "unparsed-feature",
                f"{ref!r} names {kind} {slug!r}, which feature {feature_key!r} does not "
                f"declare — and that feature has Gherkin that does not parse ({detail}), so "
                f"the element may be in the file that failed. Fix the spec before concluding "
                f"the reference is wrong.",
                ref=ref, file=feat.get("sourcePath"), element=slug, **where,
            )]
        return None, [_diag(
            "error", "dangling-ref",
            f"{ref!r} names {kind} {slug!r}, which feature {feature_key!r} does not declare. "
            f"A retired, split or merged identifier is never reused, so an old reference "
            f"dangles here by design — repoint it deliberately rather than guessing.",
            ref=ref, file=feat.get("sourcePath"), element=slug, **where,
        )]

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
        "ref": ref, "kind": kind, "slug": slug, "featureKey": feature_key, "source": source,
        "name": node.get("rule") if kind == "rule" else node.get("name"),
        "idSource": node.get("idSource"), "file": node.get("file"),
        "line": node.get("line"), "tags": node.get("tags") or [],
        "resolved": True, "external": False,
    }, diagnostics


def _first_error(feat):
    first = feat["parseErrors"][0]
    return first.get("message", first) if isinstance(first, dict) else first


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
            if step.get("actor") and step["actor"] not in actor_ids:
                diagnostics.append(_diag(
                    "error", "unknown-actor",
                    f"Step {sid!r} names actor {step['actor']!r}, which is not declared.",
                    activity=aid, step=sid,
                ))

            # A handoff is where work changes hands, which is the thing L2
            # exists to show. Its endpoints are actors like any other, and an
            # unchecked one renders into the collaboration view looking exactly
            # as authoritative as a real one.
            handoff = step.get("handoff") or {}
            if isinstance(handoff, dict):
                for end in ("from", "to"):
                    who = handoff.get(end)
                    if who and who not in actor_ids:
                        diagnostics.append(_diag(
                            "error", "unknown-actor",
                            f"Step {sid!r} hands off {end} {who!r}, which is not a declared "
                            f"actor.",
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


def resolve(workflow, features, source_key=None):
    """Resolve `workflow` against ingested `features`.

    `source_key` identifies the corpus. It defaults to the workflow's own
    `source_key`, so a workflow states which repository its local references
    belong to and anything naming another source is carried through unresolved
    rather than bound to a local feature that happens to share a key.

    Returns `{"workflow", "views": {"l1","l2","l3"}, "diagnostics", "ok"}`.
    `ok` is true only when no diagnostic is an error — warnings (a derived
    identifier, say) do not make a workflow unusable, they make it
    un-approvable, which is a different thing decided elsewhere.
    """
    if source_key is None:
        source_key = workflow.get("source_key")

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
            got, ds = resolve_ref(ref, index, where=where, source_key=source_key)
            diagnostics.extend(ds)
            if got:
                behavior.append(got)

        for ref in act.get("design") or []:
            got, ds = resolve_ref(ref, index, where=where, source_key=source_key)
            diagnostics.extend(ds)
            if got:
                design.append(got)

        steps = []
        for step in act.get("steps") or []:
            sw = {"activity": act.get("id"), "step": step.get("id")}
            step_behavior = []
            for ref in step.get("behavior") or []:
                got, ds = resolve_ref(ref, index, where=sw, source_key=source_key)
                diagnostics.extend(ds)
                if got:
                    step_behavior.append(got)
            steps.append({**{k: v for k, v in step.items() if k != "behavior"},
                          "behavior": step_behavior})

        activities.append({**{k: v for k, v in act.items()
                              if k not in ("behavior", "design", "steps")},
                           "steps": steps, "behavior": behavior, "design": design})

    resolved = {**workflow, "activities": activities}
    cover = coverage(workflow, features, source_key)
    for entry in cover["uncovered"]:
        diagnostics.append(_diag(
            "warning", "uncovered-behavior",
            f"{entry['kind']} {entry['slug']!r} in feature {entry['featureKey']!r} is not "
            f"referenced by any activity or step. Legitimate if it belongs to another journey "
            f"— but unreferenced behavior is behavior this map implies does not exist.",
            file=entry.get("file"), element=entry["slug"],
        ))

    return {
        "workflow": workflow.get("workflow_key"),
        "views": {"l1": view_l1(resolved), "l2": view_l2(resolved), "l3": view_l3(resolved)},
        "coverage": cover,
        "diagnostics": diagnostics,
        "ok": not any(d["level"] == "error" for d in diagnostics),
    }


def coverage(workflow, features, source_key=None):
    """Which canonical behavior the workflow reaches, and which it does not.

    The resolver's other direction. Resolving asks "does every reference land
    somewhere"; coverage asks the question a reviewer actually has — "is there
    behavior in the corpus that no step in this journey touches".

    Uncovered behavior is a **finding, not an error**. A Rule may legitimately
    belong to a journey this workflow does not describe. What is not legitimate
    is nobody noticing: an unreferenced scenario is behavior the map silently
    implies does not exist.
    """
    referenced = set()
    for act in workflow.get("activities") or []:
        for ref in (act.get("behavior") or []) + (act.get("design") or []):
            if isinstance(ref, str):
                referenced.add(ref)
        for step in act.get("steps") or []:
            for ref in step.get("behavior") or []:
                if isinstance(ref, str):
                    referenced.add(ref)

    local = source_key if source_key is not None else workflow.get("source_key")
    covered, uncovered = [], []

    for feat in features:
        key = feat.get("key") or ""
        if feat.get("parseErrors"):
            # Its elements did not parse, so "uncovered" would be meaningless
            # — the resolver reports the parse failure separately.
            continue
        for rule in feat.get("rules") or []:
            for kind, node, name in (
                ("rule", rule, rule.get("rule")),
                *(("scenario", sc, sc.get("name")) for sc in rule.get("scenarios") or []),
            ):
                slug = node.get("id")
                if not slug:
                    continue
                ref = f"{local}/{key}#{kind}:{slug}" if local else None
                entry = {"ref": ref, "kind": kind, "slug": slug, "featureKey": key,
                         "name": name, "idSource": node.get("idSource"),
                         "file": node.get("file")}
                (covered if ref in referenced else uncovered).append(entry)

    return {"covered": covered, "uncovered": uncovered,
            "referencedNotInCorpus": sorted(
                r for r in referenced
                if (p := parse_ref(r)) and p["kind"] in BEHAVIOR_KINDS
                and not any(c["ref"] == r for c in covered))}


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
