# Security

## Server authority
Rewards, XP, streaks, levels, milestones, achievements, battle wins and punishments are
computed exclusively in `@quacko/backend` services running server-side (Cloud Functions
in prod, in-process demo in dev). A client can request actions but cannot set values.

## Input validation
Every public backend method validates its input with a zod schema through
`assertInput<Schema>(input, schema): z.infer<Schema>` (`packages/backend/src/ctx.ts`).
Unknown fields, wrong types, and out-of-range values are rejected with
`ValidationFailure`. AI outputs are validated against their own contracts before any write.

## Ownership
Services are called with `(ctx, uid, ...)`: the authenticated caller's uid from
`assertUser` in functions, `DEMO_UID` in demo mode. Every read/write to a user-scoped
document confirms `ownerId === uid` (or explicit peer visibility). `UnauthorizedError` →
`permission-denied`.

## Firestore rules (`firebase/firestore.rules`)
Locked down by default: `match /{document=**} { allow read, write: if false; }`.
Admin-sdk function writes bypass rules anyway. Only user-owned reads are opened:
`proofs`, `notifications`, and one's own `userProfiles`. Storage is scoped to
`/users/{uid}/**` for writes and public mascots for reads.

## Proof integrity
- Client payloads are re-validated server-side; mission type mismatches are rejected.
- `autoVerify` minimums (GPS ≥ 1000 m, timer ≥ 60 s, quiz score ≥ 0.7) and metric
  coercion prevent garbage submissions.
- A mission verifies at most once, so double-submission cannot double-XP.
- Media types route through AI triage + the human vote queue.

## AI
Provider replies are schema-validated before acceptance (see `docs/AI.md`); malformed
model output can never corrupt state. Output is treated as untrusted data, not code.

## Secrets
`AI_API_KEY` and Firebase secrets live in the functions runtime env / secret manager —
never in the repo or client bundle. `EXPO_PUBLIC_*` client keys are Firebase public
config, not secrets. `.env*` and functions `.env` are gitignored.