// node check-page.mjs /absolute/dashboard.html [screenshot-directory]
// Reuses the journey viewer's pinned Playwright; no runtime dependency is shipped.
import assert from 'node:assert/strict';
import {mkdirSync} from 'node:fs';
import {resolve} from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';
const {chromium}=await import(process.env.PORTFOLIO_PLAYWRIGHT_MODULE || new URL('../journey/node_modules/playwright-core/index.mjs',import.meta.url).href);
const target=process.argv[2],shots=process.argv[3];if(!target)throw new Error('Pass the rendered HTML file.');if(shots)mkdirSync(shots,{recursive:true});
const fixtures=fileURLToPath(new URL('../../plugins/aipos/skills/aipos-portfolio-dashboard/evals/files/',import.meta.url));
const browser=await chromium.launch({channel:'chrome'});
try{
const page=await browser.newPage({viewport:{width:1500,height:1000}}),errors=[],remote=[];
page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(!/^(file|data|blob):/.test(r.url()))remote.push(r.url());});
await page.goto(pathToFileURL(resolve(target)).href);await page.waitForFunction(()=>document.querySelector('#status').hidden);
if(shots)await page.screenshot({path:shots+'/desktop.png',fullPage:true});
assert.equal(await page.locator('#dashboard').isVisible(),true,await page.locator('#error').innerText());
assert.equal(await page.locator('#rows tr').count(),32);
await page.locator('#product').selectOption('CLAIMS');await page.locator('#phase').selectOption('exploration');await page.locator('#disposition').selectOption('open');assert.equal(await page.locator('#rows tr').count(),1);
await page.locator('#rows .case-link').first().focus();await page.keyboard.press('Enter');assert.match(await page.locator('#detail').innerText(),/CL01/);
await page.getByRole('tab',{name:'Evidence',exact:true}).click();assert.match(await page.locator('#case-content').innerText(),/2 observed \/ 6 planned/);assert.match(await page.locator('#case-content').innerText(),/No measured finding/);
await page.keyboard.press('ArrowRight');assert.equal(await page.getByRole('tab',{name:'History',exact:true}).getAttribute('aria-selected'),'true');
await page.locator('#clear-filters').click();await page.locator('#product').selectOption('BROKER');assert.equal(await page.locator('#rows tr').count(),10);
await page.locator('#phase').selectOption('retired');await page.locator('#disposition').selectOption('open');assert.equal(await page.locator('#empty').isVisible(),true);assert.doesNotMatch(await page.locator('#detail').innerText(),/CL01/);await page.locator('#empty-clear').click();
for(const id of ['Q01','Q02','Q03','Q04','Q05','Q06','Q07','Q08','Q09','Q10']){await page.locator(`[data-question=${id}]`).click();assert.equal(await page.locator(`[data-answer=${id}]`).count(),1);}
assert.match(await page.locator('[data-answer=Q04]').innerText(),/daily carrier exports/);assert.match(await page.locator('[data-answer=Q09]').innerText(),/1.5 percentage points/);
await page.locator('[data-answer=Q09]').getByRole('button',{name:'Inspect CL06'}).click();await page.getByRole('tab',{name:'Results',exact:true}).click();assert.match(await page.locator('#case-content').innerText(),/18 → 11 minutes/);
if(shots)await page.screenshot({path:shots+'/detail.png',fullPage:true});
await page.locator('#chat-input').fill('Approve CL02');await page.locator('#chat-form').getByRole('button').click();assert.match(await page.locator('#conversation').innerText(),/cannot approve/);
await page.setViewportSize({width:390,height:844});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=document.documentElement.clientWidth),'Mobile horizontal overflow');if(shots)await page.screenshot({path:shots+'/mobile.png',fullPage:true});
for(const file of ['partial-page','mixed-revisions','unavailable']){await page.locator('#file-input').setInputFiles(fixtures+file+'.json');await page.waitForFunction(()=>document.querySelector('#status').hidden);assert.equal(await page.locator('#dashboard').isVisible(),false);assert.equal(await page.locator('#error').isVisible(),true);}
await page.locator('#file-input').setInputFiles(fixtures+'portfolio.json');await page.waitForFunction(()=>!document.querySelector('#dashboard').hidden);assert.equal(await page.locator('#rows tr').count(),32);assert.equal(await page.locator('[data-answer]').count(),0,'Reload retains stale chat');
assert.deepEqual(errors,[]);assert.deepEqual(remote,[]);console.log('Browser checks passed: filters, keyboard/tabs, all ten questions, detail, read-only behavior, mobile, error/reload states, no network requests.');
}finally{await browser.close();}
