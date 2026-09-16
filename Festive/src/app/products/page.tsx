import Link from "next/link";
import {
  getCategories,
  getRegions,
  getProducts,
} from "@/data/catalog";
import { ProductCard } from "@/components/ProductCard";
import { SortSelect } from "@/components/SortSelect";
import { Icon } from "@/components/icons";

export default async function ProductsPage({
  searchParams,
}: {
  searchParams: Promise<{ category?: string; region?: string; sort?: string }>;
}) {
  const { category, region, sort } = await searchParams;
  const cat = typeof category === "string" ? category : "";
  const reg = typeof region === "string" ? region : "";
  const sortKey = typeof sort === "string" ? sort : "featured";

  const [categories, regions, allProducts] = await Promise.all([
    getCategories(),
    getRegions(),
    getProducts(),
  ]);

  let products = [...allProducts];
  if (cat) products = products.filter((p) => p.category === cat);
  if (reg) products = products.filter((p) => p.stateSlug === reg);

  switch (sortKey) {
    case "price-asc":
      products.sort((a, b) => a.price - b.price);
      break;
    case "price-desc":
      products.sort((a, b) => b.price - a.price);
      break;
    case "rating":
      products.sort((a, b) => b.rating - a.rating);
      break;
    default:
      products.sort((a, b) => Number(b.bestseller ?? false) - Number(a.bestseller ?? false));
  }

  const activeCategory = categories.find((c) => c.slug === cat);
  const activeRegion = regions.find((r) => r.slug === reg);

  return (
    <main className="mx-auto w-full max-w-7xl flex-grow px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="mb-2 text-4xl font-bold tracking-tight text-ink lg:text-5xl">
          {activeCategory?.name ?? activeRegion?.name ?? "All Products"}
        </h1>
        <p className="text-lg text-ink-muted">
          {products.length} products across every state and union territory
        </p>
      </div>

      <div className="flex flex-col gap-8 lg:flex-row">
        {/* Sidebar */}
        <aside className="w-full shrink-0 lg:w-[220px]">
          <div className="sticky top-[100px]">
            <div className="mb-8">
              <h3 className="mb-4 text-xs font-bold uppercase tracking-widest text-ink-muted">
                Categories
              </h3>
              <ul className="space-y-1">
                <li>
                  <Link
                    href="/products"
                    className={`block rounded-lg px-3 py-2 transition-colors ${!cat ? "bg-violet-100 font-medium text-violet-700" : "text-ink hover:bg-stone-100"}`}
                  >
                    All
                  </Link>
                </li>
                {categories.map((c) => (
                  <li key={c.slug}>
                    <Link
                      href={`/products?category=${c.slug}${reg ? `&region=${reg}` : ""}`}
                      className={`block rounded-lg px-3 py-2 transition-colors ${cat === c.slug ? "bg-violet-100 font-medium text-violet-700" : "text-ink hover:bg-stone-100"}`}
                    >
                      {c.name}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h3 className="mb-4 text-xs font-bold uppercase tracking-widest text-ink-muted">
                Regions
              </h3>
              <div className="max-h-[300px] space-y-1 overflow-y-auto pr-2">
                <Link
                  href="/products"
                  className="flex items-center gap-2 rounded-lg p-2 transition-colors hover:bg-stone-100"
                >
                  <span
                    className={`flex h-4 w-4 shrink-0 items-center justify-center rounded border ${
                      !reg
                        ? "border-violet-600 bg-violet-600 text-white"
                        : "border-stone-300 bg-white"
                    }`}
                  >
                    {!reg && <Icon name="check" className="h-3 w-3" />}
                  </span>
                  <span className="text-sm text-ink">All India</span>
                </Link>
                {regions.map((r) => (
                  <Link
                    key={r.slug}
                    href={`/products?region=${r.slug}${cat ? `&category=${cat}` : ""}`}
                    className="flex items-center gap-2 rounded-lg p-2 transition-colors hover:bg-stone-100"
                  >
                    <span
                      className={`flex h-4 w-4 shrink-0 items-center justify-center rounded border ${
                        reg === r.slug
                          ? "border-violet-600 bg-violet-600 text-white"
                          : "border-stone-300 bg-white"
                      }`}
                    >
                      {reg === r.slug && <Icon name="check" className="h-3 w-3" />}
                    </span>
                    <span className="text-sm text-ink">{r.name}</span>
                  </Link>
                ))}
              </div>
            </div>
          </div>
        </aside>

        {/* Grid */}
        <div className="flex-1">
          <div className="mb-6 flex items-center justify-between">
            <span className="text-sm text-ink-muted">
              {products.length} {products.length === 1 ? "product" : "products"}
            </span>
            <SortSelect current={sortKey} />
          </div>

          {products.length === 0 ? (
            <div className="rounded-2xl border border-stone-200 bg-white p-12 text-center text-ink-muted">
              No products found for this selection.
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-4 lg:gap-6">
              {products.map((p) => (
                <ProductCard key={p.id} product={p} />
              ))}
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
