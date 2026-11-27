// ──────────────────────────────────────────────────────────────
// Nilambur Teak Wood – Global Constants
// ──────────────────────────────────────────────────────────────

export const SITE_NAME = "Nilambur Teak Wood";
export const SITE_DESCRIPTION =
  "Premium teak wood interiors, furniture, and architectural woodwork crafted from the legendary Nilambur teak forests of Kerala.";
export const SITE_URL = "https://nilamburteakwood.com";

// Navigation
export const NAV_LINKS = [
  { label: "Home", href: "/" },
  { label: "About", href: "/about" },
  { label: "Collections", href: "/collections" },
  { label: "Portfolio", href: "/portfolio" },
  { label: "Process", href: "/process" },
  { label: "Contact", href: "/contact" },
] as const;

// Product Categories
export const CATEGORIES = [
  { slug: "living-rooms", label: "Living Rooms", icon: "sofa" },
  { slug: "kitchens", label: "Kitchens", icon: "chef-hat" },
  { slug: "bedrooms", label: "Bedrooms", icon: "bed" },
  { slug: "wardrobes", label: "Wardrobes", icon: "shirt" },
  { slug: "furniture", label: "Furniture", icon: "armchair" },
  { slug: "doors", label: "Doors & Windows", icon: "door-open" },
  { slug: "staircases", label: "Staircases", icon: "stairs" },
] as const;

// Animation
export const SCROLL_TRIGGER_DEFAULTS = {
  start: "top 85%",
  end: "bottom 15%",
  toggleActions: "play none none reverse",
} as const;

export const TRANSITION_DURATION = 0.8;
export const STAGGER_DELAY = 0.15;

// 3D Scene
export const CAMERA_FOV = 45;
export const CAMERA_NEAR = 0.1;
export const CAMERA_FAR = 1000;

// Breakpoints (matches Tailwind defaults)
export const BREAKPOINTS = {
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  "2xl": 1536,
} as const;
