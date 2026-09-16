import type { EntityId, IsoDate } from './common';

export const ActivityKindEnum = [
  'running',
  'walking',
  'cycling',
  'meditation',
  'reading',
  'coding',
  'sleep',
  'digital_wellbeing',
  'custom',
] as const;
export type ActivityKind = (typeof ActivityKindEnum)[number];

export const ActivitySessionStateEnum = [
  'idle',
  'requesting_permissions',
  'live',
  'paused',
  'interrupted',
  'completed',
  'cancelled',
  'failed',
] as const;
export type ActivitySessionState = (typeof ActivitySessionStateEnum)[number];

/** One captured GPS point. */
export interface RoutePoint {
  lat: number;
  lng: number;
  /** epoch ms */
  t: number;
  accuracyM: number;
  speedMps: number | null;
}

export interface ActivityDefinition {
  kind: ActivityKind;
  /** Narrative target, e.g. '5 km' or '15 min'. */
  target: string;
  targetUnits: 'distance_km' | 'duration_min' | 'steps' | 'sessions' | 'custom';
  targetValue: number;
  proofMethod: 'gps' | 'timer' | 'steps' | 'health' | 'manual' | 'code';
  durationMinutes: number;
}

export interface ActivitySession {
  id: EntityId;
  missionId: EntityId | null;
  userId: EntityId;
  kind: ActivityKind;
  state: ActivitySessionState;
  /** Reconstructable so an interrupted session can be resumed. */
  startedAt: IsoDate;
  elapsedSeconds: number;
  pausedAt: IsoDate | null;
  resumedAt: IsoDate | null;
  targetUnits: ActivityDefinition['targetUnits'];
  targetValue: number;
  distanceMeters: number;
  steps: number | null;
  avgPaceSecondsPerKm: number | null;
  route: RoutePoint[];
  /** Where proof/coordinates are persisted. */
  proofRef: EntityId | null;
  /** Server idempotency key (client generated, server validated). */
  sessionToken: string;
  updatedAt: IsoDate;
}

export interface ActivitySummary {
  kind: ActivityKind;
  totalDistanceM: number;
  totalDurationMinutes: number;
  totalSessions: number;
  lastSessionAt: IsoDate | null;
}