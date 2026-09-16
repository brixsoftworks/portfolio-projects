import type { BackendCtx } from './ctx';
import type {
  LearningMaterial,
  LearningMaterialChunk,
  LearningTopic,
  Lesson,
  LearningPlan,
  Quiz,
  QuizQuestion,
} from '@quacko/types';
import { assertDoc, assertInput, assertUser, isOwner } from './ctx';
import {
  createLearningPlanInput,
  generateQuizInput,
  markMaterialUploadedInput,
  requestMaterialUploadInput,
  createLessonProofInput,
} from '@quacko/validation';
import { createNotification } from './notifications';

export async function requestMaterialUpload(ctx: BackendCtx, rawUid: unknown, rawInput: unknown): Promise<LearningMaterial> {
  const uid = assertUser(rawUid);
  const input = assertInput(rawInput, requestMaterialUploadInput);
  const now = ctx.now().toISOString();
  const material: LearningMaterial = {
    id: ctx.store.newId(),
    ownerId: uid,
    title: input.fileName.replace(/\.[^.]+$/, ''),
    fileName: input.fileName,
    kind: input.kind,
    sizeBytes: input.sizeBytes,
    status: 'processing',
    chunkCount: 0,
    topicCount: 0,
    conceptCount: 0,
    summary: null,
    storagePath: null,
    error: null,
    createdAt: now,
    updatedAt: now,
  };
  await ctx.store.transaction(async (tx) => {
    await tx.create('learningMaterials', material);
  });
  return material;
}

export async function markMaterialUploaded(ctx: BackendCtx, rawUid: unknown, rawInput: unknown): Promise<LearningMaterial> {
  const uid = assertUser(rawUid);
  const input = assertInput(rawInput, markMaterialUploadedInput);
  const material = assertDoc(await ctx.store.get<LearningMaterial>('learningMaterials', input.materialId), 'material');
  isOwner(material, uid);
  const updated = await ctx.store.transaction(async (tx) => {
    return assertDoc(
      await tx.update<LearningMaterial>('learningMaterials', material.id, {
        storagePath: input.storagePath,
        status: 'processing',
        updatedAt: ctx.now().toISOString(),
      }),
      'material',
    );
  });
  return updated;
}

/** Server-side text extraction → chunking → AI summary. In demo, truncates text. */
export async function processLearningMaterial(ctx: BackendCtx, materialIdRaw: unknown, ownerUid?: string): Promise<LearningMaterial> {
  const material = assertDoc(await ctx.store.get<LearningMaterial>('learningMaterials', String(materialIdRaw)), 'material');
  if (ownerUid) isOwner(material, ownerUid);
  if (material.status !== 'processing') {
    return material;
  }
  try {
    // Step 1: ingestion — real impl reads from Storage and chunks; demo fabricates a transcript.
    const demoText = `DEMO CONTENT for ${material.title}. ` + Array.from({ length: 6 }, (_, i) => `Section ${i + 1}: key idea about ${material.title.toLowerCase()} in a few sentences of study material.`).join(' ');
    const chunks: LearningMaterialChunk[] = [
      { id: ctx.store.newId(), materialId: material.id, index: 1, text: demoText, wordCount: demoText.split(' ').length, topics: ['core'] },
    ];
    const summaryResult = await ctx.ai.summarizeMaterial({
      title: material.title,
      chunkTexts: chunks.map((c) => c.text),
    });
    const topics: LearningTopic[] = (summaryResult.topics.length ? summaryResult.topics : ['overview'])
      .slice(0, 5)
      .map((t, i) => ({
        id: ctx.store.newId(),
        materialId: material.id,
        title: t,
        order: i,
        chunkIds: chunks.map((c) => c.id),
      }));

    await ctx.store.transaction(async (tx) => {
      for (const c of chunks) await tx.create('learningMaterialChunks', c);
      for (const t of topics) await tx.create('learningTopics', t);
      await tx.update<LearningMaterial>('learningMaterials', material.id, {
        status: 'ready',
        chunkCount: chunks.length,
        topicCount: topics.length,
        conceptCount: topics.length,
        summary: summaryResult.summary,
        error: null,
        updatedAt: ctx.now().toISOString(),
      });
    });
    return (await ctx.store.get<LearningMaterial>('learningMaterials', material.id)) ?? material;
  } catch (err) {
    await ctx.store.transaction(async (tx) => {
      await tx.update<LearningMaterial>('learningMaterials', material.id, {
        status: 'failed',
        error: err instanceof Error ? err.message : 'processing failed',
        updatedAt: ctx.now().toISOString(),
      });
    });
    return (await ctx.store.get<LearningMaterial>('learningMaterials', material.id)) ?? material;
  }
}

/** Build a day-structured learning plan from an AI layout. */
export async function createLearningPlan(ctx: BackendCtx, rawUid: unknown, rawInput: unknown): Promise<LearningPlan> {
  const uid = assertUser(rawUid);
  const input = assertInput(rawInput, createLearningPlanInput);
  const material = assertDoc(await ctx.store.get<LearningMaterial>('learningMaterials', input.materialId), 'material');
  isOwner(material, uid);

  const topics = await ctx.store.find<LearningTopic>('learningTopics', { where: [{ field: 'materialId', equals: material.id }] });
  const plan: LearningPlan = {
    id: ctx.store.newId(),
    materialId: material.id,
    ownerId: uid,
    title: `${material.title} plan`,
    totalDays: Math.max(1, Math.min(30, Math.ceil(topics.length / 1))),
    dailyMinutes: input.dailyMinutes,
    status: 'active',
    createdAt: ctx.now().toISOString(),
    updatedAt: ctx.now().toISOString(),
  };

  const lessons: Lesson[] = [];
  for (let i = 0; i < plan.totalDays; i += 1) {
    const title = topics[i % Math.max(1, topics.length)]?.title ?? `Day ${i + 1}`;
    const lesson = await ctx.ai.generateLesson({
      topic: title,
      concepts: [title],
      chunkText: material.summary ?? '',
      maxMinutes: input.dailyMinutes,
    });
    lessons.push({
      id: ctx.store.newId(),
      planId: plan.id,
      materialId: material.id,
      dayIndex: i,
      title: `${plan.title} — ${title}`,
      summary: lesson.summary,
      concepts: lesson.concepts,
      chunkIds: [],
      durationMinutes: lesson.durationMinutes,
      status: i === 0 ? 'available' : 'locked',
      createdAt: ctx.now().toISOString(),
    });
  }

  await ctx.store.transaction(async (tx) => {
    await tx.create('learningPlans', plan);
    for (const l of lessons) await tx.create('lessons', l);
  });
  await createNotification(ctx, uid, 'mission_reminder', 'Plan ready', `${plan.title} is ready for ${plan.totalDays} days.`, { planId: plan.id });
  return plan;
}

export async function generateQuiz(ctx: BackendCtx, rawUid: unknown, rawInput: unknown): Promise<Quiz> {
  const uid = assertUser(rawUid);
  const input = assertInput(rawInput, generateQuizInput);

  let material: LearningMaterial | null = null;
  let lesson: Lesson | null = null;
  if (input.lessonId) {
    lesson = assertDoc(await ctx.store.get<Lesson>('lessons', input.lessonId), 'lesson');
    const plan = await ctx.store.get<LearningPlan>('learningPlans', lesson.planId);
    if (plan) isOwner(plan, uid);
    material = (await ctx.store.get<LearningMaterial>('learningMaterials', lesson.materialId)) ?? null;
  } else if (input.materialId) {
    material = assertDoc(await ctx.store.get<LearningMaterial>('learningMaterials', input.materialId), 'material');
  }

  const questionsRaw = await ctx.ai.generateQuiz({
    topic: lesson?.title ?? material?.summary ?? 'general knowledge',
    concepts: lesson?.concepts ?? [],
    questionCount: input.questionCount,
    language: 'en',
  });
  const questions: QuizQuestion[] = questionsRaw.map((q) => ({
    id: ctx.store.newId(),
    question: q.question,
    options: q.options,
    correctIndex: q.correctIndex,
    explanation: q.explanation,
    concept: q.concept,
    codeSnippet: q.codeSnippet ?? null,
  }));

  const quiz: Quiz = {
    id: ctx.store.newId(),
    lessonId: lesson?.id ?? null,
    materialId: material?.id ?? null,
    goalId: input.goalId ?? null,
    title: `Quiz: ${lesson?.title ?? material?.title ?? 'general'}`,
    proofType: 'learning',
    questions,
    passingScore: 0.7,
    status: 'ready',
    createdAt: ctx.now().toISOString(),
  };
  await ctx.store.transaction(async (tx) => {
    await tx.create('quizzes', quiz);
  });
  return quiz;
}

export async function createLessonProof(ctx: BackendCtx, rawUid: unknown, rawInput: unknown): Promise<Lesson> {
  const uid = assertUser(rawUid);
  const input = assertInput(rawInput, createLessonProofInput);
  const lesson = assertDoc(await ctx.store.get<Lesson>('lessons', input.lessonId), 'lesson');
  const plan = assertDoc(await ctx.store.get<LearningPlan>('learningPlans', lesson.planId), 'plan');
  isOwner(plan, uid);
  if (input.minutesSpent >= Math.min(lesson.durationMinutes, 5)) {
    await ctx.store.transaction(async (tx) => {
      await tx.set('lessons', { ...lesson, id: lesson.id, status: 'completed' });
    });
  }
  return lesson;
}