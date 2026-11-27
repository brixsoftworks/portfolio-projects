# Changelog

All notable changes to Strict Day.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to a milestone-based scheme.

## [Unreleased]

### Added

- **Android app shell** (Kotlin, Jetpack Compose, Material 3, Hilt, Room,
  DataStore, WorkManager).
  - Clean architecture: `domain` models + repository interfaces, `data`
    (Room entities/DAOs/mappers, repository impls, DataStore preferences),
    `enforcement`, `verification`, `planner`, `worker`, `ui` screens and
    viewmodels, `security`, and `di` (Hilt modules).
  - Product flow implemented as scaffold: SCHEDULE → LOCK → WORK → VERIFY →
    UNLOCK.
  - UI screens: onboarding, home, schedule, task editor, active task,
    verification, night planner, integrations, analytics, settings.
  - Navigation via Navigation Compose (`Screen` + `StrictDayNavHost`).
- **Schedule planner**: `PlannerEngine`, `ConstraintSolver`, `ScheduleValidator`.
  - Resolves sleep windows including those crossing midnight, reserves fixed
    commitments, prioritises tasks, and reports conflicts / unscheduled work.
- **Enforcement**: `EnforcementPolicy`, `EnforcementManager` +
  `AndroidEnforcementManager`, device-capability detection, app
  allow/block restriction via `DevicePolicyManager` when the device is a
  Device Owner, `StrictDayDeviceAdminReceiver`.
- **Verification** (honest model):
  - `DefaultRuleEvaluator` supporting count / exists / greater-than /
    less-than / equals / contains / duration / within-time-window operators.
  - Providers (github, google_docs, notion, fitness) return `NotConnected`
    until real credentials exist; no fabricated verification.
  - Server-authoritative verdicts: the device uploads evidence; the
    `verify-task` edge function evaluates rules server-side.
- **Background workers** (`@HiltWorker`): schedule activation, verification
  polling, and periodic sync.
- **Supabase backend scaffolding**:
  - `supabase/migrations/20260101000000_init.sql` — full schema with RLS on
    every table.
  - `supabase/functions/verify-task` — edge function evaluating rules on the
    server and recording to `verification_state` + `audit_events`.
  - `supabase/config.toml` and env examples.
- **Optional remote sync layer** (flag-gated, default off via
  `SUPABASE_SYNC_ENABLED`): `SupabaseClient` (Postgrest + Functions),
  `SupabaseSyncService` pushing schedules, tasks, and audit events,
  `SessionTokenStore`, and `SyncWorker` integration.
- **Tests**: 29 unit tests for `ConstraintSolver`, `ScheduleValidator`,
  `PlannerEngine`, and `DefaultRuleEvaluator`.
- Repo documentation: `README.md`, `.env.example`, `supabase/.env.example`.

### Notes

- `app-debug.apk` output: `app/build/outputs/apk/debug/`.
- Release build is minified/shrunk (proguard); signing is not configured, so
  release signing credentials are intentionally absent.
- Build system: Kotlin 2.1.0, AGP 8.7.3, Gradle 8.11.1, minSdk 26 / targetSdk 35.