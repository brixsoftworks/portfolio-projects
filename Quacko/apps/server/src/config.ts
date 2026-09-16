export type AIProviderConfig =
  | { provider: 'demo' }
  | { provider: 'http'; baseUrl: string; apiKey: string; model: string };

export interface ServerConfig {
  host: string;
  port: number;
  /** HMAC secret used to sign auth JWTs. Must be stable across restarts. */
  jwtSecret: string;
  /** Where SQLite db + uploads live. Created on demand. */
  dataDir: string;
  /** Directory holding the exported Expo web app (served at `/`). Null disables. */
  webDir: string | null;
  timezone: string;
  defaultLevelTitle: string;
  ai: AIProviderConfig;
  /** External base URL used to build absolute asset links (uploads). Optional. */
  publicUrl: string;
  /** Upload body size cap. */
  maxUploadBytes: number;
}

function parseEnv(env: Record<string, string | undefined>): ServerConfig {
  const isProd = env.NODE_ENV === 'production';
  const jwtSecret = env.JWT_SECRET ?? '';
  if (isProd && jwtSecret.length < 16) {
    throw new Error('JWT_SECRET is required (>= 16 chars) in production');
  }
  const ai: AIProviderConfig = env.AI_API_KEY
    ? {
        provider: 'http',
        baseUrl: env.AI_BASE_URL ?? 'https://api.openai.com/v1',
        apiKey: env.AI_API_KEY,
        model: env.AI_MODEL ?? 'gpt-4o-mini',
      }
    : { provider: 'demo' };
  return {
    host: env.HOST ?? '0.0.0.0',
    port: Number(env.PORT ?? '8787'),
    jwtSecret: jwtSecret || 'dev-only-jwt-secret-change-in-prod',
    dataDir: env.DATA_DIR ?? '.data',
    webDir: env.WEB_DIR ?? null,
    timezone: env.TIMEZONE ?? 'UTC',
    defaultLevelTitle: env.DEFAULT_LEVEL_TITLE ?? 'Fresh Ducky',
    ai,
    publicUrl: env.PUBLIC_URL ?? '',
    maxUploadBytes: Number(env.MAX_UPLOAD_BYTES ?? String(20 * 1024 * 1024)),
  };
}

/** Singleton resolved once at boot; overridable in tests. */
let cache: ServerConfig | null = null;

export function loadConfig(env: Record<string, string | undefined> = process.env): ServerConfig {
  cache ??= parseEnv(env);
  return cache;
}

/** Recompute config (tests). */
export function resetConfig(): void {
  cache = null;
}

export { parseEnv };