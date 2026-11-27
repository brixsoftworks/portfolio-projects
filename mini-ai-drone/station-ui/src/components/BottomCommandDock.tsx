import React from 'react';
import { DroneTelemetry } from '../types';
import { 
  Home, 
  Zap, 
  ZoomIn, 
  Sparkles, 
  Flame, 
  Radio, 
  Map as MapIcon, 
  Octagon, 
  Camera 
} from 'lucide-react';

interface CommandDockProps {
  telemetry: DroneTelemetry;
  onToggleRth: () => void;
  onCycleMode: () => void;
  onCycleZoom: () => void;
  onToggleClarity: () => void;
  onToggleThermal: () => void;
  onScanSubnet: () => void;
  onToggleMapSwap: () => void;
  onEmergencyBrake: () => void;
}

export const BottomCommandDock: React.FC<CommandDockProps> = ({
  telemetry,
  onToggleRth,
  onCycleMode,
  onCycleZoom,
  onToggleClarity,
  onToggleThermal,
  onScanSubnet,
  onToggleMapSwap,
  onEmergencyBrake,
}) => {
  return (
    <footer className="relative z-30 px-3 pb-3 w-full flex justify-center pointer-events-auto">
      {/* Outer Double-Bezel Shell */}
      <div className="p-1 rounded-2xl bg-white/[0.03] backdrop-blur-2xl ring-1 ring-white/10 shadow-[0_8px_32px_rgba(0,0,0,0.5)]">
        {/* Inner Content Core */}
        <div className="flex items-center space-x-1.5 px-3 py-1.5 bg-[#0b0f17]/90 rounded-[calc(1rem-0.25rem)] border border-white/5">
          
          {/* 1. Return-To-Home (RTH) Button */}
          <button
            onClick={onToggleRth}
            className={`px-3 py-1.5 rounded-xl border text-[11px] font-mono font-bold tracking-wider transition-all duration-300 active:scale-95 flex items-center space-x-2 group ${
              telemetry.flight_mode === 'RTH'
                ? 'bg-fuchsia-500/20 text-fuchsia-300 border-fuchsia-500/60 shadow-[0_0_15px_rgba(217,70,239,0.4)] animate-pulse'
                : 'bg-white/[0.03] hover:bg-white/[0.08] text-slate-200 border-white/10'
            }`}
            title="Engage Autonomous Return-To-Home [H]"
          >
            <div className="w-5 h-5 rounded-lg bg-fuchsia-500/20 border border-fuchsia-500/40 flex items-center justify-center">
              <Home className="w-3 h-3 text-fuchsia-400 group-hover:scale-110 transition-transform" />
            </div>
            <span>RTH</span>
          </button>

          {/* 2. Mode Selector */}
          <button
            onClick={onCycleMode}
            className="px-3 py-1.5 rounded-xl bg-white/[0.03] hover:bg-white/[0.08] border border-white/10 text-[11px] font-mono font-medium text-slate-200 transition-all duration-300 active:scale-95 flex items-center space-x-2 group"
            title="Cycle Mode: Normal / Sport / Cine"
          >
            <div className="w-5 h-5 rounded-lg bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center">
              <Zap className="w-3 h-3 text-emerald-400 group-hover:scale-110 transition-transform" />
            </div>
            <span>{telemetry.flight_mode}</span>
          </button>

          {/* 3. Wide FOV Zoom */}
          <button
            onClick={onCycleZoom}
            className="px-3 py-1.5 rounded-xl bg-white/[0.03] hover:bg-white/[0.08] border border-white/10 text-[11px] font-mono font-medium text-slate-200 transition-all duration-300 active:scale-95 flex items-center space-x-2 group"
            title="Cycle Wide Angle FOV Presets"
          >
            <div className="w-5 h-5 rounded-lg bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center">
              <ZoomIn className="w-3 h-3 text-cyan-400 group-hover:scale-110 transition-transform" />
            </div>
            <span>{telemetry.fov_zoom.toFixed(2)}x FOV</span>
          </button>

          {/* 4. AI Clarity Boost */}
          <button
            onClick={onToggleClarity}
            className={`px-3 py-1.5 rounded-xl border text-[11px] font-mono font-medium transition-all duration-300 active:scale-95 flex items-center space-x-2 group ${
              telemetry.clarity_boost
                ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/60 shadow-[0_0_12px_rgba(6,182,212,0.3)]'
                : 'bg-white/[0.03] hover:bg-white/[0.08] text-slate-300 border-white/10'
            }`}
            title="Toggle AI CLAHE & Edge Sharpness Boost"
          >
            <div className="w-5 h-5 rounded-lg bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center">
              <Sparkles className="w-3 h-3 text-cyan-400 group-hover:scale-110 transition-transform" />
            </div>
            <span>CLARITY</span>
          </button>

          {/* 5. Zenmuse FLIR Thermal */}
          <button
            onClick={onToggleThermal}
            className={`px-3 py-1.5 rounded-xl border text-[11px] font-mono font-medium transition-all duration-300 active:scale-95 flex items-center space-x-2 group ${
              telemetry.thermal_mode
                ? 'bg-amber-500/20 text-amber-300 border-amber-500/60 shadow-[0_0_12px_rgba(245,158,11,0.3)]'
                : 'bg-white/[0.03] hover:bg-white/[0.08] text-slate-300 border-white/10'
            }`}
            title="Toggle Synthetic Zenmuse FLIR Thermal Nightscape"
          >
            <div className="w-5 h-5 rounded-lg bg-amber-500/20 border border-amber-500/40 flex items-center justify-center">
              <Flame className="w-3 h-3 text-amber-400 group-hover:scale-110 transition-transform" />
            </div>
            <span>FLIR</span>
          </button>

          {/* 6. Easy-Connect Subnet Auto-Scan */}
          <button
            onClick={onScanSubnet}
            className="px-3 py-1.5 rounded-xl bg-white/[0.03] hover:bg-white/[0.08] border border-white/10 text-[11px] font-mono font-medium text-slate-200 transition-all duration-300 active:scale-95 flex items-center space-x-2 group"
            title="Auto-Scan Subnet (192.168.31.0/24) for ESP32-CAM"
          >
            <div className="w-5 h-5 rounded-lg bg-purple-500/20 border border-purple-500/40 flex items-center justify-center">
              <Radio className="w-3 h-3 text-purple-400 group-hover:animate-pulse" />
            </div>
            <span>SCAN CAM</span>
          </button>

          {/* 7. PIP Map / Camera Viewport Swap */}
          <button
            onClick={onToggleMapSwap}
            className="px-3 py-1.5 rounded-xl bg-white/[0.03] hover:bg-white/[0.08] border border-white/10 text-[11px] font-mono font-medium text-slate-200 transition-all duration-300 active:scale-95 flex items-center space-x-2 group"
            title="Swap Fullscreen Map <-> Fullscreen Camera [TAB / N]"
          >
            <div className="w-5 h-5 rounded-lg bg-blue-500/20 border border-blue-500/40 flex items-center justify-center">
              <MapIcon className="w-3 h-3 text-blue-400 group-hover:scale-110 transition-transform" />
            </div>
            <span>MAP SWAP</span>
          </button>

          {/* 8. Emergency Brake & Hover */}
          <button
            onClick={onEmergencyBrake}
            className="px-3 py-1.5 rounded-xl bg-rose-500/20 hover:bg-rose-500/30 border border-rose-500/50 text-rose-300 text-[11px] font-mono font-bold tracking-wider transition-all duration-300 active:scale-95 flex items-center space-x-2 group shadow-[0_0_12px_rgba(244,63,94,0.3)]"
            title="Emergency Hover & Brake [SPACE]"
          >
            <div className="w-5 h-5 rounded-lg bg-rose-500/30 border border-rose-500/60 flex items-center justify-center">
              <Octagon className="w-3 h-3 text-rose-400 group-hover:scale-110 transition-transform" />
            </div>
            <span>BRAKE</span>
          </button>

        </div>
      </div>
    </footer>
  );
};
