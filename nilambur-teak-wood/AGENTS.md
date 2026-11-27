<!-- BEGIN:nextjs-agent-rules -->

## This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` (resolved from this file's directory; in monorepos the `next` package may not be visible from the repo root) before writing any code. Heed deprecation notices.

This block is written and re-added by `next dev` — verify at `node_modules/next/dist/server/lib/generate-agent-files.js`. Removing it from a diff only re-creates the uncommitted change; committing it with your work keeps the tree clean.

<!-- END:nextjs-agent-rules -->

# Nilambur Teak Wood — Coordinated Agent Workflow & Architectural Governance

This document governs the division of responsibilities, technical standards, and execution protocols for the Nilambur Teak Wood luxury web application.

---

## Agent Roles & Responsibilities

### 1. DESIGN AGENT (`Vanguard_UI_Architect`)
- **Primary Domain**: Luxury brand identity, art direction, color hierarchy, typography, spatial rhythm, and tactile micro-aesthetics.
- **Skills Assigned**: `luxury-web-design`, `high-end-visual-design`, `modern-ui-patterns`, `responsive-premium-layouts`.
- **Core Directives**:
  - Enforce the "Absolute Zero" anti-pattern filter (no generic sans fonts, no raw black `#000000`, no flat 1px gray borders).
  - Apply the **Double-Bezel (Doppelrand)** nested enclosure architecture for all cards and interactive containers.
  - Maintain macro-whitespace (`py-32` to `py-48`) and fluid typography scaling via `clamp()`.
  - Ensure deep espresso, golden amber, and warm cream palettes reflecting authentic Kerala Nilambur teak heartwood.

### 2. FRONTEND AGENT (`NextJS_AppRouter_Specialist`)
- **Primary Domain**: Next.js 16 App Router, React 19 components, TypeScript contracts, client/server boundary management, and Tailwind CSS architecture.
- **Skills Assigned**: `nextjs-app-router-patterns`, `vercel-react-best-practices`, `shadcn-ui-expert`, `shadcn`.
- **Core Directives**:
  - Keep route layouts and page shells as Server Components (RSC) by default.
  - Isolate interactive controls, 3D canvases, and animations into strictly marked `"use client"` leaf components.
  - Compose UI primitives from `src/components/ui/` using `clsx` and `tailwind-merge` (`cn()`).
  - Maintain strict TypeScript type definitions in `src/types/index.ts`.

### 3. 3D AGENT (`Spatial_Experience_Engineer`)
- **Primary Domain**: Three.js, React Three Fiber (R3F), `@react-three/drei`, PBR material shaders, lighting rigs, and 3D furniture interaction.
- **Skills Assigned**: `threejs-r3f-development`, `react-three-fiber`.
- **Core Directives**:
  - Wrap all WebGL `Canvas` components in client-only dynamic imports (`ssr: false`) with graceful loading skeletons.
  - Implement realistic Nilambur Teak PBR wood shaders using roughness, normal, and grain maps.
  - Cap device pixel ratio (`dpr={[1, 2]}`) to protect mobile GPUs and prevent battery drain.
  - Utilize `Float`, `ContactShadows`, and `Environment` presets for studio-grade realism.

### 4. ANIMATION AGENT (`Motion_Choreographer`)
- **Primary Domain**: GSAP, ScrollTrigger, `@gsap/react`, Lenis smooth scrolling, inertia physics, and timeline orchestration.
- **Skills Assigned**: `gsap-scroll-animations`, `gsap-scrolltrigger`, `gsap-react`, `gsap-core`.
- **Core Directives**:
  - Scope all GSAP animations within `useGSAP(() => {}, { scope: containerRef })` for leak-free unmounting.
  - Synchronize Lenis momentum scroll with GSAP's `ScrollTrigger.update` and ticker.
  - Animate exclusively via hardware-accelerated transforms (`transform: translate3d/scale/rotate`) and `opacity`.
  - Implement pinned horizontal showcase galleries with smooth inertia scrubbing.

### 5. ASSET AGENT (`Visual_Asset_Curator`)
- **Primary Domain**: Photography sourcing, licensing verification, texture curation, 3D model asset integration, and image optimization.
- **Skills Assigned**: `nextjs-performance-seo`, `rdkit-general`.
- **Core Directives**:
  - Source exclusively from verified royalty-free or open-license repositories (Unsplash License, Pexels License, CC0).
  - Maintain the official `ASSET_MANIFEST.md` with complete provenance, source URLs, dimensions, and license types.
  - Enforce `next/image` optimization with AVIF/WebP formats, responsive `sizes`, and preloading on LCP hero assets.

### 6. QA AGENT (`Performance_Accessibility_Auditor`)
- **Primary Domain**: Browser testing, responsive layout verification, Core Web Vitals (CWV), WCAG 2.2 AA accessibility, and build integrity.
- **Skills Assigned**: `core-web-vitals`, `accessibility`, `web-design-guidelines`, `impeccable`.
- **Core Directives**:
  - Verify zero console errors, zero hydration mismatches, and passing `npm run build`.
  - Validate touch targets (>= 48px), keyboard navigation, focus visible rings, and ARIA attributes.
  - Test responsiveness across mobile (`375px`), tablet (`768px`), desktop (`1280px`), and ultra-wide (`1920px`).
  - Guarantee LCP < 2.0s, CLS = 0, and fluid 60fps frame rates.

---

## Inter-Agent Handoff Protocol

```
[DESIGN AGENT]  ---> Generates luxury color tokens, typography scales & layout wireframes
      │
[FRONTEND AGENT] ---> Implements RSC page shells, semantic layout & type-safe component trees
      ├───────────────────────────────┬──────────────────────────────┐
      ▼                               ▼                              ▼
[3D AGENT]                     [ANIMATION AGENT]              [ASSET AGENT]
Embeds R3F PBR wood viewer     Choreographs GSAP/Lenis        Curates & optimizes photos,
& interactive camera rigs      ScrollTrigger timelines        textures & asset manifest
      │                               │                              │
      └───────────────────────────────┴──────────────────────────────┘
                                      │
                                      ▼
                                [QA AGENT]
                     Runs verification audit: CWV, a11y,
                     mobile responsiveness & build check
```
