# 🧭 Conference Compass

**A privacy-first, AI-assisted personal planner for large medical congresses.**
Tell it what you want to learn; it reads the whole scientific programme, matches sessions to your goals with an on-device multilingual language model, and builds a conflict-free personal itinerary you can export to your calendar.

Originally built for a national emergency medicine congress, now released as a generic, brand-free tool with a fully fictional demo programme.

[![License: MIT](https://img.shields.io/badge/License-MIT-0b4f6c.svg)](LICENSE)
![No backend required](https://img.shields.io/badge/backend-optional-1f7a9c)
![AI runs in the browser](https://img.shields.io/badge/AI-on--device-1f7a9c)
[![Live demo on Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Demo-Hugging%20Face%20Space-ffcc4d)](https://huggingface.co/spaces/farukdanis/conference-compass)

---

## Why

A four-day congress can have 100+ sessions across ten halls. Attendees typically skim a PDF, miss the sessions that matter to them, and double-book themselves. Conference Compass turns a free-text learning goal ("I want to get better at ultrasound in shock and understand clinical AI") into a feasible schedule — without sending that goal anywhere.

## Features

| | |
|---|---|
| 🧠 **Multilingual semantic matching** | `Xenova/paraphrase-multilingual-MiniLM-L12-v2` (quantised, Transformers.js + ONNX Runtime Web) embeds your goal **in the browser** and compares it with pre-computed session vectors. Works in Turkish and English (and 50+ other languages). |
| 📅 **Conflict-free planning** | An exact dynamic-programming scheduler over each day's sessions: respects attendance hours, daily pace (4 / 6 / 10 sessions), a configurable room-change buffer, pinned sessions and personal time blocks. Impossible pins fail loudly instead of disappearing silently. |
| 📌 **Human in the loop** | Pin, remove, compare "what else is on at the same time", reserve personal time; replanning keeps your choices. Courses are never auto-added (registration check), satellite symposia are opt-in. |
| 📤 **Export** | RFC 5545 `.ics` calendar (correct UTC offsets, escaping and line folding) and a print/PDF view. |
| 📴 **Offline-ready PWA** | Service worker caches the programme and your plan; preferences live in `localStorage`. |
| 🔒 **Privacy by design** | No accounts, no cookies, no third-party trackers. The optional analytics backend stores only cookieless, ID-free daily marginal counters (see [ANALYTICS-SETUP.md](ANALYTICS-SETUP.md)). |
| 🌐 **Bilingual UI** | Turkish / English toggle; all programme content is bilingual. |
| 🤖 **Agent-friendly** | Registers read-only `search_conference_program` and `read_personal_plan` tools via the experimental `document.modelContext` API when available. |

The model **does not generate text**. It never invents sessions, speakers, times or rooms — it only ranks what is in the programme file. If the model cannot load, the app falls back to transparent keyword/topic matching and says so.

## Architecture

```
public/
  index.html, app.js, styles.css   UI (vanilla JS, no framework, no build step)
  engine.js                        topic tagging, scoring, DP scheduler, ICS writer
  ai-client.js → ai-worker.js      Web Worker running MiniLM via Transformers.js/ONNX (WASM)
  program.json                     programme data (fictional demo by default)
  vectors.json                     pre-computed, L2-normalised session embeddings
  sw.js, manifest.json             offline cache / PWA
  analytics*.js                    optional cookieless counters (disabled by default)
worker/                            optional Cloudflare Worker: /api/metrics + /stats dashboard (D1)
scripts/
  make-demo-program.py             generates the fictional demo programme
  build-vectors.mjs                computes session embeddings with the same model (Node)
  gen-session-ids.mjs              analytics allow-list derived from the programme
  serve-static.mjs                 zero-dependency local preview server
tests/                             node:test suites (planner + analytics)
docs/PROGRAM-SCHEMA.md             how to plug in a real programme
```

Score for each candidate session = topic matches + goal keyword hits + semantic cosine similarity (+ small role-based adjustments). The scheduler then maximises total score per day subject to hard constraints (no overlap incl. room-change buffer, availability window, pace limit, all pinned items included).

## Quick start

```sh
git clone https://github.com/farukdanis/conference-compass
cd conference-compass
npm run serve            # http://127.0.0.1:8765  (static, no install needed)
```

The first AI-assisted plan downloads the model (~120 MB) from Hugging Face into the browser cache.

Development:

```sh
npm ci
npm test                 # 17 tests: scheduling invariants, ICS, analytics privacy
npm run demo             # regenerate demo programme + vectors
npm start                # full stack incl. optional analytics (wrangler + local D1)
```

## Use it for your own meeting

1. Write your programme into `public/program.json` following [docs/PROGRAM-SCHEMA.md](docs/PROGRAM-SCHEMA.md).
2. `npm ci && npm run vectors` to rebuild the semantic index.
3. Adjust topic keyword lists in `public/engine.js` if your field is not emergency medicine.
4. Deploy `public/` to any static host (GitHub Pages, Hugging Face Spaces, Netlify, Cloudflare Pages…).

## Limitations

- Walking times between halls are not measured; the buffer is a user setting.
- Individual talk times inside a session are often unpublished, so sessions are scheduled as a whole.
- Recommendations are relevance estimates, not ratings of scientific quality or educational level.
- The demo programme, congress, venue and "Speaker A"-style names are entirely fictional.

## Türkçe özet

**Conference Compass**, büyük tıp kongreleri için gizlilik öncelikli, yapay zekâ destekli kişisel program planlayıcısıdır. Öğrenme hedefinizi Türkçe veya İngilizce yazarsınız; çok dilli MiniLM modeli **tarayıcınızda** çalışarak hedefinizi oturum içerikleriyle anlamsal olarak eşleştirir, çizelgeleme algoritması da çakışmasız, salon geçiş payını ve katılım saatlerinizi gözeten bir program kurar. Plan `.ics` takvim dosyası ve PDF olarak dışa aktarılır, çevrimdışı çalışır; hesap, çerez veya dış izleyici yoktur. İsteğe bağlı ölçüm yalnızca çerezsiz, kimliksiz günlük toplamlar tutar. Ulusal bir acil tıp kongresi için geliştirilmiş, markasız ve kurgusal demo programla açık kaynak olarak yayımlanmıştır.

## Author

**Faruk Danış, MD** — emergency physician, Bolu Abant İzzet Baysal University · [faruk.md](https://www.faruk.md) · [ORCID 0000-0001-8722-5402](https://orcid.org/0000-0001-8722-5402)

Released under the [MIT License](LICENSE).
