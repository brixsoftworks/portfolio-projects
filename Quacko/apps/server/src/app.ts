import fs from 'node:fs';
import path from 'node:path';
import express from 'express';
import type { Express, Request, Response } from 'express';
import { z } from 'zod';
import type { Store } from '@quacko/backend';
import type { Backend } from '@quacko/backend';
import type { UserProfile } from '@quacko/types';
import { rpcMethodNames, type RpcMethodName } from '@quacko/client';
import type { ServerConfig } from './config';
import { authRequired, hashPassword, signToken, verifyPassword } from './auth';
import { HttpError, errorMiddleware } from './errors';
import { buildRpcHandlers, type RpcHandlers } from './rpc';

export interface ServerServices {
  backend: Backend;
  store: Store;
}

export interface AuthUser {
  id: string;
  email: string;
  passHash: string;
  displayName: string;
  createdAt: string;
  updatedAt: string;
}

const emailSchema = z.string().trim().toLowerCase().email().max(160);
const passwordSchema = z.string().min(8).max(128);
const registerSchema = z.object({
  email: emailSchema,
  password: passwordSchema,
  displayName: z.string().trim().min(1).max(64).optional(),
  timezone: z.string().min(1).max(64).optional(),
});
const loginSchema = z.object({ email: emailSchema, password: z.string().min(1).max(128) });
const rpcBodySchema = z.object({
  method: z.string(),
  args: z.array(z.unknown()).default([]),
});

export function createApp(config: ServerConfig, services: ServerServices): Express {
  const { backend, store } = services;
  const app = express();
  app.disable('x-powered-by');
  app.use(express.json({ limit: '2mb' }));

  const uploadsDir = path.join(config.dataDir, 'uploads');
  fs.mkdirSync(uploadsDir, { recursive: true });

  /* ------------------------------ health ------------------------------ */
  app.get('/api/v1/health', (_req: Request, res: Response) => {
    res.json({ ok: true, service: 'quacko', version: '0.1.0', time: new Date().toISOString() });
  });

  /* ------------------------------- auth ------------------------------- */
  app.post('/api/v1/auth/register', async (req, res, next) => {
    const parsed = registerSchema.safeParse(req.body);
    if (!parsed.success) return next(new HttpError(400, parsed.error.message));
    const { email, password, displayName, timezone } = parsed.data;
    const existing = await store.find<AuthUser>('authUsers', { where: [{ field: 'email', equals: email }] });
    if (existing.length > 0) return next(new HttpError(409, `email already registered`));
    const uid = store.newId();
    const passHash = await hashPassword(password);
    const nowIso = new Date().toISOString();
    await store.transaction(async (tx) => {
      await tx.create<AuthUser>('authUsers', {
        id: uid,
        email,
        passHash,
        displayName: displayName ?? email.split('@')[0] ?? 'Quacko Member',
        createdAt: nowIso,
        updatedAt: nowIso,
      });
    });
    const profile = await backend.getOrCreateProfile(uid, {
      displayName: displayName ?? email.split('@')[0] ?? 'Quacko Member',
      email,
      timezone: timezone ?? config.timezone,
    });
    const token = signToken(config.jwtSecret, uid, email);
    res.status(201).json({ token, profile });
  });

  app.post('/api/v1/auth/login', async (req, res, next) => {
    const parsed = loginSchema.safeParse(req.body);
    if (!parsed.success) return next(new HttpError(400, parsed.error.message));
    const { email, password } = parsed.data;
    const users = await store.find<AuthUser>('authUsers', { where: [{ field: 'email', equals: email }] });
    const user = users[0];
    const ok = user ? await verifyPassword(password, user.passHash) : false;
    if (!user || !ok) return next(new HttpError(401, 'invalid email or password'));
    const profile = await backend.getOrCreateProfile(user.id);
    const token = signToken(config.jwtSecret, user.id, user.email);
    res.json({ token, profile });
  });

  app.get('/api/v1/auth/me', authRequired(config.jwtSecret), async (_req, res, next) => {
    try {
      const uid = res.locals.uid as string;
      const profile = await backend.getOrCreateProfile(uid);
      res.json(profile satisfies UserProfile);
    } catch (err) {
      next(err);
    }
  });

  /* -------------------------------- rpc ------------------------------- */
  const handlers: RpcHandlers = buildRpcHandlers(backend);
  app.post('/api/v1/rpc', authRequired(config.jwtSecret), async (req, res, next) => {
    const parsed = rpcBodySchema.safeParse(req.body);
    if (!parsed.success) return next(new HttpError(400, parsed.error.message));
    const { method, args } = parsed.data;
    if (!rpcMethodNames.includes(method as RpcMethodName)) {
      return next(new HttpError(404, `unknown method: ${method}`));
    }
    try {
      const handler = handlers[method as RpcMethodName];
      const data = await handler(backend, res.locals.uid as string, args);
      res.json({ data: data ?? null });
    } catch (err) {
      next(err);
    }
  });

  /* ------------------------------ uploads ----------------------------- */
  app.post(
    '/api/v1/uploads',
    authRequired(config.jwtSecret),
    express.raw({ type: () => true, limit: config.maxUploadBytes }),
    (req, res, next) => {
      const requested = String(req.query.ext ?? 'bin').slice(0, 8);
      const ext = /^[a-z0-9]{1,6}$/.test(requested) ? requested : 'bin';
      const name = `${store.newId()}.${ext}`;
      const buf = req.body as Buffer | undefined;
      if (!Buffer.isBuffer(buf) || buf.length === 0) {
        return next(new HttpError(400, 'empty upload body'));
      }
      fs.writeFile(path.join(uploadsDir, name), buf, (err) => {
        if (err) return next(err);
        const rel = `/uploads/${name}`;
        res.status(201).json({ url: config.publicUrl ? `${config.publicUrl}${rel}` : rel });
      });
    },
  );
  app.use('/uploads', express.static(uploadsDir, { maxAge: '7d' }));

  /* --------------------------- api 404 + errors ------------------------ */
  app.use('/api', (_req, res) => {
    res.status(404).json({ error: { code: 'not-found', message: 'route not found' } });
  });
  app.use(errorMiddleware);

  /* --------------------------- web (SPA) static ------------------------ */
  if (config.webDir && fs.existsSync(path.join(config.webDir, 'index.html'))) {
    app.use(express.static(config.webDir, { index: 'index.html', maxAge: process.env.NODE_ENV === 'production' ? '1h' : 0 }));
    const indexHtml = path.join(config.webDir, 'index.html');
    app.use((req, res, next) => {
      if (req.method !== 'GET') return next();
      const accepts = req.headers.accept ?? '';
      if (!accepts.includes('text/html') && req.path !== '/') return next();
      res.sendFile(indexHtml, () => {});
    });
  }

  return app;
}