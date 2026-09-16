import { describe, expect, it } from 'vitest';
import { DemoProvider } from '@quacko/ai';
import { createBackend } from '../src/backend';
import { InMemoryStore } from '../src/inMemory';
import type { Goal, Mission } from '@quacko/types';

const fixedNow = () => new Date('2026-01-02T10:00:00Z');

function makeBackend() {
  const store = new InMemoryStore();
  const backend = createBackend(new DemoProvider(), { store, now: fixedNow, timezone: 'UTC' });
  return { store, backend };
}

async function seedGoal(backend: ReturnType<typeof createBackend>) {
  const uid = 'user1';
  await backend.getOrCreateProfile(uid, { timezone: 'UTC' });
  const goal: Goal = await backend.createGoal(uid, {
    title: 'Run every day',
    description: 'Build an unbreakable running habit.',
    category: 'fitness',
    target: 'Run 5 km',
    dailyAvailabilityMinutes: 30,
    schedule: { cadence: 'daily', days: [], timezone: 'UTC' },
    difficulty: 'easy',
    proofRequired: true,
    deadline: '2026-02-01T00:00:00Z',
  });
  const plan = await backend.generateGoalPlan(uid, goal.id);
  return { uid, goal, plan };
}

describe('mission golden path', () => {
  it('createGoal -> plan -> missions -> proof -> verified streak/xp cycle', async () => {
    const { store, backend } = makeBackend();
    const { uid, goal } = await seedGoal(backend);

    const missions = await backend.generateDailyMissions();
    expect(missions.length).toBeGreaterThan(0);
    const mission = missions[0] as Mission;
    expect(mission.goalId).toBe(goal.id);
    expect(mission.proofType).toBe('gps');

    await backend.startMission(uid, { missionId: mission.id });
    await backend.finishMission(uid, { missionId: mission.id, percent: 100 });

    const proof = await backend.submitProof(uid, {
      missionId: mission.id,
      proof: { type: 'gps', metadata: { distanceMeters: 2500 }, mediaUrl: null },
    });
    expect(proof.state).toBe('verified');

    const streak = await store.get('streaks', `${uid}:${goal.id}`);
    expect((streak as { currentStreak: number })?.currentStreak).toBe(1);

    const level = await store.get('levels', uid);
    expect((level as { totalXp: number })?.totalXp).toBeGreaterThan(0);

    const goalAfter = await store.get<Goal>('goals', goal.id);
    expect(goalAfter?.progress).toBeGreaterThan(0);

    const ledger = await store.find('xpLedger', { where: [{ field: 'userId', equals: uid }] });
    expect(ledger.length).toBeGreaterThanOrEqual(1);
  });

  it('rejects a proof with the wrong type and keeps the mission unverified', async () => {
    const { backend } = makeBackend();
    const { uid } = await seedGoal(backend);
    const missions = await backend.generateDailyMissions();
    const mission = missions[0] as Mission;

    const proof = await backend.submitProof(uid, {
      missionId: mission.id,
      proof: { type: 'timer', metadata: { durationSeconds: 120 }, mediaUrl: null },
    });
    expect(proof.state).toBe('submitted');
    const fresh = await backend.finishMission(uid, {
      missionId: mission.id,
      percent: 100,
    });
    expect(fresh.status).toBe('proof_pending');
  });

  it('two verifications on consecutive days extend the streak to 2', async () => {
    let day = '2026-01-02T10:00:00Z';
    let current = 0;
    const store = new InMemoryStore();
    const backend = createBackend(new DemoProvider(), {
      store,
      now: () => new Date(day),
      timezone: 'UTC',
    });
    const { uid, goal } = await seedGoal(backend);

    for (const offset of [0, 1]) {
      day = `2026-01-${String(2 + offset).padStart(2, '0')}T10:00:00Z`;
      const missions = await backend.generateDailyMissions();
      const mission = missions.find((m) => m.goalId === goal.id) as Mission;
      await backend.finishMission(uid, { missionId: mission.id, percent: 100 });
      await backend.submitProof(uid, {
        missionId: mission.id,
        proof: { type: 'gps', metadata: { distanceMeters: 2500 }, mediaUrl: null },
      });
      const streak = await store.get('streaks', `${uid}:${goal.id}`);
      current = (streak as { currentStreak: number })?.currentStreak ?? 0;
    }
    expect(current).toBe(2);
  });
});