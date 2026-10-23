// Builds the opportunities panel into one self-contained HTML file: template.html with style.css
// and the bundled app (app.mjs + bridge.mjs + model.mjs + the MCP Apps SDK) inlined. The engine
// serves exactly this file, so nothing may load from anywhere else.
//
//   node build.mjs            writes dist/opportunities.html and prints its size and SHA-256
//   node build.mjs --check    fails if the committed dist/ is not what this source builds
//   node build.mjs --out F    writes somewhere else (the page check uses this)
//
// Licence notices for every bundled package travel inside the file, at the top of the script,
// because the engine serves no file beside it.
import {build, transform} from 'esbuild';
import {createHash} from 'node:crypto';
import {existsSync, mkdirSync, readdirSync, readFileSync, writeFileSync} from 'node:fs';
import {dirname, join, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const DIST = resolve(here, 'dist/opportunities.html');
const pkg = JSON.parse(readFileSync(join(here, 'package.json'), 'utf8'));

// `@modelcontextprotocol/ext-apps/app-with-deps` is the SDK's own prebuilt bundle, so esbuild sees
// one package where several libraries ship. These are the ones inside it, reviewed for the pinned
// SDK version; each with a fingerprint must still be found in the built script. An SDK bump fails
// the build until this list is reviewed again. Licence texts come from node_modules where the
// package is installed, and from licenses/ where it is not.
const SDK = {name: '@modelcontextprotocol/ext-apps', reviewed: '2.0.3'};
const SDK_CONTENTS = [
  {name: '@modelcontextprotocol/core', license: 'node_modules/@modelcontextprotocol/core/LICENSE', spdx: 'Apache-2.0 (MIT for earlier contributions)'},
  {name: '@modelcontextprotocol/client', license: 'node_modules/@modelcontextprotocol/client/LICENSE', spdx: 'Apache-2.0 (MIT for earlier contributions)'},
  {name: 'zod', license: 'node_modules/zod/LICENSE', spdx: 'MIT', fingerprint: /ZodError/},
  {name: '@cfworker/json-schema', license: 'licenses/cfworker-json-schema.txt', spdx: 'MIT', fingerprint: /github\.com\/cfworker/},
  {name: 'content-type', license: 'licenses/content-type.txt', spdx: 'MIT', fingerprint: /content-type header is missing from object/},
];

export async function buildPanel() {
  const options = {
    entryPoints: [join(here, 'app.mjs')],
    bundle: true,
    minify: true,
    format: 'iife',
    target: ['es2022'],
    legalComments: 'none',
    charset: 'utf8',
    define: {__PANEL_VERSION__: JSON.stringify(pkg.version)},
    write: false,
    metafile: true,
    logLevel: 'silent',
  };
  const result = await build(options);
  const script = result.outputFiles[0].text;

  const packages = new Map();
  for (const input of Object.keys(result.metafile.inputs)) {
    const m = input.match(/node_modules\/((?:@[^/]+\/)?[^/]+)\//);
    if (!m || packages.has(m[1])) continue;
    const dir = join(here, 'node_modules', m[1]);
    const meta = JSON.parse(readFileSync(join(dir, 'package.json'), 'utf8'));
    const file = readdirSync(dir).find(f => /^licen[cs]e(\.|$)/i.test(f));
    const text = file ? readFileSync(join(dir, file), 'utf8').trim() : null;
    if (!text) throw new Error(`${m[1]} ships no licence file; add its notice by hand before bundling it`);
    packages.set(m[1], {name: `${meta.name}@${meta.version}`, license: meta.license, text});
  }
  const sdk = packages.get(SDK.name);
  if (sdk) {
    if (sdk.name !== `${SDK.name}@${SDK.reviewed}`) {
      throw new Error(`${sdk.name} is not the reviewed ${SDK.reviewed}; review SDK_CONTENTS in build.mjs and update it.`);
    }
    for (const lib of SDK_CONTENTS) {
      if (lib.fingerprint && !lib.fingerprint.test(script)) throw new Error(`${lib.name} is no longer in the SDK bundle; review SDK_CONTENTS.`);
      packages.set(lib.name, {name: `${lib.name} (inside ${sdk.name})`, license: lib.spdx,
        text: readFileSync(join(here, lib.license), 'utf8').trim()});
    }
  }
  const sorted = [...packages.values()].sort((a, b) => a.name.localeCompare(b.name));
  const texts = [...new Set(sorted.map(p => p.text))];
  const notices = [
    `/*! aipos opportunities panel ${pkg.version}. Bundles third-party code under these licences:`,
    ...sorted.map(p => `  ${p.name}: ${p.license}, text ${texts.indexOf(p.text) + 1} below`),
    ...texts.flatMap((text, i) => ['', `--- Licence text ${i + 1} ---`, '', text]),
    '*/',
  ].join('\n').replace(/\*\/(?!$)/g, '* /');

  const css = (await transform(readFileSync(join(here, 'style.css'), 'utf8'), {loader: 'css', minify: true})).code.trim();
  const body = `${notices}\n${script}`;
  if (/<\/script/i.test(body) || /<!--/.test(body)) throw new Error('The bundled script contains an HTML terminator; it cannot be inlined.');
  if (/<\/style/i.test(css)) throw new Error('The stylesheet contains </style; it cannot be inlined.');

  const template = readFileSync(join(here, 'template.html'), 'utf8');
  if (!template.includes('/*__STYLE__*/') || !template.includes('/*__SCRIPT__*/')) throw new Error('template.html lost a placeholder.');
  const html = template.replace('/*__STYLE__*/', () => css).replace('/*__SCRIPT__*/', () => body);
  return {html, packages: sorted.map(p => p.name)};
}

const sha256 = text => createHash('sha256').update(text, 'utf8').digest('hex');

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const args = process.argv.slice(2);
  const {html, packages} = await buildPanel();
  const bytes = Buffer.byteLength(html, 'utf8');
  if (args.includes('--check')) {
    if (!existsSync(DIST) || readFileSync(DIST, 'utf8') !== html) {
      console.error('dist/opportunities.html is stale: run `node build.mjs` in panels/opportunities and commit the result.');
      process.exit(1);
    }
    console.log(`dist/opportunities.html matches source (${bytes} bytes, sha256 ${sha256(html)}).`);
  } else {
    const at = args.indexOf('--out');
    const out = at >= 0 ? resolve(args[at + 1]) : DIST;
    mkdirSync(dirname(out), {recursive: true});
    writeFileSync(out, html);
    console.log(`${out}\n  ${bytes} bytes  sha256 ${sha256(html)}\n  bundled: ${packages.join(', ')}`);
  }
}
