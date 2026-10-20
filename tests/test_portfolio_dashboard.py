"""The offline dashboard preserves data integrity and treats fixture text as data."""
import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'plugins/aipos/skills/aipos-portfolio-dashboard'
SPEC=importlib.util.spec_from_file_location('portfolio_renderer',SKILL/'scripts/render_dashboard.py')
renderer=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(renderer)

@pytest.fixture
def bundle():return json.loads((SKILL/'evals/files/portfolio.json').read_text())

def test_renderer_embeds_portable_data_and_no_remote_assets(bundle):
    page=renderer.render(bundle)
    assert '/*DATA*/' not in page
    assert '<script src=' not in page
    assert '<link rel="stylesheet"' not in page
    assert 'https://tracker.invalid' in page  # inert fixture value, never fetched by renderer

def test_resources_cannot_break_out_of_json_script(bundle):
    ref=next(iter(bundle['resource_bodies']))
    bundle['resource_bodies'][ref]='</script><img src=x onerror=alert(1)>'
    for d in bundle['responses']['details'].values():
        for r in d['resources']:
            if r['reference']==ref:r['digest']=renderer.sha(bundle['resource_bodies'][ref])
    payloads=copy.deepcopy(bundle['responses'])
    for r in [payloads['summary'],payloads['list'],*payloads['details'].values()]:r.pop('meta')
    digest=renderer.sha(renderer.canonical(dict(contract_version=renderer.CONTRACT,payloads=payloads,resource_bodies=bundle['resource_bodies'],accounts=bundle['accounts'])))
    for r in [bundle['responses']['summary'],bundle['responses']['list'],*bundle['responses']['details'].values()]:r['meta']['dataset_digest']=digest
    page=renderer.render(bundle)
    assert '<img src=x' not in page
    assert '\\u003c/script\\u003e' in page

@pytest.mark.parametrize('name',['partial-page','mixed-revisions','unavailable'])
def test_unusable_snapshots_are_refused(name):
    with pytest.raises(ValueError):renderer.render(json.loads((SKILL/f'evals/files/{name}.json').read_text()))

def test_changed_resource_does_not_render_as_trusted_fixture(bundle):
    bundle['resource_bodies'][next(iter(bundle['resource_bodies']))]+='changed'
    with pytest.raises(ValueError,match='digest'):renderer.render(bundle)

def test_renderer_runs_from_unrelated_working_directory(tmp_path):
    target=tmp_path/'portfolio.html'
    result=subprocess.run([sys.executable,str(SKILL/'scripts/render_dashboard.py'),str(SKILL/'evals/files/portfolio.json'),'-o',str(target)],cwd=tmp_path,capture_output=True,text=True)
    assert result.returncode==0,result.stderr
    assert target.stat().st_size>10000

def test_packaged_viewer_matches_maintained_source():
    result=subprocess.run([sys.executable,str(ROOT/'viewers/portfolio/build.py'),'--check'],capture_output=True,text=True)
    assert result.returncode==0,result.stderr

@pytest.fixture
def collector():
    sys.path.insert(0,str(SKILL/'scripts'))
    try:
        spec=importlib.util.spec_from_file_location('portfolio_capture',SKILL/'scripts/capture_portfolio.py')
        module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:sys.path.pop(0)

def fake_graph(bundle, page_size=10):
    from urllib.parse import urlsplit,parse_qs
    responses=copy.deepcopy(bundle['responses'])
    for response in [responses['summary'],responses['list'],*responses['details'].values()]:
        response['meta']['dataset_version']='graph.1'
        response['meta']['dataset_digest']='sha256:'+'a'*64
    paths=[]
    def get(path):
        paths.append(path)
        url=urlsplit(path)
        if url.path.endswith('/opportunities'):
            offset=int(parse_qs(url.query)['offset'][0]);page=copy.deepcopy(responses['list'])
            page.update(offset=offset,limit=page_size,items=page['items'][offset:offset+page_size])
            return page
        if '/opportunities/' in url.path:return copy.deepcopy(responses['details'][url.path.rsplit('/',1)[1]])
        return copy.deepcopy(responses['summary'])
    return get,paths

def test_connected_capture_exhausts_pages_and_preserves_graph_metadata(bundle,collector):
    get,paths=fake_graph(bundle)
    captured=collector.capture_consistent(get,'http://127.0.0.1:18000','harborlight-insurance-v1',bundle['resource_bodies'])
    assert len(paths)==38  # summary + four pages + 32 details + final summary
    assert captured['responses']['summary']['meta']['dataset_digest']=='sha256:'+'a'*64
    assert captured['snapshot_digest']!=captured['responses']['summary']['meta']['dataset_digest']
    assert len(captured['responses']['details'])==32
    assert captured['accounts']==[]  # No account names invented from the fixture.
    assert captured['source_mode']=='connected'
    assert renderer.validate(captured)==captured
    assert '/*DATA*/' not in renderer.render(captured)

def test_connected_capture_without_narrative_bodies_is_valid(bundle,collector):
    get,_=fake_graph(bundle)
    captured=collector.capture_consistent(get,'http://127.0.0.1:18000','harborlight-insurance-v1')
    assert captured['resource_bodies']=={}
    renderer.validate(captured)

def test_capture_discards_mixed_revision_and_restarts_whole_read(bundle,collector):
    get,paths=fake_graph(bundle)
    first=True
    def changing(path):
        nonlocal first
        data=get(path)
        if '/opportunities/' in path and first:
            data['meta']['read_revision']+=1;first=False
        return data
    captured=collector.capture_consistent(changing,'http://127.0.0.1:18000','harborlight-insurance-v1')
    assert sum(p.endswith('/harborlight-insurance-v1') for p in paths)==3
    assert captured['responses']['summary']['meta']==captured['responses']['details']['BI01']['meta']

def test_repeated_snapshot_changes_fail_without_fallback(bundle,collector):
    get,_=fake_graph(bundle)
    def changing(path):
        data=get(path)
        if '/opportunities/' in path:data['meta']['read_revision']+=1
        return data
    with pytest.raises(ValueError,match='two complete attempts'):
        collector.capture_consistent(changing,'http://127.0.0.1:18000','harborlight-insurance-v1')

def test_connected_snapshot_cannot_silently_mutate(bundle,collector):
    get,_=fake_graph(bundle)
    captured=collector.capture_consistent(get,'http://127.0.0.1:18000','harborlight-insurance-v1')
    captured['responses']['details']['CL06']['findings'][0]['measurement']['value']=99
    with pytest.raises(ValueError,match='digest'):renderer.validate(captured)

def test_capture_rejects_mismatched_local_narrative(bundle,collector):
    get,_=fake_graph(bundle)
    resources={ref:body+' changed' for ref,body in bundle['resource_bodies'].items()}
    with pytest.raises(ValueError,match='resource digest'):
        collector.capture_consistent(get,'http://127.0.0.1:18000','harborlight-insurance-v1',resources)

@pytest.mark.parametrize('base',['http://example.com:18000','http://token@localhost:18000','http://localhost:18000/?token=x','http://localhost','http://localhost:18000/path'])
def test_capture_only_sends_token_to_explicit_local_api(base,collector):
    with pytest.raises(ValueError,match='loopback'):collector.local_base(base)

def test_capture_rejects_incomplete_pages(bundle,collector):
    get,_=fake_graph(bundle)
    def empty_page(path):
        data=get(path)
        if 'offset=10' in path:data['items']=[]
        return data
    with pytest.raises(ValueError,match='Incomplete pagination'):
        collector.capture_consistent(empty_page,'http://127.0.0.1:18000','harborlight-insurance-v1')

def test_capture_helper_runs_when_only_packaged_scripts_are_installed(tmp_path):
    import shutil
    installed=tmp_path/'installed'
    installed.mkdir()
    for name in ['capture_portfolio.py','render_dashboard.py']:
        shutil.copy2(SKILL/'scripts'/name,installed/name)
    result=subprocess.run([sys.executable,str(installed/'capture_portfolio.py'),'--help'],cwd=tmp_path,capture_output=True,text=True)
    assert result.returncode==0,result.stderr
    assert '--api-base' in result.stdout

def test_mcp_capture_calls_only_the_three_named_tools(bundle,collector):
    from urllib.parse import urlencode
    get,_=fake_graph(bundle)
    calls=[]
    def tool(name,args):
        calls.append((name,args))
        assert args['dataset_id']=='harborlight-insurance-v1'
        route='/v1/demo/portfolios/'+args['dataset_id']
        if name=='get_demo_portfolio':return get(route)
        if name=='list_demo_opportunities':return get(route+'/opportunities?'+urlencode({k:v for k,v in args.items() if k!='dataset_id'}))
        assert name=='get_demo_opportunity'
        return get(route+'/opportunities/'+args['case_id'])
    captured=collector.capture_consistent(tool,'http://127.0.0.1:18000','harborlight-insurance-v1',transport='mcp')
    assert captured['source']['transport']=='mcp'
    assert len(calls)==38  # fake server deliberately returns 10-row pages
    assert {name for name,_ in calls}=={'get_demo_portfolio','list_demo_opportunities','get_demo_opportunity'}
    assert len(captured['responses']['details'])==32

def test_mcp_failure_does_not_use_rest_or_write_snapshot(tmp_path,collector,monkeypatch,capsys):
    from types import SimpleNamespace
    async def fail(*args):raise ValueError('MCP capture failed')
    monkeypatch.setitem(sys.modules,'portfolio_mcp',SimpleNamespace(capture_mcp=fail))
    monkeypatch.setenv('ENGINE_DEMO_TOKEN','sentinel-not-a-real-token')
    def no_rest(*args):raise AssertionError('REST fallback was called')
    monkeypatch.setattr(collector,'reader',no_rest)
    out=tmp_path/'absent.json'
    monkeypatch.setattr(sys,'argv',['capture','--api-base','http://127.0.0.1:18000','-o',str(out)])
    assert collector.main()==1
    assert not out.exists()
    assert 'sentinel' not in capsys.readouterr().err

@pytest.fixture
def mcp_helper():
    sys.path.insert(0,str(SKILL/'scripts'))
    try:
        spec=importlib.util.spec_from_file_location('portfolio_mcp_test',SKILL/'scripts/portfolio_mcp.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        return module
    finally:sys.path.pop(0)

def test_mcp_structured_error_is_not_an_empty_portfolio(mcp_helper):
    from types import SimpleNamespace
    with pytest.raises(ValueError,match='capture stopped'):
        mcp_helper.unpack(SimpleNamespace(is_error=True,structured_content={'error':{'code':'INVALID_TOKEN'}}))
    with pytest.raises(ValueError,match='structured result'):
        mcp_helper.unpack(SimpleNamespace(is_error=False,structured_content=None))
    with pytest.raises(ValueError,match='Graph changed'):
        mcp_helper.unpack(SimpleNamespace(is_error=True,structured_content={'error':{'code':'DEMO_REVISION_CHANGED'}}))

def test_mcp_discovery_rejects_missing_or_mutating_tools(mcp_helper,monkeypatch):
    import asyncio
    from types import SimpleNamespace
    monkeypatch.setitem(sys.modules,'mcp.types',SimpleNamespace(PaginatedRequestParams=lambda **kw:kw))
    class Session:
        def __init__(self,tools):self.tools=tools
        async def list_tools(self,**kwargs):return SimpleNamespace(tools=self.tools,next_cursor=None)
    tools=[SimpleNamespace(name=name,annotations=SimpleNamespace(read_only_hint=True)) for name in mcp_helper.TOOLS]
    assert len(asyncio.run(mcp_helper.discover(Session(tools))))==3
    with pytest.raises(ValueError,match='read-only'):asyncio.run(mcp_helper.discover(Session(tools[:-1])))
    tools[0].annotations.read_only_hint=False
    with pytest.raises(ValueError,match='read-only'):asyncio.run(mcp_helper.discover(Session(tools)))
