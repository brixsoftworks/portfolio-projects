import { LEVEL_BASE_XP, LEVEL_MULTIPLIER, xpForLevel, type LevelState } from '@quacko/types';

/** Compute the level state from a running total XP. Pure and server-authoritative. */
export function levelFromTotalXp(totalXp: number): LevelState {
  let level = 1;
  let remaining = totalXp;
  while (remaining >= xpForLevel(level)) {
    remaining -= xpForLevel(level);
    level += 1;
  }
  const need = xpForLevel(level);
  return {
    id: '',
    userId: '',
    level,
    totalXp,
    xpIntoLevel: remaining,
    xpForNext: need,
    updatedAt: new Date(0).toISOString(),
  };
}

export { LEVEL_BASE_XP, LEVEL_MULTIPLIER, xpForLevel };