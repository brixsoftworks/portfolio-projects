import type { EntityId, IsoDate } from './common';

export const NotificationCategoryEnum = [
  'mission_reminder',
  'streak_safe',
  'streak_broken',
  'check_in',
  'battle',
  'chat',
  'group_event',
  'punishment',
  'comeback',
  'achievement',
  'system',
] as const;
export type NotificationCategory = (typeof NotificationCategoryEnum)[number];

export interface NotificationItem {
  id: EntityId;
  userId: EntityId;
  category: NotificationCategory;
  title: string;
  body: string;
  data: Record<string, string>;
  read: boolean;
  createdAt: IsoDate;
}

export interface NotificationPreference {
  userId: EntityId;
  missionReminder: { enabled: boolean; timeMinutes: number };
  streak: { enabled: boolean };
  checkIn: { enabled: boolean; timeMinutes: number };
  group: { enabled: boolean };
  battle: { enabled: boolean };
  punishment: { enabled: boolean };
  achievement: { enabled: boolean };
}

export interface DeviceConnection {
  id: EntityId;
  userId: EntityId;
  pushToken: string | null;
  platform: 'ios' | 'android' | 'web';
  lastSeenAt: IsoDate;
}

export interface AuditLog {
  id: EntityId;
  at: IsoDate;
  action: string;
  actor: EntityId;
  target: EntityId | null;
  payload: Record<string, unknown>;
}