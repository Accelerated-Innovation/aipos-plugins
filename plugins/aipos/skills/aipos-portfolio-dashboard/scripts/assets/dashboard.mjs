// Deterministic read-only projections. No network, model calls or lifecycle writes.
export const PHASES = ['discovery','exploration','validation','committed','delivery','live','learning','retired'];
export const DISPOSITIONS = ['open','deferred','rejected','stopped'];
export const CONTRACT = 'demo-portfolio.v0.2';
export const OP_SYMBOL = Object.freeze({lte:'≤',gte:'≥',eq:'='});
export const QUESTIONS = [
  ['Q01','Show the portfolio by product and lifecycle phase.'],
  ['Q02','Which claims opportunities are being explored?'],
  ['Q03','Which validation cases have demand but unresolved feasibility?'],
  ['Q04','Why was the instant-bind idea rejected?'],
  ['Q05','Which latest commitments no longer authorize work?'],
  ['Q06','Which opportunities affect multiple products?'],
  ['Q07','Which open cases have spent more than 30 days in their phase?'],
  ['Q08','What entered delivery during October?'],
  ['Q09','Compare claims payment and failed-collection outcomes.'],
  ['Q10','What evidence supports the first-notice-of-loss proposal?']
];
const assert = (ok, message) => { if (!ok) throw new Error(message); };
export const canonical = value => {
  if (Array.isArray(value)) return '[' + value.map(canonical).join(',') + ']';
  if (value && typeof value === 'object') return '{' + Object.keys(value).sort().map(k => JSON.stringify(k)+':'+canonical(value[k])).join(',') + '}';
  return JSON.stringify(value);
};
export function validateBundle(bundle) {
  if (bundle?.response?.error) throw new Error(`${bundle.response.error.code}: ${bundle.response.error.message}`);
  assert(['fixture','connected'].includes(bundle?.source_mode), 'Supply a labeled fixture or captured graph snapshot.');
  if(bundle.source_mode==='connected') {
    assert(['rest','mcp'].includes(bundle.source?.transport) && Number.isFinite(Date.parse(bundle.source?.captured_at)), 'Missing connected read provenance.');
    assert(/^sha256:[0-9a-f]{64}$/.test(bundle.snapshot_digest), 'Missing captured snapshot digest.');
  }
  const {summary, list, details} = bundle.responses || {};
  assert(summary && list && details, 'A complete summary, catalog and case details are required.');
  assert(bundle.resource_bodies !== null && typeof bundle.resource_bodies === 'object' && !Array.isArray(bundle.resource_bodies), 'Resource bodies must be an object; use {} when narratives are unavailable.');
  assert(Array.isArray(bundle.accounts), 'Accounts must be an array; use [] when account names are unavailable.');
  assert(summary.meta?.contract_version === CONTRACT, 'Unsupported portfolio contract version.');
  assert(summary.meta.synthetic === true, 'This prototype requires a synthetic snapshot.');
  assert(Number.isInteger(summary.meta.read_revision) && summary.meta.read_revision >= 0, 'Invalid read revision.');
  assert(/^sha256:[0-9a-f]{64}$/.test(summary.meta.dataset_digest), 'Invalid snapshot digest.');
  const baseline = canonical(summary.meta);
  assert([list, ...Object.values(details)].every(r => canonical(r.meta) === baseline), 'Mixed snapshot revisions. Reload one consistent snapshot.');
  assert(list.offset === 0 && list.items?.length === list.total && bundle.coverage?.catalog_complete === true,
    'Partial catalog: all pages are required for a portfolio dashboard.');
  assert(Object.values(list.filters).every(v => v === null), 'The dashboard requires an unfiltered catalog.');
  assert(summary.total_cases === list.total && list.total > 0, 'Summary and catalog totals disagree.');
  const ids = new Set(list.items.map(r => r.case_id));
  assert(summary.meta.dataset_id==='harborlight-insurance-v1' && ['CL01','CL02','UW08','CL06','BI06','BR04'].every(id=>ids.has(id)), 'The guided questions require the Harborlight fixture dataset.');
  assert(ids.size === list.items.length, 'Duplicate case IDs in catalog.');
  assert(Object.keys(details).length === ids.size, 'Case details are missing or extra.');
  const products = new Set(summary.products.map(p => p.product_id));
  assert(products.size === summary.products.length, 'Duplicate product IDs.');
  const idsInOrder = [...ids];
  assert(canonical(idsInOrder) === canonical([...ids].sort()), 'Catalog is not ordered by case ID.');
  for (const row of list.items) {
    assert(details[row.case_id] && canonical(row) === canonical(details[row.case_id].case), `Case detail mismatch: ${row.case_id}`);
    assert(PHASES.includes(row.phase) && DISPOSITIONS.includes(row.disposition), 'Unknown lifecycle value.');
    assert(['proposal','problem'].includes(row.record_kind), 'Unknown record kind.');
    assert(Number.isFinite(caseAge(row, summary.meta.snapshot_at)) && caseAge(row, summary.meta.snapshot_at) >= 0, 'Invalid phase entry date.');
    const memberships = [row.primary_product_id,...row.additional_product_ids];
    assert(new Set(memberships).size === memberships.length && memberships.every(p => products.has(p)), 'Invalid product membership.');
    const d=details[row.case_id];
    for(const key of ['timeline','studies','evidence_refs','findings','criteria','commitments','work_links','resources']) assert(Array.isArray(d[key]), `Missing ${key}: ${row.case_id}`);
    assert(new Set(d.timeline.map(e=>e.event_id)).size === d.timeline.length, 'Duplicate timeline event.');
    assert(d.timeline.every(e=>Date.parse(e.occurred_at)<=Date.parse(summary.meta.snapshot_at)), 'Completed event is after snapshot.');
    const last=d.commitments.at(-1);
    assert(last ? row.latest_commitment?.commitment_id===last.commitment_id && row.latest_commitment.status===last.status : row.latest_commitment===null, 'Latest commitment disagrees with history.');
    if(bundle.source_mode==='fixture') for(const r of d.resources) assert(typeof bundle.resource_bodies?.[r.reference] === 'string', `Missing resource body: ${r.reference}`);
    for(const f of d.findings) assert(Number.isFinite(f.measurement.value), 'Invalid measurement.');
  }
  const count = (key,value) => list.items.filter(r=>r[key]===value).length;
  assert(PHASES.every(p=>summary.phase_counts[p]===count('phase',p)) && DISPOSITIONS.every(d=>summary.disposition_counts[d]===count('disposition',d)), 'Lifecycle summary totals disagree.');
  assert(summary.total_product_memberships===list.items.reduce((n,r)=>n+1+r.additional_product_ids.length,0), 'Membership total disagrees.');
  for(const p of summary.products) assert(p.primary_case_count===count('primary_product_id',p.product_id) && p.membership_case_count===filterRows(list.items,{product:p.product_id}).length, 'Product totals disagree.');
  return bundle;
}
async function hash(text) {
  const bytes=await globalThis.crypto.subtle.digest('SHA-256',new TextEncoder().encode(text));
  return 'sha256:'+Array.from(new Uint8Array(bytes),b=>b.toString(16).padStart(2,'0')).join('');
}
export async function verifyIntegrity(bundle) {
  const payloads=structuredClone(bundle.responses);
  for(const response of [payloads.summary,payloads.list,...Object.values(payloads.details)]) delete response.meta;
  const raw={contract_version:CONTRACT,payloads,resource_bodies:bundle.resource_bodies,accounts:bundle.accounts};
  if(bundle.source_mode==='fixture') assert(await hash(canonical(raw))===bundle.responses.summary.meta.dataset_digest,'Snapshot digest does not match its contents.');
  else {const {snapshot_digest,...captured}=bundle;assert(await hash(canonical(captured))===snapshot_digest,'Captured snapshot digest does not match its contents.');}
  for(const d of Object.values(bundle.responses.details)) for(const r of d.resources) {
    const body=bundle.resource_bodies?.[r.reference];
    if(body==null && bundle.source_mode==='connected')continue;
    assert(typeof body==='string' && await hash(body)===r.digest,`Resource digest mismatch: ${r.reference}`);
  }
}
export function filterRows(rows,{product='',phase='',disposition='',search=''}={}) {
  const query=search.trim().toLowerCase();
  return rows.filter(r=>(!product || r.primary_product_id===product || r.additional_product_ids.includes(product)) &&
    (!phase || r.phase===phase) && (!disposition || r.disposition===disposition) &&
    (!query || `${r.case_id} ${r.title}`.toLowerCase().includes(query)));
}
export function caseAge(row,snapshot) { return Math.round((Date.parse(snapshot.slice(0,10)+'T00:00:00Z')-Date.parse(row.phase_entered_on+'T00:00:00Z'))/86400000); }
export function outcome(d) {
  const criterion=d.criteria.find(c=>c.finding_refs.length===2);
  if(!criterion) return null;
  const [base,after]=criterion.finding_refs.map(ref=>d.findings.find(f=>f.provenance_reference===ref));
  if(!base || !after || !base.window || !after.window) return null;
  if(base.measurement.metric!==after.measurement.metric || base.measurement.unit!==after.measurement.unit || criterion.unit!==after.measurement.unit) return null;
  const a=base.measurement.value,b=after.measurement.value;
  const nOK=criterion.minimum_n===null || [base,after].every(f=>f.measurement.n!==null && f.measurement.n>=criterion.minimum_n);
  const met=nOK && ({lte:b<=criterion.threshold,gte:b>=criterion.threshold,eq:b===criterion.threshold})[criterion.operator];
  return {base,after,criterion,change:b-a,relative:a===0?null:100*(b-a)/a,met};
}
export function answerQuestion(bundle,id) {
  const {summary,list,details}=bundle.responses, rows=list.items;
  const result={id,title:QUESTIONS.find(q=>q[0]===id)?.[1]||'Question',text:'',caseIds:[],refs:[]};
  const select=cases=>{ result.caseIds=cases.map(r=>r.case_id);return cases; };
  switch(id) {
    case 'Q01': result.text=`${summary.total_cases} distinct opportunities across ${summary.products.length} products. ${summary.products.map(p=>`${p.name}: ${p.primary_case_count} primary`).join('; ')}. ${summary.total_product_memberships} product memberships include shared work. Phases: ${Object.entries(summary.phase_counts).map(([k,v])=>`${k} ${v}`).join(', ')}. Dispositions: ${Object.entries(summary.disposition_counts).map(([k,v])=>`${k} ${v}`).join(', ')}.`;break;
    case 'Q02': {
      const found=select(filterRows(rows,{product:'CLAIMS',phase:'exploration',disposition:'open'}));
      result.text=found.map(r=>{const d=details[r.case_id];return `${r.case_id}: ${r.title}. ${d.studies.map(s=>`${s.study_id} is ${s.status}; ${s.observed_n} of ${s.planned_n} planned sessions completed`).join('; ')}. ${d.findings.length===0?'No measured finding is recorded.':`${d.findings.length} findings recorded.`}`;}).join('\n');
      result.refs=found.flatMap(r=>details[r.case_id].studies.map(s=>s.study_id));break;
    }
    case 'Q03': {
      const found=select(rows.filter(r=>r.phase==='validation' && r.disposition==='open' && r.assessments.demand?.verdict==='passed' && r.assessments.feasibility?.verdict==='unknown'));
      result.text=found.map(r=>`${r.case_id}: demand passed; feasibility remains unknown.`).join('\n')+' These are recorded assessments, not executed gate checks.';
      result.refs=found.flatMap(r=>[r.assessments.demand.assessment_id,...r.assessments.demand.finding_refs,r.assessments.demand.criterion_ref.reference]);break;
    }
    case 'Q04': {
      const d=details.UW08,reason=d.resources.find(r=>r.kind==='disposition_rationale');select([d.case]);
      result.text=(reason && bundle.resource_bodies[reason.reference])||'Rejection rationale body is unavailable; the graph records the rejected disposition and evidence references.';
      result.refs=[...d.findings.map(f=>f.provenance_reference),...d.resources.filter(r=>['disposition_rationale','research_artifact'].includes(r.kind)).map(r=>r.reference),...d.timeline.filter(e=>e.disposition==='rejected').map(e=>e.event_id)];break;
    }
    case 'Q05': {
      const found=select(rows.filter(r=>r.latest_commitment && r.latest_commitment.status!=='authorizing'));
      const br=details.BR04;
      result.text=found.map(r=>`${r.case_id}: ${r.latest_commitment.status}. ${details[r.case_id].resources.filter(x=>['research_artifact','decision'].includes(x.kind)).map(x=>bundle.resource_bodies[x.reference]?.trim()||`Narrative unavailable: ${x.reference}`).join(' ')}`).join('\n')+` BR04’s latest commitment is ${br.case.latest_commitment?.status??'not recorded'}; previous revisions are historical. Cases with no commitment are a separate category.`;
      result.refs=found.flatMap(r=>r.latest_commitment.event_refs);break;
    }
    case 'Q06': {const found=select(rows.filter(r=>r.additional_product_ids.length));result.text=found.map(r=>`${r.case_id}: ${[r.primary_product_id,...r.additional_product_ids].join(' + ')}`).join('\n')+`\n${found.length} distinct cases; ${found.reduce((n,r)=>n+1+r.additional_product_ids.length,0)} memberships in this subset.`;break;}
    case 'Q07': {const found=select(rows.filter(r=>r.disposition==='open' && caseAge(r,summary.meta.snapshot_at)>30));result.text=`As of ${summary.meta.snapshot_at.slice(0,10)}: `+found.map(r=>`${r.case_id} ${caseAge(r,summary.meta.snapshot_at)} days`).join('; ')+'. Phase age alone does not establish a blocker.';break;}
    case 'Q08': {
      const found=select(rows.filter(r=>details[r.case_id].timeline.some(e=>e.kind==='phase_entered' && e.phase==='delivery' && e.occurred_at>='2026-10-01T00:00:00Z' && e.occurred_at<=summary.meta.snapshot_at)));
      result.text=found.map(r=>`${r.case_id} entered delivery on ${details[r.case_id].timeline.find(e=>e.kind==='phase_entered' && e.phase==='delivery' && e.occurred_at>='2026-10-01T00:00:00Z').occurred_at.slice(0,10)}.`).join('\n');result.refs=found.flatMap(r=>details[r.case_id].timeline.filter(e=>e.kind==='phase_entered' && e.phase==='delivery' && e.occurred_at>='2026-10-01T00:00:00Z').map(e=>e.event_id));break;
    }
    case 'Q09': {
      select([details.CL06.case,details.BI06.case]);
      result.text=result.caseIds.map(c=>{const m=outcome(details[c]);if(!m) return `${c}: comparable measurements unavailable.`;const a=m.base.measurement,b=m.after.measurement;const direction=m.change<0?'Reduction':m.change>0?'Increase':'No change';return `${c}: ${a.value} → ${b.value} ${a.unit}; target ${OP_SYMBOL[m.criterion.operator]??'?'}${m.criterion.threshold} ${a.unit}, ${m.met?'met':'missed'}. ${direction}: ${Math.abs(m.change)} ${a.unit==='percent'?'percentage points':a.unit}${m.relative===null?'':` (${Math.abs(m.relative).toFixed(1)}% relative)`}. n=${a.n} and n=${b.n}. Baseline ${m.base.window.start_on}–${m.base.window.end_on}; follow-up ${m.after.window.start_on}–${m.after.window.end_on}.`;}).join('\n')+' Observed changes do not establish causation.';
      result.refs=result.caseIds.flatMap(c=>details[c].findings.map(f=>f.provenance_reference));break;
    }
    case 'Q10': {const d=details.CL02;select([d.case]);result.text=`CL02 is a ${d.case.record_kind}. ${d.findings.length===0?'No measured evidence is recorded.':'Measured findings are available.'} Proposals are intentionally excluded from ranked opportunity reads. Missing evidence is not a zero result; no score or approval is inferred.`;result.refs=[...d.intent_refs,...d.thread_refs];break;}
    default: throw new Error('Unsupported question.');
  }
  result.refs=[...new Set([...result.caseIds,...result.refs])];return result;
}
export function matchQuestion(text) {
  const t=text.toLowerCase().trim();
  const explicit=t.match(/^q(0?[1-9]|10)\b/);if(explicit)return 'Q'+explicit[1].padStart(2,'0');
  if(/approv|move .*deliver|reset|delete|promote/.test(t))return 'write';
  if(/first.notice|cl02/.test(t))return 'Q10';
  if(/compar|outcome|cl06.*bi06|payment checks/.test(t))return 'Q09';
  if(/october|entered delivery/.test(t))return 'Q08';
  if(/30 days|stale|phase age/.test(t))return 'Q07';
  if(/multiple product|cross.product|more than one|shared/.test(t))return 'Q06';
  if(/commitment|authoriz|br04/.test(t))return 'Q05';
  if(/instant.bind|uw08|reject/.test(t))return 'Q04';
  if(/feasibility|demonstrated demand/.test(t))return 'Q03';
  if(/claims.*explor|explor.*claims/.test(t))return 'Q02';
  if(/overview|portfolio|by product/.test(t))return 'Q01';
  return null;
}

const $=id=>document.getElementById(id);
const state={bundle:null,selected:null,tab:'overview'};
const pretty=s=>s.replaceAll('_',' ').replace(/^./,c=>c.toUpperCase());
function el(tag,attrs={},...children){const n=document.createElement(tag);for(const [k,v] of Object.entries(attrs)){if(k.startsWith('on'))n.addEventListener(k.slice(2),v);else if(v!==null)n.setAttribute(k,String(v));}for(const c of children.flat())if(c!==null && c!==undefined)n.append(c instanceof Node?c:document.createTextNode(String(c)));return n;}
const replace=(id,...nodes)=>$(id).replaceChildren(...nodes.flat());
const badge=(value)=>el('span',{class:'badge '+(['invalidated','rejected','stopped','failed'].includes(value)?'red':['incomplete','deferred','inconclusive'].includes(value)?'gold':['authorizing','passed'].includes(value)?'teal':'')},pretty(value));
const reference=t=>el('div',{class:'reference'},t);
const emptyMessage=t=>el('p',{class:'muted'},t);
const rows=()=>state.bundle.responses.list.items;
function filters(){return {product:$('product').value,phase:$('phase').value,disposition:$('disposition').value,search:$('search').value};}
function clearFilters(){for(const id of ['product','phase','disposition','search'])$(id).value='';renderRows();}
function selectCase(id){if(!filterRows(rows(),filters()).some(r=>r.case_id===id))clearFilters();state.selected=id;state.tab='overview';renderRows();$('detail').focus({preventScroll:true});$('detail').scrollIntoView({block:'nearest'});}
function showResource(r){const d=el('details',{class:'resource'},el('summary',{},`${pretty(r.kind)} · ${r.reference}`),el('p',{},state.bundle.resource_bodies[r.reference]??'Narrative body unavailable. Only its reference was returned.'),reference(r.digest));return d;}
function renderRows(){
  const visible=filterRows(rows(),filters());if(state.selected && !visible.some(r=>r.case_id===state.selected))state.selected=null;
  $('result-count').textContent=`${visible.length} of ${rows().length} opportunities · primary + shared product membership`;
  $('empty').hidden=visible.length>0;
  replace('rows',visible.map(row=>el('tr',{class:row.case_id===state.selected?'selected':'','data-case-id':row.case_id},
    el('td',{},el('button',{class:'case-link',onclick:()=>selectCase(row.case_id),'aria-label':`${row.case_id}: ${row.title}`},row.title),el('div',{class:'row-meta'},el('span',{class:'row-id'},row.case_id),[row.primary_product_id,...row.additional_product_ids].map(pretty).join(' + '))),
    el('td',{},badge(row.phase),el('span',{class:'disposition'},row.disposition)),
    el('td',{},row.latest_commitment?badge(row.latest_commitment.status):el('span',{class:'muted'},'None recorded')))));
  for(const b of $('phases').children)b.setAttribute('aria-pressed',String(b.dataset.phase===$('phase').value));
  renderDetail();
}
function overview(d){
  const latest=d.case.latest_commitment;
  const facts=el('div',{class:'fact-grid'},[['Phase age',`${caseAge(d.case,state.bundle.responses.summary.meta.snapshot_at)} days as of snapshot`],['Commitment',latest?pretty(latest.status):'None recorded'],['Evidence',`${d.evidence_refs.length} reference${d.evidence_refs.length===1?'':'s'} · ${d.findings.length} measured findings`],['Representation',d.case.record_kind==='proposal'?'Proposal · intentionally unranked':'Problem · ranked-read eligible']].map(([title,value])=>el('div',{class:'fact'},el('span',{},title),el('strong',{},value))));
  const resources=d.resources.filter(r=>['intent','disposition_rationale','decision','research_artifact','research_plan'].includes(r.kind));
  return [facts,el('p',{class:'muted'},'Lifecycle phase describes position. Commitment status describes authorization in this fictional history.'),...resources.map(showResource)];
}
function evidence(d){
  const cards=[];
  for(const s of d.studies)cards.push(el('div',{class:'record'},el('h3',{},s.study_id,' · ',badge(s.status)),el('p',{},`Sample: ${s.observed_n??'not recorded'} observed / ${s.planned_n??'not specified'} planned. Completion and verdict are separate.`),reference(s.finding_refs.join(' · '))));
  for(const [kind,a] of Object.entries(d.case.assessments))if(a)cards.push(el('div',{class:'record'},el('h3',{},pretty(kind),' · ',badge(a.verdict)),reference(a.assessment_id),reference([...a.finding_refs,...a.artifact_refs].join(' · ')),reference(a.criterion_ref.reference)));
  for(const f of d.findings){const m=f.measurement;cards.push(el('div',{class:'record'},el('h3',{},`${pretty(m.metric)}: ${Number(m.value.toFixed(2))} ${m.unit}`),el('p',{},`${pretty(m.method)} · n=${m.n??'not recorded'} · recorded ${f.occurred_at.slice(0,10)}`),f.window?el('p',{},`Window: ${f.window.start_on} — ${f.window.end_on}`):null,reference(f.provenance_reference)));}
  if(!d.findings.length)cards.push(emptyMessage('No measured finding is recorded. This is missing evidence, not a zero result.'));
  cards.push(...d.resources.filter(r=>['criterion','support_record','research_artifact'].includes(r.kind)).map(showResource));
  return cards;
}
function history(d){return [el('ol',{class:'timeline'},d.timeline.map(e=>el('li',{},el('time',{datetime:e.occurred_at},e.occurred_at.slice(0,10)),el('strong',{},`${pretty(e.kind)}${e.phase?' · '+pretty(e.phase):''}${e.disposition?' · '+pretty(e.disposition):''}`),reference(e.event_id),e.record_refs.length?reference(e.record_refs.join(' · ')):null,...e.resource_refs.map(ref=>{const r=d.resources.find(x=>x.reference===ref);return r?showResource(r):reference(ref);})) ))];}
function commitments(d){
  if(!d.commitments.length)return [emptyMessage('No commitment is recorded. A lifecycle phase or completed study does not grant authority.')];
  const cards=d.commitments.map(c=>el('div',{class:'record'},el('h3',{},c.commitment_id,' · ',badge(c.status)),c.replaces_commitment_id?el('p',{},`Replaces ${c.replaces_commitment_id}`):null,
    el('p',{},c.commitment_id===d.case.latest_commitment?.commitment_id?'Latest commitment in this snapshot.':'Historical commitment; retained for traceability.'),
    ...c.events.map(e=>el('p',{},`${e.occurred_at.slice(0,10)} · ${pretty(e.event)}`,reference(e.event_id))),showResource(c.baseline_ref)));
  if(d.work_links.length)cards.push(el('h3',{},'Delivery links'),...d.work_links.map(l=>el('div',{class:'record'},el('h3',{},l.external_reference,' · ',badge(l.status)),el('p',{},`${pretty(l.link_type)} link · fictional ${l.target_system} reference. Link state is not tracker delivery status.`),reference(l.link_id))));
  else cards.push(emptyMessage('No delivery link is recorded.'));
  return cards;
}
function results(d){const m=outcome(d);if(!m)return [emptyMessage('No comparable baseline and follow-up pair is recorded for this case.')];const a=m.base.measurement,b=m.after.measurement;return [
  el('div',{class:'record'},el('h3',{},pretty(a.metric)),el('p',{},`${a.value} → ${b.value} ${a.unit}`),badge(m.met?'passed':'failed'),el('p',{},`Target ${OP_SYMBOL[m.criterion.operator]??'?'}${m.criterion.threshold} ${a.unit}: ${m.met?'met':'missed'}.`),el('p',{},`Change: ${m.change} ${a.unit==='percent'?'percentage points':a.unit}${m.relative===null?'':` (${m.relative.toFixed(1)}% relative)`}.`),el('p',{},`Baseline: ${m.base.window.start_on} — ${m.base.window.end_on}, n=${a.n}. Follow-up: ${m.after.window.start_on} — ${m.after.window.end_on}, n=${b.n}.`),reference(`${m.base.provenance_reference} · ${m.after.provenance_reference}`)),el('p',{class:'muted'},'These are synthetic observed changes. They do not establish causal attribution.'),showResource(m.criterion.criterion_ref)];}
function renderDetail(){
  if(!state.selected){replace('detail',el('div',{class:'detail-placeholder'},el('span',{class:'detail-icon','aria-hidden':'true'},'↗'),el('div',{},el('h2',{},'The story behind a case'),el('p',{},'Select an opportunity to explore its evidence, decisions and history.'))));return;}
  const d=state.bundle.responses.details[state.selected];const r=d.case;
  const tabs=[['overview','Overview',overview],['evidence','Evidence',evidence],['history','History',history],['commitments','Commitments',commitments],['results','Results',results]];
  const tablist=el('div',{class:'tabs',role:'tablist','aria-label':'Case details'});
  for(const [id,label] of tabs){const button=el('button',{id:`tab-${id}`,role:'tab','aria-selected':id===state.tab,'aria-controls':'case-content',tabindex:id===state.tab?'0':'-1',onclick:()=>{state.tab=id;renderDetail();$(`tab-${id}`).focus();}},label);button.addEventListener('keydown',e=>{if(['ArrowLeft','ArrowRight','Home','End'].includes(e.key)){e.preventDefault();let n=tabs.findIndex(t=>t[0]===state.tab);n=e.key==='Home'?0:e.key==='End'?tabs.length-1:(n+(e.key==='ArrowRight'?1:-1)+tabs.length)%tabs.length;state.tab=tabs[n][0];renderDetail();$(`tab-${state.tab}`).focus();}});tablist.append(button);}
  replace('detail',el('div',{class:'detail-head'},el('div',{class:'detail-kicker'},`${r.case_id} / ${pretty(r.primary_product_id)}`,el('button',{class:'text-button','aria-label':'Close case detail',onclick:()=>{state.selected=null;renderRows();}},'Close ×')),el('h2',{},r.title),el('div',{class:'tags'},badge(r.phase),badge(r.disposition),badge(r.record_kind)),el('div',{class:'detail-context'},d.context.personas.join(' · '),el('br'),d.context.account_ids.map(id=>state.bundle.accounts.find(a=>a.account_id===id)?.name||id).join(' · '))),tablist,
    el('div',{id:'case-content',class:'tab-body',role:'tabpanel','aria-labelledby':`tab-${state.tab}`,tabindex:'0'},tabs.find(t=>t[0]===state.tab)[2](d)));
}
function addAnswer(id,prompt){
  const answer=answerQuestion(state.bundle,id);
  $('conversation').append(el('div',{class:'user-message'},prompt||answer.title),el('div',{class:'assistant','data-answer':id},el('div',{class:'message-label'},'FROM THIS SNAPSHOT'),el('p',{},answer.text),el('div',{class:'answer-cases'},answer.caseIds.map(c=>el('button',{onclick:()=>selectCase(c),'aria-label':`Inspect ${c}`},c,' ↗'))),el('details',{class:'answer-refs'},el('summary',{},`${answer.refs.length} record references`),el('p',{},answer.refs.join('\n')))));
  $('conversation').scrollTop=$('conversation').scrollHeight;
}
async function load(bundle){
  $('dashboard').hidden=true;$('error').hidden=true;$('status').hidden=false;$('status').textContent='Checking the supplied snapshot…';$('load-button').disabled=true;
  try{
    validateBundle(bundle);await verifyIntegrity(bundle);state.bundle=bundle;state.selected=null;state.tab='overview';
    const s=bundle.responses.summary;
    $('header-date').textContent=s.meta.snapshot_at.slice(0,10);
    $('phase-caption').textContent=`All ${s.total_cases} opportunities · select a phase to filter`;
    for(const id of ['product','phase','disposition'])$(id).replaceChildren($(id).firstElementChild);
    for(const p of s.products)$('product').append(el('option',{value:p.product_id},p.name));
    for(const p of PHASES)$('phase').append(el('option',{value:p},pretty(p)));
    for(const d of DISPOSITIONS)$('disposition').append(el('option',{value:d},pretty(d)));
    const nonAuth=rows().filter(r=>r.latest_commitment && r.latest_commitment.status!=='authorizing').length;
    replace('metrics',[[s.total_cases,'Opportunities',`Includes ${rows().filter(r=>r.record_kind==='proposal').length} unranked proposals`,'↗'],[s.products.length,'Products',`${s.total_product_memberships} memberships · shared work counted once`,'▦'],[s.disposition_counts.open,'Open opportunities','Across discovery, delivery and learning','◌'],[nonAuth,'Commitments to review','Latest non-authorizing commitments','◇']].map(([value,label,note,icon])=>el('div',{class:'metric'},el('div',{class:'metric-label'},label,el('span',{'aria-hidden':'true'},icon)),el('div',{class:'metric-value'},value),el('div',{class:'metric-note'},note))));
    replace('phases',PHASES.map(p=>el('button',{class:'phase','data-phase':p,'aria-pressed':'false','aria-label':`Filter ${p}: ${s.phase_counts[p]} opportunities`,onclick:()=>{$('phase').value=$('phase').value===p?'':p;renderRows();}},el('span',{class:'phase-name'},p),el('span',{class:'phase-count'},s.phase_counts[p]))));
    replace('question-list',QUESTIONS.map(([id,title])=>el('button',{'data-question':id,onclick:()=>addAnswer(id)},el('span',{},id),title)));
    const welcome=$('conversation').querySelector('.welcome');$('conversation').replaceChildren(welcome);
    const connected=bundle.source_mode==='connected';
    const transport=connected?bundle.source.transport.toUpperCase():null;
    $('source-mode').textContent=connected?`Graph via ${transport}`:'Example fixture';
    $('source-label').textContent=connected?'CONNECTED CAPTURE':'FIXTURE MODE';
    $('chat-mode').textContent='Guided snapshot queries · 10 sample questions';
    $('source-summary').textContent=`${connected?transport+' capture':'Fixture'} · ${s.meta.dataset_version} · ${s.meta.snapshot_at.slice(0,10)} · read revision ${s.meta.read_revision}${connected?' · captured '+bundle.source.captured_at:''}`;
    $('source-details').textContent=JSON.stringify({source_mode:bundle.source_mode,...s.meta,...(connected?{capture:bundle.source,snapshot_digest:bundle.snapshot_digest}:{})},null,2)+'\n'+(connected?`Read through the local engine ${transport} interface. This page is a fixed capture; rerun the skill to refresh. Supplied narrative bodies are checked against graph references.`:'Read-only synthetic response fixtures. No graph or live API connection.');
    clearFilters();$('dashboard').hidden=false;$('status').hidden=true;
  }catch(error){state.bundle=null;state.selected=null;replace('detail');replace('rows');$('error').textContent=`Snapshot unavailable: ${error.message} Open a complete, consistent snapshot file to continue.`;$('error').hidden=false;$('status').hidden=true;}
  finally{$('load-button').disabled=false;}
}
for(const id of ['product','phase','disposition'])$(id).addEventListener('change',renderRows);
$('search').addEventListener('input',renderRows);$('clear-filters').addEventListener('click',clearFilters);$('empty-clear').addEventListener('click',clearFilters);
$('nav-portfolio').addEventListener('click',()=>$('workspace').scrollIntoView());$('nav-questions').addEventListener('click',()=>$('chat-input').focus());
$('load-button').addEventListener('click',()=>$('file-input').click());
$('file-input').addEventListener('change',async e=>{const file=e.target.files[0];if(!file)return;try{if(file.size>5000000)throw new Error('Snapshot exceeds the 5 MB preview limit.');await load(JSON.parse(await file.text()));}catch(error){await load({response:{error:{code:'INVALID_SNAPSHOT',message:error.message}}});}finally{e.target.value='';}});
$('chat-form').addEventListener('submit',e=>{e.preventDefault();if(!state.bundle)return;const text=$('chat-input').value.trim();if(!text)return;$('chat-input').value='';const id=matchQuestion(text);if(id && id!=='write')addAnswer(id,text);else{const caseId=text.toUpperCase().match(/\b(?:BR|UW|CL|BI)\d{2}\b/)?.[0];if(id!=='write' && caseId && state.bundle.responses.details[caseId]){selectCase(caseId);$('conversation').append(el('div',{class:'assistant'},el('p',{},`Opened ${caseId}. Its tabs show the supplied records.`)));}else $('conversation').append(el('div',{class:'user-message'},text),el('div',{class:'assistant'},el('p',{},id==='write'?'This explorer is read-only. It cannot approve, promote, move or reset work. Use the owning governed decision interface for a real change.':'This guided prototype supports the ten sample questions and case IDs. Choose a question above; open-ended AI chat is not connected.')));$('conversation').scrollTop=$('conversation').scrollHeight;}});
try{await load(JSON.parse($('portfolio-data').textContent));}catch(error){await load({response:{error:{code:'INVALID_SNAPSHOT',message:error.message}}});}
