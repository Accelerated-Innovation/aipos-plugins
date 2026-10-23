// node check-page.mjs [screenshot-directory]
// Drives the built panel (dist/opportunities.html) inside the mock host in real Chrome: the SDK's
// own host bridge, a sandboxed iframe under the MCP Apps default CSP, and the captured engine
// results. Reuses the journey viewer's pinned Playwright (set PANEL_PLAYWRIGHT_MODULE to point
// elsewhere); nothing here ships.
import assert from 'node:assert/strict';
import {mkdirSync, mkdtempSync, readdirSync, readFileSync, writeFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join, resolve} from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
import {build} from 'esbuild';
import {buildPanel} from './build.mjs';

const here = fileURLToPath(new URL('.', import.meta.url));
const {chromium} = await import(process.env.PANEL_PLAYWRIGHT_MODULE
  || new URL('../../viewers/journey/node_modules/playwright-core/index.mjs', import.meta.url).href);
const shots = process.argv[2] ? resolve(process.argv[2]) : null;
if (shots) mkdirSync(shots, {recursive: true});

const panel = readFileSync(join(here, 'dist/opportunities.html'), 'utf8');
assert.equal(panel, (await buildPanel()).html, 'dist/opportunities.html is stale: run node build.mjs first');

const ALLOWED = new Set(['list_opportunities', 'get_problem', 'list_evidence']);
const READ_AT = '2026-10-23T16:00:00Z';
const read = path => JSON.parse(readFileSync(join(here, path), 'utf8'));
const captures = Object.fromEntries(readdirSync(join(here, 'fixtures/mcp')).filter(f => f.endsWith('.json'))
  .map(f => [f.replace(/\.json$/, ''), read(`fixtures/mcp/${f}`)]));
const key = (name, args) => `${name} ${JSON.stringify(args)}`;
const CAPTURED = Object.fromEntries(Object.values(captures).filter(c => !c.result.isError)
  .map(c => [key(c.request.name, c.request.arguments), c.result]));
const result = stem => captures[stem].result;
// The boundary the plan names: MCP structuredContent is the REST sample's data field. Wrap it the
// way the engine's server does (see any captured success) instead of handing the panel {data, error}.
const fromSample = name => {
  const {data} = read(`fixtures/engine-samples/${name}.json`);
  return {...structuredClone(result('get-problem')), content: [{type: 'text', text: JSON.stringify(data, null, 2)}], structuredContent: data};
};

const LIGHT = {
  theme: 'light', locale: 'en-GB', timeZone: 'UTC', platform: 'desktop',
  styles: {variables: {
    '--color-background-primary': '#ffffff', '--color-text-primary': '#1f1f1f',
    '--color-text-secondary': '#595959', '--color-border-primary': '#d9d9d9',
    '--color-ring-primary': '#2f6feb', '--font-sans': '"Trebuchet MS", system-ui, sans-serif',
  }},
};
const DARK_COLOURS = {styles: {variables: {
  '--color-background-primary': '#1a1a1a', '--color-text-primary': '#f2f2f2',
  '--color-text-secondary': '#b8b8b8', '--color-border-primary': '#3d3d3d', '--color-ring-primary': '#7aa7ff',
}}};

const mockHost = (await build({
  entryPoints: [join(here, 'mock-host.mjs')], bundle: true, format: 'iife', write: false, logLevel: 'silent',
})).outputFiles[0].text;
assert.ok(!/<\/script/i.test(mockHost), 'mock host bundle cannot be inlined');
const tmp = mkdtempSync(join(tmpdir(), 'opportunities-panel-'));

function hostPage(name, config) {
  const json = JSON.stringify({panel, now: READ_AT, hostContext: LIGHT, input: {offset: 0, limit: 20},
    initial: result('list-opportunities'), ...config, responses: {...CAPTURED, ...config.responses}})
    .replace(/</g, '\\u003c');
  const file = join(tmp, `${name}.html`);
  writeFileSync(file, `<!doctype html><html><head><meta charset="utf-8"><title>Mock host: ${name}</title>
<style>body{margin:0;background:#8a8a8a;padding:12px}#frame iframe{border:0;width:100%;display:block;min-height:80px}</style>
</head><body><div id="frame"></div><script>window.__MOCK__=${json}</script><script>${mockHost}</script></body></html>`);
  return pathToFileURL(file).href;
}

const browser = await chromium.launch({channel: 'chrome'});
const problems = [];
async function open(name, config = {}, viewport = {width: 1000, height: 900}) {
  const page = await browser.newPage({viewport});
  page.on('pageerror', e => problems.push(`${name}: page error ${e.message}`));
  page.on('console', m => { if (m.type() === 'error') problems.push(`${name}: console error ${m.text()}`); });
  page.on('request', r => { if (!/^(file|data|about|blob):/.test(r.url())) problems.push(`${name}: remote request ${r.url()}`); });
  await page.goto(hostPage(name, config));
  await page.waitForFunction(() => globalThis.__HOST__?.initialized || globalThis.__HOST__?.error);
  assert.equal(await page.evaluate(() => globalThis.__HOST__.error ?? null), null, `${name}: host failed`);
  const frame = page.frameLocator('iframe');
  const host = () => page.evaluate(() => ({calls: globalThis.__HOST__.calls, links: globalThis.__HOST__.links, sizes: globalThis.__HOST__.sizes}));
  const panelFrame = () => page.frames().find(f => f !== page.mainFrame());
  return {page, frame, host, panelFrame};
}
const text = locator => locator.innerText();
// Screenshots wait until the host has applied the panel's last size-changed report.
async function settled(page) {
  const inner = page.frames().find(f => f !== page.mainFrame());
  for (let i = 0; i < 40; i++) {
    const wanted = await inner.evaluate(() => Math.ceil(document.documentElement.getBoundingClientRect().height));
    const given = await page.locator('iframe').evaluate(el => el.clientHeight);
    if (Math.abs(wanted - given) <= 1) return;
    await page.waitForTimeout(50);
  }
  throw new Error('the host never matched the panel height');
}
const shoot = async (page, file) => {
  if (!shots) return;
  await settled(page);
  await page.screenshot({path: join(shots, file), fullPage: true});
};

try {
  // --- Open, page, filter, sort, drill in, theme, narrow -------------------------------------
  {
    const {page, frame, host, panelFrame} = await open('paged', {
      input: {offset: 0, limit: 1}, initial: result('list-opportunities-first-of-two')});
    await frame.locator('#list-view:not([hidden])').waitFor();
    assert.equal(await text(frame.locator('#provenance')), 'Connected · opportunity-engine · read 23 Oct 2026, 16:00 UTC');
    assert.equal(await frame.locator('#stale').isVisible(), false);
    assert.equal(await frame.locator('#rows tr').count(), 1);
    assert.equal(await text(frame.locator('#coverage')), '1 loaded of 2 opportunities.');
    const first = await text(frame.locator('[data-row="p-1"]'));
    assert.match(first, /Exports time out on large accounts[\s\S]*4\.50[\s\S]*aha:OPP-12/);
    assert.doesNotMatch(first, /OPP-99/, 'a severed link is not shown as active');
    assert.equal(await frame.locator('#empty').isVisible(), false);
    assert.match(await text(frame.locator('#version')), /^Opportunities panel \d+\.\d+\.\d+$/);
    const font = await frame.locator('body').evaluate(el => getComputedStyle(el).fontFamily);
    assert.match(font, /Trebuchet MS/, 'the host font is used');

    // More: the next page through the host, appended, focus on the first new row
    assert.equal(await text(frame.locator('#more')), 'Load the next 1');
    await frame.locator('#more').click();
    await frame.locator('[data-row="p-2"]').waitFor();
    assert.equal(await frame.locator('#more').isVisible(), false);
    assert.equal(await text(frame.locator('#coverage')), '2 opportunities.');
    assert.equal(await frame.locator('#open-p-2').evaluate(el => el === document.activeElement), true);
    assert.ok((await host()).calls.includes(key('list_opportunities', {offset: 1, limit: 1})));

    // Filter, work-item filter, sort
    await frame.locator('#search').fill('bulk');
    assert.deepEqual(await frame.locator('#rows tr').evaluateAll(rows => rows.map(r => r.dataset.row)), ['p-2']);
    assert.equal(await text(frame.locator('#coverage')), 'Showing 1 of 2 opportunities.');
    await frame.locator('#search').fill('zzz');
    assert.equal(await frame.locator('#no-match').isVisible(), true);
    await frame.locator('#search').fill('');
    await frame.locator('#linked').selectOption('linked');
    assert.deepEqual(await frame.locator('#rows tr').evaluateAll(rows => rows.map(r => r.dataset.row)), ['p-1']);
    await frame.locator('#linked').selectOption('all');
    await frame.locator('#sort').selectOption('title');
    assert.deepEqual(await frame.locator('#rows tr').evaluateAll(rows => rows.map(r => r.dataset.row)), ['p-2', 'p-1']);
    await frame.locator('#sort').selectOption('rank');
    await shoot(page, 'light-list.png');

    // Drill in by keyboard only
    await frame.locator('#open-p-1').focus();
    await page.keyboard.press('Enter');
    await frame.locator('.evidence li').first().waitFor();
    assert.equal(await frame.locator('#detail-title').evaluate(el => el === document.activeElement), true);
    assert.equal(await frame.locator('#list-view').isVisible(), false);
    const detail = await text(frame.locator('#detail-view'));
    assert.match(detail, /p-1 · rank 1 · lineage lin-1/);
    assert.match(detail, /Ops lead\s+80%/);
    assert.match(detail, /3 of 3 references\. References only; evidence text is not shown in this panel\./);
    assert.match(detail, /Export completion time: 42\.5 minutes \(n=12, time study\)/);
    assert.match(detail, /Call transcript · gong · 1 Jun 2026/);
    assert.equal(await frame.locator('.evidence li').count(), 3);
    const calls = (await host()).calls;
    assert.ok(calls.includes(key('get_problem', {problem_id: 'p-1'})) && calls.includes(key('list_evidence', {problem_id: 'p-1'})));

    // Record links go to the host's ui/open-link, and a refusal is said
    await frame.locator('.evidence a', {hasText: 'gong:c-1'}).click();
    await page.waitForFunction(() => globalThis.__HOST__.links.length === 1);
    assert.deepEqual((await host()).links, ['https://app.gong.io/call?id=c-1']);
    await shoot(page, 'light-detail.png');

    // Escape returns to the list with focus on the row it came from
    await page.keyboard.press('Escape');
    await frame.locator('#list-view:not([hidden])').waitFor();
    assert.equal(await frame.locator('#open-p-1').evaluate(el => el === document.activeElement), true);

    // A partial host-context update (theme only) merges: the host font survives, and the accent
    // is re-checked against the surface the host still declares (white), so it falls back
    await page.evaluate(() => globalThis.__HOST__.setContext({theme: 'dark'}));
    await frame.locator('html[data-theme="dark"]').waitFor();
    assert.match(await frame.locator('body').evaluate(el => getComputedStyle(el).fontFamily), /Trebuchet MS/);
    const link = () => frame.locator('#open-p-1').evaluate(el => getComputedStyle(el).color);
    assert.equal(await link(), 'rgb(31, 31, 31)', 'light blue fails on white, so the host text colour is used');
    // Then colour variables only: the font still survives, and the dark accent applies
    await page.evaluate(update => globalThis.__HOST__.setContext(update), DARK_COLOURS);
    await page.waitForFunction(() => true);
    await frame.locator('body').evaluate(() => new Promise(r => requestAnimationFrame(r)));
    assert.equal(await link(), 'rgb(10, 190, 239)');
    assert.equal(await frame.locator('body').evaluate(el => getComputedStyle(el).backgroundColor), 'rgb(26, 26, 26)');
    assert.equal(await frame.locator('h1').evaluate(el => getComputedStyle(el).color), 'rgb(242, 242, 242)');
    assert.match(await frame.locator('body').evaluate(el => getComputedStyle(el).fontFamily), /Trebuchet MS/);
    await shoot(page, 'dark-list.png');
    await frame.locator('#open-p-2').click();
    await frame.locator('.evidence li').first().waitFor();
    assert.match(await text(frame.locator('#detail-view')), /Data admin\s+60%[\s\S]*1 of 1 references/);
    await shoot(page, 'dark-detail.png');
    await frame.locator('#back').click();

    // Narrow: components leave the table for the detail view
    await page.setViewportSize({width: 420, height: 900});
    await frame.locator('td.component').first().waitFor({state: 'hidden'});
    assert.equal(await frame.locator('#open-p-1').isVisible(), true);
    await shoot(page, 'dark-narrow.png');

    // Stale past 24 hours, on the next render
    await panelFrame().evaluate(() => { globalThis.__PANEL_NOW__ = '2026-10-24T16:00:01Z'; });
    await frame.locator('#search').fill('e');
    assert.equal(await frame.locator('#stale').isVisible(), true);
    assert.match(await text(frame.locator('#stale')), /Stale:/);

    const seen = await host();
    assert.ok(seen.sizes.length > 0 && seen.sizes.every(h => h > 0), 'the panel reports its size to the host');
    for (const call of seen.calls) assert.ok(ALLOWED.has(call.split(' ')[0]), `called ${call}`);
    await page.close();
  }

  // --- A refused initial call shows the engine code, not an empty list ------------------------
  {
    const {page, frame} = await open('refused', {initial: result('error-insufficient-scope')});
    await frame.locator('.error-block').waitFor();
    const status = await text(frame.locator('#status'));
    assert.match(status, /Opportunities could not be read: INSUFFICIENT_SCOPE/);
    assert.match(status, /does not carry the pm role/);
    assert.match(status, /Engine message: Role 'pm' required/);
    assert.equal(await frame.locator('#list-view').isVisible(), false);
    await shoot(page, 'light-refused.png');
    await page.close();
  }

  // --- No scoring run yet ----------------------------------------------------------------------
  {
    const {page, frame} = await open('empty', {initial: result('list-opportunities-empty')});
    await frame.locator('#empty').waitFor();
    assert.equal(await text(frame.locator('#coverage')), 'No opportunities.');
    assert.equal(await frame.locator('#controls').isVisible(), false);
    assert.equal(await frame.locator('#more').isVisible(), false);
    await page.close();
  }

  // --- A failed detail read is shown, never folded into "none" --------------------------------
  {
    const {page, frame} = await open('evidence-refused', {
      delay: 150, responses: {[key('list_evidence', {problem_id: 'p-1'})]: result('error-problem-not-found')}});
    await frame.locator('#open-p-1').click();
    assert.match(await text(frame.locator('#detail-view')), /Reading evidence references…/);
    await frame.locator('#detail-view .error-block').waitFor();
    const detail = await text(frame.locator('#detail-view'));
    assert.match(detail, /Ops lead\s+80%/);
    assert.match(detail, /Evidence references could not be read: PROBLEM_NOT_FOUND/);
    assert.doesNotMatch(detail, /of \d+ references/);
    await page.close();
  }

  // --- Cancelled before the result -------------------------------------------------------------
  {
    const {page, frame} = await open('cancelled', {cancel: true});
    await frame.locator('#status', {hasText: 'cancelled'}).waitFor();
    await page.close();
  }

  // --- The published engine samples, carried as MCP results -----------------------------------
  {
    const {page, frame} = await open('samples', {
      initial: fromSample('opportunities'),
      responses: {
        [key('get_problem', {problem_id: 'prob-1a2b3c'})]: fromSample('problem-detail'),
        [key('list_evidence', {problem_id: 'prob-1a2b3c'})]: fromSample('problem-evidence'),
      }});
    await frame.locator('[data-row="prob-1a2b3c"]').waitFor();
    assert.match(await text(frame.locator('[data-row="prob-1a2b3c"]')), /CSV export times out for large reports[\s\S]*0\.78/);
    await frame.locator('#open-prob-1a2b3c').click();
    await frame.locator('.evidence li').nth(2).waitFor();
    const detail = await text(frame.locator('#detail-view'));
    assert.match(detail, /Operations Analyst\s+95%[\s\S]*Administrator\s+90%/);
    assert.match(detail, /Support ticket · zendesk · 26 Jun 2026/);
    await shoot(page, 'light-samples-detail.png');
    await page.close();
  }

  assert.deepEqual(problems, [], 'no page errors, console errors (including CSP violations) or remote requests');
  console.log(`check-page: all scenarios passed${shots ? `; screenshots in ${shots}` : ''}.`);
} finally {
  await browser.close();
}
