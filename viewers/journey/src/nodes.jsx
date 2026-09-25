// Custom React Flow nodes. Each is a card that says what it is before it says
// anything else, because a reader scanning a large map reads kinds first.
import { Handle, Position } from "@xyflow/react";
import { sliceTags } from "./model.js";

const ACTOR_MARK = { human: "●", system: "■", agent: "◆", tool: "▲" };

const PLACEMENT_LABEL = {
  referenced: null,
  "under-referenced-rule": "under a referenced rule",
  uncovered: "in no journey",
  outside: "not in this journey",
};

function Ports() {
  return (
    <>
      <Handle type="target" position={Position.Left} isConnectable={false} />
      <Handle type="source" position={Position.Right} isConnectable={false} />
    </>
  );
}

function Shell({ data, kind, children }) {
  const cls = ["jv-node", `jv-${kind}`];
  if (data.dim) cls.push("jv-dim");
  if (data.on) cls.push("jv-on");
  if (data.placement) cls.push(`jv-p-${data.placement}`);
  return (
    <div className={cls.join(" ")} title={data.title}>
      <Ports />
      {children}
    </div>
  );
}

export function Actor({ actor }) {
  if (!actor) return <span className="jv-actor jv-muted">no actor</span>;
  return (
    <span className={`jv-actor jv-k-${actor.kind || "unknown"}`}>
      <i aria-hidden="true">{ACTOR_MARK[actor.kind] || "○"}</i>
      {actor.name || actor.id}
    </span>
  );
}

function JourneyNode({ data }) {
  const n = data.node;
  return (
    <Shell data={data} kind="journey">
      <div className="jv-kind">Journey</div>
      <div className="jv-title">{n.name}</div>
      <div className="jv-sub">{n.outcome}</div>
    </Shell>
  );
}

function ActivityNode({ data }) {
  const n = data.node;
  const h = n.handoffs.length;
  return (
    <Shell data={data} kind="activity">
      <div className="jv-kind">Activity</div>
      <div className="jv-title">{n.name}</div>
      <div className="jv-meta">
        <Actor actor={n.actor} />
        {h > 0 && <span className="jv-badge">{h} handoff{h > 1 ? "s" : ""}</span>}
      </div>
    </Shell>
  );
}

function MissingNode({ data }) {
  return (
    <Shell data={data} kind="missing">
      <div className="jv-kind jv-warn">No such activity</div>
      <div className="jv-title">{data.node.name}</div>
    </Shell>
  );
}

function FeatureNode({ data }) {
  const n = data.node;
  const j = data.journeyCount;
  return (
    <Shell data={data} kind="feature">
      <div className="jv-kind">Feature <span className="jv-key">{n.key}</span></div>
      <div className="jv-title">{n.name}</div>
      <div className="jv-meta">
        <span>{n.ruleCount} rule{n.ruleCount === 1 ? "" : "s"} · {n.scenarioCount} scenario{n.scenarioCount === 1 ? "" : "s"}</span>
        {j === 0 ? <span className="jv-badge jv-warn">in no journey</span>
          : j > 1 ? <span className="jv-badge">{j} journeys</span> : null}
        {n.partial && <span className="jv-badge jv-warn">partial parse</span>}
      </div>
    </Shell>
  );
}

function RuleNode({ data }) {
  const n = data.node;
  const note = PLACEMENT_LABEL[data.placement];
  return (
    <Shell data={data} kind="rule">
      <div className="jv-kind">Rule {note && <span className="jv-note">{note}</span>}</div>
      <div className="jv-title jv-clamp">{n.name}</div>
    </Shell>
  );
}

function ScenarioNode({ data }) {
  const n = data.node;
  const note = PLACEMENT_LABEL[data.placement];
  return (
    <Shell data={data} kind="scenario">
      <div className="jv-kind">
        Scenario
        {sliceTags(n.tags).map((t) => <span key={t} className="jv-chip">{t}</span>)}
        {n.idSource === "derived" && <span className="jv-note jv-warn">derived id</span>}
        {note && <span className="jv-note">{note}</span>}
      </div>
      <div className="jv-title jv-clamp">{n.name}</div>
    </Shell>
  );
}

function UnresolvedNode({ data }) {
  const n = data.node;
  return (
    <Shell data={data} kind="unresolved">
      <div className="jv-kind jv-warn">Unresolved · {n.why}</div>
      <div className="jv-title jv-mono jv-clamp">{n.ref}</div>
    </Shell>
  );
}

export const nodeTypes = {
  journey: JourneyNode,
  activity: ActivityNode,
  missing: MissingNode,
  feature: FeatureNode,
  rule: RuleNode,
  scenario: ScenarioNode,
  unresolved: UnresolvedNode,
};
