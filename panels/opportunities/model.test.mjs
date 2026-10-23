import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {
  BRAND, contrast, coverage, errorView, evidence, filterRows, formatMeasurement, formatScore,
  isStale, mergeHostContext, mergePage, palette, parseColor, personas, provenance, safeLink,
  sortRows, toRows, validatePage,
} from './model.mjs';

const read = path => JSON.parse(readFileSync(new URL(path, import.meta.url), 'utf8'));
// The model receives normalized data: an MCP result's structuredContent.
const mcp = stem => read(`./fixtures/mcp/${stem}.json`).result.structuredContent;
const sample = name => read(`./fixtures/engine-samples/${name}.json`).data;
const UTC = {locale: 'en-GB', timeZone: 'UTC'};

test('rows keep engine order, score components and only active work-item links', () => {
  const rows = toRows(mcp('list-opportunities'));
  assert.deepEqual(rows.map(r => [r.rank, r.problemId, r.score]), [[1, 'p-1', 4.5], [2, 'p-2', 3.25]]);
  assert.deepEqual(rows[0].components, {evidence_strength: 1, revenue_impact: 2, persona_breadth: 3, recency: 4, validation_signal: 5});
  // The fixture also holds a severed link (OPP-99); only the active one is shown.
  assert.deepEqual(rows[0].links.map(l => l.reference), ['aha:OPP-12']);
  assert.equal(rows[0].links[0].url, 'https://aha.test/OPP-12');
  assert.deepEqual(rows[1].links, []);
});

test('the published REST sample shapes into the same rows as its MCP data', () => {
  const rows = toRows(sample('opportunities'));
  assert.deepEqual(rows.map(r => r.problemId), ['prob-1a2b3c', 'prob-4d5e6f']);
  assert.equal(formatScore(rows[0].score), '0.78');
});

test('a page that is not a list_opportunities result is refused, not rendered', () => {
  assert.throws(() => validatePage({items: [], total: 0}), /paging/);
  assert.throws(() => toRows({...mcp('list-opportunities'), items: [{title: 'x'}]}), /missing required/);
  assert.throws(() => toRows(mcp('get-problem')), /no items/);
});

test('paging continues numbering, appends the next page and stops at the total', () => {
  let list = mergePage(null, mcp('list-opportunities-first-of-two'));
  assert.deepEqual([list.rows.length, list.total, list.nextOffset, list.hasMore], [1, 2, 1, true]);
  list = mergePage(list, mcp('list-opportunities-second-of-two'));
  assert.deepEqual(list.rows.map(r => [r.rank, r.problemId]), [[1, 'p-1'], [2, 'p-2']]);
  assert.deepEqual([list.nextOffset, list.hasMore, list.firstOffset], [2, false, 0]);
});

test('a page that does not continue the held rows replaces them', () => {
  const list = mergePage(null, mcp('list-opportunities'));
  const replaced = mergePage(list, mcp('list-opportunities-second-of-two'));
  assert.deepEqual(replaced.rows.map(r => r.problemId), ['p-2']);
  assert.equal(replaced.firstOffset, 1);
});

test('an empty list is a valid result with nothing more to load', () => {
  const list = mergePage(null, mcp('list-opportunities-empty'));
  assert.deepEqual([list.rows.length, list.total, list.hasMore], [0, 0, false]);
  assert.equal(coverage(list, 0, false), 'No opportunities.');
});

test('filters search title and ID and split by active work items', () => {
  const rows = toRows(mcp('list-opportunities'));
  assert.deepEqual(filterRows(rows, {search: 'BULK'}).map(r => r.problemId), ['p-2']);
  assert.deepEqual(filterRows(rows, {search: ' p-1 '}).map(r => r.problemId), ['p-1']);
  assert.deepEqual(filterRows(rows, {linked: 'linked'}).map(r => r.problemId), ['p-1']);
  assert.deepEqual(filterRows(rows, {linked: 'unlinked'}).map(r => r.problemId), ['p-2']);
  assert.equal(filterRows(rows, {search: 'nothing'}).length, 0);
});

test('sorts: rank and title ascend, scores descend, ties fall back to rank', () => {
  const rows = toRows(mcp('list-opportunities'));
  assert.deepEqual(sortRows(rows, 'title').map(r => r.problemId), ['p-2', 'p-1']);
  assert.deepEqual(sortRows(rows, 'score').map(r => r.problemId), ['p-1', 'p-2']);
  assert.deepEqual(sortRows([...rows].reverse(), 'rank').map(r => r.problemId), ['p-1', 'p-2']);
  assert.deepEqual(sortRows(rows, 'recency').map(r => r.problemId), ['p-1', 'p-2']); // equal: rank order
  const withMissing = rows.map((r, i) => ({...r, components: {...r.components, recency: i ? 9 : null}}));
  assert.deepEqual(sortRows(withMissing, 'recency').map(r => r.problemId), ['p-2', 'p-1']);
});

test('coverage says when filters cover only the loaded page', () => {
  const all = mergePage(null, mcp('list-opportunities'));
  assert.equal(coverage(all, 2, false), '2 opportunities.');
  assert.equal(coverage(all, 1, true), 'Showing 1 of 2 opportunities.');
  const part = mergePage(null, mcp('list-opportunities-first-of-two'));
  assert.equal(coverage(part, 1, false), '1 loaded of 2 opportunities.');
  assert.equal(coverage(part, 0, true), 'Showing 0 of 1 loaded, 2 opportunities in total. Filters cover only the loaded rows.');
});

test('personas sort by confidence and show it as a percentage', () => {
  assert.deepEqual(personas(sample('problem-detail')), [
    {name: 'Operations Analyst', confidence: '95%'}, {name: 'Administrator', confidence: '90%'}]);
  assert.deepEqual(personas(mcp('get-problem')), [{name: 'Ops lead', confidence: '80%'}]);
});

test('evidence is references only: source, type, date, link and measurement', () => {
  const items = evidence(mcp('list-evidence'), UTC);
  assert.equal(items.length, 3);
  assert.deepEqual(items[0], {reference: 'gong:c-1', source: 'gong', type: 'Call transcript',
    occurred: '1 Jun 2026', url: 'https://app.gong.io/call?id=c-1', measurement: null});
  assert.equal(items[2].measurement, 'Export completion time: 42.5 minutes (n=12, time study)');
  for (const item of items) assert.deepEqual(Object.keys(item).sort(), ['measurement', 'occurred', 'reference', 'source', 'type', 'url']);
});

test('measurements keep units, currency and a missing sample size explicit', () => {
  const m = {metric: 'cost_per_case', value: 12, unit: 'currency', currency: 'USD', n: null, method: 'log_analysis'};
  assert.equal(formatMeasurement(m), 'Cost per case: 12 USD (n not recorded, log analysis)');
  assert.equal(formatMeasurement({...m, unit: 'percent', value: 30, n: 40}), 'Cost per case: 30% (n=40, log analysis)');
});

test('only absolute http(s) links are kept', () => {
  assert.equal(safeLink('https://aha.test/OPP-12'), 'https://aha.test/OPP-12');
  for (const bad of ['javascript:alert(1)', 'data:text/html,x', '/relative', '', null, 7]) assert.equal(safeLink(bad), null);
  const row = toRows({...mcp('list-opportunities'), items: [{...mcp('list-opportunities').items[0],
    links: [{...mcp('list-opportunities').items[0].links[0], record_url: 'javascript:alert(1)'}]}]})[0];
  assert.equal(row.links[0].url, null);
});

test('provenance names the server and read time; stale only past 24 hours', () => {
  const readAt = '2026-10-23T16:00:00Z';
  const p = provenance({server: 'opportunity-engine', readAt, now: '2026-10-24T16:00:00Z', ...UTC});
  assert.equal(p.text, 'Connected · opportunity-engine · read 23 Oct 2026, 16:00 UTC');
  assert.equal(p.stale, false);
  assert.equal(isStale(readAt, '2026-10-24T16:00:01Z'), true);
  assert.match(provenance({server: null, readAt, now: readAt, ...UTC}).text, /^Connected · MCP server ·/);
});

test('engine error codes get a plain explanation and keep the engine message', () => {
  assert.deepEqual(errorView({code: 'INSUFFICIENT_SCOPE', message: "Role 'pm' required"}), {
    code: 'INSUFFICIENT_SCOPE',
    summary: 'Your engine token does not carry the pm role, which reading opportunities needs.',
    detail: "Role 'pm' required"});
  assert.equal(errorView({code: 'SOMETHING_NEW'}).summary, 'The call failed.');
  assert.equal(errorView({}).code, 'TOOL_ERROR');
});

test('a partial host-context update merges, never replaces', () => {
  const initial = {theme: 'light', locale: 'en-GB', styles: {variables: {'--font-sans': 'Inter', '--color-background-primary': '#ffffff'}, css: {fonts: '@font-face{}'}}};
  const themeOnly = mergeHostContext(initial, {theme: 'dark'});
  assert.equal(themeOnly.theme, 'dark');
  assert.deepEqual(themeOnly.styles, initial.styles);
  const someVars = mergeHostContext(themeOnly, {styles: {variables: {'--color-background-primary': '#1a1a1a'}}});
  assert.deepEqual(someVars.styles.variables, {'--font-sans': 'Inter', '--color-background-primary': '#1a1a1a'});
  assert.equal(someVars.styles.css.fonts, '@font-face{}');
  assert.equal(someVars.locale, 'en-GB');
  assert.deepEqual(initial.styles.variables['--color-background-primary'], '#ffffff'); // not mutated
});

test('colour parsing and WCAG contrast match the BRAND.md table', () => {
  assert.deepEqual(parseColor('#fff'), [255, 255, 255]);
  assert.deepEqual(parseColor('rgb(26, 26, 26)'), [26, 26, 26]);
  assert.deepEqual(parseColor('rgb(26 26 26 / 100%)'), [26, 26, 26]);
  for (const unknown of ['var(--x)', 'oklch(0.2 0 0)', 'transparent', 'rgba(0,0,0,0.5)', '#0008']) assert.equal(parseColor(unknown), null);
  const round = n => Math.round(n * 100) / 100;
  assert.equal(round(contrast(BRAND.purple, '#ffffff')), 4.74);
  assert.equal(round(contrast(BRAND.lightBlue, BRAND.black90)), 7.98);
  assert.equal(round(contrast(BRAND.lightBlue, '#ffffff')), 2.18);
  assert.equal(round(contrast(BRAND.darkPurple, BRAND.black90)), 1.05);
  assert.equal(round(contrast(BRAND.purple, BRAND.aiWhite)), 4.23);
  assert.equal(contrast('var(--x)', '#fff'), null);
});

test('accents: purple on light, light blue on dark, dark purple only for light headings', () => {
  const light = palette({theme: 'light'});
  assert.deepEqual([light.background, light.accentText, light.accentUi, light.heading],
    ['#ffffff', BRAND.purple, BRAND.purple, BRAND.darkPurple]);
  const dark = palette({theme: 'dark'});
  assert.deepEqual([dark.background, dark.accentText, dark.accentUi, dark.heading],
    [BRAND.black90, BRAND.lightBlue, BRAND.lightBlue, BRAND.aiWhite]);
});

test('an accent that fails on the resolved host surface falls back to host colours', () => {
  const vars = {'--color-background-primary': '#f2f2f2', '--color-text-primary': '#111111', '--color-ring-primary': '#2255ff'};
  const p = palette({theme: 'light', styles: {variables: vars}});
  assert.equal(p.accentText, '#111111'); // purple is 4.23:1 on #f2f2f2, below 4.5
  assert.equal(p.accentUi, BRAND.purple); // still above 3:1 for UI parts
  const grey = palette({theme: 'dark', styles: {variables: {'--color-background-primary': '#6b6b6b', '--color-text-primary': '#ffffff'}}});
  assert.equal(grey.accentText, '#ffffff'); // light blue is under 4.5:1 on mid grey
  assert.equal(grey.accentUi, '#ffffff'); // and under 3:1, so the ring falls back too (no ring var: text)
  const unknown = palette({theme: 'light', styles: {variables: {'--color-background-primary': 'var(--bg)', '--color-text-primary': '#222'}}});
  assert.deepEqual([unknown.accentText, unknown.heading], ['#222', '#222']); // cannot check, so never a brand colour
});

test('the theme is inferred from the surface when the host omits it', () => {
  assert.equal(palette({styles: {variables: {'--color-background-primary': '#121212'}}}).theme, 'dark');
  assert.equal(palette({styles: {variables: {'--color-background-primary': '#fafafa'}}}).theme, 'light');
  assert.equal(palette({}).theme, 'light');
});

test('status colours: host semantic colours first, brand only where it passes', () => {
  assert.equal(palette({theme: 'light', styles: {variables: {'--color-text-danger': '#c00'}}}).danger, '#c00');
  assert.equal(palette({theme: 'light'}).danger, BRAND.red);
  assert.equal(palette({theme: 'dark'}).danger, BRAND.aiWhite); // red fails on #1a1a1a
  assert.equal(palette({theme: 'dark'}).warning, BRAND.yellow);
  assert.equal(palette({theme: 'light'}).warning, BRAND.black90); // yellow fails on light surfaces
});
