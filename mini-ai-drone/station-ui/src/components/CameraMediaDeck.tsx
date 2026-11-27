import React, { useState } from 'react';
import { DroneTelemetry } from '../types';
import { 
  Camera, 
  Video, 
  Square, 
  Disc, 
  HardDrive, 
  Sliders, 
  ChevronUp, 
  ChevronDown 
} from 'lucide-react';

interface MediaDeckProps {
  telemetry: DroneTelemetry;
  onToggleRecord: () => void;
  onCapturePhoto: () => void;
}

export const CameraMediaDeck: React.FC<MediaDeckProps> = ({
  telemetry,
  onToggleRecord,
  onCapturePhoto
}) => {
  const [gimbalPitch, setGimbalPitch] = useState<number>(-15);

  const handlePitchChange = (delta: number) => {
    setGimbalPitch((prev) => Math.max(-90, Math.min(0, prev + delta)));
  };

  return (
    <div className="absolute right-3 top-1/2 -translate-y-1/2 z-20 flex flex-col items-center space-y-3 pointer-events-auto">
      
      {/* Double-Bezel Container */}
      <div className="p-1.5 rounded-2xl bg-white/[0.03] backdrop-blur-2xl ring-1 ring-white/10 shadow-[0_8px_32px_rgba(0,0,0,0.5)]">
        <div className="flex flex-col items-center p-2.5 bg-[#0b0f17]/90 rounded-[calc(1rem-0.25rem)] border border-white/5 space-y-4">
          
          {/* 1. Big Red Record Button [R] */}
          <div className="flex flex-col items-center space-y-1">
            <button
              onClick={onToggleRecord}
              className={`relative w-12 h-12 rounded-full border-2 transition-all duration-300 flex items-center justify-center active:scale-95 group ${
                telemetry.is_recording
                  ? 'border-rose-500 shadow-[0_0_20px_rgba(244,63,94,0.6)] bg-rose-500/10'
                  : 'border-slate-300 hover:border-white shadow-lg bg-white/5'
              }`}
              title="Start/Stop Video Recording [R]"
            >
              {telemetry.is_recording ? (
                <Square className="w-5 h-5 fill-rose-500 text-rose-500 animate-pulse" />
              ) : (
                <div className="w-5 h-5 rounded-full bg-rose-500 shadow-[0_0_8px_#f43f5e] group-hover:scale-110 transition-transform" />
              )}
            </button>

            {/* Recording Timer Badge */}
            {telemetry.is_recording && (
              <span className="px-1.5 py-0.5 rounded text-[8px] font-mono font-bold bg-rose-500/20 text-rose-400 border border-rose-500/40 animate-pulse">
                {telemetry.record_duration}
              </span>
            )}
          </div>

          <div className="w-8 h-[1px] bg-white/10" />

          {/* 2. White Photo Shutter Button [P] */}
          <button
            onClick={onCapturePhoto}
            className="w-10 h-10 rounded-full border-2 border-white/80 hover:border-white bg-white/10 flex items-center justify-center transition-all duration-200 active:scale-90 shadow-md group"
            title="Capture High-Res Photo [P]"
          >
            <div className="w-6 h-6 rounded-full bg-white shadow-[0_0_10px_rgba(255,255,255,0.8)] group-hover:scale-105 transition-transform" />
          </button>

          <div className="w-8 h-[1px] bg-white/10" />

          {/* 3. Gimbal Pitch Dial */}
          <div className="flex flex-col items-center space-y-1">
            <button
              onClick={() => handlePitchChange(5)}
              className="p-1 rounded hover:bg-white/10 text-slate-400 hover:text-white transition-colors"
              title="Pitch Gimbal Up"
            >
              <ChevronUp className="w-4 h-4" />
            </button>

            <div className="flex flex-col items-center">
              <span className="text-[9px] font-mono font-bold text-cyan-300">
                {gimbalPitch}°
              </span>
              <span className="text-[7px] font-mono text-slate-500 uppercase">
                GIMBAL
              </span>
            </div>

            <button
              onClick={() => handlePitchChange(-5)}
              className="p-1 rounded hover:bg-white/10 text-slate-400 hover:text-white transition-colors"
              title="Pitch Gimbal Down"
            >
              <ChevronDown className="w-4 h-4" />
            </button>
          </div>

          <div className="w-8 h-[1px] bg-white/10" />

          {/* 4. Storage & Format Meter */}
          <div className="flex flex-col items-center text-center space-y-0.5">
            <HardDrive className="w-3.5 h-3.5 text-slate-400" />
            <span className="text-[8px] font-mono text-slate-300 font-medium">48.2 GB</span>
            <span className="text-[7px] font-mono text-cyan-400">4K 60P</span>
          </div>

        </div>
      </div>
    </div>
  );
};
