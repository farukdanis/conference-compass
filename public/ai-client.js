let worker,serial=0,status={phase:'idle'};
const pending=new Map(),listeners=new Set();
function update(next){status=next;for(const fn of listeners)fn(status)}
export function subscribeAI(fn){listeners.add(fn);fn(status);return()=>listeners.delete(fn)}
export function rankGoal(query){
  if(typeof query!=='string'||!query.trim()||query.length>2500)return Promise.reject(Error('Invalid goal'));
  if(!worker){
    worker=new Worker(new URL('./ai-worker.js',import.meta.url),{type:'module'});
    worker.onmessage=({data})=>{if(data.phase)update({phase:data.phase});const item=pending.get(data.id);if(item){clearTimeout(item.timer);pending.delete(data.id);data.error?item.reject(Error(data.error)):item.resolve(data)}};
    worker.onerror=(event)=>{update({phase:'error'});for(const item of pending.values()){clearTimeout(item.timer);item.reject(Error(event.message||'AI could not load'))}pending.clear();worker.terminate();worker=null};
  }
  return new Promise((resolve,reject)=>{const id=++serial;const timer=setTimeout(()=>{pending.delete(id);update({phase:'error'});reject(Error('AI download timed out'))},180000);pending.set(id,{resolve,reject,timer});worker.postMessage({id,query})});
}
