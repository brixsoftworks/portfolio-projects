export interface Festival {
  slug: string;
  name: string;
  stateSlug: string | null; // null => celebrated pan-India
  month: number; // 1-12
  category:
    | "Religious"
    | "Harvest"
    | "Cultural"
    | "Dance & Music"
    | "Fairs & Mela"
    | "Tribal"
    | "Food"
    | "National";
  emoji: string;
  description: string;
  isPanIndia?: boolean;
}

const M = (name: string, stateSlug: string | null, month: number, category: Festival["category"], emoji: string, description: string): Festival => ({
  slug: name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, ""),
  name,
  stateSlug,
  month,
  category,
  emoji,
  description,
  isPanIndia: stateSlug === null,
});

export const PAN_INDIA_FESTIVALS: Festival[] = [
  M("Diwali", null, 10, "Religious", "🪔", "The festival of lights — diyas, rangoli, sweets and fireworks across every home in India."),
  M("Holi", null, 3, "Religious", "🎨", "The festival of colours that paints the whole country in joy and gulal."),
  M("Navratri", null, 10, "Religious", "🥁", "Nine nights of devotion to Goddess Durga, with garba, dandiya and fasting."),
  M("Durga Puja", null, 10, "Religious", "🪔", "The worship of Goddess Durga with elaborate pandals, dhunuchi dance and bhog."),
  M("Dussehra / Vijayadashami", null, 10, "Religious", "🏹", "Victory of good over evil, marked by effigy burning and Ravana dahan."),
  M("Makar Sankranti", null, 1, "Harvest", "🪁", "The harvest festival of kites, til-gul sweets and sacred river dips."),
  M("Raksha Bandhan", null, 8, "Religious", "🧵", "The sacred thread of protection tying siblings together."),
  M("Janmashtami", null, 8, "Religious", "🥁", "Birth of Lord Krishna — dahi handi, jhankis and midnight prayers."),
  M("Ganesh Chaturthi", null, 9, "Religious", "🙏", "Birth of Lord Ganesha, celebrated with idols, modaks and visarjan processions."),
  M("Maha Shivratri", null, 2, "Religious", "🔱", "The great night of Lord Shiva with all-night vigils and abhishek."),
  M("Karva Chauth", null, 10, "Religious", "🌙", "The day of fasting by married women for the long life of their husbands."),
  M("Eid-ul-Fitr", null, 3, "Religious", "🌙", "Festival marking the end of Ramadan with feasts, sevaiyan and charity."),
  M("Eid-ul-Adha (Bakrid)", null, 6, "Religious", "🐑", "Festival of sacrifice honouring Ibrahim's devotion, with shared feasts."),
  M("Christmas", null, 12, "Religious", "🎄", "Birth of Jesus Christ — carols, cakes, stars and gift-giving."),
  M("Guru Nanak Jayanti", null, 11, "Religious", "🙏", "Birth anniversary of Guru Nanak, celebrated with langar and kirtan."),
  M("Buddha Purnima", null, 5, "Religious", "🧘", "Birth, enlightenment and mahaparinirvana of Gautama Buddha."),
  M("Rath Yatra", null, 7, "Religious", "🛕", "The chariot festival of Lord Jagannath, grandest in Puri."),
  M("Kumbh Mela", null, 1, "Religious", "🛕", "The world's largest human gathering for a holy dip, rotating among four cities."),
  M("Pongal", null, 1, "Harvest", "🍚", "The four-day Tamil harvest festival honouring the sun god and cattle."),
  M("Lohri", null, 1, "Harvest", "🔥", "The Punjabi winter harvest bonfire festival of song and dance."),
  M("Baisakhi", null, 4, "Harvest", "🌾", "The spring harvest festival of Punjab marking the Sikh New Year."),
  M("Onam", null, 8, "Harvest", "🌸", "Kerala's harvest festival of flower carpets, boat races and the grand sadya."),
  M("Ugadi / Gudi Padwa", null, 3, "Cultural", "🌸", "The lunar New Year of the Deccan — pachadi, gudi hoisting and rangoli."),
  M("Vishu", null, 4, "Harvest", "🌅", "Kerala's astronomical New Year celebrated with the Vishu kani arrangement."),
  M("Rakhi / Nariyal Poornima", null, 8, "Religious", "🥥", "Full moon of the monsoon — rakhi tying and coconut offerings to the sea."),
  M("Independence Day", null, 8, "National", "🇮🇳", "15 August — the nation remembers its freedom with flag hoisting and parades."),
  M("Republic Day", null, 1, "National", "🇮🇳", "26 January — the Constitution's adoption celebrated with the grand parade."),
  M("Gandhi Jayanti", null, 10, "National", "🕊️", "2 October — birth anniversary of Mahatma Gandhi, the Father of the Nation."),
];

export const FESTIVALS: Festival[] = PAN_INDIA_FESTIVALS;

export function getFestival(slug: string) {
  return FESTIVALS.find((f) => f.slug === slug);
}

export const MONTH_NAMES = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

export const FESTIVAL_CATEGORIES = [
  "Religious",
  "Harvest",
  "Cultural",
  "Dance & Music",
  "Fairs & Mela",
  "Tribal",
  "Food",
  "National",
] as const;
