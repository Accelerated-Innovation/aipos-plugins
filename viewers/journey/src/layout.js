// Left-to-right layout with dagre. Customer order runs left to right, then the
// features an activity uses, then their Rules and scenarios.
import dagre from "@dagrejs/dagre";

export const SIZES = {
  journey: { width: 230, height: 76 },
  activity: { width: 230, height: 84 },
  missing: { width: 180, height: 48 },
  feature: { width: 250, height: 92 },
  unresolved: { width: 230, height: 64 },
  rule: { width: 250, height: 60 },
  scenario: { width: 250, height: 58 },
};

export function layout(nodes, edges, pinned = {}) {
  const g = new dagre.graphlib.Graph();
  g.setGraph({ rankdir: "LR", nodesep: 18, ranksep: 60, marginx: 10, marginy: 10 });
  g.setDefaultEdgeLabel(() => ({}));
  // dagre writes x/y onto the label object it is given, so each node needs its
  // own copy; sharing SIZES entries put every node of a kind at one position.
  for (const n of nodes) g.setNode(n.id, { ...(SIZES[n.kind] || SIZES.activity) });
  // A branch condition is a label on its edge. Giving dagre the label's size
  // makes it leave room between the ranks instead of drawing it under a node.
  for (const e of edges) {
    g.setEdge(e.source, e.target, e.condition
      ? { width: 7 * e.condition.length + 16, height: 18, labelpos: "c" }
      : {});
  }
  dagre.layout(g);

  const out = new Map();
  for (const n of nodes) {
    const size = SIZES[n.kind] || SIZES.activity;
    const p = g.node(n.id);
    // A hand-set position wins: a stakeholder-facing journey reads better laid
    // out by a person, and config.json positions are that escape hatch.
    const pin = pinned[n.id];
    out.set(n.id, pin ? { x: pin.x, y: pin.y } : { x: p.x - size.width / 2, y: p.y - size.height / 2 });
  }
  return out;
}
