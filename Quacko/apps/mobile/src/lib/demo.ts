import { DemoProvider } from '@quacko/ai';
import { createBackend } from '@quacko/backend';
import { InMemoryStore } from '@quacko/backend/src/inMemory';

/**
 * Demo-mode backend. Runs the same server-authoritative backend services
 * over an in-memory store with the deterministic demo AI provider, so the
 * whole golden path (goals → plans → missions → proof → XP/streak) works
 * without Firebase. State resets on app restart.
 */
export function createDemoBackend() {
  const store = new InMemoryStore();
  return createBackend(new DemoProvider(), {
    store,
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone ?? 'UTC',
  });
}

export type DemoBackend = ReturnType<typeof createDemoBackend>;