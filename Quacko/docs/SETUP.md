# Setup

## Requirements
- Node.js **24** (tested with 24.18)
- npm **11** (no yarn/pnpm/bun used in this repo)
- Docker (optional — only for the e2e suite and the self-hosted deploy)

## Install
```bash
npm install            # better-sqlite3 + esbuild postinstall are auto-approved
                       # via "trustedDependencies" in the root package.json
```
Two quirks of this toolchain to be aware of:

1. **No `workspace:` protocol.** This npm build resolves local workspace packages via
   `"*"`. All `@quacko/*` deps use `"*"`.
2. **React peer conflict.** React 19 vs `@types/react` requires
   `legacy-peer-deps=true` (already set in root `.npmrc`).

## Verify
```bash
npm run typecheck   # tsc over all packages + apps/server + apps/mobile
npm test            # domain engines, backend golden path, server integration (supertest)
```

## Run the app (demo mode)
```bash
npm run dev -w @quacko/mobile
```
No API keys needed. Create a demo goal on the Today tab and complete a mission to see
the full streak/XP cycle.

## Run the self-hosted server locally
```bash
npm run dev -w @quacko/server          # starts on http://127.0.0.1:8787
node apps/server/scripts/smoke.mjs     # end-to-end smoke against a live process
```
Serve the website too by pointing `WEB_DIR` at an exported web build:

```bash
npm run e2e:build                      # expo export --platform web → apps/mobile/dist
WEB_DIR=../../apps/mobile/dist npm run dev -w @quacko/server
```

## Run the app against the real server
1. Create `apps/mobile/.env` from `.env.example` and set `EXPO_PUBLIC_DEMO_MODE=0` plus
   `EXPO_PUBLIC_API_URL` (empty for same-origin web).
2. Start the server (above) — or deploy it with `docs/DEPLOY_COLLEGE.md`.
3. `npm run dev -w @quacko/mobile` and register an account.

## End-to-end tests (Playwright)
```bash
npm run e2e   # builds the web export, then runs 20 tests × desktop + mobile
```
Needs Docker: `mcr.microsoft.com/playwright:v1.62.1-noble` via `--network host`. See
`docs/TESTING.md`.

## Formatting
Prettier is configured at the repo root; format with `npx prettier --write .`.