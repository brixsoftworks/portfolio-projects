"use client";

import Link from "next/link";
import { useCart } from "@/lib/CartContext";
import { formatINR } from "@/lib/format";
import { Icon } from "@/components/icons";

export function CartDrawer() {
  const { items, isOpen, setOpen, updateQty, remove, subtotal } = useCart();

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      {/* Backdrop */}
      <div
        className="absolute inset-0 cursor-pointer"
        style={{ background: "rgba(0,0,0,0.65)", backdropFilter: "blur(4px)" }}
        onClick={() => setOpen(false)}
        aria-label="Close cart"
      />

      {/* Drawer panel */}
      <div
        className="relative flex h-full w-full max-w-[420px] flex-col"
        style={{
          background: "rgba(10,8,14,0.97)",
          borderLeft: "1px solid rgba(255,255,255,0.08)",
          backdropFilter: "blur(24px)",
        }}
      >
        {/* Header */}
        <div
          className="flex items-center justify-between px-6 py-5"
          style={{ borderBottom: "1px solid rgba(255,255,255,0.07)" }}
        >
          <div>
            <h2
              className="text-2xl font-medium"
              style={{
                fontFamily: "var(--font-cormorant), Georgia, serif",
                color: "rgba(245,240,232,0.95)",
              }}
            >
              Your Cart
            </h2>
            <p className="text-[11px] mt-0.5" style={{ color: "rgba(201,169,110,0.6)" }}>
              {items.length} {items.length === 1 ? "item" : "items"}
            </p>
          </div>
          <button
            onClick={() => setOpen(false)}
            className="flex h-9 w-9 items-center justify-center rounded-full transition-all duration-200"
            style={{
              background: "rgba(255,255,255,0.05)",
              border: "1px solid rgba(255,255,255,0.1)",
              color: "rgba(245,240,232,0.6)",
            }}
            aria-label="Close cart"
          >
            <Icon name="close" className="h-4 w-4" />
          </button>
        </div>

        {/* Items */}
        <div className="flex-1 overflow-y-auto px-6 py-5">
          {items.length === 0 ? (
            <div className="flex h-full flex-col items-center justify-center gap-5 text-center">
              <div
                className="flex h-20 w-20 items-center justify-center rounded-full text-4xl"
                style={{
                  background: "rgba(201,169,110,0.08)",
                  border: "1px solid rgba(201,169,110,0.15)",
                }}
              >
                🛍️
              </div>
              <div>
                <p
                  className="mb-1 text-lg"
                  style={{ fontFamily: "var(--font-cormorant), Georgia, serif", color: "rgba(245,240,232,0.8)" }}
                >
                  Your cart is empty
                </p>
                <p className="text-sm" style={{ color: "rgba(245,240,232,0.35)" }}>
                  Discover festive treasures from across India
                </p>
              </div>
              <Link
                href="/products"
                onClick={() => setOpen(false)}
                className="rounded-full px-6 py-3 text-sm font-semibold uppercase tracking-wider transition-all duration-200 hover:opacity-90"
                style={{
                  background: "linear-gradient(135deg, #c9a96e, #e8c882)",
                  color: "#0a0809",
                  letterSpacing: "0.08em",
                }}
              >
                Start Shopping
              </Link>
            </div>
          ) : (
            <ul className="space-y-4">
              {items.map((item) => (
                <li
                  key={item.id}
                  className="flex gap-4 rounded-xl p-3"
                  style={{
                    background: "rgba(255,255,255,0.03)",
                    border: "1px solid rgba(255,255,255,0.07)",
                  }}
                >
                  {/* Product image */}
                  <div
                    className="h-18 w-18 shrink-0 overflow-hidden rounded-lg"
                    style={{ width: "72px", height: "72px", background: "rgba(255,255,255,0.05)" }}
                  >
                    <img
                      src={item.image}
                      alt={item.name}
                      className="h-full w-full object-cover"
                    />
                  </div>

                  {/* Info */}
                  <div className="flex-1 min-w-0">
                    <Link
                      href={`/product/${item.id}`}
                      onClick={() => setOpen(false)}
                      className="line-clamp-2 text-sm font-medium leading-snug transition-colors duration-200 hover:text-[#c9a96e]"
                      style={{ color: "rgba(245,240,232,0.8)", fontFamily: "var(--font-montserrat)" }}
                    >
                      {item.name}
                    </Link>
                    <p className="mt-1 text-[11px]" style={{ color: "rgba(245,240,232,0.35)" }}>
                      {formatINR(item.price)} each
                    </p>

                    {/* Qty controls */}
                    <div className="mt-2.5 flex items-center gap-3">
                      <div
                        className="flex items-center overflow-hidden rounded-full"
                        style={{
                          background: "rgba(255,255,255,0.05)",
                          border: "1px solid rgba(255,255,255,0.1)",
                        }}
                      >
                        <button
                          onClick={() => updateQty(item.id, item.qty - 1)}
                          className="flex h-7 w-7 items-center justify-center text-sm transition-colors hover:text-[#c9a96e]"
                          style={{ color: "rgba(245,240,232,0.5)" }}
                          aria-label="Decrease quantity"
                        >
                          −
                        </button>
                        <span
                          className="w-7 text-center text-sm font-semibold"
                          style={{ color: "rgba(245,240,232,0.9)" }}
                        >
                          {item.qty}
                        </span>
                        <button
                          onClick={() => updateQty(item.id, item.qty + 1)}
                          className="flex h-7 w-7 items-center justify-center text-sm transition-colors hover:text-[#c9a96e]"
                          style={{ color: "rgba(245,240,232,0.5)" }}
                          aria-label="Increase quantity"
                        >
                          +
                        </button>
                      </div>
                      <button
                        onClick={() => remove(item.id)}
                        className="ml-auto text-[11px] font-medium transition-colors duration-200 hover:text-[#e8c882]"
                        style={{ color: "rgba(245,240,232,0.3)" }}
                      >
                        Remove
                      </button>
                    </div>
                  </div>

                  {/* Line total */}
                  <div className="shrink-0 text-right">
                    <span
                      className="text-sm font-semibold tabular-nums"
                      style={{ color: "#c9a96e" }}
                    >
                      {formatINR(item.price * item.qty)}
                    </span>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Footer */}
        {items.length > 0 && (
          <div
            className="px-6 py-5"
            style={{ borderTop: "1px solid rgba(255,255,255,0.07)" }}
          >
            {/* Subtotal */}
            <div className="mb-4 flex items-center justify-between">
              <span className="text-sm" style={{ color: "rgba(245,240,232,0.5)" }}>
                Subtotal
              </span>
              <span
                className="text-xl font-semibold tabular-nums"
                style={{
                  fontFamily: "var(--font-cormorant), Georgia, serif",
                  background: "linear-gradient(135deg, #c9a96e, #e8c882)",
                  WebkitBackgroundClip: "text",
                  WebkitTextFillColor: "transparent",
                  backgroundClip: "text",
                }}
              >
                {formatINR(subtotal)}
              </span>
            </div>

            {/* Checkout CTA */}
            <Link
              href="/checkout"
              onClick={() => setOpen(false)}
              className="flex w-full items-center justify-center gap-2 rounded-full py-4 text-center text-[13px] font-semibold uppercase tracking-widest transition-all duration-200 hover:opacity-90 hover:-translate-y-0.5 active:scale-[0.98]"
              style={{
                background: "linear-gradient(135deg, #c9a96e 0%, #e8c882 50%, #c9a96e 100%)",
                color: "#0a0809",
                boxShadow: "0 8px 32px rgba(201,169,110,0.3)",
              }}
            >
              Proceed to Checkout
              <Icon name="arrow_forward" className="h-4 w-4" />
            </Link>

            <p className="mt-3 text-center text-[10px]" style={{ color: "rgba(245,240,232,0.2)" }}>
              Free delivery on orders above ₹999
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
