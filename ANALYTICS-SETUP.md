# Optional cookieless analytics (Cloudflare Worker + D1)

Analytics are **off by default** (`public/analytics-config.js` → `analyticsEnabled=false`). The static planner works without any backend.

When enabled, `public/analytics.js` sends bounded, allow-listed events to the same site's `/api/metrics` endpoint with credentials omitted. There is no visitor ID, session ID, cookie, fingerprint or visitor history. The `session_id` field is a *programme* identifier (checked against `worker/session-ids.js`, generated from `public/program.json`), never a visitor session. Do Not Track and Global Privacy Control are respected; each page has a 150-event budget and known bot user agents are skipped.

D1 table `daily_counts` holds only `day, metric, value, count`. Country/city, coarse device/browser/OS, traffic source category and programme events are separate marginal counters and cannot be joined into an individual visit. The IP address is never read or stored by the application. Counters older than 90 days are deleted on new intake.

## Owner dashboard

`GET /stats` is protected with HTTP Basic auth against the `DASHBOARD_PASSWORD` secret (any username). Without the secret the route returns 404. Responses are `private, no-store`; the service worker never caches it.

## Deploy

```sh
npm ci
# 1. enable analytics in public/analytics-config.js
# 2. create the database and note its id
npx wrangler d1 create conference-compass-metrics
D1_DATABASE_ID=<id> TIMEZONE=Europe/Istanbul npm run build
npx wrangler d1 migrations apply DB --remote --config dist/server/wrangler.json
npx wrangler secret put DASHBOARD_PASSWORD --config dist/server/wrangler.json
npx wrangler deploy --config dist/server/wrangler.json
```

Local full stack: `npm start` (builds, applies migrations to a local D1 and runs `wrangler dev` on port 8765).
