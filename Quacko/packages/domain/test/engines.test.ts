import { describe, expect, it } from 'vitest';
import { gradeQuiz, updateMastery, weaknessScore } from '../src/quiz';
import { levelFromTotalXp, xpForLevel } from '../src/level';
import { approval, battleXp, battleOutcomes } from '../src/battle';
import { autoVerify } from '../src/proof';
import { haversineM, paceSecPerKm, routeDistance } from '../src/activity';
import { nextScheduledDayKeys, resolveMissionStatus, endOfDayUtc } from '../src/mission';

describe('gradeQuiz', () => {
  it('grades with pass threshold 0.7', () => {
    const r = gradeQuiz([0, 1, 2, 3], [0, 1, 2, 3]);
    expect(r.score).toBe(1);
    expect(r.passed).toBe(true);
    const p = gradeQuiz([0, 1, 0, 1], [0, 1, 2, 3]);
    expect(p.score).toBe(0.5);
    expect(p.passed).toBe(false);
  });
  it('rejects mismatched length', () => {
    const r = gradeQuiz([0, 1], [0]);
    expect(r.passed).toBe(false);
  });
});

describe('updateMastery', () => {
  it('correct answer raises mastery toward 1 by 0.2', () => {
    const r = updateMastery({ mastery: 0.4, attempts: 1, correct: 1 }, true);
    expect(r.mastery).toBe(0.6);
    expect(r.attempts).toBe(2);
  });
  it('wrong answer pulls mastery down but never below 0', () => {
    const r = updateMastery({ mastery: 0.1, attempts: 1, correct: 1 }, false);
    expect(r.mastery).toBe(0);
  });
  it('weaknessScore ranks low mastery with few attempts highest', () => {
    expect(weaknessScore(0.1, 1)).toBeGreaterThan(weaknessScore(0.9, 5));
  });
});

describe('levelFromTotalXp', () => {
  it('climbs levels by cumulative thresholds', () => {
    const lvl2 = levelFromTotalXp(xpForLevel(1));
    expect(lvl2.level).toBe(2);
    const lvl4 = levelFromTotalXp(xpForLevel(1) + xpForLevel(2) + xpForLevel(3));
    expect(lvl4.level).toBe(4);
  });
  it('accounts overflow into next level', () => {
    const lvl = levelFromTotalXp(xpForLevel(1) + 10);
    expect(lvl.level).toBe(2);
    expect(lvl.xpIntoLevel).toBe(10);
  });
});

describe('approval', () => {
  it('passes when for/total crosses threshold', () => {
    expect(approval({ votesFor: 3, votesAgainst: 1 }, 0.6)).toBe(true);
    expect(approval({ votesFor: 2, votesAgainst: 2 }, 0.6)).toBe(false);
    expect(approval({ votesFor: 0, votesAgainst: 0 }, 0.6)).toBe(false);
  });
});

describe('battleXp', () => {
  it('winner gets 70% of pool', () => {
    const r = battleXp(100, 5, 2);
    expect(r.mine).toBe(70);
    expect(r.theirs).toBe(30);
  });
  it('draw splits evenly', () => {
    const r = battleXp(101, 5, 5);
    expect(r.mine).toBe(50);
    expect(r.theirs).toBe(51);
  });
  it('battleOutcomes picks win/loss/draw', () => {
    expect(battleOutcomes(3, 1)).toBe('win');
    expect(battleOutcomes(1, 3)).toBe('loss');
    expect(battleOutcomes(2, 2)).toBe('draw');
  });
});

describe('autoVerify', () => {
  it('verifies GPS with sufficient distance', () => {
    const r = autoVerify('gps', { distanceMeters: 1500 });
    expect(r.verified).toBe(true);
  });
  it('rejects GPS short run', () => {
    const r = autoVerify('gps', { distanceMeters: 100 });
    expect(r.verified).toBe(false);
  });
  it('verifies passed quiz by server score', () => {
    const r = autoVerify('quiz', { score: 0.9 });
    expect(r.verified).toBe(true);
  });
});

describe('activity math', () => {
  it('haversine gives plausible distance for 1deg lat ~111km', () => {
    const m = haversineM({ lat: 0, lng: 0 }, { lat: 1, lng: 0 });
    expect(m).toBeGreaterThan(110000);
    expect(m).toBeLessThan(112000);
  });
  it('routeDistance sums segments', () => {
    const route = [
      { lat: 0, lng: 0, t: 0, accuracyM: 5, speedMps: null },
      { lat: 0, lng: 0.01, t: 1, accuracyM: 5, speedMps: null },
    ];
    const d = routeDistance(route);
    expect(d).toBeGreaterThan(1000);
    expect(d).toBeLessThan(1200);
  });
  it('pace converts to seconds per km', () => {
    expect(paceSecPerKm(1000, 360)).toBe(360);
    expect(paceSecPerKm(5000, 1500)).toBe(300);
    expect(paceSecPerKm(0, 100)).toBeNull();
  });
});

describe('mission scheduling', () => {
  it('generates contiguous scheduled days', () => {
    const keys = nextScheduledDayKeys('2026-01-01', 3, { cadence: 'daily', days: [] });
    expect(keys).toEqual(['2026-01-02', '2026-01-03', '2026-01-04']);
  });
  it('skips non-scheduled weekdays for weekends cadence', () => {
    const keys = nextScheduledDayKeys('2026-01-01', 2, { cadence: 'weekends', days: [] });
    expect(keys).toEqual(['2026-01-03', '2026-01-04']);
  });
  it('expires a mission whose due day is in the past without proof', () => {
    const mission = {
      id: 'm1', goalId: 'g1', ownerId: 'u1',
      title: 't', description: 'd', durationMinutes: 30,
      proofType: 'timer' as const, target: 'x',
      dueAt: '2026-01-01T23:59:59.999Z', dueDay: '2026-01-01',
      difficulty: 'easy' as const, status: 'available' as const,
      progress: 0, lessonId: null, concept: null, instanceOf: null,
      instanceKey: 'k', lockedReason: null,
      createdAt: '2026-01-01T00:00:00.000Z', updatedAt: '2026-01-01T00:00:00.000Z',
      completedAt: null, verifiedAt: null,
    };
    const status = resolveMissionStatus(mission, { now: new Date('2026-01-03T10:00:00Z'), timezone: 'UTC' });
    expect(status).toBe('expired');
  });
  it('endOfDayUtc is deterministic', () => {
    expect(endOfDayUtc('2026-06-15')).toBe('2026-06-15T23:59:59.999Z');
  });
});