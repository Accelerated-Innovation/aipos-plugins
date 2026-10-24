// The panel's only door to the host: a narrow adapter around the official MCP Apps SDK.
//
// The SDK instance stays private here. The rest of the panel gets named operations (the four
// read tools the engine allows this panel, opening a record link, and handing one message back to
// the conversation) and normalized results, never a general tool-call method. The SDK owns the protocol: the ui/initialize
// handshake, tool input and result notifications, host context, size reporting and transport.
import {App, PostMessageTransport} from '@modelcontextprotocol/ext-apps/app-with-deps';

const SERVER_INFO = 'io.modelcontextprotocol/serverInfo';
// The engine raises EngineToolError(code, message), which the MCP SDK reports as
// "Error executing tool <name>: <CODE>: <message>" with isError set and no structuredContent.
const ENGINE_ERROR = /([A-Z][A-Z0-9_]*[A-Z0-9]): ([\s\S]*)$/;

// A CallToolResult as {ok, data, server} or {ok: false, code, message, server}. Tool errors keep
// the engine's code; a result without structured content falls back to its JSON text block.
export function normalizeResult(result) {
  if (!result || typeof result !== 'object') {
    return {ok: false, code: 'MALFORMED_RESULT', message: 'The host returned no tool result.', server: null};
  }
  const server = result._meta?.[SERVER_INFO]?.name ?? null;
  const text = (Array.isArray(result.content) ? result.content : [])
    .filter(block => block?.type === 'text' && typeof block.text === 'string')
    .map(block => block.text).join('\n');
  if (result.isError) {
    const match = text.match(ENGINE_ERROR);
    return match
      ? {ok: false, code: match[1], message: match[2].trim(), server}
      : {ok: false, code: 'TOOL_ERROR', message: text || 'The tool reported an error.', server};
  }
  const structured = result.structuredContent;
  if (structured && typeof structured === 'object' && !Array.isArray(structured)) {
    return {ok: true, data: structured, server};
  }
  try {
    const data = JSON.parse(text);
    if (data && typeof data === 'object' && !Array.isArray(data)) return {ok: true, data, server};
  } catch { /* reported below */ }
  return {ok: false, code: 'MALFORMED_RESULT', message: 'The tool result carried no structured data.', server};
}

const hostFailure = error => ({
  ok: false, code: 'HOST_ERROR', message: error?.message || String(error), server: null,
});

// Connects to the host and returns the panel's operations. Handlers are registered before
// connecting, as the SDK requires, so the initial tool input and result are never missed.
// `App` and `transport` are injectable for tests; production uses the SDK and window.parent.
export async function connectBridge(handlers = {}, {AppClass = App, transport, version = '0.0.0'} = {}) {
  const app = new AppClass({name: 'aipos-opportunities-panel', version}, {}, {autoResize: true});
  app.ontoolinput = params => handlers.onToolInput?.(params?.arguments ?? {});
  app.ontoolresult = result => handlers.onToolResult?.(normalizeResult(result));
  app.ontoolcancelled = params => handlers.onToolCancelled?.(params?.reason ?? '');
  app.onhostcontextchanged = update => handlers.onHostContext?.(update ?? {});
  app.onteardown = async () => ({});

  await app.connect(transport ?? new PostMessageTransport(window.parent, window.parent));

  const call = async (name, args) => {
    try {
      return normalizeResult(await app.callServerTool({name, arguments: args}));
    } catch (error) {
      return hostFailure(error);
    }
  };
  return Object.freeze({
    hostContext: () => app.getHostContext() ?? {},
    hostVersion: () => app.getHostVersion() ?? null,
    listOpportunities: ({offset, limit}) => call('list_opportunities', {offset, limit}),
    getProblem: problemId => call('get_problem', {problem_id: problemId}),
    listEvidence: problemId => call('list_evidence', {problem_id: problemId}),
    // Semantic search: the engine's dedup read, ordinal bands only, at most five matches.
    findSimilar: text => call('find_similar_problems', {text, limit: 5}),
    openLink: async url => {
      try {
        const result = await app.openLink({url});
        return !result?.isError;
      } catch {
        return false;
      }
    },
    // The panel's one write-shaped operation: a plain-text user message into the conversation
    // (ui/message). The host shows it as the user's own turn and may ask them to confirm; the
    // panel never calls another server's tools, so anything that acts on a tracker happens in
    // the conversation with whatever the user has connected.
    sendMessage: async text => {
      try {
        const result = await app.sendMessage({role: 'user', content: [{type: 'text', text}]});
        return !result?.isError;
      } catch {
        return false;
      }
    },
  });
}
