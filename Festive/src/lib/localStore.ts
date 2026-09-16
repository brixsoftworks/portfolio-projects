"use client";

interface LocalStore<T> {
  subscribe: (cb: () => void) => () => void;
  getSnapshot: () => T;
  serverSnapshot: () => T;
  set: (updater: T | ((prev: T) => T)) => void;
}

export function createLocalStore<T>(key: string, initial: T): LocalStore<T> {
  let cache: T = initial;
  const listeners = new Set<() => void>();

  const subscribe = (cb: () => void) => {
    listeners.add(cb);
    window.addEventListener("storage", cb);
    return () => {
      listeners.delete(cb);
      window.removeEventListener("storage", cb);
    };
  };

  const getSnapshot = (): T => {
    try {
      const raw = localStorage.getItem(key);
      cache = raw === null ? initial : (JSON.parse(raw) as T);
    } catch {
      // keep last known cache on corrupt/missing storage
    }
    return cache;
  };

  const serverSnapshot = () => initial;

  const set = (updater: T | ((prev: T) => T)) => {
    const next =
      typeof updater === "function"
        ? (updater as (prev: T) => T)(getSnapshot())
        : updater;
    cache = next;
    try {
      localStorage.setItem(key, JSON.stringify(next));
    } catch {
      // storage unavailable — keep in-memory copy
    }
    listeners.forEach((l) => l());
  };

  return { subscribe, getSnapshot, serverSnapshot, set };
}
