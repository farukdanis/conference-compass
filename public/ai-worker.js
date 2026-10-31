import {pipeline,env} from './vendor/transformers.web.min.js';
env.allowLocalModels=false;
env.backends.onnx.wasm.wasmPaths={mjs:new URL('./vendor/ort-runtime.js',import.meta.url).href,wasm:new URL('./vendor/ort-wasm-simd-threaded.jsep.wasm',import.meta.url).href};
env.backends.onnx.wasm.numThreads=1;
let ready;
async function initialize(){
  const [extractor,cache]=await Promise.all([
    pipeline('feature-extraction','Xenova/paraphrase-multilingual-MiniLM-L12-v2',{dtype:'q8',device:'wasm'}),
    fetch('./vectors.json').then(r=>{if(!r.ok)throw Error('Programme index unavailable');return r.json()})
  ]);
  return {extractor,vectors:cache.vectors};
}
self.onmessage=async({data})=>{
  try{
    if(!ready){self.postMessage({phase:'loading'});ready=initialize().catch(e=>{ready=null;throw e})}
    const {extractor,vectors}=await ready;
    const output=await extractor(data.query,{pooling:'mean',normalize:true});
    const scores=Object.fromEntries(vectors.map(x=>[x.id,x.v.reduce((sum,v,i)=>sum+v*output.data[i],0)]));
    self.postMessage({id:data.id,scores,mode:'local-semantic',phase:'ready'});
  }catch(e){self.postMessage({id:data.id,error:e.message,phase:'error'})}
};
