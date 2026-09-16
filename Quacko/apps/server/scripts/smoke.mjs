/**
 * QUACKO server smoke test. Exercises the full golden path over real HTTP:
 * register → me → createGoal → plan → daily missions → start/finish →
 * gps proof (auto-verified) → streak/level → login → wrong password.
 *
 *   node scripts/smoke.mjs [baseUrl] [email]
 */
const BASE = process.argv[2] ?? 'http://127.0.0.1:8787/api/v1';
const EMAIL = process.argv[3] ?? `smoke_${Date.now()}@quacko.app`;
const VERBOSE = process.argv.includes('--verbose');

let failures = 0;
function check(name, condition, detail = '') {
  if (condition) {
    console.log(`  ok   ${name}`);
  } else {
    failures += 1;
    console.error(`  FAIL ${name} ${detail}`);
  }
}

async function j(method, path, { token, body } = {}) {
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: {
      ...(body !== undefined ? { 'content-type': 'application/json' } : {}),
      ...(token ? { authorization: `Bearer ${token}` } : {}),
    },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
  const text = await res.text();
  if (VERBOSE) console.log(`\n>> ${method} ${path} -> ${res.status}\n   ${text.slice(0, 400)}`);
  let parsed = null;
  try {
    parsed = text ? JSON.parse(text) : null;
  } catch {
    parsed = null;
  }
  // Unwrap RPC-style `{data}` envelopes; auth/health return top-level fields.
  return { status: res.status, data: parsed?.data ?? parsed, body: parsed };
}

async function rpc(token, method, args = []) {
  return j('POST', '/rpc', { token, body: { method, args } });
}

console.log(`smoke: BASE=${BASE} EMAIL=${EMAIL}`);
check('health', (await j('GET', '/health')).data?.ok === true);

const reg = await j('POST', '/auth/register', { body: { email: EMAIL, password: 'hunter22', displayName: 'Smoke Duck', timezone: 'UTC' } });
check('register → token+profile', Boolean(reg.data?.token && reg.data?.profile?.displayName === 'Smoke Duck'), JSON.stringify(reg.data?.error ?? ''));
const token = reg.data?.token;

const me = await j('GET', '/auth/me', { token });
check('auth/me → profile', me.data?.email === EMAIL && me.status === 200, JSON.stringify(me.data?.error ?? ''));

const goal = await rpc(token, 'createGoal', [{ title: 'Run daily', description: '5k every morning', category: 'fitness', target: '5 sessions / week', deadline: null, dailyAvailabilityMinutes: 30, difficulty: 'medium', proofRequired: true, schedule: { cadence: 'daily', days: [], preferredWindows: [], timezone: 'UTC' } }]);
check('createGoal', Boolean(goal.data?.id), JSON.stringify(goal.data?.error ?? ''));
const goalId = goal.data?.id;

const plan = await rpc(token, 'generateGoalPlan', [goalId]);
check('generateGoalPlan', Boolean(plan.data), JSON.stringify(plan.data?.error ?? ''));

const gen = await rpc(token, 'generateDailyMissions');
check('generateDailyMissions → 2 missions', Array.isArray(gen.data) && gen.data.length === 2, JSON.stringify(gen.data?.error ?? ''));

const list = await rpc(token, 'listMissions');
const mission = list.data?.[0];
check('listMissions → owned missions', Boolean(mission), JSON.stringify(list.data?.error ?? ''));

const started = await rpc(token, 'startMission', [{ missionId: mission?.id }]);
check('startMission → started', started.data?.status === 'started', JSON.stringify(started.data?.error ?? ''));

const finished = await rpc(token, 'finishMission', [{ missionId: mission?.id, percent: 100 }]);
check('finishMission → proof_pending', finished.data?.status === 'proof_pending', JSON.stringify(finished.data?.error ?? ''));

const proof = await rpc(token, 'submitProof', [{ missionId: mission?.id, proof: { type: 'gps', metadata: { distanceMeters: 5000, durationMinutes: 32 }, mediaUrl: null } }]);
check('submitProof → auto-verified', proof.data?.state === 'verified', JSON.stringify(proof.data?.error ?? proof.data?.state ?? ''));

const streak = await rpc(token, 'getStreak', [goalId]);
check('streak = 1 after proof', streak.data?.currentStreak === 1, JSON.stringify(streak.data?.error ?? streak.data?.currentStreak ?? ''));

const level = await rpc(token, 'getLevel');
check('level ≥ 1 and xp > 0', Number(level.data?.level) >= 1 && Number(level.data?.totalXp) > 0, JSON.stringify(level.body?.error ?? ''));

const coach = await rpc(token, 'requestCoachMessage', [{ goalId, context: 'just finished' }]);
check('coach message from demo AI', Boolean(coach.data?.message), JSON.stringify(coach.body?.error ?? ''));

const login = await j('POST', '/auth/login', { body: { email: EMAIL, password: 'hunter22' } });
check('login → token', Boolean(login.data?.token), JSON.stringify(login.data?.error ?? ''));

const badLogin = await j('POST', '/auth/login', { body: { email: EMAIL, password: 'wrong-password' } });
check('wrong password → 401', badLogin.status === 401, JSON.stringify(badLogin.data ?? ''));

const noAuth = await j('POST', '/rpc', { body: { method: 'listGoals', args: [] } });
check('rpc without token → 401', noAuth.status === 401, String(noAuth.status));

const rpcBad = await rpc(token, 'noSuchMethod');
check('unknown rpc method → 404', rpcBad.status === 404, String(rpcBad.status));

console.log(failures === 0 ? '\nSMOKE PASSED' : `\nSMOKE FAILED (${failures})`);
process.exit(failures === 0 ? 0 : 1);