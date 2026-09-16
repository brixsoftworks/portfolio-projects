import type {
  Cadence,
  Difficulty,
  EntityId,
  GoalCategory,
  IsoDate,
  Schedule,
} from './common';
import type { ProofType } from './proof';

export const GoalStatusEnum = [
  'active',
  'planning',
  'paused',
  'archived',
  'completed',
  'failed',
] as const;
export type GoalStatus = (typeof GoalStatusEnum)[number];

export interface GoalMilestone {
  id: EntityId;
  goalId: EntityId;
  index: number;
  title: string;
  description: string;
  /** 0..1 target progress at which this milestone unlocks. */
  progressThreshold: number;
  status: 'locked' | 'active' | 'completed';
  completedAt: IsoDate | null;
}

export interface GoalPlanDay {
  dayIndex: number;
  title: string;
  durationMinutes: number;
  focus: string;
  proofType: ProofType;
  concept?: string;
}

export interface GoalAIPlan {
  summary: string;
  totalDays: number;
  cadence: Cadence;
  difficulty: Difficulty;
  generatedAt: IsoDate;
  source: 'ai' | 'manual';
  days: GoalPlanDay[];
  milestones: { title: string; description: string; index: number }[];
}

export interface Goal {
  id: EntityId;
  ownerId: EntityId;
  title: string;
  description: string;
  category: GoalCategory;
  status: GoalStatus;
  target: string;
  deadline: IsoDate | null;
  dailyAvailabilityMinutes: number;
  schedule: Schedule;
  difficulty: Difficulty;
  proofRequired: boolean;
  aiPlan: GoalAIPlan | null;
  progress: number; // 0..1
  currentMilestoneIndex: number;
  createdAt: IsoDate;
  updatedAt: IsoDate;
  pausedAt: IsoDate | null;
  /** Set when an AI plan is being generated. */
  planStatus: 'idle' | 'generating' | 'ready' | 'failed';
}

export const MissionStatusEnum = [
  'locked',
  'available',
  'started',
  'paused',
  'completed',
  'proof_pending',
  'verified',
  'failed',
  'expired',
] as const;
export type MissionStatus = (typeof MissionStatusEnum)[number];

export interface Mission {
  id: EntityId;
  goalId: EntityId;
  ownerId: EntityId;
  title: string;
  description: string;
  durationMinutes: number;
  proofType: ProofType;
  target: string;
  /** Due endpoint for the day in UTC. */
  dueAt: IsoDate | null;
  /** Exact local day the mission belongs to (YYYY-MM-DD) in the user's timezone. */
  dueDay: string;
  difficulty: Difficulty;
  status: MissionStatus;
  progress: number; // 0..1
  /** Server-authoritative lesson/quiz reference when proofType === quiz. */
  lessonId: EntityId | null;
  concept: string | null;
  instanceOf: EntityId | null;
  /** Idempotency key computed server-side to avoid duplicate generation. */
  instanceKey: string | null;
  lockedReason: 'insufficient_xp' | 'previous_pending' | 'schedule_limit' | 'goal_paused' | null;
  createdAt: IsoDate;
  updatedAt: IsoDate;
  completedAt: IsoDate | null;
  verifiedAt: IsoDate | null;
}

export interface GoalProgressEvent {
  id: EntityId;
  goalId: EntityId;
  day: string;
  xpDelta: number;
  source: 'mission_verified' | 'quiz' | 'activity' | 'manual';
  at: IsoDate;
}