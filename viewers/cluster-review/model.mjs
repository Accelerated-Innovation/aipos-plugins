// Cluster Review board — pure logic. No DOM and no network, so node --test pins every rule.
// The board compares candidate problems and prepares corrections as pending hand-offs.
// Nothing here applies a correction: there is no engine correction path to apply it to.

export const STALE_AFTER_HOURS = 24;
const NO_DESTINATION =
  'TBD — no engine correction path exists (merge/split corrections were retired); owner: product and engine leads';

const byId = (review, id) => {
  const problem = review.problems.find(p => p.problem_id === id);
  if (!problem) throw new Error(`unknown problem ${id}`);
  return problem;
};
const refsOf = problem => problem.evidence.map(e => e.provenance_reference);
const intersect = (a, b) => [...new Set(a)].filter(x => b.includes(x)).sort();
const minus = (a, b) => [...new Set(a)].filter(x => !b.includes(x)).sort();

export function compare(review, a, b) {
  const pa = byId(review, a), pb = byId(review, b);
  const ra = refsOf(pa), rb = refsOf(pb);
  return {
    shared_evidence: intersect(ra, rb),
    shared_origins: intersect(pa.originating_sources, pb.originating_sources),
    shared_personas: intersect(pa.personas.map(p => p.name), pb.personas.map(p => p.name)),
    only: {[a]: minus(ra, rb), [b]: minus(rb, ra)},
  };
}

export function signalsFor(review, id) {
  return (review.signals || []).filter(s => s.problems.includes(id));
}

export function isStale(capturedAt, nowIso, hours = STALE_AFTER_HOURS) {
  return Date.parse(nowIso) - Date.parse(capturedAt) > hours * 3600 * 1000;
}

export function prepareCorrection(review, suggestionId, nowIso) {
  const s = (review.suggestions || []).find(x => x.id === suggestionId);
  if (!s) throw new Error(`unknown suggestion ${suggestionId}`);
  const stale = isStale(review.source.captured_at, nowIso);
  const correction = {
    suggestion: s.id,
    kind: s.kind,
    problems: [...s.problems],
    rationale: s.rationale,
    basis: s.basis,
    status: 'pending',
    applied: false,
    destination: NO_DESTINATION,
    prepared_at: nowIso,
    based_on_capture: review.source.captured_at,
    stale,
    before_applying: [
      `Re-read ${s.problems.join(', ')} from the graph: this was prepared from a capture taken ${review.source.captured_at}.`,
      'A person with authority over the problem inventory decides, and applies it through whatever correction path the engine provides.',
    ],
  };
  if (stale) correction.before_applying.unshift('The capture is more than a day old: re-read before anyone relies on this.');
  if (s.kind === 'merge') correction.evidence = structuredClone(s.evidence);
  else correction.sides = structuredClone(s.sides);
  return correction;
}

export function handoff(corrections) {
  return JSON.stringify({
    kind: 'cluster-correction-request',
    draft: true,
    note: 'Prepared for hand-off. Not applied: no engine correction path exists, and this board writes nothing.',
    corrections,
  }, null, 2);
}

export function sourceLabel(source) {
  const mode = source.mode === 'connected'
    ? `Connected read${source.server ? ` (${source.server})` : ''}`
    : 'Supplied records';
  return `${mode}${source.synthetic ? ' · synthetic' : ''} · captured ${source.captured_at}`;
}
