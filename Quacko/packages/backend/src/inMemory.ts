import type { FindOptions, Store, Tx } from './store';

const randId = () =>
  Array.from({ length: 20 }, () => 'abcdefghijklmnopqrstuvwxyz0123456789'[Math.floor(Math.random() * 36)] ?? 'a').join('');

export interface InMemoryStoreOptions {
  seed?: Record<string, Record<string, Record<string, unknown>>>;
  newId?: () => string;
}

/**
 * In-memory Store for demo mode, tests, and the dev preview backend.
 * Not a fake: it enforces the exact same invariants as the Firestore adapter
 * because every mutation goes through the shared backend services.
 */
export class InMemoryStore implements Store {
  private readonly data: Map<string, Map<string, Record<string, unknown>>>;
  readonly _makeId: () => string;
  readonly name = 'in-memory';

  constructor(options: InMemoryStoreOptions = {}) {
    this._makeId = options.newId ?? randId;
    this.data = new Map();
    if (options.seed) {
      for (const [collection, docs] of Object.entries(options.seed)) {
        const col = new Map<string, Record<string, unknown>>();
        for (const [id, doc] of Object.entries(docs)) col.set(id, structuredClone(doc));
        this.data.set(collection, col);
      }
    }
  }

  newId(): string {
    return this._makeId();
  }

  private col(collection: string): Map<string, Record<string, unknown>> {
    let c = this.data.get(collection);
    if (!c) {
      c = new Map();
      this.data.set(collection, c);
    }
    return c;
  }

  async transaction<T>(fn: (tx: Tx) => Promise<T>): Promise<T> {
    const tx: Tx = {
      get: async (collection, id) => {
        const doc = this.col(collection).get(id);
        return doc ? (structuredClone(doc) as never) : null;
      },
      create: async (collection, doc) => {
        const col = this.col(collection);
        if (col.has(doc.id)) throw new Error(`create conflict on ${collection}/${doc.id}`);
        col.set(doc.id, structuredClone(doc as Record<string, unknown>));
        return structuredClone(doc);
      },
      set: async (collection, doc) => {
        this.col(collection).set(doc.id, structuredClone(doc as Record<string, unknown>));
      },
      update: async (collection, id, patch) => {
        const col = this.col(collection);
        const existing = col.get(id);
        if (!existing) return null;
        const merged = { ...existing, ...patch, id } as Record<string, unknown>;
        col.set(id, merged);
        return structuredClone(merged) as never;
      },
      delete: async (collection, id) => {
        this.col(collection).delete(id);
      },
    };
    return fn(tx);
  }

  async get<T>(collection: string, id: string): Promise<T | null> {
    const doc = this.col(collection).get(id);
    return doc ? (structuredClone(doc) as T) : null;
  }

  async find<T>(collection: string, options: FindOptions<T> = {}): Promise<T[]> {
    let docs = [...this.col(collection).values()].map((d) => structuredClone(d) as T);
    for (const w of options.where ?? []) {
      docs = docs.filter((d) => (d as Record<string, unknown>)[w.field] === w.equals);
    }
    if (options.orderBy) {
      const { field, direction } = options.orderBy;
      docs.sort((a, b) => {
        const av = (a as Record<string, unknown>)[field] as string | number;
        const bv = (b as Record<string, unknown>)[field] as string | number;
        if (av < bv) return direction === 'asc' ? -1 : 1;
        if (av > bv) return direction === 'asc' ? 1 : -1;
        return 0;
      });
    }
    if (options.limit) docs = docs.slice(0, options.limit);
    return docs;
  }
}