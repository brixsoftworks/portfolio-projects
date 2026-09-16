"use client";

import { useState } from "react";
import { useCart } from "@/lib/CartContext";
import { Icon } from "@/components/icons";
import type { Product } from "@/data/products";

export function BuyBox({ product }: { product: Product }) {
  const { add } = useCart();
  const [qty, setQty] = useState(1);

  return (
    <div className="flex items-center gap-4">
      {/* Quantity stepper */}
      <div
        className="flex h-14 w-36 shrink-0 items-center overflow-hidden rounded-full"
        style={{
          background: "rgba(255,255,255,0.04)",
          border: "1px solid rgba(255,255,255,0.12)",
        }}
      >
        <button
          onClick={() => setQty((q) => Math.max(1, q - 1))}
          className="flex h-full w-12 items-center justify-center transition-colors duration-200"
          style={{ color: "rgba(245,240,232,0.5)" }}
          onMouseEnter={(e) => { e.currentTarget.style.color = "#c9a96e"; }}
          onMouseLeave={(e) => { e.currentTarget.style.color = "rgba(245,240,232,0.5)"; }}
          aria-label="Decrease quantity"
        >
          <Icon name="remove" className="h-4 w-4" />
        </button>
        <input
          readOnly
          value={qty}
          aria-label="Quantity"
          className="w-full border-0 bg-transparent p-0 text-center text-base font-semibold tabular-nums"
          style={{ color: "rgba(245,240,232,0.9)", fontFamily: "var(--font-montserrat)" }}
        />
        <button
          onClick={() => setQty((q) => q + 1)}
          className="flex h-full w-12 items-center justify-center transition-colors duration-200"
          style={{ color: "rgba(245,240,232,0.5)" }}
          onMouseEnter={(e) => { e.currentTarget.style.color = "#c9a96e"; }}
          onMouseLeave={(e) => { e.currentTarget.style.color = "rgba(245,240,232,0.5)"; }}
          aria-label="Increase quantity"
        >
          <Icon name="add" className="h-4 w-4" />
        </button>
      </div>

      {/* Add to cart button */}
      <button
        onClick={() => add(product, qty)}
        className="flex h-14 flex-1 items-center justify-center gap-2.5 rounded-full text-sm font-semibold uppercase tracking-widest transition-all duration-200 hover:-translate-y-0.5 hover:opacity-90 active:scale-[0.98]"
        style={{
          background: "linear-gradient(135deg, #c9a96e 0%, #e8c882 50%, #c9a96e 100%)",
          backgroundSize: "200% 200%",
          color: "#0a0809",
          boxShadow: "0 8px 32px rgba(201,169,110,0.3), 0 1px 0 rgba(255,255,255,0.2) inset",
          letterSpacing: "0.08em",
        }}
      >
        <Icon name="shopping_bag" className="h-5 w-5" />
        Add to Cart
      </button>
    </div>
  );
}
