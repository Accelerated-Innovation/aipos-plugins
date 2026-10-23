// Pure shaping for the opportunities panel: tool data in, rows, filters, labels and colours out.
// No SDK, no DOM, no I/O, so it runs under `node --test` and can be shared with viewers/ later.
// It receives normalized tool data (bridge.mjs strips the MCP envelope) and never sees a token.

export const COMPONENTS = Object.freeze([
  ['evidence_strength', 'Evidence'],
  ['revenue_impact', 'Revenue'],
  ['persona_breadth', 'Personas'],
  ['recency', 'Recency'],
  ['validation_signal', 'Validation'],
]);
export const SORTS = Object.freeze([
  ['rank', 'Engine rank'],
  ['score', 'Composite score'],
  ['title', 'Title'],
  ...COMPONENTS,
]);
export const LINK_FILTERS = Object.freeze([
  ['all', 'All'],
  ['linked', 'With active work items'],
  ['unlinked', 'Without active work items'],
]);
export const STALE_AFTER_MS = 24 * 60 * 60 * 1000;

const fail = message => { throw new Error(message); };
const isObject = v => v !== null && typeof v === 'object' && !Array.isArray(v);
const isCount = v => Number.isInteger(v) && v >= 0;

// --- Tool data -----------------------------------------------------------------------------

export function validatePage(page) {
  if (!isObject(page) || !Array.isArray(page.items)) fail('The opportunities result has no items list.');
  if (![page.total, page.offset, page.limit].every(isCount)) fail('The opportunities result has no paging fields.');
  for (const item of page.items) {
    if (!isObject(item) || typeof item.problem_id !== 'string' || typeof item.title !== 'string'
      || !Number.isFinite(item.composite_score) || !isObject(item.components) || !Array.isArray(item.links)) {
      fail('An opportunity in the result is missing required fields.');
    }
  }
  return page;
}

export function validateProblem(problem) {
  if (!isObject(problem) || typeof problem.problem_id !== 'string' || !Array.isArray(problem.personas)
    || !Array.isArray(problem.evidence_references)) fail('The problem result is missing required fields.');
  return problem;
}

export function validateEvidence(evidence) {
  if (!isObject(evidence) || !Array.isArray(evidence.items) || !isCount(evidence.total)) {
    fail('The evidence result is missing required fields.');
  }
  return evidence;
}

// One page of `list_opportunities` as display rows. Rank is the engine's order, counted from the
// page's offset, so a second page continues the numbering instead of restarting it.
export function toRows(page) {
  validatePage(page);
  return page.items.map((item, i) => ({
    problemId: item.problem_id,
    title: item.title,
    rank: page.offset + i + 1,
    score: item.composite_score,
    components: Object.fromEntries(COMPONENTS.map(([key]) => [key, item.components[key] ?? null])),
    strategicWeight: item.strategic_weight ?? null,
    weightVersion: item.weight_config_version ?? null,
    links: item.links.filter(l => l?.status === 'active').map(l => ({
      reference: l.external_reference || `${l.target_system}:${l.external_record_id}`,
      system: l.target_system,
      type: l.target_type,
      linkType: l.link_type,
      url: safeLink(l.record_url),
    })),
  }));
}

// The rows the panel holds, plus where the next page starts. A page that does not continue the
// held rows (a host replayed an old call, or the list was re-run) replaces them.
export function mergePage(list, page) {
  const rows = toRows(page);
  const continues = list && page.offset === list.nextOffset;
  const held = continues ? list.rows : [];
  const seen = new Set(held.map(r => r.problemId));
  const merged = [...held, ...rows.filter(r => !seen.has(r.problemId))];
  const nextOffset = page.offset + page.items.length;
  return {
    rows: merged,
    firstOffset: continues ? list.firstOffset : page.offset,
    nextOffset,
    limit: page.limit,
    total: page.total,
    hasMore: page.items.length > 0 && nextOffset < page.total,
  };
}

export function filterRows(rows, {search = '', linked = 'all'} = {}) {
  const needle = search.trim().toLowerCase();
  return rows.filter(r =>
    (!needle || r.title.toLowerCase().includes(needle) || r.problemId.toLowerCase().includes(needle))
    && (linked === 'all' || (linked === 'linked') === (r.links.length > 0)));
}

export function sortRows(rows, key = 'rank') {
  const value = r => key === 'rank' ? r.rank : key === 'score' ? r.score : key === 'title' ? r.title
    : r.components[key];
  const ascending = key === 'rank' || key === 'title';
  return [...rows].sort((a, b) => {
    const x = value(a), y = value(b);
    if (x === y || (x == null && y == null)) return a.rank - b.rank;
    if (x == null) return 1;
    if (y == null) return -1;
    const order = typeof x === 'string' ? x.localeCompare(y) : x - y;
    return (ascending ? order : -order) || a.rank - b.rank;
  });
}

// What the PM is looking at, against what the engine holds. Filters run over held rows only, so
// say so whenever more exist than are held.
export function coverage(list, shown, filtered) {
  if (!list) return '';
  const held = list.rows.length, total = list.total;
  const noun = n => n === 1 ? 'opportunity' : 'opportunities';
  if (total === 0) return 'No opportunities.';
  if (held === total && list.firstOffset === 0) {
    return filtered ? `Showing ${shown} of ${total} ${noun(total)}.` : `${total} ${noun(total)}.`;
  }
  return filtered
    ? `Showing ${shown} of ${held} loaded, ${total} ${noun(total)} in total. Filters cover only the loaded rows.`
    : `${held} loaded of ${total} ${noun(total)}.`;
}

// --- Problem detail ------------------------------------------------------------------------

export function personas(problem) {
  validateProblem(problem);
  return [...problem.personas]
    .sort((a, b) => (b.confidence ?? 0) - (a.confidence ?? 0) || a.name.localeCompare(b.name))
    .map(p => ({name: p.name, confidence: Number.isFinite(p.confidence) ? `${Math.round(p.confidence * 100)}%` : '—'}));
}

const titleCase = s => String(s || '').replace(/_/g, ' ').replace(/^./, c => c.toUpperCase());

// Evidence as provenance references only: source, record link, date, and a study measurement when
// the engine supplies one. There is no text to show, and the panel never asks for any.
export function evidence(result, format = {}) {
  validateEvidence(result);
  return result.items.map(e => ({
    reference: e.provenance_reference,
    source: e.source_system,
    type: titleCase(e.source_type),
    occurred: e.occurred_at ? formatTime(e.occurred_at, {...format, dateOnly: true}) : 'Date not recorded',
    url: safeLink(e.record_url),
    measurement: e.measurement ? formatMeasurement(e.measurement) : null,
  }));
}

export function formatMeasurement(m) {
  const value = m.unit === 'currency' ? `${m.value} ${m.currency || ''}`.trim()
    : m.unit === 'percent' ? `${m.value}%` : `${m.value} ${m.unit}`;
  const sample = Number.isInteger(m.n) ? `n=${m.n}` : 'n not recorded';
  return `${titleCase(m.metric)}: ${value} (${sample}, ${titleCase(m.method).toLowerCase()})`;
}

export function formatScore(n) {
  return Number.isFinite(n) ? n.toFixed(2) : '—';
}

// Only absolute http(s) links leave the panel, and only through the host's ui/open-link.
export function safeLink(url) {
  if (typeof url !== 'string') return null;
  try {
    const parsed = new URL(url);
    return parsed.protocol === 'https:' || parsed.protocol === 'http:' ? parsed.href : null;
  } catch {
    return null;
  }
}

// --- Provenance ----------------------------------------------------------------------------

export function formatTime(iso, {locale, timeZone, dateOnly = false} = {}) {
  const when = new Date(iso);
  if (Number.isNaN(when.getTime())) return 'unknown time';
  const options = dateOnly ? {dateStyle: 'medium'}
    : {year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', timeZoneName: 'short'};
  try {
    return new Intl.DateTimeFormat(locale || undefined, {...options, timeZone: timeZone || undefined}).format(when);
  } catch {
    return new Intl.DateTimeFormat('en-GB', {...options, timeZone: 'UTC'}).format(when);
  }
}

export function isStale(readAt, now) {
  return Date.parse(now) - Date.parse(readAt) > STALE_AFTER_MS;
}

// panel-contract.md: source mode, server, read time and coverage on every view. The panel reads
// live through the host, so the mode is always `connected`; the read time is when this panel
// received the result, which is all a panel can know.
export function provenance({server, readAt, now, locale, timeZone}) {
  return {
    text: `Connected · ${server || 'MCP server'} · read ${formatTime(readAt, {locale, timeZone})}`,
    stale: isStale(readAt, now),
  };
}

const ERRORS = {
  INSUFFICIENT_SCOPE: 'Your engine token does not carry the pm role, which reading opportunities needs.',
  INVALID_TOKEN: 'The engine did not accept the token. Reconnect the engine with a valid token.',
  PROBLEM_NOT_FOUND: 'The engine does not hold this problem. The list may be out of date.',
  VALIDATION_ERROR: 'The engine refused the request as invalid.',
  HOST_ERROR: 'The host could not complete the call.',
  MALFORMED_RESULT: 'The result did not have the expected shape.',
  CANCELLED: 'The call was cancelled before it returned.',
};

export function errorView({code, message}) {
  return {code: code || 'TOOL_ERROR', summary: ERRORS[code] || 'The call failed.', detail: message || ''};
}

// --- Host context and colour ---------------------------------------------------------------

// host-context-changed carries a partial context. Merge it into what the panel holds, one level
// deeper than the SDK does, so a styles update with some variables keeps the rest (BRAND.md).
export function mergeHostContext(current = {}, update = {}) {
  const merged = {...current, ...update};
  if (isObject(current.styles) || isObject(update.styles)) {
    const a = current.styles || {}, b = update.styles || {};
    merged.styles = {
      ...a,
      ...b,
      variables: {...(a.variables || {}), ...(b.variables || {})},
      css: {...(a.css || {}), ...(b.css || {})},
    };
  }
  return merged;
}

export const BRAND = Object.freeze({
  darkPurple: '#19004f', purple: '#5865e7', lightBlue: '#0abeef',
  red: '#af1e44', blue: '#1a4b84', green: '#6fa113', yellow: '#d1b70d',
  white: '#ffffff', aiWhite: '#f2f2f2', black90: '#1a1a1a',
});

// Parses the colour forms hosts send: #rgb, #rrggbb, #rrggbbaa, rgb()/rgba(). Anything else
// (a var(), oklch(), a keyword) is unknown, and the caller falls back to the host's own colours.
export function parseColor(value) {
  if (typeof value !== 'string') return null;
  const v = value.trim().toLowerCase();
  let m = v.match(/^#([0-9a-f]{3,4}|[0-9a-f]{6}|[0-9a-f]{8})$/);
  if (m) {
    let h = m[1];
    if (h.length <= 4) h = [...h].map(c => c + c).join('');
    const [r, g, b, a = 255] = h.match(/../g).map(x => parseInt(x, 16));
    return a === 255 ? [r, g, b] : null;
  }
  m = v.match(/^rgba?\(\s*(\d+(?:\.\d+)?)[\s,]+(\d+(?:\.\d+)?)[\s,]+(\d+(?:\.\d+)?)(?:\s*[,/]\s*([\d.]+%?))?\s*\)$/);
  if (m) {
    const alpha = m[4] === undefined ? 1 : m[4].endsWith('%') ? parseFloat(m[4]) / 100 : parseFloat(m[4]);
    if (alpha < 1) return null;
    return [m[1], m[2], m[3]].map(Number).map(n => Math.min(255, Math.round(n)));
  }
  return null;
}

export function luminance(rgb) {
  const [r, g, b] = rgb.map(c => {
    const s = c / 255;
    return s <= 0.04045 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4;
  });
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

export function contrast(a, b) {
  const x = typeof a === 'string' ? parseColor(a) : a, y = typeof b === 'string' ? parseColor(b) : b;
  if (!x || !y) return null;
  const [hi, lo] = [luminance(x), luminance(y)].sort((p, q) => q - p);
  return (hi + 0.05) / (lo + 0.05);
}

export const TEXT_MIN = 4.5;
export const UI_MIN = 3;

// The panel's colours for the resolved host surface (BRAND.md "Accents change with the theme").
// Each brand use is checked against the actual background and falls back to the host's own
// colour when it fails, so a host shade the guide did not anticipate never yields unreadable text.
export function palette(context = {}) {
  const vars = context.styles?.variables || {};
  const declared = vars['--color-background-primary'];
  const bgRgb = parseColor(declared);
  const theme = context.theme === 'dark' || context.theme === 'light' ? context.theme
    : bgRgb ? (luminance(bgRgb) < 0.2 ? 'dark' : 'light') : 'light';
  const dark = theme === 'dark';
  const background = declared || (dark ? BRAND.black90 : BRAND.white);
  const text = vars['--color-text-primary'] || (dark ? BRAND.aiWhite : BRAND.black90);
  const ring = vars['--color-ring-primary'] || text;
  const passes = (colour, min) => (contrast(colour, background) ?? 0) >= min;
  const accent = dark ? BRAND.lightBlue : BRAND.purple;
  const status = (hostVar, brandColour) => vars[hostVar]
    || (brandColour && passes(brandColour, TEXT_MIN) ? brandColour : text);
  return {
    theme,
    background,
    text,
    accentText: passes(accent, TEXT_MIN) ? accent : text,
    accentUi: passes(accent, UI_MIN) ? accent : ring,
    heading: !dark && passes(BRAND.darkPurple, TEXT_MIN) ? BRAND.darkPurple : text,
    danger: status('--color-text-danger', BRAND.red),
    warning: status('--color-text-warning', dark ? BRAND.yellow : null),
  };
}
