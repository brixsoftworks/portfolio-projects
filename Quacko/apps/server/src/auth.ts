import { createHmac, randomBytes, scrypt, timingSafeEqual } from 'node:crypto';
import type { NextFunction, Request, Response } from 'express';
import { UnauthorizedError } from '@quacko/backend';

/* ------------------------------- passwords ------------------------------ */

const KEY_LEN = 64;

export async function hashPassword(password: string): Promise<string> {
  const salt = randomBytes(16);
  const key = await new Promise<Buffer>((resolve, reject) => {
    scrypt(password, salt, KEY_LEN, (err, derived) => (err ? reject(err) : resolve(derived)));
  });
  return `${salt.toString('hex')}:${key.toString('hex')}`;
}

export async function verifyPassword(password: string, stored: string): Promise<boolean> {
  const [saltHex, keyHex] = stored.split(':');
  if (!saltHex || !keyHex) return false;
  const salt = Buffer.from(saltHex, 'hex');
  const expected = Buffer.from(keyHex, 'hex');
  try {
    const derived = await new Promise<Buffer>((resolve, reject) => {
      scrypt(password, salt, expected.length, (err, key) => (err ? reject(err) : resolve(key)));
    });
    return derived.length === expected.length && timingSafeEqual(derived, expected);
  } catch {
    return false;
  }
}

/* --------------------------------- JWT ---------------------------------- */

export interface JwtPayload {
  sub: string;
  email: string;
  iat: number;
  exp: number;
}

const b64url = (input: string | Buffer): string => Buffer.from(input).toString('base64url');

const TOKEN_TTL_SECONDS = 60 * 60 * 24 * 30; // 30 days

export function signToken(secret: string, sub: string, email: string, ttlSeconds = TOKEN_TTL_SECONDS): string {
  const header = b64url(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
  const now = Math.floor(Date.now() / 1000);
  const payload = b64url(JSON.stringify({ sub, email, iat: now, exp: now + ttlSeconds } satisfies JwtPayload));
  const signature = createHmac('sha256', secret).update(`${header}.${payload}`).digest('base64url');
  return `${header}.${payload}.${signature}`;
}

export function verifyToken(secret: string, token: string): JwtPayload {
  if (typeof token !== 'string' || token.split('.').length !== 3) {
    throw new UnauthorizedError('malformed token');
  }
  const [header, payload, signature] = token.split('.') as [string, string, string];
  const expected = createHmac('sha256', secret).update(`${header}.${payload}`).digest('base64url');
  if (!timingSafeEqual(Buffer.from(signature), Buffer.from(expected))) {
    throw new UnauthorizedError('invalid token signature');
  }
  let decoded: JwtPayload;
  try {
    decoded = JSON.parse(Buffer.from(payload, 'base64url').toString('utf8')) as JwtPayload;
  } catch {
    throw new UnauthorizedError('malformed token payload');
  }
  if (typeof decoded.exp !== 'number' || decoded.exp <= Math.floor(Date.now() / 1000)) {
    throw new UnauthorizedError('token expired');
  }
  return decoded;
}

/* ------------------------------ middleware ------------------------------ */

export interface AuthedLocals {
  uid: string;
  email?: string;
}

export function authRequired(secret: string) {
  return (req: Request, res: Response, next: NextFunction): void => {
    const header = req.headers.authorization;
    const token = header?.startsWith('Bearer ') ? header.slice('Bearer '.length) : null;
    if (!token) {
      next(new UnauthorizedError('missing bearer token'));
      return;
    }
    try {
      const payload = verifyToken(secret, token);
      res.locals.uid = payload.sub;
      res.locals.email = payload.email ?? '';
      next();
    } catch (err) {
      next(err);
    }
  };
}