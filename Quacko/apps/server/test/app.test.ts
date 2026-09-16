import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import request from 'supertest';
import { DemoProvider } from '@quacko/ai';
import { createBackend } from '@quacko/backend';
import type { Mission } from '@quacko/types';
import { SqliteStore } from '../src/sqliteStore';
import { createApp, type ServerServices } from '../src/app';
import type { ServerConfig } from '../src/config';

let store: SqliteStore;
let app: ReturnType<typeof createApp>;
let tmpDir: string;

async function makeConfig(overrides: Partial<ServerConfig> = {}): Promise<ServerConfig> {
  const cfg: ServerConfig = {
    host: '127.0.0.1',
    port: 0,
    jwtSecret: 'test-secret-for-integration-tests-abcdef',
    dataDir: tmpDir,
    webDir: null,
    timezone: 'UTC',
    defaultLevelTitle: 'Fresh Ducky',
    ai: { provider: 'demo' },
    publicUrl: '',
    maxUploadBytes: 20 * 1024 * 1024,
    ...overrides,
  };
  return cfg;
}

async function register(email: string): Promise<string> {
  const res = await request(app).post('/api/v1/auth/register').send({
    email,
    password: 'password123',
    displayName: 'Duck',
    timezone: 'UTC',
  });
  expect(res.status).toBe(201);
  return res.body.token as string;
}

async function rpc(token: string, method: string, args: unknown[] = []) {
  return request(app).post('/api/v1/rpc').set('Authorization', `Bearer ${token}`).send({ method, args });
}

beforeAll(async () => {
  tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'quacko-test-'));
  store = new SqliteStore(':memory:');
  const config = await makeConfig();
  const backend = createBackend(new DemoProvider(), { store, timezone: config.timezone, defaultLevelTitle: config.defaultLevelTitle });
  app = createApp(config, { backend, store } as ServerServices);
});

afterAll(async () => {
  store.close();
  fs.rmSync(tmpDir, { recursive: true, force: true });
});

describe('health', () => {
  it('reports ok', async () => {
    const res = await request(app).get('/api/v1/health');
    expect(res.status).toBe(200);
    expect(res.body.ok).toBe(true);
  });

  it('404s unknown /api routes', async () => {
    const res = await request(app).get('/api/v1/nope');
    expect(res.status).toBe(404);
    expect(res.body.error.code).toBe('not-found');
  });
});

describe('auth', () => {
  it('registers, logs in, and identifies via /me', async () => {
    const token = await register('duck1@example.com');
    expect(token.length).toBeGreaterThan(20);

    const me = await request(app).get('/api/v1/auth/me').set('Authorization', `Bearer ${token}`);
    expect(me.status).toBe(200);
    expect(me.body.email).toBe('duck1@example.com');
    expect(me.body.hasSeenOnboarding).toBe(false);
  });

  it('rejects duplicate email with 409', async () => {
    const res = await request(app)
      .post('/api/v1/auth/register')
      .send({ email: 'duck1@example.com', password: 'password123' });
    expect(res.status).toBe(409);
  });

  it('rejects invalid shapes with 400', async () => {
    const bad = await request(app).post('/api/v1/auth/register').send({ email: 'nope', password: 'short' });
    expect(bad.status).toBe(400);
    const bad2 = await request(app).post('/api/v1/auth/login').send({ email: 'nope', password: 'x' });
    expect(bad2.status).toBe(400);
  });

  it('logs in with correct password and rejects wrong ones', async () => {
    const ok = await request(app).post('/api/v1/auth/login').send({ email: 'duck1@example.com', password: 'password123' });
    expect(ok.status).toBe(200);
    expect(ok.body.token).toBeTruthy();

    const bad = await request(app).post('/api/v1/auth/login').send({ email: 'duck1@example.com', password: 'wrong-password' });
    expect(bad.status).toBe(401);

    const unknown = await request(app).post('/api/v1/auth/login').send({ email: 'ghost@example.com', password: 'password123' });
    expect(unknown.status).toBe(401);
  });

  it('rejects missing or invalid bearer tokens on /me', async () => {
    const none = await request(app).get('/api/v1/auth/me');
    expect(none.status).toBe(401);
    const bad = await request(app).get('/api/v1/auth/me').set('Authorization', 'Bearer garbage-token');
    expect(bad.status).toBe(401);
  });
});

describe('RPC golden path', () => {
  let token: string;
  let goalId: string;
  let mission: Mission;

  beforeAll(async () => {
    token = await register('duck2@example.com');
  });

  it('creates a goal', async () => {
    const res = await rpc(token, 'createGoal', [
      { title: 'Run daily', description: '5k every morning', category: 'fitness', target: '5 sessions / week', deadline: null, dailyAvailabilityMinutes: 30, difficulty: 'medium', proofRequired: true, schedule: { cadence: 'daily', days: [], preferredWindows: [], timezone: 'UTC' } },
    ]);
    expect(res.status).toBe(200);
    goalId = res.body.data.id;
    expect(goalId).toBeTruthy();
  });

  it('generates a goal plan', async () => {
    const res = await rpc(token, 'generateGoalPlan', [goalId]);
    expect(res.status, JSON.stringify(res.body)).toBe(200);
    expect(Array.isArray(res.body.data)).toBe(false);
    expect(res.body.data.days).toHaveLength(30);
  });

  it('finishes onboarding and generates missions', async () => {
    const onboard = await rpc(token, 'setOnboarding', [{ step: 'done', completed: true, selectedAreas: ['fitness'] }]);
    expect(onboard.status).toBe(200);
    const missions = await rpc(token, 'generateDailyMissions');
    expect(missions.status).toBe(200);
    expect(missions.body.data).toHaveLength(2);
  });

  it('starts, finishes, submits proof, and earns a streak', async () => {
    const list = await rpc(token, 'listMissions');
    expect(list.status, JSON.stringify(list.body)).toBe(200);
    mission = list.body.data[0];
    expect(mission?.id, JSON.stringify(list.body)).toBeTruthy();

    const started = await rpc(token, 'startMission', [{ missionId: mission.id }]);
    expect(started.status, JSON.stringify(started.body)).toBe(200);
    expect(started.body.data.status).toBe('started');

    const finished = await rpc(token, 'finishMission', [{ missionId: mission.id, percent: 100 }]);
    expect(finished.status, JSON.stringify(finished.body)).toBe(200);
    expect(finished.body.data.status).toBe('proof_pending');

    const proof = await rpc(token, 'submitProof', [
      { missionId: mission.id, proof: { type: 'gps', metadata: { distanceMeters: 5000, durationMinutes: 32 }, mediaUrl: null } },
    ]);
    expect(proof.status).toBe(200);
    expect(proof.body.data.state).toBe('verified');

    const streak = await rpc(token, 'getStreak', [goalId]);
    expect(streak.status, JSON.stringify(streak.body)).toBe(200);
    expect(streak.body.data.currentStreak).toBeGreaterThanOrEqual(1);
  });

  it('rejects proof payloads without the nested proof object', async () => {
    const res = await rpc(token, 'submitProof', [{ missionId: 'nope', type: 'gps', metadata: {} }]);
    expect(res.status).toBe(400);
  });
});

describe('RPC guards', () => {
  it('rejects unknown methods with 404', async () => {
    const token = await register('duck3@example.com');
    const res = await rpc(token, 'deleteEverything');
    expect(res.status).toBe(404);
  });

  it('rejects requests without a token', async () => {
    const res = await request(app).post('/api/v1/rpc').send({ method: 'listGoals', args: [] });
    expect(res.status).toBe(401);
  });

  it('blocks reading another user goal', async () => {
    const a = await register('owner@example.com');
    const goal = await rpc(a, 'createGoal', [
      { title: 'Secret Goal', description: 'hush', category: 'learning', target: 'redact', deadline: null, dailyAvailabilityMinutes: 15, difficulty: 'easy', proofRequired: true, schedule: { cadence: 'daily', days: [], preferredWindows: [], timezone: 'UTC' } },
    ]);
    const goalId = goal.body.data.id;

    const b = await register('intruder@example.com');
    const res = await rpc(b, 'getGoal', [{ goalId }]);
    // ownedDoc conceals foreign access as unauthorized/not-found (no user enumeration).
    expect(res.status, JSON.stringify(res.body)).not.toBe(200);
    expect(res.body.error.code).toBe('unauthorized');
  });
});

describe('uploads', () => {
  it('stores raw bodies and serves them back', async () => {
    const token = await register('duck4@example.com');
    const up = await request(app)
      .post('/api/v1/uploads?ext=png')
      .set('Authorization', `Bearer ${token}`)
      .set('Content-Type', 'image/png')
      .send(Buffer.from([0x89, 0x50, 0x4e, 0x47]));
    expect(up.status).toBe(201);
    const url = up.body.url;
    expect(url.startsWith('/uploads/')).toBe(true);
    expect(url.endsWith('.png')).toBe(true);

    const got = await request(app).get(url);
    expect(got.status).toBe(200);
    expect(got.body).toEqual(Buffer.from([0x89, 0x50, 0x4e, 0x47]));
  });

  it('requires auth', async () => {
    const up = await request(app).post('/api/v1/uploads?ext=png').send(Buffer.from([1, 2, 3]));
    expect(up.status).toBe(401);
  });
});

describe('web static', () => {
  it('serves the SPA from WEB_DIR', async () => {
    const webDir = fs.mkdtempSync(path.join(os.tmpdir(), 'quacko-web-'));
    fs.writeFileSync(path.join(webDir, 'index.html'), '<html><body>quacko</body></html>');
    const cfg = await makeConfig({ webDir });
    const store2 = new SqliteStore(':memory:');
    const backend = createBackend(new DemoProvider(), { store: store2 });
    const app2 = createApp(cfg, { backend, store: store2 } as ServerServices);
    try {
      const res = await request(app2).get('/');
      expect(res.status).toBe(200);
      expect(res.text).toContain('quacko');

      const deep = await request(app2).get('/some/deep/route').set('Accept', 'text/html');
      expect(deep.status).toBe(200);
      expect(deep.text).toContain('quacko');
    } finally {
      store2.close();
      fs.rmSync(webDir, { recursive: true, force: true });
    }
  });
});