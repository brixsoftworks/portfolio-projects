import { db } from "@/lib/firebase";
import { collection, getDocs, query, where, orderBy } from "firebase/firestore";
import type { Category } from "./categories";
import type { Region } from "./regions";
import type { Festival } from "./festivals";
import type { Product } from "./products";

import { CATEGORIES as LOCAL_CATEGORIES } from "./categories";
import { REGIONS as LOCAL_REGIONS } from "./regions";
import { FESTIVALS as LOCAL_FESTIVALS } from "./festivals";
import { PRODUCTS as LOCAL_PRODUCTS } from "./products";

export { MONTH_NAMES, FESTIVAL_CATEGORIES } from "./festivals";

const cache = new Map<string, Promise<unknown>>();

function cached<T>(key: string, fn: () => Promise<T>): Promise<T> {
  if (!cache.has(key)) {
    cache.set(
      key,
      fn().catch((e) => {
        cache.delete(key);
        throw e;
      })
    );
  }
  return cache.get(key) as Promise<T>;
}

interface CategoryRow {
  slug: string;
  name: string;
  emoji: string;
  description: string;
  color: string;
}

function toCategory(r: CategoryRow): Category {
  return {
    slug: r.slug,
    name: r.name,
    emoji: r.emoji,
    description: r.description,
    color: r.color,
  };
}

interface RegionRow {
  slug: string;
  name: string;
  type: Region["type"];
  capital: string;
  region: Region["region"];
  description: string;
  emoji: string;
}

function toRegion(r: RegionRow): Region {
  return {
    slug: r.slug,
    name: r.name,
    type: r.type,
    capital: r.capital,
    region: r.region,
    description: r.description,
    emoji: r.emoji,
  };
}

interface FestivalRow {
  slug: string;
  name: string;
  state_slug: string | null;
  month: number;
  category: Festival["category"];
  emoji: string;
  description: string;
  is_pan_india: boolean;
}

function toFestival(r: FestivalRow): Festival {
  return {
    slug: r.slug,
    name: r.name,
    stateSlug: r.state_slug,
    month: r.month,
    category: r.category,
    emoji: r.emoji,
    description: r.description,
    isPanIndia: r.is_pan_india,
  };
}

interface ProductRow {
  id: string;
  name: string;
  category: string;
  state_slug: string;
  region: string;
  price: number;
  mrp: number;
  rating: number | string;
  reviews: number;
  image: string;
  description: string;
  tags: string[];
  bestseller: boolean;
}

function toProduct(r: ProductRow): Product {
  return {
    id: r.id,
    name: r.name,
    category: r.category,
    stateSlug: r.state_slug,
    region: r.region,
    price: r.price,
    mrp: r.mrp,
    rating: Number(r.rating),
    reviews: r.reviews,
    image: r.image,
    description: r.description,
    tags: r.tags ?? [],
    bestseller: r.bestseller,
  };
}

export async function getCategories(): Promise<Category[]> {
  return cached("categories", async () => {
    try {
      const q = query(collection(db, "categories"), orderBy("name"));
      const snapshot = await getDocs(q);
      const data = snapshot.docs.map((doc) => doc.data() as CategoryRow);
      return data.map(toCategory);
    } catch (e) {
      console.warn("Firebase fetch failed, falling back to local categories:", e);
      return LOCAL_CATEGORIES;
    }
  });
}

export async function getCategory(slug: string): Promise<Category | null> {
  const categories = await getCategories();
  return categories.find((c) => c.slug === slug) ?? null;
}

export async function getRegions(): Promise<Region[]> {
  return cached("regions", async () => {
    try {
      const q = query(collection(db, "regions"), orderBy("name"));
      const snapshot = await getDocs(q);
      const data = snapshot.docs.map((doc) => doc.data() as RegionRow);
      return data.map(toRegion);
    } catch (e) {
      console.warn("Firebase fetch failed, falling back to local regions:", e);
      return LOCAL_REGIONS;
    }
  });
}

export async function getRegion(slug: string): Promise<Region | null> {
  const regions = await getRegions();
  return regions.find((r) => r.slug === slug) ?? null;
}

export async function getStates(): Promise<Region[]> {
  const regions = await getRegions();
  return regions.filter((r) => r.type === "State");
}

export async function getUnionTerritories(): Promise<Region[]> {
  const regions = await getRegions();
  return regions.filter((r) => r.type === "Union Territory");
}

export async function getFestivals(): Promise<Festival[]> {
  return cached("festivals", async () => {
    try {
      const q = query(
        collection(db, "festivals"),
        where("is_pan_india", "==", true),
        orderBy("month")
      );
      const snapshot = await getDocs(q);
      const data = snapshot.docs.map((doc) => doc.data() as FestivalRow);
      return data.map(toFestival);
    } catch (e) {
      console.warn("Firebase fetch failed, falling back to local festivals:", e);
      return LOCAL_FESTIVALS;
    }
  });
}

export async function getFestival(slug: string): Promise<Festival | null> {
  const festivals = await getFestivals();
  return festivals.find((f) => f.slug === slug) ?? null;
}

export async function festivalsByMonth(month: number): Promise<Festival[]> {
  const festivals = await getFestivals();
  return festivals.filter((f) => f.month === month);
}

export async function getUpcomingFestivals(
  month: number,
  limit = 4
): Promise<Festival[]> {
  const panIndia = await getFestivals();
  const upcoming = [...panIndia.filter((f) => f.month >= month), ...panIndia.filter((f) => f.month < month)];
  return upcoming.slice(0, limit);
}

export async function getProducts(): Promise<Product[]> {
  return cached("products", async () => {
    try {
      const q = query(collection(db, "products"), orderBy("name"));
      const snapshot = await getDocs(q);
      const data = snapshot.docs.map((doc) => doc.data() as ProductRow);
      return data.map(toProduct);
    } catch (e) {
      console.warn("Firebase fetch failed, falling back to local products:", e);
      return LOCAL_PRODUCTS;
    }
  });
}

export async function getProduct(id: string): Promise<Product | null> {
  const products = await getProducts();
  return products.find((p) => p.id === id) ?? null;
}

export async function getProductsByIds(ids: string[]): Promise<Product[]> {
  if (ids.length === 0) return [];
  try {
    const chunks = [];
    for (let i = 0; i < ids.length; i += 10) {
      chunks.push(ids.slice(i, i + 10));
    }
    const data: ProductRow[] = [];
    for (const chunk of chunks) {
      const q = query(collection(db, "products"), where("id", "in", chunk));
      const snapshot = await getDocs(q);
      data.push(...snapshot.docs.map((doc) => doc.data() as ProductRow));
    }
    const byId = new Map(data.map((r) => [r.id, toProduct(r)]));
    return ids.map((id) => byId.get(id)).filter((p): p is Product => Boolean(p));
  } catch (e) {
    console.warn("Firebase fetch failed for ids, falling back to local products:", e);
    const byId = new Map(LOCAL_PRODUCTS.map((p) => [p.id, p]));
    return ids.map((id) => byId.get(id)).filter((p): p is Product => Boolean(p));
  }
}

export async function productsByRegion(stateSlug: string): Promise<Product[]> {
  const products = await getProducts();
  return products.filter((p) => p.stateSlug === stateSlug);
}

export async function productsByCategory(category: string): Promise<Product[]> {
  const products = await getProducts();
  return products.filter((p) => p.category === category);
}

export async function featuredProducts(limit = 6): Promise<Product[]> {
  const products = await getProducts();
  return products.filter((p) => p.bestseller).slice(0, limit);
}

export async function bestsellerProducts(): Promise<Product[]> {
  const products = await getProducts();
  return products.filter((p) => p.bestseller);
}

export async function relatedProducts(
  product: Product,
  limit = 4
): Promise<Product[]> {
  const products = await getProducts();
  const sameRegion = products.filter(
    (p) => p.stateSlug === product.stateSlug && p.id !== product.id
  );
  const sameCat = products.filter(
    (p) => p.category === product.category && p.id !== product.id
  );
  return [...sameRegion, ...sameCat].slice(0, limit);
}

export async function searchProducts(query: string, limit = 30): Promise<Product[]> {
  const q = query.toLowerCase().trim();
  if (!q) return [];
  const products = await getProducts();
  return products
    .filter(
      (p) =>
        p.name.toLowerCase().includes(q) ||
        p.description.toLowerCase().includes(q) ||
        p.tags.some((t) => t.includes(q)) ||
        p.region.toLowerCase().includes(q)
    )
    .slice(0, limit);
}

export async function getRegionStats(): Promise<
  Record<string, { festivals: number; products: number }>
> {
  return cached("region-stats", async () => {
    const [festivals, products] = await Promise.all([getFestivals(), getProducts()]);
    const stats: Record<string, { festivals: number; products: number }> = {};
    for (const f of festivals) {
      if (f.stateSlug) {
        (stats[f.stateSlug] ??= { festivals: 0, products: 0 }).festivals += 1;
      }
    }
    for (const p of products) {
      (stats[p.stateSlug] ??= { festivals: 0, products: 0 }).products += 1;
    }
    return stats;
  });
}

export async function getProductIds(): Promise<string[]> {
  const products = await getProducts();
  return products.map((p) => p.id);
}

export async function getRegionSlugs(): Promise<string[]> {
  const regions = await getRegions();
  return regions.map((r) => r.slug);
}

export async function getFestivalSlugs(): Promise<string[]> {
  const festivals = await getFestivals();
  return festivals.map((f) => f.slug);
}
