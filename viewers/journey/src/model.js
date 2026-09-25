// What each level shows, and what a selection highlights.
//
// Every fact here is a lookup into the graph journey_graph.py built: which
// journey an activity belongs to, which features a journey uses, which
// scenarios specify it. Nothing is resolved or counted again in the browser,
// so the diagram cannot disagree with the Python model or the fallback tables.

export const LEVELS = [
  { level: 1, label: "L1 Journey", hint: "Activities in customer order, with actors and handoffs" },
  { level: 2, label: "L2 Features", hint: "The features and Rules each activity uses" },
  { level: 3, label: "L3 Scenarios", hint: "The scenarios under each Rule" },
];

const KINDS_BY_LEVEL = {
  1: new Set(["journey", "activity", "missing"]),
  2: new Set(["journey", "activity", "missing", "feature", "unresolved"]),
  3: new Set(["journey", "activity", "missing", "feature", "unresolved", "rule", "scenario"]),
};

const EDGES_BY_LEVEL = {
  1: new Set(["starts", "next"]),
  2: new Set(["starts", "next", "uses", "unresolved"]),
  3: new Set(["starts", "next", "uses", "unresolved", "contains"]),
};

export function indexNodes(graph) {
  const byId = new Map();
  for (const n of graph.nodes) byId.set(n.id, n);
  return byId;
}

function inJourney(n, journey, graph) {
  if (!journey) return true;
  switch (n.kind) {
    case "journey":
    case "activity":
    case "missing":
      return n.journey === journey;
    case "feature":
      return (graph.index.journeysByFeature[n.id] || []).includes(journey);
    case "unresolved":
      return (n.refs || []).some((r) => r.journey === journey);
    default:
      return true; // rules and scenarios follow their feature
  }
}

// The nodes and edges a level shows, within the chosen scope.
//
// `journey` narrows to one journey's activities and the features it uses.
// `feature` narrows L3 to one feature's Rules and scenarios, so a large corpus
// stays readable. Neither scope changes a fact; they only hide what is out of
// scope.
export function visibleGraph(graph, { level, journey = null, feature = null }) {
  const byId = indexNodes(graph);
  const kinds = KINDS_BY_LEVEL[level];
  const keep = new Set();

  for (const n of graph.nodes) {
    if (!kinds.has(n.kind)) continue;
    if (n.kind === "rule" || n.kind === "scenario") continue; // decided by their feature below
    if (n.kind === "feature" && feature && n.id !== feature && level === 3) continue;
    if (!inJourney(n, journey, graph)) continue;
    keep.add(n.id);
  }

  if (level === 3) {
    for (const n of graph.nodes) {
      if ((n.kind === "rule" || n.kind === "scenario") && keep.has(n.feature)) keep.add(n.id);
    }
  }

  const edgeKinds = EDGES_BY_LEVEL[level];
  const edges = graph.edges.filter(
    (e) => edgeKinds.has(e.kind) && keep.has(e.source) && keep.has(e.target),
  );
  return { nodes: [...keep].map((id) => byId.get(id)), edges };
}

// A scenario's standing, relative to the journey in scope. With no journey in
// scope it is the page-wide placement the Python model computed.
export function placementFor(node, graph, journey) {
  if (node.kind !== "scenario" && node.kind !== "rule") return null;
  if (!journey) return node.placement;
  if (node.kind === "rule") {
    return (node.refs || []).some((r) => r.journey === journey) ? "referenced" : "outside";
  }
  const got = graph.index.scenariosByJourney[journey] || { referenced: [], underReferencedRule: [] };
  if (got.referenced.includes(node.id)) return "referenced";
  if (got.underReferencedRule.includes(node.id)) return "under-referenced-rule";
  return "outside";
}

// The ids a selection lights up. Everything else is dimmed, not hidden, so the
// reader keeps the surrounding journey in view.
export function highlightSet(graph, selectedId) {
  if (!selectedId) return null;
  const byId = indexNodes(graph);
  const n = byId.get(selectedId);
  if (!n) return null;
  const on = new Set([n.id]);
  const activities = graph.index.activitiesByFeature || {};

  const addFeature = (fid) => {
    on.add(fid);
    for (const m of graph.nodes) if (m.feature === fid) on.add(m.id);
  };
  const addActivity = (aid) => {
    const a = byId.get(aid);
    if (!a) return;
    on.add(aid);
    on.add(`j:${a.journey}`);
  };

  switch (n.kind) {
    case "journey":
      for (const m of graph.nodes) if (m.journey === n.journey) on.add(m.id);
      for (const fid of featuresOfJourney(graph, n.journey)) on.add(fid);
      break;
    case "activity":
      on.add(`j:${n.journey}`);
      for (const e of graph.edges) {
        if (e.source === n.id && (e.kind === "uses" || e.kind === "unresolved")) on.add(e.target);
      }
      break;
    case "feature":
      // Question 2: which journeys are affected if this feature changes.
      addFeature(n.id);
      for (const aid of activities[n.id] || []) addActivity(aid);
      break;
    case "rule":
    case "scenario":
      on.add(n.feature);
      if (n.rule) on.add(n.rule);
      for (const m of graph.nodes) if (n.kind === "rule" && m.rule === n.id) on.add(m.id);
      for (const r of n.refs || []) addActivity(`j:${r.journey}/a:${r.activity}`);
      break;
    case "unresolved":
      for (const r of n.refs || []) addActivity(`j:${r.journey}/a:${r.activity}`);
      break;
    default:
      break;
  }
  return on;
}

export function featuresOfJourney(graph, journey) {
  return Object.entries(graph.index.journeysByFeature)
    .filter(([, js]) => js.includes(journey))
    .map(([fid]) => fid);
}

// Question 1, as the panel lists it: the scenarios that specify a journey, and
// separately the ones that only sit under a Rule it references.
export function specifyingScenarios(graph, journey) {
  const byId = indexNodes(graph);
  const got = graph.index.scenariosByJourney[journey] || { referenced: [], underReferencedRule: [] };
  return {
    referenced: got.referenced.map((id) => byId.get(id)).filter(Boolean),
    underReferencedRule: got.underReferencedRule.map((id) => byId.get(id)).filter(Boolean),
  };
}

// Question 2, as the panel lists it: the journeys and activities that use a feature.
export function affectedJourneys(graph, featureId) {
  const byId = indexNodes(graph);
  const acts = (graph.index.activitiesByFeature[featureId] || []).map((id) => byId.get(id));
  const out = new Map();
  for (const a of acts) {
    if (!a) continue;
    if (!out.has(a.journey)) out.set(a.journey, []);
    out.get(a.journey).push(a);
  }
  return [...out.entries()].map(([journey, activities]) => ({ journey, activities }));
}

export const SLICE_TAGS = ["@mvp", "@v1", "@v2"];

export function sliceTags(tags) {
  return (tags || []).filter((t) => SLICE_TAGS.includes(t));
}
