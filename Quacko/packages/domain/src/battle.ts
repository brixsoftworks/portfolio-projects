import { clamp, round1 } from './streak';

/**
 * Battle / punishment voting verified purely.
 * Approval happens when votesFor / councilSize crosses the threshold.
 */
export function approval(reached: { votesFor: number; votesAgainst: number }, threshold: number): boolean {
  const total = reached.votesFor + reached.votesAgainst;
  if (total === 0) return false;
  return round1(reached.votesFor / total) >= threshold;
}

export function battleOutcomes(me: number, other: number): 'win' | 'loss' | 'draw' {
  if (me > other) return 'win';
  if (me < other) return 'loss';
  return 'draw';
}

/** Split battle XP between winner and loser (draw splits evenly). */
export function battleXp(pool: number, me: number, other: number): { mine: number; theirs: number } {
  if (me === other) return { mine: Math.floor(pool / 2), theirs: Math.ceil(pool / 2) };
  const winnerShare = 0.7;
  const win = me > other;
  return {
    mine: Math.round(pool * (win ? winnerShare : 1 - winnerShare)),
    theirs: Math.round(pool * (win ? 1 - winnerShare : winnerShare)),
  };
}

/** Basic pace validity for a GPS run "kill" check. */
export function plausiblePace(avgPaceSecPerKm: number | null, minMps: number, maxMps: number): boolean {
  if (avgPaceSecPerKm == null) return false;
  const avgMps = 1000 / avgPaceSecPerKm;
  return avgMps >= minMps && avgMps <= maxMps;
}

export function elapsedMinutes(elapsedSeconds: number): number {
  return clamp(Math.round(elapsedSeconds / 60), 0, 24 * 60);
}