import Link from "next/link";
import { searchProducts } from "@/data/catalog";
import { ProductCard } from "@/components/ProductCard";
import { Icon } from "@/components/icons";

export const metadata = { title: "Search — The Divine Things" };

export default async function SearchPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>;
}) {
  const { q } = await searchParams;
  const query = typeof q === "string" ? q : "";
  const results = await searchProducts(query);

  return (
    <div className="mx-auto w-full max-w-7xl px-4 py-8 md:px-6 md:py-12">
      <div className="mb-8 border-b border-black/5 pb-4">
        <h1 className="text-3xl font-bold tracking-tight text-ink md:text-4xl">
          {query ? `Results for “${query}”` : "Search Products"}
        </h1>
        <p className="mt-1 text-sm text-ink-muted">
          {query
            ? `${results.length} ${results.length === 1 ? "product" : "products"} found`
            : "Type a search above to find products."}
        </p>
      </div>

      {query && results.length === 0 && (
        <div className="flex flex-col items-center rounded-2xl border border-stone-200 bg-white p-12 text-center">
          <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-violet-100">
            <Icon name="search" className="h-8 w-8 text-violet-500/60" />
          </div>
          <p className="text-ink-muted">No products match “{query}”.</p>
          <Link
            href="/products"
            className="mt-4 inline-block text-sm font-semibold text-violet-700 hover:underline"
          >
            Browse all products
          </Link>
        </div>
      )}

      {results.length > 0 && (
        <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4 lg:gap-6">
          {results.map((p) => (
            <ProductCard key={p.id} product={p} />
          ))}
        </div>
      )}
    </div>
  );
}
