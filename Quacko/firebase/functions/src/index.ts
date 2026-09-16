import { initializeApp } from 'firebase-admin/app';
import { getFirestore } from 'firebase-admin/firestore';
import { onCall, HttpsError, type CallableRequest } from 'firebase-functions/v2/https';
import { onSchedule } from 'firebase-functions/v2/scheduler';
import { createBackend } from '@quacko/backend';
import {
  ConflictError,
  NotFoundError,
  UnauthorizedError,
  ValidationFailure,
} from '@quacko/backend/src/store';
import { createHttpProvider, DemoProvider } from '@quacko/ai';
import { FirestoreStore } from './firestoreStore';

const app = initializeApp();
const db = getFirestore(app);
const store = new FirestoreStore(db);

const ai =
  process.env.AI_API_KEY != null && process.env.AI_API_KEY !== ''
    ? createHttpProvider({
        baseUrl: process.env.AI_BASE_URL ?? 'https://api.openai.com/v1',
        apiKey: process.env.AI_API_KEY,
        model: process.env.AI_MODEL ?? 'gpt-4o-mini',
      })
    : new DemoProvider();

const backend = createBackend(ai, { store });

function callerUid(ctx: CallableRequest): string {
  if (!ctx.auth?.uid) {
    throw new HttpsError('unauthenticated', 'Sign in required.');
  }
  return ctx.auth.uid;
}

function toError(err: unknown): HttpsError {
  if (err instanceof NotFoundError) return new HttpsError('not-found', err.message);
  if (err instanceof UnauthorizedError) return new HttpsError('permission-denied', err.message);
  if (err instanceof ValidationFailure) return new HttpsError('invalid-argument', err.message);
  if (err instanceof ConflictError) return new HttpsError('already-exists', err.message);
  if (err instanceof Error) return new HttpsError('internal', err.message);
  return new HttpsError('internal', 'unexpected error');
}

function call(method: (uid: string, data: unknown) => Promise<unknown>, skipAuth = false) {
  return onCall(async (req: CallableRequest) => {
    const uid = skipAuth ? (req.auth?.uid ?? 'anonymous') : callerUid(req);
    try {
      return await method(uid, req.data);
    } catch (err) {
      throw toError(err);
    }
  });
}

/* -------------------------------- auth/user ------------------------------- */

export const getOrCreateProfile = call((uid, data) =>
  backend.getOrCreateProfile(uid, (data ?? {}) as never),
);
export const setOnboarding = call((uid, data) => backend.setOnboarding(uid, data));
export const getOnboarding = call((uid) => backend.getOnboarding(uid));

/* --------------------------------- goals --------------------------------- */

export const createGoal = call((uid, data) => backend.createGoal(uid, data));
export const generateGoalPlan = call((uid, data) => backend.generateGoalPlan(uid, (data as { goalId?: string } | null)?.goalId));
export const updateGoal = call((uid, data) => backend.updateGoal(uid, (data as any)?.goalId, (data as any)?.patch));
export const listGoals = call((uid) => backend.listGoals(uid));

/* ------------------------------- missions --------------------------------- */

export const startMission = call((uid, data) => backend.startMission(uid, data));
export const sendProgress = call((uid, data) => backend.sendProgress(uid, data));
export const finishMission = call((uid, data) => backend.finishMission(uid, data));
export const submitProof = call((uid, data) => backend.submitProof(uid, data));
export const verifyProofHuman = call((uid, data) =>
  backend.verifyProofHuman(uid, (data as any)?.proofId, (data as any)?.decision, (data as any)?.note ?? ''),
);
export const submitQuiz = call((uid, data) => backend.submitQuiz(uid, data));

/* -------------------------------- learning -------------------------------- */

export const requestMaterialUpload = call((uid, data) => backend.requestMaterialUpload(uid, data));
export const markMaterialUploaded = call((uid, data) => backend.markMaterialUploaded(uid, data));
export const processLearningMaterial = call((uid, data) =>
  backend.processLearningMaterial((data as any)?.materialId, uid),
);
export const createLearningPlan = call((uid, data) => backend.createLearningPlan(uid, data));
export const generateQuiz = call((uid, data) => backend.generateQuiz(uid, data));
export const createLessonProof = call((uid, data) => backend.createLessonProof(uid, data));

/* -------------------------------- activity -------------------------------- */

export const startActivity = call((uid, data) => backend.startActivity(uid, data));
export const endActivity = call((uid, data) => backend.endActivity(uid, data));
export const activityCheckIn = call((uid, data) => backend.activityCheckIn(uid, data));

/* --------------------------------- social --------------------------------- */

export const createGroup = call((uid, data) => backend.createGroup(uid, data));
export const joinGroup = call((uid, data) => backend.joinGroup(uid, data));
export const sendMessage = call((uid, data) => backend.sendMessage(uid, data));
export const createBattle = call((uid, data) => backend.createBattle(uid, data));
export const tickBattle = call((uid, data) => backend.tickBattle(uid, data));
export const resolveBattle = call((uid, data) => backend.resolveBattle(uid, data));
export const proposePunishment = call((uid, data) => backend.proposePunishment(uid, data));
export const castVote = call((uid, data) => backend.castVote(uid, data));
export const submitPunishmentProof = call((uid, data) =>
  backend.submitPunishmentProof(uid, (data as any)?.punishmentId, (data as any)?.evidence ?? null),
);
export const requestCoachMessage = call((uid, data) => backend.requestCoachMessage(uid, data));
export const simulateGroupAIMessage = call((uid, data) => backend.simulateGroupAIMessage(uid, data));

/* --------------------------- notifications/device ------------------------- */

export const saveNotificationPreference = call((uid, data) => backend.saveNotificationPreference(uid, data));
export const updateDeviceConnection = call((uid, data) => backend.updateDeviceConnection(uid, data));
export const listNotifications = call((uid) => backend.listNotifications(uid));

/* ------------------------------- scheduled -------------------------------- */

export const dailyMissions = onSchedule('every day 00:10', async () => {
  await backend.generateDailyMissions();
});

export const debugHealth = onCall(async () => ({
  ok: true,
  ai: ai.name,
  store: store.name,
  region: 'us-central1',
}));