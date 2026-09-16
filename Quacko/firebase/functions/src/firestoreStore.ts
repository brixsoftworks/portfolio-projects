import { Firestore, Timestamp } from 'firebase-admin/firestore';
import type { FindOptions, Store, Tx } from '@quacko/backend';

/**
 * Real Firestore adapter for the shared backend Store contract.
 * Enforces the same invariants as InMemoryStore but with ACID transactions
 * on the production database.
 */
export class FirestoreStore implements Store {
  readonly name = 'firestore';
  private readonly db: Firestore;

  constructor(db: Firestore) {
    this.db = db;
  }

  newId(): string {
    return this.db.collection('_ids').doc().id;
  }

  async get<T>(collection: string, id: string): Promise<T | null> {
    const snap = await this.db.collection(collection).doc(id).get();
    if (!snap.exists) return null;
    return { id, ...snap.data() } as T;
  }

  async find<T>(collection: string, options: FindOptions<T> = {}): Promise<T[]> {
    let query: FirebaseFirestore.Query = this.db.collection(collection);
    for (const w of options.where ?? []) {
      query = query.where(w.field as string, '==', w.equals);
    }
    if (options.orderBy) {
      query = query.orderBy(options.orderBy.field as string, options.orderBy.direction);
    }
    if (options.limit) {
      query = query.limit(options.limit);
    }
    const snap = await query.get();
    return snap.docs.map((d) => ({ id: d.id, ...d.data() }) as T);
  }

  async transaction<T>(fn: (tx: Tx) => Promise<T>): Promise<T> {
    return this.db.runTransaction(async (t) => {
      const tx: Tx = {
        get: async <TDoc,>(c: string, id: string) => {
          const snap = await t.get(this.db.collection(c).doc(id));
          if (!snap.exists) return null;
          return { id, ...snap.data() } as TDoc;
        },
        create: async <TDoc extends { id: string }>(c: string, doc: TDoc) => {
          const ref = this.db.collection(c).doc(doc.id);
          const snap = await t.get(ref);
          if (snap.exists) throw new Error(`create conflict on ${c}/${doc.id}`);
          t.create(ref, { ...doc });
          return doc;
        },
        set: async <TDoc extends { id: string }>(c: string, doc: TDoc) => {
          t.set(this.db.collection(c).doc(doc.id), { ...doc });
        },
        update: async <TDoc extends { id: string }>(
          c: string,
          id: string,
          patch: Partial<TDoc> & { [k: string]: unknown },
        ) => {
          const ref = this.db.collection(c).doc(id);
          const snap = await t.get(ref);
          if (!snap.exists) return null;
          t.update(ref, { ...patch });
          return { id, ...snap.data(), ...patch } as TDoc;
        },
        delete: async (c: string, id: string) => {
          t.delete(this.db.collection(c).doc(id));
        },
      };
      return fn(tx);
    });
  }
}

export function toFirestoreValue<T extends Record<string, unknown>>(doc: T): T {
  const out: Record<string, unknown> = {};
  for (const [k, v] of Object.entries(doc)) {
    out[k] = v instanceof Date ? Timestamp.fromDate(v) : v;
  }
  return out as T;
}