/**
 * Environment access. All values come from EXPO_PUBLIC_* so they are inlined
 * at build time and safe to read on the client. `.env.example` documents each.
 */
export const env = {
  demoMode: (process.env.EXPO_PUBLIC_DEMO_MODE ?? '1') !== '0',
  /** Self-hosted backend origin (no trailing slash). Empty = same-origin (web). */
  apiUrl: process.env.EXPO_PUBLIC_API_URL ?? '',
  aiBaseUrl: process.env.EXPO_PUBLIC_AI_BASE_URL ?? 'https://api.openai.com/v1',
} as const;

export const isDemo = env.demoMode;