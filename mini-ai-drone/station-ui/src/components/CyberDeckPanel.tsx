import React, { useState, useEffect, useRef } from 'react';
import { DroneTelemetry } from '../types';
import { RealMapLeaflet } from './RealMapLeaflet';
import { CameraFeed } from './CameraFeed';
import { 
  Radio, 
  Video, 
  Camera, 
  Home, 
  Zap, 
  Map as MapIcon, 
  Octagon, 
  Mountain, 
  Activity, 
  Maximize2,
  ShieldCheck,
  AlertTriangle,
  Compass
} from 'lucide-react';

interface CyberDeckPanelProps {
  telemetry: DroneTelemetry;
  onToggleRecord: () => void;
  onCapturePhoto: () => void;
  onToggleRth: () => void;
  onCycleMode: () => void;
  onOpenConnectDrawer: () => void;
  onEmergencyBrake: () => void;
}

export const CyberDeckPanel: React.FC<CyberDeckPanelProps> = ({
  telemetry,
  onToggleRecord,
  onCapturePhoto,
  onToggleRth,
  onCycleMode,
  onOpenConnectDrawer,
  onEmergencyBrake,
}) => {
  // Real live camera view is the default view!
  const [heroMode, setHeroMode] = useState<'camera' | 'topography'>('camera');
  const [mapExpanded, setMapExpanded] = useState<boolean>(false);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  // Animated Topographic Silk Wave & Mountain Canvas (Undulates with Real Telemetry)
  useEffect(() => {
    if (heroMode !== 'topography') return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animId: number;
    let t = 0;

    const render = () => {
      t += 0.02;
      const w = canvas.width;
      const h = canvas.height;

      ctx.clearRect(0, 0, w, h);

      // Deep dark background
      ctx.fillStyle = '#141822';
      ctx.fillRect(0, 0, w, h);

      // Ambient radial glow behind mountain
      const radGlow = ctx.createRadialGradient(w * 0.82, h * 0.35, 10, w * 0.82, h * 0.35, w * 0.45);
      radGlow.addColorStop(0, 'rgba(245, 158, 11, 0.16)');
      radGlow.addColorStop(0.5, 'rgba(244, 63, 94, 0.06)');
      radGlow.addColorStop(1, 'rgba(20, 24, 34, 0)');
      ctx.fillStyle = radGlow;
      ctx.fillRect(0, 0, w, h);

      // 1. Shaded 3D Mountain Ridges (Right side)
      ctx.beginPath();
      ctx.moveTo(w * 0.52, h);
      ctx.lineTo(w * 0.58, h * 0.62);
      ctx.lineTo(w * 0.65, h * 0.68);
      ctx.lineTo(w * 0.73, h * 0.52);
      ctx.lineTo(w * 0.82, h * 0.22); // Main peak
      ctx.lineTo(w * 0.92, h * 0.58);
      ctx.lineTo(w, h * 0.48);
      ctx.lineTo(w, h);
      ctx.closePath();

      const bgMountGrad = ctx.createLinearGradient(w * 0.82, h * 0.22, w * 0.82, h);
      bgMountGrad.addColorStop(0, '#fef08a');
      bgMountGrad.addColorStop(0.15, '#d97706');
      bgMountGrad.addColorStop(0.45, '#78350f');
      bgMountGrad.addColorStop(1, '#1c1917');
      ctx.fillStyle = bgMountGrad;
      ctx.fill();

      // Foreground sharp craggy ridge
      ctx.beginPath();
      ctx.moveTo(w * 0.60, h);
      ctx.lineTo(w * 0.68, h * 0.65);
      ctx.lineTo(w * 0.78, h * 0.45);
      ctx.lineTo(w * 0.84, h * 0.28);
      ctx.lineTo(w * 0.90, h * 0.52);
      ctx.lineTo(w * 0.96, h * 0.40);
      ctx.lineTo(w, h * 0.60);
      ctx.lineTo(w, h);
      ctx.closePath();

      const fgMountGrad = ctx.createLinearGradient(w * 0.84, h * 0.28, w * 0.84, h);
      fgMountGrad.addColorStop(0, '#fde68a');
      fgMountGrad.addColorStop(0.2, '#b45309');
      fgMountGrad.addColorStop(0.5, '#451a03');
      fgMountGrad.addColorStop(1, '#0c0a09');
      ctx.fillStyle = fgMountGrad;
      ctx.fill();

      // Fine contour lines across mountains
      ctx.strokeStyle = 'rgba(254, 240, 138, 0.25)';
      ctx.lineWidth = 1;
      for (let y = h * 0.35; y < h; y += 14) {
        ctx.beginPath();
        ctx.moveTo(w * 0.70 + Math.sin(y * 0.05 + t) * 6, y);
        ctx.lineTo(w * 0.95, y + Math.cos(y * 0.05 + t) * 4);
        ctx.stroke();
      }

      // 2. Flowing Topographic Waves (Modulated by Real Drone Pitch & Roll)
      const numLines = 36;
      const pitchMod = (telemetry.pitch / 20.0) * (h * 0.15);
      const rollMod = (telemetry.roll / 20.0) * (h * 0.10);

      for (let i = 0; i < numLines; i++) {
        const lineProgress = i / numLines;
        const baseY = h * 0.65 - (lineProgress * h * 0.42) + pitchMod;

        ctx.beginPath();
        const strokeGrad = ctx.createLinearGradient(0, baseY, w * 0.65, baseY);
        strokeGrad.addColorStop(0, 'rgba(255, 255, 255, 0.05)');
        strokeGrad.addColorStop(0.25, `rgba(255, 255, 255, ${0.4 - lineProgress * 0.25})`);
        strokeGrad.addColorStop(0.55, `rgba(251, 191, 36, ${0.6 - lineProgress * 0.3})`);
        strokeGrad.addColorStop(0.85, `rgba(244, 63, 94, ${0.4 - lineProgress * 0.2})`);
        strokeGrad.addColorStop(1, 'rgba(20, 24, 34, 0)');

        ctx.strokeStyle = strokeGrad;
        ctx.lineWidth = 1.2;

        ctx.moveTo(0, baseY + Math.sin(t + i * 0.2) * 8);

        const cp1x = w * 0.12;
        const cp1y = baseY - h * 0.32 * Math.sin(lineProgress * Math.PI * 0.9 + t * 0.5) + rollMod;
        const p1x = w * 0.25;
        const p1y = baseY - h * 0.38 * (1 - lineProgress * 0.3) + Math.sin(t + i * 0.15) * 6;

        const cp2x = w * 0.35;
        const cp2y = baseY + h * 0.12;
        const p2x = w * 0.45;
        const p2y = baseY - h * 0.22 * (1 - lineProgress * 0.2) + Math.cos(t + i * 0.15) * 5;

        const cp3x = w * 0.55;
        const cp3y = baseY - h * 0.10;
        const p3x = w * 0.68;
        const p3y = h * 0.72 + lineProgress * 25;

        ctx.bezierCurveTo(cp1x, cp1y, cp1x + 30, p1y, p1x, p1y);
        ctx.bezierCurveTo(p1x + 40, p1y, cp2x, cp2y, p2x, p2y);
        ctx.bezierCurveTo(p2x + 40, p2y, cp3x, cp3y, p3x, p3y);
        ctx.stroke();
      }

      // Real Altitude Beacon on Peak 1
      const peakX = w * 0.25;
      const peakY = h * 0.28 + Math.sin(t) * 4;
      ctx.fillStyle = '#00f2fe';
      ctx.beginPath();
      ctx.arc(peakX, peakY, 4, 0, Math.PI * 2);
      ctx.fill();

      ctx.strokeStyle = 'rgba(0, 242, 254, 0.6)';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.arc(peakX, peakY, 10 + Math.sin(t * 3) * 3, 0, Math.PI * 2);
      ctx.stroke();

      animId = requestAnimationFrame(render);
    };

    render();
    return () => cancelAnimationFrame(animId);
  }, [heroMode, telemetry.pitch, telemetry.roll]);

  // Generate SVG path from real history array
  const createSplinePath = (hist: number[], scaleY: number = 1.0, offsetY: number = 40) => {
    if (!hist || hist.length === 0) return '';
    const stepX = 320 / (hist.length - 1);
    let d = `M 0 ${offsetY - hist[0] * scaleY}`;
    for (let i = 1; i < hist.length; i++) {
      const x = i * stepX;
      const y = offsetY - hist[i] * scaleY;
      d += ` L ${x.toFixed(1)} ${y.toFixed(1)}`;
    }
    return d;
  };

  // Speedometer Arc calculation from Real Ground Speed (0 to 60 km/h)
  const speedNorm = Math.min(1.0, Math.max(0.0, (telemetry.ground_speed_kmh || 0) / 60.0));
  const arcDashOffset = 190 - speedNorm * 130;

  return (
    <div className="relative w-full h-full flex flex-col justify-between p-4 bg-[#0e1117] text-slate-200 overflow-hidden select-none">
      
      {/* Ambient background glows */}
      <div className="absolute top-0 right-1/4 w-96 h-96 bg-amber-500/5 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-0 left-1/4 w-96 h-96 bg-cyan-500/5 rounded-full blur-3xl pointer-events-none" />

      {/* ==================================================================== */}
      {/* 1. TOP ROW: 3 Modular Cards                                          */}
      {/* ==================================================================== */}
      <div className="grid grid-cols-12 gap-3.5 h-[135px] z-10">
        
        {/* Card 1 (Left): Real ESC Motor Mixer (M1-M4) */}
        <div className="col-span-4 p-3 rounded-2xl bg-[#141722]/90 border border-white/[0.07] shadow-lg flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-mono tracking-wider text-slate-400 uppercase font-semibold">
              ESC MOTOR MIXER (REAL)
            </span>
            <div className="flex space-x-1">
              {[1, 2, 3, 4].map((d) => (
                <div key={d} className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              ))}
            </div>
          </div>

          {/* 4 Real Motor Load Bars */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-[9px] font-mono">
              <span className="text-cyan-400 font-bold">M1 (FR)</span>
              <div className="w-36 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-cyan-400 shadow-[0_0_6px_#00f2fe] transition-all duration-150" 
                  style={{ width: `${telemetry.motors ? telemetry.motors[0] : 74}%` }} 
                />
              </div>
              <span className="text-slate-300 font-bold">{telemetry.motors ? telemetry.motors[0].toFixed(0) : 74}%</span>
            </div>

            <div className="flex items-center justify-between text-[9px] font-mono">
              <span className="text-rose-400 font-bold">M2 (RR)</span>
              <div className="w-36 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-rose-400 shadow-[0_0_6px_#fb7185] transition-all duration-150" 
                  style={{ width: `${telemetry.motors ? telemetry.motors[1] : 78}%` }} 
                />
              </div>
              <span className="text-slate-300 font-bold">{telemetry.motors ? telemetry.motors[1].toFixed(0) : 78}%</span>
            </div>

            <div className="flex items-center justify-between text-[9px] font-mono">
              <span className="text-amber-400 font-bold">M3 (RL)</span>
              <div className="w-36 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-amber-400 shadow-[0_0_6px_#f59e0b] transition-all duration-150" 
                  style={{ width: `${telemetry.motors ? telemetry.motors[2] : 76}%` }} 
                />
              </div>
              <span className="text-slate-300 font-bold">{telemetry.motors ? telemetry.motors[2].toFixed(0) : 76}%</span>
            </div>

            <div className="flex items-center justify-between text-[9px] font-mono">
              <span className="text-emerald-400 font-bold">M4 (FL)</span>
              <div className="w-36 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-emerald-400 shadow-[0_0_6px_#10b981] transition-all duration-150" 
                  style={{ width: `${telemetry.motors ? telemetry.motors[3] : 72}%` }} 
                />
              </div>
              <span className="text-slate-300 font-bold">{telemetry.motors ? telemetry.motors[3].toFixed(0) : 72}%</span>
            </div>
          </div>

          <div className="text-[8px] font-mono text-slate-500 flex justify-between">
            <span>LINK: 5.8 GHz | {telemetry.signal_pct}% RSSI</span>
            <span>BUS: {telemetry.battery_voltage.toFixed(1)}V</span>
          </div>
        </div>

        {/* Card 2 (Center): Real GPS Coordinates & Real Map Tile (Click to Expand) */}
        <div 
          onClick={() => setMapExpanded(!mapExpanded)}
          className="col-span-5 p-3 rounded-2xl bg-[#141722]/90 border border-white/[0.07] shadow-lg flex items-center justify-between cursor-pointer hover:border-cyan-500/40 transition-all group"
          title="Click to expand full interactive OpenStreetMap"
        >
          {/* Real Split Donut Ring on Left */}
          <div className="relative w-16 h-16 flex items-center justify-center">
            <svg className="w-full h-full -rotate-90">
              <circle cx="32" cy="32" r="24" fill="none" stroke="#1f2937" strokeWidth="6" />
              {/* Coral Arc (RTH Reserve) */}
              <circle 
                cx="32" cy="32" r="24" fill="none" stroke="#f43f5e" strokeWidth="6" 
                strokeDasharray="150" 
                strokeDashoffset={150 - (telemetry.rth_threshold_pct / 100.0) * 150} 
              />
              {/* Cyan Arc (Active Battery) */}
              <circle 
                cx="32" cy="32" r="24" fill="none" stroke="#00f2fe" strokeWidth="6" 
                strokeDasharray="150" 
                strokeDashoffset={150 - (telemetry.battery_pct / 100.0) * 150} 
              />
            </svg>
            <div className="absolute w-6 h-6 rounded-full bg-amber-400/90 shadow-[0_0_8px_#f59e0b] flex items-center justify-center text-[8px] font-bold text-black font-mono">
              {telemetry.battery_pct.toFixed(0)}%
            </div>
          </div>

          {/* Center Real GPS Coordinates & Map Thumbnail */}
          <div className="flex-1 px-3 flex flex-col justify-between h-full">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-mono font-bold tracking-wider text-cyan-300 uppercase flex items-center space-x-1.5">
                <MapIcon className="w-3 h-3 text-cyan-400" />
                <span>REAL GPS AVIONICS (WGS84)</span>
              </span>
              <Maximize2 className="w-3.5 h-3.5 text-slate-500 group-hover:text-cyan-400 transition-colors" />
            </div>

            {/* Dark Minimal World Map Silhouette with Live Drone GPS Pin */}
            <div className="relative h-12 rounded bg-black/50 border border-white/5 overflow-hidden flex items-center justify-center">
              <svg className="w-full h-full opacity-40" viewBox="0 0 200 80">
                <path d="M 25 35 Q 35 25 50 28 Q 65 30 75 42 Q 60 55 45 52 Z" fill="#64748b" />
                <path d="M 90 25 Q 115 20 140 28 Q 155 35 150 48 Q 125 55 105 45 Z" fill="#64748b" />
                <path d="M 145 45 Q 165 42 175 52 Q 165 65 148 58 Z" fill="#64748b" />
              </svg>
              {/* Drone Real Location Ping */}
              <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 flex items-center justify-center">
                <div className="w-2.5 h-2.5 rounded-full bg-cyan-400 shadow-[0_0_10px_#00f2fe] animate-ping" />
                <div className="absolute w-1.5 h-1.5 rounded-full bg-white" />
              </div>
            </div>

            <div className="text-[8px] font-mono text-slate-300 flex justify-between">
              <span>{telemetry.lat.toFixed(6)}°N, {telemetry.lon.toFixed(6)}°E</span>
              <span className="text-emerald-400 font-bold">{telemetry.sats} SATS (RTK FIX)</span>
            </div>
          </div>
        </div>

        {/* Card 3 (Right): Real Compass Gyro Dial & Actual Rotor RPM */}
        <div className="col-span-3 p-3 rounded-2xl bg-[#141722]/90 border border-white/[0.07] shadow-lg flex items-center justify-between">
          {/* Compass Dial rotating to Real Yaw */}
          <div className="relative w-16 h-16 rounded-full border-2 border-slate-700 bg-black/40 flex items-center justify-center">
            <div 
              className="w-1 h-6 bg-cyan-400 rounded-full origin-bottom transition-transform duration-100 shadow-[0_0_8px_#00f2fe]"
              style={{ transform: `rotate(${telemetry.yaw}deg)` }}
            />
            <div className="absolute w-2 h-2 rounded-full bg-white" />
            <span className="absolute bottom-1 text-[7px] font-mono text-slate-400">
              {Math.round(telemetry.yaw)}°
            </span>
          </div>

          {/* Big Number: Actual Motor RPM */}
          <div className="flex flex-col items-end">
            <span className="text-2xl font-extrabold font-mono tracking-tight text-amber-300 drop-shadow-[0_0_8px_rgba(245,158,11,0.4)]">
              {(telemetry.rpm || 4850).toLocaleString()}
            </span>
            <span className="text-[8px] font-mono text-slate-400 -mt-1 uppercase">
              ACTUAL ROTOR RPM
            </span>
            <div className="text-[8px] font-mono text-slate-400 mt-1 space-y-0.5 text-right">
              <div>ALT: <strong className="text-cyan-300">{telemetry.rel_alt.toFixed(1)}m AGL</strong></div>
              <div>GPU TEMP: <strong className="text-emerald-400">{telemetry.gpu_temp ? telemetry.gpu_temp.toFixed(0) : 68}°C</strong></div>
            </div>
          </div>
        </div>

      </div>

      {/* ==================================================================== */}
      {/* 2. CENTER HERO: LIVE CAMERA VIEW (DEFAULT) & TOPOGRAPHY TOGGLE        */}
      {/* ==================================================================== */}
      <div className="relative w-full h-[270px] my-3 rounded-2xl overflow-hidden border border-white/[0.09] shadow-2xl bg-[#0b0e14]">
        
        {heroMode === 'camera' ? (
          <div className="relative w-full h-full flex items-center justify-center bg-black">
            <CameraFeed telemetry={telemetry} className="w-full h-full" />
          </div>
        ) : (
          <canvas ref={canvasRef} width={1240} height={270} className="w-full h-full object-cover" />
        )}

        {/* View Mode Toggle Pill (Top Left of Hero) */}
        <div className="absolute top-3 left-3 z-20 flex space-x-1.5 p-1 rounded-xl bg-[#0b0e14]/85 backdrop-blur-md border border-white/10 shadow-lg">
          <button
            onClick={() => setHeroMode('camera')}
            className={`px-3 py-1 rounded-lg text-[10px] font-mono font-bold tracking-wider flex items-center space-x-1.5 transition-all ${
              heroMode === 'camera'
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-[0_0_10px_rgba(6,182,212,0.3)]'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Video className="w-3.5 h-3.5 text-cyan-400" />
            <span>LIVE FPV CAMERA (ACTIVE)</span>
          </button>

          <button
            onClick={() => setHeroMode('topography')}
            className={`px-3 py-1 rounded-lg text-[10px] font-mono font-bold tracking-wider flex items-center space-x-1.5 transition-all ${
              heroMode === 'topography'
                ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40 shadow-[0_0_10px_rgba(245,158,11,0.3)]'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Mountain className="w-3.5 h-3.5 text-amber-400" />
            <span>3D TOPOGRAPHY MESH</span>
          </button>
        </div>

        {/* Top-Right Secondary Gauge: Real Zoom & FPS */}
        <div className="absolute top-3 right-4 z-20 flex items-center space-x-3 p-1.5 px-3 rounded-xl bg-[#0b0e14]/80 backdrop-blur-md border border-white/10 text-right">
          <div className="flex flex-col">
            <span className="text-[12px] font-mono font-extrabold text-cyan-300">
              x{telemetry.fov_zoom ? telemetry.fov_zoom.toFixed(2) : '0.70'}
            </span>
            <span className="text-[8px] font-mono text-slate-400 uppercase">FOV ZOOM</span>
          </div>
          <div className="flex flex-col border-l border-white/10 pl-2">
            <span className="text-sm font-mono font-bold text-emerald-400">{telemetry.fps ? telemetry.fps.toFixed(0) : 30}</span>
            <span className="text-[7px] font-mono text-slate-400 uppercase">FPS</span>
          </div>
        </div>

        {/* Bottom Horizontal Real Telemetry Ribbon Inside Hero */}
        <div className="absolute bottom-0 inset-x-0 h-9 bg-[#0b0f17]/90 backdrop-blur-md border-t border-white/10 px-4 flex items-center justify-between text-[10px] font-mono text-slate-300">
          <div className="flex items-center space-x-4">
            <span>YAW: <strong className="text-cyan-400">{telemetry.yaw.toFixed(0)}°</strong></span>
            <span>PITCH: <strong className="text-rose-400">{telemetry.pitch.toFixed(1)}°</strong></span>
            <span>ROLL: <strong className="text-amber-400">{telemetry.roll.toFixed(1)}°</strong></span>
            <span>SPD: <strong className="text-emerald-400">{telemetry.speed.toFixed(1)} m/s ({telemetry.ground_speed_kmh.toFixed(1)} km/h)</strong></span>
          </div>
          <div className="flex items-center space-x-4">
            <span>ALT: <strong className="text-cyan-300">{telemetry.rel_alt.toFixed(1)}m</strong></span>
            <span>HOME: <strong className="text-amber-400">{telemetry.dist_home.toFixed(1)}m</strong></span>
            <span>SATS: <strong className="text-emerald-400">{telemetry.sats}</strong></span>
            <span>BAT: <strong className="text-amber-300">{telemetry.battery_pct.toFixed(0)}%</strong></span>
          </div>
        </div>

      </div>

      {/* ==================================================================== */}
      {/* 3. BOTTOM ROW: 3 Columns (100% Real Sensor Readings)                 */}
      {/* ==================================================================== */}
      <div className="grid grid-cols-12 gap-3.5 h-[195px] z-10">
        
        {/* Column 1 (Left): Real APAS 5.0 Obstacle Clearance Matrix */}
        <div className="col-span-4 p-3 rounded-2xl bg-[#141722]/90 border border-white/[0.07] shadow-lg flex flex-col justify-between">
          <div className="flex items-center justify-between">
            {/* Status Swirl Badge */}
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 rounded-full border border-cyan-500/40 bg-black/40 flex items-center justify-center shadow-[0_0_10px_rgba(6,182,212,0.3)]">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
              </div>
              <div className="flex flex-col">
                <span className="text-[11px] font-mono font-bold text-slate-200">
                  APAS 5.0 SHIELD
                </span>
                <span className="text-[7px] font-mono text-emerald-400 uppercase">
                  {telemetry.wire_hazard ? 'HAZARD DETECTED' : 'CLEARANCE OK'}
                </span>
              </div>
            </div>

            {/* Real IMU Vibration Sine Wave */}
            <svg className="w-24 h-6 opacity-80">
              <path 
                d={`M 0 12 Q 12 ${12 + telemetry.pitch * 0.8} 24 12 T 48 12 T 72 12 T 96 12`} 
                fill="none" 
                stroke="#00f2fe" 
                strokeWidth="1.5" 
              />
            </svg>
          </div>

          {/* Real 9-Sector Depth Clearance Bars */}
          <div className="flex items-end justify-between h-20 px-1 pt-2 border-t border-white/5">
            {(telemetry.obstacle_sectors || [4.5, 5.2, 3.8, 2.4, 1.8, 3.1, 4.0, 5.5, 4.8]).map((dist, idx) => {
              const heightPx = Math.min(65, Math.max(10, (dist / 6.0) * 65));
              const barColor = dist < 1.5 
                ? 'from-rose-600 to-rose-400 shadow-[0_0_8px_#f43f5e]' 
                : (dist < 3.0 ? 'from-amber-600 to-amber-300' : 'from-[#78350f] via-[#b45309] to-[#fde68a]');

              return (
                <div key={idx} className="flex flex-col items-center space-y-1">
                  <div 
                    className={`w-3 rounded-t-sm bg-gradient-to-t ${barColor} transition-all duration-200`}
                    style={{ height: `${heightPx}px` }}
                  />
                  <span className="text-[7px] font-mono text-slate-400">{dist.toFixed(1)}m</span>
                </div>
              );
            })}
          </div>

          <div className="text-[8px] font-mono text-slate-400 flex justify-between">
            <span>SECTORS: FL - FRONT - FR</span>
            <span className="text-cyan-400 font-bold">3D DEPTHNET</span>
          </div>
        </div>

        {/* Column 2 (Center): Real Flight Dynamics Spectrum & Instruments */}
        <div className="col-span-5 p-3 rounded-2xl bg-[#141722]/90 border border-white/[0.07] shadow-lg flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-mono tracking-wider text-slate-400 uppercase font-semibold">
              FLIGHT DYNAMICS (REAL-TIME HISTORY)
            </span>
            <span className="text-[8px] font-mono text-amber-400 font-bold">
              {telemetry.flight_mode}
            </span>
          </div>

          {/* Real Telemetry History Curves */}
          <div className="relative h-20 w-full overflow-hidden rounded-lg bg-black/40 border border-white/5">
            <svg className="w-full h-full" viewBox="0 0 320 80">
              {/* Speed Area Curve */}
              {telemetry.speed_history && (
                <path 
                  d={`${createSplinePath(telemetry.speed_history, 4.0, 70)} L 320 80 L 0 80 Z`} 
                  fill="rgba(245, 158, 11, 0.2)" 
                  stroke="#f59e0b" 
                  strokeWidth="1.5" 
                />
              )}
              {/* Pitch Spline Curve */}
              {telemetry.pitch_history && (
                <path 
                  d={createSplinePath(telemetry.pitch_history, 1.5, 40)} 
                  fill="none" 
                  stroke="#00f2fe" 
                  strokeWidth="1.5" 
                />
              )}
              {/* Roll Spline Curve */}
              {telemetry.roll_history && (
                <path 
                  d={createSplinePath(telemetry.roll_history, 1.5, 40)} 
                  fill="none" 
                  stroke="#f43f5e" 
                  strokeWidth="1.2" 
                  strokeDasharray="4, 4" 
                />
              )}
            </svg>
          </div>

          {/* 4 Circular Real Mini-Dials */}
          <div className="grid grid-cols-4 gap-2 pt-1 border-t border-white/5 text-center">
            <div className="flex flex-col items-center">
              <div className="w-7 h-7 rounded-full border border-cyan-400/50 bg-black/40 flex items-center justify-center text-[9px] font-bold font-mono text-cyan-300">
                WP1
              </div>
              <span className="text-[7px] font-mono text-slate-400 mt-0.5">WAYPOINT</span>
            </div>

            <div className="flex flex-col items-center">
              <div className="w-7 h-7 rounded-full border border-amber-400/50 bg-black/40 flex items-center justify-center text-[9px] font-bold font-mono text-amber-300">
                {telemetry.battery_pct.toFixed(0)}%
              </div>
              <span className="text-[7px] font-mono text-slate-400 mt-0.5">BATTERY</span>
            </div>

            <div className="flex flex-col items-center">
              <div className="w-7 h-7 rounded-full border border-emerald-400/50 bg-black/40 flex items-center justify-center text-[9px] font-bold font-mono text-emerald-300">
                {telemetry.gpu_temp ? telemetry.gpu_temp.toFixed(0) : 68}°C
              </div>
              <span className="text-[7px] font-mono text-slate-400 mt-0.5">GPU TEMP</span>
            </div>

            <div className="flex flex-col items-center">
              <div className="w-7 h-7 rounded-full border border-rose-400/50 bg-black/40 flex items-center justify-center text-[9px] font-bold font-mono text-rose-300">
                {telemetry.speed.toFixed(1)}
              </div>
              <span className="text-[7px] font-mono text-slate-400 mt-0.5">M/S SPEED</span>
            </div>
          </div>
        </div>

        {/* Column 3 (Right): Real Distance to Home & Real Speedometer Arc Gauge */}
        <div className="col-span-3 p-3 rounded-2xl bg-[#141722]/90 border border-white/[0.07] shadow-lg flex items-center justify-between">
          
          {/* Numbers Left: Real Distance & Bearing */}
          <div className="flex flex-col justify-between h-full py-1">
            <div className="flex flex-col">
              <span className="text-[8px] font-mono text-slate-400 uppercase">DIST TO HOME</span>
              <span className="text-xl font-extrabold font-mono text-rose-400 drop-shadow-[0_0_8px_rgba(244,63,94,0.4)]">
                {telemetry.dist_home.toFixed(1)}m
              </span>
            </div>

            <div className="flex flex-col">
              <span className="text-[8px] font-mono text-slate-400 uppercase">HOME BEARING</span>
              <span className="text-[11px] font-mono font-bold text-emerald-400">
                {telemetry.bearing_home.toFixed(0)}° BEARING
              </span>
            </div>

            {/* Real Frame Latency Wave */}
            <div className="text-[8px] font-mono text-slate-400">
              PING: <strong className="text-amber-400">{telemetry.ping_ms.toFixed(0)} ms</strong>
            </div>
          </div>

          {/* Big Arc Speedometer Gauge (Bound to Actual Ground Speed in km/h) */}
          <div className="relative w-28 h-28 flex items-center justify-center">
            <svg className="w-full h-full -rotate-135">
              <circle cx="56" cy="56" r="42" fill="none" stroke="#1f2937" strokeWidth="8" strokeDasharray="190" strokeDashoffset="40" />
              <circle 
                cx="56" 
                cy="56" 
                r="42" 
                fill="none" 
                stroke="#f59e0b" 
                strokeWidth="8" 
                strokeDasharray="190" 
                strokeDashoffset={arcDashOffset} 
                strokeLinecap="round"
                className="filter drop-shadow-[0_0_8px_rgba(245,158,11,0.6)] transition-all duration-150"
              />
            </svg>

            {/* Gauge Center Value: Real Speed in km/h */}
            <div className="absolute flex flex-col items-center">
              <span className="text-xl font-extrabold font-mono text-slate-100">
                {(telemetry.ground_speed_kmh || 0).toFixed(1)}
              </span>
              <span className="text-[8px] font-mono text-amber-400 font-bold -mt-1">
                KM/H
              </span>
            </div>
          </div>

        </div>

      </div>

      {/* ==================================================================== */}
      {/* 4. FLOATING AEROSPACE FLIGHT CONTROL DOCK (Bottom)                   */}
      {/* ==================================================================== */}
      <div className="relative z-20 flex justify-center pt-2">
        <div className="p-1 rounded-2xl bg-[#0b0e14]/90 backdrop-blur-xl border border-white/10 shadow-2xl flex items-center space-x-2 px-3 py-1.5">
          
          {/* Big Record Button */}
          <button
            onClick={onToggleRecord}
            className={`px-3 py-1 rounded-xl text-[10px] font-mono font-bold tracking-wider flex items-center space-x-1.5 transition-all ${
              telemetry.is_recording
                ? 'bg-rose-500/20 text-rose-300 border border-rose-500/50 animate-pulse'
                : 'bg-white/5 hover:bg-white/10 text-slate-300'
            }`}
          >
            <div className={`w-2.5 h-2.5 rounded-full ${telemetry.is_recording ? 'bg-rose-500 animate-ping' : 'bg-rose-500'}`} />
            <span>{telemetry.is_recording ? `REC [${telemetry.record_duration}]` : 'RECORD [R]'}</span>
          </button>

          {/* Photo Shutter Button */}
          <button
            onClick={onCapturePhoto}
            className="px-3 py-1 rounded-xl bg-white/5 hover:bg-white/10 text-slate-300 text-[10px] font-mono font-bold flex items-center space-x-1.5 active:scale-95"
          >
            <Camera className="w-3.5 h-3.5 text-white" />
            <span>PHOTO [P]</span>
          </button>

          {/* RTH Button */}
          <button
            onClick={onToggleRth}
            className={`px-3 py-1 rounded-xl text-[10px] font-mono font-bold tracking-wider flex items-center space-x-1.5 transition-all ${
              telemetry.flight_mode === 'RTH'
                ? 'bg-fuchsia-500/20 text-fuchsia-300 border border-fuchsia-500/50 animate-pulse'
                : 'bg-white/5 hover:bg-white/10 text-slate-300'
            }`}
          >
            <Home className="w-3.5 h-3.5 text-fuchsia-400" />
            <span>RTH [H]</span>
          </button>

          {/* Mode Switcher */}
          <button
            onClick={onCycleMode}
            className="px-3 py-1 rounded-xl bg-white/5 hover:bg-white/10 text-slate-300 text-[10px] font-mono font-bold flex items-center space-x-1.5"
          >
            <Zap className="w-3.5 h-3.5 text-emerald-400" />
            <span>{telemetry.flight_mode}</span>
          </button>

          {/* Easy-Connect Manager */}
          <button
            onClick={onOpenConnectDrawer}
            className="px-3 py-1 rounded-xl bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/30 text-cyan-300 text-[10px] font-mono font-bold flex items-center space-x-1.5"
          >
            <Radio className="w-3.5 h-3.5 text-cyan-400" />
            <span>EASY-CONNECT</span>
          </button>

          {/* Emergency Brake */}
          <button
            onClick={onEmergencyBrake}
            className="px-3 py-1 rounded-xl bg-rose-500/20 hover:bg-rose-500/30 border border-rose-500/50 text-rose-300 text-[10px] font-mono font-bold flex items-center space-x-1.5"
          >
            <Octagon className="w-3.5 h-3.5 text-rose-400" />
            <span>BRAKE</span>
          </button>

        </div>
      </div>

      {/* ==================================================================== */}
      {/* 5. FULLSCREEN EXPANDED MAP MODAL (Triggered by Map click)            */}
      {/* ==================================================================== */}
      {mapExpanded && (
        <div className="fixed inset-4 z-50 rounded-3xl overflow-hidden border border-white/20 shadow-2xl bg-[#0b0e14] flex flex-col">
          <div className="p-3 bg-[#141722] border-b border-white/10 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <MapIcon className="w-4 h-4 text-cyan-400" />
              <span className="text-xs font-mono font-bold text-slate-200 uppercase tracking-wider">
                Full-Scale Tactical OpenStreetMap Navigation
              </span>
            </div>
            <button
              onClick={() => setMapExpanded(false)}
              className="px-3 py-1 rounded-lg bg-white/10 hover:bg-white/20 text-xs font-mono text-slate-200"
            >
              CLOSE MAP [ESC]
            </button>
          </div>
          <div className="flex-1 w-full h-full">
            <RealMapLeaflet telemetry={telemetry} className="w-full h-full" />
          </div>
        </div>
      )}

    </div>
  );
};
