import type { EntityId, IsoDate } from './common';

export const ProofTypeEnum = [
  'gps',
  'quiz',
  'timer',
  'health_data',
  'photo',
  'video',
  'audio',
  'screenshot',
  'code_tests',
  'manual_log',
] as const;
export type ProofType = (typeof ProofTypeEnum)[number];

export const ProofStateEnum = [
  'not_required',
  'pending',
  'submitted',
  'processing',
  'verified',
  'rejected',
  'expired',
] as const;
export type ProofState = (typeof ProofStateEnum)[number];

export type ProofVerifier =
  | 'auto'
  | 'ai'
  | 'peer'
  | 'group_council'
  | 'admin';

export interface Proof {
  id: EntityId;
  missionId: EntityId;
  goalId: EntityId;
  userId: EntityId;
  type: ProofType;
  state: ProofState;
  metadata: Record<string, unknown>;
  /** Server-side summary of what was verified, never raw client flags. */
  verifier: ProofVerifier | null;
  verifiedAt: IsoDate | null;
  rejectedReason: string | null;
  /** e.g. quiz score, distance achieved, timer seconds. */
  result: Record<string, unknown> | null;
  createdAt: IsoDate;
  updatedAt: IsoDate;
  /** One-time claim token so the same proof cannot be used for two missions. */
  claimToken: string | null;
}

export interface ProofSubmission {
  missionId: EntityId;
  type: ProofType;
  metadata: Record<string, unknown>;
  /** URL uploaded to private storage (filled by the upload step, never trusted). */
  mediaUrl: string | null;
}

export const AUTO_VERIFIED_TYPES: ReadonlySet<ProofType> = new Set([
  'gps',
  'quiz',
  'timer',
  'code_tests',
  'health_data',
  'manual_log',
]);