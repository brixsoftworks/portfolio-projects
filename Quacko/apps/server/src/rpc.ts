import type { Backend } from '@quacko/backend';
import { UnauthorizedError } from '@quacko/backend';
import type { UserProfile } from '@quacko/types';
import { rpcMethodNames, type RpcMethodName } from '@quacko/client';

/**
 * Server-side RPC handlers. One entry per client method; `uid` is injected from
 * the JWT (never trusted from the request body). Methods that take an id on the
 * wire are narrowed to documents owned by the caller.
 */
export type RpcHandler = (backend: Backend, uid: string, args: unknown[]) => Promise<unknown>;

export type RpcHandlers = Record<RpcMethodName, RpcHandler>;

async function ownedDoc<T extends { id: string; ownerId?: string | null }>(
  backend: Backend,
  uid: string,
  collection: string,
  id: unknown,
): Promise<T> {
  const doc = await backend.store.get<T>(collection, String(id ?? ''));
  if (!doc || (doc.ownerId != null && doc.ownerId !== uid)) {
    throw new UnauthorizedError('not found');
  }
  return doc;
}

export function buildRpcHandlers(backend: Backend): RpcHandlers {
  const b = backend;
  const handlers: RpcHandlers = {
    /* profile & onboarding */
    getOrCreateProfile: (_b, uid, [partial]) => b.getOrCreateProfile(uid, partial as Partial<UserProfile> | undefined),
    setOnboarding: (_b, uid, [input]) => b.setOnboarding(uid, input),
    getOnboarding: (_b, uid) => b.getOnboarding(uid),
    getUserProfile: (_b, uid) => b.getUserProfile(uid),

    /* goals */
    createGoal: (_b, uid, [input]) => b.createGoal(uid, input),
    generateGoalPlan: (_b, uid, [goalId]) => b.generateGoalPlan(uid, goalId),
    updateGoal: (_b, uid, [goalId, patch]) => b.updateGoal(uid, goalId, patch),
    listGoals: (_b, uid) => b.listGoals(uid),

    /* missions */
    generateDailyMissions: () => b.generateDailyMissions(),
    startMission: (_b, uid, [input]) => b.startMission(uid, input),
    sendProgress: (_b, uid, [input]) => b.sendProgress(uid, input),
    finishMission: (_b, uid, [input]) => b.finishMission(uid, input),
    submitProof: (_b, uid, [input]) => b.submitProof(uid, input),
    submitQuiz: (_b, uid, [input]) => b.submitQuiz(uid, input),
    listMissions: (_b, uid) => b.listMissions(uid),
    getMission: (_b, uid, [id]) => ownedDoc(b, uid, 'missions', id),
    getGoal: (_b, uid, [id]) => ownedDoc(b, uid, 'goals', id),

    /* queries */
    getStreak: (_b, uid, [goalId]) => b.getStreak(uid, String(goalId)),
    getLevel: (_b, uid) => b.getLevel(uid),

    /* social & coach */
    requestCoachMessage: (_b, uid, [input]) => b.requestCoachMessage(uid, input),
    simulateGroupAIMessage: (_b, uid, [input]) => b.simulateGroupAIMessage(uid, input),
    createGroup: (_b, uid, [input]) => b.createGroup(uid, input),
    joinGroup: (_b, uid, [input]) => b.joinGroup(uid, input),
    sendMessage: (_b, uid, [input]) => b.sendMessage(uid, input),
    createBattle: (_b, uid, [input]) => b.createBattle(uid, input),
    tickBattle: (_b, uid, [input]) => b.tickBattle(uid, input),
    resolveBattle: (_b, uid, [input]) => b.resolveBattle(uid, input),
    proposePunishment: (_b, uid, [input]) => b.proposePunishment(uid, input),
    castVote: (_b, uid, [input]) => b.castVote(uid, input),
    submitPunishmentProof: (_b, uid, [punishmentId, evidence]) =>
      b.submitPunishmentProof(uid, punishmentId, evidence === null ? null : String(evidence ?? '')),

    /* learning */
    requestMaterialUpload: (_b, uid, [input]) => b.requestMaterialUpload(uid, input),
    markMaterialUploaded: (_b, uid, [input]) => b.markMaterialUploaded(uid, input),
    createLearningPlan: (_b, uid, [input]) => b.createLearningPlan(uid, input),
    generateQuiz: (_b, uid, [input]) => b.generateQuiz(uid, input),
    createLessonProof: (_b, uid, [input]) => b.createLessonProof(uid, input),

    /* activity */
    startActivity: (_b, uid, [input]) => b.startActivity(uid, input),
    endActivity: (_b, uid, [input]) => b.endActivity(uid, input),
    activityCheckIn: (_b, uid, [input]) => b.activityCheckIn(uid, input),

    /* notifications */
    saveNotificationPreference: (_b, uid, [input]) => b.saveNotificationPreference(uid, input),
    updateDeviceConnection: (_b, uid, [input]) => b.updateDeviceConnection(uid, input),
    listNotifications: (_b, uid) => b.listNotifications(uid),
  };

  for (const method of rpcMethodNames) {
    if (!handlers[method]) throw new Error(`missing RPC handler for ${method}`);
  }
  return handlers;
}