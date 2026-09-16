import Link from "next/link";
import {
  MONTH_NAMES,
  getCategories,
  getUpcomingFestivals,
  getRegions,
  getRegionStats,
  bestsellerProducts,
} from "@/data/catalog";
import { ProductCard } from "@/components/ProductCard";
import { FestivalCard } from "@/components/FestivalCard";
import { RegionCard } from "@/components/RegionCard";
import { CategoryArt } from "@/components/artwork";
import { Icon } from "@/components/icons";
import { festivalImage } from "@/data/festivalImages";
import Interactive3DLogo from "@/components/Interactive3DLogo";

const now = new Date();
const thisMonth = now.getMonth() + 1;

/* ─── Section header ─────────────────────────────────────────── */
function SectionHead({
  eyebrow,
  title,
  subtitle,
  link,
  linkLabel,
}: {
  eyebrow?: string;
  title: string;
  subtitle?: string;
  link?: string;
  linkLabel?: string;
}) {
  return (
    <div className="mb-10 flex flex-col justify-between gap-4 md:flex-row md:items-end">
      <div>
        {eyebrow && (
          <p className="eyebrow mb-4">
            <span
              className="inline-block h-px w-6 align-middle"
              style={{ background: "linear-gradient(90deg, #c9a96e, #e8c882)" }}
            />
            <span className="ml-2">{eyebrow}</span>
          </p>
        )}
        <h2
          className="text-4xl font-medium leading-none md:text-5xl"
          style={{ fontFamily: "var(--font-cormorant), Georgia, serif", color: "rgba(245,240,232,0.95)" }}
        >
          {title}
        </h2>
        {subtitle && (
          <p className="mt-3 text-sm" style={{ color: "rgba(245,240,232,0.4)" }}>
            {subtitle}
          </p>
        )}
      </div>
      {link && (
        <Link
          href={link}
          className="group flex items-center gap-2 text-sm font-medium shrink-0"
          style={{ color: "rgba(201,169,110,0.7)", transition: "color 200ms var(--ease-out)" }}
        >
          {linkLabel ?? "View all"}
          <Icon name="arrow_forward" className="h-4 w-4 group-hover:translate-x-1" style={{ transition: "transform 250ms var(--ease-out)" }} />
        </Link>
      )}
    </div>
  );
}


/* ─── Category pill ──────────────────────────────────────────── */
const CATEGORY_COLORS = [
  { from: "#7c3aed", to: "#a855f7" },  // violet
  { from: "#be185d", to: "#e879a0" },  // rose
  { from: "#b45309", to: "#f59e0b" },  // amber
  { from: "#065f46", to: "#10b981" },  // emerald
  { from: "#1d4ed8", to: "#60a5fa" },  // blue
  { from: "#7c2d12", to: "#f97316" },  // orange
  { from: "#312e81", to: "#818cf8" },  // indigo
  { from: "#134e4a", to: "#2dd4bf" },  // teal
];

/* ─── Page ───────────────────────────────────────────────────── */
export default async function HomePage() {
  const [categories, upcoming, regions, regionStats, bestsellers] =
    await Promise.all([
      getCategories(),
      getUpcomingFestivals(thisMonth),
      getRegions(),
      getRegionStats(),
      bestsellerProducts(),
    ]);

  const heroTiles = upcoming.slice(0, 4).map((f) => ({
    name: f.name,
    slug: f.slug,
    image: festivalImage(f.slug),
  }));

  return (
    <div>
      {/* ══════════ HERO ══════════════════════════════════════════════ */}
      <section
        className="relative w-full overflow-hidden flex items-center justify-center"
        style={{ minHeight: "92vh", background: "#08070a" }}
      >
        {/* Cinematic Background Video */}
        <video
          autoPlay
          loop
          muted
          playsInline
          className="pointer-events-none absolute inset-0 h-full w-full object-cover z-0 opacity-100"
        >
          <source src="/images/make_a_profesinoal_old_primium.mp4" type="video/mp4" />
        </video>

        {/* Ambient Dark Overlay (Softened for video visibility, transitioning to dark footer) */}
        <div
          className="pointer-events-none absolute inset-0 z-0 bg-gradient-to-b from-black/5 via-black/15 to-[#08070a]"
        />

        {/* Dot pattern */}
        <div className="pattern-dots absolute inset-0 opacity-10 z-0" />

        {/* Gold accent line at top */}
        <div
          className="absolute top-0 left-0 right-0 h-px z-10"
          style={{ background: "linear-gradient(90deg, transparent, rgba(201,169,110,0.4), transparent)" }}
        />

        <div className="relative z-10 mx-auto max-w-5xl px-5 py-24 md:px-8 flex flex-col items-center text-center">
          {/* Eyebrow */}
          <div className="inline-flex items-center gap-3 mb-8">
            <span
              className="h-px w-10"
              style={{ background: "linear-gradient(90deg, transparent, #c9a96e)" }}
            />
            <span
              className="text-[10px] font-bold uppercase tracking-[0.3em]"
              style={{ color: "rgba(201,169,110,0.85)" }}
            >
              Every festival · Every state
            </span>
            <span
              className="h-px w-10"
              style={{ background: "linear-gradient(90deg, #c9a96e, transparent)" }}
            />
          </div>

          {/* Main headline */}
          <h1
            className="leading-[1.1] tracking-tight mb-8"
            style={{
              fontFamily: "var(--font-cormorant), Georgia, serif",
              fontSize: "clamp(52px, 8vw, 92px)",
              fontWeight: 500,
              color: "rgba(245,240,232,0.98)",
              textShadow: "0 2px 24px rgba(0,0,0,0.6)"
            }}
          >
            Experience the sacred essence of <br />
            <span
              style={{
                background: "linear-gradient(135deg, #a78bfa 0%, #e879a0 40%, #fbbf24 100%)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
                backgroundClip: "text",
                fontStyle: "italic",
              }}
            >
              The Divine Things
            </span>
          </h1>

          {/* Subtext */}
          <p
            className="max-w-2xl text-base leading-relaxed md:text-lg mb-10"
            style={{ color: "rgba(245,240,232,0.75)", fontWeight: 300, textShadow: "0 1px 12px rgba(0,0,0,0.6)" }}
          >
            Handcrafted pooja essentials, regional sweets, ethnic wear and decor from
            every Indian celebration — straight from local artisans.
          </p>

          {/* CTAs */}
          <div className="flex flex-wrap justify-center gap-4">
            <Link href="/products" className="btn-primary">
              Shop Now
              <Icon name="arrow_forward" className="h-4 w-4" />
            </Link>
            <Link href="/festivals" className="btn-ghost">
              Festival Calendar
            </Link>
          </div>
        </div>

        {/* Bottom fade */}
        <div
          className="pointer-events-none absolute bottom-0 left-0 right-0 h-32"
          style={{ background: "linear-gradient(180deg, transparent, #08070a)" }}
        />
      </section>


      {/* ══════════ UPCOMING FESTIVALS ════════════════════════════════ */}
      <section className="py-24" style={{ background: "rgba(255,255,255,0.015)" }}>
        <div className="section-wrap">
          <SectionHead
            eyebrow="Calendar"
            title="Upcoming Festivals"
            subtitle={`In ${MONTH_NAMES[thisMonth - 1]} and beyond`}
            link="/festivals"
            linkLabel="View all"
          />
        </div>
        <div className="marquee overflow-hidden">
          <div className="marquee-track flex w-max py-3 pl-5 md:pl-8" style={{ animationDirection: "reverse" }}>
            {[...upcoming, ...upcoming].map((f, i) => (
              <div key={`${f.slug}-${i}`} className="mr-5 shrink-0" style={{ width: "180px" }}>
                <FestivalCard festival={f} />
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ══════════ CATEGORIES ════════════════════════════════════════ */}
      <section className="section-wrap py-24">
        <SectionHead
          eyebrow="Shop by category"
          title="Find Your Celebration"
          link="/products"
          linkLabel="View all"
        />

        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          {categories.map((c, i) => {
            const grad = CATEGORY_COLORS[i % CATEGORY_COLORS.length];
            return (
              <Link
                key={c.slug}
                href={`/products?category=${c.slug}`}
                className="category-card group relative flex flex-col gap-4 overflow-hidden rounded-2xl p-5 animate-[fadeUp_0.6s_both]"
                style={{ animationDelay: `${i * 80}ms` }}
              >
                {/* Icon */}
                <div
                  className="flex h-12 w-12 items-center justify-center rounded-xl group-hover:scale-110"
                  style={{ background: `linear-gradient(135deg, ${grad.from}, ${grad.to})`, transition: "transform 300ms var(--ease-out)" }}
                >
                  <CategoryArt slug={c.slug} className="h-7 w-7 text-white" />
                </div>

                {/* Text */}
                <div>
                  <h3
                    className="mb-1 font-medium group-hover:text-[#e8c882]"
                    style={{ color: "rgba(245,240,232,0.9)", fontFamily: "var(--font-cormorant), Georgia, serif", fontSize: "18px", transition: "color 200ms var(--ease-out)" }}
                  >
                    {c.name}
                  </h3>
                  <p className="line-clamp-2 text-xs leading-relaxed" style={{ color: "rgba(245,240,232,0.35)" }}>
                    {c.description}
                  </p>
                </div>

                {/* Arrow */}
                <Icon
                  name="arrow_forward"
                  className="absolute right-4 bottom-4 h-4 w-4 opacity-0 group-hover:opacity-100 group-hover:translate-x-0.5"
                  style={{ color: "#c9a96e", transition: "opacity 200ms var(--ease-out), transform 250ms var(--ease-out)" }}
                />
              </Link>
            );
          })}
        </div>
      </section>

      {/* ══════════ GOLD DIVIDER BAND ═════════════════════════════════ */}
      <div className="section-wrap">
        <hr className="gold-divider" />
      </div>

      {/* ══════════ BESTSELLERS ═══════════════════════════════════════ */}
      <section className="section-wrap py-24">
        <SectionHead
          eyebrow="Trending"
          title="Divine Bestsellers"
          subtitle="Loved by thousands of festival celebrants"
          link="/products"
          linkLabel="View all"
        />
        <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-6">
          {bestsellers.slice(0, 6).map((p) => (
            <ProductCard key={p.id} product={p} />
          ))}
        </div>
      </section>

      {/* ══════════ CTA BANNER ════════════════════════════════════════ */}
      <section className="section-wrap pb-24">
        <div
          className="relative overflow-hidden rounded-3xl p-10 md:p-16 text-center"
          style={{
            background: "linear-gradient(135deg, rgba(124,58,237,0.2) 0%, rgba(201,169,110,0.15) 50%, rgba(190,24,93,0.15) 100%)",
            border: "1px solid rgba(201,169,110,0.15)",
          }}
        >
          {/* Subtle glow orb */}
          <div
            className="pointer-events-none absolute left-1/2 top-1/2 h-64 w-64 -translate-x-1/2 -translate-y-1/2 rounded-full blur-3xl"
            style={{ background: "rgba(201,169,110,0.12)" }}
          />

          <div className="relative z-10">
            <p className="eyebrow mb-4 justify-center">Discover India</p>
            <h2
              className="mb-4 text-4xl font-medium md:text-5xl"
              style={{
                fontFamily: "var(--font-cormorant), Georgia, serif",
                color: "rgba(245,240,232,0.95)",
              }}
            >
              500+ festivals, one store
            </h2>
            <p
              className="mx-auto mb-8 max-w-lg text-sm leading-relaxed"
              style={{ color: "rgba(245,240,232,0.45)" }}
            >
              From Diwali diyas to Onam flowers — explore every celebration
              across all 36 states and union territories of India.
            </p>
            <div className="flex flex-wrap items-center justify-center gap-4">
              <Link href="/festivals" className="btn-primary">
                Explore Festival Calendar
                <Icon name="arrow_forward" className="h-4 w-4" />
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
