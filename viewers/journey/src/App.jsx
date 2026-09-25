import { useCallback, useMemo, useState } from "react";
import { Background, Controls, MarkerType, MiniMap, ReactFlow } from "@xyflow/react";
import { layout, SIZES } from "./layout.js";
import { highlightSet, indexNodes, LEVELS, placementFor, visibleGraph } from "./model.js";
import { nodeTypes } from "./nodes.jsx";
import { Panel } from "./Panel.jsx";

const EDGE_STYLE = {
  starts: { className: "jv-e-starts" },
  next: { className: "jv-e-next", markerEnd: { type: MarkerType.ArrowClosed } },
  uses: { className: "jv-e-uses" },
  contains: { className: "jv-e-contains" },
  unresolved: { className: "jv-e-unresolved" },
};

export function App({ graph, config }) {
  const byId = useMemo(() => indexNodes(graph), [graph]);
  const [level, setLevel] = useState(1);
  // Start unscoped even with one journey: the out-of-journey features are part
  // of the finding, and with a single journey there is no selector to widen to.
  const [journey, setJourney] = useState(null);
  const [feature, setFeature] = useState(null);
  const [selected, setSelected] = useState(null);

  const visible = useMemo(
    () => visibleGraph(graph, { level, journey, feature }),
    [graph, level, journey, feature],
  );
  const positions = useMemo(
    () => layout(visible.nodes, visible.edges, config.positions || {}),
    [visible, config],
  );
  const lit = useMemo(() => highlightSet(graph, selected), [graph, selected]);

  const nodes = visible.nodes.map((n) => ({
    id: n.id,
    type: n.kind,
    position: positions.get(n.id),
    width: SIZES[n.kind]?.width,
    height: SIZES[n.kind]?.height,
    selected: n.id === selected,
    ariaLabel: `${n.kind} ${n.name || n.ref || ""}`,
    data: {
      node: n,
      on: lit ? lit.has(n.id) : false,
      dim: lit ? !lit.has(n.id) : false,
      placement: placementFor(n, graph, journey),
      journeyCount: (graph.index.journeysByFeature[n.id] || []).length,
    },
  }));

  const edges = visible.edges.map((e) => {
    const dim = lit && !(lit.has(e.source) && lit.has(e.target));
    const style = EDGE_STYLE[e.kind] || {};
    return {
      id: `${e.kind}:${e.source}->${e.target}`,
      source: e.source,
      target: e.target,
      type: "smoothstep",
      label: e.condition || undefined,
      className: `${style.className || ""}${e.dangling ? " jv-e-dangling" : ""}${dim ? " jv-dim" : ""}`,
      markerEnd: style.markerEnd,
      focusable: false,
    };
  });

  // Selecting something the current view does not show (a scenario picked from
  // a journey's list while on L1, say) moves to where it can be seen.
  const select = useCallback((id) => {
    setSelected(id);
    const n = id ? byId.get(id) : null;
    if (!n) return;
    if (n.level > level) setLevel(n.level);
    if (feature && n.feature && n.feature !== feature) setFeature(null);
    if (journey && n.journey && n.journey !== journey) setJourney(null);
  }, [byId, level, feature, journey]);

  const focusFeature = useCallback((fid) => {
    setFeature(fid);
    setLevel(3);
  }, []);

  // React Flow nodes are focusable; Enter or Space on one selects it, the same
  // as a click. The tables below remain the complete keyboard route.
  const onKeyDown = (ev) => {
    if (ev.key !== "Enter" && ev.key !== " ") return;
    const el = document.activeElement?.closest?.(".react-flow__node");
    if (el?.dataset?.id) {
      ev.preventDefault();
      select(el.dataset.id);
    }
  };

  const scope = `${level}|${journey || "*"}|${feature || "*"}`;
  const focused = feature ? byId.get(feature) : null;

  return (
    <div className="jv" onKeyDown={onKeyDown}>
      <div className="jv-bar" role="toolbar" aria-label="Journey diagram controls">
        <div className="jv-levels" role="group" aria-label="Level">
          {LEVELS.map((l) => (
            <button key={l.level} type="button" title={l.hint} aria-pressed={level === l.level}
              onClick={() => setLevel(l.level)}>{l.label}</button>
          ))}
        </div>
        {graph.journeys.length > 1 && (
          <label className="jv-scope">
            Journey{" "}
            <select value={journey || ""} onChange={(ev) => { setJourney(ev.target.value || null); setSelected(null); }}>
              <option value="">All journeys</option>
              {graph.journeys.map((j) => <option key={j.id} value={j.id}>{j.id}</option>)}
            </select>
          </label>
        )}
        {focused && (
          <span className="jv-focus">
            Only {focused.key}
            <button type="button" aria-label="Show all features" onClick={() => setFeature(null)}>×</button>
          </span>
        )}
        <span className="jv-hint">{LEVELS[level - 1].hint}</span>
      </div>
      <div className="jv-body">
        <div className="jv-canvas">
          <ReactFlow
            key={scope}
            nodes={nodes}
            edges={edges}
            nodeTypes={nodeTypes}
            fitView
            fitViewOptions={{ padding: 0.12 }}
            minZoom={0.15}
            nodesConnectable={false}
            elementsSelectable
            onNodeClick={(_, n) => select(n.id)}
            onPaneClick={() => setSelected(null)}
          >
            <Background gap={18} size={1} />
            <Controls showInteractive={false} />
            <MiniMap pannable zoomable style={{ width: 150, height: 96 }} />
          </ReactFlow>
        </div>
        <Panel graph={graph} selected={selected} onSelect={select} onFocus={focusFeature} />
      </div>
    </div>
  );
}
