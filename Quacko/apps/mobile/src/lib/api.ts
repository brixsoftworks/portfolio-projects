import { createHttpBackend, type RpcApi } from '@quacko/client';
import { createDemoBackend } from './demo';
import { isDemo, env } from '../env';
import { useAuth } from '@/state/auth';

/**
 * Unified client API.
 *
 * - Demo mode: every call hits the in-process backend over the InMemoryStore
 *   (the exact same services the self-hosted server wraps). No login, no
 *   network, deterministic AI.
 * - Real mode: routes to the self-hosted server via JSON-RPC
 *   (`POST /api/v1/rpc`); `uid` is injected server-side from the JWT.
 */
export interface QuackoApi extends RpcApi {}

let demo: QuackoApi | null = null;
function demoApi(): QuackoApi {
  demo ??= createDemoBackend();
  return demo;
}

let http: QuackoApi | null = null;
function httpApi(): QuackoApi {
  if (!env.apiUrl) {
    throw new Error('EXPO_PUBLIC_API_URL is not set. Point it at the self-hosted server.');
  }
  http ??= createHttpBackend({ baseUrl: env.apiUrl, getToken: () => useAuth.getState().token });
  return http;
}

/** The backend used by screens. Demo unless a server is configured. */
export function getApi(): QuackoApi {
  return isDemo ? demoApi() : httpApi();
}