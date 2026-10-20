"""Capture the local Harborlight read API, without graph writes or embedded credentials."""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

from render_dashboard import canonical, sha, snapshot_digest, validate


class ChangedSnapshot(ValueError):
    pass


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('The local read API redirected; capture stopped.')


def local_base(value):
    url = urlsplit(value)
    if (url.scheme != 'http' or url.hostname not in ('127.0.0.1', 'localhost', '::1')
            or not url.port or url.username or url.password or url.query or url.fragment
            or url.path not in ('', '/')):
        raise ValueError('Use an explicit loopback HTTP API base with a port and no credentials.')
    return value.rstrip('/')


def reader(base, token):
    opener = build_opener(ProxyHandler({}), NoRedirect())

    def get(path):
        request = Request(base + path, headers={'Authorization': 'Bearer ' + token})
        try:
            with opener.open(request, timeout=20) as response:
                raw = response.read(5_000_001)
        except HTTPError as exc:
            if exc.code == 409:
                try:
                    error = json.loads(exc.read(100_000)).get('error') or {}
                except (ValueError, AttributeError):
                    error = {}
                if error.get('code') == 'DEMO_REVISION_CHANGED':
                    raise ChangedSnapshot('Graph changed during capture.') from None
            raise ValueError(f'Portfolio API returned HTTP {exc.code}; capture stopped.') from None
        except (URLError, TimeoutError, OSError):
            raise ValueError('Portfolio API is unavailable; no example data was substituted.') from None
        if len(raw) > 5_000_000:
            raise ValueError('Portfolio response exceeds 5 MB.')
        envelope = json.loads(raw)
        if envelope.get('error'):
            if envelope['error'].get('code') == 'DEMO_REVISION_CHANGED':
                raise ChangedSnapshot('Graph changed during capture.')
            raise ValueError('Portfolio API reported an error; capture stopped.')
        if not isinstance(envelope.get('data'), dict):
            raise ValueError('Portfolio API did not return a successful data envelope.')
        return envelope['data']

    return get


def capture(get, base, dataset, resources=None, *, transport='rest'):
    """Exhaust pagination and require identical metadata across the entire capture."""
    route = '/v1/demo/portfolios/' + quote(dataset, safe='')
    def operation(name, **args):
        arguments = {'dataset_id': dataset, **args}
        if transport == 'mcp':
            return get(name, arguments)
        if name == 'get_demo_portfolio':
            return get(route)
        if name == 'list_demo_opportunities':
            return get(route + '/opportunities?' + urlencode(args))
        return get(route + '/opportunities/' + quote(args['case_id'], safe=''))

    summary = operation('get_demo_portfolio')
    meta = summary['meta']
    if meta['dataset_id'] != dataset:
        raise ValueError('The API returned a different dataset.')
    requests = 1

    def read(name, **args):
        nonlocal requests
        data = operation(name, **args)
        requests += 1
        if data['meta'] != meta:
            raise ChangedSnapshot('Graph changed during capture.')
        return data

    items, offset, first = [], 0, None
    while True:
        page = read('list_demo_opportunities', offset=offset, limit=100)
        if first is None:
            first = page
        if (page['offset'] != offset or page['total'] != summary['total_cases']
                or page['filters'] != {'product_id': None, 'phase': None, 'disposition': None}
                or not 1 <= page['limit'] <= 100 or len(page['items']) > page['limit']
                or page['total'] > 5000):
            raise ValueError('Invalid or inconsistent pagination.')
        items.extend(page['items'])
        offset += len(page['items'])
        if offset == page['total']:
            break
        if not page['items'] or offset > page['total']:
            raise ValueError('Incomplete pagination.')
    ids = [row['case_id'] for row in items]
    if len(set(ids)) != len(ids) or ids != sorted(ids):
        raise ValueError('Duplicate or unordered cases across pages.')
    details = {case: read('get_demo_opportunity', case_id=case) for case in ids}
    # Close the read interval: discard even a final-detail/summary revision mismatch.
    if read('get_demo_portfolio') != summary:
        raise ChangedSnapshot('Graph changed during capture.')
    bodies = {}
    for detail in details.values():
        for ref in detail['resources']:
            body = (resources or {}).get(ref['reference'])
            if body is not None:
                if not isinstance(body, str) or sha(body) != ref['digest']:
                    raise ValueError('A local narrative does not match its graph resource digest.')
                bodies[ref['reference']] = body
    bundle = {
        'source_mode': 'connected',
        'source': {
            'transport': transport, 'api_base': base,
            'captured_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            'request_count': requests,
            'operations': ['get_demo_portfolio', 'list_demo_opportunities', 'get_demo_opportunity'],
            'resource_origin': 'Explicit local resource file; bodies verified against graph references.' if resources else 'Narrative bodies not supplied.',
        },
        'coverage': {'summary': True, 'catalog_complete': True, 'detail_case_ids': ids},
        'responses': {'summary': summary, 'list': {**first, 'items': items, 'offset': 0}, 'details': details},
        'resource_bodies': bodies,
        # The read contract exposes account IDs, not account display names.
        'accounts': [],
    }
    bundle['snapshot_digest'] = snapshot_digest(bundle)
    validate(bundle)
    return bundle


def capture_consistent(get, base, dataset, resources=None, *, transport='rest'):
    for attempt in range(2):
        try:
            return capture(get, base, dataset, resources, transport=transport)
        except ChangedSnapshot:
            if attempt:
                raise ValueError('No consistent graph snapshot after two complete attempts.') from None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--api-base', required=True)
    parser.add_argument('--transport', choices=['mcp', 'rest'], default='mcp')
    parser.add_argument('--dataset', default='harborlight-insurance-v1')
    parser.add_argument('--token-env', default='ENGINE_DEMO_TOKEN')
    parser.add_argument('--resources', type=Path, help='Explicit local JSON map of resource references to bodies.')
    parser.add_argument('-o', '--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        base = local_base(args.api_base)
        token = os.environ.get(args.token_env)
        if not token:
            raise ValueError('Supply the local API bearer token in the requested environment variable.')
        if args.resources and args.output.resolve() == args.resources.resolve():
            raise ValueError('Output cannot overwrite the resource input.')
        resources = json.loads(args.resources.read_text()) if args.resources else None
        if resources is not None and not isinstance(resources, dict):
            raise ValueError('The resource file must be an object.')
        if args.transport == 'mcp':
            import asyncio
            from portfolio_mcp import capture_mcp

            bundle = asyncio.run(capture_mcp(base, token, args.dataset, resources))
        else:
            bundle = capture_consistent(reader(base, token), base, args.dataset, resources)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(canonical(bundle))
    except ImportError:
        print('MCP capture requires scripts/requirements.txt. Install it in the capture interpreter; no REST fallback was used.', file=sys.stderr)
        return 1
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(f'Cannot capture portfolio: {exc}', file=sys.stderr)
        return 1
    print(json.dumps({'output': str(args.output.resolve()), 'cases': bundle['responses']['summary']['total_cases'],
                      'meta': bundle['responses']['summary']['meta'], 'requests': bundle['source']['request_count']}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
