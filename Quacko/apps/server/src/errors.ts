import type { NextFunction, Request, Response } from 'express';

/** Our public HTTP error. */
export class HttpError extends Error {
  constructor(
    readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = 'HttpError';
  }
}

const KIND_STATUS: Record<string, number> = {
  'not-found': 404,
  conflict: 409,
  validation: 400,
  unauthorized: 401,
};

/** Maps backend error kinds + unexpected errors to JSON responses. */
export function errorMiddleware(err: unknown, _req: Request, res: Response, _next: NextFunction): void {
  if (err instanceof HttpError) {
    res.status(err.status).json({ error: { code: 'http', message: err.message } });
    return;
  }
  const kind = (err as { kind?: unknown } | null)?.kind;
  const status = typeof kind === 'string' ? KIND_STATUS[kind] : undefined;
  if (status) {
    res.status(status).json({ error: { code: kind, message: err instanceof Error ? err.message : String(err) } });
    return;
  }
  console.error('[server] unhandled error:', err);
  res.status(500).json({ error: { code: 'internal', message: 'internal server error' } });
}