"use client";

import { createContext, useCallback, useContext, useMemo, useSyncExternalStore } from "react";
import { createLocalStore } from "@/lib/localStore";

interface WishlistContextValue {
  ids: string[];
  count: number;
  toggle: (id: string) => void;
  has: (id: string) => boolean;
  clear: () => void;
}

const WishlistContext = createContext<WishlistContextValue | null>(null);
const wishlistStore = createLocalStore<string[]>("festive_wishlist", []);

export function WishlistProvider({ children }: { children: React.ReactNode }) {
  const ids = useSyncExternalStore(
    wishlistStore.subscribe,
    wishlistStore.getSnapshot,
    wishlistStore.serverSnapshot
  );

  const toggle = useCallback((id: string) => {
    wishlistStore.set((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  }, []);

  const has = useCallback((id: string) => ids.includes(id), [ids]);
  const clear = useCallback(() => wishlistStore.set([]), []);

  const value = useMemo(
    () => ({ ids, count: ids.length, toggle, has, clear }),
    [ids, toggle, has, clear]
  );

  return <WishlistContext.Provider value={value}>{children}</WishlistContext.Provider>;
}

export function useWishlist() {
  const ctx = useContext(WishlistContext);
  if (!ctx) throw new Error("useWishlist must be used within WishlistProvider");
  return ctx;
}
