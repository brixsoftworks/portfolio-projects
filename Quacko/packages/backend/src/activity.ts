import type { BackendCtx } from './ctx';
import type { ActivityDefinition, ActivitySession, Mission, RoutePoint } from '@quacko/types';
import { pruneRoute } from '@quacko/domain/src/activity';
import { routeDistance, paceSecPerKm } from '@quacko/domain/src/activity';
import { assertDoc, assertInput, assertUser } from './ctx';
import { UnauthorizedError } from './store';
import { checkInActivityInput, endActivityInput, startActivityInput } from '@quacko/validation';
import { submitProof } from './missions';

const DEFINITIONS: Record<ActivityDefinition['kind'], Omit<ActivityDefinition, 'kind'>> = {
  running: { target: '5 km', targetUnits: 'distance_km', targetValue: 5, proofMethod: 'gps', durationMinutes: 40 },
  walking: { target: '30 min', targetUnits: 'duration_min', targetValue: 30, proofMethod: 'gps', durationMinutes: 30 },
  cycling: { target: '15 km', targetUnits: 'distance_km', targetValue: 15, proofMethod: 'gps', durationMinutes: 60 },
  meditation: { target: '15 min', targetUnits: 'duration_min', targetValue: 15, proofMethod: 'timer', durationMinutes: 15 },
  reading: { target: '20 min', targetUnits: 'duration_min', targetValue: 20, proofMethod: 'timer', durationMinutes: 20 },
  coding: { target: '1 session', targetUnits: 'sessions', targetValue: 1, proofMethod: 'manual', durationMinutes: 60 },
  sleep: { target: '7 h', targetUnits: 'duration_min', targetValue: 420, proofMethod: 'health', durationMinutes: 420 },
  digital_wellbeing: { target: '1 block', targetUnits: 'sessions', targetValue: 1, proofMethod: 'timer', durationMinutes: 30 },
  custom: { target: '1 session', targetUnits: 'sessions', targetValue: 1, proofMethod: 'manual', durationMinutes: 30 },
};

export async function startActivity(ctx: BackendCtx, rawUid: unknown, rawInput: unknown): Promise<ActivitySession> {
  const uid = assertUser(rawUid);
  const input = assertInput(rawInput, startActivityInput);
  const def = DEFINITIONS[input.kind] ?? DEFINITIONS.custom;
  const now = ctx.now().toISOString();
  const session: ActivitySession = {
    id: ctx.store.newId(),
    missionId: input.missionId ?? null,
    userId: uid,
    kind: input.kind,
    state: 'live',
    startedAt: now,
    elapsedSeconds: 0,
    pausedAt: null,
    resumedAt: null,
    targetUnits: input.targetUnits ?? def.targetUnits,
    targetValue: input.targetValue ?? def.targetValue,
    distanceMeters: 0,
    steps: null,
    avgPaceSecondsPerKm: null,
    route: [],
    proofRef: null,
    sessionToken: input.sessionToken,
    updatedAt: now,
  };
  await ctx.store.transaction(async (tx) => {
    await tx.create('activitySessions', session);
  });
  return session;
}

export async function endActivity(ctx: BackendCtx, rawUid: unknown, rawInput: unknown): Promise<ActivitySession> {
  const uid = assertUser(rawUid);
  const input = assertInput(rawInput, endActivityInput);
  const session = assertDoc(await ctx.store.get<ActivitySession>('activitySessions', input.sessionId), 'activity session');
  if (session.userId !== uid) throw new UnauthorizedError('not the owner');

  const route: RoutePoint[] = (input.route ?? []).map((p) => ({ ...p, speedMps: p.speedMps ?? null }));
  const distanceMeters = input.distanceMeters ?? routeDistance(route);
  const avgPace = paceSecPerKm(distanceMeters, input.elapsedSeconds);
  const finished: ActivitySession = {
    ...session,
    id: session.id,
    state: 'completed',
    elapsedSeconds: input.elapsedSeconds,
    distanceMeters: Math.round(distanceMeters),
    steps: input.steps ?? session.steps,
    avgPaceSecondsPerKm: avgPace,
    route: pruneRoute(route, 20),
    updatedAt: ctx.now().toISOString(),
  };
  await ctx.store.transaction(async (tx) => {
    await tx.set('activitySessions', finished);
  });

  if (session.missionId) {
    const mission = await ctx.store.get<Mission>('missions', session.missionId);
    if (mission && mission.status === 'proof_pending') {
      const proofType = session.kind === 'meditation' || session.kind === 'reading' || session.kind === 'digital_wellbeing' ? 'timer' : 'gps';
      await submitProof(ctx, uid, {
        missionId: mission.id,
        proof: {
          type: proofType,
          metadata:
            proofType === 'gps'
              ? { distanceMeters, durationSeconds: input.elapsedSeconds }
              : { durationSeconds: input.elapsedSeconds },
          mediaUrl: null,
        },
      });
    }
  }
  return finished;
}

export async function checkIn(ctx: BackendCtx, rawUid: unknown, rawInput: unknown): Promise<ActivitySession> {
  const uid = assertUser(rawUid);
  const input = assertInput(rawInput, checkInActivityInput);
  const session = assertDoc(await ctx.store.get<ActivitySession>('activitySessions', input.sessionId), 'activity session');
  if (session.userId !== uid) throw new UnauthorizedError('not the owner');
  const updated = await ctx.store.transaction(async (tx) => {
    return assertDoc(
      await tx.update<ActivitySession>('activitySessions', session.id, { updatedAt: ctx.now().toISOString() }),
      'activity session',
    );
  });
  return updated;
}

export { DEFINITIONS };