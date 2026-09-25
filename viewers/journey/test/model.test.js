// The viewer's own logic: what each level shows and what a selection lights up.
// Facts about the graph (coverage, placement, who uses what) are tested in
// Python, where they are computed; this fixture is that Python output, kept
// current by tests/test_journey_graph.py.
import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import {
  affectedJourneys, highlightSet, placementFor, specifyingScenarios, visibleGraph,
} from "../src/model.js";

const graph = JSON.parse(readFileSync(new URL("./fixtures/two-journeys.graph.json", import.meta.url)));

const INV_FULL = "f:acme/FEATURE-inv_full";
const INV_PARTNER = "f:acme/FEATURE-inv_partner";
const PARTNER_AWAY = "acme/FEATURE-inv_partner#scenario:partner-manager-unavailable";
const ROUTING = "acme/FEATURE-inv_full#scenario:approval-routing-by-amount";

const kinds = (v) => new Set(v.nodes.map((n) => n.kind));
const ids = (v) => new Set(v.nodes.map((n) => n.id));

describe("levels add detail to the level above", () => {
  it("L1 shows journeys and activities only", () => {
    expect(kinds(visibleGraph(graph, { level: 1 }))).toEqual(new Set(["journey", "activity"]));
  });

  it("L2 adds features and unresolved references", () => {
    const k = kinds(visibleGraph(graph, { level: 2 }));
    expect(k.has("feature") && k.has("unresolved")).toBe(true);
    expect(k.has("scenario")).toBe(false);
  });

  it("L3 adds rules and scenarios", () => {
    const k = kinds(visibleGraph(graph, { level: 3 }));
    expect(k.has("rule") && k.has("scenario")).toBe(true);
  });

  it("never draws an edge to a node it hides", () => {
    for (const level of [1, 2, 3]) {
      const v = visibleGraph(graph, { level, journey: "threshold-setup" });
      const shown = ids(v);
      for (const e of v.edges) expect(shown.has(e.source) && shown.has(e.target)).toBe(true);
    }
  });
});

describe("scope", () => {
  it("a journey scope keeps only that journey's activities and features", () => {
    const v = visibleGraph(graph, { level: 2, journey: "threshold-setup" });
    const shown = ids(v);
    expect(shown.has(INV_FULL)).toBe(true);
    expect(shown.has(INV_PARTNER)).toBe(false);
    expect([...shown].some((id) => id.startsWith("j:invoice-approval"))).toBe(false);
  });

  it("all journeys includes features no journey uses, so they can be seen", () => {
    expect(ids(visibleGraph(graph, { level: 2 })).has("f:acme/FEATURE-legacy_simple")).toBe(true);
  });

  it("a feature focus narrows L3 to that feature's rules and scenarios", () => {
    const v = visibleGraph(graph, { level: 3, feature: INV_PARTNER });
    const features = v.nodes.filter((n) => n.kind === "feature").map((n) => n.id);
    expect(features).toEqual([INV_PARTNER]);
    expect(v.nodes.filter((n) => n.kind === "scenario").every((n) => n.feature === INV_PARTNER)).toBe(true);
  });
});

describe("the two questions", () => {
  it("selecting a shared feature lights every journey that uses it", () => {
    const on = highlightSet(graph, INV_FULL);
    expect(on.has("j:invoice-approval")).toBe(true);
    expect(on.has("j:threshold-setup")).toBe(true);
    expect(on.has("j:invoice-approval/a:partner-approve")).toBe(false);
  });

  it("the affected-journeys list names journeys and their activities", () => {
    const got = affectedJourneys(graph, INV_FULL).map((x) => [x.journey, x.activities.map((a) => a.activity).sort()]);
    expect(got).toEqual([
      ["invoice-approval", ["approve", "route"]],
      ["threshold-setup", ["confirm-routing", "set-threshold"]],
    ]);
  });

  it("the specifying scenarios keep referenced and under-a-rule apart", () => {
    const got = specifyingScenarios(graph, "invoice-approval");
    expect(got.referenced.map((s) => s.id)).not.toContain(PARTNER_AWAY);
    expect(got.underReferencedRule.map((s) => s.id)).toEqual([PARTNER_AWAY]);
  });

  it("a scenario's placement is relative to the journey in scope", () => {
    const n = graph.nodes.find((x) => x.id === ROUTING);
    expect(placementFor(n, graph, "threshold-setup")).toBe("referenced");
    const away = graph.nodes.find((x) => x.id === PARTNER_AWAY);
    expect(placementFor(away, graph, "threshold-setup")).toBe("outside");
    expect(placementFor(away, graph, null)).toBe("under-referenced-rule");
  });

  it("selecting a scenario lights the activities that reference it", () => {
    const on = highlightSet(graph, ROUTING);
    expect(on.has("j:invoice-approval/a:route")).toBe(true);
    expect(on.has("j:threshold-setup/a:confirm-routing")).toBe(true);
  });

  it("no selection highlights nothing", () => {
    expect(highlightSet(graph, null)).toBeNull();
  });
});
