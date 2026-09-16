import { describe, expect, it } from 'vitest';

export const cut = <T, K extends keyof T>(obj: T, keys: K[]): Pick<T, K> => {
  const out: Partial<T> = {};
  for (const k of keys) out[k] = obj[k];
  return out as Pick<T, K>;
};

export const expectDeepStable = <T>(value: T) => expect(value);

export { describe, expect, it };