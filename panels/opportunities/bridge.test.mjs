import test from 'node:test';
import assert from 'node:assert/strict';
import {readdirSync, readFileSync} from 'node:fs';
import {connectBridge, normalizeResult} from './bridge.mjs';

const dir = new URL('./fixtures/mcp/', import.meta.url);
const capture = stem => JSON.parse(readFileSync(new URL(`${stem}.json`, dir), 'utf8'));
const sample = name => JSON.parse(readFileSync(new URL(`./fixtures/engine-samples/${name}.json`, import.meta.url), 'utf8'));

test('every captured success normalizes to its structuredContent and the server name', () => {
  for (const file of readdirSync(dir).filter(f => !f.startsWith('error-'))) {
    const {result} = capture(file.replace(/\.json$/, ''));
    assert.deepEqual(normalizeResult(result), {ok: true, data: result.structuredContent, server: 'opportunity-engine'}, file);
  }
});

test('captured engine errors keep the engine code and message', () => {
  const cases = {
    'error-problem-not-found': ['PROBLEM_NOT_FOUND', "Problem 'missing' not found"],
    'error-insufficient-scope': ['INSUFFICIENT_SCOPE', "Role 'pm' required"],
    'error-invalid-token': ['INVALID_TOKEN', 'Could not validate credentials'],
  };
  for (const [stem, [code, message]] of Object.entries(cases)) {
    const {result} = capture(stem);
    assert.equal(result.isError, true);
    assert.equal(result.structuredContent, undefined, 'an engine error carries no structured content');
    assert.deepEqual(normalizeResult(result), {ok: false, code, message, server: 'opportunity-engine'}, stem);
  }
});

test('the MCP data is the REST sample\'s data field, never the {data, error} envelope', () => {
  const pairs = [['list-opportunities', 'opportunities'], ['get-problem', 'problem-detail'], ['list-evidence', 'problem-evidence']];
  for (const [stem, name] of pairs) {
    const data = normalizeResult(capture(stem).result).data;
    const rest = sample(name);
    assert.deepEqual(Object.keys(rest), ['data', 'error']);
    assert.deepEqual(Object.keys(data), Object.keys(rest.data), `${stem} has the fields of ${name}.data`);
    assert.equal('data' in data || 'error' in data, false);
  }
});

test('a result without structured content falls back to its JSON text, else is malformed', () => {
  const {result} = capture('list-opportunities');
  const textOnly = {content: result.content};
  assert.deepEqual(normalizeResult(textOnly), {ok: true, data: result.structuredContent, server: null});
  assert.equal(normalizeResult({content: [{type: 'text', text: 'not json'}]}).code, 'MALFORMED_RESULT');
  assert.equal(normalizeResult({content: [{type: 'text', text: '[1,2]'}]}).code, 'MALFORMED_RESULT');
  assert.equal(normalizeResult(undefined).code, 'MALFORMED_RESULT');
  assert.deepEqual(normalizeResult({isError: true, content: [{type: 'text', text: 'boom'}]}),
    {ok: false, code: 'TOOL_ERROR', message: 'boom', server: null});
});

// A stand-in for the SDK's App that records what the bridge does with it.
function fakeApp({connectFails = false, respond = () => capture('list-opportunities').result} = {}) {
  const log = [];
  class FakeApp {
    constructor(info, caps, options) { log.push(['new', info, caps, options]); }
    set ontoolinput(f) { log.push(['handler', 'toolinput']); this._input = f; }
    set ontoolresult(f) { log.push(['handler', 'toolresult']); this._result = f; }
    set ontoolcancelled(f) { log.push(['handler', 'toolcancelled']); this._cancelled = f; }
    set onhostcontextchanged(f) { log.push(['handler', 'hostcontextchanged']); this._context = f; }
    set onteardown(f) { log.push(['handler', 'teardown']); this._teardown = f; }
    async connect(transport) {
      log.push(['connect', transport]);
      FakeApp.instance = this;
      if (connectFails) throw new Error('no host');
    }
    async callServerTool(params) { log.push(['call', params]); return respond(params); }
    async openLink(params) { log.push(['openLink', params]); return params.url.includes('refuse') ? {isError: true} : {}; }
    getHostContext() { return {theme: 'dark'}; }
    getHostVersion() { return {name: 'Mock host', version: '1'}; }
  }
  return {FakeApp, log};
}

test('handlers are registered before connecting, so the initial result is never missed', async () => {
  const {FakeApp, log} = fakeApp();
  await connectBridge({}, {AppClass: FakeApp, transport: 'T', version: '0.1.0'});
  const connectAt = log.findIndex(e => e[0] === 'connect');
  const handlers = log.filter((e, i) => e[0] === 'handler' && i < connectAt).map(e => e[1]);
  assert.deepEqual(handlers, ['toolinput', 'toolresult', 'toolcancelled', 'hostcontextchanged', 'teardown']);
  assert.deepEqual(log[0], ['new', {name: 'aipos-opportunities-panel', version: '0.1.0'}, {}, {autoResize: true}]);
  assert.deepEqual(log[connectAt], ['connect', 'T']);
});

test('notifications reach the panel normalized', async () => {
  const {FakeApp} = fakeApp();
  const seen = [];
  await connectBridge({
    onToolInput: args => seen.push(['input', args]),
    onToolResult: r => seen.push(['result', r.ok, r.code ?? r.data.total]),
    onToolCancelled: reason => seen.push(['cancelled', reason]),
    onHostContext: update => seen.push(['context', update]),
  }, {AppClass: FakeApp, transport: 'T'});
  const app = FakeApp.instance;
  app._input({arguments: {offset: 0, limit: 20}});
  app._result(capture('list-opportunities').result);
  app._result(capture('error-insufficient-scope').result);
  app._cancelled({reason: 'user'});
  app._context({theme: 'light'});
  assert.deepEqual(seen, [['input', {offset: 0, limit: 20}], ['result', true, 2], ['result', false, 'INSUFFICIENT_SCOPE'],
    ['cancelled', 'user'], ['context', {theme: 'light'}]]);
  assert.deepEqual(await app._teardown(), {});
});

test('the panel gets named read operations only, with the engine argument names', async () => {
  const {FakeApp, log} = fakeApp({respond: ({name}) => capture(name === 'get_problem' ? 'get-problem' : name === 'list_evidence' ? 'list-evidence' : 'list-opportunities-second-of-two').result});
  const bridge = await connectBridge({}, {AppClass: FakeApp, transport: 'T'});
  assert.deepEqual(Object.keys(bridge).sort(), ['getProblem', 'hostContext', 'hostVersion', 'listEvidence', 'listOpportunities', 'openLink']);
  assert.equal(Object.isFrozen(bridge), true);
  assert.equal((await bridge.listOpportunities({offset: 1, limit: 1})).data.offset, 1);
  assert.equal((await bridge.getProblem('p-1')).data.problem_id, 'p-1');
  assert.equal((await bridge.listEvidence('p-1')).data.total, 3);
  assert.deepEqual(log.filter(e => e[0] === 'call').map(e => e[1]), [
    {name: 'list_opportunities', arguments: {offset: 1, limit: 1}},
    {name: 'get_problem', arguments: {problem_id: 'p-1'}},
    {name: 'list_evidence', arguments: {problem_id: 'p-1'}},
  ]);
  assert.deepEqual(bridge.hostContext(), {theme: 'dark'});
  assert.deepEqual(bridge.hostVersion(), {name: 'Mock host', version: '1'});
});

test('a transport failure is a HOST_ERROR, distinct from a tool error', async () => {
  const {FakeApp} = fakeApp({respond: () => { throw new Error('request timed out'); }});
  const bridge = await connectBridge({}, {AppClass: FakeApp, transport: 'T'});
  assert.deepEqual(await bridge.getProblem('p-1'), {ok: false, code: 'HOST_ERROR', message: 'request timed out', server: null});
});

test('openLink reports whether the host opened the link', async () => {
  const {FakeApp, log} = fakeApp();
  const bridge = await connectBridge({}, {AppClass: FakeApp, transport: 'T'});
  assert.equal(await bridge.openLink('https://aha.test/OPP-12'), true);
  assert.equal(await bridge.openLink('https://refuse.test/'), false);
  assert.deepEqual(log.filter(e => e[0] === 'openLink').map(e => e[1].url), ['https://aha.test/OPP-12', 'https://refuse.test/']);
});

test('a failed handshake rejects, so the panel can say it is not connected', async () => {
  const {FakeApp} = fakeApp({connectFails: true});
  await assert.rejects(connectBridge({}, {AppClass: FakeApp, transport: 'T'}), /no host/);
});
