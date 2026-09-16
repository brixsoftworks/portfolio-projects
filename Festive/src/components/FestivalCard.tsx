import Link from "next/link";
import type { Festival } from "@/data/festivals";
import { MONTH_NAMES } from "@/data/festivals";
import { REGIONS } from "@/data/regions";
import { StateOutline, stateColor, tintColor } from "@/components/artwork";
import { festivalImage } from "@/data/festivalImages";
import Interactive3DLogo from "@/components/Interactive3DLogo";

export const MONTH_ABBR = [
  "Jan", "Feb", "Mar", "Apr", "May", "Jun",
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
];

const REGION_NAME = new Map(REGIONS.map((r) => [r.slug, r.name]));

function getDepthPath(imagePath: string) {
  const extIndex = imagePath.lastIndexOf('.');
  if (extIndex === -1) return imagePath;
  return imagePath.substring(0, extIndex) + '_depth' + imagePath.substring(extIndex);
}

export function FestivalCard({
  festival,
  compact,
}: {
  festival: Festival;
  compact?: boolean;
}) {
  const shapeSlug = festival.stateSlug ?? "india";
  const color = stateColor(shapeSlug);
  const image = festivalImage(festival.slug);
  const regionLabel = festival.isPanIndia
    ? "All of India"
    : (festival.stateSlug && REGION_NAME.get(festival.stateSlug)) || "India";

  return (
    <div className="group relative flex flex-col items-center gap-4 w-full h-full">
      {/* Circle Button Image */}
      <Link
        href={`/festival/${festival.slug}`}
        className="festival-circle relative flex aspect-square w-full max-w-[180px] overflow-hidden rounded-full p-1.5"
        style={{
          background: "linear-gradient(145deg, rgba(201,169,110,0.3) 0%, rgba(255,255,255,0.02) 100%)",
          boxShadow: "inset 0 1px 1px rgba(255,255,255,0.1)",
        }}
      >
        <div className="relative h-full w-full overflow-hidden rounded-full bg-[#1a1820]">
          {image ? (
            <Interactive3DLogo 
              imagePath={image} 
              depthPath={getDepthPath(image)} 
              alt={festival.name} 
            />
          ) : (
            <>
              <div
                className="absolute inset-0"
                style={{ background: `linear-gradient(135deg, ${tintColor(color)}dd, rgba(8,7,10,0.6))` }}
              />
              <div className="absolute inset-0 p-6" style={{ opacity: 0.4 }}>
                <StateOutline slug={shapeSlug} className="h-full w-full" />
              </div>
            </>
          )}

          <div
            className="absolute inset-0 pointer-events-none"
            style={{ background: "linear-gradient(180deg, transparent 40%, rgba(8,7,10,0.6) 100%)" }}
          />
        </div>
      </Link>

      {/* Text Area */}
      <div className="flex flex-col items-center text-center px-2">
        <p
          className="mb-1.5 text-[10px] font-bold uppercase tracking-[0.2em]"
          style={{ color: "rgba(201,169,110,0.8)" }}
        >
          {MONTH_ABBR[festival.month - 1]} • {regionLabel}
        </p>
        <Link href={`/festival/${festival.slug}`}>
          <h3
            className="line-clamp-2 font-medium leading-snug transition-colors duration-200 group-hover:text-[#e8c882]"
            style={{
              fontFamily: "var(--font-cormorant), Georgia, serif",
              color: "rgba(245,240,232,0.9)",
              fontSize: "19px",
            }}
          >
            {festival.name}
          </h3>
        </Link>
      </div>
    </div>
  );
}
