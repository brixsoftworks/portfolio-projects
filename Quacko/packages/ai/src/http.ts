import { z } from 'zod';
import type { AIProvider } from './interfaces';
import type {
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
import {
  aiCoachOutput,
  aiGoalPlanOutput,
  aiGroupMessageOutput,
  aiProofOutput,
  aiQuizOutput,
  aiRescueOutput,
  aiSummarizeOutput,
} from '@quacko/validation';

export interface HttpProviderConfig {
  baseUrl: string;
  apiKey?: string;
  model: string;
  /** Ask the model for a single JSON object. */
  jsonMode?: boolean;
  timeoutMs?: number;
}

interface ChatRequest {
  model: string;
  messages: { role: 'system' | 'user' | 'assistant'; content: string }[];
  temperature?: number;
  response_format?: { type: 'json_object' };
}

function parseJsonLoose(text: string): unknown {
  const trimmed = text.trim();
  const fenced = trimmed.match(/^```(?:json)?\s*([\s\S]*?)\s*```$/);
  const body = fenced?.[1] ?? trimmed;
  const start = body.indexOf('{');
  const end = body.lastIndexOf('}');
  if (start === -1 || end === -1 || end <= start) throw new Error('No JSON object in model response');
  return JSON.parse(body.slice(start, end + 1)) as unknown;
}

export function createHttpProvider(config: HttpProviderConfig): AIProvider {
  const headers: Record<string, string> = {
    'content-type': 'application/json',
  };
  if (config.apiKey) headers.authorization = `Bearer ${config.apiKey}`;

  async function complete(
    system: string,
    user: string,
    schema: z.ZodType<unknown>,
  ): Promise<unknown> {
    const messages: ChatRequest['messages'] = [
      { role: 'system', content: system },
      { role: 'user', content: user },
    ];
    const body: ChatRequest = {
      model: config.model,
      messages,
      temperature: 0.4,
    };
    if (config.jsonMode !== false) {
      body.response_format = { type: 'json_object' };
      system = `${system}\nRespond with a single JSON object only.`;
      messages[0] = { role: 'system', content: system };
    }
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), config.timeoutMs ?? 60_000);
    try {
      const res = await fetch(`${config.baseUrl.replace(/\/$/, '')}/chat/completions`, {
        method: 'POST',
        headers,
        body: JSON.stringify(body),
        signal: controller.signal,
      });
      if (!res.ok) {
        const detail = await res.text();
        throw new Error(`AI HTTP ${res.status}: ${detail.slice(0, 400)}`);
      }
      const data = (await res.json()) as { choices?: { message?: { content?: string } }[] };
      const content = data.choices?.[0]?.message?.content;
      if (!content) throw new Error('Empty completion');
      const parsed = parseJsonLoose(content);
      const result = schema.safeParse(parsed);
      if (!result.success) {
        throw new Error(`AI output failed validation: ${result.error.message.slice(0, 500)}`);
      }
      return result.data;
    } finally {
      clearTimeout(timer);
    }
  }

  return {
    name: `http:${config.model}`,
    async ping() {
      return { ok: true as const };
    },
    async generatePlan(input: GoalPromptInput) {
      const out = await complete(
        'You are Quacko, a sharp goal coach. Design a precise daily mission deck (max 30 days) with fresh, concrete tasks per day and milestones.',
        JSON.stringify(input),
        aiGoalPlanOutput,
      );
      return { ...(out as z.infer<typeof aiGoalPlanOutput>), generatedAt: new Date().toISOString(), source: 'ai' };
    },
    async generateLesson(input: LessonPromptInput) {
      return {
        title: `Mastering ${input.topic}`,
        summary: `Focused walkthrough of ${input.topic} drawn from your material.`,
        concepts: input.concepts.slice(0, 5),
        chunkIds: input.chunkText ? ['chunk'] : [],
        durationMinutes: Math.min(input.maxMinutes || 20, 45),
      };
    },
    async generateQuiz(input: QuizPromptInput) {
      const out = await complete(
        `Write ${input.questionCount} multiple-choice questions on "${input.topic}". Follow the JSON exactly, 4 options each, one correctIndex.`,
        JSON.stringify(input),
        z.object({ questions: aiQuizOutput }),
      );
      return (out as { questions: z.infer<typeof aiQuizOutput> }).questions;
    },
    async summarizeMaterial(input: SummaryPromptInput) {
      const out = await complete(
        'Summarize the study material into an actionable long-form summary and up to 12 topic labels.',
        JSON.stringify(input),
        aiSummarizeOutput,
      );
      return out as z.infer<typeof aiSummarizeOutput>;
    },
    async generateCoachMessage(input: CoachPromptInput) {
      const out = await complete(
        'You are Quacko, the duck coach. Reply with a short motivating message and an emoji. JSON only.',
        JSON.stringify(input),
        aiCoachOutput,
      );
      const parsed = out as z.infer<typeof aiCoachOutput>;
      return { message: parsed.message, emoji: parsed.emoji ?? '🦆' };
    },
    async generateGroupMessage(input: GroupMessagePromptInput) {
      const out = await complete(
        'You briefly join a group chat. Reply in character as "Quacko" with a short, energetic line. JSON only.',
        JSON.stringify(input),
        aiGroupMessageOutput,
      );
      const parsed = out as z.infer<typeof aiGroupMessageOutput>;
      return { message: parsed.message, as: parsed.as };
    },
    async analyzeProof(input: ProofPromptInput) {
      const out = await complete(
        'Judge whether this proof submission plausibly matches the mission. Return verdict + confidence + short reason.',
        JSON.stringify(input),
        aiProofOutput,
      );
      return out as z.infer<typeof aiProofOutput>;
    },
    async generateRescueMission(input: RescuePromptInput) {
      const out = await complete(
        'Design a small (easy) rescue mission to get the user back on a broken goal streak. JSON only.',
        JSON.stringify(input),
        aiRescueOutput,
      );
      return (out as z.infer<typeof aiRescueOutput>).mission;
    },
    async generateGame(input: GamePromptInput) {
      const out = await complete(
        `Produce 5 engaging ${input.gameType} questions for a group game. JSON only.`,
        JSON.stringify(input),
        z.object({ questions: z.array(z.any()).max(10) }),
      );
      return (out as { questions: unknown[] }).questions as never[];
    },
  };
}