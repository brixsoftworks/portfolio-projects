import Link from "next/link";
import { notFound } from "next/navigation";
import {
  getProduct,
  getProductIds,
  relatedProducts,
  getRegion,
  getCategory,
} from "@/data/catalog";
import { discountPercent, formatINR } from "@/lib/format";
import { ProductCard } from "@/components/ProductCard";
import { BuyBox } from "@/components/BuyBox";
import { WishlistButton } from "@/components/WishlistButton";
import { Icon } from "@/components/icons";

export async function generateStaticParams() {
  const ids = await getProductIds();
  return ids.map((id) => ({ id }));
}

export const dynamicParams = false;

const HIGHLIGHT_ICONS = ["spa", "verified", "texture", "local_shipping", "auto_awesome"] as const;

export default async function ProductPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const product = await getProduct(id);
  if (!product) notFound();

  const off = discountPercent(product.price, product.mrp);
  const [region, category, related] = await Promise.all([
    getRegion(product.stateSlug),
    getCategory(product.category),
    relatedProducts(product),
  ]);

  return (
    <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      {/* Breadcrumb */}
      <nav className="mb-8 flex items-center gap-2 text-sm text-stone-500">
        <Link href="/" className="transition-colors hover:text-violet-700">Home</Link>
        <span className="text-stone-300">/</span>
        <Link href="/products" className="transition-colors hover:text-violet-700">Shop</Link>
        {category && (
          <>
            <span className="text-stone-300">/</span>
            <Link
              href={`/products?category=${category.slug}`}
              className="transition-colors hover:text-violet-700"
            >
              {category.name}
            </Link>
          </>
        )}
        <span className="text-stone-300">/</span>
        <span className="font-medium text-ink">{product.region}</span>
      </nav>

      {/* Product hero */}
      <div className="mb-16 grid grid-cols-1 gap-12 lg:grid-cols-2">
        {/* Image */}
        <div className="relative aspect-[4/5] w-full overflow-hidden rounded-2xl border border-stone-200/50 bg-gradient-to-br from-violet-50 to-fuchsia-50 p-4 shadow-sm">
          <div className="absolute left-6 top-6 z-10 flex flex-col gap-2">
            {off > 0 && (
              <span className="w-max rounded-full bg-gradient-to-r from-fuchsia-600 to-rose-500 px-3 py-1 text-xs font-bold uppercase tracking-wider text-white shadow-sm">
                {off}% OFF
              </span>
            )}
            <span className="w-max rounded-full border border-stone-200/50 bg-white/80 px-3 py-1 text-xs font-bold uppercase tracking-wider text-stone-800 shadow-sm backdrop-blur-md">
              {category?.name ?? product.category}
            </span>
          </div>
          <div className="absolute right-6 top-6 z-10">
            <WishlistButton
              id={product.id}
              className="flex h-11 w-11 items-center justify-center rounded-full border border-stone-200/50 bg-white/80 text-stone-600 shadow-sm backdrop-blur-md transition-all hover:bg-white hover:text-accent"
            />
          </div>
          <div className="relative h-full w-full overflow-hidden rounded-xl shadow-sm">
            <img
              src={product.image}
              alt={product.name}
              className="h-full w-full object-cover transition-transform duration-700 group-hover:scale-105"
            />
            <div className="absolute inset-x-0 bottom-0 h-1/3 bg-gradient-to-t from-black/60 to-transparent" />
            <div className="absolute bottom-6 left-6 right-6">
              <h2 className="text-2xl font-bold text-white">
                {product.name}
              </h2>
            </div>
          </div>
        </div>

        {/* Info */}
        <div className="flex flex-col pt-4">
          <span className="mb-3 text-xs font-bold uppercase tracking-[0.2em] text-violet-700">
            {region ? (
              <Link href={`/region/${region.slug}`} className="hover:underline">
                {product.region}
              </Link>
            ) : (
              product.region
            )}
          </span>
          <h1 className="mb-4 text-4xl font-bold leading-tight tracking-tight text-stone-900 lg:text-5xl">
            {product.name}
          </h1>
          <div className="mb-6 flex items-center gap-2">
            <div className="flex text-lg text-amber-400">
              {Array.from({ length: 5 }).map((_, i) => (
                <Icon
                  key={i}
                  name="star"
                  className={`h-5 w-5 ${i < Math.round(product.rating) ? "text-amber-400" : "text-stone-300"}`}
                />
              ))}
            </div>
            <span className="text-sm font-medium text-stone-500">
              {product.rating} · {product.reviews} reviews
            </span>
          </div>
          <p className="mb-8 text-lg leading-relaxed text-stone-600">
            {product.description}
          </p>

          {/* Price */}
          <div className="relative mb-8 overflow-hidden rounded-2xl border border-stone-200 bg-white p-6 shadow-sm">
            <div className="absolute -right-12 -top-12 h-32 w-32 rounded-full bg-orange-50 opacity-50 blur-2xl" />
            <div className="relative z-10 mb-2 flex items-baseline gap-4">
              <span className="text-4xl font-bold tracking-tight tabular-nums text-stone-900">
                {formatINR(product.price)}
              </span>
              {product.mrp > product.price && (
                <span className="text-lg tabular-nums text-stone-400 line-through">
                  {formatINR(product.mrp)}
                </span>
              )}
              {off > 0 && (
                <span className="rounded-md bg-green-50 px-2 py-1 text-sm font-bold text-success">
                  {off}% off
                </span>
              )}
            </div>
            <p className="relative z-10 text-sm text-stone-500">
              Inclusive of all taxes ·{" "}
              <span className="inline-flex items-center gap-1 font-medium text-success">
                <Icon name="local_shipping" className="h-4 w-4" /> Free shipping
              </span>
            </p>
          </div>

          {/* Actions */}
          <div className="mb-10">
            <BuyBox product={product} />
          </div>

          {/* Highlights */}
          <div className="rounded-2xl border border-stone-200 bg-white p-6 shadow-sm">
            <h3 className="mb-4 flex items-center gap-2 text-lg font-bold text-stone-900">
              <Icon name="auto_awesome" className="h-5 w-5 text-violet-600" />
              Product Highlights
            </h3>
            <ul className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              {product.tags.slice(0, 4).map((t, i) => (
                <li key={t} className="flex items-start gap-3">
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-violet-100 text-violet-700">
                    <Icon name={HIGHLIGHT_ICONS[i % HIGHLIGHT_ICONS.length]} className="h-4 w-4" />
                  </div>
                  <span className="mt-1.5 text-sm font-medium capitalize text-stone-700">
                    {t.replace(/-/g, " ")}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Related */}
      <section>
        <h2 className="mb-6 text-3xl font-bold tracking-tight text-ink">
          You may also like
        </h2>
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          {related.map((p) => (
            <ProductCard key={p.id} product={p} />
          ))}
        </div>
      </section>
    </main>
  );
}
