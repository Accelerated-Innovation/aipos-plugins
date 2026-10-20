"""Client for the existing engine MCP server. No server, REST fallback or graph writes."""
import asyncio

from capture_portfolio import ChangedSnapshot, capture_consistent
from render_dashboard import snapshot_digest, validate

TOOLS = ('get_demo_portfolio', 'list_demo_opportunities', 'get_demo_opportunity')


def unpack(result):
    if result.is_error:
        data = result.structured_content or {}
        error = data.get('error') or data
        if error.get('code') == 'DEMO_REVISION_CHANGED':
            raise ChangedSnapshot('Graph changed during capture.')
        raise ValueError('MCP tool returned an error; capture stopped without fallback.')
    if not isinstance(result.structured_content, dict):
        raise ValueError('MCP tool did not return the documented structured result.')
    return result.structured_content


async def discover(session):
    tools, cursor, seen = {}, None, set()
    from mcp.types import PaginatedRequestParams

    while True:
        page = await session.list_tools(params=PaginatedRequestParams(cursor=cursor) if cursor else None)
        for tool in page.tools:
            if tool.name in tools:
                raise ValueError('MCP tool discovery returned duplicate names.')
            tools[tool.name] = tool
        cursor = page.next_cursor
        if not cursor:
            break
        if cursor in seen or len(seen) >= 20:
            raise ValueError('MCP tool discovery did not finish.')
        seen.add(cursor)
    for name in TOOLS:
        tool = tools.get(name)
        if not tool or not tool.annotations or tool.annotations.read_only_hint is not True:
            raise ValueError('The MCP server must advertise all three portfolio tools as read-only.')
    return [tools[name] for name in TOOLS]


async def capture_mcp(base, token, dataset, resources=None):
    # Optional capture dependencies; rendering and explicit REST capture remain stdlib-only.
    import httpx2
    from mcp import ClientSession
    from mcp.client.streamable_http import streamable_http_client

    endpoint = base + '/mcp/'

    async def no_redirect(response):
        if 300 <= response.status_code < 400:
            raise ValueError('MCP endpoint redirected; credentials were not forwarded.')

    try:
        async with httpx2.AsyncClient(
            headers={'Authorization': 'Bearer ' + token}, timeout=30,
            follow_redirects=False, trust_env=False, event_hooks={'response': [no_redirect]},
        ) as client:
            async with streamable_http_client(endpoint, http_client=client) as streams:
                async with ClientSession(streams[0], streams[1]) as session:
                    initialized = await session.initialize()
                    selected = await discover(session)
                    loop = asyncio.get_running_loop()

                    async def call(name, arguments):
                        if name not in TOOLS:
                            raise ValueError('Unsupported portfolio operation.')
                        return unpack(await session.call_tool(name, arguments, read_timeout_seconds=30))

                    def blocking_call(name, arguments):
                        return asyncio.run_coroutine_threadsafe(call(name, arguments), loop).result(timeout=35)

                    bundle = await asyncio.to_thread(
                        capture_consistent, blocking_call, base, dataset, resources, transport='mcp',
                    )
                    bundle['source'].update(
                        mcp_url=endpoint,
                        server_name=initialized.server_info.name,
                        server_version=initialized.server_info.version,
                        protocol_version=initialized.protocol_version,
                        discovered_read_tools=[tool.name for tool in selected],
                    )
                    bundle['snapshot_digest'] = snapshot_digest(bundle)
                    validate(bundle)
                    return bundle
    except Exception:
        # SDK exception groups can contain headers or arbitrary server text. Never print them.
        raise ValueError('MCP capture failed: check the local server, authentication, read tools and snapshot consistency. No REST fallback was used.') from None
