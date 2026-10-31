import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';
import {safeEvent,track} from '../public/analytics.js';
import worker,{counters,isOwner} from '../worker/index.js';
import {dashboard} from '../worker/dashboard.js';
test('only aggregate fields are accepted, no free text or IP',()=>{
 assert.deepEqual(safeEvent('planner_completed',{mode:'topics',goal:'private',ip:'1.2.3.4',event_count:99}),{event:'planner_completed',params:{mode:'topics'}});
 assert.equal(safeEvent('search',{query:'private'}),null);assert.doesNotThrow(()=>track('page_view'));
 const req=new Request('https://example.test/api/metrics',{headers:{'user-agent':'Mozilla iPhone Safari private-identifying-string','cf-connecting-ip':'1.2.3.4'}});
 const rows=counters({event:'page_view',params:{source:'google',goal:'secret'}},req);
 assert.ok(rows.some(x=>x[0]==='country'&&x[1]==='Unknown'));assert.ok(!JSON.stringify(rows).includes('private'));assert.ok(!JSON.stringify(rows).includes('1.2.3.4'));
 assert.equal(counters({event:'invalid'},req),null);
});
test('unknown or injected session IDs never enter counters',()=>{
 assert.deepEqual(counters({event:'session_view',params:{session_id:'99999999'}},new Request('https://example.test')), [['event','session_view']]);
 assert.ok(!JSON.stringify(counters({event:'section_view',params:{section:'private free text'}},new Request('https://example.test'))).includes('private'));
});
test('metrics reject cross-origin, invalid body and non-POST',async()=>{
 const env={DB:{batch(){throw Error('should not write')}}};
 assert.equal((await worker.fetch(new Request('https://example.test/api/metrics'),env)).status,405);
 assert.equal((await worker.fetch(new Request('https://example.test/api/metrics',{method:'POST',headers:{origin:'https://evil.test'}}),env)).status,403);
 assert.equal((await worker.fetch(new Request('https://example.test/api/metrics',{method:'POST',headers:{origin:'https://example.test','content-type':'application/json'},body:'{"event":"private"}'}),env)).status,400);
});
test('accepted events store marginal counts only and apply 90-day expiry',async()=>{
 let batch;const env={DB:{prepare(sql){return {bind(...args){return {sql,args}}}},async batch(rows){batch=rows}}};
 const req=new Request('https://example.test/api/metrics',{method:'POST',headers:{origin:'https://example.test','content-type':'application/json','cf-connecting-ip':'1.2.3.4'},body:JSON.stringify({event:'planner_completed',params:{mode:'topics',goal:'secret'}})});
 assert.equal((await worker.fetch(req,env)).status,204);assert.equal(batch.length,3);assert.ok(batch.at(-1).sql.startsWith('DELETE'));assert.ok(!JSON.stringify(batch).includes('secret'));assert.ok(!JSON.stringify(batch).includes('1.2.3.4'));
});
test('owner dashboard is hidden without a secret and requires Basic auth',async()=>{
 assert.equal((await worker.fetch(new Request('https://example.test/stats'),{})).status,404);
 const env={DASHBOARD_PASSWORD:'correct horse',DB:{prepare(){return {bind(){return {async all(){return {results:[]}}}}}}}};
 const anon=await worker.fetch(new Request('https://example.test/stats'),env);assert.equal(anon.status,401);assert.ok(anon.headers.get('www-authenticate').startsWith('Basic'));
 const bad=new Request('https://example.test/stats',{headers:{authorization:'Basic '+btoa('owner:wrong')}});
 assert.equal((await worker.fetch(bad,env)).status,401);assert.equal(isOwner(bad,env),false);
 const owner=new Request('https://example.test/stats',{headers:{authorization:'Basic '+btoa('owner:correct horse')}});
 const r=await worker.fetch(owner,env);assert.equal(r.status,200);assert.equal(r.headers.get('cache-control'),'private, no-store');assert.ok((await r.text()).includes('No data yet'));
});
test('dashboard escapes values, web has no Google tracker or permission prompt',()=>{
 assert.ok(!dashboard([{day:'2026-10-03',metric:'city',value:'<img src=x onerror=alert(1)>',count:2}],30).includes('<img'));
 const src=fs.readFileSync(new URL('../public/analytics.js',import.meta.url),'utf8');assert.ok(!src.includes('googletagmanager'));assert.ok(!src.includes('createElement(\'script\')'));assert.ok(!src.includes('showChoice'));assert.ok(src.includes("credentials:'omit'"));
});
