import {analyticsEnabled} from './analytics-config.js';
// First-party marginal counters only. No cookies, IDs, fingerprints or visitor histories.
const names=new Set(['page_view','planner_started','planner_completed','planner_failed','session_view','session_added','session_removed','calendar_download','section_view','language_changed','print_plan','program_download','preset_selected','engagement']);
const enums={mode:['local-semantic','topics'],section:['planner','explore','program','plan','speakers','about'],language:['tr','en'],preset:['clinical','ai','resident'],duration:['under_30s','30_119s','2_5min','over_5min'],source:['direct','google','bing','instagram','facebook','linkedin','x','youtube','other']};
const fields={page_view:['source'],planner_completed:['mode'],session_view:['session_id'],session_added:['session_id'],session_removed:['session_id'],section_view:['section'],language_changed:['language'],preset_selected:['preset'],engagement:['duration']};
export function safeEvent(name,params={}){if(!names.has(name))return null;const clean={};for(const key of fields[name]||[]){const value=String(params[key]??'');if(key==='session_id'?/^\d{1,8}$/.test(value):enums[key]?.includes(value))clean[key]=value}return {event:name,params:clean}}
let active=false,budget=0;
export function track(name,params){const item=safeEvent(name,params);if(!active||!item||budget++>=150||navigator.doNotTrack==='1'||navigator.globalPrivacyControl)return;fetch('/api/metrics',{method:'POST',headers:{'Content-Type':'application/json'},credentials:'omit',body:JSON.stringify(item),keepalive:true}).catch(()=>{})}
function source(){try{const host=new URL(document.referrer).hostname.toLowerCase();for(const s of ['google','bing','instagram','facebook','linkedin','youtube'])if(host===s+'.com'||host.endsWith('.'+s+'.com'))return s;if(['t.co','x.com','twitter.com'].includes(host))return 'x';return host===location.hostname?'direct':'other'}catch{return 'direct'}}
export function initAnalytics(){
 if(active||!analyticsEnabled)return;active=true;
 track('page_view',{source:source()});
 let start=document.visibilityState==='visible'?performance.now():null,total=0,sent=false;
 const accrue=()=>{if(start!==null){total+=performance.now()-start;start=null}};
 document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='hidden')accrue();else start=performance.now()});
 window.addEventListener('pagehide',()=>{if(sent)return;sent=true;accrue();track('engagement',{duration:total<30000?'under_30s':total<120000?'30_119s':total<300000?'2_5min':'over_5min'})});
 const footer=document.createElement('p');footer.className='metrics-note';footer.innerHTML='<a href="privacy.html">Privacy · Gizlilik</a> · Cookieless aggregate usage statistics';document.body.append(footer);
}
