// Deterministic read-only projections. No network, model calls or lifecycle writes.
export const PHASES = ['discovery','exploration','validation','committed','delivery','live','learning','retired'];
export const DISPOSITIONS = ['open','deferred','rejected','stopped'];
export const CONTRACT = 'demo-portfolio.v0.2';
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
      result.text=result.caseIds.map(c=>{const m=outcome(details[c]);if(!m) return `${c}: comparable measurements unavailable.`;const a=m.base.measurement,b=m.after.measurement;return `${c}: ${a.value} → ${b.value} ${a.unit}; target ≤${m.criterion.threshold} ${a.unit}, ${m.met?'met':'missed'}. Reduction ${Math.abs(m.change)} ${a.unit==='percent'?'percentage points':a.unit}${m.relative===null?'':` (${Math.abs(m.relative).toFixed(1)}% relative)`}. n=${a.n} and n=${b.n}. Baseline ${m.base.window.start_on}–${m.base.window.end_on}; follow-up ${m.after.window.start_on}–${m.after.window.end_on}.`;}).join('\n')+' Observed changes do not establish causation.';
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
