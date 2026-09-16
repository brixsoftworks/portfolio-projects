# Release

## Versioning & build
- App version in `apps/mobile/app.json` (`version: 0.1.0`, Expo SDK 57).
- Workspace packages bump independently; update `"*"` references stay declarative.

## Bundle for stores
```bash
npx expo prebuild --clean       # ios/ + android/ native projects
npx expo run:ios|run:android    # local build (or eas build)
```
`npx expo export --platform ios,android` produces JS bundles for CDN/app checking.
CI guard: `npm run typecheck && npm test` before any tag/release.

## Production prerequisites
1. Deploy functions + rules + indexes (see `docs/FIREBASE.md`).
2. Set `AI_API_KEY` (+ `AI_MODEL`/`AI_BASE_URL`) in the functions runtime — without it,
   production falls back to `DemoProvider` (deterministic, safe, but non-generative).
3. Point the app at production via `EXPO_PUBLIC_DEMO_MODE=0` + firebase web config.
4. Seed the `mascots` public folder; verify storage rules allow `public/**` reads.
5. Stand up the 00:10 `dailyMissions` schedule and App Check enforcement for callables.

## App Store checklist
- [ ] Icon/splash replaced from design package (currently template assets).
- [ ] Mascot assets licensed/commercially clear.
- [ ] Location usage descriptions (`NSLocationWhenInUseUsageDescription`, Android
      permissions) reviewed.
- [ ] Privacy nutrition label (location + photo/video proof uploads).
- [ ] Content rating: no real money gambling (punishments are faux); "battles" label it
      as peer challenge, not cash stakes.

## Backend gaps to close before GA (tracked in docs/completion notes)
- `gameSessions`/`gameScores`/`DailyWord` game service.
- Achievement rules table (currently hardcoded in `okMissionCycle`).
- Storage/media proof verification queue (currently vote-driven).
- Push notification scheduling (notifications are stored in-app today).