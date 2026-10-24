// npm run dev  (PORT=5173 by default)
// A local dev server for UI work: the panel inside the mock host at http://localhost:PORT, rebuilt
// in memory whenever a source file changes, and the browser reloaded. The toolbar picks a scenario,
// a theme and a width. It never writes dist/: run `node build.mjs` before committing. Never shipped.
import {watch} from 'node:fs';
import {createServer} from 'node:http';
import {fileURLToPath} from 'node:url';
import {buildPanel} from './build.mjs';
import {DARK_COLOURS, LIGHT, bundleMockHost, fromSample, hostPage, key, result} from './mock-scenarios.mjs';

const here = fileURLToPath(new URL('.', import.meta.url));
const PORT = Number(process.env.PORT || 5173);

const SCENARIOS = {
  list: {label: 'Ranked list', config: {}},
  paged: {label: 'Two pages (load more)', config: {input: {offset: 0, limit: 1}, initial: result('list-opportunities-first-of-two')}},
  samples: {label: 'Engine samples', config: {
    initial: fromSample('opportunities'),
    responses: {
      [key('get_problem', {problem_id: 'prob-1a2b3c'})]: fromSample('problem-detail'),
      [key('list_evidence', {problem_id: 'prob-1a2b3c'})]: fromSample('problem-evidence'),
    }}},
  slow: {label: 'Slow detail reads (2 s)', config: {delay: 2000}},
  empty: {label: 'No opportunities', config: {initial: result('list-opportunities-empty')}},
  refused: {label: 'List refused (scope)', config: {initial: result('error-insufficient-scope')}},
  'evidence-refused': {label: 'Evidence read fails', config: {
    delay: 150, responses: {[key('list_evidence', {problem_id: 'p-1'})]: result('error-problem-not-found')}}},
  cancelled: {label: 'Cancelled by the user', config: {cancel: true}},
};
const THEMES = {
  light: LIGHT,
  dark: {...LIGHT, theme: 'dark', styles: {variables: {...LIGHT.styles.variables, ...DARK_COLOURS.styles.variables}}},
};
const WIDTHS = {full: '', 640: '640px', 420: '420px'};

// One build at a time; requests wait for the latest. A failed build is shown, not thrown.
let current;
function rebuild() {
  current = (async () => {
    const started = Date.now();
    try {
      const [{html}, mockHost] = await Promise.all([buildPanel(), bundleMockHost()]);
      console.log(`built in ${Date.now() - started} ms`);
      return {panel: html, mockHost};
    } catch (error) {
      console.error(`build failed: ${error.message}`);
      return {error};
    }
  })();
  return current;
}

const clients = new Set();
let timer;
watch(here, (event, file) => {
  if (!file || !/\.(mjs|css|html)$/.test(file) || file === 'dev.mjs' || file.endsWith('.test.mjs')) return;
  clearTimeout(timer);
  timer = setTimeout(async () => {
    await rebuild();
    for (const res of clients) res.write('data: reload\n\n');
  }, 100);
});

const escape = text => String(text).replace(/[&<>"]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'})[c]);
const options = (choices, chosen) => Object.entries(choices)
  .map(([value, label]) => `<option value="${value}"${value === chosen ? ' selected' : ''}>${escape(label)}</option>`).join('');

const RELOAD = `<script>new EventSource('/events').onmessage = () => location.reload();</script>`;
const STYLE = `<style>
#dev{display:flex;gap:16px;flex-wrap:wrap;align-items:center;margin:-12px -12px 12px;padding:8px 12px;
  background:#2b2b2b;color:#eee;font:13px system-ui,sans-serif}
#dev label{display:flex;gap:6px;align-items:center}#dev span{margin-left:auto;opacity:.7}
#frame{margin:0 auto}
pre{background:#fff;color:#a00;padding:16px;white-space:pre-wrap;font:13px ui-monospace,monospace}
</style>`;

function toolbar(scenario, theme, width) {
  return `<form id="dev" onchange="this.submit()">
<label>Scenario <select name="scenario">${options(Object.fromEntries(Object.entries(SCENARIOS).map(([k, s]) => [k, s.label])), scenario)}</select></label>
<label>Theme <select name="theme">${options({light: 'Light', dark: 'Dark'}, theme)}</select></label>
<label>Width <select name="width">${options({full: 'Full', 640: '640 px', 420: '420 px'}, width)}</select></label>
<span>Dev preview with recorded engine data. Not the shipped build: run node build.mjs before committing.</span>
</form>`;
}

async function page(url) {
  const scenario = SCENARIOS[url.searchParams.get('scenario')] ? url.searchParams.get('scenario') : 'list';
  const theme = THEMES[url.searchParams.get('theme')] ? url.searchParams.get('theme') : 'light';
  const width = url.searchParams.get('width') in WIDTHS ? url.searchParams.get('width') : 'full';
  const built = await current;
  const bar = toolbar(scenario, theme, width);
  if (built.error) {
    return `<!doctype html><html><head><meta charset="utf-8"><title>Build failed</title>${STYLE}
<style>body{margin:0;background:#8a8a8a;padding:12px}</style>${RELOAD}</head><body>${bar}
<pre>Build failed. Fix the source and save; this page reloads.\n\n${escape(built.error.stack || built.error)}</pre></body></html>`;
  }
  const head = STYLE + (WIDTHS[width] ? `<style>#frame{max-width:${WIDTHS[width]}}</style>` : '') + RELOAD;
  return hostPage({name: SCENARIOS[scenario].label, panel: built.panel, mockHost: built.mockHost,
    config: {...SCENARIOS[scenario].config, hostContext: THEMES[theme]}, head, before: bar});
}

await rebuild();
createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);
  if (url.pathname === '/events') {
    res.writeHead(200, {'content-type': 'text/event-stream', 'cache-control': 'no-cache', connection: 'keep-alive'});
    res.write(': connected\n\n');
    clients.add(res);
    res.on('close', () => clients.delete(res));
  } else if (url.pathname === '/') {
    res.writeHead(200, {'content-type': 'text/html; charset=utf-8', 'cache-control': 'no-store'});
    res.end(await page(url));
  } else if (url.pathname === '/favicon.ico') {
    res.writeHead(204).end();
  } else {
    res.writeHead(404).end();
  }
}).listen(PORT, '127.0.0.1', () => {
  console.log(`Opportunities panel dev server: http://localhost:${PORT}\nWatching ${here} for changes. Ctrl+C to stop.`);
});
