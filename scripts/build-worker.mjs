// Builds dist/ for the optional Cloudflare Worker deployment (static client + /api/metrics + /stats).
import fs from 'node:fs/promises';
import {execFileSync} from 'node:child_process';
execFileSync(process.execPath,['scripts/gen-session-ids.mjs'],{stdio:'inherit'});
await fs.rm('dist',{recursive:true,force:true});
await fs.mkdir('dist/server',{recursive:true});
await fs.cp('public','dist/client',{recursive:true});
await fs.cp('worker','dist/server',{recursive:true});
const databaseId=process.env.D1_DATABASE_ID||'00000000-0000-4000-8000-000000000000';
await fs.writeFile('dist/server/wrangler.json',JSON.stringify({name:process.env.WORKER_NAME||'conference-compass',main:'index.js',compatibility_date:'2026-05-15',vars:{TIMEZONE:process.env.TIMEZONE||'UTC'},assets:{directory:'../client',binding:'ASSETS',run_worker_first:['/api/*','/stats']},d1_databases:[{binding:'DB',database_name:process.env.D1_DATABASE_NAME||'conference-compass-metrics',database_id:databaseId,migrations_dir:'../../drizzle'}]},null,2));
console.log('dist/ ready');
