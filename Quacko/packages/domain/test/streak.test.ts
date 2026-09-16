import { describe, expect, it } from 'vitest';
import {
  advanceStreak,
  localDayKey,
  localMidnightMs,
  nextDay,
  yesterday,
} from '../src/streak';

describe('localDayKey', () => {
  it('formats a UTC instant in a western timezone with previous calendar day', () => {
    const d = new Date('2026-01-02T01:00:00Z');
    expect(localDayKey(d, 'America/New_York')).toBe('2026-01-01');
  });
  it('keeps same calendar day in UTC+ fusing timezone', () => {
    const d = new Date('2026-01-02T01:00:00Z');
    expect(localDayKey(d, 'Europe/Paris')).toBe('2026-01-02');
  });
});

describe('localMidnightMs', () => {
  it('is a multiple of 24h at UTC', () => {
    const d = new Date('2026-01-02T01:00:00Z');
    const ms = localMidnightMs(d, 'UTC');
    expect(ms % (24 * 60 * 60 * 1000)).toBe(0);
  });
});

describe('advanceStreak', () => {
  const base = {
    currentStreak: 0,
    longestStreak: 0,
    successfulDays: 0,
    brokenCount: 0,
    shields: 1,
    remainingGraceDays: 2,
    lastVerifiedDay: null,
    lastBreakDay: null,
  };

  it('starts a fresh streak', () => {
    const r = advanceStreak(base, '2026-01-01');
    expect(r.currentStreak).toBe(1);
    expect(r.advanced).toBe(true);
    expect(r.comeback).toBe(false);
  });

  it('extends a contiguous streak', () => {
    const a = advanceStreak(base, '2026-01-01');
    const b = advanceStreak({ ...base, ...a }, '2026-01-02');
    expect(b.currentStreak).toBe(2);
  });

  it('consumes a grace day on a gap, without breaking', () => {
    const a = advanceStreak(base, '2026-01-01');
    const b = advanceStreak({ ...base, ...a }, '2026-01-03');
    expect(b.currentStreak).toBe(2);
    expect(b.remainingGraceDays).toBe(1);
    expect(b.brokenCount).toBe(0);
  });

  it('consumes a shield next, still without breaking', () => {
    const a = advanceStreak(base, '2026-01-01');
    const b = advanceStreak({ ...base, ...a }, '2026-01-03');
    const c = advanceStreak({ ...base, ...b }, '2026-01-05');
    expect(c.currentStreak).toBe(3);
    expect(c.shields).toBe(0);
  });

  it('breaks the streak and flags a comeback when protections are gone', () => {
    const a = advanceStreak(base, '2026-01-01');
    const b = advanceStreak({ ...base, ...a }, '2026-01-03');
    const c = advanceStreak({ ...base, ...b }, '2026-01-05');
    const d = advanceStreak({ ...base, ...c }, '2026-01-07');
    expect(d.currentStreak).toBe(1);
    expect(d.brokenCount).toBe(1);
    expect(d.comeback).toBe(true);
  });

  it('same-day update advances but only counts once per day', () => {
    const a = advanceStreak(base, '2026-01-01');
    const b = advanceStreak({ ...base, ...a }, '2026-01-01');
    expect(b.currentStreak).toBe(1);
    expect(b.successfulDays).toBe(2);
  });
});

describe('day helpers', () => {
  it('yesterday/next are symmetric', () => {
    expect(nextDay('2026-03-01')).toBe('2026-03-02');
    expect(yesterday('2026-03-02')).toBe('2026-03-01');
  });
  it('handles month boundary and leap year', () => {
    expect(nextDay('2026-02-28')).toBe('2026-03-01');
    expect(nextDay('2028-02-28')).toBe('2028-02-29');
  });
});