import Link from "next/link";
import { notFound } from "next/navigation";
import {
  getRegion,
  getRegionSlugs,
  productsByRegion,
} from "@/data/catalog";
import { ProductCard } from "@/components/ProductCard";
import { RegionArt } from "@/components/artwork";
import { Icon } from "@/components/icons";

export async function generateStaticParams() {
  const slugs = await getRegionSlugs();
  return slugs.map((slug) => ({ slug }));
}

export const dynamicParams = false;

export default async function RegionPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const region = await getRegion(slug);
  if (!region) notFound();

  const products = await productsByRegion(region.slug);

  return (
    <main className="mx-auto max-w-7xl flex-grow px-4 py-8 sm:px-6 lg:px-8">
      {/* Breadcrumb */}
      <nav className="mb-6 flex items-center gap-2 text-sm text-ink-muted">
        <Link href="/" className="transition-colors hover:text-violet-700">Home</Link>
        <Icon name="arrow_forward" className="h-3.5 w-3.5 rotate-180 text-stone-300" />
        <Link href="/regions" className="transition-colors hover:text-violet-700">Regions</Link>
        <Icon name="arrow_forward" className="h-3.5 w-3.5 rotate-180 text-stone-300" />
        <span className="font-medium text-ink">{region.name}</span>
      </nav>

      {/* Hero */}
      <section className="relative flex flex-col items-center justify-between gap-8 overflow-hidden rounded-[2rem] bg-slate-950 p-8 text-white shadow-xl md:flex-row md:p-16">
        <div
          className="pointer-events-none absolute inset-0"
          style={{
            background:
              "radial-gradient(60% 80% at 20% 20%, rgba(124,58,237,0.5) 0%, transparent 60%), radial-gradient(50% 70% at 80% 30%, rgba(236,72,153,0.4) 0%, transparent 60%)",
          }}
        />
        <div className="relative z-10 max-w-2xl space-y-6">
          <div className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-4 py-1.5 text-xs font-bold uppercase tracking-wider text-white/90 backdrop-blur-md">
            <RegionArt
              name={region.name}
              slug={region.slug}
              regionGroup={region.region}
              className="h-7 w-7 rounded-lg ring-1 ring-white/40"
            />
            {region.type} · Capital {region.capital}
          </div>
          <h1 className="text-5xl font-bold leading-tight tracking-tight drop-shadow-sm md:text-7xl">
            {region.name}
          </h1>
          <p className="max-w-xl text-lg leading-relaxed text-white/90 md:text-xl">
            {region.description}
          </p>
          <div className="flex flex-wrap gap-4 pt-4">
            <div className="flex items-center gap-3 rounded-xl border border-white/20 bg-white/10 px-6 py-3 backdrop-blur-md">
              <Icon name="auto_awesome" className="h-6 w-6" />
              <span className="font-medium">{products.length} Products</span>
            </div>
          </div>
        </div>
        <div className="relative z-10 hidden drop-shadow-lg md:block">
          <div className="rounded-2xl bg-white/95 p-4 shadow-2xl ring-4 ring-white/30">
            <RegionArt
              name={region.name}
              slug={region.slug}
              regionGroup={region.region}
              className="h-40 w-40 md:h-48 md:w-48"
            />
          </div>
        </div>
      </section>

      {/* Products */}
      <section className="mt-12">
        <div className="mb-6 flex items-end justify-between">
          <div>
            <p className="eyebrow-soft mb-3">Shop the region</p>
            <h2 className="text-3xl font-bold tracking-tight text-ink md:text-4xl">
              {region.name} Collection
            </h2>
          </div>
          <Link
            href={`/products?region=${region.slug}`}
            className="group flex items-center gap-1 font-bold text-violet-700 transition-colors hover:text-violet-900"
          >
            View all
            <Icon name="arrow_forward" className="h-4 w-4 transition-transform group-hover:translate-x-1" />
          </Link>
        </div>
        {products.length === 0 ? (
          <p className="text-ink-muted">Products coming soon for this region.</p>
        ) : (
          <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
            {products.slice(0, 8).map((p) => (
              <ProductCard key={p.id} product={p} />
            ))}
          </div>
        )}
      </section>
    </main>
  );
}
