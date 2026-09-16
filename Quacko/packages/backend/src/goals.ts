import type { BackendCtx } from './ctx';
import type {
  Goal,
  GoalAIPlan,
  GoalMilestone,
  UserProfile,
} from '@quacko/types';
import { z } from 'zod';
import { nextScheduledDayKeys } from '@quacko/domain/src/mission';
import { localDayKey } from '@quacko/domain/src/streak';
import { assertDoc, assertInput, assertUser, isOwner } from './ctx';
import { createGoalInput, updateGoalInput, createGoalAIInput } from '@quacko/validation';

export async function createGoal(
  ctx: BackendCtx,
  rawUid: unknown,
  rawInput: unknown,
): Promise<Goal> {
  const uid = assertUser(rawUid);
  const input = assertInput(rawInput, createGoalInput);
  const now = ctx.now();
  const id = ctx.store.newId();
  const goal: Goal = {
    id,
    ownerId: uid,
    title: input.title,
    description: input.description,
    category: input.category,
    status: 'active',
    target: input.target,
    deadline: input.deadline ?? null,
    dailyAvailabilityMinutes: input.dailyAvailabilityMinutes,
    schedule: { ...input.schedule, timezone: input.schedule.timezone },
    difficulty: input.difficulty,
    proofRequired: input.proofRequired,
    aiPlan: null,
    progress: 0,
    currentMilestoneIndex: 0,
    createdAt: now.toISOString(),
    updatedAt: now.toISOString(),
    pausedAt: null,
    planStatus: 'idle',
  };
  await ctx.store.transaction(async (tx) => {
    await tx.create('goals', goal);
  });
  return goal;
}

/** AI-plan generation. Marks planStatus generating then persists the validated plan. */
export async function generateGoalPlan(ctx: BackendCtx, rawUid: unknown, goalIdRaw: unknown): Promise<GoalAIPlan> {
  const uid = assertUser(rawUid);
  const goalId = assertInput(goalIdRaw, z.string().min(1));
  const goal = assertDoc(await ctx.store.get<Goal>('goals', goalId), 'goal');
  isOwner(goal, uid);

  await ctx.store.transaction(async (tx) => {
    await tx.update<Goal>('goals', goalId, { planStatus: 'generating', updatedAt: ctx.now().toISOString() });
  });

  const plan = await ctx.ai.generatePlan({
    title: goal.title,
    description: goal.description,
    category: goal.category,
    target: goal.target,
    deadline: goal.deadline,
    dailyAvailabilityMinutes: goal.dailyAvailabilityMinutes,
    difficulty: goal.difficulty,
    proofRequired: goal.proofRequired,
    timezone: goal.schedule.timezone,
  });

  const milestones: GoalMilestone[] = plan.milestones.map((m, i) => ({
    id: ctx.store.newId(),
    goalId,
    index: i,
    title: m.title,
    description: m.description,
    progressThreshold: m.index / Math.max(1, plan.totalDays),
    status: i === 0 ? 'active' : 'locked',
    completedAt: null,
  }));

  await ctx.store.transaction(async (tx) => {
    await tx.update<Goal>('goals', goalId, {
      aiPlan: plan,
      planStatus: 'ready',
      currentMilestoneIndex: 0,
      updatedAt: ctx.now().toISOString(),
    });
    for (const m of milestones) await tx.create('goalMilestones', m);
  });
  return plan;
}

export async function updateGoal(ctx: BackendCtx, rawUid: unknown, goalId: unknown, rawPatch: unknown): Promise<Goal> {
  const uid = assertUser(rawUid);
  const patch = assertInput(rawPatch, updateGoalInput);
  const goal = assertDoc(await ctx.store.get<Goal>('goals', String(goalId)), 'goal');
  isOwner(goal, uid);
  const next = await ctx.store.transaction(async (tx) => {
    const g = await tx.update<Goal>('goals', goal.id, { ...patch, updatedAt: ctx.now().toISOString() });
    return assertDoc(g, 'goal');
  });
  return next;
}

export async function listGoals(ctx: BackendCtx, rawUid: unknown): Promise<Goal[]> {
  const uid = assertUser(rawUid);
  return ctx.store.find<Goal>('goals', { where: [{ field: 'ownerId', equals: uid }] });
}

export async function getUserProfile(ctx: BackendCtx, rawUid: unknown): Promise<UserProfile> {
  const uid = assertUser(rawUid);
  const profile = assertDoc(await ctx.store.get<UserProfile>('userProfiles', uid), 'user profile');
  return profile;
}

export function scheduledDayKeysForGoal(goal: Goal, from: Date, count: number): string[] {
  return nextScheduledDayKeys(localDayKey(from, goal.schedule.timezone), count, goal.schedule);
}

export type { GoalAIPlan };

// Keep the AI input schema referenced so tree-shaking does not drop it.
void createGoalAIInput;