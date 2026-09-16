import type { EntityId, IsoDate } from './common';

export const MaterialKindEnum = ['pdf', 'docx', 'pptx', 'txt', 'notes'] as const;
export type MaterialKind = (typeof MaterialKindEnum)[number];

export const MaterialStatusEnum = [
  'uploading',
  'processing',
  'ready',
  'failed',
  'deleted',
] as const;
export type MaterialStatus = (typeof MaterialStatusEnum)[number];

export interface LearningMaterial {
  id: EntityId;
  ownerId: EntityId;
  title: string;
  fileName: string;
  kind: MaterialKind;
  sizeBytes: number;
  status: MaterialStatus;
  /** Fragment count produced by server extraction. */
  chunkCount: number;
  topicCount: number;
  conceptCount: number;
  /** Long/planning summary derived server-side. */
  summary: string | null;
  storagePath: string | null;
  error: string | null;
  createdAt: IsoDate;
  updatedAt: IsoDate;
}

export interface LearningMaterialChunk {
  id: EntityId;
  materialId: EntityId;
  index: number;
  text: string;
  wordCount: number;
  topics: string[];
}

export interface LearningTopic {
  id: EntityId;
  materialId: EntityId;
  title: string;
  /** Ordered reading order. */
  order: number;
  chunkIds: string[];
}

export interface LearningConcept {
  id: EntityId;
  materialId: EntityId;
  topicId: EntityId;
  name: string;
  /** Prerequisites by concept name. */
  dependsOn: string[];
}

export interface LearningPlanFocusInput {
  materialId: EntityId;
  deadline: IsoDate;
  dailyMinutes: number;
  proofType: 'quiz' | 'code_tests';
}

export interface LearningPlan {
  id: EntityId;
  materialId: EntityId;
  ownerId: EntityId;
  title: string;
  totalDays: number;
  dailyMinutes: number;
  status: 'draft' | 'active' | 'completed' | 'paused';
  createdAt: IsoDate;
  updatedAt: IsoDate;
}

export interface Lesson {
  id: EntityId;
  planId: EntityId;
  materialId: EntityId;
  dayIndex: number;
  title: string;
  summary: string;
  concepts: string[];
  chunkIds: string[];
  durationMinutes: number;
  status: 'locked' | 'available' | 'completed';
  createdAt: IsoDate;
}

export interface PracticeItem {
  id: EntityId;
  lessonId: EntityId;
  prompt: string;
  starterCode: string | null;
  expected: string | null;
}

export interface QuizQuestion {
  id: string;
  question: string;
  options: string[];
  correctIndex: number;
  explanation: string;
  concept: string;
  codeSnippet: string | null;
}

export interface Quiz {
  id: EntityId;
  lessonId: EntityId | null;
  materialId: EntityId | null;
  goalId: EntityId | null;
  title: string;
  proofType: 'learning' | 'group';
  questions: QuizQuestion[];
  passingScore: number; // 0..1
  status: 'draft' | 'ready' | 'done';
  createdAt: IsoDate;
}

export interface QuizAttempt {
  id: EntityId;
  quizId: EntityId;
  userId: EntityId;
  selected: number[];
  score: number; // 0..1 server computed
  passed: boolean;
  createdAt: IsoDate;
}

export interface ConceptMastery {
  id: EntityId;
  userId: EntityId;
  materialId: EntityId;
  conceptId: EntityId;
  conceptName: string;
  mastery: number; // 0..1
  attempts: number;
  correct: number;
  lastCorrect: boolean;
  updatedAt: IsoDate;
}

export interface WeakArea extends ConceptMastery {
  weaknessScore: number;
  locked: boolean;
}