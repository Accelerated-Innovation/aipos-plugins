#!/usr/bin/env python3
"""
Render a scored feature corpus into a single self-contained HTML feature map.

Inputs (see references/ingestion-contract.md for the full schema):
    features.json   required   the normalized corpus
    scores.json     optional   govkit-feature-refine batch verdicts, keyed by feature key
    sizing.json     optional   govkit-feature-slice verdicts AFTER compute_size.py --
                               only the computed file carries points/bands/rollups
    config.json     optional   title, lanes, boundary sets, explicit node positions

The map has three registers, and they answer different questions:
    the chain   -- how artifacts flow between features, and where readiness is weakest
    the lanes   -- what each workstream owns, one card per feature
    the ledger  -- every producer/consumer edge, in full

Usage:
    python render_map.py -f features.json -s scores.json -z sizing_computed.json \
                         -c config.json -o map.html
"""

import argparse
import html
import json
import os
import sys
from collections import defaultdict

e = lambda s: html.escape(str(s) if s is not None else "")

TOKCLS = {"Approved": "tok-ok", "Approved with edits": "tok-edit", "Blocked": "tok-block"}
SVGTOK = {"Approved": "ok", "Approved with edits": "edit", "Blocked": "block"}
PIP = {1.0: "1", 0.5: "h", 0.0: "0"}


# ------------------------------------------------------------------ layout

NW, NH = 200, 84
COLW, ROWH, PADX, PADY = 350, 140, 40, 84


def layer_nodes(feats):
    """Longest-path layering over the producer/consumer DAG.

    Longest path rather than shortest: a feature should sit to the right of
    everything it consumes, so the picture reads as 'what has to exist first'.
    Cycles are expected here -- a reviewed output re-entering an earlier stage is a
    real pattern, not a modelling error -- so the walk is depth-bounded rather than
    assuming acyclicity.
    """
    producers = defaultdict(list)
    for f in feats:
        for a in f.get("produces") or []:
            producers[a].append(f["key"])
    byk = {f["key"]: f for f in feats}

    depth, visiting = {}, set()

    def walk(k, guard=0):
        if k in depth:
            return depth[k]
        if k in visiting or guard > len(feats):
            return 0
        visiting.add(k)
        best = 0
        for a in byk[k].get("consumes") or []:
            for p in producers.get(a, []):
                if p != k:
                    best = max(best, walk(p, guard + 1) + 1)
        visiting.discard(k)
        depth[k] = best
        return best

    for f in feats:
        walk(f["key"])
    return depth


def auto_positions(feats, _per_row=None):
    """Layered placement: depth is the column, position within the layer is the row.

    Wrapping layers into fixed-width rows reads more compactly but sends edges
    backwards through the picture, which is worse than a tall column -- the whole
    point of the chain is that dependency runs one way. Columns it is.

    Rows within a layer are ordered by the average row of each node's producers, a
    single-pass barycentre that markedly reduces edge crossings for very little code.
    Auto-layout is for the first look; hand-set `positions` in config.json when the
    diagram is going in front of stakeholders.
    """
    depth = layer_nodes(feats)
    byk = {f["key"]: f for f in feats}
    producers = defaultdict(list)
    for f in feats:
        for a in f.get("produces") or []:
            producers[a].append(f["key"])

    cols = defaultdict(list)
    for f in sorted(feats, key=lambda x: x["key"]):
        cols[depth[f["key"]]].append(f["key"])

    row_of = {}
    for d in sorted(cols):
        keys = cols[d]
        if d > 0:
            def bary(k):
                ups = [row_of[p] for a in byk[k].get("consumes") or []
                       for p in producers.get(a, []) if p in row_of]
                return sum(ups) / len(ups) if ups else 99
            keys.sort(key=lambda k: (bary(k), k))
        for i, k in enumerate(keys):
            row_of[k] = i

    return {k: (PADX + depth[k] * COLW, PADY + row_of[k] * ROWH) for k in row_of}


def build_chain(feats, scores, cfg):
    pos = cfg.get("positions") or auto_positions(feats, cfg.get("perRow", 4))
    byk = {f["key"]: f for f in feats}
    central = set(cfg.get("central") or [])
    undecided = set(cfg.get("undecided") or [])

    width = max((x for x, _ in pos.values()), default=0) + NW + PADX
    height = max((y for _, y in pos.values()), default=0) + NH + 60

    producers = defaultdict(list)
    for f in feats:
        for a in f.get("produces") or []:
            producers[a].append(f["key"])

    edges, seen = [], set()
    for f in feats:
        for a in f.get("consumes") or []:
            for p in producers.get(a, []):
                if p == f["key"] or (p, f["key"], a) in seen:
                    continue
                seen.add((p, f["key"], a))
                edges.append((p, f["key"], a))

    def anchors(k):
        x, y = pos[k]
        return {"l": (x, y + NH / 2), "r": (x + NW, y + NH / 2),
                "t": (x + NW / 2, y), "b": (x + NW / 2, y + NH)}

    # Render at natural size and let the container scroll. Scaling a long chain down
    # to fit the page makes every label unreadable, which defeats the diagram; a
    # horizontal scrollbar is the lesser cost.
    s = [f'<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" '
         f'aria-label="Producer and consumer flow between features" class="spine" '
         f'style="width:{width}px;height:{height}px">']
    s.append('<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
             'markerHeight="7" orient="auto-start-reverse">'
             '<path d="M0,0 L10,5 L0,10 z" fill="#7C8493"/></marker>'
             '<marker id="ahb" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
             'markerHeight="7" orient="auto-start-reverse">'
             '<path d="M0,0 L10,5 L0,10 z" fill="#B06A0F"/></marker></defs>')

    drawn = []
    for a_key, b_key, art in edges:
        ax, ay = pos[a_key]
        bx, by = pos[b_key]
        back = bx < ax
        if abs(ay - by) < 4 and not back:
            p1, p2 = anchors(a_key)["r"], anchors(b_key)["l"]
            d = f"M{p1[0]},{p1[1]} C{p1[0]+52},{p1[1]} {p2[0]-52},{p2[1]} {p2[0]-9},{p2[1]}"
            mx, my = (p1[0] + p2[0]) / 2, p1[1] - 11
        elif back:
            p1, p2 = anchors(a_key)["l"], anchors(b_key)["r"]
            d = f"M{p1[0]},{p1[1]} C{p1[0]-52},{p1[1]} {p2[0]+52},{p2[1]} {p2[0]+9},{p2[1]}"
            mx, my = (p1[0] + p2[0]) / 2, p1[1] - 11
        else:
            p1, p2 = anchors(a_key)["b"], anchors(b_key)["t"]
            d = (f"M{p1[0]},{p1[1]} C{p1[0]},{p1[1]+50} {p2[0]},{p2[1]-50} "
                 f"{p2[0]},{p2[1]-9}")
            mx, my = (p1[0] + p2[0]) / 2 + 8, (p1[1] + p2[1]) / 2
        s.append(f'<path d="{d}" class="edge{" back" if back else ""}" '
                 f'marker-end="url(#{"ahb" if back else "ah"})"/>')
        drawn.append((art, mx, my, back))

    for k, (x, y) in pos.items():
        f = byk[k]
        cls = "undecided" if k in undecided else ("central" if k in central else "deployment")
        s.append(f'<a href="#{e(k)}"><g class="node {cls}">')
        s.append(f'<rect x="{x}" y="{y}" width="{NW}" height="{NH}" rx="5"/>')
        s.append(f'<text x="{x+13}" y="{y+21}" class="nk">{e(k)}</text>')
        sc = scores.get(k)
        if sc:
            c, w = SVGTOK[sc["decision"]], 38
            s.append(f'<rect x="{x+NW-11-w}" y="{y+9}" width="{w}" height="16" rx="3" '
                     f'class="tkbg t-{c}"/>')
            s.append(f'<text x="{x+NW-11-w/2}" y="{y+21}" class="tkt t-{c}">'
                     f'{sc["score"]:g}</text>')
        for j, line in enumerate(wrap_label(f.get("title", k))):
            s.append(f'<text x="{x+13}" y="{y+41+j*15}" class="nt">{e(line)}</text>')
        s.append(f'<text x="{x+13}" y="{y+74}" class="nm">'
                 f'{f.get("ruleCount",0)} rules &#183; {f.get("scenarioCount",0)} scenarios</text>')
        s.append("</g></a>")

    # Nudge colliding labels apart. An unreadable pile of overlapping artifact names
    # is worse than a slightly displaced one, and displacement still reads correctly
    # because each label sits on its own path.
    placed = []
    for art, mx, my, back in drawn:
        w, h = len(art) * 5.4, 13
        for attempt in range(9):
            off = ((attempt + 1) // 2) * 15 * (1 if attempt % 2 else -1)
            box = (mx - w / 2, my + off - h, mx + w / 2, my + off)
            if not any(not (box[2] < p[0] or p[2] < box[0]
                            or box[3] < p[1] or p[3] < box[1]) for p in placed):
                placed.append(box)
                my += off
                break
        else:
            placed.append((mx - w / 2, my - h, mx + w / 2, my))
        s.append(f'<text x="{mx}" y="{my}" class="elab{" backl" if back else ""}">{e(art)}</text>')
    s.append("</svg>")
    return "\n".join(s)


def wrap_label(t, width=24, maxlines=2):
    words, lines, cur = str(t).split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= width:
            cur = f"{cur} {w}".strip()
        else:
            lines.append(cur)
            cur = w
        if len(lines) == maxlines:
            break
    if cur and len(lines) < maxlines:
        lines.append(cur)
    if len(lines) == maxlines and len(" ".join(lines)) < len(str(t)):
        lines[-1] = lines[-1][: width - 1] + "…"
    return lines or [str(t)]


# ------------------------------------------------------------------ sizing

SLICE_TAGS = ("mvp", "v1", "v2")
SIZE_TAGS = ("small", "medium", "large")


def eff_tags(sc):
    """Tags that actually apply to a scenario: its own, plus any inherited from the
    Feature or the Rule. Gherkin says tags inherit, and a `--tags @mvp` run agrees; an
    ingest that only reported a scenario's own tags quietly under-reported the slice a
    team had declared one level up. Older features.json files carry only `tags`, so
    fall back to those."""
    return sc.get("effectiveTags") or sc.get("tags") or []


def scen_slice(sc):
    """The scenario's tagged release slice, or "". Tags are decisions the team made;
    only these drive grouping and filtering -- a batch recommendation never does.

    Most specific declaration wins: the scenario's own tag, then one inherited from the
    Rule or the Feature. A slice tag on a Feature is a default for everything beneath it,
    and a scenario that names its own slice has overridden that default deliberately."""
    for source in (sc.get("tags") or [], eff_tags(sc)):
        for t in source:
            n = t.lstrip("@").lower()
            if n in SLICE_TAGS:
                return n
    return ""


def size_badge(f, sizing):
    roll = (sizing.get(f["key"]) or {}).get("rollup") or {}
    if roll:
        c = roll["counts"]
        lg = ' class="lg"' if c["large"] else ""
        return (f'<span class="szb"><b{lg}>{c["large"]}</b>L &#183; <b>{c["medium"]}</b>M '
                f'&#183; <b>{c["small"]}</b>S &#183; <b>{roll["totalPoints"]}</b> pts</span>')
    # No sizing run, but the team may have committed size tags -- band counts alone
    # still render honestly; the points total genuinely needs a sizing pass.
    counts = dict.fromkeys(SIZE_TAGS, 0)
    for r in f.get("rules") or []:
        for sc in r.get("scenarios") or []:
            for t in eff_tags(sc):
                n = t.lstrip("@").lower()
                if n in counts:
                    counts[n] += 1
    if not any(counts.values()):
        return ""
    lg = ' class="lg"' if counts["large"] else ""
    return (f'<span class="szb"><b{lg}>{counts["large"]}</b>L &#183; '
            f'<b>{counts["medium"]}</b>M &#183; <b>{counts["small"]}</b>S</span>')


def sizing_panel(f, sizing):
    sz = sizing.get(f["key"]) or {}
    roll = sz.get("rollup")
    if not roll:
        return ""

    risks = "".join(f"<li>{e(r)}</li>" for r in roll.get("riskFlags") or [])
    riskb = (f'<div class="gh">Risk <span class="gn">{len(roll["riskFlags"])}</span>'
             f'<em>Large scenarios on the MVP critical path &#8212; split or accept explicitly'
             f'</em></div><ol class="blk">{risks}</ol>') if risks else ""

    rows = ""
    for s in sz.get("scenarios") or []:
        d = s.get("dimensions") or {}
        sl = s.get("effectiveSlice") or ""
        rec = ' <em class="rec">rec</em>' if sl and s.get("sliceSource") != "tagged" else ""
        rows += (f'<tr><td>{e(s.get("name", ""))}</td>'
                 f'<td class="dsz">{d.get("dataState", "?")}&#183;{d.get("integration", "?")}'
                 f'&#183;{d.get("uiSteps", "?")}</td>'
                 f'<td class="dsz"><b>{s.get("points", "")}</b></td>'
                 f'<td class="bnd b-{e(s.get("band", ""))}">'
                 f'{e((s.get("band") or "").capitalize())}</td>'
                 f'<td class="slc">{f"@{e(sl)}{rec}" if sl else "&#8212;"}</td></tr>')

    c = roll["counts"]
    ct = f'{c["large"]}L / {c["medium"]}M / {c["small"]}S &#183; {roll["totalPoints"]} pts'
    return (f'<details class="sub siz"><summary>Scenario sizing'
            f'<span class="ct">{ct}</span></summary>{riskb}'
            f'<div class="gh">Complexity <em>Data &amp; State &#183; Integration &#183; UI/UX, '
            f'each 1&#8211;3 &#183; Small 3&#8211;4 &#183; Medium 5&#8211;7 &#183; '
            f'Large 8&#8211;9 &#183; slices marked <b>rec</b> are unconfirmed recommendations'
            f'</em></div>'
            f'<table class="nfr szt"><tr><th>Scenario</th><th>D&#183;I&#183;U</th><th>Pts</th>'
            f'<th>Size</th><th>Slice</th></tr>{rows}</table></details>')


# ------------------------------------------------------------------ cards

#: How a commitment's current state reads on a card. `None` for
#: authorizes_work is *could not determine* and is deliberately not styled
#: like either answer — a map that renders an outage as a green chip is the
#: cached-authority failure with a nicer font.
CMTCLS = {True: "cmt-ok", False: "cmt-block", None: "cmt-unk"}
CMTWORD = {True: "authorized", False: "blocked", None: "unverified"}


def commitment(f, scores):
    """The chip naming this feature's commitment and its state, or "".

    Two things a reader cannot get from a Development Token: *which*
    commitment governs this feature, and whether it still authorizes work.
    A blocked commitment and a blocked token are different failures with
    different fixes — the package is not ready, versus the approval is gone
    and editing the package will not help — so the chip never rewrites one
    verdict into the other.

    The read time is shown because a map is a snapshot rendered at some past
    moment. Without it a green chip is indistinguishable from a fresh check,
    which is the stale-authority problem moved into a dashboard.
    """
    s = scores.get(f["key"]) or {}
    c = s.get("commitment")
    # Score files are agent-produced. A string where an object belongs took
    # the whole page down through `c.get`, and one bad record meant nobody
    # saw any of the map.
    if not isinstance(c, dict):
        return ""
    ident = c.get("commitment_id")
    if not isinstance(ident, str) or not ident.strip():
        return ""

    authorizes = c.get("authorizes_work")
    if not isinstance(authorizes, bool):
        # None is "could not determine" and so is anything else. A dict
        # lookup is only total over hashable keys, which is easy to forget
        # when the values are meant to be True/False/None — `CMTCLS.get(["yes"])`
        # raises TypeError, not KeyError.
        authorizes = None

    when = c.get("checked_at")
    when = when if isinstance(when, str) and when.strip() else None

    # A reading whose freshness cannot be assessed is not a verified one.
    # Rendering an untimed `True` as the confident green is precisely the
    # thing the read time exists to prevent: a chip indistinguishable from
    # a fresh check. 14A settled this for the token; the pixel agrees.
    untimed = authorizes is True and when is None
    state = None if untimed else authorizes

    cls = CMTCLS.get(state, "cmt-unk")
    word = CMTWORD.get(state, "unverified")
    reason = c.get("reason")
    detail = f' &#183; {e(str(reason))}' if reason and state is not True else ""
    if untimed:
        detail = " &#183; read time unknown"
    read = f'<span class="cmtw">read {e(when)}</span>' if when else ""
    return (f'<div class="cmt {cls}"><span class="cmtk">commitment</span>'
            f'<span class="cmtid">{e(ident)}</span>'
            f'<span class="cmts">{word}{detail}</span>{read}</div>')


def readiness(f, scores):
    s = scores.get(f["key"])
    if not s:
        return "", ""
    tc = TOKCLS[s["decision"]]
    na = ('<span class="na">not assessable from this record &#8212; the spec lives elsewhere'
          '</span>') if s.get("notAssessable") else ""
    tok = (f'<div class="token {tc}"><span class="tk">{e(s["decision"])}</span>'
           f'<span class="tsc"><b>{s["score"]:g}</b>/10</span>'
           f'<span class="tlab">Development Token &#183; advisory score</span>{na}</div>')

    dims = "".join(
        '<tr class="d{c}"><td class="dn">{n}</td><td class="dnm">{nm}</td>'
        '<td class="ds"><span class="pip p{c}"></span>{sc:g}</td>'
        '<td class="dnote">{note}</td></tr>'.format(
            c=PIP.get(d["score"], "h"), n=d.get("n", i + 1), nm=e(d.get("name", "")),
            sc=d["score"], note=e(d.get("note", "")))
        for i, d in enumerate(s.get("dimensions") or []))

    blk = ("".join(f"<li>{e(b)}</li>" for b in s.get("blockers") or [])
           or '<li class="clear">None. This draft is gated by score and edits only.</li>')
    eds = "".join(f"<li>{e(x)}</li>" for x in s.get("edits") or [])

    panel = (
        f'<details class="sub gk {tc}"><summary>GovKit readiness'
        f'<span class="ct">{s["score"]:g}/10</span></summary>'
        f'<p class="gsum">{e(s.get("summary",""))}</p>'
        f'<div class="gh">Critical blockers <span class="gn">{len(s.get("blockers") or [])}</span>'
        f'<em>the gate &#8212; any one of these blocks AI-assisted coding regardless of score</em>'
        f'</div><ol class="blk">{blk}</ol>'
        f'<div class="gh">High-priority edits <span class="gn">{len(s.get("edits") or [])}</span>'
        f'</div><ol class="eds">{eds}</ol>'
        f'<div class="gh">Rubric breakdown '
        f'<em>1.0 ready &#183; 0.5 needs targeted edits &#183; 0.0 not ready</em></div>'
        f'<table class="dim">{dims}</table></details>')
    return tok, panel


def table_html(rows, cls="gtab"):
    """A Gherkin table (step data table or Examples block) as HTML. First row is the
    header when there is more than one row."""
    if not rows:
        return ""
    head = "".join(f"<th>{e(c)}</th>" for c in rows[0])
    body = "".join("<tr>" + "".join(f"<td>{e(c)}</td>" for c in r) + "</tr>"
                   for r in rows[1:])
    return f'<table class="{cls}"><tr>{head}</tr>{body}</table>'


def steps_block(sc):
    """Steps with the detail the old line-scanner threw away: a step's data table and
    doc string are part of what the step means, and a reviewer who cannot see them is
    reviewing a different scenario."""
    details = sc.get("stepDetails")
    if not details:
        return ('<ol class="steps">'
                + "".join(f"<li>{e(x)}</li>" for x in sc.get("steps") or [])
                + "</ol>")
    out = ""
    for d in details:
        extra = ""
        if d.get("dataTable"):
            extra += table_html(d["dataTable"])
        if d.get("docString"):
            extra += f'<pre class="gdoc">{e(d["docString"].get("content", ""))}</pre>'
        kw = (d.get("keyword") or "").strip()
        out += f'<li>{e((kw + " " + (d.get("text") or "")).strip())}{extra}</li>'
    return f'<ol class="steps">{out}</ol>'


def examples_block(sc):
    """Examples tables under an outline, with the expanded row count. One authored
    outline is several executable examples, and the card says both numbers."""
    exs = sc.get("examples") or []
    if not exs:
        return ""
    out = ""
    for ex in exs:
        name = f' &#183; {e(ex.get("name"))}' if ex.get("name") else ""
        rows = ([ex.get("header") or []] + (ex.get("rows") or [])) if ex.get("header") \
            else (ex.get("rows") or [])
        out += (f'<div class="exs"><span class="exh">Examples{name}'
                f' <em>{len(ex.get("rows") or [])} row(s)</em></span>'
                f'{table_html(rows)}</div>')
    return out


def bg_block(bg, label):
    """A Background, with its scope named. Feature-level and Rule-level backgrounds run
    for different scenarios, and a card that shows one without saying which is which
    invites exactly the wrong conclusion."""
    if not bg or not (bg.get("steps") or bg.get("stepDetails")):
        return ""
    steps = steps_block(bg)
    nm = f' &#183; {e(bg.get("name"))}' if bg.get("name") else ""
    return (f'<div class="bgb"><span class="bgh">{e(label)}{nm}</span>{steps}</div>')


def card(f, scores, sizing, central):
    st = f.get("status") or ""
    cls = "ok" if st == "In Delivery" else ("rdy" if st.startswith("Ready") else "wip")
    chips = "".join(f'<span class="chip in" data-art="{e(a)}">&#8592; {e(a)}</span>'
                    for a in f.get("consumes") or [])
    chips += "".join(f'<span class="chip out" data-art="{e(a)}">{e(a)} &#8594;</span>'
                     for a in f.get("produces") or [])

    # One .feature file has one Feature background, and a package may hold several
    # files. Render each file's background ahead of that file's rules, so a later file's
    # scenarios never sit under the first file's unrelated setup. A single-file package
    # renders exactly as before.
    bgs = [b for b in (f.get("backgrounds") or [f.get("background")]) if b]
    by_file = {}
    for b in bgs:
        by_file.setdefault(b.get("file") or "", b)
    multi = len(bgs) > 1
    rules = "" if multi else bg_block(bgs[0] if bgs else None, "Feature background")
    shown = set()
    for r in f.get("rules") or []:
        if multi:
            fn = r.get("file") or ""
            if fn not in shown:
                shown.add(fn)
                rules += bg_block(by_file.get(fn), f"Feature background \u00b7 {fn}")
        scs = ""
        for sc in r.get("scenarios") or []:
            sl = scen_slice(sc)
            tags = "".join(
                f'<span class="stag st-{t.lstrip("@").lower()}">{e(t)}</span>'
                for t in eff_tags(sc)
                if t.lstrip("@").lower() in SLICE_TAGS + SIZE_TAGS)
            outline = ('<span class="stag st-outline">Outline</span>'
                       if sc.get("type") == "scenario_outline" else "")
            steps = steps_block(sc)
            exb = examples_block(sc)
            slattr = f' data-slice="{sl}"' if sl else ""
            scs += (f'<li{slattr}><b>{e(sc.get("name", ""))}</b>'
                    f'{outline}{tags}{steps}{exb}</li>')
        label = e(r.get("rule") or "(no Rule declared)")
        rules += (f'<details class="rule"><summary><span class="rr">RULE</span>{label}'
                  f'<span class="ct">{len(r.get("scenarios") or [])}</span></summary>'
                  f'{bg_block(r.get("background"), "Rule background")}'
                  f'<ul class="scen">{scs}</ul></details>')
    if multi:
        # A background whose file produced no rules (or a record without file names)
        # still belongs to the reader; show it up front rather than drop it.
        for fn, b in by_file.items():
            if fn not in shown:
                rules = bg_block(b, f"Feature background \u00b7 {fn}") + rules
    if not (f.get("rules") or []):
        note = f.get("specNote") or ("No acceptance criteria in this record.")
        rules = f'<p class="none">{e(note)}</p>'
    if f.get("parseErrors"):
        # A parse failure is not a thin spec, and a card that cannot tell them apart
        # sends the reader to the wrong person. Name file, line and column.
        errs = "".join(
            '<li><code>{}:{}{}</code> {}</li>'.format(
                e(x.get("file") or ""), x.get("line") or "?",
                ":" + str(x["column"]) if x.get("column") else "", e(x.get("message") or ""))
            for x in f["parseErrors"])
        rules = (f'<div class="perr"><b>Gherkin did not parse &#8212; '
                 f'{len(f["parseErrors"])} error(s).</b> No scenarios were ingested from '
                 f'the failed file(s).<ul>{errs}</ul></div>' + rules)

    nfr = "".join(
        '<tr><td>{}</td><td>{}</td><td>{}</td><td class="{}">{}</td><td>{}</td></tr>'.format(
            e(n.get("id")), e(n.get("dim")), e(n.get("req")),
            "tbd" if "TBD" in (n.get("threshold") or "").upper() or not (n.get("threshold") or "").strip() else "",
            e(n.get("threshold") or "&#8212;"), e(n.get("gap") or "&#8212;"))
        for n in f.get("nfr") or [])
    nfrb = (f'<details class="sub"><summary>Non-functional requirements'
            f'<span class="ct">{len(f.get("nfr") or [])}</span></summary>'
            f'<table class="nfr"><tr><th>#</th><th>Dimension</th><th>Requirement</th>'
            f'<th>Threshold</th><th>Gap</th></tr>{nfr}</table></details>') if f.get("nfr") else ""

    ev = "".join(
        '<tr><td><code>{}</code></td><td>{}</td><td class="{}">{}</td>'
        '<td><span class="gate g{}">{}</span></td></tr>'.format(
            e(x.get("id")), e(x.get("type")),
            "tbd" if "TBD" in (x.get("pass_threshold") or "").upper() else "",
            e(x.get("pass_threshold")), e(x.get("gate")), e(x.get("gate")))
        for x in f.get("evals") or [])
    evb = (f'<details class="sub"><summary>Evaluation criteria'
           f'<span class="ct">{len(f.get("evals") or [])}</span></summary>'
           f'<table class="nfr"><tr><th>id</th><th>type</th><th>pass threshold</th>'
           f'<th>gate</th></tr>{ev}</table></details>') if f.get("evals") else ""

    oq = "".join(f"<li>{e(q)}</li>" for q in f.get("openQuestions") or [])
    oqb = (f'<details class="sub warn"><summary>Open questions'
           f'<span class="ct">{len(f.get("openQuestions") or [])}</span></summary>'
           f'<ol class="oq">{oq}</ol></details>') if oq else ""

    scope = "".join(f"<li>{e(x)}</li>" for x in f.get("scope") or [])
    scopeb = (f'<details class="sub"><summary>Functional scope'
              f'<span class="ct">{len(f.get("scope") or [])}</span></summary>'
              f'<ul class="pl">{scope}</ul></details>') if scope else ""

    oos = "".join(f"<li>{e(x)}</li>" for x in f.get("outOfScope") or [])
    oosb = (f'<details class="sub"><summary>Out of scope'
            f'<span class="ct">{len(f.get("outOfScope") or [])}</span></summary>'
            f'<ul class="pl">{oos}</ul></details>') if oos else ""

    dod = "".join(f"<li>{e(x)}</li>" for x in f.get("dod") or [])
    dodb = (f'<details class="sub"><summary>Definition of done'
            f'<span class="ct">{len(f.get("dod") or [])}</span></summary>'
            f'<ul class="pl">{dod}</ul></details>') if dod else ""

    ph = " ".join(f'<span class="pp">P{e(p)}</span>' for p in f.get("phases") or [])
    env = "central" if f["key"] in central else "deployment"
    tok, panel = readiness(f, scores)
    sizb = sizing_panel(f, sizing)
    cmtb = commitment(f, scores)
    szb = size_badge(f, sizing)
    url = f.get("url")
    keyhtml = (f'<a class="key" href="{e(url)}" target="_blank" rel="noopener">{e(f["key"])}</a>'
               if url else f'<span class="key nolink">{e(f["key"])}</span>')
    ntbd = len(f.get("nfrTbd") or [])

    return f'''<article class="card {env}" id="{e(f['key'])}" data-key="{e(f['key'])}">
{tok}{cmtb}<header><div class="ktop">{keyhtml}
{f'<span class="status {cls}">{e(st)}</span>' if st else ''}{ph}
{'<span class="cv">client-visible</span>' if f.get('clientVisible') else ''}</div>
<h4>{e(f.get('title',''))}</h4>
{f'<p class="uc">{e(f.get("userContext"))}</p>' if f.get('userContext') else ''}
<div class="chips">{chips}</div>
<div class="metrics"><span><b>{f.get('ruleCount',0)}</b> rules</span>
<span><b>{f.get('scenarioCount',0)}</b> scenarios</span>
{f"<span><b>{f.get('exampleCount')}</b> examples</span>" if f.get('exampleCount') and f.get('exampleCount') != f.get('scenarioCount') else ''}
<span><b>{len(f.get('openQuestions') or [])}</b> open</span>
<span class="{'amber' if ntbd else ''}"><b>{ntbd}</b> NFR gaps</span>{szb}</div></header>
<div class="body">{panel}{sizb}{scopeb}<details class="sub ac" open>
<summary>Acceptance criteria<span class="ct">{f.get('ruleCount',0)}</span></summary>
{rules}</details>{nfrb}{evb}{oqb}{oosb}{dodb}</div></article>'''



# ------------------------------------------------------------------ workflow views

def _actor_map(view):
    return {a.get("id"): a for a in view.get("actors") or []}


def _actor_label(actors, aid):
    a = actors.get(aid)
    if not a:
        return e(aid or "&#8212;")
    kind = a.get("kind") or ""
    mark = {"human": "&#9679;", "system": "&#9632;", "agent": "&#9670;"}.get(kind, "&#9675;")
    return f'<span class="actor k-{e(kind)}"><i aria-hidden="true">{mark}</i>{e(a.get("name") or aid)}</span>'


def wf_l1(views):
    """L1 — the customer journey. No Gherkin: this is the view someone outside
    the team reads, and a rule slug leaking into it is the failure mode."""
    v = views.get("l1") or {}
    actors = _actor_map(v)
    known = {a.get("id") for a in v.get("activities") or []}
    rows = ""
    for a in v.get("activities") or []:
        nxt = a.get("next") or []
        if nxt:
            items = []
            for x in nxt:
                tgt = x.get("to")
                # A transition the resolver flagged as dangling must not render
                # as a link: a fragment with no destination looks navigable and
                # silently does nothing.
                label = (f'<a href="#wfa-{e(tgt)}">{e(tgt)}</a>' if tgt in known
                         else f'{e(tgt)} <em class="warn">no such activity</em>')
                if x.get("condition"):
                    label += f' <em>when {e(x["condition"])}</em>'
                elif len(nxt) > 1:
                    label += ' <em class="warn">no stated condition</em>'
                items.append(f"<li>{label}</li>")
            to = f"<ul class='nx'>{''.join(items)}</ul>"
        else:
            to = '<em>ends the journey</em>'
        rows += (f'<tr id="wfa-{e(a.get("id"))}"><td class="an">{e(a.get("name") or a.get("id"))}</td>'
                 f'<td>{_actor_label(actors, a.get("actor"))}</td><td>{to}</td></tr>')
    return (f'<p class="h2s">{e(v.get("outcome") or "")}</p>'
            f'<table class="led wf"><tr><th>Activity</th><th>Actor</th><th>Then</th></tr>'
            f'{rows}</table>')


def wf_l2(views):
    """L2 — who collaborates inside each activity, and where work changes
    hands. Handoffs get their own column because that is where most real
    defects live and adjacency hides them."""
    v = views.get("l2") or {}
    actors = _actor_map(v)
    out = ""
    for a in v.get("activities") or []:
        steps = a.get("steps") or []
        if not steps:
            body = '<p class="h2s"><em>no steps recorded</em></p>'
        else:
            rows = ""
            for st in steps:
                h = st.get("handoff") or {}
                hand = (f'{_actor_label(actors, h.get("from"))} &#8594; '
                        f'{_actor_label(actors, h.get("to"))}') if h else "&#8212;"
                rows += (f'<tr><td class="an">{e(st.get("name") or st.get("id"))}</td>'
                         f'<td>{_actor_label(actors, st.get("actor"))}</td><td>{hand}</td></tr>')
            body = (f'<table class="led wf"><tr><th>Step</th><th>Actor</th>'
                    f'<th>Handoff</th></tr>{rows}</table>')
        out += (f'<details class="wfact" open><summary>{e(a.get("name") or a.get("id"))}'
                f'<span class="ls">{_actor_label(actors, a.get("actor"))}</span></summary>'
                f'{body}</details>')
    return out


def wf_l3(views, coverage):
    """L3 — the behavior governing each step, by reference.

    A Rule referenced from several activities is authored once. `referencedBy`
    is rendered next to it so the reuse reads as reuse rather than as three
    copies of the same Rule.
    """
    v = views.get("l3") or {}
    refby = v.get("referencedBy") or {}
    out = ""
    for a in v.get("activities") or []:
        aid = a.get("id")
        items = ""
        for b in (a.get("behavior") or []) + (a.get("design") or []):
            items += _wf_ref_row(b, refby, here=aid, where="<em>activity</em>")
        for st in a.get("steps") or []:
            for b in st.get("behavior") or []:
                items += _wf_ref_row(b, refby, here=f"{aid}.{st.get('id')}",
                                     where=e(st.get("name") or st.get("id")))
        if not items:
            items = '<tr><td colspan="4"><em>no behavior referenced at this activity</em></td></tr>'
        out += (f'<details class="wfact" open><summary>{e(a.get("name") or a.get("id"))}</summary>'
                f'<table class="led wf"><tr><th>Behavior</th><th>Where</th><th>Identity</th>'
                f'<th>Also referenced at</th></tr>{items}</table></details>')

    unc = coverage.get("uncovered") or []
    if unc:
        rows = "".join(
            f'<tr><td class="an">{e(u.get("name") or u.get("slug"))}</td>'
            f'<td><code>{e(u.get("kind"))}:{e(u.get("slug"))}</code></td>'
            f'<td>{e(u.get("featureKey"))}</td></tr>' for u in unc)
        out += ('<details class="wfact"><summary>Not touched by this journey '
                f'<span class="ls">{len(unc)}</span></summary>'
                '<p class="h2s">Behavior in the corpus that no activity or step references. '
                'Legitimate if it belongs to another journey &#8212; but unreferenced behavior '
                'is behavior this map implies does not exist.</p>'
                f'<table class="led wf"><tr><th>Behavior</th><th>Identity</th><th>Feature</th>'
                f'</tr>{rows}</table></details>')
    return out


def _wf_ref_row(b, refby, here=None, where="&#8212;"):
    """One behavior row. `here` is this row's own location key, exactly as the
    resolver writes it (`activity` or `activity.step`).

    Matching on the location key rather than a display name matters: the column
    is meant to show reuse *elsewhere*, and a row that lists its own location
    turns one reference into apparent duplication — the opposite of what the
    column exists to demonstrate.
    """
    ref = b.get("ref") or ""
    others = [x for x in refby.get(ref, []) if x != here]
    also = ", ".join(e(o) for o in others) if others else "&#8212;"

    if not b.get("resolved"):
        why = b.get("reason") or "unresolved"
        label = ("declared outside the Gherkin corpus" if why == "non-gherkin-kind"
                 else "in another repository &#8212; not resolvable here" if why == "foreign-source"
                 else "unresolved")
        name = f'<em>{e(ref)}</em>'
        ident = f'<span class="warn">{e(label)}</span>'
    else:
        anchor = e(b.get("featureKey") or "")
        name = f'<a href="#{anchor}">{e(b.get("name") or b.get("slug"))}</a>'
        tags = " ".join(f'<span class="chip">{e(t)}</span>' for t in (b.get("tags") or [])
                        if t.startswith("@mvp") or t.startswith("@v1") or t.startswith("@v2"))
        derived = ('<span class="warn"> derived id</span>'
                   if b.get("idSource") == "derived" else "")
        ident = f'<code>{e(b.get("kind"))}:{e(b.get("slug"))}</code>{derived} {tags}'
    return f'<tr><td class="an">{name}</td><td>{where}</td><td>{ident}</td><td>{also}</td></tr>'


def workflow_section(resolved):
    """The whole workflow block: three views, diagnostics, and an honest status.

    Rendered from the resolver's output, so this function performs no
    resolution of its own and cannot disagree with the resolver about what a
    reference means.
    """
    if not resolved:
        return ""
    views = resolved.get("views") or {}
    cov = resolved.get("coverage") or {}
    diags = resolved.get("diagnostics") or []
    errs = [d for d in diags if d.get("level") == "error"]
    warns = [d for d in diags if d.get("level") != "error"]

    def dlist(items):
        return "".join(
            f'<li><code>{e(d.get("code"))}</code> {e(d.get("message"))}'
            + (f' <span class="ls">{e(d.get("activity") or d.get("element") or "")}</span>'
               if d.get("activity") or d.get("element") else "")
            + "</li>" for d in items)

    diag_block = ""
    if errs or warns:
        diag_block = (
            f'<details class="wfact"{" open" if errs else ""}>'
            f'<summary>Diagnostics <span class="ls">{len(errs)} error, {len(warns)} warning'
            f'</span></summary><ul class="wfd">{dlist(errs)}{dlist(warns)}</ul></details>')

    return (
        '<h2 id="workflow">The journey</h2>'
        '<p class="h2s">One workflow source, three views. Behavior is referenced, never '
        'restated &#8212; a Rule shown at several steps is authored once.</p>'
        '<p class="advisory"><strong>Advisory view.</strong> Slice chips are a planning view '
        'over behavior, not a commitment, and nothing here is an approval: this page is '
        'generated from files in a working tree and cannot verify that any decision was '
        'recorded. Where a card shows a commitment, that is a <strong>snapshot</strong> of what was read when this page was generated &#8212; it does not gate anything, and it can be out of date the moment it is written. The gate is in CI.</p>'
        '<details class="wfview" open><summary>L1 &#8212; customer journey</summary>'
        f'{wf_l1(views)}</details>'
        '<details class="wfview"><summary>L2 &#8212; who collaborates, and where work changes '
        f'hands</summary>{wf_l2(views)}</details>'
        '<details class="wfview"><summary>L3 &#8212; the behavior that governs each step'
        f'</summary>{wf_l3(views, cov)}</details>'
        f'{diag_block}')


# ------------------------------------------------------------------ document

CSS = """
:root{--ink:#131A2B;--ink2:#3D4759;--mut:#6B7486;--pap:#F7F8FA;--wht:#fff;
--cen:#275E8E;--dep:#1F6F5C;--amb:#B06A0F;--red:#9B3B2E;--hair:#D8DCE4;--hair2:#EAEDF2}
*{box-sizing:border-box}
body{margin:0;background:var(--pap);color:var(--ink);
font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,sans-serif;
-webkit-font-smoothing:antialiased}
.mono,code,.key,.an,.chip,.ph,.eyebrow,.rr,.gate,.pp,.status,.tk,.tsc,.ct
{font-family:ui-monospace,SFMono-Regular,"SF Mono",Menlo,"JetBrains Mono",Consolas,monospace}
.wrap{max-width:1640px;margin:0 auto;padding:0 26px 80px}
.top{padding:44px 0 8px}
.eyebrow{margin:0 0 10px;font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--mut)}
h1{margin:0 0 8px;font-size:36px;letter-spacing:-.025em;font-weight:680}
h1 span{color:var(--mut);font-weight:400}
.gov{font-size:12.5px;letter-spacing:.05em;color:var(--ink2);border-left:3px solid var(--cen);
padding-left:10px;margin:0 0 16px}
.lede{max-width:820px;color:var(--ink2);margin:0 0 22px}
.stats{display:flex;flex-wrap:wrap;background:var(--wht);border:1px solid var(--hair);border-radius:9px}
.stat{flex:1;min-width:118px;padding:13px 16px;border-right:1px solid var(--hair2)}
.stat:last-child{border-right:0}
.stat b{display:block;font-size:26px;font-family:ui-monospace,monospace;letter-spacing:-.03em;line-height:1.1}
.stat span{font-size:10.5px;letter-spacing:.13em;text-transform:uppercase;color:var(--mut)}
.stat.a b{color:var(--amb)} .stat.r b{color:var(--red)} .stat.g b{color:var(--dep)}
h2{margin:44px 0 6px;font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--mut);
font-family:ui-monospace,monospace;padding-top:26px;border-top:2px solid var(--ink)}
.h2s{max-width:820px;color:var(--ink2);margin:0 0 20px}
.spinebox{background:var(--wht);border:1px solid var(--hair);border-radius:10px;padding:18px 16px;overflow-x:auto}
svg.spine{display:block;max-width:none}
.node rect{fill:#fff;stroke:var(--hair);stroke-width:1.5}
.node.central rect{stroke:var(--cen)} .node.deployment rect{stroke:var(--dep)}
.node.undecided rect{stroke:var(--amb);stroke-width:1.5;stroke-dasharray:5 3}
.node:hover rect{fill:#FAFBFC}
.nk{font:600 11px ui-monospace,monospace;letter-spacing:.06em;fill:var(--mut)}
.node.central .nk{fill:var(--cen)} .node.deployment .nk{fill:var(--dep)}
.node.undecided .nk{fill:var(--amb)}
.nt{font:600 13px -apple-system,sans-serif;fill:var(--ink)}
.nm{font:10.5px ui-monospace,monospace;fill:var(--mut)}
.node .tkbg{stroke:none}
.node .tkbg.t-ok{fill:#DCEDE5} .node .tkbg.t-edit{fill:#F5E8D4} .node .tkbg.t-block{fill:#F4DED9}
.tkt{font:700 11px ui-monospace,monospace;text-anchor:middle;letter-spacing:-.02em}
.tkt.t-ok{fill:var(--dep)} .tkt.t-edit{fill:var(--amb)} .tkt.t-block{fill:var(--red)}
.edge{fill:none;stroke:#7C8493;stroke-width:1.3}
.edge.back{stroke:var(--amb);stroke-dasharray:5 3}
.elab{font:10.5px ui-monospace,monospace;fill:var(--mut);text-anchor:middle}
.elab.backl{fill:var(--amb)}
.legend{display:flex;flex-wrap:wrap;gap:18px;margin:12px 0 0;font-size:11.5px;color:var(--mut)}
.legend i{display:inline-block;width:15px;border-top:2px solid var(--cen);margin-right:6px;
vertical-align:middle}
.legend span:nth-child(2) i{border-color:var(--dep)}
.legend.tkleg{margin-top:6px} .legend.tkleg span{line-height:1.6}
.lane{margin-top:40px}
.lh h3{margin:0 0 3px;font-size:22px;letter-spacing:-.015em}
.lh h3 .ls{font-size:13px;color:var(--mut);font-weight:400;margin-left:9px}
.lh p{margin:0 0 16px;color:var(--ink2);font-size:13.5px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(360px,1fr));gap:16px;align-items:start}
.card{background:var(--wht);border:1px solid var(--hair);border-radius:9px;overflow:hidden;
border-top:3px solid var(--hair)}
.card.central{border-top-color:var(--cen)} .card.deployment{border-top-color:var(--dep)}
.card header{padding:15px 17px 13px;border-bottom:1px solid var(--hair2)}
.ktop{display:flex;flex-wrap:wrap;gap:7px;align-items:center;margin-bottom:9px}
.key{font-size:12px;font-weight:600;color:var(--ink);text-decoration:none;border-bottom:1px solid var(--hair)}
.key.nolink{border-bottom:0;color:var(--mut)}
.status{font-size:9.5px;letter-spacing:.1em;text-transform:uppercase;padding:2.5px 7px;border-radius:3px;
background:var(--hair2);color:var(--ink2)}
.status.ok{background:#E3F1EC;color:var(--dep)} .status.rdy{background:#E7EEF4;color:var(--cen)}
.status.wip{background:#F6EEE2;color:var(--amb)}
.pp{font-size:9.5px;padding:2.5px 6px;border-radius:3px;background:var(--hair2);color:var(--ink2)}
.cv{font-size:9.5px;letter-spacing:.06em;text-transform:uppercase;padding:2.5px 7px;border-radius:3px;
border:1px solid var(--dep);color:var(--dep);font-family:ui-monospace,monospace}
.card h4{margin:0 0 8px;font-size:16px;line-height:1.3;letter-spacing:-.012em;font-weight:640}
.uc{margin:0 0 11px;font-size:13px;color:var(--ink2);line-height:1.5}
.chips{display:flex;flex-wrap:wrap;gap:5px;margin-bottom:11px}
.chip{font-size:10.5px;padding:2px 7px;border-radius:3px;cursor:default}
.chip.in{background:#F1F3F6;color:var(--ink2)}
.chip.out{background:#E7EEF4;color:var(--cen);font-weight:600}
.chip.hl{outline:2px solid var(--amb);outline-offset:1px}
.metrics{display:flex;gap:15px;font-size:11.5px;color:var(--mut);flex-wrap:wrap}
.metrics b{color:var(--ink);font-family:ui-monospace,monospace}
.metrics .amber b{color:var(--amb)}
.token{display:flex;align-items:baseline;gap:9px;padding:8px 17px 7px;flex-wrap:wrap;
border-bottom:1px solid rgba(0,0,0,.07)}
.token .tk{font-size:10px;letter-spacing:.12em;text-transform:uppercase;font-weight:700}
.token .tsc{font-size:11px;color:var(--ink2);opacity:.85}
.token .tsc b{font-size:14.5px;letter-spacing:-.02em}
.token .tlab{margin-left:auto;font-size:9.5px;letter-spacing:.09em;text-transform:uppercase;color:var(--mut)}
.token .na{width:100%;font-size:10.5px;color:var(--red);opacity:.9}
.tok-ok{background:#E7F2ED} .tok-ok .tk{color:var(--dep)}
.tok-edit{background:#F8F0E3} .tok-edit .tk{color:var(--amb)}
.tok-block{background:#F7E9E6} .tok-block .tk{color:var(--red)}
.body{padding:5px 17px 13px}
details.sub{border-bottom:1px solid var(--hair2)}
details.sub:last-child{border-bottom:0}
details.sub>summary{cursor:pointer;padding:9px 0;font-size:12px;font-weight:600;letter-spacing:.02em;
display:flex;align-items:center;gap:7px;list-style:none}
details.sub>summary::-webkit-details-marker{display:none}
details.sub>summary::before{content:"+";font-family:ui-monospace,monospace;color:var(--mut);
width:11px;flex:0 0 11px;text-align:center}
details.sub[open]>summary::before{content:"\\2212"}
details.sub.warn>summary{color:var(--amb)}
details.sub.gk>summary{font-weight:640}
details.sub.gk.tok-block>summary{color:var(--red)}
details.sub.gk.tok-edit>summary{color:var(--amb)}
details.sub.gk.tok-ok>summary{color:var(--dep)}
details.sub.gk{background:transparent}
.ct{margin-left:auto;font-size:10.5px;color:var(--ink2);background:var(--hair2);padding:1px 7px;border-radius:9px}
details.rule{border-left:2px solid var(--hair2);padding-left:10px;margin:0 0 3px}
details.rule>summary{cursor:pointer;padding:6px 0;font-size:12.5px;display:flex;gap:8px;
align-items:center;list-style:none}
details.rule>summary::-webkit-details-marker{display:none}
.rr{font-size:8.5px;letter-spacing:.11em;color:var(--mut);border:1px solid var(--hair);
padding:1px 4px;border-radius:2px}
ul.scen{margin:2px 0 8px;padding-left:15px;font-size:12.5px;color:var(--ink2)}
ul.scen>li{margin-bottom:7px}
ol.steps{margin:3px 0 0;padding-left:15px;font-size:12px;color:var(--mut);line-height:1.5}
table.nfr{width:100%;border-collapse:collapse;font-size:11.5px;margin-bottom:10px}
table.nfr th{text-align:left;color:var(--mut);font-weight:600;border-bottom:1px solid var(--hair);padding:4px 6px 4px 0}
table.nfr td{padding:4px 6px 4px 0;border-bottom:1px solid var(--hair2);vertical-align:top;color:var(--ink2)}
td.tbd{color:var(--amb);font-weight:600}
.gate{font-size:9px;letter-spacing:.08em;text-transform:uppercase;padding:1px 5px;border-radius:2px;
background:var(--hair2);color:var(--ink2)}
.gate.grelease{background:#F5E6E3;color:var(--red)} .gate.gpr{background:#E7EEF4;color:var(--cen)}
ol.oq{margin:2px 0 10px;padding-left:17px;font-size:12.5px;color:var(--ink2)}
ol.oq li{margin-bottom:5px}
ul.pl{margin:2px 0 10px;padding-left:17px;font-size:12.5px;color:var(--ink2)}
ul.pl li{margin-bottom:3px}
.none{color:var(--mut);font-size:12.5px;font-style:italic}
.gsum{margin:2px 0 13px;font-size:13px;color:var(--ink2);line-height:1.5}
.gh{display:flex;align-items:baseline;gap:8px;flex-wrap:wrap;margin:14px 0 6px;font-size:10px;
letter-spacing:.12em;text-transform:uppercase;color:var(--ink);font-weight:700}
.gh .gn{font-family:ui-monospace,monospace;background:var(--hair2);color:var(--ink2);
padding:1px 6px;border-radius:8px;letter-spacing:0}
.gh em{font-style:normal;text-transform:none;letter-spacing:0;font-weight:400;font-size:11px;color:var(--mut)}
ol.blk,ol.eds{margin:0;padding-left:19px;font-size:12.5px;line-height:1.5;color:var(--ink2)}
ol.blk li{margin-bottom:5px;color:var(--red)}
ol.blk li.clear{color:var(--dep)}
ol.eds li{margin-bottom:5px}
table.dim{width:100%;table-layout:fixed;border-collapse:collapse;font-size:12px;margin-top:2px}
table.dim td{padding:6px 8px 6px 0;border-bottom:1px solid var(--hair2);vertical-align:top}
table.dim td.dn{font-family:ui-monospace,monospace;color:var(--mut);width:16px;font-size:10px;
padding-right:4px;padding-top:7px}
table.dim td.dnm{width:104px;color:var(--ink);font-weight:560;line-height:1.35;font-size:11.5px}
table.dim td.ds{font-family:ui-monospace,monospace;white-space:nowrap;width:44px;font-size:11.5px}
table.dim td.dnote{color:var(--mut);font-size:11.5px;line-height:1.45}
tr.d1 td.ds{color:var(--dep)} tr.dh td.ds{color:var(--amb)} tr.d0 td.ds{color:var(--red)}
.pip{display:inline-block;width:7px;height:7px;border-radius:50%;margin-right:6px;vertical-align:middle}
.pip.p1{background:var(--dep)} .pip.ph{background:var(--amb)} .pip.p0{background:var(--red)}
.govnote{margin:16px 0 0;padding:13px 16px;background:var(--wht);border:1px solid var(--hair);
border-radius:8px;font-size:12.5px;line-height:1.6;color:var(--ink2)}
.govnote b{color:var(--ink)}
.tki{font-family:ui-monospace,monospace;font-size:9.5px;letter-spacing:.1em;text-transform:uppercase;
font-weight:700;padding:2px 7px;border-radius:3px;white-space:nowrap}
.tki.tok-ok{color:var(--dep)} .tki.tok-edit{color:var(--amb)} .tki.tok-block{color:var(--red)}
table.led{width:100%;border-collapse:collapse;font-size:12.5px;background:var(--wht);
border:1px solid var(--hair);border-radius:9px;overflow:hidden}
table.led th{text-align:left;font-size:10px;letter-spacing:.12em;text-transform:uppercase;
color:var(--mut);padding:10px 14px;border-bottom:1px solid var(--hair)}
table.led td{padding:8px 14px;border-bottom:1px solid var(--hair2);vertical-align:top}
table.led td.an{font-family:ui-monospace,monospace;color:var(--cen)}
tr.term td.an{color:var(--mut)}
a.mini{font-family:ui-monospace,monospace;font-size:11px;color:var(--ink2);text-decoration:none;
border-bottom:1px solid var(--hair);margin-right:5px}
.stag{font-size:9px;letter-spacing:.05em;padding:1px 5px;border-radius:3px;margin-left:6px;
font-family:ui-monospace,monospace;vertical-align:1px;white-space:nowrap}
.stag.st-mvp{background:#E7EEF4;color:var(--cen);font-weight:700}
.stag.st-v1{background:var(--hair2);color:var(--ink2)}
.stag.st-v2{background:#F1F3F6;color:var(--mut)}
.stag.st-outline{background:#EFEAF6;color:#5B4A86;font-weight:600}
.bgb{margin:6px 0 8px;padding:7px 10px;border-left:3px solid var(--hair2);background:#FAFAFB;
border-radius:0 5px 5px 0}
.bgh{display:block;font-size:9.5px;letter-spacing:.07em;text-transform:uppercase;
color:var(--mut);margin-bottom:2px}
table.gtab{border-collapse:collapse;margin:4px 0 2px;font-size:11.5px}
table.gtab th,table.gtab td{border:1px solid var(--hair);padding:2px 7px;text-align:left;
color:var(--ink2)}
table.gtab th{background:var(--hair2);font-weight:600}
pre.gdoc{margin:4px 0 2px;padding:6px 9px;background:var(--hair2);border-radius:4px;
font-size:11.5px;white-space:pre-wrap;color:var(--ink2)}
.exs{margin:5px 0 2px}
.exh{display:block;font-size:9.5px;letter-spacing:.07em;text-transform:uppercase;
color:var(--mut)}
.exh em{text-transform:none;letter-spacing:0;font-style:normal;color:var(--mut)}
.perr{margin:0 0 10px;padding:9px 12px;background:#F7E9E6;border:1px solid #E4C6C0;
border-radius:6px;font-size:12px;color:var(--ink)}
.perr ul{margin:5px 0 0;padding-left:17px}
.perr code{font-family:ui-monospace,monospace}
.stag.st-small{border:1px solid var(--hair);color:var(--dep)}
.stag.st-medium{border:1px solid var(--hair);color:var(--ink2)}
.stag.st-large{border:1px solid var(--amb);color:var(--amb);font-weight:700}
.metrics .szb{white-space:nowrap}
.metrics .szb b.lg{color:var(--amb)}
table.szt td{font-size:11.5px}
table.szt td.dsz{font-family:ui-monospace,monospace;white-space:nowrap}
table.szt td.bnd{font-weight:600}
table.szt td.b-large{color:var(--amb)} table.szt td.b-small{color:var(--dep)}
table.szt td.slc{font-family:ui-monospace,monospace;white-space:nowrap}
table.szt em.rec{font-style:normal;font-size:9px;letter-spacing:.08em;text-transform:uppercase;
color:var(--amb);border:1px solid var(--hair);padding:0 3px;border-radius:2px}
.fltbar{display:flex;align-items:center;gap:8px;margin:18px 0 0;flex-wrap:wrap}
.fltbar>span{font-size:10px;letter-spacing:.13em;text-transform:uppercase;color:var(--mut);
font-family:ui-monospace,monospace}
.fltbar button{font:600 11px ui-monospace,monospace;padding:3px 10px;border-radius:4px;
border:1px solid var(--hair);background:var(--wht);color:var(--ink2);cursor:pointer}
.fltbar button.on{border-color:var(--cen);color:var(--cen);background:#E7EEF4}
.fltbar em{font-size:11px;color:var(--mut);font-style:normal}
body.flt-mvp ul.scen>li:not([data-slice="mvp"]),
body.flt-v1 ul.scen>li:not([data-slice="v1"]),
body.flt-v2 ul.scen>li:not([data-slice="v2"]){opacity:.28}
@media(max-width:640px){
.wrap{padding:0 15px 60px} h1{font-size:27px} .grid{grid-template-columns:1fr}
.stat{min-width:50%;border-right:0;border-bottom:1px solid var(--hair2)}
table.dim td.dnm{width:86px}
table.nfr{display:block;overflow-x:auto}}
"""

JS = """
document.querySelectorAll('.chip[data-art]').forEach(function(c){
  var a=c.getAttribute('data-art');
  function set(on){document.querySelectorAll('.chip[data-art="'+a+'"]')
    .forEach(function(x){x.classList.toggle('hl',on)})}
  c.addEventListener('mouseenter',function(){set(true)});
  c.addEventListener('mouseleave',function(){set(false)});
});
var fb=document.querySelectorAll('.fltbar button');
fb.forEach(function(b){b.addEventListener('click',function(){
  fb.forEach(function(x){x.classList.remove('on')});b.classList.add('on');
  var f=b.getAttribute('data-flt');document.body.className=f?'flt-'+f:'';
})});
"""


WF_CSS = """
.cmt{display:flex;gap:.4rem;align-items:center;font-size:.72rem;padding:.25rem .5rem;
border-radius:5px;margin:0 0 .35rem}
.cmt .cmtk{text-transform:uppercase;letter-spacing:.04em;opacity:.7}
.cmt .cmtid{font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
.cmt .cmtw{margin-left:auto;opacity:.65}
.cmt-ok{background:#eef6ee;border:1px solid #cfe3cf}
.cmt-block{background:#fdecec;border:1px solid #f0c3c3;font-weight:600}
.cmt-unk{background:#f4f1e6;border:1px solid #ddd6bd}
.advisory{background:#fff8e6;border:1px solid #e8d9a8;border-radius:6px;padding:.6rem .8rem;
 margin:.6rem 0 1rem;font-size:.86rem;line-height:1.45}
details.wfview{border:1px solid #dcdfe4;border-radius:8px;margin:.5rem 0;background:#fff}
details.wfview>summary{padding:.6rem .85rem;font-weight:600;cursor:pointer;list-style:revert}
details.wfview[open]>summary{border-bottom:1px solid #eceef1}
details.wfview>*:not(summary){padding:0 .85rem .7rem}
details.wfact{margin:.4rem 0;border-left:3px solid #e3e6ea;padding-left:.7rem}
details.wfact>summary{cursor:pointer;font-weight:600;padding:.25rem 0;list-style:revert}
table.wf td,table.wf th{vertical-align:top}
ul.nx{margin:0;padding-left:1.1rem}
ul.wfd{margin:.3rem 0;padding-left:1.1rem;font-size:.86rem}
ul.wfd code{background:#f3f4f6;padding:.05rem .3rem;border-radius:3px}
.actor i{margin-right:.3rem;font-style:normal}
.actor.k-human{color:#1f6f43}.actor.k-system{color:#31507d}.actor.k-agent{color:#7a3d8f}
.warn{color:#8a5a00;font-style:italic}
@media(max-width:640px){
 table.wf,table.wf tbody,table.wf tr,table.wf td,table.wf th{display:block;width:auto}
 table.wf tr{border-bottom:1px solid #eceef1;padding:.35rem 0}
 table.wf th{display:none}
 table.wf td{padding:.15rem 0}
 details.wfview>*:not(summary){padding:0 .6rem .6rem}
}
"""


def render(feats, scores, sizing, cfg, workflow=None):
    central = set(cfg.get("central") or [])
    lanes_cfg = cfg.get("lanes") or []
    if not lanes_cfg:
        seen = []
        for f in feats:
            w = f.get("workstream") or "Features"
            if w not in seen:
                seen.append(w)
        lanes_cfg = [{"name": w} for w in seen]

    lanes = ""
    for L in lanes_cfg:
        cs = "".join(card(f, scores, sizing, central) for f in feats
                     if (f.get("workstream") or "Features") == L["name"])
        if not cs:
            continue
        sub = f'<span class="ls">{e(L["sub"])}</span>' if L.get("sub") else ""
        note = f'<p>{e(L["note"])}</p>' if L.get("note") else ""
        lanes += (f'<section class="lane" id="ws-{e(L["name"])}"><div class="lh">'
                  f'<h3>{e(L["name"])}{sub}</h3>{note}</div><div class="grid">{cs}</div></section>')

    arts = {}
    for f in feats:
        for a in f.get("produces") or []:
            arts.setdefault(a, {"prod": [], "cons": []})["prod"].append(f["key"])
        for a in f.get("consumes") or []:
            arts.setdefault(a, {"prod": [], "cons": []})["cons"].append(f["key"])
    led = ""
    for a, v in sorted(arts.items()):
        cons = " ".join(f'<a href="#{e(k)}" class="mini">{e(k)}</a>' for k in v["cons"]) \
            or "<em>terminal &#8212; consumed outside this corpus</em>"
        prod = " ".join(f'<a href="#{e(k)}" class="mini">{e(k)}</a>' for k in v["prod"]) \
            or "<em>unproduced</em>"
        led += (f'<tr class="{"term" if not v["cons"] else ""}"><td>{prod}</td>'
                f'<td class="an">{e(a)}</td><td>{cons}</td></tr>')

    TR = sum(f.get("ruleCount", 0) for f in feats)
    TS = sum(f.get("scenarioCount", 0) for f in feats)
    TQ = sum(len(f.get("openQuestions") or []) for f in feats)
    TN = sum(len(f.get("nfrTbd") or []) for f in feats)

    gov = ""
    if scores:
        vals = list(scores.values())
        nb = sum(1 for v in vals if v["decision"] == "Blocked")
        nok = sum(1 for v in vals if v["decision"] == "Approved")
        tb = sum(len(v.get("blockers") or []) for v in vals)
        mean = round(sum(v["score"] for v in vals) / len(vals), 1)
        gov = (f'<div class="stat g"><b>{nok}</b><span>Approved</span></div>'
               f'<div class="stat a"><b>{mean}</b><span>Mean readiness</span></div>'
               f'<div class="stat r"><b>{nb}</b><span>Token blocked</span></div>')
        govnote = (
            '<p class="govnote"><b>Readiness badges.</b> Every feature card carries a GovKit '
            '<b>Development Token</b> &#8212; <span class="tki tok-ok">Approved</span> '
            '<span class="tki tok-edit">Approved with edits</span> '
            '<span class="tki tok-block">Blocked</span> &#8212; with an advisory score out of 10 '
            "from the Gherkin Quality Rubric's ten dimensions. <b>The blocker list is the gate, "
            'not the number:</b> a feature can score above the bar and still be Blocked if one '
            "critical blocker stands. Open a card's <em>GovKit readiness</em> panel for the "
            'blockers, the ranked edits and the per-dimension breakdown. Scored in batch from the '
            'source record &#8212; a starting point for refinement, not a substitute for Product, '
            f'QA and Engineering reviewing Draft 0 together. {tb} critical blockers stand across '
            f'{nb} features.</p>')
        # Only where a commitment is actually shown. A page with no chips
        # does not need a paragraph about them, and an unconditional note
        # is one more thing readers learn to skip.
        # Same shape as the chip's own guard, and the same reason: a score
        # file is agent-produced, so `.get` on a non-dict aborts the page.
        # The review found one instance of this; there were two.
        if any(isinstance(v.get("commitment"), dict)
               and v["commitment"].get("commitment_id") for v in vals):
            govnote += (
                '<p class="govnote"><b>Commitment chips.</b> Where a card names a commitment, '
                'that is a <b>snapshot</b> of what was read when this page was generated. It '
                'does not gate anything and it can be out of date the moment it is written '
                '&#8212; the gate runs in CI, against a fresh read. A <em>blocked commitment</em> '
                'and a <em>Blocked</em> token are different failures: the first means the '
                'approval is gone and editing the package will not help, the second means the '
                'package is not ready yet.</p>')
        tkleg = ('<div class="legend tkleg"><span>The pill on each node is that feature&#39;s '
                 'GovKit readiness score out of 10. Colour is the Development Token, not the '
                 'number &#8212; a high score with an open blocker still reads as Blocked. Open '
                 'the feature card below for the blockers behind each one.</span></div>')
    else:
        govnote = tkleg = ""

    sizenote, szstats = "", ""
    if sizing:
        rolls = [sz.get("rollup") or {} for sz in sizing.values()]
        tp = sum(r.get("totalPoints", 0) for r in rolls)
        nl = sum(r.get("counts", {}).get("large", 0) for r in rolls)
        nrisk = sum(len(r.get("riskFlags") or []) for r in rolls)
        mvp_pts = sum(r.get("slicePoints", {}).get("mvp", 0) for r in rolls)
        szstats = f'<div class="stat"><b>{tp}</b><span>Size points</span></div>'
        if mvp_pts:
            szstats += f'<div class="stat"><b>{mvp_pts}</b><span>MVP points</span></div>'
        sizenote = (
            '<p class="govnote"><b>Size badges.</b> Sized cards carry a scenario-size '
            'distribution &#8212; <b>nL / nM / nS &#183; total points</b> &#8212; from the '
            'Scenario Complexity Matrix (Data &amp; State, Integration, UI/UX at 1&#8211;3 '
            'points each; Small 3&#8211;4, Medium 5&#8211;7, Large 8&#8211;9). Counts rather '
            'than an average, because the Large count is the risk signal an average hides. '
            "Open a card's <em>Scenario sizing</em> panel for the per-scenario breakdown. "
            'Slices marked <em>rec</em> are batch recommendations nobody has confirmed '
            '&#8212; the release plan is the team&#39;s decision, not the map&#39;s. '
            f'Judgments by govkit-feature-slice; all arithmetic by compute_size.py. '
            f'{nl} Large scenario(s) stand across the corpus, {nrisk} of them on an MVP '
            'critical path.</p>')

    has_slice_tags = any(scen_slice(sc) for f in feats for r in f.get("rules") or []
                         for sc in r.get("scenarios") or [])
    fltbar = ""
    if has_slice_tags:
        fltbar = ('<div class="fltbar"><span>Release slice</span>'
                  '<button class="on">All</button>'
                  '<button data-flt="mvp">@mvp</button>'
                  '<button data-flt="v1">@v1</button>'
                  '<button data-flt="v2">@v2</button>'
                  '<em>dims scenarios outside the slice &#8212; tagged slices only, '
                  'untagged scenarios dim under any filter</em></div>')

    title = cfg.get("title", "Feature Map")
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><style>{CSS}{WF_CSS}</style></head><body><div class="wrap">
<header class="top">
{f'<p class="eyebrow">{e(cfg["eyebrow"])}</p>' if cfg.get('eyebrow') else ''}
<h1>{e(title)}</h1>
{f'<p class="gov">{e(cfg["motto"])}</p>' if cfg.get('motto') else ''}
{f'<p class="lede">{e(cfg["lede"])}</p>' if cfg.get('lede') else ''}
<div class="stats">
<div class="stat"><b>{len(feats)}</b><span>Features</span></div>
<div class="stat"><b>{TR}</b><span>Rules</span></div>
<div class="stat"><b>{TS}</b><span>Scenarios</span></div>
<div class="stat"><b>{len(arts)}</b><span>Artifacts</span></div>
<div class="stat a"><b>{TQ}</b><span>Open questions</span></div>
<div class="stat a"><b>{TN}</b><span>NFR gaps</span></div>
{szstats}{gov}</div>{govnote}{sizenote}</header>
<h2>The chain</h2>
<p class="h2s">Every producer-to-consumer link in the corpus. Each arrow is a named artifact one
feature emits and the next reads.</p>
<div class="spinebox">{build_chain(feats, scores, cfg)}</div>
{workflow_section(workflow)}
<div class="legend"><span><i></i>{e(cfg.get('centralLabel','Runs centrally'))}</span>
<span><i></i>{e(cfg.get('deploymentLabel','Runs in the deployment'))}</span></div>
{tkleg}
{fltbar}
{lanes}
<h2>Artifact ledger</h2>
<p class="h2s">Every named artifact, who produces it and who consumes it.</p>
<table class="led"><tr><th>Produced by</th><th>Artifact</th><th>Consumed by</th></tr>{led}</table>
</div><script>{JS}</script></body></html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-f", "--features", required=True)
    ap.add_argument("-s", "--scores")
    ap.add_argument("-z", "--sizing",
                    help="computed sizing (compute_size.py output), keyed by feature key")
    ap.add_argument("-w", "--workflow",
                    help="resolved workflow (workflow_resolve.py output) — adds the L1/L2/L3 views")
    ap.add_argument("-c", "--config")
    ap.add_argument("-o", "--out", default="feature-map.html")
    a = ap.parse_args()

    feats = json.load(open(a.features))
    scores = {}
    if a.scores and os.path.isfile(a.scores):
        raw = json.load(open(a.scores))
        scores = {k: v for k, v in (raw.get("features", raw)).items()
                  if not k.startswith("_")}
    sizing = {}
    if a.sizing and os.path.isfile(a.sizing):
        raw = json.load(open(a.sizing))
        sizing = {k: v for k, v in (raw.get("features", raw)).items()
                  if not k.startswith("_")}
        raw_only = [k for k, v in sizing.items() if not v.get("rollup")]
        if raw_only:
            print(f"warning: {len(raw_only)} sizing entr(ies) have no rollup -- run "
                  f"compute_size.py first; skipping: {', '.join(raw_only)}")
            sizing = {k: v for k, v in sizing.items() if v.get("rollup")}
    cfg = json.load(open(a.config)) if a.config and os.path.isfile(a.config) else {}

    missing = [f["key"] for f in feats if f["key"] not in scores]
    if scores and missing:
        print(f"warning: {len(missing)} feature(s) unscored: {', '.join(missing)}")

    workflow = json.load(open(a.workflow)) if a.workflow and os.path.isfile(a.workflow) else None
    if a.workflow and workflow is None:
        print(f"warning: workflow file not found: {a.workflow} -- rendering without the journey views")

    doc = render(feats, scores, sizing, cfg, workflow)
    open(a.out, "w", encoding="utf-8").write(doc)
    wf_note = ""
    if workflow:
        cov = workflow.get("coverage") or {}
        wf_note = (f", workflow '{workflow.get('workflow')}' "
                   f"({len(cov.get('covered') or [])} covered, "
                   f"{len(cov.get('uncovered') or [])} uncovered)")
    print(f"{len(feats)} features, {len(scores)} scored, {len(sizing)} sized{wf_note} -> "
          f"{a.out} ({len(doc)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
