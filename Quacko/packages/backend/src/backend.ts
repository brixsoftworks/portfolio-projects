import type { AIProvider } from '@quacko/ai';
import type { Store } from './store';
import type { BackendCtx } from './ctx';
import { InMemoryStore } from './inMemory';
import type { UserProfile, OnboardingState, Goal, Mission, StreakState, LevelState } from '@quacko/types';
import { DEFAULT_STREAK_CONFIG } from '@quacko/domain/src/streak';
import * as goals from './goals';
import * as missions from './missions';
import * as learning from './learning';
import * as activity from './activity';
import * as social from './social';
import * as notifications from './notifications';
import type {
  requestMaterialUploadInput,
  markMaterialUploadedInput,
  createLearningPlanInput,
  generateQuizInput,
  submitQuizAttemptInput,
  startActivityInput,
  endActivityInput,
  checkInActivityInput,
  createGroupInput,
  joinGroupInput,
  sendMessageInput,
  createBattleInput,
  tickBattleInput,
  resolveBattleInput,
  proposePunishmentInput,
  voteInput,
  requestCoachMessageInput,
  simulateGroupAIMessageInput,
  createGoalInput,
  updateGoalInput,
  setMissionProofInput,
  finishMissionInput,
} from '@quacko/validation';
import { BirthdayTracker, trackBirthdays } from './birthday';

export interface BackendOptions {
  store?: Store;
  now?: () => Date;
  timezone?: string;
  defaultLevelTitle?: string;
}

/** Create the full, wires-everything backend. Both Callable Functions and the
 *  in-process demo server share this exact entrypoint. */
export function createBackend(ai: AIProvider, options: BackendOptions = {}) {
  const store = options.store ?? new InMemoryStore();
  const now = options.now ?? (() => new Date());
  const ctx: BackendCtx = { store, ai, now };
  const timezone = options.timezone ?? 'UTC';

  return {
    ctx,
    store,
    ai,
    now,
    birthday: new BirthdayTracker(ctx),

    /* goals */
    createGoal: (uid: unknown, input: unknown) => goals.createGoal(ctx, uid, input),
    generateGoalPlan: (uid: unknown, goalId: unknown) => goals.generateGoalPlan(ctx, uid, goalId),
    updateGoal: (uid: unknown, goalId: unknown, patch: unknown) => goals.updateGoal(ctx, uid, goalId, patch),
    listGoals: (uid: unknown) => goals.listGoals(ctx, uid),
    getUserProfile: (uid: unknown) => goals.getUserProfile(ctx, uid),

    /* profile & onboarding */

    getOrCreateProfile: async (uid: string, partial: Partial<UserProfile> = {}): Promise<UserProfile> => {
      const existing = await store.get<UserProfile>('userProfiles', uid);
      if (existing) return existing;
      const nowIso = now().toISOString();
      const profile: UserProfile = {
        id: uid,
        authUid: uid,
        username: partial.username ?? `ducky_${uid.slice(0, 6)}`,
        displayName: partial.displayName ?? 'Quacko Member',
        tagline: partial.tagline ?? 'High-energy achiever in training',
        avatarUrl: partial.avatarUrl ?? null,
        levelTitle: partial.levelTitle ?? options.defaultLevelTitle ?? 'Fresh Ducky',
        timezone: partial.timezone ?? timezone,
        hasSeenOnboarding: partial.hasSeenOnboarding ?? false,
        mode: partial.mode ?? 'solo',
        challengeRules: 'standard',
        createdAt: nowIso,
        updatedAt: nowIso,
        pushEnabled: false,
        email: partial.email ?? null,
      };
      await store.transaction(async (tx) => {
        await tx.create('userProfiles', profile);
        await tx.create('onboardingStates', {
          id: uid,
          uid,
          step: 'welcome',
          selectedAreas: [],
          completedAt: null,
          updatedAt: nowIso,
        });
        await tx.create('streaks', {
          id: `${uid}:root`,
          userId: uid,
          goalId: 'root',
          currentStreak: 0,
          longestStreak: 0,
          successfulDays: 0,
          brokenCount: 0,
          shields: DEFAULT_STREAK_CONFIG.shields,
          remainingGraceDays: DEFAULT_STREAK_CONFIG.graceDays,
          lastVerifiedDay: null,
          lastBreakDay: null,
          updatedAt: nowIso,
        });
      });
      return profile;
    },

    setOnboarding: async (uid: unknown, input: unknown): Promise<OnboardingState> => {
      const userId = String(uid);
      const body = (input ?? {}) as Partial<OnboardingState>;
      const current = (await store.get<OnboardingState>('onboardingStates', userId)) ?? {
        id: userId,
        uid: userId,
        step: 'welcome',
        selectedAreas: [],
        completed: false,
        completedAt: null,
        updatedAt: now().toISOString(),
      };
      const next: OnboardingState = {
        ...current,
        step: body.step ?? current.step,
        selectedAreas: body.selectedAreas ?? current.selectedAreas,
        completed: body.completed ?? current.completed,
        completedAt: body.completed ? now().toISOString() : current.completedAt,
        updatedAt: now().toISOString(),
      };
      await store.transaction(async (tx) => {
        await tx.set('onboardingStates', next);
      });
      return next;
    },

    getOnboarding: (uid: unknown) => store.get<OnboardingState>('onboardingStates', String(uid)),

    /* missions */
    generateDailyMissions: () => missions.generateDailyMissions(ctx),
    startMission: (uid: unknown, input: unknown) => missions.startMission(ctx, uid, input),
    sendProgress: (uid: unknown, input: unknown) => missions.sendProgress(ctx, uid, input),
    finishMission: (uid: unknown, input: unknown) => missions.finishMission(ctx, uid, input),
    submitProof: (uid: unknown, input: unknown) => missions.submitProof(ctx, uid, input),
    verifyProofHuman: (uid: unknown, proofId: unknown, decision: 'verified' | 'rejected', note: string) =>
      missions.verifyProofHuman(ctx, uid, proofId, decision, note),
    submitQuiz: (uid: unknown, input: unknown) => missions.submitQuiz(ctx, uid, input),

    /* learning */
    requestMaterialUpload: (uid: unknown, input: unknown) => learning.requestMaterialUpload(ctx, uid, input),
    markMaterialUploaded: (uid: unknown, input: unknown) => learning.markMaterialUploaded(ctx, uid, input),
    processLearningMaterial: (materialId: unknown, ownerUid?: unknown) => learning.processLearningMaterial(ctx, materialId, ownerUid as string | undefined),
    createLearningPlan: (uid: unknown, input: unknown) => learning.createLearningPlan(ctx, uid, input),
    generateQuiz: (uid: unknown, input: unknown) => learning.generateQuiz(ctx, uid, input),
    createLessonProof: (uid: unknown, input: unknown) => learning.createLessonProof(ctx, uid, input),

    /* activity */
    startActivity: (uid: unknown, input: unknown) => activity.startActivity(ctx, uid, input),
    endActivity: (uid: unknown, input: unknown) => activity.endActivity(ctx, uid, input),
    activityCheckIn: (uid: unknown, input: unknown) => activity.checkIn(ctx, uid, input),

    /* social */
    createGroup: (uid: unknown, input: unknown) => social.createGroup(ctx, uid, input),
    joinGroup: (uid: unknown, input: unknown) => social.joinGroup(ctx, uid, input),
    sendMessage: (uid: unknown, input: unknown) => social.sendMessage(ctx, uid, input),
    createBattle: (uid: unknown, input: unknown) => social.createBattle(ctx, uid, input),
    tickBattle: (uid: unknown, input: unknown) => social.tickBattle(ctx, uid, input),
    resolveBattle: (uid: unknown, input: unknown) => social.resolveBattle(ctx, uid, input),
    proposePunishment: (uid: unknown, input: unknown) => social.proposePunishment(ctx, uid, input),
    castVote: (uid: unknown, input: unknown) => social.castVote(ctx, uid, input),
    submitPunishmentProof: (uid: unknown, punishmentId: unknown, evidence: string | null) =>
      social.submitPunishmentProof(ctx, uid, punishmentId, evidence),
    requestCoachMessage: (uid: unknown, input: unknown) => social.requestCoachMessage(ctx, uid, input),
    simulateGroupAIMessage: (uid: unknown, input: unknown) => social.simulateGroupAIMessage(ctx, uid, input),

    /* notifications & device */
    createNotification: (uid: string, category: Parameters<typeof notifications.createNotification>[2], title: string, body: string, data?: Record<string, string>) =>
      notifications.createNotification(ctx, uid, category, title, body, data),
    saveNotificationPreference: (uid: unknown, input: unknown) => notifications.saveNotificationPreference(ctx, uid, input),
    updateDeviceConnection: (uid: unknown, input: unknown) => notifications.updateDeviceConnection(ctx, uid, input),
    listNotifications: (uid: unknown) => notifications.listNotifications(ctx, uid),

    /* queries (read-only helpers for functions + app) */
    getMission: (id: string) => store.get<Mission>('missions', id),
    getGoal: (id: string) => store.get<Goal>('goals', id),
    listMissions: (uid: unknown) => missions.listMissions(ctx, uid),
    getStreak: (uid: string, goalId: string) => store.get<StreakState>('streaks', `${uid}:${goalId}`),
    getLevel: (uid: string) => store.get<LevelState>('levels', uid),
  };
}

export type Backend = ReturnType<typeof createBackend>;

export { InMemoryStore };

// Referenced so validation modules stay in the type graph when tree-shaken.
export type {
  requestMaterialUploadInput, markMaterialUploadedInput, createLearningPlanInput, generateQuizInput,
  submitQuizAttemptInput, startActivityInput, endActivityInput, checkInActivityInput, createGroupInput,
  joinGroupInput, sendMessageInput, createBattleInput, tickBattleInput, resolveBattleInput,
  proposePunishmentInput, voteInput, requestCoachMessageInput, simulateGroupAIMessageInput,
  createGoalInput, updateGoalInput, setMissionProofInput, finishMissionInput,
};
void trackBirthdays;