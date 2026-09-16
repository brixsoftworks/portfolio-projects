export type FieldValue =
  | { kind: 'increment'; amount: number }
  | { kind: 'serverTimestamp' };

export interface FindOptions<T = Record<string, unknown>> {
  where?: { field: keyof T & string; equals: unknown }[];
  orderBy?: { field: keyof T & string; direction: 'asc' | 'desc' };
  limit?: number;
}

/** Atomic unit of work. Implemented over Firestore transactions or in-memory. */
export interface Tx {
  get<T>(collection: string, id: string): Promise<T | null>;
  create<T extends { id: string }>(collection: string, doc: T): Promise<T>;
  set<T extends { id: string }>(collection: string, doc: T): Promise<void>;
  update<T extends { id: string }>(
    collection: string,
    id: string,
    patch: Partial<T> & { [k: string]: unknown },
  ): Promise<T | null>;
  delete(collection: string, id: string): Promise<void>;
}

export interface Store {
  /** Run fn atomically. Must be short-lived; no reads of other transactions. */
  transaction<T>(fn: (tx: Tx) => Promise<T>): Promise<T>;
  /** Plain non-transaction reads for query/list workloads. */
  find<T>(collection: string, options?: FindOptions<T>): Promise<T[]>;
  get<T>(collection: string, id: string): Promise<T | null>;
  newId(): string;
}

export class NotFoundError extends Error {
  readonly kind = 'not-found';
  constructor(message: string) {
    super(message);
    this.name = 'NotFoundError';
  }
}

export class ConflictError extends Error {
  readonly kind = 'conflict';
  constructor(message: string) {
    super(message);
    this.name = 'ConflictError';
  }
}

export class ValidationFailure extends Error {
  readonly kind = 'validation';
  constructor(message: string) {
    super(message);
    this.name = 'ValidationFailure';
  }
}

export class UnauthorizedError extends Error {
  readonly kind = 'unauthorized';
  constructor(message: string) {
    super(message);
    this.name = 'UnauthorizedError';
  }
}