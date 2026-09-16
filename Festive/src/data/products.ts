import { REGIONS, type Region } from "./regions";

export interface Product {
  id: string;
  name: string;
  category: string;
  stateSlug: string;
  region: string;
  price: number;
  mrp: number;
  rating: number;
  reviews: number;
  image: string; // solid fallback color
  description: string;
  tags: string[];
  featured?: boolean;
  bestseller?: boolean;
}

type RegionName = (r: Region) => string;

interface ProductTemplate {
  category: string;
  name: RegionName;
  description: RegionName;
  basePrice: number;
  mrpDelta: number; // percent markup above price
  tags: string[];
}

// Deterministic PRNG so the catalog is stable between builds
function mulberry32(a: number) {
  return function () {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const TEMPLATES: ProductTemplate[] = [
  {
    category: "pooja",
    name: () => "Brass Aarti Thali Set",
    description: (r) => `Hand-finished brass aarti thali with diya, kumkum box and bells, made in ${r.name}.`,
    basePrice: 649,
    mrpDelta: 30,
    tags: ["brass", "aarti", "pooja"],
  },
  {
    category: "pooja",
    name: (r) => `Ashtamangala Diya ${r.name} Special`,
    description: (r) => `Traditional oil lamps handcrafted by artisans of ${r.name} for the evening aarti.`,
    basePrice: 399,
    mrpDelta: 25,
    tags: ["diya", "oil-lamp"],
  },
  {
    category: "pooja",
    name: () => "Agarwood Incense Gift Pack",
    description: (r) => `A pack of 6 premium agarwood incense cones, a ${r.name} temple-household staple.`,
    basePrice: 299,
    mrpDelta: 35,
    tags: ["incense", "agarwood", "dhoop"],
  },
  {
    category: "decor",
    name: () => "Rangoli Powder Combo (24 shades)",
    description: (r) => `Vibrant rangoli colours inspired by the ${r.name} palette, safe for indoor use.`,
    basePrice: 249,
    mrpDelta: 40,
    tags: ["rangoli", "holi", "decor"],
  },
  {
    category: "decor",
    name: (r) => `Festive Toran Door Hanger ${r.name}`,
    description: (r) => `Hand-embroidered toran crafted with traditional motifs of ${r.name}.`,
    basePrice: 349,
    mrpDelta: 30,
    tags: ["toran", "door-decor"],
  },
  {
    category: "decor",
    name: () => "Marigold Garland Bundle",
    description: (r) => `A bundle of 12 fresh-style marigold strands, strung the way they do at ${r.name} weddings.`,
    basePrice: 199,
    mrpDelta: 50,
    tags: ["marigold", "garland"],
  },
  {
    category: "sweets",
    name: () => "Assorted Mithai Gift Box",
    description: (r) => `A 12-piece box of traditional sweets, a festive classic across ${r.name}.`,
    basePrice: 499,
    mrpDelta: 25,
    tags: ["mithai", "sweets", "gift"],
  },
  {
    category: "sweets",
    name: () => "Dry Fruit Ladoo Jar",
    description: (r) => `Milk and dry-fruit ladoos in a reusable jar, popular during festivals in ${r.name}.`,
    basePrice: 549,
    mrpDelta: 20,
    tags: ["ladoo", "dry-fruit", "prasad"],
  },
  {
    category: "sweets",
    name: () => "Namkeen Farsan Hamper",
    description: (r) => `A mixed savouries hamper, the go-to tea-time snack of ${r.name} households.`,
    basePrice: 399,
    mrpDelta: 35,
    tags: ["namkeen", "snacks", "farsan"],
  },
  {
    category: "clothing",
    name: (r) => `Handloom Festive Kurti ${r.name}`,
    description: (r) => `A handwoven kurti featuring the signature weave of ${r.name}'s looms.`,
    basePrice: 899,
    mrpDelta: 22,
    tags: ["kurti", "handloom", "ethnic"],
  },
  {
    category: "clothing",
    name: (r) => `Saree in ${r.name} Classic Weave`,
    description: (r) => `An elegant saree with the timeless weaving tradition of ${r.name}.`,
    basePrice: 1499,
    mrpDelta: 20,
    tags: ["saree", "festive", "weave"],
  },
  {
    category: "clothing",
    name: () => "Men's Festive Kurta Set",
    description: (r) => `A comfortable cotton-blend kurta set, an everyday festive choice across ${r.name}.`,
    basePrice: 1299,
    mrpDelta: 18,
    tags: ["kurta", "men", "festive"],
  },
  {
    category: "gifts",
    name: () => "Puja Hampers for the Family",
    description: (r) => `A curated hamper of pooja essentials and sweets, the signature ${r.name} gifting style.`,
    basePrice: 1199,
    mrpDelta: 15,
    tags: ["hamper", "gift", "pooja"],
  },
  {
    category: "gifts",
    name: () => "Festive Greeting Card Set",
    description: (r) => `A set of 10 illustrated cards carrying the festivals celebrated in ${r.name}.`,
    basePrice: 149,
    mrpDelta: 60,
    tags: ["cards", "greetings"],
  },
  {
    category: "gifts",
    name: () => "Dry Fruit & Dates Gift Box",
    description: (r) => `A premium box of dry fruits and dates, a thoughtful gift across ${r.name}.`,
    basePrice: 799,
    mrpDelta: 25,
    tags: ["dry-fruit", "dates", "gift-box"],
  },
  {
    category: "handicrafts",
    name: (r) => `${r.name} Handcrafted Terracotta Set`,
    description: (r) => `Terracotta pieces shaped by the potters' community of ${r.name}.`,
    basePrice: 599,
    mrpDelta: 20,
    tags: ["terracotta", "handicraft"],
  },
  {
    category: "handicrafts",
    name: () => "Wall Hanging with Folk Art",
    description: (r) => `A canvas wall hanging inspired by the folk art tradition of ${r.name}.`,
    basePrice: 449,
    mrpDelta: 25,
    tags: ["folk-art", "wall-art"],
  },
  {
    category: "handicrafts",
    name: (r) => `Bamboo Weave Basket ${r.name}`,
    description: (r) => `A sturdy hand-woven bamboo basket from the craft clusters of ${r.name}.`,
    basePrice: 529,
    mrpDelta: 28,
    tags: ["bamboo", "basket", "handmade"],
  },
  {
    category: "jewellery",
    name: () => "Temple Jewellery Jhumka Set",
    description: (r) => `Gold-tone temple jhumkas echoing the designs worn in ${r.name}'s festive season.`,
    basePrice: 749,
    mrpDelta: 30,
    tags: ["jhumka", "temple", "earrings"],
  },
  {
    category: "jewellery",
    name: () => "Kundan Necklace Set",
    description: (r) => `A traditional kundan necklace set with earrings, loved across ${r.name}.`,
    basePrice: 999,
    mrpDelta: 20,
    tags: ["kundan", "necklace", "set"],
  },
  {
    category: "jewellery",
    name: () => "Feather & Bead Anklets",
    description: (r) => `Lightweight anklets inspired by the festive looks of ${r.name}.`,
    basePrice: 299,
    mrpDelta: 40,
    tags: ["anklets", "jewellery"],
  },
  {
    category: "home",
    name: () => "Festive Serveware Set",
    description: (r) => `A six-piece melamine serveware set in festive motifs from ${r.name}.`,
    basePrice: 899,
    mrpDelta: 22,
    tags: ["serveware", "home", "kitchen"],
  },
  {
    category: "home",
    name: () => "Copper Water Bottle",
    description: (r) => `A hammered copper bottle, a wellness staple in ${r.name} homes.`,
    basePrice: 699,
    mrpDelta: 30,
    tags: ["copper", "bottle", "wellness"],
  },
  {
    category: "home",
    name: () => "Clay Utensil Set",
    description: (r) => `Authentic clay pots and cups used in traditional ${r.name} cooking.`,
    basePrice: 599,
    mrpDelta: 25,
    tags: ["clay", "utensils", "traditional"],
  },
];

const FLAG_SHORTCUT: Record<string, string> = {
  "andaman-and-nicobar": "andaman",
  "dadra-nagar-haveli-daman-diu": "daman-diu",
};

function regionShort(r: Region) {
  return FLAG_SHORTCUT[r.slug] ?? r.slug.replace(/-/g, "");
}

const IMAGE_POOL: Record<string, string[]> = {
  pooja: [
    "/images/products/brass-peacock-diya.jpg",
    "/images/products/brass-kuber-diya.jpg",
    "/images/products/brass-diya-set.jpg",
    "/images/products/silver-pooja-thali.jpg",
    "/images/products/nilavilakku.jpg",
    "/images/products/brass-diya-up.jpg",
  ],
  decor: [
    "/images/products/terracotta-diyas.jpg",
    "/images/products/marigold-toran.jpg",
    "/images/products/wooden-chowki.jpg",
    "/images/products/nettipattam.jpg",
  ],
  sweets: [
    "/images/products/mithai-box.jpg",
    "/images/products/assorted-mithai.jpg",
    "/images/products/festive-mithai-box.jpg",
    "/images/products/banana-chips.jpg",
  ],
  clothing: [
    "/images/products/banarasi-saree.jpg",
    "/images/products/kanjeevaram-saree.jpg",
    "/images/products/kanchipuram-saree.jpg",
    "/images/products/kasavu-saree.jpg",
    "/images/products/kasavu-saree-detail.jpg",
    "/images/products/kasavu-saree-cart.jpg",
  ],
  handicrafts: [
    "/images/products/wooden-elephant.jpg",
    "/images/products/nettipattam.jpg",
    "/images/products/wooden-chowki.jpg",
    "/images/products/terracotta-diyas.jpg",
  ],
  gifts: [
    "/images/products/festive-mithai-box.jpg",
    "/images/products/assorted-mithai.jpg",
    "/images/products/mithai-box.jpg",
    "/images/products/wooden-elephant.jpg",
  ],
  jewellery: [
    "/images/products/brass-peacock-diya.jpg",
    "/images/products/brass-diya-set.jpg",
    "/images/products/nilavilakku.jpg",
  ],
  home: [
    "/images/products/wooden-chowki.jpg",
    "/images/products/nettipattam.jpg",
    "/images/products/terracotta-diyas.jpg",
    "/images/products/marigold-toran.jpg",
  ],
};

function poolImage(category: string, seed: number) {
  const pool = IMAGE_POOL[category] ?? IMAGE_POOL.decor;
  return pool[seed % pool.length];
}

// Curated signature products rendered with the AI-generated product imagery.
const SIGNATURE: Product[] = [
  { id: "sig_brass_peacock_diya", name: "Handcrafted Brass Peacock Diya", category: "pooja", stateSlug: "rajasthan", region: "Rajasthan", price: 850, mrp: 1000, rating: 4.8, reviews: 124, image: "/images/products/brass-peacock-diya.jpg", description: "A handcrafted brass oil diya, intricately detailed with a peacock motif, glowing over a colourful rangoli during Diwali.", tags: ["brass", "diya", "peacock"], bestseller: true },
  { id: "sig_mithai_box", name: "Premium Assorted Mithai Box (1kg)", category: "sweets", stateSlug: "delhi", region: "Delhi", price: 1200, mrp: 1500, rating: 4.7, reviews: 89, image: "/images/products/mithai-box.jpg", description: "A box of premium assorted mithai including kaju katli and ladoos, beautifully arranged in a decorative gifting box.", tags: ["mithai", "sweets", "gift"], bestseller: true },
  { id: "sig_banarasi_saree", name: "Classic Maroon Banarasi Silk Saree", category: "clothing", stateSlug: "uttar-pradesh", region: "Uttar Pradesh", price: 4500, mrp: 6500, rating: 4.9, reviews: 45, image: "/images/products/banarasi-saree.jpg", description: "An elegant Banarasi silk saree in rich maroon with gold zari work, crafted on the looms of Varanasi.", tags: ["saree", "banarasi", "silk"], bestseller: true },
  { id: "sig_terracotta_diyas", name: "Painted Terracotta Diya Set (12 Pcs)", category: "decor", stateSlug: "gujarat", region: "Gujarat", price: 350, mrp: 450, rating: 4.6, reviews: 210, image: "/images/products/terracotta-diyas.jpg", description: "Painted terracotta clay diyas with vibrant colours and mirror work, arranged for a warm festive glow.", tags: ["terracotta", "diya", "decor"], bestseller: true },
  { id: "sig_marigold_toran", name: "Marigold & Bell Door Toran (3ft)", category: "decor", stateSlug: "delhi", region: "Delhi", price: 550, mrp: 700, rating: 4.9, reviews: 342, image: "/images/products/marigold-toran.jpg", description: "A decorative marigold toran with small brass bells, strung the festive way for every doorway.", tags: ["toran", "marigold", "door-decor"], bestseller: true },
  { id: "sig_silver_thali", name: "Pure Silver Plated Pooja Thali Set", category: "pooja", stateSlug: "maharashtra", region: "Maharashtra", price: 2100, mrp: 2500, rating: 5.0, reviews: 67, image: "/images/products/silver-pooja-thali.jpg", description: "A silver puja thali set with bowls for kumkum, a bell and an agarbatti stand, reflecting luxury and purity.", tags: ["thali", "silver", "pooja"], bestseller: true },
  { id: "sig_brass_kuber_diya", name: "Traditional Brass Kuber Diya Set of 2", category: "pooja", stateSlug: "maharashtra", region: "Maharashtra", price: 699, mrp: 899, rating: 4.7, reviews: 965, image: "/images/products/brass-kuber-diya.jpg", description: "A pair of traditional brass Kuber diyas, polished to a golden shine for the evening aarti.", tags: ["diya", "brass", "kuber"], bestseller: true },
  { id: "sig_kanjeevaram", name: "Kanjeevaram Silk Saree — Magenta Glow", category: "clothing", stateSlug: "tamil-nadu", region: "Tamil Nadu", price: 3999, mrp: 4999, rating: 4.9, reviews: 412, image: "/images/products/kanjeevaram-saree.jpg", description: "A luxurious Kanjeevaram silk saree in magenta with a shimmering gold zari border.", tags: ["saree", "kanjeevaram", "silk"], bestseller: true },
  { id: "sig_assorted_mithai", name: "Assorted Mithai Gift Box (18 pc)", category: "sweets", stateSlug: "west-bengal", region: "West Bengal", price: 749, mrp: 999, rating: 4.8, reviews: 1504, image: "/images/products/assorted-mithai.jpg", description: "An 18-piece gift box of assorted traditional sweets — a festive classic across Bengal and beyond.", tags: ["mithai", "sweets", "gift"], bestseller: true },
  { id: "sig_wooden_elephant", name: "Handcrafted Wooden Painted Elephant", category: "handicrafts", stateSlug: "karnataka", region: "Karnataka", price: 549, mrp: 699, rating: 4.7, reviews: 233, image: "/images/products/wooden-elephant.jpg", description: "A handcrafted wooden painted elephant, a symbol of auspiciousness from Mysore's craft clusters.", tags: ["elephant", "wooden", "handicraft"], bestseller: true },
  { id: "sig_brass_diya_set", name: "Handcrafted Brass Diya Set with Intricate Etching", category: "pooja", stateSlug: "uttar-pradesh", region: "Uttar Pradesh", price: 599, mrp: 799, rating: 4.8, reviews: 1052, image: "/images/products/brass-diya-set.jpg", description: "A brass diya set with intricate etching, polished and ready for the festival of lights.", tags: ["diya", "brass", "pooja"], bestseller: true },
  { id: "sig_kanchipuram", name: "Pure Silk Kanchipuram Saree with Gold Zari Border", category: "clothing", stateSlug: "tamil-nadu", region: "Tamil Nadu", price: 4499, mrp: 5599, rating: 4.9, reviews: 728, image: "/images/products/kanchipuram-saree.jpg", description: "A pure silk Kanchipuram saree with a bold gold zari border, handwoven by master weavers.", tags: ["saree", "kanchipuram", "silk"], bestseller: true },
  { id: "sig_wooden_chowki", name: "Meenakari Art Wooden Chowki Stool", category: "decor", stateSlug: "rajasthan", region: "Rajasthan", price: 899, mrp: 1199, rating: 4.6, reviews: 187, image: "/images/products/wooden-chowki.jpg", description: "A hand-painted meenakari wooden chowki stool, a heritage accent piece from Rajasthan.", tags: ["chowki", "meenakari", "wooden"], bestseller: true },
  { id: "sig_festive_mithai", name: "Festive Mithai Gift Box", category: "sweets", stateSlug: "delhi", region: "Delhi", price: 699, mrp: 899, rating: 4.7, reviews: 654, image: "/images/products/festive-mithai-box.jpg", description: "A beautifully packed festive mithai gift box, perfect for sharing the season's sweetness.", tags: ["mithai", "gift-box", "sweets"], bestseller: true },
  { id: "sig_banana_chips", name: "Authentic Nendran Banana Chips Combo Pack", category: "sweets", stateSlug: "kerala", region: "Kerala", price: 450, mrp: 600, rating: 4.6, reviews: 89, image: "/images/products/banana-chips.jpg", description: "Golden thin-sliced nendran banana chips with jaggery-coated sharkara varatti in eco-friendly packaging.", tags: ["banana-chips", "kerala", "snacks"], bestseller: true },
  { id: "sig_nettipattam", name: "Nettipattam Miniature Wall Hanging Decor", category: "decor", stateSlug: "kerala", region: "Kerala", price: 1850, mrp: 1850, rating: 5.0, reviews: 42, image: "/images/products/nettipattam.jpg", description: "A detailed Nettipattam — the traditional elephant caparison — repurposed as an ornate wall hanging.", tags: ["nettipattam", "wall-art", "kerala"], bestseller: true },
  { id: "sig_nilavilakku", name: "Traditional Brass Nilavilakku Lamp", category: "pooja", stateSlug: "kerala", region: "Kerala", price: 1250, mrp: 1499, rating: 4.9, reviews: 315, image: "/images/products/nilavilakku.jpg", description: "A tall traditional South Indian brass nilavilakku, glowing softly beside every festive Kerala home.", tags: ["nilavilakku", "brass", "lamp"], bestseller: true },
  { id: "sig_kasavu_saree", name: "Hand-loomed Kasavu Saree with Gold Border", category: "clothing", stateSlug: "kerala", region: "Kerala", price: 4250, mrp: 5000, rating: 4.6, reviews: 234, image: "/images/products/kasavu-saree-detail.jpg", description: "A traditional off-white cotton kasavu saree with a striking golden zari border, handcrafted in Balaramapuram.", tags: ["kasavu", "saree", "kerala"], bestseller: true },
  { id: "sig_brass_diya_up", name: "Ornate Brass Diya with Carvings", category: "pooja", stateSlug: "uttar-pradesh", region: "Uttar Pradesh", price: 449, mrp: 599, rating: 4.7, reviews: 156, image: "/images/products/brass-diya-up.jpg", description: "An ornate brass diya polished to a golden shine, carved by the metal artisans of Uttar Pradesh.", tags: ["diya", "brass", "pooja"], bestseller: true },
  { id: "sig_kasavu_cart", name: "Hand-loomed Kasavu Saree (Kerala Classic)", category: "clothing", stateSlug: "kerala", region: "Kerala", price: 3999, mrp: 4999, rating: 4.6, reviews: 312, image: "/images/products/kasavu-saree-cart.jpg", description: "A crisp off-white cotton kasavu saree with traditional gold zari borders, elegant for Onam and Vishu.", tags: ["kasavu", "saree", "kerala"], bestseller: true },
];

export const PRODUCTS: Product[] = [...SIGNATURE, ...REGIONS.flatMap((region) => {
  const rng = mulberry32(region.slug.length * 997 + region.name.length * 31);
  return TEMPLATES.map((tpl, i) => {
    const price = Math.round((tpl.basePrice * (0.85 + rng() * 0.3)) / 10) * 10;
    const mrp = Math.round((price * (1 + tpl.mrpDelta / 100)) / 10) * 10;
    const rating = Math.round((3.7 + rng() * 1.2) * 10) / 10;
    const reviews = Math.floor(12 + rng() * 900);
    const short = regionShort(region);
    const slugBase = tpl.name(region).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");
    return {
      id: `prd_${short}_${i}_${slugBase.slice(0, 24)}`,
      name: tpl.name(region),
      category: tpl.category,
      stateSlug: region.slug,
      region: region.name,
      price,
      mrp,
      rating,
      reviews,
      image: poolImage(tpl.category, region.slug.length + i * 7),
      description: tpl.description(region),
      tags: tpl.tags,
    };
  });
})];

export function getProduct(id: string) {
  return PRODUCTS.find((p) => p.id === id);
}

export function productsByRegion(stateSlug: string) {
  return PRODUCTS.filter((p) => p.stateSlug === stateSlug);
}

export function productsByCategory(category: string) {
  return PRODUCTS.filter((p) => p.category === category);
}

export function featuredProducts() {
  return SIGNATURE.slice(0, 6);
}

export function bestsellerProducts() {
  return SIGNATURE;
}

export function relatedProducts(product: Product, limit = 4) {
  const sameCat = PRODUCTS.filter(
    (p) => p.category === product.category && p.id !== product.id
  );
  const sameRegion = PRODUCTS.filter(
    (p) => p.stateSlug === product.stateSlug && p.id !== product.id
  );
  return [...sameRegion, ...sameCat].slice(0, limit);
}

export function searchProducts(query: string) {
  const q = query.toLowerCase().trim();
  if (!q) return [];
  return PRODUCTS.filter(
    (p) =>
      p.name.toLowerCase().includes(q) ||
      p.description.toLowerCase().includes(q) ||
      p.tags.some((t) => t.includes(q)) ||
      p.region.toLowerCase().includes(q)
  ).slice(0, 30);
}
