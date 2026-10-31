// Pre-computes normalised MiniLM embeddings for every non-break session in public/program.json.
// Run after replacing the programme: npm run vectors
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {pipeline,env} from '@huggingface/transformers';
const root=path.join(path.dirname(fileURLToPath(import.meta.url)),'..');
env.cacheDir=path.join(root,'.model-cache');
const MODEL='Xenova/paraphrase-multilingual-MiniLM-L12-v2';
const program=JSON.parse(await fs.readFile(path.join(root,'public/program.json'),'utf8'));
const rows=program.events.filter(e=>e.valid!==false&&e.type!=='break');
const extractor=await pipeline('feature-extraction',MODEL,{dtype:'q8',device:'cpu'});
export const sessionText=e=>Object.values(e.translations).flatMap(t=>[t.title,t.description,...(t.talks||[]).map(x=>x.title)]).filter(Boolean).join('. ').slice(0,2200);
const vectors=[];
for(const e of rows){const out=await extractor(sessionText(e),{pooling:'mean',normalize:true});vectors.push({id:e.id,v:Array.from(out.data,x=>Math.round(x*1e6)/1e6)})}
await fs.writeFile(path.join(root,'public/vectors.json'),JSON.stringify({fetchedAt:program.fetchedAt,model:MODEL,vectors}));
console.log('vectors.json:',vectors.length,'sessions with',MODEL);
