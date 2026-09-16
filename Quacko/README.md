# QUACKO — Don't Break the Streak 🦆

A Neon Tokyo–themed accountability and streak app. Set a goal, show up daily, submit
proof, and never let the chain break. Quacko coaches you, runs 1v1 streak battles with
friends, convenes a punishment council, and learns from your uploaded material.

The app is built as a monorepo of small, independently-typed packages over one shared
**server-authoritative backend**. The exact same backend services run inside a dev-only
demo mode (in-memory + deterministic demo AI), in the **self-hosted production server**
(Express + SQLite + JWT, `apps/server`), and straight from the git clone you can throw on
any college box — see `docs/DEPLOY_COLLEGE.md`.

## Quickstart
> **Note**:  legacy-peer-deps=true is currently set in .npmrc to suppress peer dependency conflicts. This masks real incompatibilities. Consider removing it and resolving conflicts properly.

```bash
npm install
npm run typecheck   # all packages + apps/server + apps/mobile
npm test            # domain engines + backend golden path + server integration
npm run dev -w @quacko/server   # optional: the self-hosted backend (http://127.0.0.1:8787)
npm run dev -w @quacko/mobile   # Expo dev server (demo mode by default)
```

Demo mode needs no keys: `EXPO_PUBLIC_DEMO_MODE=1` (default) boots the backend over an
in-memory store with the deterministic demo coach. Set `EXPO_PUBLIC_DEMO_MODE=0` (and
optionally `EXPO_PUBLIC_API_URL`) to talk to the self-hosted server, which also serves the
**website**: an `expo export --platform web` build served from the same origin, login and
register built in.

## Repository layout

| Path | What it is |
| --- | --- |
| `packages/types` | Shared entity types, enums, XP/level tables |
| `packages/validation` | Zod schemas: every function input + AI output contract |
| `packages/domain` | Pure engines: streak, level, quiz, mission, proof, activity, battle, social |
| `packages/ai` | `AIProvider` interface, `DemoProvider`, OpenAI-compatible HTTP provider |
| `packages/backend` | The one backend: `Store` interface, `InMemoryStore`, all services, `createBackend` |
| `packages/client` | RPC contract + `createHttpBackend` REST client + auth helpers |
| `packages/activity` | Activity data providers (mock + native GPS) |
| `packages/proof` | Proof-type descriptors + payload builders |
| `packages/learning` | Mastery helpers and weak-area ranking |
| `packages/ui` | Neon Tokyo design system (theme, components) |
| `apps/mobile` | Expo SDK 57 app (`@quacko/mobile`) — demo or real via `@quacko/client` |
| `apps/server` | Self-hosted backend + website (`@quacko/server`): Express, SQLite, JWT, RPC, uploads |
| `firebase/*` | **Legacy** Cloud Functions + Firestore adapter (no longer used) |
| `assets/mascots` | Rendered Quacko mascot/avatar images from the design package |
| `docs/` | Deep-dive docs (see below) |

## The core loop

```
createGoal → ai.generatePlan → generateDailyMissions
  → startMission → finishMission → submitProof
  → verify (auto/AI/peer) → okMissionCycle  ← single server-authoritative reward path
     (streak, grace days, shields, XP, level, milestones, achievements, notifications)
```

Client code never awards XP or manipulates streaks. It calls backend methods; the backend
decides. See `docs/ARCHITECTURE.md` and `packages/backend/src/missions.ts` (`okMissionCycle`).

## Design

All UI follows the approved Neon Tokyo design package (the bundled design zip at repo
root). Screens re-theme the yellow Streak System flows while keeping their copy and
structure. Design tokens and the Material-Symbol→glyph map live in
`packages/ui/src/theme.ts`.

## Docs

- [Architecture](docs/ARCHITECTURE.md)
- [Setup](docs/SETUP.md)
- [Deploy to a college server (free self-hosting)](docs/DEPLOY_COLLEGE.md)
- [Environment variables](docs/ENVIRONMENT.md)
- [Firebase (legacy)](docs/FIREBASE.md)
- [AI providers & prompts](docs/AI.md)
- [Activity tracking](docs/ACTIVITY_TRACKING.md)
- [Proof system](docs/PROOF_SYSTEM.md)
- [Learning](docs/LEARNING.md)
- [Social & battles](docs/SOCIAL.md)
- [Security](docs/SECURITY.md)
- [Testing](docs/TESTING.md)
- [Release & store submission](docs/RELEASE.md)

## License

Private project.