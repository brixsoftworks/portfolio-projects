import React from 'react';
import { DroneTelemetry } from '../types';
import { AlertTriangle, Crosshair } from 'lucide-react';

interface CameraFeedProps {
  telemetry: DroneTelemetry;
  className?: string;
}

export const CameraFeed: React.FC<CameraFeedProps> = ({ telemetry, className = '' }) => {
  const { detections, wire_hazard, landing_safe, roughness, fov_zoom, clarity_boost, thermal_mode } = telemetry;
  // Ensure the live view is always big and full-screen (never shrunk below 1.0x)
  const zoomScale = Math.max(1.0, fov_zoom || 1.0);

  return (
    <div className={`relative w-full h-full bg-[#05070a] overflow-hidden flex items-center justify-center ${className}`}>
      
      {/* 1. Full-Bleed Video Element / Stream Frame */}
      <div 
        className="relative w-full h-full flex items-center justify-center transition-all duration-300"
        style={{
          transform: `scale(${zoomScale})`,
          filter: `
            ${clarity_boost ? 'contrast(1.25) saturate(1.15) brightness(1.05)' : ''}
            ${thermal_mode ? 'hue-rotate(180deg) invert(1) contrast(1.5)' : ''}
          `
        }}
      >
        <img
          src="/api/video_feed"
          alt="MINI Drone Cockpit View"
          className="w-full h-full object-cover select-none pointer-events-none"
          onError={(e) => {
            const target = e.target as HTMLImageElement;
            setTimeout(() => {
              target.src = `/api/video_feed?t=${Date.now()}`;
            }, 800);
          }}
        />

        {/* 2. SVG AI Object Detection Bounding Boxes & Photogrammetry */}
        <svg className="absolute inset-0 w-full h-full pointer-events-none overflow-visible">
          {detections && detections.map((obj) => {
            const [x1, y1, x2, y2] = obj.box;
            const w = x2 - x1;
            const h = y2 - y1;
            const isPerson = obj.label === 'person';
            const color = isPerson ? '#00f5a0' : '#00f2fe';

            return (
              <g key={obj.id} className="transition-all duration-100">
                {/* Outer Bounding Box */}
                <rect
                  x={`${x1 * 100}%`}
                  y={`${y1 * 100}%`}
                  width={`${w * 100}%`}
                  height={`${h * 100}%`}
                  fill="none"
                  stroke={color}
                  strokeWidth="1.5"
                  strokeDasharray={isPerson ? 'none' : '4, 4'}
                  className="filter drop-shadow-[0_0_8px_rgba(0,245,160,0.4)]"
                />

                {/* Target Corners */}
                <path
                  d={`
                    M ${x1 * 100 - 1}% ${y1 * 100 + 3}% L ${x1 * 100 - 1}% ${y1 * 100 - 1}% L ${x1 * 100 + 3}% ${y1 * 100 - 1}%
                    M ${x2 * 100 + 1}% ${y1 * 100 + 3}% L ${x2 * 100 + 1}% ${y1 * 100 - 1}% L ${x2 * 100 - 3}% ${y1 * 100 - 1}%
                  `}
                  stroke={color}
                  strokeWidth="2"
                  fill="none"
                />

                {/* Metric Dimensions HUD Tag */}
                <foreignObject
                  x={`${x1 * 100}%`}
                  y={`${Math.max(0, y1 * 100 - 5)}%`}
                  width="220"
                  height="24"
                >
                  <div 
                    className="px-1.5 py-0.5 rounded text-[8px] font-mono font-bold tracking-wider uppercase inline-block border backdrop-blur-md shadow-lg"
                    style={{ 
                      backgroundColor: 'rgba(11, 15, 23, 0.85)', 
                      borderColor: color, 
                      color: color 
                    }}
                  >
                    [{obj.label.toUpperCase()} | {obj.dist_m.toFixed(1)}m | {obj.width_m.toFixed(2)}x{obj.height_m.toFixed(2)}m | {obj.area_sq_m.toFixed(2)}m²]
                  </div>
                </foreignObject>
              </g>
            );
          })}
        </svg>

        {/* Center Optical Reticle */}
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="relative w-8 h-8 rounded-full border border-cyan-400/40 flex items-center justify-center">
            <div className="w-1.5 h-1.5 rounded-full bg-cyan-400 shadow-[0_0_8px_#00f2fe]" />
            <div className="absolute top-0 bottom-0 w-[1px] bg-cyan-400/30" />
            <div className="absolute left-0 right-0 h-[1px] bg-cyan-400/30" />
          </div>
        </div>
      </div>

      {/* 3. APAS Hazard Warning Banner */}
      {wire_hazard && (
        <div className="absolute top-16 left-1/2 -translate-x-1/2 z-20 px-6 py-2 bg-rose-600/90 text-white font-mono font-bold text-xs rounded-xl border border-rose-400 shadow-[0_0_25px_rgba(225,29,72,0.8)] animate-bounce flex items-center space-x-2">
          <AlertTriangle className="w-4 h-4 text-white animate-spin" />
          <span>! APAS 5.0 ALERT: THIN WIRE / OBSTACLE HAZARD DETECTED !</span>
        </div>
      )}

      {/* 4. Landing Matrix Status Badge */}
      <div className="absolute bottom-16 left-1/2 -translate-x-1/2 z-20 px-3.5 py-1 bg-[#0b0f17]/90 backdrop-blur-md rounded-xl border border-white/10 text-[10px] font-mono shadow-xl flex items-center space-x-2">
        <span 
          className={`w-2 h-2 rounded-full ${landing_safe ? 'bg-emerald-400 shadow-[0_0_8px_#10b981]' : 'bg-rose-500 shadow-[0_0_8px_#f43f5e]'}`} 
        />
        <span className={landing_safe ? 'text-emerald-300' : 'text-rose-400 font-bold'}>
          LANDING MATRIX: {landing_safe ? 'SAFE (FLAT)' : 'HAZARDOUS (UNEVEN)'}
        </span>
        <span className="text-slate-500">|</span>
        <span className="text-slate-400">ROUGHNESS: {roughness.toFixed(3)}</span>
      </div>

    </div>
  );
};
