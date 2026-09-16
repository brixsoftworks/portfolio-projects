import type { EntityId, IsoDate } from './common';

export const ChatMessageKindEnum = [
  'text',
  'mission_verified',
  'user_join',
  'battle_challenge',
  'poker_bet',
  'group_event',
  'ai_comment',
  'punishment_verdict',
  'comeback',
] as const;
export type ChatMessageKind = (typeof ChatMessageKindEnum)[number];

export interface ChatMessage {
  id: EntityId;
  groupId: EntityId;
  authorId: EntityId;
  authorName: string;
  authorAvatar: string | null;
  kind: ChatMessageKind;
  text: string | null;
  createdAt: IsoDate;
  /** Server incrementing for pages. */
  seq: number;
}

export const GroupEventKindEnum = [
  'created',
  'member_joined',
  'member_left',
  'battle_started',
  'battle_finished',
  'game_started',
  'punishment_announced',
] as const;
export type GroupEventKind = (typeof GroupEventKindEnum)[number];

export interface ChatCardData {
  kind: ChatMessageKind;
  entityId: EntityId;
  title: string;
  subtitle: string;
  emoji: string;
}

export interface Chat {
  id: EntityId;
  groupId: EntityId;
  createdAt: IsoDate;
  membersNextMarker: number;
}

export interface Group {
  id: EntityId;
  name: string;
  description: string;
  emoji: string;
  ownerId: EntityId;
  memberCount: number;
  invitationCode: string;
  createdAt: IsoDate;
  /** Room settings the server enforces (stakes, reminders). */
  settings: {
    defaultStakesPoints: number;
    punishmentEnabled: boolean;
    batteryVersion: 'bq4' | 'bq5';
  };
}

export interface GroupMember {
  groupId: EntityId;
  userId: EntityId;
  username: string;
  avatarUrl: string | null;
  joinedAt: IsoDate;
  role: 'member' | 'admin';
  status: 'active' | 'left';
  balance: number;
}

export const BattleStatusEnum = [
  'pending',
  'active',
  'finished',
  'aborted',
  'forfeited',
] as const;
export type BattleStatus = (typeof BattleStatusEnum)[number];

export interface Battle {
  id: EntityId;
  groupId: EntityId;
  challengeeId: EntityId;
  challengerId: EntityId;
  killCriteria: string;
  timeLimitSeconds: number;
  stakesPoints: number;
  status: BattleStatus;
  punishments: EntityId[];
  outcome: 'kill' | 'time_limit' | 'draw' | 'double_kill' | null;
  winnerId: EntityId | null;
  tickAt: IsoDate | null;
  createdAt: IsoDate;
  finishedAt: IsoDate | null;
}

export interface BattleTick {
  id: EntityId;
  battleId: EntityId;
  at: IsoDate;
  checkin1: boolean;
  checkin2: boolean;
  xp1: number;
  xp2: number;
}

export const PunishmentStatusEnum = [
  'proposed',
  'voting',
  'approved',
  'assigned',
  'in_progress',
  'proof_pending',
  'completed',
  'rejected',
  'expired',
] as const;
export type PunishmentStatus = (typeof PunishmentStatusEnum)[number];

export interface Punishment {
  id: EntityId;
  groupId: EntityId;
  targetUserId: EntityId;
  title: string;
  description: string;
  durationDays: number;
  severity: 'petty' | 'moderate' | 'grand';
  emoji: string;
  link: string | null;
  status: PunishmentStatus;
  proposerId: EntityId | null;
  councilSize: number;
  approvalThreshold: number; // fraction 0..1
  votesFor: number;
  votesAgainst: number;
  assignedDay: string;
  deadlineAt: IsoDate | null;
  proof: {
    accepted: boolean;
    verifiedAt: IsoDate | null;
    details: string | null;
  } | null;
  createdAt: IsoDate;
  updatedAt: IsoDate;
}

export interface PunishmentVote {
  id: EntityId;
  punishmentId: EntityId;
  voterId: EntityId;
  vote: 'for' | 'against';
  createdAt: IsoDate;
}

export interface MovingGroupEvent {
  id: EntityId;
  groupId: EntityId;
  kind: GroupEventKind;
  payload: Record<string, unknown>;
  happenedAt: IsoDate;
}