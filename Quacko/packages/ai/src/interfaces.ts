import type { ProofType, WeakArea } from '@quacko/types';
import type { z } from 'zod';
import type { aiQuizOutput } from '@quacko/validation';

export interface GoalPromptInput {
  title: string;
  description: string;
  category: string;
  target: string;
  deadline: string | null;
  dailyAvailabilityMinutes: number;
  difficulty: 'easy' | 'medium' | 'hard';
  proofRequired: boolean;
  timezone: string;
}

export interface LessonPromptInput {
  topic: string;
  concepts: string[];
  chunkText: string;
  maxMinutes: number;
}

export interface QuizPromptInput {
  topic: string;
  concepts: string[];
  questionCount: number;
  language: string;
}

export interface SummaryPromptInput {
  title: string;
  chunkTexts: string[];
}

export interface CoachPromptInput {
  goalTitle: string;
  streak: number;
  recentNote: string;
  context: string;
}

export interface GroupMessagePromptInput {
  groupName: string;
  recentMessages: string[];
}

export interface ProofPromptInput {
  missionTitle: string;
  proofType: ProofType;
  metadata: Record<string, unknown>;
  weakness: WeakArea | null;
}

export interface RescuePromptInput {
  goalTitle: string;
  failedDay: string;
  weakConcepts: string[];
  timezone: string;
}

export interface GamePromptInput {
  gameType: string;
  members: { name: string; xp: number }[];
  language: string;
}

/** Unified AI provider that the backend services call. */
export interface AIProvider {
  generatePlan(input: GoalPromptInput): Promise<import('@quacko/types').GoalAIPlan>;
  generateLesson(input: LessonPromptInput): Promise<{ title: string; summary: string; concepts: string[]; chunkIds: string[]; durationMinutes: number }>;
  generateQuiz(input: QuizPromptInput): Promise<z.infer<typeof aiQuizOutput>>;
  summarizeMaterial(input: SummaryPromptInput): Promise<{ summary: string; topics: string[] }>;
  generateCoachMessage(input: CoachPromptInput): Promise<{ message: string; emoji: string }>;
  generateGroupMessage(input: GroupMessagePromptInput): Promise<{ message: string; as: string }>;
  analyzeProof(input: ProofPromptInput): Promise<{ verdict: 'verified' | 'rejected'; confidence: number; reason: string }>;
  generateRescueMission(input: RescuePromptInput): Promise<{
    title: string;
    description: string;
    durationMinutes: number;
    proofType: ProofType;
    difficulty: 'easy' | 'medium' | 'hard';
  }>;
  generateGame(input: GamePromptInput): Promise<
    { type: string; prompt: string; options: string[] | null; answer: string | null; hint: string | null }[]
  >;
  /** Warm up / connectivity check. Demo returns instantly. */
  ping(): Promise<{ ok: true }>;
  readonly name: string;
}

export function isAIProvider(value: unknown): value is AIProvider {
  return (
    typeof value === 'object' &&
    value !== null &&
    'generatePlan' in value &&
    'generateQuiz' in value &&
    'name' in value
  );
}