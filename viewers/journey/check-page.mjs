// Drives a rendered map in a real browser and checks the journey diagram.
//
//   node check-page.mjs <map.html> [screenshot-dir] [--browser chrome|webkit|firefox]
//
// Uses the installed Chrome by default. WebKit and Firefox need Playwright's
// builds once: `npx playwright-core install webkit firefox`. Exits non-zero on the first failed check. This is the manual
// verification step in references/rendering.md, not a CI gate.
import { chromium, firefox, webkit } from "playwright-core";
import { mkdirSync } from "node:fs";
import { resolve } from "node:path";

const args = process.argv.slice(2);
const browserName = args.includes("--browser") ? args[args.indexOf("--browser") + 1] : "chrome";
const [page_, shots = null] = args.filter((a, i) => !a.startsWith("--") && args[i - 1] !== "--browser");
if (!page_) {
  console.error("usage: node check-page.mjs <map.html> [screenshot-dir] [--browser chrome|webkit|firefox]");
  process.exit(2);
}
if (shots) mkdirSync(shots, { recursive: true });

const failures = [];
const check = (ok, what) => {
  console.log(`${ok ? "ok  " : "FAIL"} ${what}`);
  if (!ok) failures.push(what);
};

const browser = browserName === "webkit" ? await webkit.launch()
  : browserName === "firefox" ? await firefox.launch()
  : await chromium.launch({ channel: "chrome" });
const context = await browser.newContext({ viewport: { width: 1360, height: 900 } });
const page = await context.newPage();
const external = [];
const errors = [];
page.on("request", (r) => { if (!/^(file|data|blob|about):/.test(r.url())) external.push(r.url()); });
page.on("pageerror", (e) => errors.push(String(e)));
page.on("console", (m) => { if (m.type() === "error") errors.push(m.text()); });

await page.goto("file://" + resolve(page_), { waitUntil: "load" });
await page.waitForSelector(".jv .react-flow__node", { timeout: 8000 });
const shot = async (name) => {
  if (!shots) return;
  await page.locator(".jv").screenshot({ path: `${shots}/${name}.png` });
};

check(external.length === 0, `no network requests (${external.join(", ") || "none"})`);
check(errors.length === 0, `no script errors (${errors.join(" | ") || "none"})`);
check(!(await page.locator("details.wftables").first().evaluate((d) => d.open)),
  "table view collapses once the diagram is up");

const count = (sel) => page.locator(`.jv ${sel}`).count();
const level = async (n) => {
  await page.locator(`.jv-levels button`).nth(n - 1).click();
  await page.waitForTimeout(250);
};

await level(1);
check(await count(".jv-activity") > 0 && await count(".jv-feature") === 0, "L1 shows activities and no features");
await shot("l1");

await level(2);
check(await count(".jv-feature") > 0 && await count(".jv-scenario") === 0, "L2 adds features, not scenarios");
await shot("l2");

// Question 2: select the feature shared by both journeys.
const shared = page.locator(".jv .react-flow__node", { hasText: "2 journeys" }).first();
check(await shared.count() === 1, "a feature used by two journeys says so");
await shared.click();
await page.waitForTimeout(200);
const panel = page.locator(".jv-panel");
check(/Journeys affected if this feature changes\s*2/i.test(await panel.innerText()),
  "selecting it lists both affected journeys");
const litJourneys = await page.locator(".jv .jv-journey.jv-on").count();
check(litJourneys >= 2, `both journeys highlight (${litJourneys})`);
await shot("l2-shared-feature");

// Question 1: pick a journey and open one of its specifying scenarios.
await page.locator(".jv .react-flow__node", { hasText: "invoice-approval" }).first().click();
await page.waitForTimeout(200);
check(/Scenarios that specify this journey\s*3/i.test(await panel.innerText()),
  "a journey lists the scenarios that specify it");
check(/Under a referenced rule, not placed\s*1/i.test(await panel.innerText()),
  "and separately the ones only under a referenced rule");
await panel.getByRole("button", { name: /Manager rejects/ }).click();
await page.waitForTimeout(300);
check(await page.locator(".jv-levels button[aria-pressed=true]").innerText() === "L3 Scenarios",
  "picking a scenario moves to L3");
const detail = await panel.innerText();
check(/Given the following invoice is pending manager approval/.test(detail) && /INV-2210/.test(detail),
  "the scenario shows Given / When / Then with its data table");
check(/acceptance\.feature:\d+/.test(detail), "and where it lives");
await shot("l3-scenario");

// Keyboard: Enter on a focused node selects it, the same as a click.
await level(1);
await page.locator(".jv-clear").click().catch(() => {});
const target = page.locator(".jv .react-flow__node-activity").first();
const name = await target.locator(".jv-title").innerText();
await target.focus();
await page.keyboard.press("Enter");
await page.waitForTimeout(200);
check((await panel.locator("h3").first().innerText()) === name, `Enter on a focused node selects it (${name})`);

// Narrow screens: no horizontal page scroll.
await page.setViewportSize({ width: 375, height: 800 });
await page.waitForTimeout(250);
const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
check(overflow <= 0, `no horizontal overflow at 375px (${overflow}px)`);
if (shots) await page.screenshot({ path: `${shots}/mobile.png`, fullPage: false });

// Print: the canvas hides and the tables print.
await page.emulateMedia({ media: "print" });
await page.evaluate(() => window.dispatchEvent(new Event("beforeprint")));
check(await page.locator(".jv").evaluate((el) => getComputedStyle(el).display) === "none", "print hides the diagram");
check(await page.locator("details.wftables").first().evaluate((d) => d.open), "print opens the tables");

await browser.close();
if (failures.length) {
  console.error(`\n${failures.length} check(s) failed`);
  process.exit(1);
}
console.log("\nall checks passed");
