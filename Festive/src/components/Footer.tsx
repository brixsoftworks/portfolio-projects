"use client";

import Link from "next/link";


const SHOP_LINKS = [
  { href: "/products", label: "All Products" },
  { href: "/products?category=pooja", label: "Pooja Essentials" },
  { href: "/products?category=sweets", label: "Sweets & Snacks" },
  { href: "/products?category=clothing", label: "Ethnic Wear" },
  { href: "/wishlist", label: "Wishlist" },
];

const EXPLORE_LINKS = [
  { href: "/festivals", label: "Festival Calendar" },
  { href: "/cart", label: "My Cart" },
  { href: "/about", label: "About The Divine Things" },
];

export function Footer() {
  return (
    <footer
      className="mt-20 w-full"
      style={{
        background: "linear-gradient(180deg, rgba(8,7,10,0) 0%, #08070a 8%, #08070a 100%)",
        borderTop: "1px solid rgba(255,255,255,0.06)",
      }}
    >
      {/* Gold divider */}
      <div className="mx-auto max-w-7xl px-5 md:px-8">
        <hr className="gold-divider mb-14" />
      </div>

      <div className="mx-auto max-w-7xl px-5 pb-12 md:px-8">
        <div className="grid grid-cols-1 gap-12 md:grid-cols-4">

          {/* Brand column */}
          <div className="md:col-span-1">
            <Link href="/" className="mb-6 flex items-center gap-2.5 group">
              <span
                className="flex h-9 w-9 items-center justify-center rounded-full transition-all duration-300 group-hover:scale-110"
                style={{
                  background: "linear-gradient(135deg, rgba(201,169,110,0.2), rgba(124,58,237,0.15))",
                  border: "1px solid rgba(201,169,110,0.25)",
                }}
              >
                <img
                  src="/images/products/logo.png"
                  alt="The Divine Things"
                  className="h-6 w-6 object-contain"
                />
              </span>
              <span
                className="text-xl font-semibold tracking-wide"
                style={{
                  fontFamily: "var(--font-cormorant), Georgia, serif",
                  background: "linear-gradient(135deg, #c9a96e 0%, #e8c882 50%, #c9a96e 100%)",
                  WebkitBackgroundClip: "text",
                  WebkitTextFillColor: "transparent",
                  backgroundClip: "text",
                }}
              >
                The Divine Things
              </span>
            </Link>

            <p
              className="mb-6 text-sm leading-relaxed italic"
              style={{
                fontFamily: "var(--font-cormorant), Georgia, serif",
                color: "rgba(245,240,232,0.45)",
                fontSize: "15px",
              }}
            >
              &ldquo;India&apos;s land of festivals — 500+ celebrations,<br />
              one store.&rdquo;
            </p>

            <p className="text-[11px] tracking-wide" style={{ color: "rgba(245,240,232,0.25)" }}>
              © {new Date().getFullYear()} The Divine Things.<br />
              Handcrafted with love in India.
            </p>
          </div>

          {/* Shop links */}
          <div>
            <h4
              className="mb-5 text-[10px] font-bold uppercase tracking-[0.25em]"
              style={{ color: "rgba(201,169,110,0.7)" }}
            >
              Shop
            </h4>
            <ul className="space-y-3">
              {SHOP_LINKS.map((l) => (
                <li key={l.href}>
                  <Link
                    href={l.href}
                    className="group flex items-center gap-2 text-sm transition-colors duration-200"
                    style={{ color: "rgba(245,240,232,0.45)", fontFamily: "var(--font-montserrat)" }}
                  >
                    <span
                      className="h-px w-4 transition-all duration-300 group-hover:w-6"
                      style={{ background: "linear-gradient(90deg, #c9a96e, #e8c882)" }}
                    />
                    <span className="transition-colors duration-200 group-hover:text-[#c9a96e]">
                      {l.label}
                    </span>
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Explore links */}
          <div>
            <h4
              className="mb-5 text-[10px] font-bold uppercase tracking-[0.25em]"
              style={{ color: "rgba(201,169,110,0.7)" }}
            >
              Explore
            </h4>
            <ul className="space-y-3">
              {EXPLORE_LINKS.map((l) => (
                <li key={l.href}>
                  <Link
                    href={l.href}
                    className="group flex items-center gap-2 text-sm transition-colors duration-200"
                    style={{ color: "rgba(245,240,232,0.45)", fontFamily: "var(--font-montserrat)" }}
                  >
                    <span
                      className="h-px w-4 transition-all duration-300 group-hover:w-6"
                      style={{ background: "linear-gradient(90deg, #c9a96e, #e8c882)" }}
                    />
                    <span className="transition-colors duration-200 group-hover:text-[#c9a96e]">
                      {l.label}
                    </span>
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Newsletter */}
          <div>
            <h4
              className="mb-5 text-[10px] font-bold uppercase tracking-[0.25em]"
              style={{ color: "rgba(201,169,110,0.7)" }}
            >
              Stay Connected
            </h4>
            <p className="mb-5 text-sm leading-relaxed" style={{ color: "rgba(245,240,232,0.4)" }}>
              Festival updates and exclusive offers — delivered to your inbox.
            </p>
            <div className="relative flex">
              <input
                type="email"
                placeholder="your@email.com"
                aria-label="Email for newsletter"
                className="w-full rounded-l-full px-4 py-3 text-sm outline-none transition-all duration-200"
                style={{
                  background: "rgba(255,255,255,0.05)",
                  border: "1px solid rgba(255,255,255,0.1)",
                  borderRight: "none",
                  color: "rgba(245,240,232,0.8)",
                  fontFamily: "var(--font-montserrat)",
                }}
                onFocus={(e) => {
                  e.currentTarget.style.borderColor = "rgba(201,169,110,0.4)";
                  e.currentTarget.style.background = "rgba(255,255,255,0.08)";
                }}
                onBlur={(e) => {
                  e.currentTarget.style.borderColor = "rgba(255,255,255,0.1)";
                  e.currentTarget.style.background = "rgba(255,255,255,0.05)";
                }}
              />
              <button
                type="button"
                aria-label="Subscribe to newsletter"
                className="shrink-0 rounded-r-full px-5 py-3 text-sm font-semibold transition-all duration-200 hover:opacity-90 active:scale-95"
                style={{
                  background: "linear-gradient(135deg, #c9a96e, #e8c882)",
                  color: "#0a0809",
                  fontFamily: "var(--font-montserrat)",
                  letterSpacing: "0.04em",
                }}
              >
                Join
              </button>
            </div>

            {/* Social proof */}
            <p className="mt-4 text-[11px]" style={{ color: "rgba(245,240,232,0.25)" }}>
              Join 12,000+ festival lovers 🪔
            </p>
          </div>
        </div>

        {/* Bottom bar */}
        <hr className="gold-divider mt-12 mb-6" />
        <div className="flex flex-col items-center justify-between gap-4 text-[11px] md:flex-row" style={{ color: "rgba(245,240,232,0.25)" }}>
          <div className="flex items-center gap-6">
            <Link href="/about" className="hover:text-[#c9a96e] transition-colors">About</Link>
            <Link href="/products" className="hover:text-[#c9a96e] transition-colors">Products</Link>
            <Link href="/festivals" className="hover:text-[#c9a96e] transition-colors">Festivals</Link>
          </div>
          <p>Made with ❤️ for India&apos;s festivals</p>
        </div>
      </div>
    </footer>
  );
}
