import Link from "next/link";
import { notFound } from "next/navigation";
import {
  getFestival,
  getFestivals,
  getFestivalSlugs,
  MONTH_NAMES,
  getRegion,
  productsByRegion,
} from "@/data/catalog";
import { ProductCard } from "@/components/ProductCard";
import { FestivalCard } from "@/components/FestivalCard";
import { FestivalArt } from "@/components/artwork";
import { Icon } from "@/components/icons";
import { festivalImage } from "@/data/festivalImages";

export async function generateStaticParams() {
  const slugs = await getFestivalSlugs();
  return slugs.map((slug) => ({ slug }));
}

export const dynamicParams = false;

const HERO_IMAGES: Record<string, string> = {
  onam: "/images/products/onam-sadya.jpg",
};

export default async function FestivalPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const festival = await getFestival(slug);
  if (!festival) notFound();

  const [allFestivals, region, regionProducts] = await Promise.all([
    getFestivals(),
    festival.stateSlug ? getRegion(festival.stateSlug) : Promise.resolve(null),
    festival.stateSlug ? productsByRegion(festival.stateSlug) : Promise.resolve([]),
  ]);
  const sameMonth = allFestivals
    .filter((f) => f.month === festival.month && f.slug !== festival.slug)
    .slice(0, 4);
  const heroImage = festivalImage(festival.slug) ?? HERO_IMAGES[festival.slug];
  const monthName = MONTH_NAMES[festival.month - 1];

  return (
    <main className="flex-grow">
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Breadcrumb */}
        <nav className="mb-6 flex items-center gap-2 text-sm text-ink-muted">
          <Link href="/" className="transition-colors hover:text-violet-700">Home</Link>
          <Icon name="arrow_forward" className="h-3.5 w-3.5 rotate-180 text-stone-300" />
          <Link href="/festivals" className="transition-colors hover:text-violet-700">Festival Calendar</Link>
          <Icon name="arrow_forward" className="h-3.5 w-3.5 rotate-180 text-stone-300" />
          <span className="font-medium text-ink">{festival.name}</span>
        </nav>
      </div>

      {/* Hero */}
      {heroImage ? (
        <section className="relative mx-auto max-w-7xl overflow-hidden rounded-[2rem] px-4 sm:px-6 lg:px-8">
          <div className="relative overflow-hidden rounded-[2rem] shadow-xl">
            <img
              src={heroImage}
              alt={`${festival.name} celebration`}
              className="h-[480px] w-full object-cover"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/85 via-black/40 to-black/20" />
            <div className="absolute inset-x-0 bottom-0 space-y-6 p-8 text-white md:p-16">
              <div className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-4 py-1.5 text-xs font-bold uppercase tracking-wider text-white/90 backdrop-blur-md">
                <FestivalArt
                  name={festival.name}
                  description={festival.description}
                  slug={festival.slug}
                  stateSlug={festival.stateSlug}
                  className="h-7 w-7 rounded-lg ring-1 ring-white/40"
                />
                {monthName} ·{" "}
                {festival.isPanIndia
                  ? "Pan-India"
                  : region
                    ? region.name
                    : "India"}
              </div>
              <h1 className="text-5xl font-bold leading-tight tracking-tight drop-shadow-sm md:text-7xl">
                {festival.name}
              </h1>
              <p className="max-w-2xl text-lg leading-relaxed text-white/90 md:text-xl">
                {festival.description}
              </p>
              {region && regionProducts.length > 0 && (
                <div className="flex flex-wrap gap-3 pt-2">
                  <Link
                    href={`/products?region=${region.slug}`}
                    className="btn-primary"
                  >
                    Shop {festival.name.split(" ")[0]} Collection
                  </Link>
                  <Link
                    href={`/region/${region.slug}`}
                    className="btn-ghost"
                  >
                    Explore {region.name}
                    <Icon name="arrow_forward" className="h-4 w-4" />
                  </Link>
                </div>
              )}
            </div>
          </div>
        </section>
      ) : (
        <section className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="relative flex flex-col items-center justify-between gap-8 overflow-hidden rounded-[2rem] bg-slate-950 p-8 text-white shadow-xl md:flex-row md:p-16">
            <div
              className="pointer-events-none absolute inset-0"
              style={{
                background:
                  "radial-gradient(60% 80% at 20% 20%, rgba(124,58,237,0.5) 0%, transparent 60%), radial-gradient(50% 70% at 80% 30%, rgba(236,72,153,0.4) 0%, transparent 60%)",
              }}
            />
            <div className="relative z-10 max-w-2xl space-y-6">
              <div className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-4 py-1.5 text-xs font-bold uppercase tracking-wider text-white/90 backdrop-blur-md">
                <FestivalArt
                  name={festival.name}
                  description={festival.description}
                  slug={festival.slug}
                  stateSlug={festival.stateSlug}
                  className="h-7 w-7 rounded-lg ring-1 ring-white/40"
                />
                {festival.category} · {monthName} ·{" "}
                {festival.isPanIndia ? "Pan-India" : region?.name ?? "India"}
              </div>
              <h1 className="text-5xl font-bold leading-tight tracking-tight drop-shadow-sm md:text-7xl">
                {festival.name}
              </h1>
              <p className="max-w-xl text-lg leading-relaxed text-white/90 md:text-xl">
                {festival.description}
              </p>
              {region && regionProducts.length > 0 && (
                <div className="flex flex-wrap gap-3 pt-2">
                  <Link
                    href={`/products?region=${region.slug}`}
                    className="btn-primary"
                  >
                    Shop {festival.name.split(" ")[0]} Collection
                  </Link>
                  <Link
                    href={`/region/${region.slug}`}
                    className="btn-ghost"
                  >
                    Explore {region.name}
                  </Link>
                </div>
              )}
            </div>
            <div className="relative z-10 hidden drop-shadow-lg md:block">
              <div className="rounded-2xl bg-white/95 p-4 shadow-2xl ring-4 ring-white/30">
                <FestivalArt
                  name={festival.name}
                  description={festival.description}
                  slug={festival.slug}
                  stateSlug={festival.stateSlug}
                  className="h-40 w-40 md:h-48 md:w-48"
                />
              </div>
            </div>
          </div>
        </section>
      )}

      {region && regionProducts.length > 0 && (
        <section className="mx-auto max-w-7xl space-y-8 px-4 py-16 sm:px-6 lg:px-8">
          <div>
            <p className="eyebrow-soft mb-3">Celebrate with {region.name}</p>
            <h2 className="text-3xl font-bold tracking-tight text-ink md:text-4xl">
              The {festival.name.split(" ")[0]} Collection
            </h2>
          </div>
          <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
            {regionProducts.slice(0, 4).map((p) => (
              <ProductCard key={p.id} product={p} />
            ))}
          </div>
        </section>
      )}

      {/* More this month */}
      <section className="mx-auto max-w-7xl px-4 pb-16 sm:px-6 lg:px-8">
        <div className="space-y-6">
          <div className="flex items-center justify-between border-b border-black/5 pb-4">
            <h3 className="text-2xl font-semibold text-ink">
              More festivals in {monthName}
            </h3>
            <div
              className="h-1.5 w-36 rounded-full bg-gradient-to-r from-violet-600 to-fuchsia-500"
              aria-hidden
            />
          </div>
          {sameMonth.length === 0 ? (
            <p className="text-ink-muted">No other festivals recorded this month.</p>
          ) : (
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {sameMonth.map((f) => (
                <FestivalCard key={f.slug} festival={f} compact />
              ))}
            </div>
          )}
        </div>
      </section>
    </main>
  );
}
