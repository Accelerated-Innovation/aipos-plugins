// The mock host's fixtures and page, shared by check-page.mjs and dev.mjs. Never shipped.
import assert from 'node:assert/strict';
import {readdirSync, readFileSync} from 'node:fs';
import {join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {build} from 'esbuild';

const here = fileURLToPath(new URL('.', import.meta.url));

export const READ_AT = '2026-10-23T16:00:00Z';
const read = path => JSON.parse(readFileSync(join(here, path), 'utf8'));
const captures = Object.fromEntries(readdirSync(join(here, 'fixtures/mcp')).filter(f => f.endsWith('.json'))
  .map(f => [f.replace(/\.json$/, ''), read(`fixtures/mcp/${f}`)]));
export const key = (name, args) => `${name} ${JSON.stringify(args)}`;
export const CAPTURED = Object.fromEntries(Object.values(captures).filter(c => !c.result.isError)
  .map(c => [key(c.request.name, c.request.arguments), c.result]));
export const result = stem => captures[stem].result;
// The boundary the plan names: MCP structuredContent is the REST sample's data field. Wrap it the
// way the engine's server does (see any captured success) instead of handing the panel {data, error}.
export const fromSample = name => {
  const {data} = read(`fixtures/engine-samples/${name}.json`);
  return {...structuredClone(result('get-problem')), content: [{type: 'text', text: JSON.stringify(data, null, 2)}], structuredContent: data};
};

// find_similar_problems is not captured from the engine yet (it needs the gate-1 flag and an
// index); this is the response shape from src/engine/api/schemas.py SimilarProblemsResponse.
export const SIMILAR = {
  content: [{type: 'text', text: '{}'}],
  structuredContent: {matches: [
    {problem_id: 'p-1', title: 'Exports time out on large accounts', band: 'strong', schema_version: 1},
    {problem_id: 'p-7', title: 'Nightly jobs overrun on large accounts', band: 'possible', schema_version: 1},
  ], schema_version: 1},
};
export const SIMILAR_QUERY = 'exports are slow';

export const LIGHT = {
  theme: 'light', locale: 'en-GB', timeZone: 'UTC', platform: 'desktop',
  styles: {variables: {
    '--color-background-primary': '#ffffff', '--color-text-primary': '#1f1f1f',
    '--color-text-secondary': '#595959', '--color-border-primary': '#d9d9d9',
    '--color-ring-primary': '#2f6feb', '--font-sans': '"Trebuchet MS", system-ui, sans-serif',
  }},
};
export const DARK_COLOURS = {styles: {variables: {
  '--color-background-primary': '#1a1a1a', '--color-text-primary': '#f2f2f2',
  '--color-text-secondary': '#b8b8b8', '--color-border-primary': '#3d3d3d', '--color-ring-primary': '#7aa7ff',
}}};

export async function bundleMockHost() {
  const mockHost = (await build({
    entryPoints: [join(here, 'mock-host.mjs')], bundle: true, format: 'iife', write: false, logLevel: 'silent',
  })).outputFiles[0].text;
  assert.ok(!/<\/script/i.test(mockHost), 'mock host bundle cannot be inlined');
  return mockHost;
}

// A host page that loads `panel` (the built HTML) through the mock host. `config` overrides the
// defaults: the first page of the captured list, light theme, the fixed read time. `head` and
// `before` let the dev server add its own styles and toolbar.
export function hostPage({name, panel, mockHost, config = {}, head = '', before = ''}) {
  const json = JSON.stringify({panel, now: READ_AT, hostContext: LIGHT, input: {offset: 0, limit: 20},
    initial: result('list-opportunities'), ...config,
    responses: {...CAPTURED, [key('find_similar_problems', {text: SIMILAR_QUERY, limit: 5})]: SIMILAR, ...config.responses}})
    .replace(/</g, '\\u003c');
  return `<!doctype html><html><head><meta charset="utf-8"><title>Mock host: ${name}</title>
<style>body{margin:0;background:#8a8a8a;padding:12px}#frame iframe{border:0;width:100%;display:block;min-height:80px}</style>${head}
</head><body>${before}<div id="frame"></div><script>window.__MOCK__=${json}</script><script>${mockHost}</script></body></html>`;
}
