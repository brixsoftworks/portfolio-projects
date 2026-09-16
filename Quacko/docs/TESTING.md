# Testing

## Stack
- **Vitest** — unit + backend integration across the npm workspaces.
- **Playwright** — browser E2E (QA + automated UI/UX review) against the exported Expo
  web build, in `e2e/`.

```bash
npm run typecheck                              # strict tsc for every package + app
npm test                                       # vitest unit/integration
npm run e2e                                    # export web build + run Playwright
```

## E2E (Playwright)

### How it runs
`apps/mobile` exports a static web build (`npm run e2e:build`, `CI=1 expo export
--platform web`) into `apps/mobile/dist`. `e2e/playwright.config.ts` serves that build
(`e2e/serve.mjs`) and runs two projects — desktop (1280×900) and mobile (iPhone 13
viewport) — against the **demo backend** (in-memory store, deterministic AI). State
resets per page load, so each test exercises a fresh first-run flow.

### Test suites
| Suite | Covers |
| --- | --- |
| `onboarding.spec.ts` | splash → routing, 3-step onboarding, area picker, empty state |
| `qa.spec.ts` | golden path (goal → missions → start → proof → verified → streak/XP), lifecycle guards, chat, explore, profile |
| `uiux.spec.ts` | tab navigation, no cross-tab bleed, no uncaught errors, dark theme, keyboard/a11y semantics, mobile overflow |

Selectors use `data-testid` (RN-web maps `testID` → `data-testid`) for critical nodes:
`create-goal`, `mission-row-*`, `mission-back`/`mission-start`/`mission-done`, `header-streak`,
`backdrop`.

### Running locally
Playwright needs Chromium system deps. On this machine there is no passwordless `sudo`,
so the suite is run inside the official Playwright container (`docker` group is
available):

```bash
docker run --rm --network host \
  -v "$PWD:/work:z" -w /work \
  mcr.microsoft.com/playwright:v1.62.1-noble \
  npx playwright test -c e2e/playwright.config.ts
```

`:z` is required on SELinux hosts. With `sudo npx playwright install-deps chromium`
available, plain `npm run e2e` works instead.

### Notable issues caught + fixed
- **Tab scenes bled into each other on web.** RN-screens disables itself on web
  (`ENABLE_SCREENS = Platform.OS !== 'web'`), so `bottom-tabs` fell back to plain Views
  and inactive tabs never got `display: none` — stale screens painted behind the active
  tab and intercepted taps. Fix: `enableScreens(true)` at app boot
  (`apps/mobile/src/app/_layout.tsx`) so `Screen.web.js` hides inactive scenes. Guarded
  by the "no cross-tab bleed" test.
- **Today's streak/missions went stale** after completing a mission: nothing refreshed on
  tab focus, the flame stayed at 0 and the row kept "available". Fix: `useFocusEffect`
  refresh + recompute streak on `missions` change in
  `apps/mobile/src/app/(tabs)/index.tsx`.
- **Mission screen had no way back** on web (modal, `headerShown: false`). Fix: explicit
  Back button on `apps/mobile/src/app/mission/[id].tsx`.

## Domain engines (pure)
`packages/domain/test/*` cover the tape engines:

- **streak** — first-ever day, contiguous days, same-day re-verify (no double count),
  gap day consuming grace, grace pool exhausted → shield consumed, both spent → break,
  comeback reset to 1, and the scheduling helpers (`isScheduledDay` vs cadence).
- **engines** — level curves (`levelFromTotalXp`, buckets/bonus), battle reward
  splits, proof auto-verify minimums (GPS floor, timer floor, quiz pass).

## Backend golden path (integration)
`packages/backend/test/cycle.test.ts` builds the real backend over `InMemoryStore` +
`DemoProvider` with a fixed clock and asserts a complete flow:

1. `createGoal` → plan with milestones,
2. `generateDailyMissions` returns today's missions,
3. `startMission` → `finishMission` → `submitProof` (GPS) → auto-verified,
4. streak = 1, XP recorded, level bucket recomputed, progress updated,
5. a **wrong** proof (type mismatch) is rejected with no reward,
6. second-day mission submits → streak = 2 (demonstrates contiguity math end-to-end).

## Functions
`firebase/functions` keeps `tsc --noEmit` + `esbuild` bundle as its gate; the Firestore
adapter is exercised implicitly through the same golden path when deployed (rules are
enforced by the emulator in CI before release).

## Manual smoke (mobile)
Run `npm run dev -w @quacko/mobile` in demo mode: create a goal → verify onboarding →
complete today's mission → watch streak/XP update on Today + Profile.