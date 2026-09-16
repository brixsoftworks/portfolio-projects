import type { EntityId, IsoDate } from './common';

export const UserRoleEnum = ['member', 'admin', 'moderator'] as const;
export type UserRole = (typeof UserRoleEnum)[number];

export interface UserProfile {
  id: EntityId;
  authUid: EntityId;
  username: string;
  displayName: string;
  tagline: string;
  avatarUrl: string | null;
  /** Quacko 'level title', e.g. 'High-energy achiever'. */
  levelTitle: string;
  timezone: string;
  hasSeenOnboarding: boolean;
  mode: 'solo' | 'friends';
  /** Switches which rule set is used for streak grace/shields. */
  challengeRules: 'standard' | 'relaxed' | 'strict';
  createdAt: IsoDate;
  updatedAt: IsoDate;
  pushEnabled: boolean;
  email: string | null;
}

export interface OnboardingState {
  id: EntityId;
  uid: EntityId;
  step: 'welcome' | 'auth' | 'meet_quacko' | 'areas' | 'goal' | 'profile' | 'permissions' | 'plan' | 'done';
  selectedAreas: string[];
  completed: boolean;
  completedAt: IsoDate | null;
  updatedAt: IsoDate;
}

export const defaultLevelTitles: Record<number, string> = {
  1: 'Fresh Ducky',
  5: 'Streak Sprinter',
  10: 'High-Energy Achiever',
  15: 'Discipline Dealer',
  20: 'Quack Authority',
  30: 'Legendary Duck',
  50: 'Quacko Maximus',
};