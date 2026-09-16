export interface Category {
  slug: string;
  name: string;
  emoji: string;
  description: string;
  color: string; // tailwind-safe background hex for placeholders
}

export const CATEGORIES: Category[] = [
  { slug: "pooja", name: "Pooja Essentials", emoji: "🪔", description: "Idols, diyas, incense and everything for worship.", color: "#f97316" },
  { slug: "decor", name: "Home Decor", emoji: "🏺", description: "Rangoli, torans, lanterns and festive decor.", color: "#e11d48" },
  { slug: "sweets", name: "Sweets & Snacks", emoji: "🍬", description: "Traditional mithai, savouries and gift hampers.", color: "#d97706" },
  { slug: "clothing", name: "Ethnic Wear", emoji: "🥻", description: "Kurtas, sarees, lehengas and festive fashion.", color: "#7c3aed" },
  { slug: "gifts", name: "Gifts & Hampers", emoji: "🎁", description: "Thoughtful gift boxes for family and friends.", color: "#0d9488" },
  { slug: "handicrafts", name: "Handicrafts", emoji: "🧶", description: "Handmade crafts by Indian artisans.", color: "#b45309" },
  { slug: "jewellery", name: "Festive Jewellery", emoji: "📿", description: "Temple jewellery, jhumkas and festive sets.", color: "#ca8a04" },
  { slug: "home", name: "Home & Kitchen", emoji: "🍳", description: "Dinner sets, serveware and festive cookware.", color: "#2563eb" },
];

export function getCategory(slug: string) {
  return CATEGORIES.find((c) => c.slug === slug);
}
