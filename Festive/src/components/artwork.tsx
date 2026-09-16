import type { ReactNode } from "react";
import { STATE_SHAPES } from "@/data/stateShapes";

const GOOGLE = {
  blue: "#4285F4",
  red: "#EA4335",
  yellow: "#FBBC05",
  green: "#34A853",
  orange: "#F97316",
  ink: "#1f2937",
  cream: "#FFFDF7",
};

const PATCH_BGS = [
  "#EAF3FF", "#FFF1F0", "#FFFBE6", "#EAF7EF", "#FDF0E7", "#F3E8FF", "#E8F6F8", "#FFF5E6",
];

const STITCH = {
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
};

function Ring({ color = GOOGLE.ink }: { color?: string }) {
  return (
    <g>
      <circle cx="32" cy="32" r="29.5" fill="none" stroke={color} strokeWidth="1.6" strokeDasharray="3 4" {...STITCH} />
      <circle cx="32" cy="32" r="26.5" fill="none" stroke={color} strokeWidth="1" strokeDasharray="2 4" opacity="0.45" {...STITCH} />
    </g>
  );
}

function Cross({ x, y, c = GOOGLE.ink, s = 1.6 }: { x: string | number; y: string | number; c?: string; s?: number }) {
  const px = Number(x);
  const py = Number(y);
  return <path d={`M${px - s} ${py - s} L${px + s} ${py + s} M${px + s} ${py - s} L${px - s} ${py + s}`} stroke={c} strokeWidth="1.4" strokeLinecap="round" />;
}

type MotifId =
  | "diya" | "kite" | "lantern" | "flower" | "marigold" | "peacock" | "fire" | "boat"
  | "temple" | "chariot" | "drum" | "mask" | "sun" | "moon" | "lotus" | "conch"
  | "harvest" | "serpent" | "elephant" | "camel" | "bird" | "mountain" | "palm"
  | "umbrella" | "bull" | "trishul" | "thread" | "candle";

const MOTIFS: Record<MotifId, (c: string, a: string) => ReactNode> = {
  diya: (c, a) => (
    <g>
      <path d="M20 45h24l-4 6H24l-4-6z" fill="#fff" stroke={c} strokeWidth="2.6" {...STITCH} />
      <path d="M24 42c0-5 3.5-8 8-8s8 3 8 8" fill="none" stroke={c} strokeWidth="2.4" {...STITCH} />
      <path d="M32 34c0-5-3-8-5.5-10.5" fill="none" stroke={a} strokeWidth="2.2" strokeLinecap="round" />
      <path d="M32 34c0-5 3-8 5.5-10.5" fill="none" stroke={a} strokeWidth="2.2" strokeLinecap="round" />
      <path d="M32 36c-2.5-4-2.5-7-1-9.5 1.1 2.3 1.1 4.3 1 6.3 1.5-2 1.5-4.8 2.5-6.3 1 2.5 1 5.5-1.5 9.5z" fill={GOOGLE.yellow} stroke={c} strokeWidth="1.8" {...STITCH} />
      <Cross x="28" y="39" c={a} />
    </g>
  ),
  candle: (c, a) => (
    <g>
      <path d="M27 47h10v-10H27z" fill="#fff" stroke={c} strokeWidth="2.6" {...STITCH} />
      <path d="M32 37v-5" stroke={c} strokeWidth="2.4" strokeLinecap="round" />
      <path d="M32 32c-2.5-3.5-2.5-6.5-1-9 1.2 2.3 1.2 4.3 1 6.3 1.5-2 1.5-4.8 2.5-6.3 1 2.5 1 5.5-1.5 9z" fill={GOOGLE.yellow} stroke={c} strokeWidth="1.8" {...STITCH} />
      <path d="M24 47h16" stroke={c} strokeWidth="2.2" strokeLinecap="round" />
      <path d="M22 51h20" stroke={c} strokeWidth="2" strokeLinecap="round" strokeDasharray="2 3" />
    </g>
  ),
  kite: (c, a) => (
    <g>
      <polygon points="32,12 47,32 32,52 17,32" fill={GOOGLE.blue} stroke={c} strokeWidth="2.4" {...STITCH} />
      <path d="M32 14v38M19 33l24-22M19 31l24 22" stroke="#fff" strokeWidth="1.4" opacity="0.85" />
      <path d="M26 22l4 4M38 40l-4-4" stroke={GOOGLE.yellow} strokeWidth="2" strokeLinecap="round" />
      <path d="M32 52c-1 5-3 7-6 8 3-1 5-1 7 1 2-2 4-2 7-1-3-1-5-3-6-8z" fill={GOOGLE.red} stroke={c} strokeWidth="1.6" {...STITCH} />
    </g>
  ),
  lantern: (c, a) => (
    <g>
      <path d="M32 15v-4M28 11h8" stroke={c} strokeWidth="2.4" strokeLinecap="round" />
      <path d="M24 19c0-3 3.5-5 8-5s8 2 8 5l3 23c0 3.5-5 6-11 6s-11-2.5-11-6l3-23z" fill={GOOGLE.yellow} stroke={c} strokeWidth="2.4" {...STITCH} />
      <path d="M32 21v28" stroke={c} strokeWidth="1.4" strokeDasharray="2 3" />
      <path d="M25 27h14M25 33h14M25 39h14" stroke={c} strokeWidth="1.6" />
      <path d="M32 48v4M27 52h10l1.5 3h-13l1.5-3z" stroke={c} strokeWidth="2.2" fill="#fff" strokeLinejoin="round" />
      <Cross x="32" y="18" c={a} s={1.4} />
    </g>
  ),
  flower: (c, a) => (
    <g>
      {[0, 45, 90, 135, 180, 225, 270, 315].map((deg) => (
        <ellipse key={deg} cx="32" cy="19" rx="5" ry="8" fill={GOOGLE.red} stroke={c} strokeWidth="2" {...STITCH} transform={`rotate(${deg} 32 32)`} />
      ))}
      <circle cx="32" cy="32" r="6" fill={GOOGLE.yellow} stroke={c} strokeWidth="2" {...STITCH} />
      <Cross x="32" y="32" c={c} s={1.8} />
    </g>
  ),
  marigold: (c, a) => (
    <g>
      <circle cx="32" cy="32" r="17" fill={GOOGLE.yellow} stroke={c} strokeWidth="2.4" {...STITCH} />
      <circle cx="32" cy="32" r="10" fill="none" stroke={c} strokeWidth="1.8" strokeDasharray="3 3" />
      <circle cx="32" cy="32" r="4" fill={GOOGLE.orange ?? "#F97316"} stroke={c} strokeWidth="1.6" {...STITCH} />
      {[0, 45, 90, 135, 180, 225, 270, 315].map((deg) => (
        <path key={deg} d="M32 20v24" transform={`rotate(${deg} 32 32)`} stroke={c} strokeWidth="1.4" strokeDasharray="2 3" />
      ))}
    </g>
  ),
  peacock: (c, a) => (
    <g>
      <path d="M32 47c-8 0-13-5-13-12 0-5 3-9 7-11l-2 6 5-8c3-1 7-1 10-1l4 9-2-6c4 2 6 6 6 11 0 7-5 12-13 12z" fill={GOOGLE.blue} stroke={c} strokeWidth="2.4" {...STITCH} />
      <path d="M27 30a5 5 0 0 1 10 0M27 30l-3 10M37 30l3 10M24 34l-2 8M40 34l2 8" stroke={c} strokeWidth="1.6" strokeLinecap="round" />
      <circle cx="32" cy="30" r="4.5" fill={GOOGLE.green} stroke={c} strokeWidth="1.8" {...STITCH} />
      <circle cx="32" cy="30" r="1.6" fill={GOOGLE.yellow} stroke={c} strokeWidth="1" />
      <path d="M26 42l-4 7M38 42l4 7" stroke={c} strokeWidth="2" strokeLinecap="round" />
    </g>
  ),
  fire: (c, a) => (
    <g>
      <path d="M32 13c5 5 9 9 9 15a9 9 0 0 1-18 0c0-3 1.3-5.5 3.5-8-.5 2.6-.3 4.3 1.2 5.9C27.4 20 30.4 16.5 32 13z" fill={GOOGLE.red} stroke={c} strokeWidth="2.2" {...STITCH} />
      <path d="M32 24c3 2.6 4.6 4.8 4.6 7.4a4.6 4.6 0 0 1-9.2 0c0-1.8.7-3.2 1.8-4.8-.2 1.5 0 2.5.6 3.4.7-1.6 1.4-3 2.2-6z" fill={GOOGLE.yellow} stroke={c} strokeWidth="1.6" {...STITCH} />
      <path d="M22 44c3-3 6-3 9-1 3-2 6-2 9 1l2 5H20l2-5z" fill={GOOGLE.orange ?? "#F97316"} stroke={c} strokeWidth="2.2" {...STITCH} />
      <path d="M19 51h26" stroke={c} strokeWidth="2.2" strokeLinecap="round" strokeDasharray="3 3" />
    </g>
  ),
  boat: (c, a) => (
    <g>
      <path d="M13 35c8-3 15-5 19-5s11 2 19 5l-6 10c-3.4 3.4-7.5 4.6-13 4.6s-9.6-1.2-13-4.6L13 35z" fill={GOOGLE.green} stroke={c} strokeWidth="2.4" {...STITCH} />
      <path d="M32 30v-8" stroke={c} strokeWidth="2.4" strokeLinecap="round" />
      <path d="M25 27c4-2 10-2 14 0" stroke={c} strokeWidth="1.6" />
      <path d="M18 37h28" stroke={c} strokeWidth="1.4" strokeDasharray="2 3" />
      <path d="M32 22l-7 3.5 7 3.5 7-3.5L32 22z" fill={GOOGLE.red} stroke={c} strokeWidth="1.8" {...STITCH} />
      <path d="M32 29v6" stroke={c} strokeWidth="1.8" strokeLinecap="round" />
    </g>
  ),
  temple: (c, a) => (
    <g>
      <path d="M17 48h30" stroke={c} strokeWidth="2.6" strokeLinecap="round" />
      <path d="M21 48V34M43 48V34" stroke={c} strokeWidth="2.4" />
      <path d="M21 34l11-9 11 9" fill="none" stroke={c} strokeWidth="2.4" {...STITCH} />
      <path d="M26 48V22c0-2.2 2.7-4 6-4s6 1.8 6 4v26" fill={GOOGLE.yellow} stroke={c} strokeWidth="2.2" {...STITCH} />
      <path d="M28 41h2M34 41h2M28 35h2M34 35h2" stroke={c} strokeWidth="1.8" />
      <path d="M32 18V14M27 15l5-6 5 6" stroke={c} strokeWidth="2" strokeLinecap="round" />
      <path d="M27 45h3M34 45h3" stroke={GOOGLE.red} strokeWidth="2" strokeLinecap="round" />
    </g>
  ),
  chariot: (c, a) => (
    <g>
      <circle cx="25" cy="40" r="8" fill="#fff" stroke={c} strokeWidth="2.4" {...STITCH} />
      <circle cx="25" cy="40" r="3" fill="none" stroke={c} strokeWidth="1.6" />
      <circle cx="40" cy="42" r="6" fill="#fff" stroke={c} strokeWidth="2.2" {...STITCH} />
      <circle cx="40" cy="42" r="2" fill="none" stroke={c} strokeWidth="1.4" />
      <path d="M25 48v-3M40 48v-2" stroke={c} strokeWidth="2.4" strokeLinecap="round" />
      <path d="M25 14l13 13h-6v13h-7V27h-5L25 14z" fill={GOOGLE.green} stroke={c} strokeWidth="2.4" {...STITCH} />
      <path d="M32 27h8" stroke={c} strokeWidth="1.8" />
      <path d="M25 22v7M40 33v4" stroke={c} strokeWidth="1.6" />
      <path d="M28 14h-3l1.5-4zM30 14h2l1 4h-6l1-4z" fill={GOOGLE.red} stroke={c} strokeWidth="1.6" {...STITCH} />
    </g>
  ),
  drum: (c, a) => (
    <g>
      <path d="M22 22c0-4.4 4.5-8 10-8s10 3.6 10 8-4.5 8-10 8-10-3.6-10-8z" fill={GOOGLE.yellow} stroke={c} strokeWidth="2.4" {...STITCH} />
      <path d="M22 22c0 4.4 4.5 8 10 8s10-3.6 10-8" fill="none" stroke={c} strokeWidth="2.4" />
      <path d="M24 32l-2 8c-1 2.2-1 4.2 2 5.5M40 32l2 8c1 2.2 1 4.2-2 5.5" stroke={c} strokeWidth="2.2" strokeLinecap="round" />
      <path d="M23 45h18" stroke={c} strokeWidth="2.4" strokeLinecap="round" />
      <path d="M27 33v6M32 33v7M37 33v6" stroke={c} strokeWidth="2" strokeLinecap="round" />
      <path d="M25 34l7 4 7-4M25 43l7 4 7-4" stroke={GOOGLE.red} strokeWidth="1.8" strokeLinecap="round" />
    </g>
  ),
  mask: (c, a) => (
    <g>
      <path d="M20 20c4-3.5 8-3.5 12 0 4-3.5 8-3.5 12 0 1.5 5.5 1.5 12.5 0 18-4 3.5-8 3.5-12 0-4 3.5-8 3.5-12 0-1.5-5.5-1.5-12.5 0-18z" fill={GOOGLE.blue} stroke={c} strokeWidth="2.4" {...STITCH} />
      <ellipse cx="26" cy="29" rx="3.4" ry="4.6" fill="#fff" stroke={c} strokeWidth="1.8" {...STITCH} />
      <ellipse cx="38" cy="29" rx="3.4" ry="4.6" fill="#fff" stroke={c} strokeWidth="1.8" {...STITCH} />
      <circle cx="26" cy="29" r="1.4" fill={c} />
      <circle cx="38" cy="29" r="1.4" fill={c} />
      <path d="M28 39c2.5 2 5.5 2 8 0" fill="none" stroke={GOOGLE.red} strokeWidth="2" strokeLinecap="round" />
      <path d="M20 19l-6-4M44 19l6-4" stroke={GOOGLE.green} strokeWidth="2" strokeLinecap="round" />
    </g>
  ),
  sun: (c, a) => (
    <g>
      <circle cx="32" cy="32" r="10" fill={GOOGLE.yellow} stroke={c} strokeWidth="2.6" {...STITCH} />
      {Array.from({ length: 12 }).map((_, i) => (
        <path key={i} d="M32 15v4M32 45v4M15 32h4M45 32h4" transform={`rotate(${i * 30} 32 32)`} stroke={c} strokeWidth="2.4" strokeLinecap="round" />
      ))}
      <path d="M27 30l5 5 8-8" fill="none" stroke={c} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </g>
  ),
  moon: (c, a) => (
    <g>
      <path d="M40 32c0-9-5.5-16-12.5-16 .6 9.8 5.4 16.4 12.5 16.4 2.7 0 5.1-.7 7-1.9C44.7 34.5 42.6 36.5 40 36.5z" fill={GOOGLE.yellow} stroke={c} strokeWidth="2.4" {...STITCH} />
      <path d="M42 15l1 2.2 2.2 1-2.2 1L42 21.4l-1-2.2-2.2-1 2.2-1z" fill={GOOGLE.blue} stroke={c} strokeWidth="1.4" {...STITCH} />
      <path d="M26 46h14l1.5 3h-17l1.5-3z" stroke={c} strokeWidth="1.8" fill="none" strokeLinejoin="round" />
      <Cross x="38" y="30" c={a} />
    </g>
  ),
  lotus: (c, a) => (
    <g>
      <path d="M32 21c-4-6-9-9-14-9 2 7 5 11 14 11z" fill={GOOGLE.red} stroke={c} strokeWidth="2.2" {...STITCH} />
      <path d="M32 21c4-6 9-9 14-9-2 7-5 11-14 11z" fill={GOOGLE.red} stroke={c} strokeWidth="2.2" {...STITCH} />
      <path d="M32 21c-3-4-7-6-11-6 1.5 5 4.5 8 11 8z" fill={GOOGLE.orange ?? "#F97316"} stroke={c} strokeWidth="1.8" {...STITCH} />
      <path d="M32 21c3-4 7-6 11-6-1.5 5-4.5 8-11 8z" fill={GOOGLE.orange ?? "#F97316"} stroke={c} strokeWidth="1.8" {...STITCH} />
      <path d="M32 25v15" stroke={c} strokeWidth="2.2" strokeLinecap="round" />
      <path d="M32 40c-3 0-6 3-6 6h12c0-3-3-6-6-6z" fill={GOOGLE.green} stroke={c} strokeWidth="2" {...STITCH} />
      <path d="M29 43l3 3 3-3" stroke="#fff" strokeWidth="1.6" strokeLinecap="round" />
    </g>
  ),
  conch: (c, a) => (
    <g>
      <path d="M24 17c9 1 15 6 15 15s-7 14-14 14c-4 0-7-2-7-5.5 0-2.6 2-4.5 4.5-4.5 3 0 5.5 2.5 5.5 5.5 0 3.4-2.8 6-6.5 6" fill="#fff" stroke={c} strokeWidth="2.4" {...STITCH} />
      <path d="M24 17c2 4 4 6 6 8M30 26c2 2 3 5 3 8M33 37c0 2-1 3-2 4" stroke={c} strokeWidth="1.8" strokeLinecap="round" />
      <path d="M18 46l-4 4" stroke={c} strokeWidth="2" strokeLinecap="round" />
      <path d="M28 20c-1.5 4-1.5 8 0 12" stroke={GOOGLE.green} strokeWidth="1.6" strokeLinecap="round" />
    </g>
  ),
  harvest: (c, a) => (
    <g>
      <path d="M32 17c-3-3-6-4-9-4l1.5 4L32 17z" fill={GOOGLE.green} stroke={c} strokeWidth="1.8" {...STITCH} />
      <path d="M32 17c3-3 6-4 9-4l-1.5 4L32 17z" fill={GOOGLE.green} stroke={c} strokeWidth="1.8" {...STITCH} />
      <path d="M32 17c-2.5-2.5-5-3.5-7.5-3.5l1.5 3.5L32 17z" fill={GOOGLE.green} stroke={c} strokeWidth="1.4" />
      <path d="M32 17c2.5-2.5 5-3.5 7.5-3.5L38 17l-6 0z" fill={GOOGLE.green} stroke={c} strokeWidth="1.4" />
      <path d="M30 19c-4.5-1.5-8.5-1.5-12 0 .5 4 2 7 5 9" stroke={c} strokeWidth="1.8" strokeLinecap="round" />
      <path d="M34 19c4.5-1.5 8.5-1.5 12 0-.5 4-2 7-5 9" stroke={c} strokeWidth="1.8" strokeLinecap="round" />
      <path d="M32 17V45" stroke={c} strokeWidth="2.4" strokeLinecap="round" />
      <path d="M22 45h20" stroke={c} strokeWidth="2.6" strokeLinecap="round" />
      <path d="M24 41h16l2 4h-20l2-4z" fill={GOOGLE.yellow} stroke={c} strokeWidth="1.8" {...STITCH} />
      <path d="M25 27l3 3M39 27l-3 3M24 33l4 2M40 33l-4 2" stroke={GOOGLE.yellow} strokeWidth="1.6" strokeLinecap="round" />
    </g>
  ),
  serpent: (c, a) => (
    <g>
      <path d="M19 19c8-5 17-5 25 0" fill="none" stroke={c} strokeWidth="2.4" strokeLinecap="round" />
      <path d="M19 19c-1.5 4-1.5 8 1 12" fill="none" stroke={c} strokeWidth="2.4" strokeLinecap="round" />
      <path d="M20 31c4 4 9 4 13 0" fill="none" stroke={c} strokeWidth="2.4" strokeLinecap="round" />
      <path d="M33 31c1 6-1 11-5 14" fill="none" stroke={c} strokeWidth="2.2" strokeLinecap="round" />
      <path d="M28 46l-4 3M28 46l3 4" stroke={c} strokeWidth="1.8" strokeLinecap="round" />
      <path d="M44 19v-3a3 3 0 0 1 3-3c0 4-1 6-3 6z" fill={GOOGLE.green} stroke={c} strokeWidth="1.6" {...STITCH} />
      <circle cx="44" cy="16" r="1.4" fill="#fff" />
      <path d="M21 20l3-2M24 24l3-1" stroke={a} strokeWidth="1.6" strokeLinecap="round" />
    </g>
  ),
  elephant: (c, a) => (
    <g>
      <path d="M22 30c0-8 4-13 10-13s10 5 10 13v11c0 2-1.5 3-3 3H25c-1.5 0-3-1-3-3V30z" fill="#C4CBD3" stroke={c} strokeWidth="2.4" {...STITCH} />
      <path d="M25 31h14M25 34h14M25 37h14" stroke={c} strokeWidth="1.8" />
      <path d="M32 17v4" stroke={c} strokeWidth="1.8" />
      <path d="M32 21l-3 3h6l-3-3z" fill={GOOGLE.red} stroke={c} strokeWidth="1.4" {...STITCH} />
      <path d="M25 37c-3 1-5 3-6 6" stroke={c} strokeWidth="2.2" strokeLinecap="round" />
      <path d="M22 31c-4 0-6 3-6 7 0 2 1 3 2 3" stroke={c} strokeWidth="2.2" strokeLinecap="round" />
      <circle cx="28.5" cy="25" r="1.3" fill={c} />
      <circle cx="35.5" cy="25" r="1.3" fill={c} />
      <path d="M22 44h20" stroke={GOOGLE.green} strokeWidth="1.8" strokeLinecap="round" strokeDasharray="2 3" />
    </g>
  ),
  camel: (c, a) => (
    <g>
      <path d="M24 30c0-7 4-12 9-14 1.5-.5 3 .5 3 2 0 2-1 3.5-2.5 4.5C34 21 35 18 36 16c4 2 6 6 6 10 0 3-1 5-3 7" fill="#E8B87A" stroke={c} strokeWidth="2.4" {...STITCH} />
      <path d="M36 25l-8 12v7c0 1-1 2-2 2s-2-1-2-2v-6l-5 4" fill="#E8B87A" stroke={c} strokeWidth="2.4" {...STITCH} />
      <path d="M24 41v5M36 38v5" stroke={c} strokeWidth="2.2" strokeLinecap="round" />
      <circle cx="40.5" cy="15.5" r="1.8" fill={c} />
      <path d="M27 32l6-6" stroke={c} strokeWidth="1.6" strokeLinecap="round" />
      <path d="M22 46c3 1.5 6 1.5 9 0" stroke={GOOGLE.red} strokeWidth="1.6" strokeLinecap="round" />
    </g>
  ),
  bird: (c, a) => (
    <g>
      <path d="M24 24c-4 2-6 6-6 10l8 4 8 3c4-1 7-4 8-9-4-2-8-4-12-6" fill={GOOGLE.blue} stroke={c} strokeWidth="2.4" {...STITCH} />
      <path d="M22 34l-4 6M24 36l-5 7" stroke={c} strokeWidth="2" strokeLinecap="round" />
      <path d="M27 22c-1 0-2-1-2-2s1-2 2-2 2 1 2 2-1 2-2 2z" fill={GOOGLE.yellow} stroke={c} strokeWidth="1.6" />
      <path d="M30 19l-3-2M30 19l3-2" stroke={c} strokeWidth="1.8" strokeLinecap="round" />
      <path d="M34 27l6-5" stroke={c} strokeWidth="1.8" strokeLinecap="round" />
      <path d="M24 28c3-1 6-1 9 0" stroke={c} strokeWidth="1.4" strokeDasharray="2 3" />
    </g>
  ),
  mountain: (c, a) => (
    <g>
      <path d="M14 42h36L38 20 33 28l-6-10-13 24z" fill={GOOGLE.green} stroke={c} strokeWidth="2.4" {...STITCH} />
      <path d="M33 28l5-8 8 14" fill="none" stroke={c} strokeWidth="1.8" />
      <path d="M38 20l-2 4M38 20l2 4" stroke="#fff" strokeWidth="2" strokeLinecap="round" />
      <path d="M22 40l4-6 3 3 3-3 3 3 3-3 2 6" fill="#fff" opacity="0.9" stroke={c} strokeWidth="1.4" {...STITCH} />
      <path d="M14 42h36" stroke={c} strokeWidth="1.8" strokeLinecap="round" />
      <Cross x="26" y="33" c={GOOGLE.blue} />
    </g>
  ),
  palm: (c, a) => (
    <g>
      <path d="M32 46V22" stroke={c} strokeWidth="2.6" strokeLinecap="round" />
      {[-38, -8, 22].map((deg) => (
        <path key={deg} d="M32 24c-4-3-7-8-8-13 5 1 8 4 8 8z" fill={GOOGLE.green} stroke={c} strokeWidth="1.8" {...STITCH} transform={`rotate(${deg} 32 24)`} />
      ))}
      <path d="M32 24c4-3 7-8 8-13-5 1-8 4-8 8z" fill={GOOGLE.green} stroke={c} strokeWidth="1.8" {...STITCH} transform="rotate(180 32 24)" />
      <circle cx="32" cy="19" r="3" fill={GOOGLE.orange ?? "#F97316"} stroke={c} strokeWidth="1.8" {...STITCH} />
      <path d="M24 49c3-2 5-2 8 0 3-2 5-2 8 0" stroke={c} strokeWidth="2.2" strokeLinecap="round" />
      <path d="M24 52c3-2 5-2 8 0 3-2 5-2 8 0" stroke={c} strokeWidth="2.2" strokeLinecap="round" />
    </g>
  ),
  umbrella: (c, a) => (
    <g>
      <path d="M14 28c0-10 8-18 18-18s18 8 18 18" fill="none" stroke={c} strokeWidth="2.6" strokeLinecap="round" />
      <path d="M14 28h36" stroke={c} strokeWidth="2.6" strokeLinecap="round" />
      <path d="M32 10v6" stroke={c} strokeWidth="2.4" strokeLinecap="round" />
      <path d="M17 28c5-4 10-4 15 0" stroke={GOOGLE.red} strokeWidth="1.8" fill="none" strokeLinecap="round" />
      <path d="M32 28c5-4 10-4 15 0" stroke={GOOGLE.blue} strokeWidth="1.8" fill="none" strokeLinecap="round" />
      <path d="M32 28v18" stroke={c} strokeWidth="2.4" strokeLinecap="round" />
      <path d="M24 35l-5 4M27 39l-5 4M40 35l5 4M37 39l5 4" stroke={GOOGLE.green} strokeWidth="2" strokeLinecap="round" />
    </g>
  ),
  bull: (c, a) => (
    <g>
      <path d="M24 30c0-8 3.5-12 8-12s8 4 8 12v9c0 2-1.5 3-3 3h-10c-1.5 0-3-1-3-3v-9z" fill="#E8B87A" stroke={c} strokeWidth="2.4" {...STITCH} />
      <path d="M24 30c-3 0-5 2-5 5 0 2 1 3 3 3h2M40 30c3 0 5 2 5 5 0 2-1 3-3 3h-2" stroke={c} strokeWidth="2.2" strokeLinecap="round" />
      <path d="M32 18l-3-5 2 3 1-4 1 4 2-3-3 5z" fill={GOOGLE.red} stroke={c} strokeWidth="1.4" {...STITCH} />
      <path d="M28 27h8M28 31h8M28 35h8" stroke={c} strokeWidth="1.8" />
      <circle cx="29.5" cy="22" r="1.2" fill={c} />
      <circle cx="34.5" cy="22" r="1.2" fill={c} />
      <path d="M22 45h20" stroke={GOOGLE.green} strokeWidth="1.6" strokeLinecap="round" strokeDasharray="2 3" />
    </g>
  ),
  trishul: (c, a) => (
    <g>
      <path d="M32 46V18" stroke={c} strokeWidth="2.6" strokeLinecap="round" />
      <path d="M32 18l-8-7M32 18l8-7M32 18l-9 1 9-5 9-1-9 5z" fill={GOOGLE.yellow} stroke={c} strokeWidth="2" {...STITCH} />
      <path d="M32 27c-3.5 0-6-2.5-6-6 0-2.5 2.5-4.5 6-4.5s6 2 6 4.5c0 3.5-2.5 6-6 6z" fill="none" stroke={c} strokeWidth="1.8" strokeDasharray="3 3" />
      <path d="M27 38l5 4 5-4M27 42l5 4 5-4" stroke={GOOGLE.red} strokeWidth="1.8" strokeLinecap="round" />
      <path d="M27 33l-3 4M37 33l3 4" stroke={GOOGLE.green} strokeWidth="1.8" strokeLinecap="round" />
    </g>
  ),
  thread: (c, a) => (
    <g>
      <circle cx="32" cy="32" r="14" fill={GOOGLE.yellow} stroke={c} strokeWidth="2.6" {...STITCH} />
      <path d="M32 18v28M18 32h28" stroke={c} strokeWidth="1.4" opacity="0.6" />
      <path d="M25 25c5-5 9-5 14 0M39 39c-5 5-9 5-14 0M39 25c-5-5-9-5-14 0M25 39c5 5 9 5 14 0" stroke={GOOGLE.red} strokeWidth="2" strokeLinecap="round" />
      <circle cx="32" cy="32" r="3.4" fill={GOOGLE.blue} stroke={c} strokeWidth="1.6" {...STITCH} />
    </g>
  ),
};

const REGION_GROUP_MOTIF: Record<string, MotifId> = {
  North: "mountain",
  South: "temple",
  East: "lotus",
  West: "sun",
  Central: "sun",
  Northeast: "bird",
  Islands: "palm",
};

const REGION_SPECIAL: Record<string, MotifId> = {
  "karnataka": "elephant",
  "kerala": "boat",
  "tamil-nadu": "temple",
  "andhra-pradesh": "temple",
  "telangana": "flower",
  "gujarat": "kite",
  "punjab": "harvest",
  "rajasthan": "camel",
  "maharashtra": "drum",
  "west-bengal": "conch",
  "odisha": "chariot",
  "assam": "bird",
  "nagaland": "bird",
  "arunachal-pradesh": "mask",
  "chhattisgarh": "mask",
  "manipur": "drum",
  "mizoram": "drum",
  "jharkhand": "drum",
  "meghalaya": "umbrella",
  "sikkim": "mountain",
  "himachal-pradesh": "mountain",
  "uttarakhand": "mountain",
  "jammu-and-kashmir": "mountain",
  "ladakh": "mountain",
  "delhi": "lotus",
  "bihar": "lotus",
  "uttar-pradesh": "chariot",
  "madhya-pradesh": "sun",
  "haryana": "harvest",
  "goa": "palm",
  "andaman-and-nicobar": "palm",
  "lakshadweep": "palm",
  "dadra-nagar-haveli-daman-diu": "palm",
  "puducherry": "sun",
  "chandigarh": "flower",
};

const FESTIVAL_RULES: [RegExp, MotifId][] = [
  [/(diya|deepam|karthigai|diwali|lights|dev deepavali|dipavali)/i, "diya"],
  [/(kite|uttarayan)/i, "kite"],
  [/(onam|boat|vallam)/i, "boat"],
  [/(temple|brahmotsavam|kalyanotsavam|gopuram|puri|ratha)/i, "temple"],
  [/(chariot|rath yatra|rath)/i, "chariot"],
  [/(drum|dhol|dance|music|sangeet|carnival|garba|dandiya|dance fest)/i, "drum"],
  [/(mask|theyyam|theatre|kuttiyattam|masked)/i, "mask"],
  [/(bonfire|lohri|holika|dahan|fire)/i, "fire"],
  [/(harvest|crop|grain|baisakhi|sankranti|pongal|bihu|nuakhai|raja parba|sugarcane)/i, "harvest"],
  [/(cattle|cow|bull|pola)/i, "bull"],
  [/(flower|floral|bathukamma|tulip|rose|bloom)/i, "flower"],
  [/(snake|serpent|nagula|nag)/i, "serpent"],
  [/(sun|solar|surya|uttarayani)/i, "sun"],
  [/(moon|crescent|eid|chauth|shab)/i, "moon"],
  [/(elephant|dasara|jumbo|gaja)/i, "elephant"],
  [/(camel|desert)/i, "camel"],
  [/(hornbill|bird)/i, "bird"],
  [/(mountain|losar|saga|hemis|galdan|gustor|shivratri)/i, "mountain"],
  [/(coconut|nariyal|palm|island|sea)/i, "palm"],
  [/(conch|shankh|durga|kali|ganga|devi|puja)/i, "conch"],
  [/(lotus|buddha|dhamma|poornima)/i, "lotus"],
  [/(lantern|christmas|carol|new year)/i, "lantern"],
  [/(shiva|shivratri|trishul|gangasagar)/i, "trishul"],
  [/(rakhi|raksha|thread)/i, "thread"],
  [/(candle|candlelight)/i, "candle"],
  [/(marigold)/i, "marigold"],
  [/(peacock|mor)/i, "peacock"],
];

function hashNum(s: string): number {
  let h = 0;
  for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) >>> 0;
  return h;
}

export function motifForFestival(name: string, description: string, fallback: MotifId = "flower"): MotifId {
  for (const [re, m] of FESTIVAL_RULES) {
    if (re.test(name) || re.test(description)) return m;
  }
  return fallback;
}

export function motifForRegion(slug: string, regionGroup: string): MotifId {
  return REGION_SPECIAL[slug] ?? REGION_GROUP_MOTIF[regionGroup] ?? "flower";
}

export function Artwork({
  motif,
  seed,
  className,
}: {
  motif: MotifId;
  seed: string;
  className?: string;
}) {
  const bg = PATCH_BGS[hashNum(seed) % PATCH_BGS.length];
  return (
    <svg viewBox="0 0 64 64" className={className} aria-hidden="true">
      <circle cx="32" cy="32" r="31" fill={GOOGLE.cream} />
      <circle cx="32" cy="32" r="31" fill={bg} />
      <Ring color={GOOGLE.ink} />
      {MOTIFS[motif](GOOGLE.ink, GOOGLE.red)}
    </svg>
  );
}

// ---------------------------------------------------------------------------
// Real state outlines (from @react-map/india, MIT) with unique per-state color
// ---------------------------------------------------------------------------

export function stateColor(slug: string): string {
  return STATE_SHAPES[slug]?.color ?? "#ea580c";
}

export function tintColor(hex: string, amount = 0.86): string {
  const n = parseInt(hex.slice(1), 16);
  const r = (n >> 16) & 255;
  const g = (n >> 8) & 255;
  const b = n & 255;
  const mix = (c: number) => Math.round(c + (255 - c) * amount);
  return `#${((1 << 24) + (mix(r) << 16) + (mix(g) << 8) + mix(b)).toString(16).slice(1)}`;
}

function darkenColor(hex: string, amount = 0.2): string {
  const n = parseInt(hex.slice(1), 16);
  const r = (n >> 16) & 255;
  const g = (n >> 8) & 255;
  const b = n & 255;
  const mix = (c: number) => Math.round(c * (1 - amount));
  return `#${((1 << 24) + (mix(r) << 16) + (mix(g) << 8) + mix(b)).toString(16).slice(1)}`;
}

let gradientSeq = 0;

export function StateOutline({
  slug,
  className,
}: {
  slug: string;
  className?: string;
}) {
  const s = STATE_SHAPES[slug];
  if (!s) return null;
  const m = Math.max(s.w, s.h);
  const sw = m / 100;
  const gradientId = `sg-${gradientSeq++}`;
  return (
    <svg
      viewBox={`${s.x} ${s.y} ${s.w} ${s.h}`}
      className={className}
      aria-hidden="true"
      preserveAspectRatio="xMidYMid meet"
    >
      <defs>
        <linearGradient id={gradientId} x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor={s.color} />
          <stop offset="1" stopColor={darkenColor(s.color)} />
        </linearGradient>
      </defs>
      <path
        d={s.path}
        fill={`url(#${gradientId})`}
        fillOpacity="0.92"
        stroke="#292524"
        strokeWidth={sw}
        strokeLinejoin="round"
        strokeLinecap="round"
        strokeDasharray={`${sw * 2.4} ${sw * 2.4}`}
      />
    </svg>
  );
}

export function FestivalArt({
  stateSlug,
  className,
}: {
  name: string;
  description: string;
  slug: string;
  stateSlug?: string | null;
  className?: string;
}) {
  return <StateOutline slug={stateSlug ?? "india"} className={className} />;
}

export function RegionArt({
  slug,
  className,
}: {
  name: string;
  slug: string;
  regionGroup: string;
  className?: string;
}) {
  return <StateOutline slug={slug} className={className} />;
}

const CATEGORY_MOTIFS: Record<string, MotifId> = {
  pooja: "diya",
  decor: "lantern",
  sweets: "harvest",
  clothing: "thread",
  gifts: "candle",
  handicrafts: "mask",
  jewellery: "flower",
  home: "fire",
};

export function CategoryArt({
  slug,
  className,
}: {
  slug: string;
  className?: string;
}) {
  return <Artwork motif={CATEGORY_MOTIFS[slug] ?? "flower"} seed={slug} className={className} />;
}
