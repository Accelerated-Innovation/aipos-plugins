"""Render a supplied fixture or captured graph snapshot as portable offline HTML."""
from pathlib import Path
import argparse, hashlib, json, sys
ASSETS=Path(__file__).resolve().parent/'assets'
CONTRACT='demo-portfolio.v0.2'
def normalize(value):
    # Match JSON.stringify for the integral measurements returned by the API.
    if isinstance(value,float) and value.is_integer():return int(value)
    if isinstance(value,list):return [normalize(v) for v in value]
    if isinstance(value,dict):return {k:normalize(v) for k,v in value.items()}
    return value
def canonical(value):return json.dumps(normalize(value),sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)
def sha(text):return 'sha256:'+hashlib.sha256(text.encode()).hexdigest()
def snapshot_digest(bundle):return sha(canonical({k:v for k,v in bundle.items() if k!='snapshot_digest'}))
def validate(bundle):
    if bundle.get('response',{}).get('error'):raise ValueError(bundle['response']['error']['code'])
    mode=bundle.get('source_mode')
    if mode not in ('fixture','connected'):raise ValueError('Supply a labeled fixture or captured graph snapshot.')
    if mode=='connected':
        from datetime import datetime
        source=bundle.get('source',{})
        if source.get('transport') not in ('rest','mcp'):raise ValueError('Missing connected read provenance.')
        if datetime.fromisoformat(source['captured_at'].replace('Z','+00:00')).tzinfo is None:raise ValueError('Capture time needs a timezone.')
        if snapshot_digest(bundle)!=bundle.get('snapshot_digest'):raise ValueError('Captured snapshot digest mismatch.')
    responses=bundle.get('responses',{})
    if not all(key in responses for key in ['summary','list','details']):raise ValueError('A complete summary, catalog and details are required.')
    summary=responses['summary'];listing=responses['list'];details=responses['details'];meta=summary['meta']
    if meta['contract_version']!=CONTRACT or meta['synthetic'] is not True:raise ValueError('Unsupported contract or non-synthetic snapshot.')
    if any(r['meta']!=meta for r in [listing,*details.values()]):raise ValueError('Mixed snapshot revisions.')
    if listing['offset']!=0 or len(listing['items'])!=listing['total'] or not bundle['coverage']['catalog_complete']:raise ValueError('Partial catalog: supply all pages.')
    if any(v is not None for v in listing['filters'].values()):raise ValueError('Supply the unfiltered catalog.')
    rows=listing['items'];ids=[r['case_id'] for r in rows]
    if len(set(ids))!=len(ids) or ids!=sorted(ids) or set(details)!=set(ids):raise ValueError('Missing, duplicate or unordered cases.')
    if summary['total_cases']!=len(ids):raise ValueError('Summary count disagrees.')
    for r in rows:
        d=details[r['case_id']]
        if d['case']!=r:raise ValueError('Detail and list disagree.')
        for ref in d['resources']:
            body=bundle.get('resource_bodies',{}).get(ref['reference'])
            if body is None and mode=='connected':continue
            if not isinstance(body,str) or sha(body)!=ref['digest']:raise ValueError('Resource digest mismatch.')
    payloads=json.loads(json.dumps(responses))
    for response in [payloads['summary'],payloads['list'],*payloads['details'].values()]:response.pop('meta')
    raw={'contract_version':CONTRACT,'payloads':payloads,'resource_bodies':bundle['resource_bodies'],'accounts':bundle['accounts']}
    if mode=='fixture' and sha(canonical(raw))!=meta['dataset_digest']:raise ValueError('Snapshot digest mismatch.')
    return bundle
def render(bundle):
    validate(bundle)
    data=canonical(bundle).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
    template=(ASSETS/'template.html').read_text()
    values={'/*STYLE*/':(ASSETS/'style.css').read_text(),'/*DATA*/':data,'/*SCRIPT*/':(ASSETS/'dashboard.mjs').read_text()}
    for marker,value in values.items():
        if template.count(marker)!=1:raise ValueError(f'Invalid template marker: {marker}')
        template=template.replace(marker,value)
    return template
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('fixture',type=Path);parser.add_argument('-o','--output',type=Path,required=True);args=parser.parse_args()
    try:
        if args.fixture.stat().st_size>5000000:raise ValueError('Snapshot exceeds 5 MB.')
        if args.fixture.resolve()==args.output.resolve():raise ValueError('Output cannot overwrite the input fixture.')
        html=render(json.loads(args.fixture.read_text()))
        args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(html)
    except (ValueError,KeyError,TypeError,OSError) as exc:print(f'Cannot render snapshot: {exc}',file=sys.stderr);return 1
    print(str(args.output.resolve()));return 0
if __name__=='__main__':raise SystemExit(main())
