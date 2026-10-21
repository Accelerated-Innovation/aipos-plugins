import {compare, prepareCorrection, isStale, signalsFor, handoff, sourceLabel} from './model.mjs';

// DOM layer: renders the review and keeps prepared corrections in page memory only.
const $ = sel => document.querySelector(sel);
const el = (tag, attrs = {}, ...children) => {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === 'class') node.className = v;
    else if (k.startsWith('on')) node.addEventListener(k.slice(2), v);
    else if (v !== false && v != null) node.setAttribute(k, v === true ? '' : v);
  }
  for (const child of children.flat()) if (child != null) node.append(child.nodeType ? child : document.createTextNode(String(child)));
  return node;
};
const now = () => (globalThis.__BOARD_NOW__ || new Date().toISOString());

let review;
const selected = [];
const prepared = new Map();

function banner() {
  const stale = isStale(review.source.captured_at, now());
  $('#source').textContent = sourceLabel(review.source);
  const c = review.coverage || {};
  const failed = (c.failed || []).length;
  $('#coverage').textContent = `${c.problems_listed ?? review.problems.length} of ${c.problems_total ?? '?'} problems read` +
    (failed ? ` · ${failed} read${failed === 1 ? '' : 's'} failed: ${(c.failed || []).map(f => `${f.problem_id} (${f.code})`).join(', ')}` : '');
  $('#stale').hidden = !stale;
}

function problemRow(p) {
  const count = signalsFor(review, p.problem_id).length;
  const box = el('input', {type: 'checkbox', id: `pick-${p.problem_id}`, 'data-problem': p.problem_id,
    'aria-label': `Compare ${p.problem_id}`, checked: selected.includes(p.problem_id),
    disabled: selected.length >= 2 && !selected.includes(p.problem_id), onchange: () => toggle(p.problem_id)});
  const systems = [...new Set(p.evidence.map(e => e.source_system))].sort().join(', ') || '—';
  return el('tr', {'data-row': p.problem_id},
    el('td', {}, box),
    el('th', {scope: 'row'}, el('span', {class: 'pid'}, p.problem_id), el('span', {class: 'title'}, p.title)),
    el('td', {'data-label': 'Personas'}, p.personas.map(x => el('span', {class: 'chip'}, `${x.name} · ${Math.round(x.confidence * 100)}%`))),
    el('td', {'data-label': 'Evidence'}, `${p.evidence.length} ref${p.evidence.length === 1 ? '' : 's'}`, el('small', {}, systems)),
    el('td', {class: 'muted', 'data-label': 'Workflow tags'}, p.workflow_tags == null ? 'unknown — not in the graph' : (p.workflow_tags.join(', ') || 'none')),
    el('td', {'data-label': 'Overlaps'}, count ? `${count} overlap${count === 1 ? '' : 's'}` : '—'));
}

function renderProblems() {
  const body = $('#rows');
  body.replaceChildren(...review.problems.map(problemRow));
  $('#no-problems').hidden = review.problems.length > 0;
}

function toggle(id) {
  const at = selected.indexOf(id);
  if (at >= 0) selected.splice(at, 1); else if (selected.length < 2) selected.push(id);
  renderProblems();
  renderCompare();
  document.getElementById(`pick-${id}`)?.focus();
}

function refList(refs) {
  return refs.length ? el('ul', {class: 'refs'}, refs.map(r => el('li', {}, el('code', {}, r)))) : el('p', {class: 'muted'}, 'none');
}

function renderCompare() {
  const panel = $('#compare');
  if (selected.length < 2) {
    panel.replaceChildren(el('p', {class: 'muted'}, selected.length ? `Pick one more problem to compare with ${selected[0]}.` : 'Pick two problems to compare their evidence.'));
    return;
  }
  const [a, b] = selected;
  const c = compare(review, a, b);
  panel.replaceChildren(
    el('h3', {}, `${a} ↔ ${b}`),
    el('div', {class: 'grid'},
      el('section', {}, el('h4', {}, 'Shared evidence'), refList(c.shared_evidence)),
      el('section', {}, el('h4', {}, 'Shared origins'), refList(c.shared_origins)),
      el('section', {}, el('h4', {}, 'Shared personas'), refList(c.shared_personas)),
      el('section', {}, el('h4', {}, `Only ${a}`), refList(c.only[a])),
      el('section', {}, el('h4', {}, `Only ${b}`), refList(c.only[b]))),
    el('p', {class: 'muted'}, 'Overlap is where to look, not a verdict: problems drawn from one source can still be different problems.'));
}

function suggestionCard(s) {
  const done = prepared.has(s.id);
  const evidence = s.kind === 'merge'
    ? Object.entries(s.evidence).map(([pid, refs]) => el('div', {}, el('h4', {}, pid), refList(refs)))
    : s.sides.map(side => el('div', {}, el('h4', {}, `${side.label}${side.persona ? ` (${side.persona})` : ''}`), refList(side.evidence)));
  return el('article', {class: 'card', 'data-suggestion': s.id},
    el('header', {}, el('span', {class: `kind ${s.kind}`}, s.kind), ' ', s.problems.join(' + '),
      el('span', {class: 'basis', title: s.basis === 'E' ? 'evidence-backed' : 'inferred'}, `[${s.basis}]`)),
    el('p', {}, s.rationale),
    el('div', {class: 'grid'}, evidence),
    el('button', {type: 'button', disabled: done, 'data-prepare': s.id, onclick: () => prepare(s.id)},
      done ? 'Prepared — pending' : 'Prepare correction (pending)'));
}

function renderSuggestions() {
  const list = review.suggestions || [];
  $('#suggestions').replaceChildren(...list.map(suggestionCard));
  $('#no-suggestions').hidden = list.length > 0;
}

function renderExcerpts() {
  const list = review.excerpts || [];
  $('#excerpts').replaceChildren(...list.map(x => el('figure', {class: 'excerpt'},
    el('blockquote', {}, x.excerpt),
    el('figcaption', {}, 'Redacted excerpt · ', el('code', {}, x.provenance_reference), ` · ${x.problem_id}`, x.truncated ? ' · truncated' : ''))));
  $('#excerpt-count').textContent = `${list.length} of at most 5`;
}

function prepare(id) {
  prepared.set(id, prepareCorrection(review, id, now()));
  renderSuggestions();
  renderPrepared();
  $('#prepared-heading').focus();
}

function renderPrepared() {
  const items = [...prepared.values()];
  $('#prepared-list').replaceChildren(...items.map(c => el('li', {'data-prepared': c.suggestion},
    el('strong', {}, `${c.kind} ${c.problems.join(' + ')}`), ` — ${c.status}, not applied`, c.stale ? ' · stale capture' : '',
    ' ', el('button', {type: 'button', class: 'link', onclick: () => { prepared.delete(c.suggestion); renderSuggestions(); renderPrepared(); }}, 'Remove'))));
  $('#handoff').value = items.length ? handoff(items) : '';
  $('#prepared-empty').hidden = items.length > 0;
  $('#handoff-wrap').hidden = items.length === 0;
}

async function copyHandoff() {
  const box = $('#handoff');
  box.select();
  try { await navigator.clipboard.writeText(box.value); $('#copy-status').textContent = 'Copied.'; }
  catch { $('#copy-status').textContent = 'Selected — press Ctrl+C or ⌘C to copy.'; }
}

function start() {
  try {
    review = JSON.parse(document.getElementById('review-data').textContent);
    banner(); renderProblems(); renderCompare(); renderSuggestions(); renderExcerpts(); renderPrepared();
    $('#copy').addEventListener('click', copyHandoff);
    $('#board').hidden = false;
  } catch (error) {
    $('#error').hidden = false;
    $('#error').textContent = `This board could not be shown: ${error.message}`;
  }
}
start();
