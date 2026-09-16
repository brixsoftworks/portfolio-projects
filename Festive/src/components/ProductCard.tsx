"use client";

import Link from "next/link";
import { useCart } from "@/lib/CartContext";
import { useWishlist } from "@/lib/WishlistContext";
import { discountPercent, formatINR } from "@/lib/format";
import { Icon } from "@/components/icons";
import type { Product } from "@/data/products";

export function ProductCard({ product }: { product: Product }) {
  const { add } = useCart();
  const { has, toggle } = useWishlist();
  const wished = has(product.id);
  const off = discountPercent(product.price, product.mrp);

  return (
    <div
      className="group relative flex flex-col overflow-hidden rounded-2xl"
      style={{
        background: "rgba(255,255,255,0.03)",
        border: "1px solid rgba(255,255,255,0.07)",
        transition: "all 320ms cubic-bezier(0.4, 0, 0.2, 1)",
      }}
      onMouseEnter={(e) => {
        const el = e.currentTarget;
        el.style.transform = "translateY(-6px)";
        el.style.boxShadow = "0 24px 64px rgba(0,0,0,0.6), 0 0 0 1px rgba(201,169,110,0.12)";
        el.style.background = "rgba(255,255,255,0.05)";
      }}
      onMouseLeave={(e) => {
        const el = e.currentTarget;
        el.style.transform = "translateY(0)";
        el.style.boxShadow = "none";
        el.style.background = "rgba(255,255,255,0.03)";
      }}
    >
      {/* Image container */}
      <Link
        href={`/product/${product.id}`}
        className="relative block aspect-[4/5] overflow-hidden"
        style={{ background: "rgba(255,255,255,0.04)" }}
      >
        <img
          src={product.image}
          alt={product.name}
          loading="lazy"
          className="h-full w-full object-cover transition-transform duration-700 group-hover:scale-110"
        />
        {/* Gradient reveal overlay */}
        <div
          className="absolute inset-0 transition-opacity duration-300 group-hover:opacity-100"
          style={{
            background: "linear-gradient(180deg, transparent 50%, rgba(8,7,10,0.8) 100%)",
            opacity: 0.3,
          }}
        />
        {/* Quick-add CTA — revealed on hover */}
        <div
          className="absolute inset-x-4 bottom-4 translate-y-2 opacity-0 transition-all duration-300 group-hover:translate-y-0 group-hover:opacity-100"
        >
          <button
            onClick={(e) => { e.preventDefault(); e.stopPropagation(); add(product); }}
            className="w-full rounded-full py-2.5 text-center text-[12px] font-semibold uppercase tracking-wider transition-opacity hover:opacity-90"
            style={{
              background: "linear-gradient(135deg, #c9a96e, #e8c882)",
              color: "#0a0809",
              letterSpacing: "0.1em",
            }}
          >
            Add to Cart
          </button>
        </div>
      </Link>

      {/* Wishlist button */}
      <div className="absolute right-3 top-3 z-10">
        <button
          onClick={() => toggle(product.id)}
          aria-label={wished ? "Remove from wishlist" : "Add to wishlist"}
          className="flex h-8 w-8 items-center justify-center rounded-full transition-all duration-200"
          style={{
            background: wished
              ? "rgba(201,169,110,0.2)"
              : "rgba(8,7,10,0.7)",
            border: wished
              ? "1px solid rgba(201,169,110,0.4)"
              : "1px solid rgba(255,255,255,0.12)",
            color: wished ? "#c9a96e" : "rgba(245,240,232,0.6)",
            backdropFilter: "blur(8px)",
          }}
        >
          <Icon name={wished ? "favorite" : "favorite_border"} className="h-3.5 w-3.5" />
        </button>
      </div>

      {/* Top badges */}
      {(off > 0 || product.bestseller) && (
        <div className="absolute left-3 top-3 z-10 flex flex-col gap-1">
          {off > 0 && (
            <span
              className="rounded-full px-2.5 py-1 text-[9px] font-bold uppercase tracking-wider"
              style={{ background: "rgba(201,169,110,0.15)", border: "1px solid rgba(201,169,110,0.3)", color: "#c9a96e" }}
            >
              {off}% off
            </span>
          )}
          {product.bestseller && (
            <span
              className="rounded-full px-2.5 py-1 text-[9px] font-bold uppercase tracking-wider"
              style={{ background: "rgba(245,158,11,0.15)", border: "1px solid rgba(245,158,11,0.3)", color: "#f59e0b" }}
            >
              ✦ Bestseller
            </span>
          )}
        </div>
      )}

      {/* Card body */}
      <div className="flex flex-1 flex-col p-4 pt-3">
        {/* Region */}
        <p
          className="mb-1 text-[9px] font-bold uppercase tracking-[0.2em]"
          style={{ color: "rgba(201,169,110,0.6)" }}
        >
          {product.region}
        </p>

        {/* Name */}
        <Link href={`/product/${product.id}`}>
          <h3
            className="mb-2 line-clamp-2 text-sm font-medium leading-snug transition-colors duration-200 group-hover:text-[#e8c882]"
            style={{ color: "rgba(245,240,232,0.85)", fontFamily: "var(--font-montserrat)" }}
          >
            {product.name}
          </h3>
        </Link>

        {/* Stars */}
        <div className="mb-2 flex items-center gap-1.5">
          <span className="flex">
            {Array.from({ length: 5 }).map((_, i) => (
              <Icon
                key={i}
                name="star"
                className="h-3 w-3"
                style={{ color: i < Math.round(product.rating) ? "#f59e0b" : "rgba(255,255,255,0.12)" }}
              />
            ))}
          </span>
          <span className="text-[10px]" style={{ color: "rgba(245,240,232,0.35)" }}>
            ({product.reviews})
          </span>
        </div>

        {/* Pricing */}
        <div className="mt-auto flex items-end gap-2">
          <span
            className="text-base font-semibold tabular-nums"
            style={{ color: "#e8c882", fontFamily: "var(--font-montserrat)" }}
          >
            {formatINR(product.price)}
          </span>
          {product.mrp > product.price && (
            <span
              className="mb-0.5 text-xs line-through tabular-nums"
              style={{ color: "rgba(245,240,232,0.3)" }}
            >
              {formatINR(product.mrp)}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
