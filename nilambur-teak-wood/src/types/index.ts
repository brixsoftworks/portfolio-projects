// ──────────────────────────────────────────────────────────────
// Nilambur Teak Wood – Shared TypeScript Types
// ──────────────────────────────────────────────────────────────

/** Navigation link */
export interface NavLink {
  label: string;
  href: string;
  children?: NavLink[];
}

/** Product category */
export interface Category {
  slug: string;
  label: string;
  icon: string;
  description?: string;
  image?: string;
}

/** Portfolio / project item */
export interface PortfolioItem {
  id: string;
  title: string;
  slug: string;
  category: string;
  description: string;
  images: string[];
  featured?: boolean;
  location?: string;
  year?: number;
  specs?: Record<string, string>;
}

/** Testimonial */
export interface Testimonial {
  id: string;
  name: string;
  role?: string;
  avatar?: string;
  content: string;
  rating: number;
  project?: string;
}

/** Contact form data */
export interface ContactFormData {
  name: string;
  email: string;
  phone?: string;
  category?: string;
  message: string;
  budget?: string;
}

/** SEO metadata for a page */
export interface PageSEO {
  title: string;
  description: string;
  ogImage?: string;
  canonical?: string;
  noIndex?: boolean;
}

/** 3D model asset reference */
export interface Model3D {
  src: string;
  name: string;
  scale?: [number, number, number];
  position?: [number, number, number];
  rotation?: [number, number, number];
}

/** Section animation config */
export interface AnimationConfig {
  type: "fade" | "slide" | "scale" | "parallax" | "reveal";
  direction?: "up" | "down" | "left" | "right";
  duration?: number;
  delay?: number;
  stagger?: number;
  ease?: string;
}

/** Wood material / finish */
export interface WoodMaterial {
  id: string;
  name: string;
  description: string;
  texture: string;
  color: string;
  grain: "straight" | "interlocked" | "wavy";
  durability: "high" | "very-high" | "exceptional";
}

/** Generic API response wrapper */
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}
