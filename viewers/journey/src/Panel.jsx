// The detail panel. It answers whatever question the current selection asks:
// a journey lists the scenarios that specify it, a feature lists the journeys
// its change would affect, a scenario shows its Given / When / Then.
import { Actor } from "./nodes.jsx";
import { affectedJourneys, indexNodes, sliceTags, specifyingScenarios } from "./model.js";

function plural(n, word) {
  return `${n} ${word}${n === 1 ? "" : "s"}`;
}

function Pick({ id, onSelect, children }) {
  return (
    <button type="button" className="jv-link" onClick={() => onSelect(id)}>
      {children}
    </button>
  );
}

function Where({ refs }) {
  if (!refs || refs.length === 0) return <p className="jv-muted">Referenced nowhere on this page.</p>;
  return (
    <ul className="jv-list">
      {refs.map((r, i) => (
        <li key={i}>
          <b>{r.journey}</b> · {r.activity}
          {r.step ? <span className="jv-muted"> · step {r.step}</span> : null}
        </li>
      ))}
    </ul>
  );
}

function Source({ source }) {
  if (!source) return null;
  const label = `${source.path}${source.line ? `:${source.line}` : ""}`;
  return (
    <p className="jv-source">
      {source.href ? <a href={source.href} target="_blank" rel="noopener">{label}</a>
        : <code>{label}</code>}
    </p>
  );
}

function Table({ rows, header }) {
  return (
    <table className="jv-table">
      {header && (
        <thead><tr>{header.map((h, i) => <th key={i}>{h}</th>)}</tr></thead>
      )}
      <tbody>
        {rows.map((r, i) => <tr key={i}>{r.map((c, j) => <td key={j}>{c}</td>)}</tr>)}
      </tbody>
    </table>
  );
}

function Steps({ steps, muted }) {
  return (
    <ol className={`jv-steps${muted ? " jv-muted" : ""}`}>
      {steps.map((s, i) => (
        <li key={i}>
          {s.keyword && <b>{s.keyword} </b>}{s.text}
          {s.dataTable && <Table rows={s.dataTable.slice(1)} header={s.dataTable[0]} />}
          {s.docString && <pre className="jv-doc">{s.docString.content}</pre>}
        </li>
      ))}
    </ol>
  );
}

function ScenarioDetail({ n, onSelect, byId }) {
  const rule = byId.get(n.rule);
  const feat = byId.get(n.feature);
  return (
    <>
      <p className="jv-kind">Scenario{n.type === "scenario_outline" ? " outline" : ""}</p>
      <h3>{n.name}</h3>
      <p className="jv-crumbs">
        <Pick id={feat.id} onSelect={onSelect}>{feat.name}</Pick> ›{" "}
        <Pick id={rule.id} onSelect={onSelect}>{rule.name}</Pick>
      </p>
      <p>
        <code>scenario:{n.slug}</code>
        {n.idSource === "derived" && <span className="jv-warn"> derived id — cannot be approved</span>}
        {sliceTags(n.tags).map((t) => <span key={t} className="jv-chip">{t}</span>)}
      </p>
      {n.background.length > 0 && (
        <>
          <h4>Background</h4>
          <Steps steps={n.background} muted />
        </>
      )}
      <h4>Steps</h4>
      <Steps steps={n.steps} />
      {n.examples.map((ex, i) => (
        <div key={i}>
          <h4>Examples{ex.name ? `: ${ex.name}` : ""}</h4>
          <Table header={ex.header} rows={ex.rows || []} />
        </div>
      ))}
      <h4>Referenced at</h4>
      <Where refs={n.refs} />
      <h4>Source</h4>
      <Source source={n.source} />
    </>
  );
}

function JourneyDetail({ graph, journey, onSelect }) {
  const j = graph.journeys.find((x) => x.id === journey);
  const { referenced, underReferencedRule } = specifyingScenarios(graph, journey);
  return (
    <>
      <p className="jv-kind">Journey</p>
      <h3>{journey}</h3>
      <p>{j?.outcome}</p>
      {j && (j.errors > 0 || !j.ok) && (
        <p className="jv-warn">{j.errors} error(s) in this workflow — see Diagnostics below the diagram.</p>
      )}
      <h4>Scenarios that specify this journey <span className="jv-count">{referenced.length}</span></h4>
      {referenced.length === 0 ? <p className="jv-muted">None referenced.</p> : (
        <ul className="jv-list">
          {referenced.map((s) => <li key={s.id}><Pick id={s.id} onSelect={onSelect}>{s.name}</Pick></li>)}
        </ul>
      )}
      {underReferencedRule.length > 0 && (
        <>
          <h4>Under a referenced rule, not placed <span className="jv-count">{underReferencedRule.length}</span></h4>
          <p className="jv-muted">The journey names their Rule but not these scenarios, so they are not counted as specifying it.</p>
          <ul className="jv-list">
            {underReferencedRule.map((s) => <li key={s.id}><Pick id={s.id} onSelect={onSelect}>{s.name}</Pick></li>)}
          </ul>
        </>
      )}
    </>
  );
}

function FeatureDetail({ graph, n, onSelect, onFocus }) {
  const affected = affectedJourneys(graph, n.id);
  const rules = graph.nodes.filter((m) => m.kind === "rule" && m.feature === n.id);
  return (
    <>
      <p className="jv-kind">Feature <code>{n.key}</code></p>
      <h3>{n.name}</h3>
      {n.partial && <p className="jv-warn">Some Gherkin in this feature does not parse; counts are a floor.</p>}
      <h4>Journeys affected if this feature changes <span className="jv-count">{affected.length}</span></h4>
      {affected.length === 0 ? <p className="jv-muted">No journey on this page uses it.</p> : (
        <ul className="jv-list">
          {affected.map(({ journey, activities }) => (
            <li key={journey}>
              <Pick id={`j:${journey}`} onSelect={onSelect}><b>{journey}</b></Pick>
              {" · "}
              {activities.map((a, i) => (
                <span key={a.id}>{i > 0 && ", "}<Pick id={a.id} onSelect={onSelect}>{a.name}</Pick></span>
              ))}
            </li>
          ))}
        </ul>
      )}
      <h4>Rules <span className="jv-count">{rules.length}</span></h4>
      <ul className="jv-list">
        {rules.map((r) => <li key={r.id}><Pick id={r.id} onSelect={onSelect}>{r.name}</Pick></li>)}
      </ul>
      <p className="jv-actions">
        <button type="button" onClick={() => onFocus(n.id)}>Show only this feature’s scenarios</button>
        <a href={`#${encodeURIComponent(n.key)}`}>Open the feature card</a>
      </p>
    </>
  );
}

function RuleDetail({ graph, n, onSelect, byId }) {
  const scenarios = graph.nodes.filter((m) => m.kind === "scenario" && m.rule === n.id);
  return (
    <>
      <p className="jv-kind">Rule</p>
      <h3>{n.name}</h3>
      <p className="jv-crumbs"><Pick id={n.feature} onSelect={onSelect}>{byId.get(n.feature)?.name}</Pick></p>
      <p><code>rule:{n.slug}</code>{n.idSource === "derived" && <span className="jv-warn"> derived id — cannot be approved</span>}</p>
      {n.description && <p>{n.description}</p>}
      <h4>Scenarios <span className="jv-count">{scenarios.length}</span></h4>
      <ul className="jv-list">
        {scenarios.map((s) => <li key={s.id}><Pick id={s.id} onSelect={onSelect}>{s.name}</Pick></li>)}
      </ul>
      <h4>Referenced at</h4>
      <Where refs={n.refs} />
      <h4>Source</h4>
      <Source source={n.source} />
    </>
  );
}

function ActivityDetail({ graph, n, onSelect, byId }) {
  const uses = graph.edges.filter((e) => e.source === n.id && e.kind === "uses");
  const next = graph.edges.filter((e) => e.source === n.id && e.kind === "next");
  return (
    <>
      <p className="jv-kind">Activity · <Pick id={`j:${n.journey}`} onSelect={onSelect}>{n.journey}</Pick></p>
      <h3>{n.name}</h3>
      <p><Actor actor={n.actor} /></p>
      <h4>Handoffs <span className="jv-count">{n.handoffs.length}</span></h4>
      {n.handoffs.length === 0 ? <p className="jv-muted">None recorded on this activity’s steps.</p> : (
        <ul className="jv-list">
          {n.handoffs.map((h) => <li key={h.step}>{h.stepName}: <b>{h.from}</b> → <b>{h.to}</b></li>)}
        </ul>
      )}
      {n.steps.length > 0 && (
        <>
          <h4>Steps</h4>
          <ul className="jv-list">{n.steps.map((s) => <li key={s.id}>{s.name} <span className="jv-muted">({s.actor})</span></li>)}</ul>
        </>
      )}
      <h4>Then</h4>
      {next.length === 0 ? <p className="jv-muted">Ends the journey.</p> : (
        <ul className="jv-list">
          {next.map((e) => (
            <li key={e.target}>
              {e.dangling ? <span className="jv-warn">{byId.get(e.target)?.name} — no such activity</span>
                : <Pick id={e.target} onSelect={onSelect}>{byId.get(e.target)?.name}</Pick>}
              {e.condition && <span className="jv-muted"> when {e.condition}</span>}
            </li>
          ))}
        </ul>
      )}
      <h4>Features used <span className="jv-count">{uses.length}</span></h4>
      <ul className="jv-list">
        {uses.map((e) => <li key={e.target}><Pick id={e.target} onSelect={onSelect}>{byId.get(e.target)?.name}</Pick></li>)}
      </ul>
    </>
  );
}

function Overview({ graph, onSelect }) {
  return (
    <>
      <p className="jv-kind">This page</p>
      <h3>{graph.journeys.length} journey{graph.journeys.length === 1 ? "" : "s"}</h3>
      <ul className="jv-list">
        {graph.journeys.map((j) => (
          <li key={j.id}>
            <Pick id={`j:${j.id}`} onSelect={onSelect}><b>{j.id}</b></Pick>{" "}
            <span className="jv-muted">
              {plural((graph.index.scenariosByJourney[j.id]?.referenced || []).length, "scenario")} specify it
              {j.errors > 0 ? ` · ${j.errors} error(s)` : ""}
            </span>
          </li>
        ))}
      </ul>
      <h4>In no journey on this page <span className="jv-count">{graph.uncovered.length}</span></h4>
      <p className="jv-muted">
        Rules and scenarios no journey references. Legitimate if they belong to a journey not on
        this page, but unreferenced behavior is behavior these journeys imply does not exist.
      </p>
      <p className="jv-muted">Select a journey, activity, feature or scenario to see what it connects to.</p>
    </>
  );
}

export function Panel({ graph, selected, onSelect, onFocus }) {
  const byId = indexNodes(graph);
  const n = selected ? byId.get(selected) : null;
  let body;
  if (!n) body = <Overview graph={graph} onSelect={onSelect} />;
  else if (n.kind === "journey") body = <JourneyDetail graph={graph} journey={n.journey} onSelect={onSelect} />;
  else if (n.kind === "activity") body = <ActivityDetail graph={graph} n={n} onSelect={onSelect} byId={byId} />;
  else if (n.kind === "feature") body = <FeatureDetail graph={graph} n={n} onSelect={onSelect} onFocus={onFocus} />;
  else if (n.kind === "rule") body = <RuleDetail graph={graph} n={n} onSelect={onSelect} byId={byId} />;
  else if (n.kind === "scenario") body = <ScenarioDetail n={n} onSelect={onSelect} byId={byId} />;
  else if (n.kind === "unresolved") body = (
    <>
      <p className="jv-kind jv-warn">Unresolved reference</p>
      <h3 className="jv-mono">{n.ref}</h3>
      <p>{n.why}. It is shown where it was written and links nowhere, because linking it would imply behavior this corpus does not hold.</p>
      <h4>Written at</h4>
      <Where refs={n.refs} />
    </>
  );
  else body = <p className="jv-warn">{n.name}: {n.reason}</p>;

  return (
    <aside className="jv-panel" aria-live="polite">
      {n && <button type="button" className="jv-clear" onClick={() => onSelect(null)}>Clear selection</button>}
      {body}
    </aside>
  );
}
