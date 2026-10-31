import {dashboard} from './dashboard.js';
import {SESSION_IDS} from './session-ids.js';
const events=new Set(['page_view','planner_started','planner_completed','planner_failed','session_view','session_added','session_removed','calendar_download','section_view','language_changed','print_plan','program_download','preset_selected','engagement']);
const fixed={section:['planner','explore','program','plan','speakers','about'],mode:['local-semantic','topics'],language:['tr','en'],preset:['clinical','ai','resident'],duration:['under_30s','30_119s','2_5min','over_5min'],source:['direct','google','bing','instagram','facebook','linkedin','x','youtube','other']};
export function coarseAgent(ua){return {device:/ipad|tablet/i.test(ua)?'Tablet':/mobi|iphone|android/i.test(ua)?'Phone':'Desktop',browser:/edg/i.test(ua)?'Edge':/firefox/i.test(ua)?'Firefox':/opr|opera/i.test(ua)?'Opera':/chrome|crios/i.test(ua)?'Chrome':/safari/i.test(ua)?'Safari':'Other',os:/android/i.test(ua)?'Android':/iphone|ipad/i.test(ua)?'iOS':/windows/i.test(ua)?'Windows':/mac os/i.test(ua)?'macOS':/linux/i.test(ua)?'Linux':'Other'}}
export function counters(body,request){
 if(!body||!events.has(body.event))return null;
 const rows=[['event',body.event]],p=body.params||{};
 if(body.event==='page_view'){
  const agent=coarseAgent(request.headers.get('user-agent')||'');
  for(const [k,v]of Object.entries(agent))rows.push([k,v]);
  // Use only platform-provided geography. Never derive/store the IP address.
  const cf=request.cf||{};const country=/^[A-Z]{2}$/.test(cf.country||'')?cf.country:'Unknown';
  rows.push(['country',country]);
  const city=typeof cf.city==='string'&&/^[\p{L}\p{M} .'-]{1,60}$/u.test(cf.city)?cf.city:'Unknown';
  rows.push(['city',city==='Unknown'?city:country+' / '+city]);
  if(fixed.source.includes(p.source))rows.push(['source',p.source]);
 }
 const permitted={planner_completed:['mode'],session_view:['session_id'],session_added:['session_id'],session_removed:['session_id'],section_view:['section'],language_changed:['language'],preset_selected:['preset'],engagement:['duration']};
 for(const key of permitted[body.event]||[]){const value=String(p[key]??'');if(key==='session_id'?SESSION_IDS.includes(value):fixed[key]?.includes(value))rows.push([body.event+':'+key,value])}
 return rows;
}
// The owner dashboard is protected with HTTP Basic auth. Set the DASHBOARD_PASSWORD secret (wrangler secret put DASHBOARD_PASSWORD).
function safeEqual(a,b){const x=new TextEncoder().encode(a),y=new TextEncoder().encode(b);let diff=x.length^y.length;for(let i=0;i<Math.max(x.length,y.length);i++)diff|=(x[i]||0)^(y[i]||0);return diff===0}
export function isOwner(request,env={}){const secret=env.DASHBOARD_PASSWORD;if(!secret)return false;const h=request.headers.get('authorization')||'';if(!h.startsWith('Basic '))return false;let decoded='';try{decoded=atob(h.slice(6))}catch{return false}const password=decoded.slice(decoded.indexOf(':')+1);return safeEqual(password,secret)}
const privateHeaders={'Cache-Control':'private, no-store','Content-Type':'text/html; charset=utf-8','X-Robots-Tag':'noindex, nofollow','Vary':'Authorization','X-Content-Type-Options':'nosniff'};
export default {async fetch(request,env){
 const url=new URL(request.url);
 if(url.pathname==='/api/metrics'){
  if(request.method!=='POST')return new Response(null,{status:405});
  const origin=request.headers.get('origin');
  if(origin!==url.origin||request.headers.get('sec-fetch-site')==='cross-site')return new Response(null,{status:403});
  if(!request.headers.get('content-type')?.startsWith('application/json')||Number(request.headers.get('content-length')||0)>4096)return new Response(null,{status:400});
  if(/bot|crawler|spider|headless/i.test(request.headers.get('user-agent')||''))return new Response(null,{status:204});
  let body;try{const reader=request.body?.getReader();if(!reader)return new Response(null,{status:400});let size=0,raw='';const decoder=new TextDecoder();for(;;){const {done,value}=await reader.read();if(done)break;size+=value.length;if(size>4096){await reader.cancel();return new Response(null,{status:413})}raw+=decoder.decode(value,{stream:true})}raw+=decoder.decode();body=JSON.parse(raw)}catch{return new Response(null,{status:400})}
  const rows=counters(body,request);if(!rows)return new Response(null,{status:400});
  try{
   const day=new Intl.DateTimeFormat('en-CA',{timeZone:env.TIMEZONE||'UTC',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());
   const cutoff=new Date(Date.now()-90*86400000).toISOString().slice(0,10);
   await env.DB.batch([...rows.map(([metric,value])=>env.DB.prepare('INSERT INTO daily_counts (day,metric,value,count) VALUES (?,?,?,1) ON CONFLICT(day,metric,value) DO UPDATE SET count=MIN(count+1,1000000)').bind(day,metric,value)),env.DB.prepare('DELETE FROM daily_counts WHERE day < ?').bind(cutoff)]);
   return new Response(null,{status:204,headers:{'Cache-Control':'no-store'}});
  }catch{return new Response(null,{status:503,headers:{'Cache-Control':'no-store'}})}
 }
 if(url.pathname==='/stats'){
  if(!env.DASHBOARD_PASSWORD)return new Response('Not found',{status:404,headers:privateHeaders});
  if(!isOwner(request,env))return new Response('Authentication required.',{status:401,headers:{...privateHeaders,'WWW-Authenticate':'Basic realm="Conference Compass stats", charset="UTF-8"'}});
  const days=[7,30,90].includes(Number(url.searchParams.get('days')))?Number(url.searchParams.get('days')):30;
  try{const cutoff=new Date(Date.now()-(days-1)*86400000).toISOString().slice(0,10);
   const result=await env.DB.prepare('SELECT day,metric,value,count FROM daily_counts WHERE day >= ? ORDER BY day DESC').bind(cutoff).all();
   return new Response(dashboard(result.results||[],days),{headers:privateHeaders});
  }catch{return new Response('Statistics are unavailable right now. Please try again shortly.',{status:503,headers:privateHeaders})}
 }
 return env.ASSETS.fetch(request);
}};
