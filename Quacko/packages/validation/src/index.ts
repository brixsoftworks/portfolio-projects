import { z } from 'zod';

export const uidSchema = z.string().min(3).max(64);
export const isoDateSchema = z.string().datetime({ offset: true });
export const limitedText = (max: number) => z.string().min(1).max(max);
export const proofTypes = [
  'gps',
  'quiz',
  'timer',
  'health_data',
  'photo',
  'video',
  'audio',
  'screenshot',
  'code_tests',
  'manual_log',
] as const;

export const timezoneSchema = z.string().min(1).max(64);

export const scheduleSchema = z.object({
  cadence: z.enum(['daily', 'weekdays', 'weekends', 'custom']),
  days: z.array(z.enum(['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'])).max(7),
  preferredWindows: z
    .array(z.object({ startMinutes: z.number().int().min(0).max(1439), endMinutes: z.number().int().min(1).max(1440) }))
    .max(4)
    .default([]),
  timezone: timezoneSchema,
});

/* -------------------------------------------------------------------------- */
/* Auth                                                                        */
/* -------------------------------------------------------------------------- */

export const updateProfileInput = z
  .object({
    username: limitedText(32).optional(),
    displayName: limitedText(64).optional(),
    tagline: limitedText(120).optional(),
    avatarUrl: z.string().url().nullable().optional(),
    timezone: timezoneSchema.optional(),
    mode: z.enum(['solo', 'friends']).optional(),
    challengeRules: z.enum(['standard', 'relaxed', 'strict']).optional(),
    pushEnabled: z.boolean().optional(),
  })
  .refine((v) => Object.keys(v).length > 0, 'nothing to update');

export const setOnboardingInput = z.object({
  step: z.enum(['welcome', 'auth', 'meet_quacko', 'areas', 'goal', 'profile', 'permissions', 'plan', 'done']),
  selectedAreas: z.array(z.string()).max(12).default([]),
  completed: z.boolean().default(false),
});

/* -------------------------------------------------------------------------- */
/* Goals & missions                                                            */
/* -------------------------------------------------------------------------- */

export const createGoalInput = z.object({
  title: limitedText(120),
  description: limitedText(1000),
  category: z.enum(['learning', 'fitness', 'knowledge', 'skills', 'reading', 'wellbeing', 'digital_habits', 'custom']),
  target: limitedText(200),
  deadline: isoDateSchema.nullable().optional(),
  dailyAvailabilityMinutes: z.number().int().min(5).max(720),
  schedule: scheduleSchema,
  difficulty: z.enum(['easy', 'medium', 'hard']),
  proofRequired: z.boolean().default(true),
});

export const createGoalAIInput = createGoalInput.extend({});

export const updateGoalInput = z
  .object({
    title: limitedText(120).optional(),
    description: limitedText(1000).optional(),
    target: limitedText(200).optional(),
    deadline: isoDateSchema.nullable().optional(),
    status: z.enum(['active', 'paused', 'archived', 'completed']).optional(),
  })
  .refine((v) => Object.keys(v).length > 0, 'nothing to update');

export const startMissionInput = z.object({
  missionId: uidSchema,
});

export const sendProgressInput = z.object({
  missionId: uidSchema,
  progress: z.number().min(0).max(1),
});

export const finishMissionInput = z.object({
  missionId: uidSchema,
  percent: z.number().min(0).max(100),
});

export const setMissionProofInput = z.object({
  missionId: uidSchema,
  proof: z.object({
    type: z.enum(proofTypes),
    metadata: z.record(z.unknown()),
    mediaUrl: z.string().nullable().optional(),
  }),
});

export const forceUpdateStreakInput = z.object({
  goalId: uidSchema,
});

/* -------------------------------------------------------------------------- */
/* Learning                                                                    */
/* -------------------------------------------------------------------------- */

export const requestMaterialUploadInput = z.object({
  fileName: limitedText(255),
  kind: z.enum(['pdf', 'docx', 'pptx', 'txt', 'notes']),
  sizeBytes: z.number().int().positive().max(25 * 1024 * 1024),
});

export const markMaterialUploadedInput = z.object({
  materialId: uidSchema,
  storagePath: z.string().min(5).max(512),
});

export const createLearningPlanInput = z.object({
  materialId: uidSchema,
  deadline: isoDateSchema,
  dailyMinutes: z.number().int().min(5).max(600),
  proofType: z.enum(['quiz', 'code_tests']),
});

export const generateQuizInput = z.object({
  lessonId: uidSchema.nullable().optional(),
  materialId: uidSchema.nullable().optional(),
  goalId: uidSchema.nullable().optional(),
  questionCount: z.number().int().min(3).max(10).default(5),
});

export const submitQuizAttemptInput = z.object({
  quizId: uidSchema,
  selected: z.array(z.number().int().min(0).max(9)).max(20),
});

export const createLessonProofInput = z.object({
  lessonId: uidSchema,
  planId: uidSchema,
  minutesSpent: z.number().int().min(0).max(600),
});

/* -------------------------------------------------------------------------- */
/* Activity                                                                    */
/* -------------------------------------------------------------------------- */

export const startActivityInput = z.object({
  missionId: uidSchema.nullable().optional(),
  kind: z.enum(['running', 'walking', 'cycling', 'meditation', 'reading', 'coding', 'sleep', 'digital_wellbeing', 'custom']),
  targetUnits: z.enum(['distance_km', 'duration_min', 'steps', 'sessions', 'custom']),
  targetValue: z.number().min(0),
  durationMinutes: z.number().int().min(1).max(720),
  sessionToken: z.string().min(8).max(64),
  proofMethod: z.enum(['gps', 'timer', 'steps', 'health', 'manual', 'code']),
});

export const endActivityInput = z.object({
  sessionId: uidSchema,
  elapsedSeconds: z.number().min(0).max(24 * 3600),
  distanceMeters: z.number().min(0).optional(),
  steps: z.number().min(0).optional(),
  route: z
    .array(
      z.object({
        lat: z.number().min(-90).max(90),
        lng: z.number().min(-180).max(180),
        t: z.number().int(),
        accuracyM: z.number().min(0).max(200),
        speedMps: z.number().nullable().optional(),
      }),
    )
    .max(20000),
});

export const checkInActivityInput = z.object({
  sessionId: uidSchema,
});

/* -------------------------------------------------------------------------- */
/* Social                                                                      */
/* -------------------------------------------------------------------------- */

export const createGroupInput = z.object({
  name: limitedText(80),
  description: limitedText(500).default(''),
  emoji: z.string().min(1).max(8),
  defaultStakesPoints: z.number().int().min(0).max(1000).default(100),
});

export const joinGroupInput = z.object({
  invitationCode: z.string().regex(/^[A-Z0-9]{6}$/),
});

export const sendMessageInput = z.object({
  groupId: uidSchema,
  text: limitedText(2000).nullable().optional(),
  kind: z.enum(['text', 'battle_challenge', 'group_event', 'ai_comment']).optional(),
});

export const createBattleInput = z.object({
  groupId: uidSchema,
  challengeeId: uidSchema,
  killCriteria: limitedText(160),
  timeLimitSeconds: z.number().int().min(60).max(2592000),
  stakesPoints: z.number().int().min(0).max(1000),
});

export const tickBattleInput = z.object({
  battleId: uidSchema,
  checkin: z.boolean(),
});

export const resolveBattleInput = z.object({
  battleId: uidSchema,
});

export const proposePunishmentInput = z.object({
  groupId: uidSchema,
  targetUserId: uidSchema,
  title: limitedText(120),
  description: limitedText(1000),
  durationDays: z.number().int().min(1).max(60),
  severity: z.enum(['petty', 'moderate', 'grand']),
  emoji: z.string().min(1).max(8),
  link: z.string().url().nullable().optional(),
});

export const voteInput = z.object({
  punishmentId: uidSchema,
  vote: z.enum(['for', 'against']),
});

export const completePunishmentInput = z.object({
  punishmentId: uidSchema,
  evidence: z.string().nullable().optional(),
});

export const requestCoachMessageInput = z.object({
  goalId: uidSchema.nullable().optional(),
  context: limitedText(1000).default(''),
});

export const simulateGroupAIMessageInput = z.object({
  groupId: uidSchema,
});

/* -------------------------------------------------------------------------- */
/* Notifications & misc                                                        */
/* -------------------------------------------------------------------------- */

export const updateDeviceConnectionInput = z.object({
  pushToken: z.string().nullable().optional(),
  platform: z.enum(['ios', 'android', 'web']),
});

export const saveNotificationPreferenceInput = z.object({
  missionReminder: z.object({ enabled: z.boolean(), timeMinutes: z.number().int().min(0).max(1439) }).optional(),
  streak: z.object({ enabled: z.boolean() }).optional(),
  checkIn: z.object({ enabled: z.boolean(), timeMinutes: z.number().int().min(0).max(1439) }).optional(),
  group: z.object({ enabled: z.boolean() }).optional(),
  battle: z.object({ enabled: z.boolean() }).optional(),
  punishment: z.object({ enabled: z.boolean() }).optional(),
  achievement: z.object({ enabled: z.boolean() }).optional(),
});

/* -------------------------------------------------------------------------- */
/* AI output contracts (server-validated before persistence)                   */
/* -------------------------------------------------------------------------- */

export const aiGoalPlanOutput = z.object({
  summary: z.string().min(1).max(600),
  totalDays: z.number().int().min(1).max(90),
  cadence: z.enum(['daily', 'weekdays', 'weekends', 'custom']),
  difficulty: z.enum(['easy', 'medium', 'hard']),
  days: z
    .array(
      z.object({
        dayIndex: z.number().int().nonnegative(),
        title: z.string().min(1).max(120),
        durationMinutes: z.number().int().min(1).max(720),
        focus: z.string().min(1).max(240),
        proofType: z.enum(proofTypes),
        concept: z.string().min(1).max(120).optional(),
      }),
    )
    .min(3)
    .max(90),
  milestones: z
    .array(z.object({ title: z.string().min(1).max(120), description: z.string().min(1).max(400), index: z.number().int().nonnegative() }))
    .min(0)
    .max(12),
});

export const aiLearningPlanOutput = z.object({
  title: z.string().min(1).max(120),
  totalDays: z.number().int().min(1).max(60),
  dailyMinutes: z.number().int().min(5).max(600),
  topics: z.array(z.string().min(1).max(160)).max(20),
  lessons: z
    .array(
      z.object({
        dayIndex: z.number().int().nonnegative(),
        title: z.string().min(1).max(120),
        summary: z.string().min(1).max(400),
        concepts: z.array(z.string().min(1).max(120)).max(6),
        chunkIds: z.array(z.string()).max(20),
        durationMinutes: z.number().int().min(1).max(720),
      }),
    )
    .min(1)
    .max(60),
});

export const aiQuizOutput = z.array(
  z.object({
    question: z.string().min(3).max(400),
    options: z.array(z.string().min(1).max(200)).length(4),
    correctIndex: z.number().int().min(0).max(3),
    explanation: z.string().min(1).max(500),
    concept: z.string().min(1).max(120),
    codeSnippet: z.string().nullable().optional(),
  }),
);

export const aiCoachOutput = z.object({
  message: z.string().min(1).max(1000),
  emoji: z.string().min(1).max(8).optional(),
});

export const aiGroupMessageOutput = z.object({
  message: z.string().min(1).max(400),
  as: z.string().min(1).max(32),
});

export const aiProofOutput = z.object({
  verdict: z.enum(['verified', 'rejected']),
  confidence: z.number().min(0).max(1),
  reason: z.string().max(400),
});

export const aiRescueOutput = z.object({
  mission: z.object({
    title: z.string().min(1).max(120),
    description: z.string().min(1).max(400),
    durationMinutes: z.number().int().min(1).max(180),
    proofType: z.enum(proofTypes),
    difficulty: z.enum(['easy', 'medium', 'hard']),
  }),
});

export const aiSummarizeOutput = z.object({
  summary: z.string().min(1).max(800),
  topics: z.array(z.string().min(1).max(120)).max(12),
});