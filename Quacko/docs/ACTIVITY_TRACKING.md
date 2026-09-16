# Activity Tracking

## Providers (`packages/activity`)
`ActivityDataProvider` interface with three implementations:

- `MockActivityProvider` — deterministic synthetic route for demo/CI.
- `NativeActivityProvider` — wraps `expo-location` watchPosition, requested via
  `createNativeActivityProvider(kind)`. Only the native app is supported (web is not).
- `createMockProvider(kind, samples|null)` — default in demo mode.

Providers stream `ActivitySample { lat, lng, t, speedMps, accuracyM }` and emit
finalize snapshots.

## Domain (`packages/domain/src/activity.ts`)
Pure math used to close a session:

- `haversineM(a, b)` — meters between samples.
- `routeDistance(route)` — sum of segments.
- `paceSecPerKm(meters, seconds)` — pace.
- `pruneRoute(route, maxPoints)` — downsamples so a long run stays a small document.
- `speedOK`, `accuracyThreshold` guards against implausible GPS telemetry.

## Session lifecycle (`packages/backend/src/activity.ts`)
1. `startActivity` — creates a `live` session with a target from the kind definition
   (`DEFINITIONS`), owned by the user.
2. `activityCheckIn` — heartbeat upsert (keeps watch session alive).
3. `endActivity` — computes distance/pace, prunes the route, marks the session
   `completed`, then **auto-submits proof** if this session was linked to a mission in
   `proof_pending` status. The mission then flows through the normal verification path —
   the activity engine never awards XP directly.

## Background tracking
`expo-task-manager` + `expo-location` background location is configured; the live
tracking screen requests `WHILE_IN_USE` (iOS) — see `app.json`.