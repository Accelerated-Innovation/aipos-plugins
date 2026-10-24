// A mock MCP Apps host for local checks. Never shipped; check-page.mjs bundles it into a page.
//
// It speaks the real protocol through the SDK's host-side AppBridge, loads the built panel into
// a sandboxed iframe (scripts only, opaque origin) under the MCP Apps default CSP, answers the
// panel's tool calls from the captured engine results, and records what the panel asks of it.
// It replaces neither the Claude Desktop check nor the release check in a real host.
import {AppBridge, PostMessageTransport} from '@modelcontextprotocol/ext-apps/app-bridge';

// MCP Apps 2026-01-26 default policy for a resource that declares no CSP origins.
const DEFAULT_CSP = "default-src 'none'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; "
  + "img-src 'self' data:; media-src 'self' data:; connect-src 'none'";

const config = globalThis.__MOCK__;
const record = globalThis.__HOST__ = {calls: [], links: [], messages: [], sizes: [], initialized: false};

// A fixture is a captured CallToolResult; `delay` holds a response back for loading-state checks.
function respond(params) {
  const key = `${params.name} ${JSON.stringify(params.arguments ?? {})}`;
  record.calls.push(key);
  const answer = config.responses[key];
  if (!answer) {
    return {isError: true, content: [{type: 'text', text: `Error executing tool ${params.name}: VALIDATION_ERROR: mock host has no fixture for ${key}`}]};
  }
  return new Promise(resolve => setTimeout(() => resolve(answer), config.delay ?? 0));
}

async function start() {
  const iframe = document.createElement('iframe');
  iframe.setAttribute('sandbox', 'allow-scripts');
  iframe.title = 'Opportunities panel';
  document.getElementById('frame').append(iframe);

  // The bridge listens before the panel loads, as a host must: the panel starts the handshake
  // as soon as its script runs. The iframe's WindowProxy survives the srcdoc navigation.
  const bridge = new AppBridge(null, {name: 'aipos mock host', version: '0.1.0'},
    {openLinks: {}, serverTools: {}, logging: {}}, {hostContext: config.hostContext});
  bridge.oncalltool = async params => respond(params);
  bridge.onopenlink = async ({url}) => {
    record.links.push(url);
    return url.includes('refuse') ? {isError: true} : {};
  };
  // ui/message: the panel hands a user turn to the conversation; the mock records it.
  bridge.onmessage = async params => {
    record.messages.push(params);
    return params.content?.[0]?.text?.includes('refuse') ? {isError: true} : {};
  };
  bridge.onsizechange = ({height}) => {
    record.sizes.push(height);
    if (height) iframe.style.height = `${height}px`;
  };
  bridge.onloggingmessage = () => {};
  bridge.oninitialized = async () => {
    record.initialized = true;
    await bridge.sendToolInput({arguments: config.input});
    if (config.cancel) await bridge.sendToolCancelled({reason: 'user'});
    else await bridge.sendToolResult(config.initial);
  };
  record.setContext = update => bridge.sendHostContextChange(update);
  await bridge.connect(new PostMessageTransport(iframe.contentWindow, iframe.contentWindow));

  const head = `<meta http-equiv="Content-Security-Policy" content="${DEFAULT_CSP}">`
    + (config.now ? `<script>globalThis.__PANEL_NOW__=${JSON.stringify(config.now)}</script>` : '');
  iframe.srcdoc = config.panel.replace('<head>', () => `<head>${head}`);
}

start().catch(error => { record.error = String(error); });
