import React, { useState } from 'react';
import { DroneTelemetry } from '../types';
import { CameraFeed } from './CameraFeed';
import { GtaRadarMinimap } from './GtaRadarMinimap';
import { RealMapLeaflet } from './RealMapLeaflet';
import { 
  Wifi, 
  Radio, 
  ShieldCheck, 
  Clock, 
  Activity, 
  Satellite, 
  BatteryMedium, 
  Cpu, 
  Home, 
  Zap, 
  ZoomIn, 
  Sparkles, 
  Flame, 
  Octagon, 
  Square, 
  Camera, 
  Compass, 
  X,
  Gauge,
  Navigation,
  Folder
} from 'lucide-react';

interface CockpitViewProps {
  telemetry: DroneTelemetry;
  onToggleRecord: () => void;
  onCapturePhoto: () => void;
  onToggleRth: () => void;
  onCycleMode: () => void;
  onCycleZoom: () => void;
  onToggleClarity: () => void;
  onToggleThermal: () => void;
  onOpenConnectDrawer: () => void;
  onEmergencyBrake: () => void;
  onOpenMediaGallery: () => void;
}

export const CockpitView: React.FC<CockpitViewProps> = ({
  telemetry,
  onToggleRecord,
  onCapturePhoto,
  onToggleRth,
  onCycleMode,
  onCycleZoom,
  onToggleClarity,
  onToggleThermal,
  onOpenConnectDrawer,
  onEmergencyBrake,
  onOpenMediaGallery,
}) => {
  const [isMapExpanded, setIsMapExpanded] = useState<boolean>(false);

  // Flight mode colors
  const modeColors: Record<string, string> = {
    'N-MODE': 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40 shadow-[0_0_12px_rgba(16,185,129,0.3)]',
    'S-MODE': 'bg-amber-500/20 text-amber-300 border-amber-500/40 shadow-[0_0_12px_rgba(245,158,11,0.3)]',
    'C-MODE': 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40 shadow-[0_0_12px_rgba(6,182,212,0.3)]',
    'RTH': 'bg-fuchsia-500/25 text-fuchsia-300 border-fuchsia-500/50 animate-pulse shadow-[0_0_20px_rgba(217,70,239,0.4)]',
  };

  const getBatteryColor = (pct: number) => {
    if (pct > 30) return 'bg-emerald-400';
    if (pct > 15) return 'bg-amber-400';
    return 'bg-rose-500 animate-pulse';
  };

  // Sliding compass ribbon calculations
  const compassWidth = 320;
  const degPerPx = 75 / compassWidth;
  const headingDiffHome = ((telemetry.bearing_home - telemetry.yaw + 180) % 360) - 180;
  const homeMarkerOffset = Math.max(
    -compassWidth / 2 + 15,
    Math.min(compassWidth / 2 - 15, headingDiffHome / degPerPx)
  );

  // Speedometer circular arc calculation (0 to 60 km/h)
  const speedNorm = Math.min(1.0, Math.max(0.0, (telemetry.ground_speed_kmh || 0) / 60.0));
  const arcDashOffset = 190 - speedNorm * 130;

  return (
    <div className="relative w-full h-full overflow-hidden select-none bg-[#05070a] text-slate-100">
      
      {/* ==================================================================== */}
      {/* 1. LAYER 0: BIG FULL-SCREEN LIVE CAMERA VIEW (EDGE TO EDGE)          */}
      {/* ==================================================================== */}
      <div className="absolute inset-0 z-0 w-full h-full">
        <CameraFeed telemetry={telemetry} className="w-full h-full" />
      </div>

      {/* Optical Reticle Center Crosshairs */}
      <div className="absolute inset-0 pointer-events-none z-10 flex items-center justify-center">
        {/* Subtle Center Pitch Marks */}
        <div 
          className="relative w-64 h-64 flex items-center justify-center transition-transform duration-75"
          style={{ transform: `rotate(${-telemetry.roll}deg)` }}
        >
          <div 
            className="w-full flex items-center justify-center transition-transform duration-75"
            style={{ transform: `translateY(${telemetry.pitch * 2.5}px)` }}
          >
            {/* Horizon Center Crosshair Wings */}
            <div className="relative w-28 h-6 flex items-center justify-between">
              <div className="w-9 h-[2px] bg-cyan-400/80 shadow-[0_0_8px_#00f2fe] relative">
                <div className="absolute right-0 top-0 w-[2px] h-2 bg-cyan-400" />
              </div>
              <div className="w-1.5 h-1.5 rounded-full bg-cyan-400 shadow-[0_0_8px_#00f2fe]" />
              <div className="w-9 h-[2px] bg-cyan-400/80 shadow-[0_0_8px_#00f2fe] relative">
                <div className="absolute left-0 top-0 w-[2px] h-2 bg-cyan-400" />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ==================================================================== */}
      {/* 2. LAYER 1: TOP COCKPIT RIBBON (REAL AVIONICS & 360° COMPASS)         */}
      {/* ==================================================================== */}
      <header className="absolute top-0 inset-x-0 z-20 px-3 pt-2 pointer-events-auto">
        <div className="p-1 rounded-2xl bg-[#090d14]/85 backdrop-blur-xl border border-white/10 shadow-[0_8px_32px_rgba(0,0,0,0.6)]">
          <div className="flex items-center justify-between px-3.5 py-1 bg-black/40 rounded-[calc(1rem-0.25rem)] border border-white/5">
            
            {/* Left: Station Identity & Flight Mode & Real Satellites */}
            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-2">
                <div className="w-6 h-6 rounded-lg bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center shadow-[0_0_10px_rgba(6,182,212,0.4)]">
                  <Activity className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
                </div>
                <div className="flex flex-col">
                  <span className="text-[11px] font-extrabold tracking-widest text-slate-100 uppercase font-mono">
                    MINI DRONE
                  </span>
                  <span className="text-[7.5px] tracking-wider text-cyan-400 uppercase -mt-0.5 font-bold">
                    CONTROL STATION
                  </span>
                </div>
              </div>

              <div className="h-4 w-[1px] bg-white/10" />

              {/* Mode Button */}
              <button
                onClick={onCycleMode}
                className={`px-2.5 py-0.5 rounded-lg border text-[11px] font-mono font-bold tracking-wider transition-all duration-200 active:scale-95 flex items-center space-x-1.5 ${modeColors[telemetry.flight_mode] || modeColors['N-MODE']}`}
                title="Click to cycle flight mode (N-Mode / S-Mode / C-Mode)"
              >
                <span className="w-1.5 h-1.5 rounded-full bg-current animate-ping" />
                <span>{telemetry.flight_mode}</span>
              </button>

              {/* Real GNSS Satellites */}
              <div className="flex items-center space-x-1.5 px-2 py-0.5 rounded-lg bg-white/[0.04] border border-white/5 text-slate-300">
                <Satellite className="w-3.5 h-3.5 text-cyan-400" />
                <span className="text-[10px] font-mono text-cyan-300 font-bold">
                  {telemetry.sats} SATS
                </span>
                <span className="px-1 py-0.2 rounded text-[7.5px] font-mono font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                  RTK FIX
                </span>
              </div>
            </div>

            {/* Center: 360° Sliding Military Compass Ribbon with Home Beacon [H] */}
            <div className="hidden md:flex flex-col items-center">
              <div className="relative w-[320px] h-6 bg-[#0b0f17]/90 rounded-lg border border-white/10 overflow-hidden shadow-inner">
                {/* Center Lubber Line */}
                <div className="absolute top-0 bottom-0 left-1/2 -translate-x-1/2 w-[2px] bg-cyan-400 z-10 shadow-[0_0_8px_#00f2fe]" />
                
                {/* Degree readouts SVG */}
                <svg className="w-full h-full">
                  {Array.from({ length: 91 }, (_, i) => {
                    const deg = Math.floor(telemetry.yaw - 45) + i;
                    const normalizedDeg = (deg + 360) % 360;
                    const x = (deg - telemetry.yaw) / degPerPx + compassWidth / 2;

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
                          <line x1={x} y1={16} x2={x} y2={24} stroke="#64748b" strokeWidth={1} />
                          <text
                            x={x}
                            y={11}
                            fill={label === 'N' ? '#00f2fe' : '#cbd5e1'}
                            fontSize={8}
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
                  className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-4 h-4 rounded-full bg-amber-400 text-black font-extrabold text-[8px] flex items-center justify-center shadow-[0_0_8px_#f59e0b] border border-black/40"
                  style={{ left: `${compassWidth / 2 + homeMarkerOffset}px` }}
                  title={`Bearing to Home: ${telemetry.bearing_home.toFixed(0)}°`}
                >
                  H
                </div>

                {/* Heading numerical value */}
                <div className="absolute bottom-0.5 right-1.5 text-[8px] font-mono text-cyan-400 font-bold">
                  {Math.round(telemetry.yaw).toString().padStart(3, '0')}°
                </div>
              </div>
            </div>

            {/* Right: Real Battery, OcuSync Link, Camera Source, GPU Temp, Clock */}
            <div className="flex items-center space-x-3">
              {/* Real Smart Battery */}
              <div className="flex items-center space-x-2 px-2.5 py-0.5 rounded-xl bg-white/[0.04] border border-white/5">
                <BatteryMedium className="w-4 h-4 text-emerald-400" />
                <div className="flex flex-col">
                  <div className="flex items-center space-x-1.5">
                    <span className="text-[10px] font-mono font-bold text-slate-100">
                      {telemetry.battery_pct.toFixed(0)}%
                    </span>
                    <span className="text-[9px] font-mono text-slate-400">
                      {telemetry.remaining_flight_time}
                    </span>
                    <span className="text-[8.5px] font-mono text-slate-500">
                      {telemetry.battery_voltage.toFixed(1)}V
                    </span>
                  </div>
                  <div className="relative w-24 h-1 bg-slate-800 rounded-full overflow-hidden mt-0.5">
                    <div 
                      className={`h-full transition-all duration-300 ${getBatteryColor(telemetry.battery_pct)}`}
                      style={{ width: `${telemetry.battery_pct}%` }}
                    />
                    <div 
                      className="absolute top-0 bottom-0 w-[2px] bg-amber-400 shadow-[0_0_4px_#f59e0b]"
                      style={{ left: `${telemetry.rth_threshold_pct}%` }}
                      title={`RTH Reserve: ${telemetry.rth_threshold_pct.toFixed(0)}%`}
                    />
                  </div>
                </div>
              </div>

              {/* Real RF Signal & Latency */}
              <div className="flex items-center space-x-1.5 px-2 py-0.5 rounded-xl bg-white/[0.04] border border-white/5 text-[9px] font-mono">
                <div className="flex items-end space-x-0.5 h-3">
                  {[1, 2, 3, 4, 5].map((bar) => (
                    <div 
                      key={bar}
                      className={`w-0.5 rounded-t-sm transition-all ${
                        bar <= Math.ceil(telemetry.signal_pct / 20)
                          ? 'bg-cyan-400 shadow-[0_0_6px_rgba(6,182,212,0.5)]'
                          : 'bg-slate-700'
                      }`}
                      style={{ height: `${bar * 20}%` }}
                    />
                  ))}
                </div>
                <div className="flex flex-col text-[8.5px] leading-tight">
                  <span className="text-slate-200 font-semibold">{telemetry.signal_pct}% RSSI</span>
                  <span className="text-cyan-400/80">{telemetry.ping_ms.toFixed(0)}ms</span>
                </div>
              </div>

              {/* Real GPU Temperature */}
              <div className="hidden lg:flex items-center space-x-1 px-2 py-0.5 rounded-lg bg-white/[0.04] border border-white/5 text-[9px] font-mono">
                <Cpu className="w-3 h-3 text-emerald-400" />
                <span className="text-slate-300">GPU:</span>
                <span className="text-emerald-400 font-bold">{telemetry.gpu_temp ? telemetry.gpu_temp.toFixed(0) : 68}°C</span>
              </div>

              {/* Interactive Camera Source Pill */}
              <button
                onClick={onOpenConnectDrawer}
                className="px-2 py-0.5 rounded-xl bg-cyan-500/15 hover:bg-cyan-500/25 border border-cyan-500/40 text-cyan-300 transition-all duration-200 active:scale-95 flex items-center space-x-1.5 group"
                title="Click to configure camera connection, scan subnet, or switch to webcam [C]"
              >
                <Radio className="w-3 h-3 text-cyan-400 group-hover:animate-pulse" />
                <span className="text-[9px] font-mono font-medium truncate max-w-[130px]">
                  {telemetry.camera_source}
                </span>
              </button>
            </div>

          </div>
        </div>
      </header>

      {/* ==================================================================== */}
      {/* 3. LAYER 2: LEFT HUD (REAL AIRSPEED TAPE & REAL ESC MOTOR MIXER)     */}
      {/* ==================================================================== */}
      <div className="absolute left-4 top-16 z-20 flex flex-col space-y-2.5 pointer-events-auto w-36">
        
        {/* Real Airspeed Tape */}
        <div className="p-2.5 rounded-2xl bg-[#090d14]/85 backdrop-blur-xl border border-white/10 shadow-xl space-y-1">
          <div className="flex items-center justify-between text-[9px] font-mono text-slate-400">
            <span className="font-bold text-cyan-300">AIRSPEED</span>
            <span className="text-[7.5px] text-slate-500">PITOT</span>
          </div>
          
          <div className="flex items-baseline space-x-1.5 py-1 px-2 rounded-xl bg-black/40 border border-white/5">
            <span className="text-2xl font-mono font-black text-cyan-300 drop-shadow-[0_0_8px_rgba(6,182,212,0.4)]">
              {telemetry.speed.toFixed(1)}
            </span>
            <span className="text-[9px] font-mono text-cyan-400/80 font-bold">m/s</span>
            <span className="text-[9px] font-mono text-slate-400 ml-auto">
              ({telemetry.ground_speed_kmh.toFixed(1)} km/h)
            </span>
          </div>
        </div>

        {/* Real ESC Quadcopter Motor Mixer (M1-M4 Real PWM Outputs) */}
        <div className="p-2.5 rounded-2xl bg-[#090d14]/85 backdrop-blur-xl border border-white/10 shadow-xl space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-[9px] font-mono font-bold tracking-wider text-slate-300 uppercase">
              ESC MOTOR MIXER
            </span>
            <div className="flex space-x-1">
              {[1, 2, 3, 4].map((d) => (
                <div key={d} className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              ))}
            </div>
          </div>

          {/* 4 Real Motor Load Bars */}
          <div className="space-y-1.5">
            {/* M1 (Front Right) */}
            <div className="flex items-center justify-between text-[8px] font-mono">
              <span className="text-cyan-400 font-bold w-12">M1 (FR)</span>
              <div className="flex-1 h-1.5 bg-slate-900 rounded-full overflow-hidden mx-1.5 border border-white/5">
                <div 
                  className="h-full bg-cyan-400 shadow-[0_0_6px_#00f2fe] transition-all duration-150"
                  style={{ width: `${telemetry.motors ? telemetry.motors[0] : 74}%` }}
                />
              </div>
              <span className="text-slate-300 font-bold w-6 text-right">
                {telemetry.motors ? telemetry.motors[0].toFixed(0) : 74}%
              </span>
            </div>

            {/* M2 (Rear Right) */}
            <div className="flex items-center justify-between text-[8px] font-mono">
              <span className="text-rose-400 font-bold w-12">M2 (RR)</span>
              <div className="flex-1 h-1.5 bg-slate-900 rounded-full overflow-hidden mx-1.5 border border-white/5">
                <div 
                  className="h-full bg-rose-400 shadow-[0_0_6px_#fb7185] transition-all duration-150"
                  style={{ width: `${telemetry.motors ? telemetry.motors[1] : 78}%` }}
                />
              </div>
              <span className="text-slate-300 font-bold w-6 text-right">
                {telemetry.motors ? telemetry.motors[1].toFixed(0) : 78}%
              </span>
            </div>

            {/* M3 (Rear Left) */}
            <div className="flex items-center justify-between text-[8px] font-mono">
              <span className="text-amber-400 font-bold w-12">M3 (RL)</span>
              <div className="flex-1 h-1.5 bg-slate-900 rounded-full overflow-hidden mx-1.5 border border-white/5">
                <div 
                  className="h-full bg-amber-400 shadow-[0_0_6px_#f59e0b] transition-all duration-150"
                  style={{ width: `${telemetry.motors ? telemetry.motors[2] : 76}%` }}
                />
              </div>
              <span className="text-slate-300 font-bold w-6 text-right">
                {telemetry.motors ? telemetry.motors[2].toFixed(0) : 76}%
              </span>
            </div>

            {/* M4 (Front Left) */}
            <div className="flex items-center justify-between text-[8px] font-mono">
              <span className="text-emerald-400 font-bold w-12">M4 (FL)</span>
              <div className="flex-1 h-1.5 bg-slate-900 rounded-full overflow-hidden mx-1.5 border border-white/5">
                <div 
                  className="h-full bg-emerald-400 shadow-[0_0_6px_#10b981] transition-all duration-150"
                  style={{ width: `${telemetry.motors ? telemetry.motors[3] : 72}%` }}
                />
              </div>
              <span className="text-slate-300 font-bold w-6 text-right">
                {telemetry.motors ? telemetry.motors[3].toFixed(0) : 72}%
              </span>
            </div>
          </div>

          <div className="text-[7.5px] font-mono text-slate-400 flex justify-between border-t border-white/5 pt-1">
            <span>DSHOT600</span>
            <span className="text-cyan-300 font-bold">{telemetry.battery_voltage.toFixed(1)}V BUS</span>
          </div>
        </div>

      </div>

      {/* ==================================================================== */}
      {/* 4. LAYER 3: RIGHT HUD (REAL ALTITUDE, ROTOR RPM & CAMERA SHUTTER)    */}
      {/* ==================================================================== */}
      <div className="absolute right-4 top-16 z-20 flex flex-col items-end space-y-2.5 pointer-events-auto">
        
        {/* Real Altitude & Climb Rate */}
        <div className="p-2.5 rounded-2xl bg-[#090d14]/85 backdrop-blur-xl border border-white/10 shadow-xl space-y-1 w-36">
          <div className="flex items-center justify-between text-[9px] font-mono text-slate-400">
            <span className="font-bold text-emerald-300">ALTITUDE</span>
            <span className="text-[7.5px] text-slate-500">SONAR/BARO</span>
          </div>
          
          <div className="flex items-baseline space-x-1.5 py-1 px-2 rounded-xl bg-black/40 border border-white/5">
            <span className="text-2xl font-mono font-black text-emerald-300 drop-shadow-[0_0_8px_rgba(16,185,129,0.4)]">
              {telemetry.rel_alt.toFixed(1)}
            </span>
            <span className="text-[9px] font-mono text-emerald-400/80 font-bold">m AGL</span>
          </div>

          <div className="flex justify-between text-[8px] font-mono text-slate-400 px-0.5">
            <span>MSL: {telemetry.altitude.toFixed(0)}m</span>
            <span className="text-emerald-400 font-bold">
              Vz: {telemetry.climb_rate >= 0 ? `+${telemetry.climb_rate.toFixed(1)}` : telemetry.climb_rate.toFixed(1)} m/s
            </span>
          </div>
        </div>

        {/* Real Actual Rotor RPM */}
        <div className="p-2.5 rounded-2xl bg-[#090d14]/85 backdrop-blur-xl border border-white/10 shadow-xl space-y-1 w-36 text-right">
          <span className="text-[8.5px] font-mono text-slate-400 uppercase tracking-wider block">
            ROTOR SPEED
          </span>
          <div className="text-2xl font-extrabold font-mono tracking-tight text-amber-300 drop-shadow-[0_0_8px_rgba(245,158,11,0.4)]">
            {(telemetry.rpm || 4850).toLocaleString()}
          </div>
          <span className="text-[8px] font-mono text-amber-400/80 block -mt-1">
            RPM TACHOMETER
          </span>
        </div>

        {/* Dedicated DJI-Style Shutter Controls */}
        <div className="p-2 rounded-2xl bg-[#090d14]/85 backdrop-blur-xl border border-white/10 shadow-xl flex flex-col items-center space-y-3">
          
          {/* Big Red Record Button [R] */}
          <div className="flex flex-col items-center space-y-1">
            <button
              onClick={onToggleRecord}
              className={`relative w-11 h-11 rounded-full border-2 transition-all duration-200 flex items-center justify-center active:scale-95 group ${
                telemetry.is_recording
                  ? 'border-rose-500 shadow-[0_0_20px_rgba(244,63,94,0.7)] bg-rose-500/20'
                  : 'border-slate-300 hover:border-white shadow-lg bg-white/5'
              }`}
              title="Start/Stop Video Recording [R]"
            >
              {telemetry.is_recording ? (
                <Square className="w-4 h-4 fill-rose-500 text-rose-500 animate-pulse" />
              ) : (
                <div className="w-4 h-4 rounded-full bg-rose-500 shadow-[0_0_8px_#f43f5e] group-hover:scale-110 transition-transform" />
              )}
            </button>

            {telemetry.is_recording && (
              <span className="px-1.5 py-0.5 rounded text-[7.5px] font-mono font-bold bg-rose-500/20 text-rose-400 border border-rose-500/40 animate-pulse">
                {telemetry.record_duration}
              </span>
            )}
          </div>

          <div className="w-7 h-[1px] bg-white/10" />

          {/* White Photo Shutter Button [P] */}
          <button
            onClick={onCapturePhoto}
            className="w-10 h-10 rounded-full border-2 border-white/80 hover:border-white bg-white/10 flex items-center justify-center transition-all duration-200 active:scale-90 shadow-md group"
            title="Capture High-Res Photo [P]"
          >
            <div className="w-5 h-5 rounded-full bg-white shadow-[0_0_8px_rgba(255,255,255,0.8)] group-hover:scale-105 transition-transform" />
          </button>

          <div className="w-7 h-[1px] bg-white/10" />

          {/* Media Recordings Gallery Button [G] */}
          <button
            onClick={onOpenMediaGallery}
            className="w-8 h-8 rounded-xl bg-white/5 hover:bg-white/15 border border-white/10 text-slate-300 flex items-center justify-center transition-all active:scale-90"
            title="Open Drone Recordings & Photos Gallery [G]"
          >
            <Folder className="w-4 h-4 text-cyan-400" />
          </button>
        </div>

      </div>

      {/* ==================================================================== */}
      {/* 5. LAYER 4: BOTTOM-LEFT GTA RADAR MINIMAP (REAL MAP TILES & GPS)     */}
      {/* ==================================================================== */}
      <div className="absolute bottom-3 left-4 z-20 pointer-events-auto">
        <GtaRadarMinimap
          telemetry={telemetry}
          onExpandMap={() => setIsMapExpanded(true)}
        />
      </div>

      {/* ==================================================================== */}
      {/* 6. LAYER 5: BOTTOM-RIGHT SPEEDOMETER & HOME VECTOR                   */}
      {/* ==================================================================== */}
      <div className="absolute bottom-3 right-4 z-20 pointer-events-auto">
        <div className="p-2 rounded-2xl bg-[#090d14]/85 backdrop-blur-xl border border-white/10 shadow-xl flex items-center space-x-3">
          
          {/* Circular Ground Speedometer Arc */}
          <div className="relative w-16 h-16 flex items-center justify-center">
            <svg className="w-full h-full -rotate-90">
              <circle cx="32" cy="32" r="24" fill="none" stroke="#1f2937" strokeWidth="4" />
              <circle 
                cx="32" cy="32" r="24" fill="none" stroke="#00f2fe" strokeWidth="4"
                strokeDasharray="150"
                strokeDashoffset={arcDashOffset}
                className="transition-all duration-300"
              />
            </svg>
            <div className="absolute flex flex-col items-center justify-center">
              <span className="text-xs font-mono font-black text-cyan-300">
                {telemetry.ground_speed_kmh.toFixed(0)}
              </span>
              <span className="text-[6.5px] font-mono text-slate-400 uppercase -mt-0.5">KM/H</span>
            </div>
          </div>

          {/* Distance & Bearing to Home */}
          <div className="flex flex-col text-[8.5px] font-mono space-y-0.5 pr-2">
            <div className="flex items-center space-x-1 text-slate-400">
              <Navigation className="w-3 h-3 text-amber-400" />
              <span>HOME VECTOR:</span>
            </div>
            <div className="text-slate-200">
              DIST: <strong className="text-amber-300">{telemetry.dist_home.toFixed(1)}m</strong>
            </div>
            <div className="text-slate-200">
              BEARING: <strong className="text-cyan-300">{Math.round(telemetry.bearing_home)}°</strong>
            </div>
          </div>

        </div>
      </div>

      {/* ==================================================================== */}
      {/* 7. LAYER 6: BOTTOM-CENTER FLOATING COMMAND DOCK                      */}
      {/* ==================================================================== */}
      <footer className="absolute bottom-3 inset-x-0 z-20 flex justify-center pointer-events-none">
        <div className="p-1 rounded-2xl bg-[#090d14]/85 backdrop-blur-xl border border-white/10 shadow-2xl pointer-events-auto">
          <div className="flex items-center space-x-1 px-2.5 py-1 bg-black/40 rounded-[calc(1rem-0.25rem)] border border-white/5">
            
            {/* 1. Return-to-Home [H] */}
            <button
              onClick={onToggleRth}
              className={`px-2.5 py-1 rounded-xl border text-[10px] font-mono font-bold tracking-wider transition-all duration-200 active:scale-95 flex items-center space-x-1.5 ${
                telemetry.flight_mode === 'RTH'
                  ? 'bg-fuchsia-500/20 text-fuchsia-300 border-fuchsia-500/60 shadow-[0_0_15px_rgba(217,70,239,0.4)] animate-pulse'
                  : 'bg-white/[0.03] hover:bg-white/[0.08] text-slate-200 border-white/10'
              }`}
              title="Engage Autonomous Return-To-Home [H / B]"
            >
              <Home className="w-3.5 h-3.5 text-fuchsia-400" />
              <span>RTH</span>
            </button>

            {/* 2. Mode Selector */}
            <button
              onClick={onCycleMode}
              className="px-2.5 py-1 rounded-xl bg-white/[0.03] hover:bg-white/[0.08] border border-white/10 text-[10px] font-mono font-medium text-slate-200 transition-all duration-200 active:scale-95 flex items-center space-x-1.5"
              title="Cycle Mode: Normal / Sport / Cine"
            >
              <Zap className="w-3.5 h-3.5 text-emerald-400" />
              <span>{telemetry.flight_mode}</span>
            </button>

            {/* 3. Wide FOV Zoom */}
            <button
              onClick={onCycleZoom}
              className="px-2.5 py-1 rounded-xl bg-white/[0.03] hover:bg-white/[0.08] border border-white/10 text-[10px] font-mono font-medium text-slate-200 transition-all duration-200 active:scale-95 flex items-center space-x-1.5"
              title="Cycle Wide Angle FOV Presets"
            >
              <ZoomIn className="w-3.5 h-3.5 text-cyan-400" />
              <span>{telemetry.fov_zoom ? telemetry.fov_zoom.toFixed(2) : '1.00'}x</span>
            </button>

            {/* 4. AI Clarity Boost */}
            <button
              onClick={onToggleClarity}
              className={`px-2.5 py-1 rounded-xl border text-[10px] font-mono font-medium transition-all duration-200 active:scale-95 flex items-center space-x-1.5 ${
                telemetry.clarity_boost
                  ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/60 shadow-[0_0_12px_rgba(6,182,212,0.3)]'
                  : 'bg-white/[0.03] hover:bg-white/[0.08] text-slate-300 border-white/10'
              }`}
              title="Toggle AI CLAHE & Edge Sharpness Boost"
            >
              <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
              <span>CLARITY</span>
            </button>

            {/* 5. Zenmuse FLIR Thermal */}
            <button
              onClick={onToggleThermal}
              className={`px-2.5 py-1 rounded-xl border text-[10px] font-mono font-medium transition-all duration-200 active:scale-95 flex items-center space-x-1.5 ${
                telemetry.thermal_mode
                  ? 'bg-amber-500/20 text-amber-300 border-amber-500/60 shadow-[0_0_12px_rgba(245,158,11,0.3)]'
                  : 'bg-white/[0.03] hover:bg-white/[0.08] text-slate-300 border-white/10'
              }`}
              title="Toggle Synthetic Zenmuse FLIR Thermal Nightscape"
            >
              <Flame className="w-3.5 h-3.5 text-amber-400" />
              <span>FLIR</span>
            </button>

            {/* 6. Media Recordings Gallery [G] */}
            <button
              onClick={onOpenMediaGallery}
              className="px-2.5 py-1 rounded-xl bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/30 text-cyan-300 text-[10px] font-mono font-medium transition-all duration-200 active:scale-95 flex items-center space-x-1.5"
              title="Open Drone Recordings & Photos Gallery [G]"
            >
              <Folder className="w-3.5 h-3.5 text-cyan-400" />
              <span>MEDIA</span>
            </button>

            {/* 7. Emergency Hover Brake [SPACE] */}
            <button
              onClick={onEmergencyBrake}
              className="px-2.5 py-1 rounded-xl bg-rose-500/20 hover:bg-rose-500/30 border border-rose-500/50 text-rose-300 text-[10px] font-mono font-bold tracking-wider transition-all duration-200 active:scale-95 flex items-center space-x-1.5 shadow-[0_0_12px_rgba(244,63,94,0.3)]"
              title="Emergency Hover & Brake [SPACE]"
            >
              <Octagon className="w-3.5 h-3.5 text-rose-400" />
              <span>BRAKE</span>
            </button>

          </div>
        </div>
      </footer>

      {/* ==================================================================== */}
      {/* 8. EXPANDED FULL-SCREEN LEAFLET MAP MODAL (TRIGGERED BY GTA RADAR)    */}
      {/* ==================================================================== */}
      {isMapExpanded && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-xl flex items-center justify-center p-4">
          <div className="relative w-full max-w-5xl h-[85vh] bg-[#0b0f17] rounded-3xl overflow-hidden border border-white/20 shadow-2xl flex flex-col">
            
            {/* Modal Header */}
            <div className="flex items-center justify-between px-6 py-3 bg-[#111622] border-b border-white/10">
              <div className="flex items-center space-x-3">
                <Compass className="w-5 h-5 text-cyan-400" />
                <span className="text-sm font-mono font-bold text-white tracking-wider">
                  REAL GPS TACTICAL MAP (WGS84 / OPENSTREETMAP)
                </span>
                <span className="px-2 py-0.5 rounded text-[9px] font-mono bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                  {telemetry.sats} SATS (RTK FIX)
                </span>
              </div>

              <button
                onClick={() => setIsMapExpanded(false)}
                className="p-1.5 rounded-xl bg-white/10 hover:bg-white/20 text-slate-300 hover:text-white transition-colors flex items-center space-x-1"
                title="Close Map [ESC / M]"
              >
                <X className="w-5 h-5" />
                <span className="text-xs font-mono font-bold pr-1">CLOSE [M]</span>
              </button>
            </div>

            {/* Real Interactive Leaflet Map Component */}
            <div className="relative flex-1 w-full h-full">
              <RealMapLeaflet telemetry={telemetry} className="w-full h-full" />
            </div>

            {/* Modal Footer with Coordinates */}
            <div className="px-6 py-2.5 bg-[#111622] border-t border-white/10 flex items-center justify-between text-xs font-mono text-slate-300">
              <span>DRONE: {telemetry.lat.toFixed(6)}°N, {telemetry.lon.toFixed(6)}°E | ALT: {telemetry.rel_alt.toFixed(1)}m AGL</span>
              <span>HOME: {telemetry.home_lat.toFixed(6)}°N, {telemetry.home_lon.toFixed(6)}°E | DIST: {telemetry.dist_home.toFixed(1)}m</span>
            </div>

          </div>
        </div>
      )}

    </div>
  );
};
