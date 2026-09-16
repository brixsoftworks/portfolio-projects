# Environment Variables

## Mobile app (`apps/mobile/.env`, from `.env.example`)

All variables are `EXPO_PUBLIC_*` so Metro inlines them at build time.

| Variable | Default | Purpose |
| --- | --- | --- |
| `EXPO_PUBLIC_DEMO_MODE` | `1` | `1` = in-process demo backend (InMemoryStore + demo coach), no login, no server. `0` = real backend via the self-hosted server. |
| `EXPO_PUBLIC_API_URL` | `` (same origin) | Self-hosted backend origin, no trailing slash. Web can leave empty (server serves the site + API on one origin). Native needs an absolute URL, e.g. `https://quacko.college.edu`. |

Runtime access goes through `apps/mobile/src/env.ts` — never read `process.env` in screens.

## Self-hosted server (`apps/server/.env`, from `.env.example`)

| Variable | Default | Purpose |
| --- | --- | --- |
| `DATA_DIR` | `.data` | Where the SQLite DB and uploaded proof media live (created on demand). |
| `JWT_SECRET` | dev-only | HMAC secret for auth JWTs. **Required (≥ 16 chars) in production** and must stay stable across restarts. |
| `HOST` / `PORT` | `0.0.0.0` / `8787` | Bind address and port for web + API. |
| `TIMEZONE` | `UTC` | IANA zone used for streaks / "today". |
| `PUBLIC_URL` | — | Absolute origin used for absolute upload links (when behind a proxy). |
| `WEB_DIR` | — | Directory holding the exported Expo web app, served at `/`. |
| `AI_API_KEY` / `AI_BASE_URL` / `AI_MODEL` | empty / `https://api.openai.com/v1` / `gpt-4o-mini` | Optional LLM coach. **Empty = free, deterministic offline coach** (safe default). |
| `MAX_UPLOAD_BYTES` | `20971520` | Upload body cap. |

## Docker Compose (`./.env`, from `.env.example`)

`JWT_SECRET` (required), `PUBLIC_URL`, `PORT`, `TIMEZONE`, `AI_API_KEY`/`AI_BASE_URL`/`AI_MODEL`,
plus `DOMAIN` to enable the optional Caddy HTTPS profile. See `docs/DEPLOY_COLLEGE.md`.

## Legacy: Cloud Functions / Firebase CLI

`firebase/*` is kept on disk but no longer used by the app. Old `AI_*` function vars and
`firebase/functions/.env` remain for anyone testing the legacy path — see `docs/FIREBASE.md`.