#!/usr/bin/env python3
"""Join resolved workflows and the feature corpus into one journey graph.

The journey diagrams answer two questions a table cannot answer quickly:

  1. Which scenarios specify this journey?
  2. Which journeys are affected if this feature changes?

Both answers are computed here, in Python, and handed to the viewer as data.
The viewer lays the graph out and handles selection; it never decides what a
reference means, how coverage counts, or which journey uses what. Keeping
every fact on this side means every fact is tested, and the diagram cannot
disagree with the resolver or with the fallback tables.

Levels:

  L1  journeys and their activities, in customer order, with actors and the
      explicit handoffs recorded on steps
  L2  the Gherkin features and Rules each activity uses; a feature shared by
      several activities or journeys is one node with several edges
  L3  the scenarios under each Rule, with their steps, examples and source

Input is what already exists: `features.json` from repo_ingest.py and one or
more outputs of workflow_resolve.py. Nothing is resolved again here.

Read-only. It never edits a workflow or a spec and never invents an
identifier.
"""

import json
import sys

GRAPH_VERSION = 1

# Diagnostics that mean a reference was dropped from the resolved views. They
# still belong on the diagram, as unresolved nodes, so a broken reference is
# visible where it was written instead of silently disappearing.
DROPPED_REF_CODES = ("malformed-ref", "dangling-ref", "ambiguous-ref", "unparsed-feature")

UNRESOLVED_REASONS = {
    "foreign-source": "names another repository; not resolvable here",
    "non-gherkin-kind": "declared outside the Gherkin corpus",
    "malformed-ref": "not a qualified reference",
    "dangling-ref": "names behavior the corpus does not declare",
    "ambiguous-ref": "matches more than one element",
    "unparsed-feature": "its feature has Gherkin that does not parse",
}


class JourneyGraphError(ValueError):
    """The inputs cannot form one graph (for example, two journeys share a key)."""


def _feature_id(source, key):
    return f"f:{source}/{key}" if source else f"f:{key}"


def _behavior_id(source, key, kind, slug):
    return f"{source}/{key}#{kind}:{slug}" if source else f"{key}#{kind}:{slug}"


def _source_path(feat, node, base_url):
    """Where the element lives, and a link only when a base URL was supplied.

    Without a base URL the location is shown as text. Guessing a link would
    send a reader to whatever that path holds today, not to what was rendered.
    """
    file = node.get("file")
    if not file:
        return None
    prefix = (feat.get("sourcePath") or "").rstrip("/")
    path = f"{prefix}/{file}" if prefix else file
    out = {"path": path, "line": node.get("line")}
    if base_url:
        href = f"{base_url.rstrip('/')}/{path}"
        if node.get("line"):
            href += f"#L{node['line']}"
        out["href"] = href
    return out


def _steps(steps):
    return [{k: s[k] for k in ("keyword", "text", "line", "dataTable", "docString") if k in s}
            for s in steps or []]


# ------------------------------------------------------------------ corpus

def _corpus_nodes(features, source, base_url):
    """Every feature, Rule and scenario in the corpus, whether or not a journey
    uses it. Unused behavior is a finding, so it has to exist on the graph."""
    nodes, edges, rule_of = {}, [], {}

    for feat in features:
        key = feat.get("key") or ""
        fid = _feature_id(source, key)
        if fid in nodes:
            # Duplicate keys are the resolver's error to report; the graph keeps
            # the first record rather than merging two features into one card.
            continue
        rules = [r for r in feat.get("rules") or [] if r.get("id")]
        nodes[fid] = {
            "id": fid, "level": 2, "kind": "feature", "key": key,
            "name": feat.get("title") or key,
            "ruleCount": len(rules),
            "scenarioCount": sum(len([s for s in r.get("scenarios") or [] if s.get("id")])
                                 for r in rules),
            "partial": bool(feat.get("parseErrors")),
            "journeys": [], "activities": [],
        }
        background = (feat.get("background") or {}).get("stepDetails") \
            or [{"text": t} for t in (feat.get("background") or {}).get("steps") or []]

        for rule in rules:
            rid = _behavior_id(source, key, "rule", rule["id"])
            nodes[rid] = {
                "id": rid, "level": 2, "kind": "rule", "feature": fid,
                "slug": rule["id"], "name": rule.get("rule") or rule["id"],
                "description": rule.get("description") or "",
                "idSource": rule.get("idSource"),
                "source": _source_path(feat, rule, base_url),
                "refs": [],
            }
            edges.append({"source": fid, "target": rid, "kind": "contains"})
            rule_bg = (rule.get("background") or {}).get("stepDetails") or []

            for sc in rule.get("scenarios") or []:
                if not sc.get("id"):
                    continue
                sid = _behavior_id(source, key, "scenario", sc["id"])
                rule_of[sid] = rid
                nodes[sid] = {
                    "id": sid, "level": 3, "kind": "scenario", "feature": fid, "rule": rid,
                    "slug": sc["id"], "name": sc.get("name") or sc["id"],
                    "type": sc.get("type"), "tags": sc.get("tags") or [],
                    "idSource": sc.get("idSource"),
                    "background": _steps(background) + _steps(rule_bg),
                    "steps": _steps(sc.get("stepDetails"))
                    or [{"text": t} for t in sc.get("steps") or []],
                    "examples": [{k: ex[k] for k in ("name", "tags", "header", "rows", "line")
                                  if k in ex} for ex in sc.get("examples") or []],
                    "exampleCount": sc.get("exampleCount"),
                    "source": _source_path(feat, sc, base_url),
                    "refs": [],
                }
                edges.append({"source": rid, "target": sid, "kind": "contains"})
    return nodes, edges, rule_of


# ------------------------------------------------------------------ journeys

def _journey_key(resolved):
    return resolved.get("workflow") or ""


def _refs_at(activity_l3):
    """(ref entry, step id or None) for every reference on an activity."""
    for b in (activity_l3.get("behavior") or []) + (activity_l3.get("design") or []):
        yield b, None
    for st in activity_l3.get("steps") or []:
        for b in st.get("behavior") or []:
            yield b, st.get("id")


def build(features, resolved_list, *, source_key=None, base_url=None):
    """Build the graph model from the corpus and N resolved workflows.

    `source_key` names the corpus. It defaults to the `sourceKey` the workflows
    were resolved against, and workflows that disagree about it are refused:
    binding one journey's references to another source's features would point
    at different behavior entirely.
    """
    resolved_list = list(resolved_list)
    keys = [_journey_key(r) for r in resolved_list]
    dupes = sorted({k for k in keys if keys.count(k) > 1})
    if dupes:
        raise JourneyGraphError(
            f"Two workflows share the key {', '.join(repr(d) for d in dupes)}. A journey is "
            f"identified by its workflow_key, so they cannot be told apart on one page. "
            f"Rename one, or render them separately.")

    declared = sorted({r.get("sourceKey") for r in resolved_list if r.get("sourceKey")})
    if len(declared) > 1:
        raise JourneyGraphError(
            f"These workflows were resolved against different sources ({', '.join(declared)}). "
            f"One page draws one corpus; render each source separately.")
    if source_key is None and declared:
        source_key = declared[0]

    nodes, edges, rule_of = _corpus_nodes(features, source_key, base_url)
    journeys, uses = [], {}
    scenarios_by_journey, activities_by_feature = {}, {}

    for r in resolved_list:
        jkey = _journey_key(r)
        views = r.get("views") or {}
        l1, l2, l3 = views.get("l1") or {}, views.get("l2") or {}, views.get("l3") or {}
        diags = r.get("diagnostics") or []
        cov = r.get("coverage") or {}
        actors = {a.get("id"): a for a in l1.get("actors") or []}
        jid = f"j:{jkey}"

        journeys.append({
            "id": jkey, "node": jid, "outcome": l1.get("outcome") or "",
            "ok": bool(r.get("ok")),
            "errors": sum(1 for d in diags if d.get("level") == "error"),
            "warnings": sum(1 for d in diags if d.get("level") != "error"),
            "coverage": {"covered": len(cov.get("covered") or []),
                         "uncovered": len(cov.get("uncovered") or []),
                         "partial": list(cov.get("partialFeatures") or [])},
        })
        nodes[jid] = {"id": jid, "level": 1, "kind": "journey", "journey": jkey,
                      "name": jkey, "outcome": l1.get("outcome") or ""}

        l2_by_id = {a.get("id"): a for a in l2.get("activities") or []}
        activities = l1.get("activities") or []
        ids = {a.get("id") for a in activities}
        targets = {x.get("to") for a in activities for x in a.get("next") or []}

        for a in activities:
            aid = f"j:{jkey}/a:{a.get('id')}"
            steps = (l2_by_id.get(a.get("id")) or {}).get("steps") or []
            actor = actors.get(a.get("actor"))
            nodes[aid] = {
                "id": aid, "level": 1, "kind": "activity", "journey": jkey,
                "activity": a.get("id"), "name": a.get("name") or a.get("id"),
                "actor": ({"id": actor.get("id"), "name": actor.get("name"),
                           "kind": actor.get("kind")} if actor
                          else ({"id": a.get("actor"), "name": a.get("actor"), "kind": None}
                                if a.get("actor") else None)),
                "steps": [{"id": s.get("id"), "name": s.get("name"),
                           "actor": s.get("actor"), "kind": s.get("kind")} for s in steps],
                # Handoffs come only from what a step records. Adjacent
                # activities with different actors are not evidence that work
                # changed hands, and inferring one would draw a defect site
                # nobody described.
                "handoffs": [{"step": s.get("id"), "stepName": s.get("name"),
                              "from": s["handoff"].get("from"), "to": s["handoff"].get("to")}
                             for s in steps if isinstance(s.get("handoff"), dict)],
            }
            if a.get("id") not in targets:
                edges.append({"source": jid, "target": aid, "kind": "starts"})
            for x in a.get("next") or []:
                to = x.get("to")
                edge = {"source": aid, "target": f"j:{jkey}/a:{to}", "kind": "next",
                        "condition": x.get("condition")}
                if to not in ids:
                    # A transition to nowhere stays visible, pointing at a stub
                    # that says so, rather than vanishing from the picture.
                    stub = f"j:{jkey}/missing:{to}"
                    nodes[stub] = {"id": stub, "level": 1, "kind": "missing", "journey": jkey,
                                   "name": str(to), "reason": "no such activity"}
                    edge["target"], edge["dangling"] = stub, True
                edges.append(edge)

        referenced = set()
        for a in l3.get("activities") or []:
            aid = f"j:{jkey}/a:{a.get('id')}"
            for b, step in _refs_at(a):
                where = {"journey": jkey, "activity": a.get("id"), "step": step}
                # A resolved reference is local by definition, so it is keyed
                # by this corpus's identity, not by whatever prefix it was
                # written with (a workflow with no source_key writes one anyway).
                bid = (_behavior_id(source_key, b.get("featureKey"), b.get("kind"), b.get("slug"))
                       if b.get("resolved") else None)
                if bid in nodes:
                    nodes[bid]["refs"].append(where)
                    referenced.add(bid)
                    fid = nodes[bid]["feature"]
                    uses.setdefault((aid, fid), []).append({"ref": bid, "step": step})
                    feat = nodes[fid]
                    if jkey not in feat["journeys"]:
                        feat["journeys"].append(jkey)
                    if aid not in feat["activities"]:
                        feat["activities"].append(aid)
                else:
                    _unresolved(nodes, edges, aid, b.get("ref"),
                                b.get("reason") or "dangling-ref", where)

        for d in diags:
            if d.get("code") in DROPPED_REF_CODES and "ref" in d and d.get("activity"):
                aid = f"j:{jkey}/a:{d['activity']}"
                _unresolved(nodes, edges, aid, d["ref"], d["code"],
                            {"journey": jkey, "activity": d["activity"], "step": d.get("step")})

        direct = sorted(b for b in referenced if nodes[b]["kind"] == "scenario")
        rules = {b for b in referenced if nodes[b]["kind"] == "rule"}
        under = sorted(s for s, rid in rule_of.items() if rid in rules and s not in referenced)
        scenarios_by_journey[jkey] = {"referenced": direct, "underReferencedRule": under}

    for (aid, fid), via in uses.items():
        edges.append({"source": aid, "target": fid, "kind": "uses", "via": via})
        activities_by_feature.setdefault(fid, []).append(aid)

    # Placement is computed once, across every journey on the page.
    #
    # `uncovered` keeps the resolver's meaning: nothing references the element
    # directly. A scenario under a referenced Rule is still uncovered -- naming
    # a Rule does not place every scenario beneath it -- but it gets its own
    # placement so the diagram can show it as "under a referenced rule" rather
    # than as behavior nobody connected to any journey.
    under_any = {s for v in scenarios_by_journey.values() for s in v["underReferencedRule"]}
    uncovered = []
    for n in nodes.values():
        if n["kind"] not in ("rule", "scenario"):
            continue
        if n["refs"]:
            n["placement"] = "referenced"
        else:
            n["placement"] = ("under-referenced-rule" if n["id"] in under_any
                              else "uncovered")
            uncovered.append(n["id"])

    return {
        "version": GRAPH_VERSION,
        "sourceKey": source_key,
        "journeys": journeys,
        "nodes": list(nodes.values()),
        "edges": edges,
        "index": {
            "scenariosByJourney": scenarios_by_journey,
            "journeysByFeature": {n["id"]: sorted(n["journeys"])
                                  for n in nodes.values() if n["kind"] == "feature"},
            "activitiesByFeature": {k: sorted(v) for k, v in activities_by_feature.items()},
        },
        "uncovered": sorted(uncovered),
    }


def _unresolved(nodes, edges, aid, ref, reason, where):
    """A reference that is not a link: a dashed node that says why."""
    label = ref if isinstance(ref, str) else json.dumps(ref)
    uid = f"x:{label}"
    if uid not in nodes:
        nodes[uid] = {"id": uid, "level": 2, "kind": "unresolved", "ref": label,
                      "reason": reason, "why": UNRESOLVED_REASONS.get(reason, "unresolved"),
                      "refs": []}
    nodes[uid]["refs"].append(where)
    if not any(e["source"] == aid and e["target"] == uid for e in edges):
        edges.append({"source": aid, "target": uid, "kind": "unresolved"})


# ------------------------------------------------------------------ cli

def main():
    if len(sys.argv) < 3:
        print("usage: journey_graph.py <features.json> <resolved.json> [<resolved.json> ...]",
              file=sys.stderr)
        return 2
    features = json.load(open(sys.argv[1], encoding="utf-8"))
    resolved = [json.load(open(p, encoding="utf-8")) for p in sys.argv[2:]]
    try:
        graph = build(features, resolved)
    except JourneyGraphError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    json.dump(graph, sys.stdout, indent=2, ensure_ascii=False)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
