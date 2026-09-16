import type { EntityId, IsoDate } from './common';

export interface StreakState {
  id: EntityId;
  userId: EntityId;
  goalId: EntityId;
  currentStreak: number;
  longestStreak: number;
  successfulDays: number;
  brokenCount: number;
  shields: number;
  remainingGraceDays: number;
  /** YYYY-MM-DD in the user's timezone of the last verified day. */
  lastVerifiedDay: string | null;
  /** Fires once when a streak breaks. */
  lastBreakDay: string | null;
  updatedAt: IsoDate;
}

export interface CompleteAgainEvent {
  id: EntityId;
  userId: EntityId;
  goalId: EntityId;
  day: string;
  verifiedAt: IsoDate;
}

export interface XpLedgerEntry {
  id: EntityId;
  userId: EntityId;
  amount: number;
  reason: 'learning' | 'quiz' | 'activity' | 'perfect_day' | 'comeback' | 'battle' | 'game' | 'bonus';
  missionId: EntityId | null;
  createdAt: IsoDate;
}

export interface LevelState {
  id: EntityId;
  userId: EntityId;
  level: number;
  totalXp: number;
  xpIntoLevel: number;
  xpForNext: number;
  updatedAt: IsoDate;
}

export interface AchievementRule {
  id: EntityId;
  code: string;
  title: string;
  description: string;
  /** Predicate stored server-side. */
  kind: 'streak' | 'xp' | 'missions' | 'comeback' | 'battle' | 'game' | 'learning' | 'custom';
  threshold: number;
  icon: string;
  secret: boolean;
}

export interface UserAchievement {
  id: EntityId;
  userId: EntityId;
  ruleCode: string;
  unlockedAt: IsoDate;
}

export const XP_RULES = {
  learning: 50,
  quiz: 50,
  activity: 70,
  meditation: 50,
  perfectDay: 100,
  comeback: 200,
  battle: 150,
  game: 30,
} as const;

export const LEVEL_BASE_XP = 200;
export const LEVEL_MULTIPLIER = 1.35;

export function xpForLevel(level: number): number {
  return Math.round(LEVEL_BASE_XP * Math.pow(LEVEL_MULTIPLIER, level - 1));
}