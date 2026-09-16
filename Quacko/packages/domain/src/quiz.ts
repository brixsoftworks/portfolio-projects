import { round1 } from './streak';

/** Server-side graded quiz. Input: correct answer indexes and user's selection. */
export function gradeQuiz(
  answers: readonly number[],
  selected: readonly number[],
): { score: number; passed: boolean; correctCount: number; total: number } {
  if (selected.length !== answers.length || answers.length === 0) {
    return { score: 0, passed: false, correctCount: 0, total: answers.length };
  }
  const correctCount = answers.reduce(
    (acc, correct, i) => acc + (selected[i] === correct ? 1 : 0),
    0,
  );
  const score = round1(correctCount / answers.length);
  return { score, passed: score >= 0.7, correctCount, total: answers.length };
}

/** Spaced-repetition style mastery update. */
export function updateMastery(
  prev: { mastery: number; attempts: number; correct: number },
  correct: boolean,
): { mastery: number; attempts: number; correct: number; lastCorrect: boolean } {
  const attempts = prev.attempts + 1;
  const correctCount = prev.correct + (correct ? 1 : 0);
  // Hebbian-ish delta: correct pulls 0.2, incorrect pulls 0.15 with memory.
  const delta = correct ? 0.2 : -0.15;
  const mastery = round1(Math.min(1, Math.max(0, prev.mastery + delta)));
  return { mastery, attempts, correct: correctCount, lastCorrect: correct };
}

/** A concept counts as mastered (locked→unlocked) at threshold. */
export function isMastered(mastery: number, threshold = 0.7): boolean {
  return mastery >= threshold;
}

export function weaknessScore(mastery: number, attempts: number): number {
  return round1((1 - mastery) * (1 + 1 / Math.max(1, attempts)));
}