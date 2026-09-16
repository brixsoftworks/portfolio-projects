import type { AIProvider } from '@quacko/ai';
import type { z } from 'zod';
import type { Store } from './store';
import { NotFoundError, UnauthorizedError, ValidationFailure } from './store';

export interface BackendCtx {
  store: Store;
  ai: AIProvider;
  now: () => Date;
}

export function assertUser(uid: unknown): string {
  if (typeof uid !== 'string' || uid.length < 3) {
    throw new UnauthorizedError('missing or invalid auth uid');
  }
  return uid;
}

export function assertDoc<T>(doc: T | null, what = 'document'): T {
  if (!doc) throw new NotFoundError(`${what} not found`);
  return doc;
}

export function isOwner<T extends { ownerId?: string }>(doc: T, uid: string): void {
  if (doc.ownerId != null && doc.ownerId !== uid) throw new UnauthorizedError('not the owner');
}

export function assertInput<Schema extends z.ZodTypeAny>(input: unknown, schema: Schema): z.infer<Schema> {
  const r = schema.safeParse(input);
  if (!r.success) throw new ValidationFailure(r.error.message);
  return r.data;
}