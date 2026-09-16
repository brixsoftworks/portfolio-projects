import fs from 'node:fs';
import path from 'node:path';
import { DemoProvider, createHttpProvider } from '@quacko/ai';
import { createBackend } from '@quacko/backend';
import type { AIProvider } from '@quacko/ai';
import { loadConfig } from './config';
import { SqliteStore } from './sqliteStore';
import { createApp } from './app';

function buildAI(): AIProvider {
  const { ai } = loadConfig();
  if (ai.provider === 'http') {
    return createHttpProvider({
      baseUrl: ai.baseUrl,
      apiKey: ai.apiKey,
      model: ai.model,
    });
  }
  return new DemoProvider();
}

async function main(): Promise<void> {
  const config = loadConfig();
  fs.mkdirSync(config.dataDir, { recursive: true });

  const store = new SqliteStore(path.join(config.dataDir, 'quacko.db'));
  const backend = createBackend(buildAI(), {
    store,
    timezone: config.timezone,
    defaultLevelTitle: config.defaultLevelTitle,
  });

  const app = createApp(config, { backend, store });
  const server = app.listen(config.port, config.host, () => {
    console.log(`QUACKO server listening on http://${config.host}:${config.port}`);
    console.log(`  store:   sqlite → ${config.dataDir}/quacko.db`);
    console.log(`  ai:      ${config.ai.provider === 'demo' ? 'demo (deterministic)' : `http (${config.ai.model})`}`);
    console.log(`  web:     ${config.webDir && fs.existsSync(path.join(config.webDir, 'index.html')) ? `serving ${config.webDir}` : 'disabled'}`);
    console.log(`  health:  http://127.0.0.1:${config.port}/api/v1/health`);
  });

  const shutdown = (signal: string) => {
    console.log(`\n${signal} received, shutting down…`);
    server.close(() => {
      store.close();
      process.exit(0);
    });
  };
  process.on('SIGINT', () => shutdown('SIGINT'));
  process.on('SIGTERM', () => shutdown('SIGTERM'));
}

main().catch((err) => {
  console.error('[quacko] failed to start:', err);
  process.exit(1);
});