"use client";

import { useWishlist } from "@/lib/WishlistContext";
import { Icon } from "@/components/icons";

export function WishlistButton({
  id,
  className,
}: {
  id: string;
  className?: string;
}) {
  const { has, toggle } = useWishlist();
  const wished = has(id);
  return (
    <button
      onClick={() => toggle(id)}
      aria-label="Toggle wishlist"
      className={
        className ??
        "flex h-8 w-8 items-center justify-center rounded-full bg-white shadow-md transition-colors hover:text-accent"
      }
    >
      <Icon
        name={wished ? "favorite" : "favorite_border"}
        className={`h-4 w-4 ${wished ? "text-accent" : "text-stone-400"}`}
      />
    </button>
  );
}
