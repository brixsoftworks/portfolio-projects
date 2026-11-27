import React from 'react';
import { DroneTelemetry } from '../types';
import { 
  Wifi, 
  Radio, 
  ShieldCheck, 
  Clock, 
  Activity, 
  Satellite, 
  BatteryMedium, 
  Cpu
} from 'lucide-react';

interface TopRibbonProps {
  telemetry: DroneTelemetry;
  onCycleMode: () => void;
  onOpenConnectDrawer: () => void;
}

export const TopRibbon: React.FC<TopRibbonProps> = ({
  telemetry,
  onCycleMode,
  onOpenConnectDrawer
}) => {
  const modeColors = {
    'N-MODE': 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30 shadow-[0_0_15px_rgba(16,185,129,0.2)]',
    'S-MODE': 'bg-amber-500/10 text-amber-400 border-amber-500/30 shadow-[0_0_15px_rgba(245,158,11,0.2)]',
    'C-MODE': 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30 shadow-[0_0_15px_rgba(6,182,212,0.2)]',
    'RTH': 'bg-fuchsia-500/15 text-fuchsia-300 border-fuchsia-500/40 animate-pulse shadow-[0_0_20px_rgba(217,70,239,0.3)]'
  };

  const getBatteryColor = (pct: number) => {
    if (pct > 30) return 'bg-emerald-400';
    if (pct > 15) return 'bg-amber-400';
    return 'bg-rose-500 animate-pulse';
  };

  return (
    <header className="relative z-30 px-3 py-2 w-full">
      {/* Outer Double-Bezel Shell */}
      <div className="p-1 rounded-2xl bg-white/[0.03] backdrop-blur-2xl ring-1 ring-white/10 shadow-[0_8px_32px_rgba(0,0,0,0.5)]">
        {/* Inner Content Core */}
        <div className="flex items-center justify-between px-3.5 py-1.5 bg-[#0b0f17]/90 rounded-[calc(1rem-0.25rem)] border border-white/5">
          
          {/* Left Group: Brand & Mode & GNSS */}
          <div className="flex items-center space-x-3">
            {/* Logo / Brand */}
            <div className="flex items-center space-x-2">
              <div className="w-6 h-6 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center">
                <Activity className="w-3.5 h-3.5 text-cyan-400" />
              </div>
              <div className="flex flex-col">
                <span className="text-[11px] font-extrabold tracking-widest text-slate-100 uppercase font-mono">
                  MINI GCS
                </span>
                <span className="text-[8px] tracking-wider text-slate-500 uppercase -mt-0.5">
                  ENTERPRISE
                </span>
              </div>
            </div>

            <div className="h-4 w-[1px] bg-white/10" />

            {/* Flight Mode Pill Button */}
            <button
              onClick={onCycleMode}
              className={`px-2.5 py-1 rounded-lg border text-[11px] font-mono font-bold tracking-wider transition-all duration-300 active:scale-95 flex items-center space-x-1.5 ${modeColors[telemetry.flight_mode] || modeColors['N-MODE']}`}
              title="Click to cycle flight mode (N-Mode / S-Mode / C-Mode)"
            >
              <span className="w-1.5 h-1.5 rounded-full bg-current animate-ping" />
              <span>{telemetry.flight_mode}</span>
            </button>

            {/* GNSS Satellite Status */}
            <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-lg bg-white/[0.02] border border-white/5 text-slate-300">
              <Satellite className="w-3.5 h-3.5 text-cyan-400" />
              <span className="text-[10px] font-mono text-cyan-300 font-medium">
                {telemetry.sats} SATS
              </span>
              <span className="px-1 py-0.2 rounded text-[8px] font-mono bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                RTK FIX
              </span>
            </div>
          </div>

          {/* Center Group: Smart Battery & OcuSync Link */}
          <div className="flex items-center space-x-4">
            {/* Smart Battery Telemetry */}
            <div className="flex items-center space-x-2 px-3 py-1 rounded-xl bg-white/[0.02] border border-white/5">
              <BatteryMedium className="w-4 h-4 text-emerald-400" />
              
              <div className="flex flex-col">
                <div className="flex items-center space-x-2">
                  <span className="text-[11px] font-mono font-bold text-slate-100">
                    {telemetry.battery_pct.toFixed(0)}%
                  </span>
                  <span className="text-[10px] font-mono text-slate-400">
                    {telemetry.remaining_flight_time}
                  </span>
                  <span className="text-[9px] font-mono text-slate-500">
                    {telemetry.battery_voltage.toFixed(1)}V
                  </span>
                </div>

                {/* Segmented Battery Progress Bar with RTH Indicator */}
                <div className="relative w-36 h-1.5 bg-slate-800 rounded-full overflow-hidden mt-0.5">
                  <div 
                    className={`h-full transition-all duration-300 ${getBatteryColor(telemetry.battery_pct)}`}
                    style={{ width: `${telemetry.battery_pct}%` }}
                  />
                  {/* Dynamic RTH Threshold Marker */}
                  <div 
                    className="absolute top-0 bottom-0 w-[2px] bg-amber-400 shadow-[0_0_4px_#f59e0b]"
                    style={{ left: `${telemetry.rth_threshold_pct}%` }}
                    title={`RTH Reserve Threshold: ${telemetry.rth_threshold_pct.toFixed(0)}%`}
                  />
                </div>
              </div>
            </div>

            {/* OcuSync 3+ Transmission Link */}
            <div className="flex items-center space-x-2 px-2.5 py-1 rounded-xl bg-white/[0.02] border border-white/5">
              <div className="flex items-end space-x-0.5 h-3">
                {[1, 2, 3, 4, 5].map((bar) => (
                  <div 
                    key={bar}
                    className={`w-1 rounded-t-sm transition-all ${
                      bar <= Math.ceil(telemetry.signal_pct / 20)
                        ? 'bg-cyan-400 shadow-[0_0_6px_rgba(6,182,212,0.5)]'
                        : 'bg-slate-700'
                    }`}
                    style={{ height: `${bar * 20}%` }}
                  />
                ))}
              </div>
              <div className="flex flex-col text-[9px] font-mono text-slate-400">
                <span className="text-slate-200 font-semibold">5.8G | 28.5 Mbps</span>
                <span className="text-cyan-400/80">{telemetry.ping_ms.toFixed(0)} ms latency</span>
              </div>
            </div>

            {/* APAS 5.0 Sensor Shield */}
            <div className="hidden lg:flex items-center space-x-1.5 px-2.5 py-1 rounded-xl bg-white/[0.02] border border-white/5 text-slate-300">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span className="text-[10px] font-mono text-slate-300">
                APAS 5.0: <span className="text-emerald-400">ACTIVE</span>
              </span>
            </div>
          </div>

          {/* Right Group: Connection Pill & Clock */}
          <div className="flex items-center space-x-3">
            {/* Interactive Easy-Connect Pill Button */}
            <button
              onClick={onOpenConnectDrawer}
              className="px-2.5 py-1 rounded-xl bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/30 text-cyan-300 transition-all duration-300 active:scale-95 flex items-center space-x-1.5 group"
              title="Click to configure camera connection, scan subnet, or switch to webcam"
            >
              <Radio className="w-3.5 h-3.5 text-cyan-400 group-hover:animate-pulse" />
              <span className="text-[10px] font-mono font-medium truncate max-w-[140px]">
                {telemetry.camera_source}
              </span>
            </button>

            {/* Mission Clock */}
            <div className="flex items-center space-x-1 px-2.5 py-1 rounded-lg bg-white/[0.02] border border-white/5 text-slate-400">
              <Clock className="w-3 h-3 text-slate-500" />
              <span className="text-[10px] font-mono text-slate-300">
                {new Date().toLocaleTimeString()}
              </span>
            </div>
          </div>

        </div>
      </div>
    </header>
  );
};
