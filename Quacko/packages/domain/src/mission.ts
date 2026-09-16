import type { Mission, MissionStatus, ProofType, Schedule } from '@quacko/types';
import { isScheduledDay, localDayKey } from './streak';

export interface DayContext {
  now: Date;
  timezone: string;
}

/**
 * Pure "what should today's mission state be" resolution.
 * Missions become unavailable once their due day has passed without proof.
 */
export function resolveMissionStatus(mission: Mission, ctx: DayContext): MissionStatus {
  if (mission.status === 'verified' || mission.status === 'failed' || mission.status === 'expired') {
    return mission.status;
  }
  if (mission.status === 'proof_pending' && mission.dueAt && ctx.now.toISOString() <= mission.dueAt) {
    return 'proof_pending';
  }
  const today = localDayKey(ctx.now, ctx.timezone);
  if (mission.dueDay && mission.dueDay < today && mission.status !== 'proof_pending') {
    return 'expired';
  }
  return mission.status;
}

/** Idempotent per-user-per-goal-per-day key. */
export function instanceKey(goalId: string, day: string): string {
  return `${goalId}:${day}`;
}

/** Deterministic UTC end-of-day for a day key (server uses this as dueAt). */
export function endOfDayUtc(key: string): string {
  return `${key}T23:59:59.999Z`;
}

/** Next scheduled day keys for a goal from the given local day key. */
export function nextScheduledDayKeys(fromKey: string, count: number, schedule: Pick<Schedule, 'cadence' | 'days'>): string[] {
  const out: string[] = [];
  let attempt = 0;
  let current = fromKey;
  while (out.length < count && attempt < 400) {
    current = addCalendarDay(current);
    attempt += 1;
    if (isScheduledDay(current, schedule)) out.push(current);
  }
  return out;
}

function addCalendarDay(key: string): string {
  const [y, m, d] = key.split('-').map(Number);
  const dt = new Date(Date.UTC(y as number, (m as number) - 1, (d as number) + 1, 12, 0, 0));
  return dt.toISOString().slice(0, 10);
}

// Re-exported Mission types used by the engine for callers' convenience.
export type { Mission, MissionStatus, ProofType };