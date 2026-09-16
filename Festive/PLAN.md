# Festive — Indian Festival E-Commerce Website

An e-commerce platform for selling festival products across all 28 states and 8 union territories of India.

## 1. Project Overview

- **Name:** Festive
- **Purpose:** Sell festival-related products (decor, pooja items, sweets, clothing, gifts, etc.) categorized by every Indian festival, state, and union territory.
- **Tagline:** India's Land of Festivals — 500+ celebrations, one store.

### Research Summary: Festivals of India

India is known as the "Land of Festivals" — more than **500 festivals** are celebrated every year across the country. This includes:

- **~30 pan-India festivals** — Diwali, Holi, Eid-ul-Fitr, Eid-ul-Adha, Christmas, Navratri, Durga Puja, Ganesh Chaturthi, Raksha Bandhan, Janmashtami, Makar Sankranti, Maha Shivratri, Karva Chauth, Guru Nanak Jayanti, Buddha Purnima, etc.
- **~250 region-specific festivals** across 28 states and 8 UTs (5–10 unique festivals per region).
- **3 national festivals** — Independence Day, Republic Day, Gandhi Jayanti.
- Source: Ministry of Tourism's utsav.gov.in and standard references (StudyIQ, Physics Wallah, MapsofIndia).

### Festivals by State (28 states)

| State | Major Festivals |
|---|---|
| Andhra Pradesh | Ugadi, Makar Sankranti, Vinayaka Chaturthi, Brahmotsavam, Nagula Chavithi, Deccan Festival |
| Arunachal Pradesh | Losar, Dree, Mopin, Solung, Nyokum, Si-Donyi, Boori Boot, Reh, Myoko |
| Assam | Bihu (Bohag/Kongali/Bhogali), Ambubachi, Dehing Patkai, Baishagu |
| Bihar | Chhath Puja, Sonepur Cattle Fair, Makar Sankranti Mela, Buddha Jayanti, Bihula |
| Chhattisgarh | Bastar Dussehra, Maghi Purnima, Pola, Hareli, Narayanpur Mela |
| Goa | Goa Carnival, Shigmo, Sao Joao, Feast of St. Francis Xavier, Ladainha |
| Gujarat | Navratri, Uttarayan Kite Festival, Rann Utsav, Janmashtami, Tarnetar Fair |
| Haryana | Baisakhi, Surajkund Craft Mela, Teej, Lohri |
| Himachal Pradesh | Kullu Dussehra, Mandi Shivratri, Losar, Halda, Sazo, Rakhadumni |
| Jharkhand | Sarhul, Karam Utsav, Tusu, Sohrai, Rohini |
| Karnataka | Mysore Dasara, Ugadi, Makar Sankranti, Karaga, Hampi Festival |
| Kerala | Onam, Vishu, Thrissur Pooram, Nehru Trophy Boat Race, Attukal Pongala, Theyyam |
| Madhya Pradesh | Khajuraho Dance Festival, Tejaji, Lok-rang Utsav, Pachmarhi Utsav |
| Maharashtra | Ganesh Chaturthi, Gudi Padwa, Narali Purnima, Kalidas Festival |
| Manipur | Yaoshang, Kang Chingba, Lai Haraoba, Chavang Kut |
| Meghalaya | Nongkrem, Wangala, Behdienkhlam, Shad Suk Mynsiem |
| Mizoram | Chapchar Kut, Mim Kut, Pawl Kut |
| Nagaland | Hornbill Festival, Moatsu, Sekrenyi, Aoling |
| Odisha | Rath Yatra, Raja Parba, Nuakhai, Konark Dance Festival, Chandan Yatra |
| Punjab | Baisakhi, Lohri, Guru Nanak Jayanti, Holla Mohalla |
| Rajasthan | Gangaur, Teej, Pushkar Camel Fair, Desert Festival, Jaipur Literature Festival |
| Sikkim | Losar, Saga Dawa, Pang Lhabsol, Losoong, Maghe Sankranti |
| Tamil Nadu | Pongal, Thaipusam, Jallikattu, Puthandu, Karthigai Deepam |
| Telangana | Bathukamma, Bonalu, Ugadi, Samakka Jatara |
| Tripura | Kharchi Puja, Ker Puja, Garia Puja |
| Uttar Pradesh | Kumbh Mela, Diwali, Lathmar Holi, Janmashtami, Dev Deepavali |
| Uttarakhand | Magh Mela, Uttarayani Mela, Ganga Dussehra, Nanda Devi Mela |
| West Bengal | Durga Puja, Kali Puja, Poila Boishakh, Saraswati Puja, Gangasagar Mela |

### Festivals by Union Territory (8 UTs)

| Union Territory | Major Festivals |
|---|---|
| Andaman & Nicobar Islands | Island Tourism Festival, Monsoon Festival, Swami Vivekananda Jayanti |
| Chandigarh | Baisakhi, Chandigarh Carnival, Rose Festival, Lohri |
| Dadra & Nagar Haveli and Daman & Diu | Nariyela Poornima, Holika Dahan, Tribal Art Festival, Daman Festival |
| Delhi | Diwali, Holi, Dussehra, Durga Puja, Qutub Festival, Mango Festival |
| Jammu & Kashmir | Lohri, Herath (Shivratri), Navreh, Tulip Festival, Urs fairs |
| Ladakh | Hemis Festival, Losar, Galdan Namchot, Sindhu Darshan, Spituk Gustor |
| Lakshadweep | Eid-ul-Fitr, Eid-ul-Adha, Milad-un-Nabi, Muharram |
| Puducherry | Pongal, Fire Walking Festival, Bastille Day, French Food Festival |

## 2. Tech Stack

| Layer | Technology |
|---|---|
| Frontend/Backend | **Next.js 14 (App Router) + TypeScript + Tailwind CSS** |
| Database | **Supabase (PostgreSQL)** — free tier |
| Auth | Supabase Auth |
| File storage (product images) | Supabase Storage |
| Payments | **Razorpay** (UPI, cards, netbanking) |
| Deployment | Vercel (free tier) |
| Quality | ESLint + Prettier + TypeScript strict |

**Why Supabase (best free option):** Free PostgreSQL database (~500MB), built-in auth (~50k MAU free), and file storage. It fits relational e-commerce data (products, orders, carts) and pairs natively with Next.js. Alternative: self-hosted PostgreSQL + Prisma (100% free, no cloud, but you manage everything).

## 3. Database Schema

### Tables

```
states_uts
  id (pk), name, type ('state' | 'union_territory'), slug, capital, region, description

festivals
  id (pk), name, slug, state_ut_id (fk), category, month, is_pan_india (bool),
  description, image_url, date_info

categories
  id (pk), name, slug, image_url          -- e.g. Decor, Pooja Items, Sweets, Clothing, Gifts

products
  id (pk), name, slug, description, price, compare_at_price, stock,
  category_id (fk), festival_id (fk), state_ut_id (fk), images (array), featured (bool)

users
  id (pk, from auth), email, full_name, phone, address, role ('customer' | 'admin')

carts
  id (pk), user_id (fk)

cart_items
  id (pk), cart_id (fk), product_id (fk), quantity

orders
  id (pk), user_id (fk), total, status, payment_id (razorpay), shipping_address,
  created_at

order_items
  id (pk), order_id (fk), product_id (fk), quantity, unit_price
```

### Seed Data

- 36 rows in `states_uts` (28 states + 8 UTs)
- ~250 festival entries from the research tables above (top festivals per region)
- ~30 pan-India festivals flagged with `is_pan_india`
- Sample product catalog across categories (pooja kits, diyas, rangoli, sweets, ethnic wear, gifts)

## 4. Pages & Features

### Public Pages (Next.js App Router)

| Route | Description |
|---|---|
| `/` | Home — hero, pan-India festivals, featured products, state/UT explorer |
| `/states` | Browse all 28 states + 8 UTs |
| `/states/[slug]` | State/UT page — its festivals + products |
| `/festivals` | Calendar view grouped by month, filter by category/state |
| `/festivals/[slug]` | Festival detail — date, about, related products |
| `/products` | Product catalog with search + filters (category, state, festival) |
| `/products/[slug]` | Product detail |
| `/cart` | Shopping cart |
| `/checkout` | Checkout flow with Razorpay |
| `/account` | Profile, addresses |
| `/orders` | Order history + tracking |
| `/admin` | Admin panel (role-protected) |

### E-Commerce Features

1. Storefront with product catalog
2. Shopping cart (DB-backed, persistent per user)
3. Checkout with Razorpay (UPI, cards, netbanking)
4. User accounts (Supabase Auth) + order history
5. Admin panel (add/edit products, manage festivals, view orders)
6. Festival calendar (upcoming festivals by state/UT)
7. Search + filters

## 5. Production-Ready Extras

- SEO metadata per state/festival/product page + sitemap
- ISR (Incremental Static Regeneration) for fast static pages
- Next.js Image optimization for product images
- Environment variables for Razorpay + Supabase keys (never committed)
- Razorpay webhook for payment confirmation
- Order confirmation emails
- Deployment-ready for Vercel

## 6. Build Milestones

1. **Scaffold** — Next.js + TS + Tailwind, ESLint/Prettier, git repo
2. **Data layer** — Supabase project, schema migration, seed scripts (states/UTs, festivals, products)
3. **Storefront** — Home, states, festivals, products pages with search/filters
4. **Commerce** — Cart, checkout, Razorpay integration, orders
5. **Auth** — Sign up/login, accounts, admin roles
6. **Admin panel** — Product/order/festival management
7. **Polish** — SEO, images, ISR, email, error handling
8. **Deploy** — Vercel + env config

## 7. Verification

- Run lint, typecheck, and production build
- Test cart → checkout → order flow with seed data
- Verify Razorpay test-mode payments (webhook flow)
- Validate all 36 state/UT pages render with festival data

## 8. Out of Scope (v1)

- Full 500+ festival dataset (seeded with ~250 top festivals; rest added via admin)
- Logistics/shipping provider integrations
- Reviews & ratings
- Multi-language support (i18n)
- Mobile app
