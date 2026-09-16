import type { BackendCtx } from './ctx';
import type { StreakState, Goal } from '@quacko/types';

/**
 * Checks mission coverage "birthday" each morning (in the goal timezone).
 * A convenience used by demo seeding and scheduled functions to generate
 * the day's missions at local midnight.
 */
export class BirthdayTracker {
  constructor(private readonly ctx: BackendCtx) {}

  /** Returns goals that have an active streak still pending today. */
  async pendingToday(): Promise<{ goal: Goal; streak: StreakState }[]> {
    const goals = await this.ctx.store.find<Goal>('goals', { where: [{ field: 'status', equals: 'active' }] });
    const out: { goal: Goal; streak: StreakState }[] = [];
    for (const goal of goals) {
      const streak = await this.ctx.store.get<StreakState>('streaks', `${goal.ownerId}:${goal.id}`);
      if (streak) out.push({ goal, streak });
    }
    return out;
  }

  /** Generate today's missions; returns created count. */
  async generateNow(): Promise<number> {
    const { generateDailyMissions } = await import('./missions');
    const created = await generateDailyMissions(this.ctx);
    return created.length;
  }
}

export async function trackBirthdays(_ctx: BackendCtx): Promise<void> {
  // Placeholder for the scheduled function; real impl dispatches push reminders.
}