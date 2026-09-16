import { nextScheduledDayKeys } from '@quacko/domain/src/mission';
import type { GoalCategory, ProofType } from '@quacko/types';
import type {
  AIProvider,
  CoachPromptInput,
  GamePromptInput,
  GoalPromptInput,
  GroupMessagePromptInput,
  LessonPromptInput,
  ProofPromptInput,
  QuizPromptInput,
  RescuePromptInput,
  SummaryPromptInput,
} from './interfaces';

const FOCI: Record<GoalCategory, string[]> = {
  learning: ['Active recall', 'Spaced repetition', 'Build mental models'],
  fitness: ['Zone 2 base', 'Strides', 'Mobility'],
  knowledge: ['Summarize', 'Connect to prior ideas', 'Explain to a friend'],
  skills: ['Deliberate practice', 'Tiny iterations', 'Feedback loops'],
  reading: ['Chapters', 'Margin notes', 'Reflective summary'],
  wellbeing: ['Breath work', 'Gratitude', 'Body scan'],
  digital_habits: ['Phone-free block', 'App deleter', 'Context switch tracking'],
  custom: ['Warm up', 'Core reps', 'Deliberate focus'],
};

const PROOF_FOR_CATEGORY: Record<GoalCategory, ProofType> = {
  learning: 'quiz',
  fitness: 'gps',
  knowledge: 'timer',
  skills: 'code_tests',
  reading: 'timer',
  wellbeing: 'timer',
  digital_habits: 'timer',
  custom: 'manual_log',
};

const QUESTS = [
  'Focus session',
  'Mini project',
  'Review & reflect',
  'Test yourself',
  'Teach it back',
  'Timed sprint',
  'Skill drill',
  'Read & note',
];

/**
 * Deterministic, zero-dependency "AI" used in demo/CI/dev mode. Produces
 * schema-valid output so the whole pipeline is exercised without a key.
 */
export class DemoProvider implements AIProvider {
  readonly name = 'demo';

  async ping() {
    return { ok: true as const };
  }

  async generatePlan(input: GoalPromptInput) {
    const category = input.category as GoalCategory;
    const foci = FOCI[category] ?? FOCI.custom;
    const days = Math.min(input.dailyAvailabilityMinutes < 30 ? 14 : 30, 30);
    const keys = nextScheduledDayKeys('2026-01-01', days, { cadence: 'daily', days: [] });
    return {
      summary:
        `${days}-day plan to make "${input.title}" a ritual. ` +
        `You'll invest ${input.dailyAvailabilityMinutes} min/day with proof every session.`,
      totalDays: days,
      cadence: 'daily' as const,
      difficulty: input.difficulty,
      generatedAt: new Date().toISOString(),
      source: 'ai' as const,
      days: keys.map((_, i) => ({
        dayIndex: i + 1,
        title: QUESTS[i % QUESTS.length] ?? 'Focus session',
        durationMinutes: Math.min(input.dailyAvailabilityMinutes, 60),
        focus: `${foci[i % foci.length] ?? foci[0] ?? 'Focus'} on ${input.title}`,
        proofType: input.proofRequired ? (PROOF_FOR_CATEGORY[category] ?? 'manual_log') : 'manual_log',
      })),
      milestones: [
        { index: Math.max(1, Math.floor(days / 3)), title: 'First checkpoint', description: 'Consistent start — momentum is the goal.' },
        { index: Math.max(2, Math.floor((2 * days) / 3)), title: 'Halfway habit', description: 'The routine now runs on autopilot.' },
        { index: days, title: 'Goal achieved', description: 'You showed up for an entire cycle.' },
      ],
    };
  }

  async generateLesson(_input: LessonPromptInput) {
    return {
      title: 'Core concept walkthrough',
      summary: 'A guided, self-paced lesson distilled from your material.',
      concepts: _input.concepts.slice(0, 4),
      chunkIds: _input.chunkText ? ['demo-chunk'] : [],
      durationMinutes: Math.min(_input.maxMinutes || 20, 45),
    };
  }

  async generateQuiz(input: QuizPromptInput) {
    const count = input.questionCount || 5;
    const questions = Array.from({ length: count }, (_, i) => ({
      question: `${input.topic} — question ${i + 1}`,
      options: ['A is correct', 'B', 'C', 'D'],
      correctIndex: 0,
      explanation: 'Demo answer key; every choice A is correct here.',
      concept: input.concepts[i % Math.max(1, input.concepts.length)] ?? input.topic,
      codeSnippet: null as string | null,
    }));
    return questions;
  }

  async summarizeMaterial(input: SummaryPromptInput) {
    const topics = input.chunkTexts.length
      ? `demo, ${input.title.toLowerCase()}`.split(',').map((s) => s.trim()).slice(0, 6)
      : ['demo'];
    return {
      summary: `${input.title}: a demo summary of your uploaded material. Replace this text with real AI highlights in production.`,
      topics,
    };
  }

  async generateCoachMessage(input: CoachPromptInput) {
    return {
      message:
        input.streak > 0
          ? `Nice! You're on a ${input.streak}-day streak for "${input.goalTitle}". Keep the chain alive.`
          : `Fresh start on "${input.goalTitle}". Show up today and it counts.`,
      emoji: '🦆',
    };
  }

  async generateGroupMessage(input: GroupMessagePromptInput) {
    return {
      message: `Cheering on ${input.groupName}! ${input.recentMessages.length} messages today — keep the energy up.`,
      as: 'Quacko',
    };
  }

  async analyzeProof(input: ProofPromptInput) {
    const metadata = input.metadata;
    const likely = metadata && metadata.durationSeconds && Number(metadata.durationSeconds) > 0;
    return {
      verdict: (likely ? 'verified' : 'rejected') as 'verified' | 'rejected',
      confidence: likely ? 0.9 : 0.2,
      reason: likely ? 'Media appears to match the requested activity.' : 'No usable content detected.',
    };
  }

  async generateRescueMission(input: RescuePromptInput) {
    const concept = input.weakConcepts[0] ?? 'your weak spots';
    return {
      title: 'Comeback rescue',
      description: `Regain momentum on "${input.goalTitle}" after missing ${input.failedDay}. Focus: ${concept}.`,
      durationMinutes: 15,
      proofType: 'timer' as ProofType,
      difficulty: 'easy' as const,
    };
  }

  async generateGame(input: GamePromptInput) {
    const first = input.members[0];
    return Array.from({ length: 5 }, (_, i) => ({
      type: input.gameType,
      prompt: `Demo prompt ${i + 1} for ${input.gameType}`,
      options: ['A', 'B', 'C', 'D'],
      answer: 'A',
      hint: null as string | null,
      member: first?.name || 'you',
    }));
  }
}