import type { ConceptMastery, WeakArea } from '@quacko/types';

export const MASTERY_THRESHOLD = 0.7;

export function isMastered(m: ConceptMastery | undefined): boolean {
  return (m?.mastery ?? 0) >= MASTERY_THRESHOLD;
}

/** Order concepts by weakness (low mastery + few attempts first). */
export function rankWeakAreas(masteries: ConceptMastery[]): WeakArea[] {
  return masteries
    .map((m) => ({
      ...m,
      weaknessScore: (1 - m.mastery) * (1 + 1 / Math.max(1, m.attempts)),
      locked: isMastered(m),
    }))
    .sort((a, b) => b.weaknessScore - a.weaknessScore);
}

export function progressPct(completedDays: number, totalDays: number): number {
  if (totalDays <= 0) return 0;
  return Math.round((Math.min(completedDays, totalDays) / totalDays) * 100);
}

export function minutesToLabel(minutes: number): string {
  if (minutes < 60) return `${minutes}m`;
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return m ? `${h}h ${m}m` : `${h}h`;
}