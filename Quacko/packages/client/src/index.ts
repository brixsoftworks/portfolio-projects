import type { Backend } from '@quacko/backend';

/**
 * The RPC method surface shared by the self-hosted server and the web/mobile
 * clients. Define it once here: `apps/server` builds its allow-list from
 * `rpcMethodNames`, and clients narrow `Backend` to exactly this surface.
 *
 * Every method is uid-first on the backend. Over HTTP the client omits `uid`
 * and the server injects it from the JWT — call sites never change.
 */

export const rpcMethodNames = [
  'getOrCreateProfile',
  'setOnboarding',
  'getOnboarding',
  'getUserProfile',
  'createGoal',
  'generateGoalPlan',
  'updateGoal',
  'listGoals',
  'generateDailyMissions',
  'startMission',
  'sendProgress',
  'finishMission',
  'submitProof',
  'submitQuiz',
  'listMissions',
  'getMission',
  'getGoal',
  'getStreak',
  'getLevel',
  'requestCoachMessage',
  'simulateGroupAIMessage',
  'requestMaterialUpload',
  'markMaterialUploaded',
  'createLearningPlan',
  'generateQuiz',
  'createLessonProof',
  'startActivity',
  'endActivity',
  'activityCheckIn',
  'createGroup',
  'joinGroup',
  'sendMessage',
  'createBattle',
  'tickBattle',
  'resolveBattle',
  'proposePunishment',
  'castVote',
  'submitPunishmentProof',
  'saveNotificationPreference',
  'updateDeviceConnection',
  'listNotifications',
] as const;

export type RpcMethodName = (typeof rpcMethodNames)[number];

/** The exact surface clients can call over the wire. */
export type RpcApi = Pick<Backend, RpcMethodName>;

/** Server-side error, mapped from the backend's error kinds. */
export interface RpcErrorBody {
  error: { code: string; message: string };
}

export class ApiError extends Error {
  constructor(
    readonly status: number,
    readonly code: string,
    message: string,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

export interface HttpBackendOptions {
  /** API origin, e.g. `https://quacko.college.edu` or `` for same-origin. */
  baseUrl?: string;
  /** Returns the current bearer token (or null when logged out). */
  getToken?: () => string | null;
}

async function rpc(
  opts: Required<HttpBackendOptions>,
  method: RpcMethodName,
  args: unknown[],
): Promise<unknown> {
  const token = opts.getToken();
  const res = await fetch(`${opts.baseUrl.replace(/\/$/, '')}/api/v1/rpc`, {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      ...(token ? { authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({ method, args }),
  });
  const body = (await res.json().catch(() => null)) as
    | { data?: unknown; error?: { code?: string; message?: string } }
    | null;
  if (!res.ok) {
    throw new ApiError(
      res.status,
      body?.error?.code ?? 'internal',
      body?.error?.message ?? `Request failed (${res.status})`,
    );
  }
  return body?.data;
}

/** Methods whose first parameter is `uid` (omitted on the wire). */
const UID_FIRST: ReadonlySet<RpcMethodName> = new Set([
  'getOrCreateProfile',
  'setOnboarding',
  'getOnboarding',
  'getUserProfile',
  'createGoal',
  'generateGoalPlan',
  'updateGoal',
  'listGoals',
  'startMission',
  'sendProgress',
  'finishMission',
  'submitProof',
  'submitQuiz',
  'listMissions',
  'getStreak',
  'getLevel',
  'requestCoachMessage',
  'simulateGroupAIMessage',
  'requestMaterialUpload',
  'markMaterialUploaded',
  'createLearningPlan',
  'generateQuiz',
  'createLessonProof',
  'startActivity',
  'endActivity',
  'activityCheckIn',
  'createGroup',
  'joinGroup',
  'sendMessage',
  'createBattle',
  'tickBattle',
  'resolveBattle',
  'proposePunishment',
  'castVote',
  'submitPunishmentProof',
  'saveNotificationPreference',
  'updateDeviceConnection',
  'listNotifications',
]);

/** Per-method wire arg lists. Kept explicit so the RPC protocol is auditable. */

export function createHttpBackend(options: HttpBackendOptions = {}): RpcApi {
  const opts: Required<HttpBackendOptions> = {
    baseUrl: options.baseUrl ?? '',
    getToken: options.getToken ?? (() => null),
  };

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const uidCall =
    (method: RpcMethodName) =>
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    async (uid: unknown, ...rest: any[]): Promise<any> => {
      void uid;
      return rpc(opts, method, rest);
    };

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const plainCall =
    (method: RpcMethodName) =>
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    async (...args: any[]): Promise<any> => rpc(opts, method, args);

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const calls: Record<string, (...args: any[]) => Promise<any>> = {};
  for (const method of rpcMethodNames) {
    calls[method] = UID_FIRST.has(method) ? uidCall(method) : plainCall(method);
  }
  return calls as RpcApi;
}

/* -------------------------------------------------------------------------- */
/* Auth (used by login/register screens; token lives in the app, not here)     */
/* -------------------------------------------------------------------------- */

export interface AuthResponse {
  token: string;
  profile: import('@quacko/types').UserProfile;
}

export interface RegisterInput {
  email: string;
  password: string;
  displayName?: string;
  timezone?: string;
}

async function authPost(
  baseUrl: string,
  path: '/auth/register' | '/auth/login',
  body: unknown,
): Promise<AuthResponse> {
  const res = await fetch(`${baseUrl.replace(/\/$/, '')}/api/v1${path}`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(body),
  });
  const parsed = (await res.json().catch(() => null)) as
    | { token?: unknown; profile?: unknown; error?: { code?: string; message?: string } }
    | null;
  if (!res.ok) {
    throw new ApiError(
      res.status,
      parsed?.error?.code ?? 'internal',
      parsed?.error?.message ?? `Auth failed (${res.status})`,
    );
  }
  const data = parsed as AuthResponse;
  if (!data?.token || !data?.profile) throw new ApiError(500, 'internal', 'malformed auth response');
  return data;
}

export function registerUser(baseUrl: string, input: RegisterInput): Promise<AuthResponse> {
  return authPost(baseUrl, '/auth/register', input);
}

export function loginUser(baseUrl: string, email: string, password: string): Promise<AuthResponse> {
  return authPost(baseUrl, '/auth/login', { email, password });
}

export function fetchMe(baseUrl: string, token: string): Promise<unknown> {
  return fetch(`${baseUrl.replace(/\/$/, '')}/api/v1/auth/me`, {
    headers: { authorization: `Bearer ${token}` },
  }).then(async (res) => {
    const body = (await res.json().catch(() => null)) as unknown;
    if (!res.ok) {
      const err = body as { error?: { code?: string; message?: string } };
      throw new ApiError(res.status, err?.error?.code ?? 'internal', err?.error?.message ?? res.statusText);
    }
    return body;
  });
}

/** Change the wire formatter for debugging the RPC protocol. */
export { rpc };