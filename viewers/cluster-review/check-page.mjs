// node check-page.mjs /absolute/board.html [screenshot-directory]
// Drives a board rendered from fixtures/demo-review.json in real Chrome. Reuses the journey
// viewer's pinned Playwright (set CLUSTER_PLAYWRIGHT_MODULE to point elsewhere); nothing here ships.
import assert from 'node:assert/strict';
import {mkdirSync} from 'node:fs';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';

const {chromium} = await import(process.env.CLUSTER_PLAYWRIGHT_MODULE ||
  new URL('../journey/node_modules/playwright-core/index.mjs', import.meta.url).href);
const target = process.argv[2], shots = process.argv[3];
if (!target) throw new Error('Pass the rendered board HTML file.');
if (shots) mkdirSync(shots, {recursive: true});
const url = pathToFileURL(resolve(target)).href;
const FRESH = '2026-10-21T19:00:00+00:00', OLD = '2026-10-24T19:00:00+00:00';

const browser = await chromium.launch({channel: 'chrome'});
try {
  const page = await browser.newPage({viewport: {width: 1400, height: 1000}});
  const errors = [], remote = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('request', r => { if (!/^(file|data|blob):/.test(r.url())) remote.push(r.url()); });
  await page.addInitScript(now => { globalThis.__BOARD_NOW__ = now; }, FRESH);
  await page.goto(url);
  await page.waitForSelector('#board:not([hidden])');

  // Provenance and labels
  assert.match(await page.locator('.pill').innerText(), /Draft/);
  assert.match(await page.locator('#source').innerText(), /Supplied records · synthetic · captured 2026-10-21T18:00:00\+00:00/);
  assert.doesNotMatch(await page.locator('#source').innerText(), /live/i);
  assert.match(await page.locator('#coverage').innerText(), /8 of 8 problems read/);
  assert.equal(await page.locator('#stale').isVisible(), false);
  assert.match(await page.locator('.notice').innerText(), /nothing is applied, sent or written/);

  // Problems table; workflow tags are unknown, not "none"
  assert.equal(await page.locator('#rows tr').count(), 8);
  assert.match(await page.locator('[data-row="fixture:prb-renewal-quotes"]').innerText(), /unknown — not in the graph/);
  if (shots) await page.screenshot({path: `${shots}/desktop.png`, fullPage: true});

  // Compare two by keyboard; a third pick is disabled
  await page.locator('#pick-fixture\\:prb-renewal-quotes').focus();
  await page.keyboard.press('Space');
  assert.match(await page.locator('#compare').innerText(), /Pick one more problem/);
  await page.locator('#pick-fixture\\:prb-quote-templates').check();
  const compared = await page.locator('#compare').innerText();
  assert.match(compared, /fixture:prb-renewal-quotes ↔ fixture:prb-quote-templates/);
  assert.match(compared, /Shared evidence\s+gong:call-7781/);
  assert.match(compared, /Shared personas\s+Account Executive/);
  assert.match(compared, /not a verdict/);
  assert.equal(await page.locator('#pick-fixture\\:prb-month-end').isDisabled(), true);

  // Suggestions cite evidence; preparing one makes a pending, unapplied hand-off
  assert.equal(await page.locator('[data-suggestion]').count(), 2);
  assert.match(await page.locator('[data-suggestion="s2"]').innerText(), /Tickets reach the wrong team[\s\S]*gong:call-5530/);
  await page.locator('[data-prepare="s1"]').click();
  assert.equal(await page.locator('[data-prepare="s1"]').isDisabled(), true);
  assert.match(await page.locator('[data-prepare="s1"]').innerText(), /Prepared — pending/);
  assert.match(await page.locator('[data-prepared="s1"]').innerText(), /merge .* — pending, not applied/);
  const handoff = JSON.parse(await page.locator('#handoff').inputValue());
  assert.equal(handoff.draft, true);
  assert.equal(handoff.corrections[0].status, 'pending');
  assert.equal(handoff.corrections[0].applied, false);
  assert.match(handoff.corrections[0].destination, /^TBD/);
  assert.equal(handoff.corrections[0].stale, false);
  assert.equal(await page.evaluate(() => document.activeElement.id), 'prepared-heading');
  if (shots) await page.screenshot({path: `${shots}/prepared.png`, fullPage: true});

  // Remove returns to the empty state
  await page.locator('[data-prepared="s1"] button').click();
  assert.equal(await page.locator('#prepared-empty').isVisible(), true);
  assert.equal(await page.locator('#handoff-wrap').isVisible(), false);
  assert.equal(await page.locator('[data-prepare="s1"]').isDisabled(), false);

  // Excerpts are redacted, labelled, and within the cap
  assert.equal(await page.locator('.excerpt').count(), 1);
  assert.match(await page.locator('.excerpt figcaption').innerText(), /Redacted excerpt · gong:call-5530/);
  assert.match(await page.locator('#excerpt-count').innerText(), /1 of at most 5/);

  // Narrow screen: no page-level horizontal scroll
  await page.setViewportSize({width: 390, height: 844});
  assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth),
    'horizontal overflow on a phone-width viewport');
  if (shots) await page.screenshot({path: `${shots}/mobile.png`});

  // A stale capture is announced and carried into prepared corrections
  const stale = await browser.newPage();
  stale.on('pageerror', e => errors.push(e.message));
  stale.on('request', r => { if (!/^(file|data|blob):/.test(r.url())) remote.push(r.url()); });
  await stale.addInitScript(now => { globalThis.__BOARD_NOW__ = now; }, OLD);
  await stale.goto(url);
  await stale.waitForSelector('#board:not([hidden])');
  assert.equal(await stale.locator('#stale').isVisible(), true);
  await stale.locator('[data-prepare="s2"]').click();
  assert.match(await stale.locator('[data-prepared="s2"]').innerText(), /stale capture/);
  const staleHandoff = JSON.parse(await stale.locator('#handoff').inputValue());
  assert.equal(staleHandoff.corrections[0].stale, true);
  assert.equal(staleHandoff.corrections[0].sides.length, 2);

  assert.deepEqual(errors, []);
  assert.deepEqual(remote, []);
  console.log('Board checks passed: provenance and draft labels, unknown workflow tags, keyboard compare, '
    + 'two-pick limit, pending-only corrections and hand-off, remove, redacted excerpts, stale capture, '
    + 'phone width, no script errors, no network requests.');
} finally {
  await browser.close();
}
