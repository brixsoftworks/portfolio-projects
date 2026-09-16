export type EntityId = string;

/** ISO-8601 UTC timestamp. All authoritative timestamps are server-generated. */
export type IsoDate = string;

export type Timestamp = { toDate: () => Date; toMillis: () => number; seconds: number; nanoseconds: number };

export type FireTimestamp = Timestamp | IsoDate | Date;

export const CategoryEnum = [
  'learning',
  'fitness',
  'knowledge',
  'skills',
  'reading',
  'wellbeing',
  'digital_habits',
  'custom',
] as const;
export type GoalCategory = (typeof CategoryEnum)[number];

export const DifficultyEnum = ['easy', 'medium', 'hard'] as const;
export type Difficulty = (typeof DifficultyEnum)[number];

export const DayOfWeek = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'] as const;
export type DayOfWeek = (typeof DayOfWeek)[number];

export const CadenceEnum = ['daily', 'weekdays', 'weekends', 'custom'] as const;
export type Cadence = (typeof CadenceEnum)[number];

/** A minute-of-day window, e.g. { startMinutes: 6*60, endMinutes: 12*60 }. */
export interface TimeWindow {
  startMinutes: number;
  endMinutes: number;
}

export interface Schedule {
  cadence: Cadence;
  days: DayOfWeek[];
  preferredWindows: TimeWindow[];
  /** IANA timezone name used for streak/day boundaries. */
  timezone: string;
}

export interface NameValue {
  code: string;
  label: string;
}

export interface PerUserMarker {
  createdAt: IsoDate;
  createdBy: EntityId | 'system';
}