import Link from "next/link";
import type { Region } from "@/data/regions";
import { StateOutline, stateColor, tintColor } from "@/components/artwork";

export function RegionCard({
  region,
  festivalCount,
  productCount,
}: {
  region: Region;
  festivalCount?: number;
  productCount?: number;
}) {
  const color = stateColor(region.slug);
  const zoneLabel =
    region.region === "Islands"
      ? "Island Territories"
      : `${region.region} India`;

  return (
    <div 
      className="region-card group relative flex h-full w-full flex-col rounded-[28px] p-2"
      style={{ 
        background: "linear-gradient(145deg, rgba(255,255,255,0.03) 0%, rgba(255,255,255,0.01) 100%)",
        border: "1px solid rgba(255,255,255,0.08)",
        backdropFilter: "blur(24px)",
        WebkitBackdropFilter: "blur(24px)",
        boxShadow: "inset 0 1px 1px rgba(255,255,255,0.05)"
      }}
    >
      {/* Map illustration area */}
      <Link
        href={`/region/${region.slug}`}
        className="relative block aspect-[16/9] w-full overflow-hidden rounded-[20px]"
      >
        <div
          className="absolute inset-0"
          style={{
            background: `linear-gradient(135deg, ${tintColor(color)}cc 0%, rgba(8,7,10,0.8) 100%)`,
          }}
        />

        <div className="absolute inset-0 flex items-center justify-center p-8">
          <div
            className="h-full w-full group-hover:scale-105"
            style={{ 
              filter: `drop-shadow(0 0 12px ${tintColor(color)}88)`,
              transition: "transform 300ms var(--ease-out)"
            }}
          >
            <StateOutline slug={region.slug} className="h-full w-full" />
          </div>
        </div>

        <div
          className="absolute inset-0"
          style={{ background: "linear-gradient(180deg, transparent 50%, rgba(8,7,10,0.7) 100%)" }}
        />

        <span
          className="absolute left-3 top-3 z-10 rounded-full px-3 py-1 text-[9px] font-bold uppercase tracking-wider"
          style={{
            background: "rgba(8,7,10,0.75)",
            border: "1px solid rgba(255,255,255,0.12)",
            color: "rgba(245,240,232,0.6)",
            backdropFilter: "blur(8px)",
          }}
        >
          {region.type}
        </span>

        <span
          className="absolute right-3 top-3 z-10 flex h-8 w-8 items-center justify-center rounded-full group-hover:scale-110 group-hover:rotate-45"
          style={{
            background: "rgba(8,7,10,0.75)",
            border: "1px solid rgba(255,255,255,0.12)",
            color: "rgba(245,240,232,0.7)",
            backdropFilter: "blur(8px)",
            fontSize: "14px",
            transition: "transform 250ms var(--ease-out), background-color 250ms var(--ease-out)"
          }}
        >
          →
        </span>
      </Link>

      {/* Card body */}
      <div className="flex flex-1 flex-col px-4 pb-4 pt-5">
        <p
          className="mb-1 text-[9px] font-bold uppercase tracking-[0.2em]"
          style={{ color: "rgba(201,169,110,0.6)" }}
        >
          {region.capital} · {zoneLabel}
        </p>

        <Link href={`/region/${region.slug}`}>
          <h3
            className="mb-2 line-clamp-2 font-medium leading-snug group-hover:text-[#e8c882]"
            style={{
              fontFamily: "var(--font-cormorant), Georgia, serif",
              color: "rgba(245,240,232,0.9)",
              fontSize: "18px",
              transition: "color 200ms var(--ease-out)"
            }}
          >
            {region.name}
          </h3>
        </Link>

        <div className="mb-2 mt-2 flex flex-wrap items-center gap-1.5">
          {(festivalCount ?? 0) > 0 && (
            <span className="chip-accent">{festivalCount} Festivals</span>
          )}
          {(productCount ?? 0) > 0 && (
            <span className="chip">{productCount} Products</span>
          )}
        </div>
      </div>
    </div>
  );
}
