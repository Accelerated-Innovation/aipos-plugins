#!/usr/bin/env python3
"""
Ingest repo-resident feature specs into the features.json contract.

Teams that keep Gherkin under version control rather than pasting it into a tracker
have made a defensible call -- two copies of a spec drift. But it leaves Product and
QA unable to review the spec where they work, and leaves a feature map with nothing
to score. This adapter reads the repo directly so those features get a real verdict
instead of a "not assessable" zero.

Expected layout (both shapes work):

    <root>/                          <root>/
      <epic>/                          features/
        <feature>/                       <feature>/
          acceptance.feature               acceptance.feature
          nfrs.md                          nfrs.md
          eval_criteria.yaml               eval_criteria.yaml
          feature_source.md                feature_source.md

A directory is treated as a feature when it contains at least one *.feature file or a
feature_source.md. The artifact names are the ones govkit-feature-refine already
declares in its Inputs section, so a repo laid out for refinement needs no changes.

Gherkin is parsed with gherkin-official, the Cucumber team's own parser (MIT). Install it
before running:

    python -m pip install -r requirements.txt

Exit codes: 0 fine, 1 nothing found, 2 the parser is not installed, 3 one or more
.feature files failed to parse (features.json is still written; the failed files
contribute no scenarios, and the diagnostics name file, line and column on stderr).

Usage:
    python repo_ingest.py <root> [-o features.json] [--epic AI-123] [--key-from dir|feature]
    python repo_ingest.py <root> --merge tracker.json -o features.json
"""

import argparse
import json
import os
import re
import sys

FEATURE_EXT = ".feature"
SOURCE_NAMES = ("feature_source.md", "source.md", "README.md")
NFR_NAMES = ("nfrs.md", "nfr.md")
EVAL_NAMES = ("eval_criteria.yaml", "eval_criteria.yml", "evals.yaml", "evals.yml")

KEY_RE = re.compile(r"\b([A-Z][A-Z0-9]+-\d+)\b")
DIR_KEY_RE = re.compile(r"^([a-zA-Z]+)(\d+)[_-]")


# ---------------------------------------------------------------- gherkin

def _load_parser():
    """Import the official Cucumber Gherkin parser, or explain how to get it.

    Hand-rolled line scanning is what this replaced. It could not see Background
    scoping, Examples tables, step data tables, doc strings or tag inheritance, and it
    turned malformed Gherkin into a plausible-looking partial feature. A maintained
    parser is the only way the ingested record can mean the same thing the .feature
    file means.
    """
    try:
        from gherkin.parser import Parser  # noqa: PLC0415
        from gherkin.errors import CompositeParserException  # noqa: PLC0415
    except ImportError:
        sys.stderr.write(
            "repo_ingest requires the official Gherkin parser (MIT, Cucumber team).\n"
            "Install it with:\n"
            "    python -m pip install -r "
            + os.path.join(os.path.dirname(os.path.abspath(__file__)), "requirements.txt")
            + "\n"
            "or:  python -m pip install 'gherkin-official>=32,<40'\n"
        )
        raise SystemExit(2)
    return Parser, CompositeParserException


ID_TAG_PREFIXES = {"rule": "@rule:", "scenario": "@scenario:"}
OUTLINE_KEYWORDS = ("Scenario Outline", "Scenario Template")


def slugify(name):
    """Derive a stable-ish identifier from a name. Stable only while the name is --
    which is the argument for authoring explicit @rule:/@scenario: tags. See
    ../../../references/spec-identifiers.md."""
    s = re.sub(r"[^A-Za-z0-9]+", "-", (name or "").strip()).strip("-").lower()
    return s or "unnamed"


def tag_names(nodes):
    """Tag names verbatim, in source order, including the leading @."""
    return [t["name"] for t in nodes or []]


def identity(kind, tags, name):
    """(id, idSource) for a rule or scenario. An explicit @rule:/@scenario: tag is the
    authored identity; otherwise the name is slugified and marked derived so a consumer
    can tell the difference."""
    prefix = ID_TAG_PREFIXES[kind]
    for t in tags:
        if t.lower().startswith(prefix):
            slug = t[len(prefix):].strip()
            if slug:
                return slug, "tag"
    return slugify(name), "derived"


def _table(rows):
    """A Gherkin table as a list of rows of cell values."""
    return [[c["value"] for c in r.get("cells") or []] for r in rows or []]


def _steps(step_nodes):
    """Both step renderings: the flat strings downstream already reads, and the
    structured detail (data tables, doc strings, source lines) it could not see."""
    flat, detail = [], []
    for st in step_nodes or []:
        kw = st.get("keyword") or ""
        text = st.get("text") or ""
        flat.append((kw + text).strip())
        d = {"keyword": kw.strip(), "text": text,
             "line": (st.get("location") or {}).get("line")}
        if st.get("dataTable"):
            d["dataTable"] = _table(st["dataTable"].get("rows"))
        if st.get("docString"):
            ds = st["docString"]
            d["docString"] = {"content": ds.get("content", ""),
                              "mediaType": ds.get("mediaType") or ""}
        detail.append(d)
    return flat, detail


def _background(node, file_name):
    if not node:
        return None
    flat, detail = _steps(node.get("steps"))
    return {"name": node.get("name") or "", "file": file_name,
            "line": (node.get("location") or {}).get("line"),
            "steps": flat, "stepDetails": detail}


def _examples(nodes):
    """Examples blocks, header and body preserved. The body row count is the number of
    executable examples the outline expands to -- a different number from the one
    authored scenario a person reviews, and both are worth keeping."""
    out = []
    for ex in nodes or []:
        header = [c["value"] for c in (ex.get("tableHeader") or {}).get("cells") or []]
        out.append({
            "name": ex.get("name") or "",
            "tags": tag_names(ex.get("tags")),
            "line": (ex.get("location") or {}).get("line"),
            "header": header,
            "rows": _table(ex.get("tableBody")),
        })
    return out


def _scenario(node, inherited, file_name):
    own = tag_names(node.get("tags"))
    keyword = (node.get("keyword") or "Scenario").strip()
    examples = _examples(node.get("examples"))
    is_outline = keyword in OUTLINE_KEYWORDS or bool(examples)
    flat, detail = _steps(node.get("steps"))
    name = node.get("name") or ""
    sid, isrc = identity("scenario", own, name)
    # `tags` stays the scenario's own tags: that is the field every existing consumer
    # reads. Inheritance is real Gherkin semantics, so it is preserved too -- in its own
    # field, and in `effectiveTags`, which is what a --tags filter would actually match.
    effective = list(inherited) + [t for t in own if t not in inherited]
    return {
        "name": name,
        "id": sid,
        "idSource": isrc,
        "type": "scenario_outline" if is_outline else "scenario",
        "keyword": keyword,
        "file": file_name,
        "line": (node.get("location") or {}).get("line"),
        "tags": own,
        "inheritedTags": list(inherited),
        "effectiveTags": effective,
        "steps": flat,
        "stepDetails": detail,
        "examples": examples,
        "exampleCount": (sum(len(x["rows"]) for x in examples) if is_outline else 1),
    }


def _new_rule(name, tags, line, file_name, description=""):
    rid, isrc = identity("rule", tags, name)
    return {"rule": name, "id": rid, "idSource": isrc, "tags": tags,
            "file": file_name, "line": line, "description": description,
            "background": None, "scenarios": []}


def parse_feature_file(text, file_name="acceptance.feature"):
    """Parse one .feature file with the official Cucumber parser.

    Returns (title, description, rules, meta). `meta` carries what the flat rules list
    cannot: feature tags and description, the feature-level Background, the source
    language, and any parse errors.

    Scenarios are grouped under the Rule: they belong to. Scenarios written outside any
    Rule: land under a single unnamed rule -- deliberate, so the rubric's rule-coverage
    dimension marks the missing grouping instead of the adapter inventing rules the
    author never wrote. A Rule: with no scenarios is kept, because a declared rule with
    no example is exactly the coverage gap a reviewer needs to see.

    On a syntax error nothing is returned from the failed file except the diagnostics.
    A partial feature that looks complete is worse than an empty one that says why.
    """
    Parser, CompositeParserException = _load_parser()
    meta = {"featureTags": [], "featureDescription": "", "featureLine": None,
            "language": "", "background": None, "errors": []}
    try:
        doc = Parser().parse(text)
    except CompositeParserException as exc:
        for err in exc.errors:
            loc = getattr(err, "location", None) or {}
            meta["errors"].append({
                "file": file_name,
                "line": loc.get("line"),
                "column": loc.get("column"),
                "message": str(err).strip(),
            })
        return "", "", [], meta
    except Exception as exc:  # noqa: BLE001 - any parser failure is a diagnostic
        meta["errors"].append({"file": file_name, "line": None, "column": None,
                               "message": f"{type(exc).__name__}: {exc}"})
        return "", "", [], meta

    feature = (doc or {}).get("feature")
    if not feature:
        meta["errors"].append({"file": file_name, "line": None, "column": None,
                               "message": "no Feature: found in this file"})
        return "", "", [], meta

    ftags = tag_names(feature.get("tags"))
    meta["featureTags"] = ftags
    meta["featureLine"] = (feature.get("location") or {}).get("line")
    meta["language"] = feature.get("language") or ""
    description = (feature.get("description") or "").strip()
    meta["featureDescription"] = description

    rules, ungrouped = [], None
    for child in feature.get("children") or []:
        if "background" in child:
            meta["background"] = _background(child["background"], file_name)
        elif "rule" in child:
            rn = child["rule"]
            rtags = tag_names(rn.get("tags"))
            rule = _new_rule(rn.get("name") or "", rtags,
                             (rn.get("location") or {}).get("line"), file_name,
                             (rn.get("description") or "").strip())
            inherited = ftags + [t for t in rtags if t not in ftags]
            for rc in rn.get("children") or []:
                if "background" in rc:
                    rule["background"] = _background(rc["background"], file_name)
                elif "scenario" in rc:
                    rule["scenarios"].append(
                        _scenario(rc["scenario"], inherited, file_name))
            rules.append(rule)
        elif "scenario" in child:
            if ungrouped is None:
                ungrouped = _new_rule("", [], None, file_name)
                rules.append(ungrouped)
            ungrouped["scenarios"].append(_scenario(child["scenario"], ftags, file_name))

    # A single squashed description line, for the card lede. Kept for compatibility with
    # the previous parser, which folded the feature description into one string.
    desc_line = " ".join(x.strip() for x in description.splitlines() if x.strip())
    return feature.get("name") or "", desc_line, rules, meta


# ---------------------------------------------------------------- nfrs

NFR_ROW = re.compile(r"^\|(.+)\|\s*$")


def parse_nfrs(text):
    """Read an NFR markdown table. Columns are matched by header name, so column
    order does not matter and unknown columns are ignored."""
    rows, headers = [], None
    for raw in text.splitlines():
        m = NFR_ROW.match(raw.strip())
        if not m:
            continue
        cells = [c.strip() for c in m.group(1).split("|")]
        if set("".join(cells)) <= set("-: "):
            continue
        if headers is None:
            headers = [c.lower() for c in cells]
            continue
        row = dict(zip(headers, cells))

        def pick(*names, default=""):
            for n in names:
                for h, v in row.items():
                    if n in h:
                        return v
            return default

        nfr = {
            "id": pick("id", "#", default=f"N{len(rows)+1}"),
            "dim": pick("dimension", "dim", "category", "area"),
            "req": pick("requirement", "req", "constraint", "description"),
            "threshold": pick("threshold", "target", "value"),
            "evidence": pick("evidence", "proof", "artifact"),
            "gap": pick("gap", "note", "status"),
        }
        if any(nfr[k] for k in ("dim", "req")):
            rows.append(nfr)
    return rows


def parse_evals(text):
    """Read eval criteria from YAML if available, otherwise fall back to a shallow
    parse so a missing PyYAML does not silently drop the whole evidence contract."""
    try:
        import yaml  # noqa: PLC0415

        data = yaml.safe_load(text) or {}
        items = data.get("evaluation_criteria") or data.get("evals") or data
        if isinstance(items, dict):
            items = [dict(v, id=k) if isinstance(v, dict) else {"id": k, "type": str(v)}
                     for k, v in items.items()]
        out = []
        for it in items or []:
            if not isinstance(it, dict):
                continue
            out.append({
                "id": str(it.get("id", "")),
                "type": str(it.get("type", "")),
                "rule_link": str(it.get("rule_link", it.get("rule", ""))),
                "method": str(it.get("method", "")),
                "pass_threshold": str(it.get("pass_threshold", it.get("threshold", ""))),
                "gate": str(it.get("gate", "")),
            })
        return out
    except ImportError:
        print("  note: PyYAML unavailable, eval_criteria parsed shallowly", file=sys.stderr)
        out, cur = [], None
        for raw in text.splitlines():
            s = raw.strip()
            if s.startswith("- "):
                if cur:
                    out.append(cur)
                cur = {"id": "", "type": "", "rule_link": "", "method": "",
                       "pass_threshold": "", "gate": ""}
                s = s[2:].strip()
            if cur is not None and ":" in s:
                k, v = s.split(":", 1)
                k = k.strip().lower()
                if k in cur:
                    cur[k] = v.strip().strip("'\"")
        if cur:
            out.append(cur)
        return out


# ---------------------------------------------------------------- source md

SECTION = re.compile(r"^#{1,4}\s*(.+?)\s*$")


def kebab(name):
    """Normalize an artifact name to kebab-case so `produces` and `consumes` match
    string-for-string across features. `Context Pack`, `context_pack` and
    `context-pack` are the same artifact; a chain that silently drops the edge
    because two features spelled it differently is worse than no chain."""
    s = re.sub(r"[`*]", "", name.strip())
    s = re.sub(r"\s*[—–-]\s.*$", "", s)  # drop trailing " — description" clauses
    s = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "-", s)  # camelCase boundary
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()
    return s


def parse_source(text):
    """Pull intent, scope, out of scope, open questions, DoD, and the artifact
    flow (produces/consumes) out of a source markdown file by heading name.
    Headings are matched loosely because teams name them differently and a strict
    match would silently drop real content."""
    out = {"userContext": "", "scope": [], "outOfScope": [],
           "openQuestions": [], "dod": [], "privacy": "",
           "produces": [], "consumes": []}
    # Order matters: "out of scope" also contains "scope", so the more specific
    # bucket has to be tested first or every exclusion lands in the scope list.
    buckets = {
        "outOfScope": ("out of scope", "not in scope", "out-of-scope", "excluded", "deferred"),
        "scope": ("in scope", "functional scope", "scope"),
        "openQuestions": ("open question", "question", "unresolved", "decision needed"),
        "dod": ("definition of done", "done when", "dod", "acceptance evidence"),
        # Structured artifact flow (govkit-feature-create writes these sections);
        # kept to exact section names so prose "dependencies" never becomes a
        # phantom chain edge.
        "produces": ("produces",),
        "consumes": ("consumes",),
    }
    prose = {
        "userContext": ("user context", "intent", "user story", "why", "purpose", "outcome"),
        "privacy": ("privacy", "confidential", "data handling"),
    }

    cur, cur_prose = None, None
    for raw in text.splitlines():
        m = SECTION.match(raw)
        if m:
            h = m.group(1).lower()
            cur = cur_prose = None
            for k, names in buckets.items():
                if any(n in h for n in names):
                    cur = k
                    break
            else:
                for k, names in prose.items():
                    if any(n in h for n in names):
                        cur_prose = k
                        break
            continue
        s = raw.strip()
        if not s:
            continue
        if cur and s.startswith(("- ", "* ", "+ ")):
            out[cur].append(s[2:].strip())
        elif cur and re.match(r"^\d+[.)]\s", s):
            out[cur].append(re.sub(r"^\d+[.)]\s*", "", s))
        elif cur_prose:
            out[cur_prose] += (" " if out[cur_prose] else "") + s
    return out


# ---------------------------------------------------------------- walk

def derive_key(dirname, feature_title, source_text, mode, epic):
    if mode == "feature":
        m = KEY_RE.search(feature_title or "")
        if m:
            return m.group(1)
    m = KEY_RE.search(dirname)
    if m:
        return m.group(1)
    m = DIR_KEY_RE.match(dirname)
    if m:
        return f"{m.group(1).upper()}-{m.group(2)}"
    m = KEY_RE.search(source_text[:400]) if source_text else None
    if m:
        return m.group(1)
    return f"{epic or 'FEATURE'}-{dirname}"


def read_first(d, names):
    for n in names:
        p = os.path.join(d, n)
        if os.path.isfile(p):
            return open(p, encoding="utf-8", errors="replace").read()
    return ""


def ingest_dir(d, mode, epic):
    files = os.listdir(d)
    fpaths = sorted(f for f in files if f.endswith(FEATURE_EXT))
    src = read_first(d, SOURCE_NAMES)
    if not fpaths and not src:
        return None

    title, desc, rules = "", "", []
    feature_tags, backgrounds, parse_errors = [], [], []
    language = ""
    for f in fpaths:
        t, dsc, r, fmeta = parse_feature_file(
            open(os.path.join(d, f), encoding="utf-8", errors="replace").read(),
            file_name=f,
        )
        title = title or t
        desc = desc or dsc
        rules.extend(r)
        parse_errors.extend(fmeta["errors"])
        language = language or fmeta["language"]
        for tg in fmeta["featureTags"]:
            if tg not in feature_tags:
                feature_tags.append(tg)
        if fmeta["background"]:
            backgrounds.append(fmeta["background"])

    name = os.path.basename(d.rstrip("/"))
    meta = parse_source(src) if src else {
        "userContext": "", "scope": [], "outOfScope": [],
        "openQuestions": [], "dod": [], "privacy": "",
        "produces": [], "consumes": [],
    }
    nfr = parse_nfrs(read_first(d, NFR_NAMES))
    evals = parse_evals(read_first(d, EVAL_NAMES))

    feat = {
        "key": derive_key(name, title, src, mode, epic),
        "title": title or name.replace("_", " ").replace("-", " ").title(),
        "source": "repo",
        "sourcePath": d,
        "status": "",
        "workstream": "",
        "phases": [],
        "clientVisible": False,
        "consumes": [kebab(x) for x in meta["consumes"] if kebab(x)],
        "produces": [kebab(x) for x in meta["produces"] if kebab(x)],
        "userContext": meta["userContext"] or desc,
        "scope": meta["scope"],
        "outOfScope": meta["outOfScope"],
        "rules": rules,
        "ruleCount": len(rules),
        # scenarioCount is the authored count -- one Scenario Outline is one scenario a
        # person reviews. exampleCount is what a runner executes, expanding each outline
        # over its Examples rows. Conflating the two flatters or penalises outlines.
        "scenarioCount": sum(len(r["scenarios"]) for r in rules),
        "exampleCount": sum(sc.get("exampleCount", 1)
                            for r in rules for sc in r["scenarios"]),
        "featureTags": feature_tags,
        "language": language,
        "background": backgrounds[0] if backgrounds else None,
        "backgrounds": backgrounds,
        "parseErrors": parse_errors,
        "nfr": nfr,
        "nfrTbd": [n for n in nfr if "TBD" in (n.get("threshold") or "").upper()
                   or not (n.get("threshold") or "").strip()],
        "evals": evals,
        "openQuestions": meta["openQuestions"],
        "dod": meta["dod"],
        "privacy": meta["privacy"],
    }
    if parse_errors:
        # A file that did not parse contributes no rules at all. Say so on the card
        # rather than letting a partial parse read as a thin spec -- the two need very
        # different responses, and only one of them is the author's fault.
        where = "; ".join(
            "{}:{}{}".format(x["file"], x["line"] or "?",
                             ":" + str(x["column"]) if x.get("column") else "")
            for x in parse_errors[:3])
        feat["specNote"] = (
            "Gherkin did not parse; no scenarios were ingested from the failed file(s). "
            "Fix the syntax at " + where +
            ("" if len(parse_errors) <= 3 else " (+%d more)" % (len(parse_errors) - 3)))
    return feat


def walk(root, mode, epic):
    found = []
    for dirpath, dirnames, _ in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith((".", "__", "node_modules"))]
        f = ingest_dir(dirpath, mode, epic)
        if f:
            found.append(f)
            dirnames[:] = []  # a feature dir does not contain nested features
    return sorted(found, key=lambda x: x["key"])


# ---------------------------------------------------------------- merge

MERGE_PREFER_REPO = ("rules", "ruleCount", "scenarioCount", "exampleCount",
                     "featureTags", "background", "backgrounds", "language",
                     "parseErrors", "nfr", "nfrTbd", "evals")


def merge(tracker, repo):
    """Overlay repo specs onto tracker records, keyed by feature key.

    The tracker owns status, workstream, phase and ownership -- things a repo does
    not know. The repo owns the spec itself. The artifact chain (consumes/produces)
    can come from either: tracker labels take precedence, and a repo package's
    Produces/Consumes sections fill in where the tracker is silent. Where a tracker
    record is empty and the repo has content, the repo wins; that is the whole point.
    """
    by_key = {f["key"]: f for f in tracker}
    for r in repo:
        t = by_key.get(r["key"])
        if t is None:
            by_key[r["key"]] = r
            continue
        for k in MERGE_PREFER_REPO:
            if r.get(k):
                t[k] = r[k]
        for k, v in r.items():
            if k in MERGE_PREFER_REPO or k == "key":
                continue
            if v and not t.get(k):
                t[k] = v
        t["source"] = "tracker+repo"
        t["sourcePath"] = r.get("sourcePath", "")
    return sorted(by_key.values(), key=lambda x: x["key"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("-o", "--out", default="features.repo.json")
    ap.add_argument("--epic", default="")
    ap.add_argument("--key-from", choices=["dir", "feature"], default="dir")
    ap.add_argument("--merge", help="tracker features.json to overlay these specs onto")
    a = ap.parse_args()

    if not os.path.isdir(a.root):
        print(f"not a directory: {a.root}")
        return 2

    feats = walk(a.root, a.key_from, a.epic)
    if not feats:
        print(f"no feature directories found under {a.root}")
        print("expected a dir containing *.feature or feature_source.md")
        return 1

    if a.merge:
        feats = merge(json.load(open(a.merge)), feats)

    json.dump(feats, open(a.out, "w"), indent=1, ensure_ascii=False)
    print(f"{len(feats)} feature(s) -> {a.out}")
    for f in feats:
        flag = "" if f.get("ruleCount") else "   <- no Gherkin parsed"
        if f.get("parseErrors"):
            flag = f"   <- {len(f['parseErrors'])} parse error(s)"
        print(f"  {f['key']:<12} {f.get('ruleCount', 0):>2} rules  "
              f"{f.get('scenarioCount', 0):>3} scenarios  "
              f"{f.get('exampleCount', 0):>3} examples  {len(f.get('nfr') or []):>2} nfr  "
              f"{len(f.get('evals') or []):>2} evals  [{f.get('source', 'tracker')}]{flag}")

    # Diagnostics go to stderr with file:line:column so an editor or CI annotation can
    # jump straight to them. The output file is still written -- a corpus should not be
    # unmappable because one spec is malformed -- but the exit code says something is
    # wrong, so a pipeline can decide rather than silently rendering a hole.
    bad = [(f, e) for f in feats for e in f.get("parseErrors") or []]
    if bad:
        sys.stderr.write(f"\n{len(bad)} Gherkin parse error(s):\n")
        for f, err in bad:
            loc = f"{err['line'] or '?'}" + (f":{err['column']}" if err.get("column") else "")
            path = os.path.join(f.get("sourcePath") or "", err.get("file") or "")
            sys.stderr.write(f"  {path}:{loc}: {err['message']}\n")
        sys.stderr.write("No scenarios were ingested from the failed file(s).\n")
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
