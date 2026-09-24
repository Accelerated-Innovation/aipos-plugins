#!/usr/bin/env python3
"""Render a Solution Framing canvas to HTML, and to PNG / PDF when a headless browser exists.

The render is a view of `canvas.json`, never a second source of truth:

  * it re-runs the verifier (verify_canvas.py, same folder) and draws derived numbers only from
    the freshly computed block — a stale `computed` in the file can never reach the page
  * facts carry their provenance mark; GAPs are drawn as chips with their formula, never as a
    placeholder number; provisional content is visibly lighter
  * the recommendation is drawn as a recommendation to a named owner, and Proceed is drawn as
    unavailable, with the reason, whenever the verifier says so
  * banners say when the canvas is a DRAFT, UNVERIFIED (verifier errors), built on the PM's
    account rather than the graph, or SYNTHETIC (mock graph) — a banner cannot be switched off

Usage:
  render_canvas.py canvas.json [--out DIR] [--no-image] [--browser PATH]

Writes canvas.html beside the canvas (or in --out). PNG and PDF are produced with a headless
Chrome / Chromium found on PATH, in the usual application locations, or at --browser / $CHROME_PATH.
Standard library only; colours and type come from brand.json.
"""

from __future__ import annotations

import argparse
import html
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
WIDTH, HEIGHT = 1600, 900
BROWSER_CANDIDATES = [
    "google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/opt/pw-browsers/chromium",
    *sorted(str(p) for p in Path("/opt/pw-browsers").glob("chromium-*/chrome-linux/chrome")),
    "C:/Program Files/Google/Chrome/Application/chrome.exe",
]


def load_verifier():
    spec = importlib.util.spec_from_file_location("verify_canvas", HERE / "verify_canvas.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ----------------------------------------------------------------------------- small pieces


def esc(value: object) -> str:
    return html.escape("" if value is None else str(value))


def D(node: object) -> dict:
    return node if isinstance(node, dict) else {}


def L(node: object) -> list:
    return node if isinstance(node, list) else []


def num(value: float | None, digits: int = 2) -> str:
    if value is None:
        return "GAP"
    text = f"{value:,.{digits}f}"
    if "." in text:  # strip trailing zeros from decimals only — never from 100
        text = text.rstrip("0").rstrip(".")
    return text.replace("-", "−")


def signed_pct(value: float | None) -> str:
    if value is None:
        return "GAP"
    sign = "+" if value > 0 else ""
    return f"{sign}{num(value, 1)}%"


def field_html(field: object, *, empty: str = "") -> str:
    """One field: its value, its provenance mark, or its GAP chip."""
    f = D(field)
    if not f:
        return f'<span class="gap">GAP</span>' if empty is None else esc(empty)
    if f.get("status") == "gap":
        kind = f.get("gap_type") or "evidence"
        assumed = D(f.get("assumed"))
        extra = (f' <span class="assumed">PM est. {esc(assumed.get("value"))} [A]</span>'
                 if assumed else "")
        return f'<span class="gap gap-{esc(kind)}">GAP · {esc(kind)}</span>{extra}'
    value = f.get("value")
    text = esc(num(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else value)
    cls = "prov" if f.get("status") == "provisional" else ""
    mark = f.get("mark")
    mark_html = f'<sup class="mark mark-{esc(mark)}">{esc(mark)}</sup>' if mark else ""
    return f'<span class="{cls}">{text}</span>{mark_html}'


def month(value: str | None) -> str:
    if not value:
        return "date unknown"
    months = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
    try:
        return f"{months[int(value[5:7]) - 1]} {value[:4]}"
    except (ValueError, IndexError):
        return esc(value)


def date_range(tile: dict) -> str:
    first, last = tile.get("earliest"), tile.get("latest")
    if not first and not last:
        return "date unknown"
    span = month(first) if month(first) == month(last) else f"{month(first)} – {month(last)}"
    if tile.get("undated"):
        span += f" · {tile['undated']} undated"
    return span


# ----------------------------------------------------------------------------- panels


def panel(number: int, title: str, body: str, cls: str = "") -> str:
    return (f'<section class="panel {cls}"><h2><span class="num">{number}</span>{esc(title)}</h2>'
            f'<div class="body">{body}</div></section>')


def problem_panel(c: dict) -> str:
    p = D(D(c.get("panels")).get("problem"))
    personas = D(p.get("personas"))
    pains = "".join(f"<li>{field_html(x)}</li>" for x in L(p.get("pain_points")))
    impact = "".join(f"<li>{field_html(x)}</li>" for x in L(p.get("impact")))
    snaps = "".join(
        f'<div class="snap"><span class="ref">{esc(D(s).get("ref"))}</span>{esc(D(s).get("label"))}</div>'
        if D(s).get("approved_for_canvas") else
        '<div class="snap muted">A real record — shown once the PM approves it</div>'
        for s in L(p.get("snapshot")))
    st = D(p.get("statement"))
    statement = (f'The problem of {field_html(st.get("problem"))} affects {field_html(st.get("affects"))}, '
                 f'resulting in {field_html(st.get("resulting_in"))}; solving it will lead to '
                 f'{field_html(st.get("benefits"))}.')
    others = ", ".join(esc(o) for o in L(personas.get("others")))
    return panel(1, "Problem & Context", f"""
      <div class="cols">
        <div><h3>Pain points</h3><ul class="pains">{pains}</ul>
             <h3>Impact</h3><ul class="pains">{impact}</ul></div>
        <div><h3>Current state</h3>{snaps or '<p class="muted">No readable records chosen</p>'}</div>
      </div>
      <p class="persona"><b>Primary:</b> {esc(personas.get("primary"))}{f" · <b>Also:</b> {others}" if others else ""}</p>
      <p class="statement">{statement}</p>""")


def evidence_panel(c: dict, computed: dict) -> str:
    e = D(D(c.get("panels")).get("evidence"))
    tiles_c = L(D(computed.get("evidence")).get("tiles"))
    tiles = []
    for i, tile in enumerate(L(e.get("tiles"))):
        t = D(tiles_c[i]) if i < len(tiles_c) else {}
        aging = '<span class="chip warn">aging</span>' if t.get("aging") else ""
        tiles.append(f"""<div class="sticky evidence"><div class="tile-head"><b>{esc(D(tile).get("label"))}</b>
          <span class="count">{esc(t.get("count", "?"))}</span></div>
          <div class="finding">{field_html(D(tile).get("finding"))}</div>
          <div class="meta">{date_range(t)} {aging}</div></div>""")
    voice = D(e.get("voice"))
    source = {D(r).get("provenance_reference"): D(r) for r in L(D(c.get("source")).get("evidence_refs"))}
    voice_html = ""
    if voice.get("quote") and not voice.get("approved_for_canvas"):
        voice_html = '<blockquote class="muted">A quote is chosen — shown once the PM approves it</blockquote>'
    elif voice.get("quote"):
        row = source.get(voice.get("provenance_reference"), {})
        attribution = f"{esc(str(row.get('source_type', 'source')).replace('_', ' '))}, {month(row.get('occurred_at'))}"
        voice_html = (f'<blockquote>“{esc(voice.get("quote"))}”<cite>{attribution} · '
                      f'{esc(voice.get("provenance_reference"))}</cite></blockquote>')
    ev = D(computed.get("evidence"))
    breadth = (f'{esc(ev.get("evidence_refs", 0))} references · {esc(ev.get("originating_sources", 0))} '
               f'originating source{"s" if ev.get("originating_sources") != 1 else ""}')
    if ev.get("single_source"):
        breadth += ' <span class="chip warn">single source</span>'
    if D(c.get("source")).get("kind") == "pm-interview":
        return panel(2, "Discovery Evidence", """
      <p class="empty">No graph evidence — this canvas rests on the PM's account. Rebuild it from the
      Product Definition Graph to show what the evidence establishes.</p>""")
    return panel(2, "Discovery Evidence", f"""
      <div class="grid2">{''.join(tiles)}</div>{voice_html}
      <p class="meta breadth">{breadth} · read {month(ev.get("as_of"))}</p>""")


def hypothesis_panel(c: dict, computed: dict) -> str:
    panels = D(c.get("panels"))
    h = D(panels.get("hypothesis"))
    metrics = {D(m).get("id"): D(m) for m in L(panels.get("metrics"))}
    cm = D(computed.get("metrics"))
    cards = []
    for mid in L(h.get("outcomes")):
        m, k = metrics.get(mid, {}), D(cm.get(mid))
        big = signed_pct(k.get("change_pct")) if k.get("change_pct") is not None else (
            signed_pct(k.get("declared_pct")) if k.get("declared_pct") is not None else "GAP")
        if k.get("change_kind") == "points" and k.get("declared_pct") is not None and k.get("change_pct") is None:
            big = big.replace("%", " pts")
        base = D(m.get("baseline"))
        note = ("baseline GAP" if base.get("status") == "gap" else
                f"{num(base.get('value'))} → {num(k.get('target'))} {esc(m.get('unit', ''))}")
        primary = '<span class="chip primary">primary</span>' if m.get("primary") else ""
        cards.append(f"""<div class="sticky outcome"><div class="outcome-name">{esc(m.get("name"))} {primary}</div>
          <div class="big">{esc(big)}</div><div class="meta">{note}</div></div>""")
    return panel(3, "Hypothesis", f"""
      <p class="hyp"><b>If</b> {field_html(h.get("if"))}, <b>then</b> {field_html(h.get("then"))},
         <b>without</b> {field_html(h.get("without"))}.</p>
      <h3>Expected outcomes</h3><div class="grid3">{''.join(cards)}</div>""")


def options_panel(c: dict) -> str:
    panels = D(c.get("panels"))
    recommended = panels.get("recommended_option")
    cols = []
    for o in L(panels.get("options")):
        o = D(o)
        rec = '<div><span class="chip primary rec-chip">recommended</span></div>' if o.get("id") == recommended else ""
        preview = "".join(f"<div>{esc(x)}</div>" for x in L(o.get("preview")))
        pros = "".join(f"<li>{esc(x)}</li>" for x in L(o.get("pros")))
        cons = "".join(f"<li>{esc(x)}</li>" for x in L(o.get("cons")))
        cols.append(f"""<div class="option{' rec' if rec else ''}"><div class="opt-head"><span class="letter">{esc(o.get("id"))}</span>
          <b>{esc(o.get("name"))}</b></div>{rec}<p class="approach">{field_html(o.get("approach"))}</p>
          {f'<div class="preview">{preview}</div>' if preview else ''}
          <div class="pc"><span class="pro">Pros</span><ul>{pros}</ul><span class="con">Cons</span><ul>{cons}</ul></div></div>""")
    return panel(4, "Solution Options", f'<div class="options n{len(cols)}">{"".join(cols)}</div>')


def risks_panel(c: dict) -> str:
    panels = D(c.get("panels"))
    from_gap = ' <span class="chip gapsrc">from GAP</span>'
    assumptions = "".join(
        f'<div class="sticky assumption">{esc(D(a).get("text"))}'
        f'{from_gap if D(a).get("from_gap") else ""}</div>'
        for a in L(panels.get("assumptions")))
    risks = "".join(
        f'<div class="risk-row"><div class="sticky risk">{esc(D(r).get("text"))}</div>'
        f'<div class="sticky mitigation">{esc(D(r).get("mitigation")) if D(r).get("mitigation") else "<b>Unmitigated</b>"}</div></div>'
        for r in L(panels.get("risks")))
    return panel(5, "Assumptions & Risks", f"""
      <h3>Key assumptions</h3><div class="grid3 tight">{assumptions}</div>
      <h3>Risks → mitigations</h3>{risks}""")


def validation_panel(c: dict, computed: dict) -> str:
    panels = D(c.get("panels"))
    v = D(panels.get("validation"))
    plan = "".join(
        f'<li><span class="check">✓</span>{esc(D(i).get("action"))}'
        f'<span class="owner"> — {field_html(D(i).get("owner"))}{", by " + esc(D(i).get("by")) if D(i).get("by") else ""}</span></li>'
        for i in L(v.get("plan")))
    primary = next((D(m) for m in L(panels.get("metrics")) if D(m).get("primary")), {})
    k = D(D(computed.get("metrics")).get(primary.get("id")))
    base = D(primary.get("baseline"))
    base_txt = "GAP" if base.get("status") == "gap" else num(base.get("value"))
    numeric_target = k.get("target") is not None
    target_txt = num(k.get("target")) if numeric_target else (
        signed_pct(k.get("declared_pct")) if k.get("declared_pct") is not None else "GAP")
    unit_txt = esc(primary.get("unit", "")) if numeric_target else ""
    rec = D(v.get("recommendation"))
    chosen = rec.get("decision")
    available = computed.get("proceed_available", False)
    buttons = []
    for key, label, sub in (("pivot", "Pivot", "Reassess the approach"),
                            ("proceed", "Proceed", "Pilot and validate"),
                            ("park", "Park", "Defer for later")):
        blocked = key == "proceed" and not available
        cls = "btn" + (" chosen" if key == chosen else "") + (" disabled" if blocked else "")
        why = ""
        if key == "proceed" and not available:
            why = f'<div class="why">Unavailable: {esc("; ".join(L(computed.get("proceed_blocked_by"))))}</div>'
        buttons.append(f'<div class="{cls}"><b>{label}</b><div>{sub}</div>{why}</div>')
    owner = field_html(rec.get("owner")) if rec.get("owner") else '<span class="gap">no owner</span>'
    status = (f"Recommended to {owner}" if chosen else f"Recommendation open · decided by {owner}")
    return panel(6, "Validation & Decision", f"""
      <div class="cols">
        <div><h3>Validation plan</h3><ul class="plan">{plan}</ul></div>
        <div><div class="metric-box"><div class="meta">Primary metric</div><b>{esc(primary.get("name"))}</b>
          <div class="big">{esc(base_txt)} <span class="arrow">→</span> {esc(target_txt)}
          <span class="unit">{unit_txt}</span></div>
          <div class="meta">{esc(k.get("formula") or "")}</div></div></div>
      </div>
      <div class="decision"><div class="meta">{status}</div><div class="btns">{''.join(buttons)}</div>
        {f'<p class="rationale">{esc(rec.get("rationale"))}</p>' if rec.get("rationale") else ''}</div>""")


def footer_html(c: dict, computed: dict) -> str:
    f = D(c.get("footer"))
    impact = D(computed.get("impact_at_scale"))
    if impact.get("result") is not None:
        value = f'<span class="big">{num(impact["result"], 0)}</span> {esc(impact.get("result_unit", ""))}'
    else:
        value = '<span class="gap">GAP</span>'
    formula = esc(impact.get("formula") or "")
    return f"""<footer>
      <div><span class="label">Who benefits</span>{' · '.join(esc(x) for x in L(f.get("who_benefits")))}</div>
      <div><span class="label">Success looks like</span>{field_html(f.get("success"))}</div>
      <div><span class="label">Impact at scale</span>{value} <span class="formula">{formula}
        {esc(impact.get("volume_unit", "")) and "(" + esc(impact.get("volume_unit")) + ")"}</span></div>
    </footer>"""


# ----------------------------------------------------------------------------- page


def banners(c: dict, report) -> list[str]:
    src = D(c.get("source"))
    out = []
    synthetic = ("mock" in str(src.get("server", "")).lower()
                 or str(src.get("problem_id", "")).startswith("fixture:")
                 or "[SYNTHETIC]" in str(src.get("title", "")))
    if synthetic:
        out.append(("synthetic", "SYNTHETIC — built from the mock graph; nothing here is evidence"))
    if report.errors:
        out.append(("unverified", f"UNVERIFIED — {len(report.errors)} verifier error"
                                  f"{'s' if len(report.errors) != 1 else ''}; not for sharing"))
    if src.get("kind") == "pm-interview":
        out.append(("pm", "Built on the PM's account — not backed by the Product Definition Graph"))
    if c.get("stage") != "approved":
        reached = c.get("through_panel", 8)
        label = "DRAFT" if reached == 8 else (
            f"DRAFT — through panel {reached}" if isinstance(reached, int) and reached <= 6
            else "DRAFT — footer done, not yet reviewed")
        out.append(("draft", label))
    return out


def css(brand: dict) -> str:
    col, sticky = brand["colors"], brand["sticky"]
    return f"""
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:{WIDTH}px;height:{HEIGHT}px;font-family:{brand["font_family"]};color:{col["ink"]};background:{col["page"]};font-size:10.5px;line-height:1.35;overflow:hidden}}
.page{{width:{WIDTH}px;height:{HEIGHT}px;display:flex;flex-direction:column;padding:0 0 10px}}
header{{background:{brand["header_gradient"]};color:#fff;display:flex;align-items:center;gap:18px;padding:12px 22px;height:70px;flex:none}}
header .kicker{{font-size:11px;letter-spacing:.14em;text-transform:uppercase;opacity:.85;font-weight:600}}
header h1{{font-size:26px;font-weight:700;line-height:1.1}}
header .goal{{margin-left:auto;max-width:430px;text-align:right}}
header .goal b{{display:block;font-size:10px;letter-spacing:.14em;text-transform:uppercase;opacity:.8}}
header .goal span{{font-size:14px;font-weight:600}}
.banners{{display:flex;gap:6px;padding:6px 22px 0;flex:none}}
.banner{{font-size:10px;font-weight:700;letter-spacing:.06em;padding:3px 10px;border-radius:3px;color:#fff}}
.banner.synthetic{{background:{col["accent"]}}} .banner.unverified{{background:{col["red"]}}}
.banner.pm{{background:{col["blue"]}}} .banner.draft{{background:{col["muted"]}}}
main{{flex:1;display:grid;grid-template-columns:1fr 1fr 1fr;grid-template-rows:1fr 1.08fr;gap:10px;padding:8px 14px 0;min-height:0}}
.panel{{background:{col["paper"]};border-radius:8px;box-shadow:0 1px 3px rgba(25,0,79,.12);display:flex;flex-direction:column;min-height:0;overflow:hidden}}
.panel h2{{background:{col["dark"]};color:#fff;font-size:12.5px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;padding:6px 10px;display:flex;align-items:center;gap:8px}}
.num{{background:{col["highlight"]};color:{col["dark"]};width:20px;height:20px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:11px}}
.body{{padding:8px 10px;overflow:hidden;flex:1;display:flex;flex-direction:column;gap:5px}}
h3{{font-size:10px;text-transform:uppercase;letter-spacing:.08em;color:{col["primary"]};margin:2px 0 3px}}
.cols{{display:grid;grid-template-columns:1fr 1fr;gap:10px}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:6px}} .grid3{{display:grid;grid-template-columns:repeat(3,1fr);gap:6px}}
ul{{list-style:none}} .pains li{{padding-left:10px;position:relative;margin-bottom:3px}}
.pains li:before{{content:"";position:absolute;left:0;top:5px;width:5px;height:5px;border-radius:50%;background:{col["accent"]}}}
.snap{{border:1px solid #e3e1ee;border-radius:5px;padding:4px 6px;margin-bottom:4px;font-size:10px}}
.snap .ref{{display:block;color:{col["muted"]};font-size:9px}}
.persona{{font-size:10px;color:{col["muted"]}}}
.statement{{background:#f6f5fb;border-left:3px solid {col["primary"]};padding:5px 8px;font-size:10.5px}}
.sticky{{border-radius:5px;padding:5px 7px;font-size:10px;box-shadow:0 1px 2px rgba(0,0,0,.08)}}
.sticky.evidence{{background:{sticky["evidence"]}}} .sticky.outcome{{background:{sticky["outcome"]};text-align:center}}
.sticky.assumption{{background:{sticky["assumption"]}}} .sticky.risk{{background:{sticky["risk"]}}} .sticky.mitigation{{background:{sticky["mitigation"]}}}
.tile-head{{display:flex;justify-content:space-between;align-items:baseline}}
.count{{font-size:18px;font-weight:700;color:{col["primary"]}}}
.finding{{margin:2px 0}} .meta{{font-size:9px;color:{col["muted"]}}}
blockquote{{border-left:3px solid {col["accent"]};padding:3px 8px;font-style:italic;font-size:11px}}
cite{{display:block;font-style:normal;font-size:9px;color:{col["muted"]}}}
.breadth{{margin-top:auto}}
.hyp{{font-size:12.5px;line-height:1.4;padding:4px 2px}}
.outcome-name{{font-size:10px;font-weight:600;min-height:26px}}
.big{{font-size:24px;font-weight:700;color:{col["dark"]}}}
.options{{display:grid;gap:8px;height:100%}} .options.n2{{grid-template-columns:1fr 1fr}} .options.n3{{grid-template-columns:repeat(3,1fr)}}
.option{{border:1px solid #e3e1ee;border-radius:6px;padding:6px;display:flex;flex-direction:column;gap:4px;min-height:0;overflow:hidden}}
.option.rec{{border:2px solid {col["primary"]}}}
.opt-head{{display:flex;align-items:flex-start;gap:6px;font-size:11px;line-height:1.25}} .rec-chip{{margin-left:24px}}
.letter{{background:{col["primary"]};color:#fff;width:18px;height:18px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-weight:700;flex:none}}
.preview{{background:#f6f5fb;border-radius:4px;padding:4px 6px;font-size:9.5px;color:{col["dark"]}}}
.pc ul{{margin:1px 0 3px 10px;list-style:disc}} .pro{{color:{col["green"]};font-weight:700;font-size:9.5px}} .con{{color:{col["red"]};font-weight:700;font-size:9.5px}}
.tight .sticky{{font-size:9.5px}}
.risk-row{{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:4px}}
.plan li{{margin-bottom:4px;padding-left:14px;position:relative}} .check{{position:absolute;left:0;color:{col["green"]};font-weight:700}}
.owner{{color:{col["muted"]}}}
.metric-box{{border:1px solid #e3e1ee;border-radius:6px;padding:6px 8px;text-align:center}}
.metric-box .big{{font-size:22px}} .arrow{{color:{col["highlight"]}}} .unit{{font-size:12px;font-weight:600}}
.decision{{margin-top:auto}}
.btns{{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin-top:3px}}
.btn{{border:1px solid #d9d6e8;border-radius:6px;padding:5px;text-align:center;font-size:9.5px;color:{col["muted"]}}}
.btn b{{display:block;font-size:12px;color:{col["dark"]}}}
.btn.chosen{{background:{col["primary"]};border-color:{col["primary"]};color:#fff}} .btn.chosen b{{color:#fff}}
.btn.disabled{{background:repeating-linear-gradient(135deg,#f4f3f8,#f4f3f8 6px,#ebe9f3 6px,#ebe9f3 12px);opacity:.9}}
.btn.chosen.disabled{{border:2px solid {col["red"]};color:{col["muted"]}}} .btn.chosen.disabled b{{color:{col["red"]}}}
.why{{color:{col["red"]};font-size:8.5px;margin-top:2px}}
.rationale{{font-size:9.5px;color:{col["muted"]};margin-top:3px}}
footer{{display:grid;grid-template-columns:1fr 1.3fr 1.3fr;gap:10px;padding:8px 14px 0;flex:none}}
footer>div{{background:{col["dark"]};color:#fff;border-radius:8px;padding:8px 12px;font-size:11px;min-height:44px;display:flex;align-items:center;gap:8px;flex-wrap:wrap}}
footer .label{{color:{col["highlight"]};font-weight:700;font-size:10px;text-transform:uppercase;letter-spacing:.08em;margin-right:4px}}
footer .big{{color:{col["yellow"]};font-size:18px}} footer .formula{{opacity:.75;font-size:10px}}
.gap{{display:inline-block;border:1.5px dashed {col["accent"]};color:{col["accent"]};border-radius:10px;padding:0 6px;font-size:9px;font-weight:700;letter-spacing:.03em;white-space:nowrap;background:#fff}}
.gap-decision{{border-color:{col["blue"]};color:{col["blue"]}}}
footer .gap{{background:transparent;color:#fff;border-color:#fff}}
.assumed{{font-size:9px;color:{col["muted"]}}}
.prov{{opacity:.72;font-style:italic;border-bottom:1px dotted {col["muted"]}}}
.mark{{font-size:7.5px;font-weight:700;margin-left:2px;color:{col["primary"]}}} .mark-I{{color:{col["yellow"]}}}
.chip{{font-size:8.5px;font-weight:700;border-radius:8px;padding:1px 6px;margin-left:3px;white-space:nowrap}}
.chip.primary{{background:{col["primary"]};color:#fff}} .chip.warn{{background:{col["red"]};color:#fff}} .chip.gapsrc{{background:{col["accent"]};color:#fff}}
.muted{{color:{col["muted"]}}} .empty{{color:{col["muted"]};font-style:italic;margin:auto;max-width:70%;text-align:center}}
.meta-line{{padding:4px 16px 0;font-size:8.5px;color:{col["muted"]};flex:none;display:flex;justify-content:space-between}}
"""


def render_html(canvas: dict, computed: dict, report, brand: dict) -> str:
    c = canvas
    title = D(c.get("title")).get("value") or "Solution Framing"
    goal = field_html(c.get("goal"))
    banner_html = "".join(f'<span class="banner {k}">{esc(t)}</span>' for k, t in banners(c, report))
    src = D(c.get("source"))
    gaps = D(computed.get("gaps"))
    read = ("no graph read" if src.get("kind") == "pm-interview"
            else f'graph read {month(D(computed.get("evidence")).get("as_of"))}')
    meta = (f'{esc(src.get("problem_id") or "no graph problem")} · {read}'
            f' · GAPs: {gaps.get("evidence", 0)} evidence, {gaps.get("decision", 0)} decision'
            f' · verifier: {"ok" if not report.errors else str(len(report.errors)) + " errors"}')
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>{esc(title)} — Solution Framing</title><style>{css(brand)}</style></head>
<body><div class="page">
<header><div><div class="kicker">Solution Framing · {esc(brand.get("wordmark", ""))}</div><h1>{esc(title)}</h1></div>
<div class="goal"><b>Goal</b><span>{goal}</span></div></header>
<div class="banners">{banner_html}</div>
<main>
{problem_panel(c)}{evidence_panel(c, computed)}{hypothesis_panel(c, computed)}
{options_panel(c)}{risks_panel(c)}{validation_panel(c, computed)}
</main>
{footer_html(c, computed)}
<div class="meta-line"><span>{meta}</span><span>[E] evidence-backed · [I] inferred · GAP = not yet in the graph / not yet decided</span></div>
</div></body></html>"""


# ----------------------------------------------------------------------------- images


def find_browser(explicit: str | None) -> str | None:
    for candidate in [explicit, os.environ.get("CHROME_PATH"), *BROWSER_CANDIDATES]:
        if not candidate:
            continue
        found = shutil.which(candidate) or (candidate if Path(candidate).is_file() else None)
        if found:
            return found
    return None


def capture(browser: str, page: Path, png: Path, pdf: Path) -> tuple[list[str], list[str]]:
    """PDF from Chrome (exact: sized by the page's @page rule), PNG rasterised from that PDF.

    Chrome's own --screenshot is not used first: in new-headless mode its viewport comes out
    shorter than --window-size, which silently crops the bottom of a fixed-size page — the
    footer, where impact at scale lives. The PDF has no such problem, so the PNG is made from it.
    """
    made, notes, url = [], [], page.resolve().as_uri()
    with tempfile.TemporaryDirectory() as profile:
        base = [browser, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
                f"--user-data-dir={profile}", "--no-first-run", "--no-default-browser-check"]
        _run(base + ["--no-pdf-header-footer", "--print-to-pdf-no-header", f"--print-to-pdf={pdf}", url])
        if _ok(pdf):
            made.append(pdf.name)
            if rasterise(pdf, png):
                made.append(png.name)
        if png.name not in made:
            # Last resort: pad the window so the page's full height fits the shorter viewport.
            _run(base + [f"--window-size={WIDTH},{HEIGHT + 120}", "--force-device-scale-factor=2",
                         f"--screenshot={png}", url])
            if _ok(png):
                made.append(png.name)
                notes.append("PNG came from a browser screenshot and has a blank strip at the "
                             "bottom; the PDF is the exact render")
    return made, notes


def rasterise(pdf: Path, png: Path) -> bool:
    """PDF -> PNG at 2x with whatever the platform has: poppler, or macOS Quick Look / sips."""
    if shutil.which("pdftoppm"):
        _run(["pdftoppm", "-png", "-r", "192", "-singlefile", str(pdf), str(png.with_suffix(""))])
        if _ok(png):
            return True
    if shutil.which("qlmanage"):
        with tempfile.TemporaryDirectory() as tmp:
            _run(["qlmanage", "-t", "-s", str(WIDTH * 2), "-o", tmp, str(pdf)])
            thumb = Path(tmp) / f"{pdf.name}.png"
            if _ok(thumb):
                shutil.copyfile(thumb, png)
                return True
    if shutil.which("sips"):
        _run(["sips", "-s", "format", "png", "--resampleWidth", str(WIDTH * 2), str(pdf), "--out", str(png)])
        if _ok(png):
            return True
    return False


def _run(cmd: list[str]) -> None:
    try:
        subprocess.run(cmd, capture_output=True, timeout=90, check=False)
    except (OSError, subprocess.TimeoutExpired):
        pass


def _ok(path: Path) -> bool:
    return path.is_file() and path.stat().st_size > 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("canvas", type=Path)
    parser.add_argument("--out", type=Path, help="output folder (default: beside the canvas)")
    parser.add_argument("--no-image", action="store_true", help="write HTML only")
    parser.add_argument("--browser", help="path to a Chrome / Chromium binary")
    parser.add_argument("--brand", type=Path, default=HERE / "brand.json")
    args = parser.parse_args(argv)

    canvas = json.loads(args.canvas.read_text(encoding="utf-8"))
    report, computed = load_verifier().verify(canvas)
    brand = json.loads(args.brand.read_text(encoding="utf-8"))
    out = args.out or args.canvas.parent
    out.mkdir(parents=True, exist_ok=True)
    stem = args.canvas.stem
    page = out / f"{stem}.html"
    # Print CSS so the PDF is one landscape page at the canvas size.
    html_text = render_html(canvas, computed, report, brand).replace(
        "</style>", f"@page{{size:{WIDTH}px {HEIGHT}px;margin:0}}</style>")
    page.write_text(html_text, encoding="utf-8")
    made, notes = [page.name], []
    if not args.no_image:
        browser = find_browser(args.browser)
        if browser:
            images, notes = capture(browser, page, out / f"{stem}.png", out / f"{stem}.pdf")
            made += images
        else:
            print("no headless Chrome/Chromium found — wrote HTML only "
                  "(pass --browser or set CHROME_PATH)", file=sys.stderr)
    print(json.dumps({"written": made, "folder": str(out), "verifier_errors": len(report.errors),
                      "banners": [k for k, _ in banners(canvas, report)], "notes": notes}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
