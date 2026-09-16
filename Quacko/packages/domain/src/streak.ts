import type { Schedule } from '@quacko/types';

/**
 * Pure date/streak math. All functions are deterministic and timezone-aware;
 * the timezone is injected so engines can be unit tested without a clock.
 */

/** Format a Date in the given IANA timezone as YYYY-MM-DD. */
export function localDayKey(date: Date, timezone: string): string {
  const parts = new Intl.DateTimeFormat('en-CA', {
    timeZone: timezone,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).formatToParts(date);
  const map: Record<string, string> = {};
  for (const p of parts) map[p.type] = p.value;
  return `${map.year ?? '1970'}-${map.month ?? '01'}-${map.day ?? '01'}`;
}

/** Epoch ms at local start-of-day (00:00) of `date` in `timezone`. */
export function localMidnightMs(date: Date, timezone: string): number {
  const key = localDayKey(date, timezone);
  const [y, m, d] = key.split('-').map(Number);
  return Date.UTC(y as number, (m as number) - 1, d as number, 0, 0, 0, 0);
}

export function addDays(key: string, days: number): string {
  const [y, m, d] = key.split('-').map(Number);
  const dt = new Date(Date.UTC(y as number, (m as number) - 1, (d as number) + days, 12, 0, 0));
  return dt.toISOString().slice(0, 10);
}

export function yesterday(key: string): string {
  return addDays(key, -1);
}

export function nextDay(after: string): string {
  return addDays(after, 1);
}

type ScheduleShape = Pick<Schedule, 'cadence' | 'days'>;

export function isScheduledDay(key: string, schedule: ScheduleShape): boolean {
  if (schedule.cadence === 'daily') return true;
  const idx = new Date(`${key}T12:00:00Z`).getUTCDay();
  const names = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'] as const;
  const name = names[idx] ?? 'sun';
  switch (schedule.cadence) {
    case 'weekdays':
      return !name.startsWith('s');
    case 'weekends':
      return name === 'sat' || name === 'sun';
    case 'custom':
      return schedule.days.includes(name);
    default:
      return true;
  }
}

interface StreakUpdateResult {
  currentStreak: number;
  longestStreak: number;
  successfulDays: number;
  brokenCount: number;
  shields: number;
  remainingGraceDays: number;
  lastVerifiedDay: string;
  lastBreakDay: string | null;
  /** True when today's successful day extends the streak. */
  advanced: boolean;
  /** True when the streak was previously broken, i.e. this is a comeback day. */
  comeback: boolean;
  /** Period bonus flag (earned while the streak is alive). */
  perfectDay: boolean;
}

export interface StreakConfig {
  graceDays: number;
  shields: number;
  comebackDay: number;
}

export const DEFAULT_STREAK_CONFIG: StreakConfig = { graceDays: 2, shields: 1, comebackDay: 1 };

export interface StreakInput {
  currentStreak: number;
  longestStreak: number;
  successfulDays: number;
  brokenCount: number;
  shields: number;
  remainingGraceDays: number;
  lastVerifiedDay: string | null;
  lastBreakDay: string | null;
}

/**
 * Advance a streak state when a mission verifies on `day`.
 * Chain rule: successive days must be contiguous by the local day key. A gap
 * consumes one protection layer (grace days, then a shield when the grace pool
 * empties, then a shield directly); once both are gone the streak breaks and
 * the day counts as a comeback restart.
 */
export function advanceStreak(prev: StreakInput, day: string): StreakUpdateResult {
  const contiguity = prev.lastVerifiedDay != null && yesterday(day) === prev.lastVerifiedDay;
  const sameDay = prev.lastVerifiedDay === day;
  const firstEver = prev.lastVerifiedDay == null;

  let current = prev.currentStreak;
  let brokenCount = prev.brokenCount;
  let shields = prev.shields;
  let remainingGraceDays = prev.remainingGraceDays;
  let lastBreakDay = prev.lastBreakDay;
  let comeback = false;

  if (firstEver) {
    current = 1;
  } else if (!contiguity && !sameDay) {
    if (remainingGraceDays > 0) {
      remainingGraceDays -= 1;
      if (remainingGraceDays === 0) shields = Math.max(0, shields - 1);
    } else if (shields > 0) {
      shields -= 1;
    } else {
      current = 0;
      brokenCount += 1;
      lastBreakDay = prev.lastVerifiedDay;
      comeback = true;
    }
    if (current === 0) current = 1;
    else current += 1;
  } else if (contiguity) {
    current += 1;
  }

  const longest = Math.max(prev.longestStreak, current);

  return {
    currentStreak: current,
    longestStreak: longest,
    successfulDays: prev.successfulDays + 1,
    brokenCount,
    shields,
    remainingGraceDays,
    lastVerifiedDay: day,
    lastBreakDay,
    advanced: contiguity || firstEver,
    comeback,
    perfectDay: !comeback,
  };
}

/** XP bonus for a perfect (no-break) day. */
export function perfectDayBonus(streak: number): number {
  return streak >= 3 ? 100 : 50;
}

/** Effective daily XP including level multiplier. */
export function xpWithMultiplier(baseXp: number, level: number): number {
  return Math.round(baseXp * (1 + (level - 1) * 0.02));
}

export function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

export function round1(v: number): number {
  return Math.round(v * 10) / 10;
}