import React, { useState } from 'react';
import { DroneTelemetry } from '../types';
import { 
  X, 
  Radio, 
  Search, 
  Video, 
  RefreshCw, 
  CheckCircle2, 
  AlertCircle, 
  Wifi, 
  Server 
} from 'lucide-react';

interface EasyConnectDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  telemetry: DroneTelemetry;
  onScanSubnet: () => void;
  onSwitchSource: (source: string) => void;
}

export const EasyConnectDrawer: React.FC<EasyConnectDrawerProps> = ({
  isOpen,
  onClose,
  telemetry,
  onScanSubnet,
  onSwitchSource,
}) => {
  const [customIp, setCustomIp] = useState('192.168.31.16');
  const [isTesting, setIsTesting] = useState(false);
  const [testResult, setTestResult] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleTestConnect = async () => {
    setIsTesting(true);
    setTestResult(null);
    try {
      const res = await fetch(`/api/command/test_ip?ip=${customIp}`);
      const data = await res.json();
      if (data.ok) {
        setTestResult(`Success! Found ${data.type}`);
        if (data.type && data.type.includes('Stream')) {
          onSwitchSource(`http://${customIp}:81/stream`);
        } else {
          onSwitchSource(`http://${customIp}/capture`);
        }
      } else {
        setTestResult(`Failed: ${data.error || 'Unreachable'}`);
      }
    } catch (e) {
      setTestResult('Network error or server offline');
    } finally {
      setIsTesting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex justify-end pointer-events-auto bg-black/60 backdrop-blur-sm transition-all duration-300">
      <div className="relative w-full max-w-md h-full bg-[#0a0e16]/95 border-l border-white/10 shadow-2xl p-6 flex flex-col justify-between overflow-y-auto">
        
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-white/10">
          <div className="flex items-center space-x-2">
            <Radio className="w-5 h-5 text-cyan-400 animate-pulse" />
            <h2 className="text-sm font-mono font-bold tracking-wider text-slate-100 uppercase">
              Easy-Connect Link Manager
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-white/10 text-slate-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 py-6 space-y-6">
          
          {/* Active Connection Card */}
          <div className="p-4 rounded-xl bg-white/[0.02] border border-white/5 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-mono text-slate-400 uppercase">Current Source</span>
              <span className="px-2 py-0.5 rounded text-[9px] font-mono bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                ACTIVE
              </span>
            </div>
            <div className="text-sm font-mono font-bold text-cyan-300 break-all">
              {telemetry.camera_source}
            </div>
            <div className="grid grid-cols-3 gap-2 pt-2 border-t border-white/5">
              <div className="flex flex-col">
                <span className="text-[9px] font-mono text-slate-500">Latency</span>
                <span className="text-[11px] font-mono text-slate-200">{telemetry.ping_ms.toFixed(0)} ms</span>
              </div>
              <div className="flex flex-col">
                <span className="text-[9px] font-mono text-slate-500">Link Signal</span>
                <span className="text-[11px] font-mono text-slate-200">{telemetry.signal_pct}%</span>
              </div>
              <div className="flex flex-col">
                <span className="text-[9px] font-mono text-slate-500">Video Rate</span>
                <span className="text-[11px] font-mono text-slate-200">{telemetry.fps.toFixed(0)} FPS</span>
              </div>
            </div>
          </div>

          {/* Quick Connect Actions */}
          <div className="space-y-3">
            <h3 className="text-xs font-mono font-bold tracking-wider text-slate-300 uppercase">
              Quick Switching Presets
            </h3>
            
            <button
              onClick={() => onSwitchSource('http://192.168.31.16:81/stream')}
              className="w-full px-4 py-3 rounded-xl bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/30 text-cyan-300 text-xs font-mono font-semibold transition-all active:scale-[0.98] flex items-center justify-between group"
            >
              <div className="flex items-center space-x-2">
                <Radio className="w-4 h-4 text-cyan-400 group-hover:animate-pulse" />
                <span>ESP32-CAM Stream (Port 81)</span>
              </div>
              <span className="text-[9px] text-emerald-400 font-bold">Zero-Lag</span>
            </button>

            <button
              onClick={onScanSubnet}
              className="w-full px-4 py-3 rounded-xl bg-white/[0.02] hover:bg-white/[0.06] border border-white/10 text-slate-200 text-xs font-mono font-semibold transition-all active:scale-[0.98] flex items-center justify-between group"
            >
              <div className="flex items-center space-x-2">
                <Search className="w-4 h-4 text-cyan-400 group-hover:animate-spin" />
                <span>Auto-Scan Subnet (192.168.31.0/24)</span>
              </div>
              <span className="text-[9px] text-slate-400">1.8s Scan</span>
            </button>

            <button
              onClick={() => onSwitchSource('http://192.168.31.16/capture')}
              className="w-full px-4 py-3 rounded-xl bg-white/[0.02] hover:bg-white/[0.06] border border-white/10 text-slate-200 text-xs font-mono font-semibold transition-all active:scale-[0.98] flex items-center justify-between"
            >
              <div className="flex items-center space-x-2">
                <RefreshCw className="w-4 h-4 text-amber-400" />
                <span>Direct /capture Snapshot Mode</span>
              </div>
              <span className="text-[9px] text-slate-400">Port 80</span>
            </button>

            <button
              onClick={() => onSwitchSource('webcam')}
              className="w-full px-4 py-3 rounded-xl bg-white/[0.02] hover:bg-white/[0.06] border border-white/10 text-slate-200 text-xs font-mono font-semibold transition-all active:scale-[0.98] flex items-center justify-between"
            >
              <div className="flex items-center space-x-2">
                <Video className="w-4 h-4 text-emerald-400" />
                <span>Local Webcam 0 (/dev/video0)</span>
              </div>
              <span className="text-[9px] text-slate-400">720P HD</span>
            </button>
          </div>

          {/* Manual IP Input */}
          <div className="space-y-3 pt-2">
            <h3 className="text-xs font-mono font-bold tracking-wider text-slate-300 uppercase">
              Manual Device IP
            </h3>
            <div className="flex space-x-2">
              <input
                type="text"
                value={customIp}
                onChange={(e) => setCustomIp(e.target.value)}
                placeholder="192.168.31.16"
                className="flex-1 px-3 py-2 bg-black/40 border border-white/10 rounded-xl text-xs font-mono text-slate-200 focus:outline-none focus:border-cyan-400"
              />
              <button
                onClick={handleTestConnect}
                disabled={isTesting}
                className="px-4 py-2 bg-cyan-500 hover:bg-cyan-400 text-black font-mono font-bold text-xs rounded-xl transition-all active:scale-95 disabled:opacity-50"
              >
                {isTesting ? 'TESTING...' : 'CONNECT'}
              </button>
            </div>
            {testResult && (
              <div className="text-[10px] font-mono text-cyan-300">
                {testResult}
              </div>
            )}
          </div>

        </div>

        {/* Footer */}
        <div className="pt-4 border-t border-white/10 flex items-center justify-between text-[9px] font-mono text-slate-500">
          <span>MINI GCS LINK PROTOCOL V2</span>
          <span>RTX 5060 HW ACCEL</span>
        </div>

      </div>
    </div>
  );
};
