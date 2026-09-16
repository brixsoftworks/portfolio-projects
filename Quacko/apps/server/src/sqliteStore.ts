import fs from 'node:fs';
import path from 'node:path';
import Database from 'better-sqlite3';
import type { FindOptions, Store, Tx } from '@quacko/backend';

const ID_ALPHABET = 'abcdefghijklmnopqrstuvwxyz0123456789';
const randId = (): string =>
  Array.from({ length: 20 }, () => ID_ALPHABET[Math.floor(Math.random() * ID_ALPHABET.length)] ?? 'a').join('');

/**
 * SQLite-backed Store for the self-hosted server.
 *
 * Mirrors InMemoryStore semantics exactly (create-conflict on duplicate ids,
 * transactions that see their own uncommitted writes) so the shared backend
 * services behave identically in demo mode, tests, and production.
 *
 * Writes are serialized with an in-process mutex: only one logical
 * `transaction(fn)` runs at a time, and each `fn` runs between BEGIN/COMMIT.
 */
export class SqliteStore implements Store {
  private readonly db: Database.Database;
  private serial: Promise<unknown> = Promise.resolve();
  readonly name = 'sqlite';

  constructor(file: string) {
    if (file !== ':memory:') fs.mkdirSync(path.dirname(file), { recursive: true });
    this.db = new Database(file);
    this.db.pragma('journal_mode = WAL');
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS kv (
        collection TEXT NOT NULL,
        id         TEXT NOT NULL,
        doc        TEXT NOT NULL,
        PRIMARY KEY (collection, id)
      ) WITHOUT ROWID
    `);
  }

  newId(): string {
    return randId();
  }

  private getStmt(): Database.Statement {
    return this.db.prepare('SELECT doc FROM kv WHERE collection = ? AND id = ?');
  }

  private putStmt(): Database.Statement {
    return this.db.prepare(
      'INSERT INTO kv (collection, id, doc) VALUES (?, ?, ?) ON CONFLICT (collection, id) DO UPDATE SET doc = excluded.doc',
    );
  }

  private delStmt(): Database.Statement {
    return this.db.prepare('DELETE FROM kv WHERE collection = ? AND id = ?');
  }

  private allStmt(): Database.Statement {
    return this.db.prepare('SELECT id, doc FROM kv WHERE collection = ?');
  }

  async get<T>(collection: string, id: string): Promise<T | null> {
    const row = this.getStmt().get(collection, id) as { doc: string } | undefined;
    return row ? (JSON.parse(row.doc) as T) : null;
  }

  async find<T>(collection: string, options: FindOptions<T> = {}): Promise<T[]> {
    const rows = this.allStmt().all(collection) as { id: string; doc: string }[];
    let docs = rows.map((r) => JSON.parse(r.doc) as T);
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

  transaction<T>(fn: (tx: Tx) => Promise<T>): Promise<T> {
    return this.runExclusive(async () => {
      this.db.exec('BEGIN IMMEDIATE');
      try {
        const result = await fn(this.makeTx());
        this.db.exec('COMMIT');
        return result;
      } catch (err) {
        this.db.exec('ROLLBACK');
        throw err;
      }
    });
  }

  private makeTx(): Tx {
    return {
      get: async <T>(collection: string, id: string): Promise<T | null> => {
        const row = this.getStmt().get(collection, id) as { doc: string } | undefined;
        return row ? (JSON.parse(row.doc) as T) : null;
      },
      create: async <T extends { id: string }>(collection: string, doc: T): Promise<T> => {
        const existing = this.getStmt().get(collection, doc.id);
        if (existing) throw new Error(`create conflict on ${collection}/${doc.id}`);
        this.putStmt().run(collection, doc.id, JSON.stringify(doc));
        return doc;
      },
      set: async <T extends { id: string }>(collection: string, doc: T): Promise<void> => {
        this.putStmt().run(collection, doc.id, JSON.stringify(doc));
      },
      update: async <T extends { id: string }>(
        collection: string,
        id: string,
        patch: Partial<T> & { [k: string]: unknown },
      ): Promise<T | null> => {
        const existing = this.getStmt().get(collection, id) as { doc: string } | undefined;
        if (!existing) return null;
        const merged = { ...(JSON.parse(existing.doc) as Record<string, unknown>), ...patch, id } as T;
        this.putStmt().run(collection, id, JSON.stringify(merged));
        return merged;
      },
      delete: async (collection: string, id: string): Promise<void> => {
        this.delStmt().run(collection, id);
      },
    };
  }

  private runExclusive<T>(fn: () => Promise<T>): Promise<T> {
    const run = this.serial.then(fn, fn);
    this.serial = run.then(
      () => undefined,
      () => undefined,
    );
    return run;
  }

  /** Wipe all data (tests / destructive). */
  reset(): void {
    this.db.exec('DELETE FROM kv');
  }

  close(): void {
    this.db.close();
  }
}