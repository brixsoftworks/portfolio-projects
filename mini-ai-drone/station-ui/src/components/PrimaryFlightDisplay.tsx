import React from 'react';
import { DroneTelemetry } from '../types';

interface PFDProps {
  telemetry: DroneTelemetry;
}

export const PrimaryFlightDisplay: React.FC<PFDProps> = ({ telemetry }) => {
  const { pitch, roll, yaw, speed, rel_alt, climb_rate, bearing_home } = telemetry;

  // Sliding compass calculations
  const compassWidth = 340;
  const degPerPx = 75 / compassWidth;
  const headingDiffHome = ((bearing_home - yaw + 180) % 360) - 180;
  const homeMarkerOffset = Math.max(-compassWidth / 2 + 15, Math.min(compassWidth / 2 - 15, headingDiffHome / degPerPx));

  return (
    <div className="absolute inset-0 pointer-events-none z-10 flex flex-col justify-between">
      
      {/* 1. Top 360° Sliding Compass Ribbon */}
      <div className="flex justify-center pt-1">
        <div className="relative w-[340px] h-7 bg-[#0b0f17]/85 backdrop-blur-md rounded-xl border border-white/10 shadow-[0_4px_16px_rgba(0,0,0,0.5)] overflow-hidden">
          {/* Compass Strip Center Indicator */}
          <div className="absolute top-0 bottom-0 left-1/2 -translate-x-1/2 w-[2px] bg-cyan-400 z-10 shadow-[0_0_6px_#00f2fe]" />
          
          {/* Degree readouts */}
          <svg className="w-full h-full">
            {Array.from({ length: 91 }, (_, i) => {
              const deg = Math.floor(yaw - 45) + i;
              const normalizedDeg = (deg + 360) % 360;
              const x = (deg - yaw) / degPerPx + compassWidth / 2;

              if (x < 0 || x > compassWidth) return null;

              if (normalizedDeg % 15 === 0) {
                let label = '';
                if (normalizedDeg === 0) label = 'N';
                else if (normalizedDeg === 45) label = 'NE';
                else if (normalizedDeg === 90) label = 'E';
                else if (normalizedDeg === 135) label = 'SE';
                else if (normalizedDeg === 180) label = 'S';
                else if (normalizedDeg === 225) label = 'SW';
                else if (normalizedDeg === 270) label = 'W';
                else if (normalizedDeg === 315) label = 'NW';
                else label = `${normalizedDeg}°`;

                return (
                  <g key={deg}>
                    <line x1={x} y1={20} x2={x} y2={28} stroke="#94a3b8" strokeWidth={1} />
                    <text
                      x={x}
                      y={14}
                      fill={label === 'N' ? '#00f2fe' : '#cbd5e1'}
                      fontSize={9}
                      fontFamily="monospace"
                      fontWeight={label.length <= 2 ? 'bold' : 'normal'}
                      textAnchor="middle"
                    >
                      {label}
                    </text>
                  </g>
                );
              }
              return null;
            })}
          </svg>

          {/* Dynamic Home Point [H] Beacon */}
          <div
            className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-4 h-4 rounded-full bg-amber-400/90 text-black font-extrabold text-[9px] flex items-center justify-center shadow-[0_0_8px_#f59e0b] border border-black/40"
            style={{ left: `${compassWidth / 2 + homeMarkerOffset}px` }}
            title={`Bearing to Home: ${bearing_home.toFixed(0)}°`}
          >
            H
          </div>

          {/* Heading Numerical Value */}
          <div className="absolute bottom-0.5 right-2 text-[9px] font-mono text-cyan-400 font-bold">
            {Math.round(yaw).toString().padStart(3, '0')}°
          </div>
        </div>
      </div>

      {/* 2. Center Primary Flight Display (Artificial Horizon) */}
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="relative w-72 h-72">
          {/* Pitch Ladder & Roll Arc (Rotates with Aircraft Roll) */}
          <svg
            className="w-full h-full overflow-visible transition-transform duration-75"
            style={{ transform: `rotate(${-roll}deg)` }}
          >
            <g transform={`translate(0, ${pitch * 2.8})`}>
              {/* Roll Angle Arc */}
              <path
                d="M 66 144 A 78 78 0 0 1 222 144"
                fill="none"
                stroke="rgba(255, 255, 255, 0.2)"
                strokeWidth="1.5"
                strokeDasharray="4,4"
              />

              {/* Pitch Ladder Lines (+20, +10, 0, -10, -20) */}
              {[-20, -10, 10, 20].map((p) => {
                const y = 144 - p * 3.2;
                const width = Math.abs(p) === 10 ? 46 : 30;
                return (
                  <g key={p}>
                    <line
                      x1={144 - width}
                      y1={y}
                      x2={144 + width}
                      y2={y}
                      stroke="#00f2fe"
                      strokeWidth={1.5}
                      strokeOpacity={0.8}
                    />
                    <text
                      x={144 + width + 5}
                      y={y + 3}
                      fill="#00f2fe"
                      fontSize={8}
                      fontFamily="monospace"
                      opacity={0.8}
                    >
                      {Math.abs(p)}
                    </text>
                  </g>
                );
              })}
            </g>
          </svg>

          {/* Aircraft Fixed Reference Symbol (Yellow Crosshair Brackets) */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="relative w-20 h-6 flex items-center justify-between">
              <div className="w-6 h-[2px] bg-amber-400 shadow-[0_0_6px_#f59e0b] relative">
                <div className="absolute right-0 top-0 w-[2px] h-2 bg-amber-400" />
              </div>
              <div className="w-1.5 h-1.5 rounded-full bg-amber-400 shadow-[0_0_6px_#f59e0b]" />
              <div className="w-6 h-[2px] bg-amber-400 shadow-[0_0_6px_#f59e0b] relative">
                <div className="absolute left-0 top-0 w-[2px] h-2 bg-amber-400" />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 3. Left Speed Tape & Right Altitude Tape */}
      <div className="px-6 flex justify-between items-center my-auto w-full">
        {/* Left: Airspeed Tape (m/s) */}
        <div className="relative w-12 h-56 bg-[#0b0f17]/85 backdrop-blur-md rounded-xl border border-white/10 flex flex-col justify-between p-1 shadow-[0_4px_16px_rgba(0,0,0,0.5)]">
          <span className="text-[8px] font-mono text-slate-400 text-center font-bold">SPD</span>
          
          {/* Central Speed Pointer Box */}
          <div className="my-auto py-1 px-1 bg-cyan-500/20 border border-cyan-400/60 rounded-md text-center shadow-[0_0_10px_rgba(6,182,212,0.3)]">
            <span className="text-[12px] font-mono font-extrabold text-cyan-300">
              {speed.toFixed(1)}
            </span>
            <span className="text-[7px] font-mono block text-cyan-400/80 -mt-0.5">m/s</span>
          </div>

          <div className="text-[7px] font-mono text-slate-500 text-center">GND</div>
        </div>

        {/* Right: Altitude Tape (m AGL & Vz) */}
        <div className="relative w-14 h-56 bg-[#0b0f17]/85 backdrop-blur-md rounded-xl border border-white/10 flex flex-col justify-between p-1 shadow-[0_4px_16px_rgba(0,0,0,0.5)]">
          <span className="text-[8px] font-mono text-slate-400 text-center font-bold">ALT</span>
          
          {/* Central Altitude Pointer Box */}
          <div className="my-auto py-1 px-1 bg-emerald-500/20 border border-emerald-400/60 rounded-md text-center shadow-[0_0_10px_rgba(16,185,129,0.3)]">
            <span className="text-[12px] font-mono font-extrabold text-emerald-300">
              {rel_alt.toFixed(1)}
            </span>
            <span className="text-[7px] font-mono block text-emerald-400/80 -mt-0.5">m AGL</span>
          </div>

          <div className="text-[7px] font-mono text-emerald-400 text-center">
            Vz:{climb_rate > 0 ? `+${climb_rate.toFixed(1)}` : climb_rate.toFixed(1)}
          </div>
        </div>
      </div>

    </div>
  );
};
