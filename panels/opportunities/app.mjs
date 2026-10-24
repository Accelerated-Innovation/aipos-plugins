// The opportunities panel: state, rendering and interaction. Vanilla DOM, built with textContent
// only, so nothing the engine returns is ever parsed as markup. All host traffic goes through
// bridge.mjs; all shaping through model.mjs.
import {connectBridge} from './bridge.mjs';
import {
  COMPONENTS, LINK_FILTERS, SORTS, barWidth, componentScales, coverage, errorView, evidence,
  evidenceBySource, filterRows, formatScore, mergeHostContext, mergePage, palette, personas,
  provenance, similarMatches, sortRows, trackerMessage, validateEvidence, validateProblem,
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
  tracker: {busy: false, note: null}, // the Add Opportunity hand-off to the conversation
  similar: null, // {query, busy, error, matches} for the semantic search
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
  close: 'M6 6l12 12M18 6 6 18',
  link: 'M14 4h6v6m0-6-9 9M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5',
  plus: 'M12 5v14M5 12h14',
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
  view.hidden = state.phase !== 'ready';
  if (state.phase !== 'ready') return;
  const list = state.list;
  const filtered = state.search.trim() !== '' || state.linked !== 'all';
  const rows = sortRows(filterRows(list.rows, {search: state.search, linked: state.linked}), state.sort);

  $('empty').hidden = list.total !== 0;
  $('table-wrap').hidden = list.total === 0;
  $('controls').hidden = list.total === 0;
  $('coverage').textContent = coverage(list, rows.length, filtered);
  $('no-match').hidden = !(filtered && rows.length === 0 && list.rows.length > 0);

  $('rows').replaceChildren(...rows.map(row => h('tr', {'data-row': row.problemId, class: state.selected === row.problemId ? 'view' : null},
    h('td', {class: 'num rank', text: row.rank}),
    h('th', {scope: 'row'}, h('button', {
      type: 'button', class: 'open', id: `open-${row.problemId}`,
      'aria-label': `${row.title}, rank ${row.rank}. Open detail`,
      onclick: () => select(row.problemId),
    }, row.title), h('span', {class: 'id meta', text: row.problemId})),
    h('td', {class: 'links'}, workItems(row.links)),
    h('td', {class: 'num score', text: formatScore(row.score)}),
  )));

  const more = $('more');
  more.hidden = !list.hasMore;
  more.disabled = state.more.busy;
  more.textContent = state.more.busy ? 'Loading…' : `Load the next ${list.limit}`;
  $('more-status').replaceChildren();
  if (state.more.error) $('more-status').append(errorBlock('The next page could not be read', state.more.error));
}

function renderSimilar() {
  const box = $('similar');
  const sim = state.similar;
  box.hidden = !sim;
  box.replaceChildren();
  if (!sim) return;
  const head = h('div', {class: 'similar-h'},
    h('span', {class: 'meta', text: sim.busy ? `Finding opportunities similar to "${sim.query}"…`
      : sim.error ? `Similar to "${sim.query}"`
      : sim.matches.length ? `${sim.matches.length} similar to "${sim.query}" · strongest first, no scores`
      : `Nothing similar to "${sim.query}". The engine holds no near-duplicate; ask in the conversation to propose it.`}),
    h('button', {type: 'button', class: 'clear', id: 'ask-clear', onclick: clearSimilar, text: 'Clear'}));
  box.append(head);
  if (sim.error) {
    const code = sim.error.code;
    const note = code === 'TOOL_ERROR' && /unknown tool|not found|not allowed/i.test(sim.error.message || '')
      ? h('p', {class: 'meta', text: 'Semantic search is not enabled on this engine. Use the title search above.'})
      : errorBlock('Similar opportunities could not be read', sim.error);
    return box.append(note);
  }
  if (sim.busy || !sim.matches.length) return;
  box.append(h('ol', {}, sim.matches.map(m => h('li', {},
    m.row ? h('button', {type: 'button', class: 'open', id: `similar-${m.problemId}`, onclick: () => select(m.problemId)}, m.title)
      : h('span', {}, h('span', {text: m.title}), h('span', {class: 'meta', text: ` · ${m.problemId} (not in the loaded list)`})),
    h('span', {class: 'band', text: m.band})))));
}

function renderDetail() {
  const view = $('detail-view');
  const open = state.selected !== null;
  view.hidden = !open;
  $('scrim').hidden = !open;
  if (!open) return view.replaceChildren();
  const row = state.list.rows.find(r => r.problemId === state.selected);
  const {problem, evidence: refs} = state.detail;
  const scales = componentScales(state.list.rows);

  const personasPart = problem.status === 'loading' ? h('p', {class: 'meta', text: 'Reading personas…'})
    : problem.status === 'error' ? errorBlock('Personas could not be read', problem.error)
    : problem.personas.length === 0 ? h('p', {class: 'meta', text: 'No personas recorded.'})
    : h('div', {class: 'opd-chips'}, problem.personas.map(p => h('span', {}, p.name, ' ', h('b', {text: p.confidence}))));

  const evidenceHead = refs.status === 'ready'
    ? `Evidence · ${refs.total} reference${refs.total === 1 ? '' : 's'} from ${evidenceBySource(refs.items).length} source type${evidenceBySource(refs.items).length === 1 ? '' : 's'}`
    : 'Evidence';
  const evidencePart = refs.status === 'loading' ? h('p', {class: 'meta', text: 'Reading evidence references…'})
    : refs.status === 'error' ? errorBlock('Evidence references could not be read', refs.error)
    : refs.items.length === 0 ? h('p', {class: 'meta', text: 'No evidence references recorded.'})
    : evidenceBySource(refs.items).map(group => h('div', {class: 'ev-group'},
      h('div', {class: 'ev-group-h'}, h('span', {text: group.type}), h('b', {text: group.items.length})),
      h('ul', {class: 'evidence'}, group.items.map(e => h('li', {},
        h('p', {}, linkTo(e.reference, e.url, e.url ? `Open ${e.reference} in ${e.source}` : `${e.reference} has no record link`)),
        h('p', {class: 'meta', text: `${e.source} · ${e.occurred}`}),
        e.measurement ? h('p', {class: 'measure', text: e.measurement}) : null)))));

  const footer = h('div', {class: 'opd-ft'},
    h('button', {type: 'button', class: 'primary', id: 'add', disabled: state.tracker.busy || !bridge, onclick: addToTracker},
      icon('plus'), state.tracker.busy ? ' Handing to the conversation…' : ' Add Opportunity to a tracker'),
    h('p', {class: 'meta note', role: 'status', text: state.tracker.note
      || 'Sends a request to the conversation. Claude uses the tracker you have connected (Aha!, Jira, …).'}));

  view.replaceChildren(
    h('button', {type: 'button', class: 'opd-close', id: 'back', 'aria-label': 'Close details', onclick: back}, icon('close')),
    h('div', {class: 'opd-body'},
      h('div', {class: 'opd-hd'},
        h('span', {class: 'opd-id', text: [row.problemId, `rank ${row.rank}`,
          problem.status === 'ready' && problem.lineage ? `lineage ${problem.lineage}` : null].filter(Boolean).join(' · ')}),
        h('h2', {id: 'detail-title', tabindex: '-1', text: row.title})),
      h('div', {class: 'opd-sec opd-score'},
        h('div', {}, h('h3', {text: 'Score'}), h('div', {class: 'opd-big', text: formatScore(row.score)})),
        h('span', {class: 'opd-meta', text: [row.weightVersion ? `weights ${row.weightVersion}` : null,
          row.strategicWeight != null ? `strategic weight ${formatScore(row.strategicWeight)}` : null].filter(Boolean).join(' · ') || 'Weight config not recorded'})),
      h('div', {class: 'opd-sec'},
        h('h3', {text: 'Score components'}),
        h('ul', {class: 'opd-bars'}, COMPONENTS.map(([key, label]) => h('li', {},
          h('span', {text: label}),
          h('span', {class: 'track', 'aria-hidden': 'true'}, h('span', {class: 'fill', style: `width:${barWidth(row.components[key], scales[key])}%`})),
          h('span', {class: 'val', text: formatScore(row.components[key])})))),
        h('p', {class: 'meta', text: 'Bars are relative to the highest value among the loaded opportunities.'})),
      h('div', {class: 'opd-sec'}, h('h3', {text: 'Personas it serves'}), personasPart),
      h('div', {class: 'opd-sec'}, h('h3', {text: 'Active work items'}), workItems(row.links)),
      h('div', {class: 'opd-sec'},
        h('div', {class: 'opd-evh'}, h('h3', {text: evidenceHead})),
        h('p', {class: 'meta', text: 'References only; each opens in its source system. Evidence text is not shown in this panel.'}),
        evidencePart)),
    footer,
  );
}

function render() {
  // Re-rendering replaces elements; keep keyboard focus on the element with the same id.
  const focused = document.activeElement?.id;
  applyHost();
  renderHeader();
  renderStatus();
  renderList();
  renderSimilar();
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
  state.tracker = {busy: false, note: null};
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

async function findSimilar() {
  const query = $('ask-text').value.trim();
  if (!query || !bridge || state.similar?.busy) return;
  state.similar = {query, busy: true, error: null, matches: []};
  render();
  const result = await bridge.findSimilar(query);
  if (state.similar?.query !== query) return;
  if (!result.ok) state.similar = {query, busy: false, error: result, matches: []};
  else {
    try {
      state.similar = {query, busy: false, error: null, matches: similarMatches(result.data, state.list?.rows || [])};
    } catch (error) {
      state.similar = {query, busy: false, error: {code: 'MALFORMED_RESULT', message: error.message}, matches: []};
    }
  }
  render();
}

function clearSimilar() {
  state.similar = null;
  render();
  $('ask-text').focus();
}

async function addToTracker() {
  const row = state.list?.rows.find(r => r.problemId === state.selected);
  if (!row || !bridge || state.tracker.busy) return;
  state.tracker = {busy: true, note: null};
  render();
  const sent = await bridge.sendMessage(trackerMessage(row));
  if (state.selected !== row.problemId) return;
  state.tracker = {busy: false, note: sent
    ? 'Handed to the conversation. Continue there to choose the tracker and confirm.'
    : 'The host did not accept the message. Ask in the conversation instead.'};
  render();
  $('add')?.focus();
}

// The side panel is modal: Tab cycles inside it, and the scrim or Escape closes it.
function trapFocus(event) {
  if (event.key !== 'Tab' || state.selected === null) return;
  const view = $('detail-view');
  const focusable = [...view.querySelectorAll('button:not(:disabled), a[href], [tabindex="-1"]')];
  if (!focusable.length) return;
  const first = focusable[0], last = focusable[focusable.length - 1];
  if (event.shiftKey && (document.activeElement === first || !view.contains(document.activeElement))) {
    event.preventDefault(); last.focus();
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault(); first.focus();
  }
}

function back() {
  const id = state.selected;
  state.selected = null;
  state.detail = null;
  state.tracker = {busy: false, note: null};
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
  $('ask-go').addEventListener('click', findSimilar);
  $('ask-text').addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); findSimilar(); } });
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && state.selected !== null) back(); });
  document.addEventListener('keydown', trapFocus);
  $('scrim').addEventListener('click', () => { if (state.selected !== null) back(); });
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
