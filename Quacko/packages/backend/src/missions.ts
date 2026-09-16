import type { BackendCtx } from './ctx';
import {
  advanceStreak,
  DEFAULT_STREAK_CONFIG,
  perfectDayBonus,
  xpWithMultiplier,
} from '@quacko/domain/src/streak';
import { endOfDayUtc, instanceKey, nextScheduledDayKeys } from '@quacko/domain/src/mission';
import { gradeQuiz, updateMastery } from '@quacko/domain/src/quiz';
import type {
  Goal,
  Mission,
  Proof,
  StreakState,
  LevelState,
  XpLedgerEntry,
  GoalMilestone,
  UserAchievement,
  Quiz,
  QuizAttempt,
  ConceptMastery,
  UserProfile,
} from '@quacko/types';
import { XP_RULES, xpForLevel } from '@quacko/types';
import { assertDoc, assertInput, assertUser, isOwner } from './ctx';
import {
  finishMissionInput,
  sendProgressInput,
  setMissionProofInput,
  startMissionInput,
  submitQuizAttemptInput,
} from '@quacko/validation';
import { generateQuiz } from './learning';
import { createNotification } from './notifications';

const MISSION_CACHE_DAYS = 2;

/* ----------------------------- generation -------------------------------- */

function missionFromPlan(goal: Goal, day: string, dayIndex: number, ctx: BackendCtx): Mission {
  const planDay = goal.aiPlan?.days.find((d) => d.dayIndex === dayIndex);
  let proofType = goal.proofRequired ? 'manual_log' : 'manual_log';
  if (goal.aiPlan && planDay) proofType = planDay.proofType;
  else if (goal.category === 'fitness') proofType = 'gps';
  else if (goal.category === 'learning' || goal.category === 'knowledge') proofType = 'quiz';
  else if (goal.category === 'skills') proofType = 'code_tests';
  return {
    id: ctx.store.newId(),
    goalId: goal.id,
    ownerId: goal.ownerId,
    title: planDay?.title ?? `${goal.title} — day ${dayIndex}`,
    description: planDay?.focus ?? 'Consistent effort toward your goal.',
    durationMinutes: planDay?.durationMinutes ?? goal.dailyAvailabilityMinutes,
    proofType: proofType as Mission['proofType'],
    target: goal.target,
    dueAt: endOfDayUtc(day),
    dueDay: day,
    difficulty: goal.difficulty,
    status: 'available',
    progress: 0,
    lessonId: null,
    concept: planDay?.concept ?? null,
    instanceOf: null,
    instanceKey: instanceKey(goal.id, day),
    lockedReason: null,
    createdAt: ctx.now().toISOString(),
    updatedAt: ctx.now().toISOString(),
    completedAt: null,
    verifiedAt: null,
  };
}

/** Ensure upcoming days are covered for every active goal. Server-trigger friendly. */
export async function generateDailyMissions(ctx: BackendCtx): Promise<Mission[]> {
  const goals = await ctx.store.find<Goal>('goals', { where: [{ field: 'status', equals: 'active' }] });
  const created: Mission[] = [];
  for (const goal of goals) {
    const existing = await ctx.store.find<Mission>('missions', {
      where: [{ field: 'ownerId', equals: goal.ownerId }, { field: 'goalId', equals: goal.id }],
    });
    const existingKeys = new Set(existing.map((m) => m.instanceKey ?? m.id));
    const today = localDayFor(ctx, goal.schedule.timezone || 'UTC')
    const keys = nextScheduledDayKeys(today, MISSION_CACHE_DAYS, goal.schedule);
    let dayIndex = 1;
    for (const key of keys) {
      const sig = instanceKey(goal.id, key);
      if (existingKeys.has(sig)) continue;
      const mission = missionFromPlan(goal, key, dayIndex, ctx);
      dayIndex += 1;
      await ctx.store.transaction(async (tx) => {
        await tx.create('missions', mission);
      });
      created.push(mission);
      existingKeys.add(sig);
    }
  }
  return created;
}

/* ------------------------------ lifecycle -------------------------------- */

export async function listMissions(ctx: BackendCtx, rawUid: unknown): Promise<Mission[]> {
  const uid = assertUser(rawUid);
  return ctx.store.find<Mission>('missions', { where: [{ field: 'ownerId', equals: uid }] });
}

export async function startMission(ctx: BackendCtx, rawUid: unknown, rawInput: unknown): Promise<Mission> {
  const uid = assertUser(rawUid);
  const input = assertInput(rawInput, startMissionInput);
  const mission = assertDoc(await ctx.store.get<Mission>('missions', input.missionId), 'mission');
  isOwner(mission, uid);
  const next = await ctx.store.transaction(async (tx) => {
    return assertDoc(
      await tx.update<Mission>('missions', mission.id, {
        status: 'started',
        updatedAt: ctx.now().toISOString(),
      }),
      'mission',
    );
  });
  return next;
}

export async function sendProgress(ctx: BackendCtx, rawUid: unknown, rawInput: unknown): Promise<Mission> {
  const uid = assertUser(rawUid);
  const input = assertInput(rawInput, sendProgressInput);
  const mission = assertDoc(await ctx.store.get<Mission>('missions', input.missionId), 'mission');
  isOwner(mission, uid);
  const next = await ctx.store.transaction(async (tx) => {
    return assertDoc(
      await tx.update<Mission>('missions', mission.id, {
        progress: Math.min(1, Math.max(0, input.progress)),
        status: mission.status === 'available' || mission.status === 'locked' ? 'started' : mission.status,
        updatedAt: ctx.now().toISOString(),
      }),
      'mission',
    );
  });
  return next;
}

/** User taps "I did it" — marks proof_pending so the cycle can verify. */
export async function finishMission(ctx: BackendCtx, rawUid: unknown, rawInput: unknown): Promise<Mission> {
  const uid = assertUser(rawUid);
  const input = assertInput(rawInput, finishMissionInput);
  const mission = assertDoc(await ctx.store.get<Mission>('missions', input.missionId), 'mission');
  isOwner(mission, uid);
  const next = await ctx.store.transaction(async (tx) => {
    return assertDoc(
      await tx.update<Mission>('missions', mission.id, {
        progress: Math.min(1, Math.max(0, input.percent / 100)),
        status: 'proof_pending',
        updatedAt: ctx.now().toISOString(),
      }),
      'mission',
    );
  });
  return next;
}

/** Stores the proof submission. Auto-verified types verify immediately. */
export async function submitProof(ctx: BackendCtx, rawUid: unknown, rawInput: unknown): Promise<Proof> {
  const uid = assertUser(rawUid);
  const input = assertInput(rawInput, setMissionProofInput);
  const mission = assertDoc(await ctx.store.get<Mission>('missions', input.missionId), 'mission');
  isOwner(mission, uid);
  if (mission.status !== 'proof_pending' && mission.status !== 'started' && mission.status !== 'available') {
    throw new Error('mission not in a submittable state');
  }

  const proofId = ctx.store.newId();
  const now = ctx.now().toISOString();
  const auto = await verifyProofAutomatic(ctx, mission, input.proof.type, input.proof.metadata);

  const proof: Proof = {
    id: proofId,
    missionId: mission.id,
    goalId: mission.goalId,
    userId: uid,
    type: input.proof.type,
    state: auto.verified ? 'verified' : 'submitted',
    metadata: input.proof.metadata,
    verifier: auto.verified ? 'auto' : null,
    verifiedAt: auto.verified ? now : null,
    rejectedReason: auto.verified ? null : auto.reason,
    result: auto.verified ? auto.result : null,
    createdAt: now,
    updatedAt: now,
    claimToken: null,
  };

  await ctx.store.transaction(async (tx) => {
    await tx.create('proofs', proof);
    await tx.update<Mission>('missions', mission.id, {
      status: auto.verified ? 'verified' : 'proof_pending',
      progress: 1,
      completedAt: auto.verified ? now : null,
      verifiedAt: auto.verified ? now : null,
      updatedAt: now,
    });
  });

  if (auto.verified) {
    await okMissionCycle(ctx, mission, proof);
  }
  return proof;
}

export async function verifyProofHuman(
  ctx: BackendCtx,
  rawUid: unknown,
  proofId: unknown,
  decision: 'verified' | 'rejected',
  note: string,
): Promise<Proof> {
  assertUser(rawUid);
  const proof = assertDoc(await ctx.store.get<Proof>('proofs', String(proofId)), 'proof');
  const voted = await ctx.store.transaction(async (tx) => {
    if (decision === 'verified') {
      await tx.update<Proof>('proofs', proof.id, {
        state: 'verified',
        verifier: 'peer',
        verifiedAt: ctx.now().toISOString(),
        rejectedReason: null,
        updatedAt: ctx.now().toISOString(),
      });
    } else {
      await tx.update<Proof>('proofs', proof.id, {
        state: 'rejected',
        rejectedReason: note,
        updatedAt: ctx.now().toISOString(),
      });
    }
    return assertDoc(await tx.get<Proof>('proofs', proof.id), 'proof');
  });

  if (voted.state === 'verified') {
    const mission = assertDoc(await ctx.store.get<Mission>('missions', proof.missionId), 'mission');
    await okMissionCycle(ctx, mission, voted);
  }
  return voted;
}

/* --------------------------- the golden cycle ---------------------------- */

async function verifyProofAutomatic(
  _ctx: BackendCtx,
  mission: Mission,
  type: Proof['type'],
  metadata: Record<string, unknown>,
): Promise<{ verified: boolean; reason: string; result: Record<string, unknown> | null }> {
  if (mission.proofType !== type && mission.proofType !== 'manual_log') {
    return { verified: false, reason: `Expected ${mission.proofType} proof, got ${type}`, result: null };
  }
  if (type === 'quiz') {
    return { verified: true, reason: 'quiz references a passed attempt', result: {} };
  }
  switch (type) {
    case 'gps': {
      const meters = Number(metadata.distanceMeters ?? 0);
      return meters >= 1
        ? { verified: true, reason: `${Math.round(meters)}m recorded`, result: { distanceMeters: Math.round(meters) } }
        : { verified: false, reason: 'no distance recorded', result: null };
    }
    case 'timer': {
      const seconds = Number(metadata.durationSeconds ?? 0);
      return seconds >= 60
        ? { verified: true, reason: `${seconds}s focus`, result: { durationSeconds: seconds } }
        : { verified: false, reason: 'under a minute of focus', result: null };
    }
    case 'manual_log': {
      return metadata.confirm === true
        ? { verified: true, reason: 'manual confirmation', result: { confirmed: true } }
        : { verified: false, reason: 'manual confirmation missing', result: null };
    }
    default:
      return { verified: false, reason: 'requires human verification', result: null };
  }
}

/**
 * The one server-authoritative reward path: XP, streak, goal progress,
 * milestone/achievement unlocks. Only invoked after proof verification.
 */
export async function okMissionCycle(ctx: BackendCtx, mission: Mission, proof: Proof): Promise<void> {
  const now = ctx.now();
  const day = mission.dueDay || localDayFor(ctx, 'UTC');
  const goal = assertDoc(await ctx.store.get<Goal>('goals', mission.goalId), 'goal');
  const profile = (await ctx.store.get<UserProfile>('userProfiles', mission.ownerId)) ?? {
    id: mission.ownerId,
    authUid: mission.ownerId,
    username: 'you',
    displayName: 'You',
    tagline: '',
    avatarUrl: null,
    levelTitle: 'Fresh Ducky',
    timezone: 'UTC',
    hasSeenOnboarding: true,
    mode: 'solo',
    challengeRules: 'standard',
    createdAt: now.toISOString(),
    updatedAt: now.toISOString(),
    pushEnabled: false,
    email: null,
  };
  const level = (await ctx.store.get<LevelState>('levels', mission.ownerId)) ?? emptyLevel(mission.ownerId);

  const streakId = `${mission.ownerId}:${goal.id}`;
  const prevStreak = (await ctx.store.get<StreakState>('streaks', streakId)) ?? {
    userId: mission.ownerId,
    goalId: goal.id,
    currentStreak: 0,
    longestStreak: 0,
    successfulDays: 0,
    brokenCount: 0,
    shields: DEFAULT_STREAK_CONFIG.shields,
    remainingGraceDays: DEFAULT_STREAK_CONFIG.graceDays,
    lastVerifiedDay: null,
    lastBreakDay: null,
    updatedAt: now.toISOString(),
  };

  const streak = advanceStreak(prevStreak, day);

  const baseXp =
    proof.type === 'quiz' ? XP_RULES.quiz
      : proof.type === 'gps' ? XP_RULES.activity
      : proof.type === 'timer' ? XP_RULES.meditation
      : XP_RULES.learning;
  const xpGain =
    xpWithMultiplier(baseXp, level.level)
    + (streak.comeback ? XP_RULES.comeback : 0)
    + (streak.currentStreak >= 3 ? perfectDayBonus(streak.currentStreak) : 0);
  const totalXp = level.totalXp + xpGain;
  const xpLedger: XpLedgerEntry[] = [
    { id: ctx.store.newId(), userId: mission.ownerId, amount: xpWithMultiplier(baseXp, level.level), reason: 'learning', missionId: mission.id, createdAt: now.toISOString() },
  ];
  if (streak.comeback) {
    xpLedger.push({ id: ctx.store.newId(), userId: mission.ownerId, amount: XP_RULES.comeback, reason: 'comeback', missionId: mission.id, createdAt: now.toISOString() });
  }
  if (xpGain > (xpLedger[0]?.amount ?? 0)) {
    xpLedger.push({ id: ctx.store.newId(), userId: mission.ownerId, amount: xpGain - (xpLedger[0]?.amount ?? 0), reason: 'bonus', missionId: mission.id, createdAt: now.toISOString() });
  }

  const planDays = goal.aiPlan?.totalDays ?? 30;
  const newProgress = Math.min(1, goal.progress + 1 / Math.max(planDays, 1));
  let milestonesUnlocked = 0;
  const milestones = await ctx.store.find<GoalMilestone>('goalMilestones', { where: [{ field: 'goalId', equals: goal.id }] });
  for (const m of milestones) {
    if (m.status === 'locked' && newProgress >= m.progressThreshold) {
      await ctx.store.transaction(async (tx) => {
        await tx.update<GoalMilestone>('goalMilestones', m.id, { status: 'completed', completedAt: now.toISOString() });
      });
      milestonesUnlocked += 1;
    }
  }
  const newMilestoneIndex = Math.min(goal.currentMilestoneIndex + milestonesUnlocked, Math.max(milestones.length - 1, 0));
  const nextLevelState = recomputeLevel(totalXp);

  await ctx.store.transaction(async (tx) => {
    await tx.set('streaks', { id: streakId, ...streak, updatedAt: now.toISOString() });
    await tx.set<LevelState>('levels', { id: mission.ownerId, userId: mission.ownerId, ...nextLevelState, totalXp, updatedAt: now.toISOString() });
    for (const e of xpLedger) await tx.create<XpLedgerEntry>('xpLedger', e);
    await tx.update<Goal>('goals', goal.id, {
      progress: newProgress,
      currentMilestoneIndex: newMilestoneIndex,
      updatedAt: now.toISOString(),
    });
  });

  if (streak.currentStreak >= 7) await unlockAchievement(ctx, mission.ownerId, 'streak_7');
  if (nextLevelState.level > level.level) await unlockAchievement(ctx, mission.ownerId, 'level_up');

  await createNotification(ctx, mission.ownerId, 'achievement', 'Streak intact', `Day ${streak.currentStreak} verified for "${goal.title}".`, {
    goalId: goal.id,
    missionId: mission.id,
    streak: String(streak.currentStreak),
  });

  if (profile.mode === 'friends') {
    await groupEventFor(ctx, mission, goal);
  }
}

/** Pure recompute of level buckets from total XP. */
function recomputeLevel(totalXp: number): { level: number; xpIntoLevel: number; xpForNext: number } {
  let level = 1;
  let remaining = totalXp;
  while (remaining >= xpForLevel(level)) {
    remaining -= xpForLevel(level);
    level += 1;
  }
  return { level, xpIntoLevel: remaining, xpForNext: xpForLevel(level) };
}

export async function submitQuiz(
  ctx: BackendCtx,
  rawUid: unknown,
  rawInput: unknown,
): Promise<{ passed: boolean; score: number; masteryNow: number; xpGained: number }> {
  const uid = assertUser(rawUid);
  const input = assertInput(rawInput, submitQuizAttemptInput);
  const quiz = assertDoc(await ctx.store.get<Quiz>('quizzes', input.quizId), 'quiz');

  const answers = quiz.questions.map((q) => q.correctIndex);
  const graded = gradeQuiz(answers, input.selected);
  if (!graded.passed) {
    const masteryNow = await applyMasteryUpdate(ctx, uid, quiz, graded.correctCount / Math.max(1, graded.total));
    return { passed: false, score: graded.score, masteryNow, xpGained: 0 };
  }
  const attempt: QuizAttempt = {
    id: ctx.store.newId(),
    quizId: quiz.id,
    userId: uid,
    selected: input.selected,
    score: graded.score,
    passed: true,
    createdAt: ctx.now().toISOString(),
  };
  await ctx.store.transaction(async (tx) => {
    await tx.create('quizAttempts', attempt);
  });
  const masteryNow = await applyMasteryUpdate(ctx, uid, quiz, 1);
  await awardXp(ctx, uid, XP_RULES.quiz, quiz.goalId);
  return { passed: true, score: graded.score, masteryNow, xpGained: XP_RULES.quiz };
}

export async function awardXp(ctx: BackendCtx, uid: string, amount: number, goalId: string | null): Promise<void> {
  const level = (await ctx.store.get<LevelState>('levels', uid)) ?? emptyLevel(uid);
  const newTotal = level.totalXp + amount;
  const next = recomputeLevel(newTotal);
  await ctx.store.transaction(async (tx) => {
    await tx.create<XpLedgerEntry>('xpLedger', {
      id: ctx.store.newId(),
      userId: uid,
      amount,
      reason: 'quiz',
      missionId: null,
      createdAt: ctx.now().toISOString(),
    });
    await tx.set<LevelState>('levels', { id: uid, userId: uid, totalXp: newTotal, ...next, updatedAt: ctx.now().toISOString() });
  });
  if (goalId) {
    const goal = await ctx.store.get<Goal>('goals', goalId);
    if (goal) {
      await ctx.store.transaction(async (tx) => {
        await tx.update<Goal>('goals', goalId, { progress: Math.min(1, goal.progress + 0.01), updatedAt: ctx.now().toISOString() });
      });
    }
  }
}

async function applyMasteryUpdate(ctx: BackendCtx, uid: string, quiz: Quiz, correctness: number): Promise<number> {
  const concept = quiz.questions[0];
  if (!concept) return 0;
  const key = `${uid}:${quiz.materialId ?? 'x'}:${concept.concept}`;
  const prev = (await ctx.store.get<ConceptMastery>('conceptMastery', key)) ?? {
    userId: uid,
    materialId: quiz.materialId ?? 'x',
    conceptId: key,
    conceptName: concept.concept,
    mastery: 0,
    attempts: 0,
    correct: 0,
    lastCorrect: correctness >= 0.7,
    updatedAt: ctx.now().toISOString(),
  };
  const updated = updateMastery({ mastery: prev.mastery, attempts: prev.attempts, correct: prev.correct }, correctness >= 0.7);
  await ctx.store.transaction(async (tx) => {
    await tx.set<ConceptMastery>('conceptMastery', {
      id: key,
      userId: uid,
      materialId: quiz.materialId ?? 'x',
      conceptId: key,
      conceptName: concept.concept,
      mastery: updated.mastery,
      attempts: updated.attempts,
      correct: updated.correct,
      lastCorrect: updated.lastCorrect,
      updatedAt: ctx.now().toISOString(),
    });
  });
  return updated.mastery;
}

function emptyLevel(uid: string): LevelState {
  return { id: uid, userId: uid, level: 1, totalXp: 0, xpIntoLevel: 0, xpForNext: xpForLevel(1), updatedAt: new Date(0).toISOString() };
}

function localDayFor(ctx: BackendCtx, timezone: string): string {
  const tz = timezone || 'UTC';
  const parts = new Intl.DateTimeFormat('en-CA', { timeZone: tz, year: 'numeric', month: '2-digit', day: '2-digit' })
    .formatToParts(ctx.now())
    .reduce<Record<string, string>>((acc, p) => {
      if (p.type !== 'literal') acc[p.type] = p.value;
      return acc;
    }, {});
  return `${parts.year}-${parts.month}-${parts.day}`;
}

async function unlockAchievement(ctx: BackendCtx, uid: string, ruleCode: string): Promise<void> {
  const existing = await ctx.store.find<UserAchievement>('userAchievements', {
    where: [{ field: 'userId', equals: uid }, { field: 'ruleCode', equals: ruleCode }],
  });
  if (existing.length > 0) return;
  await ctx.store.transaction(async (tx) => {
    await tx.create<UserAchievement>('userAchievements', {
      id: ctx.store.newId(),
      userId: uid,
      ruleCode,
      unlockedAt: ctx.now().toISOString(),
    });
  });
}

async function groupEventFor(ctx: BackendCtx, mission: Mission, goal: Goal): Promise<void> {
  const members = await ctx.store.find<{ groupId: string; userId: string }>('groupMembers', {
    where: [{ field: 'userId', equals: mission.ownerId }],
  });
  for (const member of members) {
    await ctx.store.transaction(async (tx) => {
      await tx.create('messages', {
        id: ctx.store.newId(),
        groupId: member.groupId,
        authorId: 'quacko',
        authorName: 'Quacko',
        authorAvatar: null,
        kind: 'mission_verified',
        text: `Streak verified: ${goal.title}`,
        seq: Date.now(),
        createdAt: ctx.now().toISOString(),
      });
    });
  }
}

export { generateQuiz };
export type { StreakState, LevelState };