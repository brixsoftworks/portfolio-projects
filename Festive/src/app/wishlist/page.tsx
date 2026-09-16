"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getProductsByIds } from "@/data/catalog";
import { useWishlist } from "@/lib/WishlistContext";
import { ProductCard } from "@/components/ProductCard";
import { Icon } from "@/components/icons";
import type { Product } from "@/data/products";

export default function WishlistPage() {
  const { ids, clear } = useWishlist();
  const [items, setItems] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    getProductsByIds(ids)
      .then((products) => {
        if (!cancelled) setItems(products);
      })
      .catch(() => {
        if (!cancelled) setItems([]);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [ids]);

  if (loading) {
    return (
      <div className="mx-auto max-w-7xl px-4 py-24 text-center">
        <p className="text-ink-muted">Loading your wishlist…</p>
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="mx-auto flex max-w-7xl flex-col items-center px-4 py-24 text-center">
        <div className="mb-6 flex h-24 w-24 items-center justify-center rounded-full bg-violet-50">
          <Icon name="favorite_border" className="h-12 w-12 text-violet-500/50" />
        </div>
        <h1 className="mb-3 text-2xl font-bold tracking-tight text-ink md:text-3xl">
          Your wishlist is empty
        </h1>
        <p className="mb-8 max-w-md text-base text-ink-muted">
          Save items you love to your wishlist. Review them anytime and easily move
          them to your cart when you&apos;re ready to celebrate.
        </p>
        <Link
          href="/products"
          className="btn-primary"
        >
          Explore Products
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto w-full max-w-7xl px-4 py-8 md:px-6 md:py-12">
      <div className="mb-8 flex flex-col justify-between gap-4 border-b border-black/5 pb-4 sm:flex-row sm:items-baseline">
        <h1 className="text-3xl font-bold tracking-tight text-ink md:text-4xl">
          Your Wishlist
        </h1>
        <button
          onClick={clear}
          className="group flex items-center gap-1 text-sm font-medium text-fuchsia-600 transition-colors hover:text-fuchsia-700"
        >
          <Icon
            name="delete_outline"
            className="h-4 w-4 transition-transform group-hover:-translate-y-0.5"
          />
          Clear wishlist
        </button>
      </div>
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 lg:gap-6">
        {items.map((p) => (
          <ProductCard key={p.id} product={p} />
        ))}
      </div>
    </div>
  );
}
