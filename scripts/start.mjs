// Full local stack with the optional analytics backend (Cloudflare Worker + local D1 via wrangler).
import {spawn} from 'node:child_process';
const run=(args)=>new Promise((resolve,reject)=>{const p=spawn(process.execPath,args,{stdio:'inherit',env:{...process.env,CLOUDFLARE_CF_FETCH_ENABLED:'false',WRANGLER_SEND_METRICS:'false'}});p.on('exit',c=>c===0?resolve():reject(Error('Local server command failed: '+c)))});
await run(['scripts/build-worker.mjs']);
await run(['node_modules/wrangler/bin/wrangler.js','d1','migrations','apply','DB','--local','--config','dist/server/wrangler.json','--persist-to','.wrangler/state']);
await run(['node_modules/wrangler/bin/wrangler.js','dev','--config','dist/server/wrangler.json','--local','--persist-to','.wrangler/state','--port','8765','--ip','127.0.0.1']);
