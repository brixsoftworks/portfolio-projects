# Firebase (LEGACY)

> **Deprecated.** The app now runs on the self-hosted server (`apps/server`) — see
> `docs/DEPLOY_COLLEGE.md`. The Firestore/functions path below is kept working on disk
> for reference but is no longer wired into `apps/mobile`.

## Config files
- `firebase/firebase.json` — rules/indexes wiring, functions source, emulator ports.
- `firebase/firestore.rules` — locked down by default; only user-owned reads
  (proofs, notifications, own profile) are allowed. All writes flow through functions
  (admin SDK bypasses rules).
- `firebase/firestore.indexes.json` — composite indexes used by the store queries.
- `firebase/storage.rules` — public mascot assets + per-user proof media paths.
- `firebase/functions/*` — the deployment.

## Collections
`userProfiles`, `onboardingStates`, `goals`, `goalMilestones`, `missions`,
`proofs`, `streaks` (id `${userId}:${goalId}`), `xpLedger`, `levels`,
`userAchievements`, `conceptMastery`, `quizzes`, `quizAttempts`, `learningMaterials`,
`learningMaterialChunks`, `learningTopics`, `learningPlans`, `lessons`,
`activitySessions`, `groups`, `groupMembers`, `messages`, `battles`, `battleTicks`,
`punishments`, `punishmentVotes`, `notifications`, `notificationPreferences`,
`deviceConnections`.

## Functions
`firebase/functions/src/index.ts` exports one `onCall` per backend method with
`callerUid` → `assertUser`, mapping backend errors to HTTP codes:

| Backend error | Code |
| --- | --- |
| `NotFoundError` | `not-found` |
| `UnauthorizedError` | `permission-denied` |
| `ValidationFailure` | `invalid-argument` |
| `ConflictError` | `already-exists` |
| (other) | `internal` |

Plus:
- `dailyMissions` — `onSchedule('every day 00:10')` that regenerates mission coverage.
- `debugHealth` — reports which AI provider is active.

The AI provider is chosen at runtime: `AI_API_KEY` present → HTTP provider, else
`DemoProvider` (so a fresh deploy is safe by default).

## FirestoreStore
`firebase/functions/src/firestoreStore.ts` adapts the `Store` interface to
`firebase-admin` Firestore including `runTransaction` semantics. `create` maps to
`transaction.set(docRef, doc, { merge: false })` + conflict detection; the backend's
idempotency keys make mission generation safe against the 00:10 scheduler.

## Deploy / emulate
```bash
# emulator
npx firebase emulators:start --only firestore,storage,functions,auth

# deploy
npx firebase deploy --only functions,firestore:rules,firestore:indexes,storage
```
Point the app at the emulator with `EXPO_PUBLIC_FUNCTIONS_EMULATOR=127.0.0.1:5001`
(demo mode off).