// The opportunities panel: state, rendering and interaction. Vanilla DOM, built with textContent
// only, so nothing the engine returns is ever parsed as markup. All host traffic goes through
// bridge.mjs; all shaping through model.mjs.
import {connectBridge} from './bridge.mjs';
import {
  COMPONENTS, LINK_FILTERS, SORTS, coverage, errorView, evidence, filterRows, formatScore,
  mergeHostContext, mergePage, palette, personas, provenance, sortRows, validateEvidence,
  validateProblem,
} from './model.mjs';

/* global __PANEL_VERSION__ */
const VERSION = typeof __PANEL_VERSION__ === 'string' ? __PANEL_VERSION__ : '0.0.0-dev';
// Tests pin the clock through this global; the host never sets it.
const now = () => globalThis.__PANEL_NOW__ || new Date().toISOString();

const state = {
  host: {},
  phase: 'connecting', // connecting | waiting | ready | error | cancelled | disconnected
  error: null,
  list: null,
  server: null,
  readAt: null,
  search: '',
  linked: 'all',
  sort: 'rank',
  selected: null,
  detail: null,
  more: {busy: false, error: null},
};
let bridge = null;

const $ = id => document.getElementById(id);

function h(tag, attrs = {}, ...children) {
  const el = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (value === false || value == null) continue;
    if (key === 'class') el.className = value;
    else if (key.startsWith('on')) el.addEventListener(key.slice(2), value);
    else if (key === 'text') el.textContent = value;
    else el.setAttribute(key, value === true ? '' : String(value));
  }
  for (const child of children.flat()) {
    if (child == null || child === false) continue;
    el.append(child instanceof Node ? child : document.createTextNode(String(child)));
  }
  return el;
}

const ICONS = {
  alert: 'M12 3 2 20h20L12 3Zm0 6v5m0 3v.5',
  back: 'M15 5 8 12l7 7',
  link: 'M14 4h6v6m0-6-9 9M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5',
};
function icon(name) {
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('viewBox', '0 0 24 24');
  svg.setAttribute('aria-hidden', 'true');
  svg.setAttribute('class', 'icon');
  const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
  path.setAttribute('d', ICONS[name]);
  svg.append(path);
  return svg;
}

// --- Host context --------------------------------------------------------------------------

function applyHost() {
  const root = document.documentElement;
  for (const [name, value] of Object.entries(state.host.styles?.variables || {})) {
    if (typeof value === 'string' && name.startsWith('--')) root.style.setProperty(name, value);
  }
  const fonts = state.host.styles?.css?.fonts;
  if (typeof fonts === 'string') {
    let tag = $('host-fonts');
    if (!tag) document.head.append(tag = h('style', {id: 'host-fonts'}));
    if (tag.textContent !== fonts) tag.textContent = fonts;
  }
  const colours = palette(state.host);
  root.dataset.theme = colours.theme;
  root.style.colorScheme = colours.theme;
  const set = {
    '--panel-bg': colours.background, '--panel-text': colours.text,
    '--accent-text': colours.accentText, '--accent-ui': colours.accentUi,
    '--heading': colours.heading, '--danger': colours.danger, '--warning': colours.warning,
  };
  for (const [name, value] of Object.entries(set)) root.style.setProperty(name, value);
}

function formatOptions() {
  return {locale: state.host.locale, timeZone: state.host.timeZone};
}

// --- Rendering -----------------------------------------------------------------------------

function renderHeader() {
  if (!state.readAt) {
    $('provenance').textContent = 'Connected · reading through the host';
    $('stale').hidden = true;
    return;
  }
  const p = provenance({server: state.server, readAt: state.readAt, now: now(), ...formatOptions()});
  $('provenance').textContent = p.text;
  $('stale').hidden = !p.stale;
}

function renderStatus() {
  const box = $('status');
  box.replaceChildren();
  box.hidden = state.phase === 'ready';
  if (state.phase === 'connecting') box.append(h('p', {text: 'Connecting to the host…'}));
  if (state.phase === 'waiting') box.append(h('p', {text: 'Waiting for the opportunities result…'}));
  if (state.phase === 'cancelled') {
    box.append(h('p', {text: 'The opportunities call was cancelled before it returned. Ask again in the conversation.'}));
  }
  if (state.phase === 'disconnected') {
    box.append(h('p', {class: 'error'}, icon('alert'), ' This panel could not connect to the host. The answer in the conversation is complete without it.'));
  }
  if (state.phase === 'error') box.append(errorBlock('Opportunities could not be read', state.error));
}

function errorBlock(title, failure) {
  const view = errorView(failure);
  return h('div', {class: 'error-block', role: 'alert'},
    h('p', {class: 'error'}, icon('alert'), ` ${title}: `, h('code', {text: view.code})),
    h('p', {text: view.summary}),
    view.detail ? h('p', {class: 'meta', text: `Engine message: ${view.detail}`}) : null);
}

function workItems(links) {
  if (!links.length) return h('span', {class: 'meta', text: 'None active'});
  return h('ul', {class: 'refs'}, links.map(l => h('li', {}, linkTo(l.reference, l.url, `${l.linkType} · ${l.system} ${l.type}`))));
}

function linkTo(label, url, title) {
  if (!url) return h('span', {title, text: label});
  return h('a', {href: url, title, 'data-link': '', onclick: event => openLink(event, url)}, label, icon('link'));
}

async function openLink(event, url) {
  event.preventDefault();
  const anchor = event.currentTarget;
  const opened = bridge ? await bridge.openLink(url) : false;
  const note = anchor.parentElement.querySelector('.link-note');
  if (opened) note?.remove();
  else if (!note) anchor.after(h('span', {class: 'link-note meta', role: 'status', text: ' The host did not open this link.'}));
}

function renderList() {
  const view = $('list-view');
  view.hidden = state.phase !== 'ready' || state.selected !== null;
  if (state.phase !== 'ready') return;
  const list = state.list;
  const filtered = state.search.trim() !== '' || state.linked !== 'all';
  const rows = sortRows(filterRows(list.rows, {search: state.search, linked: state.linked}), state.sort);

  $('empty').hidden = list.total !== 0;
  $('table-wrap').hidden = list.total === 0;
  $('controls').hidden = list.total === 0;
  $('coverage').textContent = coverage(list, rows.length, filtered);
  $('no-match').hidden = !(filtered && rows.length === 0 && list.rows.length > 0);

  $('rows').replaceChildren(...rows.map(row => h('tr', {'data-row': row.problemId},
    h('td', {class: 'num', text: row.rank}),
    h('th', {scope: 'row'}, h('button', {
      type: 'button', class: 'open', id: `open-${row.problemId}`,
      'aria-label': `${row.title}, rank ${row.rank}. Open detail`,
      onclick: () => select(row.problemId),
    }, row.title), h('span', {class: 'id meta', text: row.problemId})),
    h('td', {class: 'num score', text: formatScore(row.score)}),
    ...COMPONENTS.map(([key]) => h('td', {class: 'num component', text: formatScore(row.components[key])})),
    h('td', {class: 'links'}, workItems(row.links)),
  )));

  const more = $('more');
  more.hidden = !list.hasMore;
  more.disabled = state.more.busy;
  more.textContent = state.more.busy ? 'Loading…' : `Load the next ${list.limit}`;
  $('more-status').replaceChildren();
  if (state.more.error) $('more-status').append(errorBlock('The next page could not be read', state.more.error));
}

function renderDetail() {
  const view = $('detail-view');
  view.hidden = state.selected === null;
  if (state.selected === null) return view.replaceChildren();
  const row = state.list.rows.find(r => r.problemId === state.selected);
  const {problem, evidence: refs} = state.detail;

  const personasPart = problem.status === 'loading' ? h('p', {class: 'meta', text: 'Reading personas…'})
    : problem.status === 'error' ? errorBlock('Personas could not be read', problem.error)
    : problem.personas.length === 0 ? h('p', {class: 'meta', text: 'No personas recorded.'})
    : h('table', {class: 'compact'},
      h('thead', {}, h('tr', {}, h('th', {scope: 'col', text: 'Persona'}), h('th', {scope: 'col', class: 'num', text: 'Confidence'}))),
      h('tbody', {}, problem.personas.map(p => h('tr', {}, h('td', {text: p.name}), h('td', {class: 'num', text: p.confidence})))));

  const evidencePart = refs.status === 'loading' ? h('p', {class: 'meta', text: 'Reading evidence references…'})
    : refs.status === 'error' ? errorBlock('Evidence references could not be read', refs.error)
    : h('div', {},
      h('p', {class: 'meta', text: `${refs.items.length} of ${refs.total} references. References only; evidence text is not shown in this panel.`}),
      refs.items.length === 0 ? null : h('ul', {class: 'evidence'}, refs.items.map(e => h('li', {},
        h('p', {}, linkTo(e.reference, e.url, `Open ${e.reference} in ${e.source}`)),
        h('p', {class: 'meta', text: `${e.type} · ${e.source} · ${e.occurred}`}),
        e.measurement ? h('p', {class: 'measure', text: e.measurement}) : null))));

  view.replaceChildren(
    h('button', {type: 'button', class: 'back', id: 'back', onclick: back}, icon('back'), ' All opportunities'),
    h('h2', {id: 'detail-title', tabindex: '-1', text: row.title}),
    h('p', {class: 'meta', text: [row.problemId, `rank ${row.rank}`,
      problem.status === 'ready' && problem.lineage ? `lineage ${problem.lineage}` : null].filter(Boolean).join(' · ')}),
    h('h3', {text: 'Score'}),
    h('dl', {class: 'scores'},
      h('div', {}, h('dt', {text: 'Composite'}), h('dd', {text: formatScore(row.score)})),
      COMPONENTS.map(([key, label]) => h('div', {}, h('dt', {text: label}), h('dd', {text: formatScore(row.components[key])}))),
      h('div', {}, h('dt', {text: 'Strategic weight'}), h('dd', {text: formatScore(row.strategicWeight)})),
      h('div', {}, h('dt', {text: 'Weight config'}), h('dd', {text: row.weightVersion ?? '—'}))),
    h('h3', {text: 'Active work items'}), workItems(row.links),
    h('h3', {text: 'Personas'}), personasPart,
    h('h3', {text: 'Evidence'}), evidencePart,
  );
}

function render() {
  // Re-rendering replaces elements; keep keyboard focus on the element with the same id.
  const focused = document.activeElement?.id;
  applyHost();
  renderHeader();
  renderStatus();
  renderList();
  renderDetail();
  $('panel').setAttribute('aria-busy', String(state.phase === 'connecting' || state.phase === 'waiting'));
  if (focused && document.activeElement?.id !== focused) $(focused)?.focus();
}

// --- Actions -------------------------------------------------------------------------------

function receiveList(result) {
  state.readAt = now();
  state.server = result.server || state.server;
  if (!result.ok) {
    state.phase = 'error';
    state.error = result;
    return render();
  }
  try {
    state.list = mergePage(null, result.data);
    state.phase = 'ready';
    state.error = null;
  } catch (error) {
    state.phase = 'error';
    state.error = {code: 'MALFORMED_RESULT', message: error.message};
  }
  state.selected = null;
  render();
}

async function loadMore() {
  if (!bridge || !state.list?.hasMore || state.more.busy) return;
  state.more = {busy: true, error: null};
  render();
  const result = await bridge.listOpportunities({offset: state.list.nextOffset, limit: state.list.limit});
  state.more = {busy: false, error: null};
  if (!result.ok) state.more.error = result;
  else {
    try {
      const before = state.list.rows.length;
      state.list = mergePage(state.list, result.data);
      state.readAt = now();
      render();
      // Focus the first new row wherever the current sort put it; if a filter hides it, More.
      const firstNew = state.list.rows[before];
      return ((firstNew && $(`open-${firstNew.problemId}`)) || $('more')).focus();
    } catch (error) {
      state.more.error = {code: 'MALFORMED_RESULT', message: error.message};
    }
  }
  render();
}

async function select(problemId) {
  state.selected = problemId;
  state.detail = {problem: {status: 'loading'}, evidence: {status: 'loading'}};
  render();
  $('detail-title').focus();
  if (!bridge) {
    const failure = {code: 'HOST_ERROR', message: 'The panel is not connected to the host.'};
    state.detail = {problem: {status: 'error', error: failure}, evidence: {status: 'error', error: failure}};
    return render();
  }
  const [problem, refs] = await Promise.all([bridge.getProblem(problemId), bridge.listEvidence(problemId)]);
  if (state.selected !== problemId) return; // the PM moved on while the reads were in flight
  state.detail = {problem: readProblem(problem), evidence: readEvidence(refs)};
  render();
}

function readProblem(result) {
  if (!result.ok) return {status: 'error', error: result};
  try {
    validateProblem(result.data);
    return {status: 'ready', personas: personas(result.data), lineage: result.data.lineage_ref || null};
  } catch (error) {
    return {status: 'error', error: {code: 'MALFORMED_RESULT', message: error.message}};
  }
}

function readEvidence(result) {
  if (!result.ok) return {status: 'error', error: result};
  try {
    validateEvidence(result.data);
    return {status: 'ready', items: evidence(result.data, formatOptions()), total: result.data.total};
  } catch (error) {
    return {status: 'error', error: {code: 'MALFORMED_RESULT', message: error.message}};
  }
}

function back() {
  const id = state.selected;
  state.selected = null;
  state.detail = null;
  render();
  document.getElementById(`open-${id}`)?.focus();
}

// --- Start ---------------------------------------------------------------------------------

function buildControls() {
  const options = (select, pairs, current) => select.replaceChildren(
    ...pairs.map(([value, label]) => h('option', {value, selected: value === current}, label)));
  options($('linked'), LINK_FILTERS, state.linked);
  options($('sort'), SORTS, state.sort);
  $('search').addEventListener('input', e => { state.search = e.target.value; render(); });
  $('linked').addEventListener('change', e => { state.linked = e.target.value; render(); });
  $('sort').addEventListener('change', e => { state.sort = e.target.value; render(); });
  $('controls').addEventListener('submit', e => e.preventDefault());
  $('more').addEventListener('click', loadMore);
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && state.selected !== null) back(); });
  $('version').textContent = `Opportunities panel ${VERSION}`;
}

async function start() {
  buildControls();
  render();
  try {
    bridge = await connectBridge({
      onToolInput: () => { if (state.phase === 'connecting') state.phase = 'waiting'; render(); },
      onToolResult: receiveList,
      onToolCancelled: () => { state.phase = 'cancelled'; render(); },
      onHostContext: update => { state.host = mergeHostContext(state.host, update); render(); },
    }, {version: VERSION});
    state.host = mergeHostContext(bridge.hostContext(), state.host);
    if (state.phase === 'connecting') state.phase = 'waiting';
  } catch {
    state.phase = 'disconnected';
  }
  render();
  setInterval(renderHeader, 60_000);
}

start();
