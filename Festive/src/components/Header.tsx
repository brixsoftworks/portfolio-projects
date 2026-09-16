"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useCart } from "@/lib/CartContext";
import { useWishlist } from "@/lib/WishlistContext";
import { Icon } from "@/components/icons";
import { auth } from "@/lib/firebase";
import { onAuthStateChanged, signOut } from "firebase/auth";

const NAV = [
  { href: "/products", label: "Shop" },
  { href: "/festivals", label: "Festivals" },
  { href: "/about", label: "About" },
];

export function Header() {
  const router = useRouter();
  const pathname = usePathname();
  const { count, setOpen } = useCart();
  const { count: wishCount } = useWishlist();
  const [query, setQuery] = useState("");
  const [menuOpen, setMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", onScroll, { passive: true });
    
    // Auth Listener
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser);
    });

    return () => {
      window.removeEventListener("scroll", onScroll);
      unsubscribe();
    };
  }, []);

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    const q = query.trim();
    if (q) router.push(`/search?q=${encodeURIComponent(q)}`);
  };

  return (
    <header
      className="sticky top-0 z-50 w-full transition-all duration-300"
      style={{
        background: scrolled
          ? "rgba(8,7,10,0.92)"
          : "rgba(8,7,10,0.75)",
        borderBottom: "1px solid rgba(255,255,255,0.06)",
        backdropFilter: "blur(24px) saturate(180%)",
        WebkitBackdropFilter: "blur(24px) saturate(180%)",
      }}
    >
      <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-3.5 md:px-8">

        {/* Left — Logo + mobile menu toggle */}
        <div className="flex items-center gap-3">
          <button
            className="icon-btn md:hidden"
            onClick={() => setMenuOpen((v) => !v)}
            aria-label="Toggle menu"
            aria-expanded={menuOpen}
          >
            <Icon name={menuOpen ? "close" : "menu"} className="h-5 w-5" />
          </button>

          <Link href="/" className="group flex items-center gap-2.5">
            {/* Gold glow ring around logo */}
            <span className="relative flex h-9 w-9 items-center justify-center rounded-full"
              style={{ background: "linear-gradient(135deg, rgba(201,169,110,0.2), rgba(124,58,237,0.15))", border: "1px solid rgba(201,169,110,0.25)" }}>
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
        </div>

        {/* Center — Search */}
        <form onSubmit={submit} className="relative hidden max-w-sm flex-1 md:mx-8 lg:mx-12 md:flex">
          <span className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2" style={{ color: "rgba(201,169,110,0.5)" }}>
            <Icon name="search" className="h-4 w-4" />
          </span>
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            type="text"
            placeholder="Search festivals, sweets, diyas…"
            className="input-pill pl-11 pr-4 text-sm"
            aria-label="Search products"
          />
        </form>

        {/* Right — Nav + actions */}
        <div className="flex items-center gap-1 md:gap-2">
          <nav className="hidden items-center gap-0.5 lg:flex" aria-label="Main navigation">
            {NAV.map((n) => {
              const active = pathname === n.href || pathname.startsWith(`${n.href}/`);
              return (
                <Link
                  key={n.href}
                  href={n.href}
                  className="relative px-4 py-2 text-[13px] font-medium tracking-wide transition-colors duration-200"
                  style={{
                    color: active ? "#c9a96e" : "rgba(245,240,232,0.6)",
                    fontFamily: "var(--font-montserrat), sans-serif",
                  }}
                >
                  {n.label}
                  {/* Animated gold underline */}
                  <span
                    className="absolute bottom-0.5 left-4 right-4 h-px transition-all duration-200"
                    style={{
                      background: "linear-gradient(90deg, #c9a96e, #e8c882)",
                      transform: active ? "scaleX(1)" : "scaleX(0)",
                      transformOrigin: "left",
                    }}
                  />
                </Link>
              );
            })}
          </nav>

          <div className="flex items-center gap-1 ml-2">
            {/* Auth */}
            {user ? (
              <button
                onClick={() => signOut(auth)}
                className="icon-btn"
                aria-label="Sign out"
              >
                <Icon name="logout" className="h-4.5 w-4.5" />
              </button>
            ) : (
              <Link href="/login" className="icon-btn" aria-label="Sign in">
                <Icon name="person" className="h-4.5 w-4.5" />
              </Link>
            )}

            {/* Wishlist */}
            <Link href="/wishlist" className="icon-btn" aria-label={`Wishlist (${wishCount} items)`}>
              <Icon name="favorite_border" className="h-4.5 w-4.5" />
              {wishCount > 0 && (
                <span
                  className="absolute -right-1 -top-1 flex h-4 min-w-4 items-center justify-center rounded-full px-1 text-[9px] font-bold"
                  style={{ background: "linear-gradient(135deg, #c9a96e, #e8c882)", color: "#0a0809" }}
                >
                  {wishCount}
                </span>
              )}
            </Link>

            {/* Cart */}
            <button
              onClick={() => setOpen(true)}
              className="icon-btn relative"
              aria-label={`Cart (${count} items)`}
            >
              <Icon name="shopping_bag" className="h-4.5 w-4.5" />
              {count > 0 && (
                <span
                  className="absolute -right-1 -top-1 flex h-4 min-w-4 items-center justify-center rounded-full px-1 text-[9px] font-bold"
                  style={{ background: "linear-gradient(135deg, #c9a96e, #e8c882)", color: "#0a0809" }}
                >
                  {count}
                </span>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      {menuOpen && (
        <div
          className="border-t md:hidden"
          style={{ borderColor: "rgba(255,255,255,0.06)", background: "rgba(8,7,10,0.96)" }}
        >
          {/* Mobile search */}
          <div className="px-5 pt-4 pb-2">
            <form onSubmit={submit} className="relative">
              <span className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2" style={{ color: "rgba(201,169,110,0.5)" }}>
                <Icon name="search" className="h-4 w-4" />
              </span>
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search products…"
                className="input-pill pl-11 text-sm"
                aria-label="Search products"
              />
            </form>
          </div>

          {/* Mobile nav links */}
          <nav className="flex flex-col px-5 pb-4 pt-2" aria-label="Mobile navigation">
            {NAV.map((n) => {
              const active = pathname === n.href || pathname.startsWith(`${n.href}/`);
              return (
                <Link
                  key={n.href}
                  href={n.href}
                  onClick={() => setMenuOpen(false)}
                  className="flex items-center justify-between py-3 text-sm font-medium transition-colors"
                  style={{
                    borderBottom: "1px solid rgba(255,255,255,0.05)",
                    color: active ? "#c9a96e" : "rgba(245,240,232,0.65)",
                  }}
                >
                  {n.label}
                  <Icon name="chevron_right" className="h-4 w-4 opacity-40" />
                </Link>
              );
            })}
          </nav>
        </div>
      )}
    </header>
  );
}
