import type { EntityId, IsoDate } from './common';

export const GameStatusEnum = [
  'lobby',
  'live',
  'finished',
  'cancelled',
] as const;
export type GameStatus = (typeof GameStatusEnum)[number];

export interface GameSession {
  id: EntityId;
  groupId: EntityId | null;
  gameId: EntityId | null;
  type:
    | 'speed_quiz'
    | 'trivia'
    | 'word_battle'
    | 'memory'
    | 'estimation'
    | 'daily_puzzle'
    | 'guess_the_friend'
    | 'mystery';
  status: GameStatus;
  questionIds: string[] | null;
  startedAt: IsoDate | null;
  finishedAt: IsoDate | null;
  settings: Record<string, unknown>;
}

export interface GameScore {
  id: EntityId;
  gameSessionId: EntityId;
  userId: EntityId;
  score: number;
  rank: number;
  createdAt: IsoDate;
}

export interface GameQuestion {
  id: EntityId;
  type: 'multi_choice' | 'word' | 'memory' | 'estimate' | 'mystery';
  prompt: string;
  hint: string | null;
  options: string[] | null;
  answer: string | null;
  verify: 'string' | 'numeric_tolerance' | 'mcq' | null;
  tolerance: number | null;
}

export interface DailyWord {
  id: EntityId;
  word: string;
  day: string;
  definition: string | null;
}