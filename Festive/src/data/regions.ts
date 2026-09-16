export type RegionType = "State" | "Union Territory";

export interface Region {
  slug: string;
  name: string;
  type: RegionType;
  capital: string;
  region: "North" | "South" | "East" | "West" | "Central" | "Northeast" | "Islands";
  description: string;
  emoji: string;
}

export const REGIONS: Region[] = [
  {
    slug: "andhra-pradesh",
    name: "Andhra Pradesh",
    type: "State",
    capital: "Amaravati",
    region: "South",
    emoji: "🪔",
    description:
      "Ugadi, Makar Sankranti, Vinayaka Chaturthi and the grand Brahmotsavam of Tirupati define the festive spirit of this Telugu state.",
  },
  {
    slug: "arunachal-pradesh",
    name: "Arunachal Pradesh",
    type: "State",
    capital: "Itanagar",
    region: "Northeast",
    emoji: "🏔️",
    description:
      "Losar, Dree, Mopin, Solung, Nyokum and Si-Donyi celebrate the rich tribal heritage of the eastern Himalayas.",
  },
  {
    slug: "assam",
    name: "Assam",
    type: "State",
    capital: "Dispur",
    region: "Northeast",
    emoji: "🎋",
    description:
      "The three Bihu festivals — Bohag, Kongali and Bhogali — along with Ambubachi and Baishagu capture Assam's agrarian joy.",
  },
  {
    slug: "bihar",
    name: "Bihar",
    type: "State",
    capital: "Patna",
    region: "East",
    emoji: "🌅",
    description:
      "Chhath Puja, the toughest and most luminous of festivals, along with Sonepur Cattle Fair and Buddha Jayanti.",
  },
  {
    slug: "chhattisgarh",
    name: "Chhattisgarh",
    type: "State",
    capital: "Raipur",
    region: "Central",
    emoji: "🏹",
    description:
      "The 75-day Bastar Dussehra, Pola, Hareli and Maghi Purnima reflect the tribal soul of central India.",
  },
  {
    slug: "goa",
    name: "Goa",
    type: "State",
    capital: "Panaji",
    region: "West",
    emoji: "🎭",
    description:
      "Goa Carnival, Shigmo, Sao Joao and the Feast of St Francis Xavier blend Portuguese and Konkani culture.",
  },
  {
    slug: "gujarat",
    name: "Gujarat",
    type: "State",
    capital: "Gandhinagar",
    region: "West",
    emoji: "🪁",
    description:
      "Navratri's nine nights of garba, the Uttarayan kite festival and the white-sand Rann Utsav.",
  },
  {
    slug: "haryana",
    name: "Haryana",
    type: "State",
    capital: "Chandigarh",
    region: "North",
    emoji: "🌾",
    description:
      "Baisakhi, the Surajkund Craft Mela, Teej and Lohri keep Haryana's folk culture alive.",
  },
  {
    slug: "himachal-pradesh",
    name: "Himachal Pradesh",
    type: "State",
    capital: "Shimla",
    region: "North",
    emoji: "⛰️",
    description:
      "Kullu Dussehra, Mandi Shivratri, Losar and the traditional Rakhadumni festival of the mountains.",
  },
  {
    slug: "jharkhand",
    name: "Jharkhand",
    type: "State",
    capital: "Ranchi",
    region: "East",
    emoji: "🥁",
    description:
      "Sarhul, Karam Utsav, Tusu and Sohrai celebrate nature and the tribal communities of the region.",
  },
  {
    slug: "karnataka",
    name: "Karnataka",
    type: "State",
    capital: "Bengaluru",
    region: "South",
    emoji: "🐘",
    description:
      "The royal Mysore Dasara, Ugadi, Makar Sankranti, Karaga and the Hampi festival of dance and heritage.",
  },
  {
    slug: "kerala",
    name: "Kerala",
    type: "State",
    capital: "Thiruvananthapuram",
    region: "South",
    emoji: "⛵",
    description:
      "Onam's boat races, Vishu, Thrissur Pooram's elephant pageantry and the enchanting Theyyam rituals.",
  },
  {
    slug: "madhya-pradesh",
    name: "Madhya Pradesh",
    type: "State",
    capital: "Bhopal",
    region: "Central",
    emoji: "🎨",
    description:
      "The Khajuraho Dance Festival, Tejaji fair and Lok-rang Utsav celebrate the heart of India.",
  },
  {
    slug: "maharashtra",
    name: "Maharashtra",
    type: "State",
    capital: "Mumbai",
    region: "West",
    emoji: "🙏",
    description:
      "Ganesh Chaturthi's ten-day revelry, Gudi Padwa and Narali Purnima mark the Marathi festive year.",
  },
  {
    slug: "manipur",
    name: "Manipur",
    type: "State",
    capital: "Imphal",
    region: "Northeast",
    emoji: "🎪",
    description:
      "Yaoshang, Lai Haraoba, Kang Chingba and the post-harvest Chavang Kut of the Kuki-Chin people.",
  },
  {
    slug: "meghalaya",
    name: "Meghalaya",
    type: "State",
    capital: "Shillong",
    region: "Northeast",
    emoji: "🌈",
    description:
      "Ka Pomblang Nongkrem, Wangala's hundred drums and the Behdienkhlam festival of the Khasis.",
  },
  {
    slug: "mizoram",
    name: "Mizoram",
    type: "State",
    capital: "Aizawl",
    region: "Northeast",
    emoji: "🎶",
    description:
      "Chapchar Kut, Mim Kut and Pawl Kut are the vibrant agricultural festivals of the Mizo people.",
  },
  {
    slug: "nagaland",
    name: "Nagaland",
    type: "State",
    capital: "Kohima",
    region: "Northeast",
    emoji: "🦤",
    description:
      "The Hornbill Festival showcases all Naga tribes; Moatsu, Sekrenyi and Aoling follow the agrarian cycle.",
  },
  {
    slug: "odisha",
    name: "Odisha",
    type: "State",
    capital: "Bhubaneswar",
    region: "East",
    emoji: "🛕",
    description:
      "The Rath Yatra of Puri, Raja Parba, Nuakhai and the Konark Dance Festival honour Odisha's maritime legacy.",
  },
  {
    slug: "punjab",
    name: "Punjab",
    type: "State",
    capital: "Chandigarh",
    region: "North",
    emoji: "🌻",
    description:
      "Baisakhi's bhangra, the bonfires of Lohri, Guru Nanak Jayanti and the valour of Holla Mohalla.",
  },
  {
    slug: "rajasthan",
    name: "Rajasthan",
    type: "State",
    capital: "Jaipur",
    region: "North",
    emoji: "🐪",
    description:
      "Gangaur, Teej, the Pushkar Camel Fair, Desert Festival and Jaipur Literature Festival — the land of grandeur.",
  },
  {
    slug: "sikkim",
    name: "Sikkim",
    type: "State",
    capital: "Gangtok",
    region: "Northeast",
    emoji: "🏔️",
    description:
      "Losar, Saga Dawa, Pang Lhabsol and the International Flower Festival in the shadow of Kanchenjunga.",
  },
  {
    slug: "tamil-nadu",
    name: "Tamil Nadu",
    type: "State",
    capital: "Chennai",
    region: "South",
    emoji: "🌾",
    description:
      "Pongal, Thaipusam, Karthigai Deepam, Puthandu and the December season of music and dance.",
  },
  {
    slug: "telangana",
    name: "Telangana",
    type: "State",
    capital: "Hyderabad",
    region: "South",
    emoji: "🌸",
    description:
      "Bathukamma's floral mounds, Bonalu, Ugadi and the Medaram Samakka Saralamma Jatara.",
  },
  {
    slug: "tripura",
    name: "Tripura",
    type: "State",
    capital: "Agartala",
    region: "Northeast",
    emoji: "🏛️",
    description:
      "Kharchi Puja, Ker Puja, Garia Puja and the Bengali Rabindra and Nazrul Jayanti celebrations.",
  },
  {
    slug: "uttar-pradesh",
    name: "Uttar Pradesh",
    type: "State",
    capital: "Lucknow",
    region: "North",
    emoji: "🛕",
    description:
      "Kumbh Mela, Lathmar Holi of Barsana, Janmashtami in Mathura, Dev Deepavali and Ram Leela of Varanasi.",
  },
  {
    slug: "uttarakhand",
    name: "Uttarakhand",
    type: "State",
    capital: "Dehradun",
    region: "North",
    emoji: "🏞️",
    description:
      "Magh Mela, Uttarayani Mela, Ganga Dussehra and the Nanda Devi Raj Jat yatra of the Garhwal hills.",
  },
  {
    slug: "west-bengal",
    name: "West Bengal",
    type: "State",
    capital: "Kolkata",
    region: "East",
    emoji: "🪔",
    description:
      "Durga Puja's pandals, Kali Puja, Poila Boishakh, Saraswati Puja and the Gangasagar Mela.",
  },
  {
    slug: "andaman-and-nicobar",
    name: "Andaman & Nicobar Islands",
    type: "Union Territory",
    capital: "Port Blair",
    region: "Islands",
    emoji: "🏝️",
    description:
      "The Island Tourism Festival and Monsoon Festival bring together Pongal, Holi, Eid and Christmas on the islands.",
  },
  {
    slug: "chandigarh",
    name: "Chandigarh",
    type: "Union Territory",
    capital: "Chandigarh",
    region: "North",
    emoji: "🌹",
    description:
      "Baisakhi, the Rose Festival and the Chandigarh Carnival light up the City Beautiful.",
  },
  {
    slug: "dadra-nagar-haveli-daman-diu",
    name: "Dadra & Nagar Haveli and Daman & Diu",
    type: "Union Territory",
    capital: "Daman",
    region: "West",
    emoji: "🥥",
    description:
      "Nariyela Poornima, Holika Dahan, the Tribal Art Festival and Daman's coastal carnival traditions.",
  },
  {
    slug: "delhi",
    name: "Delhi (NCT)",
    type: "Union Territory",
    capital: "New Delhi",
    region: "North",
    emoji: "🏛️",
    description:
      "Diwali, Holi, Dussehra, Durga Puja, the Qutub Festival and the International Mango Festival in the capital.",
  },
  {
    slug: "jammu-and-kashmir",
    name: "Jammu & Kashmir",
    type: "Union Territory",
    capital: "Srinagar (Summer), Jammu (Winter)",
    region: "North",
    emoji: "🌷",
    description:
      "Herath (Shivratri), Navreh, the Tulip Festival of Srinagar and the Urs fairs of the valley.",
  },
  {
    slug: "ladakh",
    name: "Ladakh",
    type: "Union Territory",
    capital: "Leh",
    region: "North",
    emoji: "🕍",
    description:
      "The Hemis Festival, Losar, Galdan Namchot, Sindhu Darshan and the Gustor mask dances of the monasteries.",
  },
  {
    slug: "lakshadweep",
    name: "Lakshadweep",
    type: "Union Territory",
    capital: "Kavaratti",
    region: "Islands",
    emoji: "🌊",
    description:
      "Eid-ul-Fitr, Eid-ul-Adha, Milad-un-Nabi and Muharram on the coral atolls of the Arabian Sea.",
  },
  {
    slug: "puducherry",
    name: "Puducherry",
    type: "Union Territory",
    capital: "Puducherry",
    region: "South",
    emoji: "🇫🇷",
    description:
      "Pongal, the Fire Walking Festival, Bastille Day and the French Food Festival blend Tamil and French culture.",
  },
];

export const STATES = REGIONS.filter((r) => r.type === "State");
export const UNION_TERRITORIES = REGIONS.filter((r) => r.type === "Union Territory");

export function getRegion(slug: string) {
  return REGIONS.find((r) => r.slug === slug);
}
