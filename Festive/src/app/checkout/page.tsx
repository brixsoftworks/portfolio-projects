"use client";

import { useState } from "react";
import Link from "next/link";
import { useCart } from "@/lib/CartContext";
import { formatINR } from "@/lib/format";
import { placeOrder } from "@/lib/orders";
import { Icon } from "@/components/icons";

export default function CheckoutPage() {
  const { items, subtotal, clear } = useCart();
  const [placed, setPlaced] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState({
    name: "",
    phone: "",
    email: "",
    address: "",
    city: "",
    state: "",
    pincode: "",
  });

  if (items.length === 0 && !placed) {
    return (
      <div className="mx-auto flex max-w-7xl flex-col items-center px-4 py-24 text-center">
        <div className="mb-6 flex h-24 w-24 items-center justify-center rounded-full bg-violet-100">
          <Icon name="shopping_bag" className="h-12 w-12 text-violet-500/50" />
        </div>
        <h1 className="mb-3 text-2xl font-bold tracking-tight text-ink md:text-3xl">
          Nothing to checkout
        </h1>
        <p className="mb-8 text-base text-ink-muted">
          Add festive favourites to your cart first, then complete your order here.
        </p>
        <Link
          href="/products"
          className="btn-primary"
        >
          Add items to your cart
        </Link>
      </div>
    );
  }

  if (placed) {
    return (
      <div className="mx-auto flex max-w-7xl flex-col items-center px-4 py-24 text-center">
        <div className="mb-6 flex h-24 w-24 items-center justify-center rounded-full bg-green-50">
          <Icon name="check_circle" className="h-12 w-12 text-success" />
        </div>
        <h1 className="mb-3 text-3xl font-bold tracking-tight text-ink md:text-4xl">
          Order placed!
        </h1>
        <p className="mb-8 max-w-md text-base text-ink-muted">
          Thank you, {form.name || "friend"}! Your festive order is on its way. A
          confirmation has been sent to {form.email || "your email"}.
        </p>
        <Link
          href="/products"
          className="btn-primary"
        >
          Continue Shopping
        </Link>
      </div>
    );
  }

  const shipping = subtotal >= 999 ? 0 : 49;
  const total = subtotal + shipping;
  const valid =
    form.name && form.phone && form.address && form.city && form.state && form.pincode;

  const update = (key: keyof typeof form) => (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => setForm((f) => ({ ...f, [key]: e.target.value }));

  const inputClass =
    "block w-full rounded-lg border border-stone-300 bg-white px-3 py-2.5 text-sm text-ink shadow-sm outline-none transition-colors placeholder:text-stone-400 focus:border-violet-500";

  return (
    <div className="mx-auto w-full max-w-7xl px-4 py-8 sm:px-6 lg:px-8 md:py-12">
      <div className="mb-8">
        <h1 className="text-4xl font-bold tracking-tight text-ink">Checkout</h1>
        <p className="mt-2 text-ink-muted">Complete your order securely.</p>
      </div>

      <div className="flex flex-col items-start gap-8 lg:flex-row">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            setSubmitting(true);
            placeOrder(
              items,
              {
                name: form.name,
                phone: form.phone,
                email: form.email,
                address: form.address,
                city: form.city,
                state: form.state,
                pincode: form.pincode,
              },
              { subtotal, shipping, total }
            )
              .then(() => {
                setPlaced(true);
                clear();
              })
              .catch((err) => {
                console.error("Order failed:", err);
                alert("Something went wrong placing your order. Please try again.");
              })
              .finally(() => setSubmitting(false));
          }}
          className="w-full rounded-2xl border border-black/5 bg-white p-6 shadow-sm md:p-8 lg:flex-1"
        >
          <h2 className="mb-6 flex items-center gap-2 border-b border-black/5 pb-4 text-xl font-semibold text-ink">
            <Icon name="local_shipping" className="h-6 w-6 text-violet-600" />
            Delivery Details
          </h2>
          <div className="space-y-6">
            <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
              <div className="space-y-1.5">
                <label
                  htmlFor="fullName"
                  className="block text-xs font-semibold uppercase tracking-wide text-stone-500"
                >
                  Full Name
                </label>
                <input
                  id="fullName"
                  required
                  value={form.name}
                  onChange={update("name")}
                  className={inputClass}
                  placeholder="Aarav Sharma"
                />
              </div>
              <div className="space-y-1.5">
                <label
                  htmlFor="phone"
                  className="block text-xs font-semibold uppercase tracking-wide text-stone-500"
                >
                  Phone Number
                </label>
                <input
                  id="phone"
                  required
                  value={form.phone}
                  onChange={update("phone")}
                  className={inputClass}
                  placeholder="+91 98765 43210"
                />
              </div>
            </div>
            <div className="space-y-1.5">
              <label
                htmlFor="email"
                className="block text-xs font-semibold uppercase tracking-wide text-stone-500"
              >
                Email Address
              </label>
              <input
                id="email"
                type="email"
                value={form.email}
                onChange={update("email")}
                className={inputClass}
                placeholder="aarav@example.com"
              />
            </div>
            <div className="space-y-1.5">
              <label
                htmlFor="address"
                className="block text-xs font-semibold uppercase tracking-wide text-stone-500"
              >
                Street Address
              </label>
              <textarea
                id="address"
                required
                value={form.address}
                onChange={(e) => update("address")(e)}
                rows={3}
                className={`${inputClass} resize-none`}
                placeholder="Flat No. / Building Name, Street"
              />
            </div>
            <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
              <div className="space-y-1.5">
                <label
                  htmlFor="city"
                  className="block text-xs font-semibold uppercase tracking-wide text-stone-500"
                >
                  City
                </label>
                <input
                  id="city"
                  required
                  value={form.city}
                  onChange={update("city")}
                  className={inputClass}
                  placeholder="Mumbai"
                />
              </div>
              <div className="space-y-1.5">
                <label
                  htmlFor="state"
                  className="block text-xs font-semibold uppercase tracking-wide text-stone-500"
                >
                  State
                </label>
                <input
                  id="state"
                  required
                  value={form.state}
                  onChange={update("state")}
                  className={inputClass}
                  placeholder="Select State"
                />
              </div>
              <div className="space-y-1.5">
                <label
                  htmlFor="pin"
                  className="block text-xs font-semibold uppercase tracking-wide text-stone-500"
                >
                  PIN Code
                </label>
                <input
                  id="pin"
                  required
                  value={form.pincode}
                  onChange={update("pincode")}
                  className={inputClass}
                  placeholder="400001"
                />
              </div>
            </div>

            <div className="border-t border-black/5 pt-6">
              <h3 className="mb-4 flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-ink">
                <Icon name="payments" className="h-5 w-5 text-stone-400" />
                Payment Status: Free Tier
              </h3>
              <div className="flex items-start gap-3 rounded-xl border border-stone-200 bg-emerald-50 p-4">
                <Icon name="check_circle" className="h-5 w-5 shrink-0 text-emerald-600" />
                <p className="text-sm leading-relaxed text-emerald-800">
                  Your order is fully complimentary. No credit card or payment information is required to checkout today.
                </p>
              </div>
            </div>

            <div className="pt-4">
              <button
                type="submit"
                disabled={!valid || submitting}
                className="flex w-full items-center justify-between rounded-full bg-gradient-to-r from-violet-600 to-fuchsia-500 px-6 py-4 font-bold text-white shadow-md shadow-violet-500/20 transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40"
              >
                <span>{submitting ? "Placing Order…" : "Place Order"}</span>
                <span className="text-lg">{formatINR(total)}</span>
              </button>
            </div>
          </div>
        </form>

        <aside className="w-full shrink-0 lg:sticky lg:top-24 lg:w-[360px]">
          <div className="rounded-2xl border border-black/5 bg-white p-6 shadow-sm">
            <h2 className="mb-6 flex items-center gap-2 border-b border-black/5 pb-4 text-xl font-semibold text-ink">
              <Icon name="shopping_bag" className="h-6 w-6 text-ink" />
              Order Summary
            </h2>
            <div className="mb-6 space-y-4">
              {items.map((i) => (
                <div key={i.id} className="flex items-start gap-4">
                  <div className="h-20 w-16 shrink-0 overflow-hidden rounded-lg border border-stone-200 bg-stone-100">
                    <img
                      src={i.image}
                      alt={i.name}
                      className="h-full w-full object-cover"
                    />
                  </div>
                  <div className="flex-1">
                    <h4 className="text-sm font-medium leading-tight text-ink">
                      {i.name}
                    </h4>
                    <p className="mt-1 text-xs text-ink-muted">Qty: {i.qty}</p>
                    <p className="mt-1 text-sm font-bold text-ink">
                      {formatINR(i.price * i.qty)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
            <div className="space-y-3 border-t border-black/5 pt-4">
              <div className="flex justify-between text-sm text-stone-600">
                <span>Subtotal</span>
                <span className="tabular-nums">{formatINR(subtotal)}</span>
              </div>
              <div className="flex justify-between text-sm text-stone-600">
                <span>Shipping</span>
                <span
                  className={`font-medium ${shipping === 0 ? "text-success" : ""}`}
                >
                  {shipping === 0 ? "Free" : formatINR(shipping)}
                </span>
              </div>
              <div className="mt-2 flex items-center justify-between border-t border-black/5 pt-3">
                <span className="text-base font-bold text-ink">Total</span>
                <span className="text-xl font-bold text-ink">{formatINR(total)}</span>
              </div>
            </div>
          </div>
          <div className="mt-6 flex items-center justify-center gap-2 text-xs text-stone-400">
            <Icon name="lock" className="h-4 w-4" />
            Secure Checkout
          </div>
        </aside>
      </div>
    </div>
  );
}
