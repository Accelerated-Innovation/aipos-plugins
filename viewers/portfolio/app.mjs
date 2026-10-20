import {PHASES, DISPOSITIONS, QUESTIONS, validateBundle, verifyIntegrity, filterRows, caseAge, outcome, answerQuestion, matchQuestion} from './model.mjs';
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
  el('div',{class:'record'},el('h3',{},pretty(a.metric)),el('p',{},`${a.value} → ${b.value} ${a.unit}`),badge(m.met?'passed':'failed'),el('p',{},`Target ${m.criterion.operator==='lte'?'≤':'≥'}${m.criterion.threshold} ${a.unit}: ${m.met?'met':'missed'}.`),el('p',{},`Change: ${m.change} ${a.unit==='percent'?'percentage points':a.unit}${m.relative===null?'':` (${m.relative.toFixed(1)}% relative)`}.`),el('p',{},`Baseline: ${m.base.window.start_on} — ${m.base.window.end_on}, n=${a.n}. Follow-up: ${m.after.window.start_on} — ${m.after.window.end_on}, n=${b.n}.`),reference(`${m.base.provenance_reference} · ${m.after.provenance_reference}`)),el('p',{class:'muted'},'These are synthetic observed changes. They do not establish causal attribution.'),showResource(m.criterion.criterion_ref)];}
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
