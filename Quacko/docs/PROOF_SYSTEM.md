# Proof System

## Types
`proofTypes = gps | quiz | timer | health_data | photo | video | audio | screenshot | code_tests | manual_log`

Described in `packages/types/src/proof.ts`; `packages/proof` provides:
- `proofRequirement(mission)` → needs media, a GPS record, a timer, etc.
- `buildProofPayload(kind, metadata)` → canonical client payload.

## Trust tiers (`packages/domain/src/proof.ts`)
- **auto** — `autoVerify(type, metadata, rules)` verifies immediately:
  - `gps`: distance ≥ 1000 m (configurable), records distance + pace.
  - `timer`: duration ≥ 60 s.
  - `quiz`: server-computed score ≥ passing (0.7).
  - `health_data`: steps synced.
  - `manual_log`: explicit `confirm: true` (the weakest auto tier).
- **human** — photo/video/audio/screenshot/code_tests. Server marks proof `submitted`
  (`verifier: null`, `rejectedReason` unset), enqueues peer votes; `verifyProofHuman`
  flips to `verified`/`rejected`. Notifications drive the vote loop.
- **ai triage** — media types call `AIProvider.analyzeProof` for a verdict +
  confidence that seeds the vote queue automatically when confidence is high.

## Server flow (`missions.ts submitProof`)
1. Mission must be in a submittable state (`available | started | proof_pending`).
2. Type mismatch → rejected (`Expected <type> proof`).
3. `verifyProofAutomatic` decides auto vs submitted.
4. On `verified`, the golden path (`okMissionCycle`) fires once — streak, XP, level,
   progress, milestones, achievements. Client-supplied rewards are impossible.

## Anti-abuse
- Rewards only after verification; a mission can verify once (status transition).
- GPS minimums, timer minimums, plausible-pace checks, and proof-metadata coercion
  (`Number(metadata.x)`) keep clients from passing junk.
- Idempotent mission instance keys prevent duplicate day-generation at scheduler runs.