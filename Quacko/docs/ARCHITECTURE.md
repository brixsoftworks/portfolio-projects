# Architecture

## Principles

1. **Server-authoritative rewards.** XP, streaks, levels, milestones, achievements,
   battles, votes and punishments are computed inside `@quacko/backend` services. The
   client sends intents (proof submissions, quiz answers, votes), never final numbers.
2. **One backend, every host.** Demo mode, the self-hosted server, and (legacy) Cloud
   Functions all construct the backend the same way: `createBackend(aiProvider, { store })`.
   Different `Store` and `AIProvider` implementations swap in without touching service code.
3. **No fake production logic.** Demo mode is a real execution of the real backend over an
   in-memory store. It is not a mock of business rules.

## Runtime shapes

```
┌─────────────────────────────────────────────────────────────────────┐
│ self-hosted server (apps/server) — Express 5 + better-sqlite3      │
│   POST /api/v1/auth/{register,login}  → { token, profile }         │
│   GET  /api/v1/auth/me                → profile (JWT required)     │
│   POST /api/v1/rpc   { method, args } → { data } (JWT required)    │
│   POST /api/v1/uploads + /uploads/*   → proof media                │
│   GET  /                              → exported Expo web app      │
│   backend = createBackend(ai, { store: SqliteStore, timezone })    │
└─────────────────────────────────────────────────────────────────────┘
             ▲ REST / JSON-RPC (JWT: scrypt password + HS256 token)
             │
┌────────────┴────────────┐        ┌──────────────────────────────┐
│ Expo app (apps/mobile)  │        │ web build (same app, served  │
│ real mode: @quacko/client│        │ by the server → "website")   │
│ demo mode: createDemoBackend │   └──────────────────────────────┘
└─────────────────────────┘
```

- **@quacko/client** (`packages/client`) is the single RPC contract: `rpcMethodNames`
  (~40 methods) + `RpcApi = Pick<Backend, ...>`. The server builds its allow-list and the
  mobile app its HTTP client from that same list, so the surface can't drift.
- `uid` is **never** sent by the client for own-data calls; the server injects it from the
  JWT. `getGoal`/`getMission`/streak reads are ownership-narrowed server-side.
- Docker builds the site with `expo export --platform web` and the server with esbuild
  (single `lib/index.cjs`). See `Dockerfile` and `docs/DEPLOY_COLLEGE.md`.

## Packages by dependency order

```
types         ← used by everything, no deps
validation    ← zod contracts shared by backend + AI + over-the-wire
domain        ← pure engines (streak, level, quiz, mission, proof, ...)
ai            ← AIProvider interface + DemoProvider + http provider
backend       ← Store interface, InMemoryStore, services, facade
client        ← rpcMethodNames / RpcApi / createHttpBackend / auth helpers
activity / proof / learning   ← thin client-side helpers
ui            ← design system (Expo components)
apps/mobile   ← Expo app (demo or @quacko/client)
apps/server   ← self-hosted REST backend (Express + SQLite + static web)
firebase/*    ← LEGACY (kept on disk, no longer used by the app)
```

## Backend layers

### Store + transactions
- `Store.find/get/newId` + `transaction(fn)` in `packages/backend/src/store.ts`.
- `InMemoryStore` (demo) and `SqliteStore` (apps/server, better-sqlite3 with a single
  `kv(collection, id, doc)` table, WAL, async tx mutex, `BEGIN IMMEDIATE/COMMIT/ROLLBACK`)
  enforce the same invariants: create-conflict and atomic transactions.

### Services
Each service file is a set of pure-ish async functions taking `(ctx, uid, input)`:

| File | Responsibilities |
| --- | --- |
| `goals.ts` | create/update/list goals, plan generation, milestone materialization |
| `missions.ts` | generation with idempotency keys, lifecycle, proof submit/verify, `okMissionCycle` |
| `learning.ts` | material/chunk ingestion, plans, lessons, quiz generation, lesson proof |
| `activity.ts` | live sessions, GPS route pruning, auto-submit proof on end |
| `social.ts` | groups, chat, battles + ticks, punishments + votes, coach messages |
| `notifications.ts` | preferences, device connections, in-app notification items |
| `birthday.ts` | morning coverage checks (used by the scheduled check in `apps/server`) |

### Facade
`createBackend(ai, options)` returns one object with typed methods. `apps/server`
wraps it in the `buildRpcHandlers` allow-list; the demo app binds it directly.

## The golden reward path (`okMissionCycle`)
1. Verify the proof is trusted (auto rules, AI verify, or peer votes).
2. Advance the streak with grace days then shields, breaking only when both are spent.
3. Compute XP (base × level multiplier + comeback + perfect-day bonus) into the ledger.
4. Recompute level buckets, progress goal %, unlock milestones/achievements atomically.
5. Emit notifications and, in friends mode, a group event.

This function is the single writer for streaks/levels/XP — see `missions.ts`.

## Auth
- Passwords: `crypto.scrypt` (per-user salt, constant-time compare) in `apps/server/src/auth.ts`.
- Sessions: HS256 JWTs, 30-day TTL, verified from the `Authorization: Bearer` header.

## Clients
- **Demo:** `apps/mobile/src/lib/demo.ts` → `createBackend` over `InMemoryStore`.
- **Real:** `apps/mobile/src/lib/api.ts` → `createHttpBackend({ baseUrl, getToken })`;
  auth state lives in `apps/mobile/src/state/auth.ts` (token persisted via AsyncStorage).

## Testing philosophy
Engines are pure and unit-tested. Backend services are integration-tested against
`InMemoryStore` + `DemoProvider`. The self-hosted server is integration-tested with
supertest over `SqliteStore(':memory:')` (`apps/server/test/app.test.ts`) and smoke-tested
against a live process (`apps/server/scripts/smoke.mjs`). Playwright e2e exercises the
exported web app in demo mode (see `docs/TESTING.md`).