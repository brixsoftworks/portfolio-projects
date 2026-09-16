"use client";

import Link from "next/link";
import { useCart } from "@/lib/CartContext";
import { formatINR } from "@/lib/format";
import { Icon } from "@/components/icons";

export default function CartPage() {
  const { items, updateQty, remove, subtotal, clear } = useCart();

  if (items.length === 0) {
    return (
      <div className="mx-auto flex max-w-7xl flex-col items-center px-4 py-24 text-center">
        <div className="mb-6 flex h-24 w-24 items-center justify-center rounded-full bg-violet-100">
          <Icon name="shopping_cart" className="h-12 w-12 text-violet-500/50" />
        </div>
        <h1 className="mb-3 text-2xl font-bold tracking-tight text-ink md:text-3xl">
          Your cart is empty
        </h1>
        <p className="mb-8 text-base text-ink-muted">
          Fill it with festive favourites from across India before they sell out.
        </p>
        <Link
          href="/products"
          className="btn-primary"
        >
          Start Shopping
        </Link>
      </div>
    );
  }

  const shipping = subtotal >= 999 ? 0 : 49;
  const total = subtotal + shipping;
  const count = items.reduce((acc, i) => acc + i.qty, 0);

  return (
    <div className="mx-auto w-full max-w-7xl px-4 py-8 md:px-6 md:py-12">
      <div className="mb-8 flex items-end justify-between">
        <h1 className="text-4xl font-bold tracking-tight text-ink md:text-5xl">
          Shopping Cart
        </h1>
        <button
          onClick={clear}
          className="text-sm font-medium text-ink-muted underline underline-offset-4 transition-colors hover:text-violet-700"
        >
          Clear cart
        </button>
      </div>

      <div className="flex flex-col items-start gap-8 lg:flex-row lg:gap-12">
        <div className="w-full flex-grow space-y-4">
          {items.map((item) => (
            <div
              key={item.id}
              className="flex flex-col items-start gap-6 rounded-2xl card p-4 sm:flex-row sm:items-center md:p-6"
            >
              <Link
                href={`/product/${item.id}`}
                className="relative h-24 w-24 shrink-0 overflow-hidden rounded-xl border border-stone-100 bg-stone-100 sm:h-32 sm:w-32"
              >
                <img
                  src={item.image}
                  alt={item.name}
                  className="h-full w-full object-cover"
                />
              </Link>
              <div className="flex w-full flex-col">
                <div className="mb-2 flex items-start justify-between">
                  <div>
                    <span className="mb-1 block text-[11px] font-medium uppercase tracking-widest text-ink-muted">
                      {item.region}
                    </span>
                    <h3 className="text-lg font-bold leading-tight text-ink">
                      {item.name}
                    </h3>
                  </div>
                  <span className="hidden text-lg font-bold text-ink sm:block">
                    {formatINR(item.price * item.qty)}
                  </span>
                </div>
                <div className="mb-4 text-sm text-ink-muted">
                  {item.tags?.join(", ")}
                </div>
                <div className="mt-auto flex items-center justify-between">
                  <div className="flex h-9 items-center overflow-hidden rounded-lg border border-stone-300">
                    <button
                      onClick={() => updateQty(item.id, item.qty - 1)}
                      aria-label="Decrease quantity"
                      className="flex h-full items-center justify-center px-3 text-stone-500 transition-colors hover:bg-stone-50 hover:text-ink"
                    >
                      <Icon name="remove" className="h-4 w-4" />
                    </button>
                    <span className="w-8 text-center text-sm font-medium text-ink">
                      {item.qty}
                    </span>
                    <button
                      onClick={() => updateQty(item.id, item.qty + 1)}
                      aria-label="Increase quantity"
                      className="flex h-full items-center justify-center px-3 text-stone-500 transition-colors hover:bg-stone-50 hover:text-ink"
                    >
                      <Icon name="add" className="h-4 w-4" />
                    </button>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="text-lg font-bold text-ink sm:hidden">
                      {formatINR(item.price * item.qty)}
                    </span>
                    <button
                      onClick={() => remove(item.id)}
                      className="text-sm text-ink-muted underline underline-offset-4 transition-colors hover:text-accent"
                    >
                      Remove
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        <aside className="w-full shrink-0 lg:sticky lg:top-24 lg:w-[360px]">
          <div className="rounded-2xl card p-6">
            <h2 className="mb-6 text-xl font-bold text-ink">
              Order Summary
            </h2>
            <div className="mb-6 space-y-4 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-ink-muted">
                  Subtotal ({count} {count === 1 ? "item" : "items"})
                </span>
                <span className="font-medium text-ink">{formatINR(subtotal)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-ink-muted">Shipping</span>
                <span
                  className={`font-medium ${shipping === 0 ? "text-success" : "text-ink"}`}
                >
                  {shipping === 0 ? "Free" : formatINR(shipping)}
                </span>
              </div>
              {shipping === 0 ? (
                <div className="flex items-center gap-2 rounded-md bg-green-50 px-3 py-2 text-xs text-success">
                  <Icon name="local_shipping" className="h-4 w-4" />
                  Your order qualifies for FREE shipping!
                </div>
              ) : (
                <p className="text-xs text-ink-muted">
                  Add {formatINR(999 - subtotal)} more for FREE shipping.
                </p>
              )}
              <div className="flex items-center justify-between">
                <span className="text-ink-muted">Taxes (calculated at checkout)</span>
                <span className="font-medium text-ink">--</span>
              </div>
            </div>
            <div className="mb-6 border-t border-black/5 pt-4">
              <div className="flex items-center justify-between">
                <span className="text-lg font-bold text-ink">Total</span>
                <span className="text-2xl font-bold text-ink">{formatINR(total)}</span>
              </div>
            </div>
            <div className="space-y-3">
              <Link
                href="/checkout"
                className="btn-primary block w-full py-4"
              >
                Proceed to Checkout
              </Link>
              <Link
                href="/products"
                className="block w-full rounded-xl border border-stone-300 py-3 text-center font-medium text-ink transition-colors hover:border-primary hover:text-violet-700"
              >
                Continue Shopping
              </Link>
            </div>
          </div>
          <div className="mt-6 flex justify-center gap-6 text-ink-muted opacity-70">
            <div className="flex flex-col items-center gap-1">
              <Icon name="lock" className="h-6 w-6" />
              <span className="text-xs">Secure</span>
            </div>
            <div className="flex flex-col items-center gap-1">
              <Icon name="verified" className="h-6 w-6" />
              <span className="text-xs">Authentic</span>
            </div>
            <div className="flex flex-col items-center gap-1">
              <Icon name="assignment_return" className="h-6 w-6" />
              <span className="text-xs">Easy Returns</span>
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}
