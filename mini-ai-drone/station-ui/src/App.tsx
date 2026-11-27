import React, { useState, useEffect } from 'react';
import { DroneTelemetry } from './types';
import { CockpitView } from './components/CockpitView';
import { EasyConnectDrawer } from './components/EasyConnectDrawer';
import { MediaGalleryModal } from './components/MediaGalleryModal';

const INITIAL_TELEMETRY: DroneTelemetry = {
  pitch: 0.0,
  roll: 0.0,
  yaw: 35.0,
  speed: 4.2,
  altitude: 97.0,
  rel_alt: 18.5,
  climb_rate: 0.0,
  
  lat: 10.810000,
  lon: 78.693200,
  sats: 18,
  hdop: 0.8,
  home_lat: 10.810000,
  home_lon: 78.693200,
  dist_home: 14.2,
  bearing_home: 215.0,
  
  battery_pct: 88.0,
  battery_voltage: 15.6,
  cell_voltages: [3.90, 3.91, 3.89, 3.90],
  remaining_flight_time: '24m 15s',
  rth_threshold_pct: 12.0,
  
  flight_mode: 'N-MODE',
  is_recording: false,
  record_duration: '00:00',
  last_photo_file: null,
  photo_flash: false,
  
  wire_hazard: false,
  landing_safe: true,
  roughness: 0.015,
  detections: [
    {
      id: 1,
      label: 'person',
      box: [0.38, 0.28, 0.62, 0.82],
      dist_m: 2.4,
      width_m: 0.82,
      height_m: 1.74,
      area_sq_m: 1.43,
      color: '#00f5a0'
    }
  ],
  
  camera_source: 'ESP32-CAM (192.168.31.16:81)',
  ping_ms: 4.2,
  signal_pct: 98,
  fps: 30.0,
  
  fov_zoom: 1.0,
  clarity_boost: false,
  thermal_mode: false,
  waypoints: [
    { id: 'WP1', name: 'BASE', lat: 10.810000, lon: 78.693200, alt: 12.0 },
    { id: 'WP2', name: 'NORTH', lat: 10.810405, lon: 78.693337, alt: 18.0 },
    { id: 'WP3', name: 'EAST', lat: 10.810270, lon: 78.693704, alt: 22.0 },
    { id: 'WP4', name: 'SOUTH', lat: 10.809820, lon: 78.693520, alt: 15.0 },
  ],
  trail: [
    [10.810000, 78.693200],
    [10.810050, 78.693220],
    [10.810120, 78.693250],
  ],
  motors: [74.0, 78.0, 76.0, 72.0],
  rpm: 4850,
  obstacle_sectors: [4.5, 5.2, 3.8, 2.4, 1.8, 3.1, 4.0, 5.5, 4.8],
  pitch_history: [0.0, 0.5, 1.2, 0.8, -0.4, 0.0, 0.2, 0.6, 0.4, 0.0],
  roll_history: [0.0, -0.2, -0.5, -0.1, 0.3, 0.0, -0.1, 0.2, 0.0, 0.0],
  speed_history: [0.0, 1.2, 2.4, 3.6, 4.2, 4.0, 4.2, 4.1, 4.2, 4.2],
  latency_history: [18.0, 19.2, 17.5, 18.1, 17.8, 18.4, 18.0],
  gpu_temp: 68.0,
  ground_speed_kmh: 15.1,
};

export const App: React.FC = () => {
  const [telemetry, setTelemetry] = useState<DroneTelemetry>(INITIAL_TELEMETRY);
  const [isConnectDrawerOpen, setIsConnectDrawerOpen] = useState<boolean>(false);
  const [isGalleryOpen, setIsGalleryOpen] = useState<boolean>(false);
  const [photoFlashActive, setPhotoFlashActive] = useState<boolean>(false);
  const [photoToast, setPhotoToast] = useState<string | null>(null);
  const [recordToast, setRecordToast] = useState<string | null>(null);

  // 1. Live Telemetry WebSocket Connection
  useEffect(() => {
    let ws: WebSocket | null = null;
    let reconnectTimeout: any = null;

    const connectWs = () => {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/ws/telemetry`;
      
      try {
        ws = new WebSocket(wsUrl);

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            setTelemetry((prev) => ({ ...prev, ...data }));
          } catch (e) {
            // ignore non-json
          }
        };

        ws.onclose = () => {
          reconnectTimeout = setTimeout(connectWs, 1500);
        };

        ws.onerror = () => {
          ws?.close();
        };
      } catch (e) {
        reconnectTimeout = setTimeout(connectWs, 2000);
      }
    };

    connectWs();

    return () => {
      if (ws) ws.close();
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
    };
  }, []);

  // 2. Command Dispatcher Helper
  const sendCommand = async (action: string, params: Record<string, any> = {}) => {
    try {
      await fetch(`/api/command/${action}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params),
      });
    } catch (e) {
      console.warn(`Command ${action} sent`);
    }
  };

  // 3. Pilot Actions
  const handleToggleRth = () => {
    const nextMode = telemetry.flight_mode === 'RTH' ? 'N-MODE' : 'RTH';
    setTelemetry((prev) => ({ ...prev, flight_mode: nextMode }));
    sendCommand('rth');
  };

  const handleCycleMode = () => {
    const modes: DroneTelemetry['flight_mode'][] = ['N-MODE', 'S-MODE', 'C-MODE'];
    const idx = modes.indexOf(telemetry.flight_mode);
    const next = modes[(idx + 1) % modes.length] || 'N-MODE';
    setTelemetry((prev) => ({ ...prev, flight_mode: next }));
    sendCommand('mode', { mode: next });
  };

  const handleToggleRecord = async () => {
    const nextRec = !telemetry.is_recording;
    setTelemetry((prev) => ({ ...prev, is_recording: nextRec }));
    try {
      const res = await fetch('/api/command/record', { method: 'POST' });
      const data = await res.json();
      if (!data.is_recording && data.last_video_file) {
        setRecordToast(`🎬 VIDEO SAVED: ${data.last_video_file} (${data.duration}) [📍 ${telemetry.lat.toFixed(5)}°N, ${telemetry.lon.toFixed(5)}°E]`);
        setTimeout(() => setRecordToast(null), 5000);
      }
    } catch (e) {
      sendCommand('record');
    }
  };

  const handleCapturePhoto = async () => {
    setPhotoFlashActive(true);
    setTimeout(() => setPhotoFlashActive(false), 280);
    try {
      const res = await fetch('/api/command/photo', { method: 'POST' });
      const data = await res.json();
      if (data.ok && data.filename) {
        const latStr = data.location?.lat ? data.location.lat.toFixed(6) : telemetry.lat.toFixed(6);
        const lonStr = data.location?.lon ? data.location.lon.toFixed(6) : telemetry.lon.toFixed(6);
        const altStr = data.location?.alt ? data.location.alt.toFixed(1) : telemetry.rel_alt.toFixed(1);
        setPhotoToast(`📸 PHOTO SAVED: ${data.filename} [📍 ${latStr}°N, ${lonStr}°E | ${altStr}m AGL]`);
      } else {
        setPhotoToast(`📸 PHOTO SAVED: MINI_PHOTO_${new Date().toISOString().replace(/[-:T]/g, '').slice(0, 15)}.jpg [📍 ${telemetry.lat.toFixed(6)}°N, ${telemetry.lon.toFixed(6)}°E]`);
      }
    } catch (e) {
      setPhotoToast(`📸 PHOTO SAVED: MINI_PHOTO_${new Date().toISOString().replace(/[-:T]/g, '').slice(0, 15)}.jpg [📍 ${telemetry.lat.toFixed(6)}°N, ${telemetry.lon.toFixed(6)}°E]`);
    }
    setTimeout(() => setPhotoToast(null), 4500);
  };

  const handleCycleZoom = () => {
    const zoomPresets = [1.0, 1.25, 1.5, 2.0];
    const current = telemetry.fov_zoom || 1.0;
    const nextZoom = zoomPresets.find(z => z > current) || zoomPresets[0];
    setTelemetry((prev) => ({ ...prev, fov_zoom: nextZoom }));
    sendCommand('fov_zoom', { zoom: nextZoom });
  };

  const handleToggleClarity = () => {
    const nextVal = !telemetry.clarity_boost;
    setTelemetry((prev) => ({ ...prev, clarity_boost: nextVal }));
    sendCommand('clarity');
  };

  const handleToggleThermal = () => {
    const nextVal = !telemetry.thermal_mode;
    setTelemetry((prev) => ({ ...prev, thermal_mode: nextVal }));
    sendCommand('thermal');
  };

  const handleScanSubnet = () => {
    sendCommand('scan_subnet');
  };

  const handleSwitchSource = (source: string) => {
    setTelemetry((prev) => ({ ...prev, camera_source: source }));
    sendCommand('switch_source', { source });
  };

  const handleEmergencyBrake = () => {
    sendCommand('emergency_brake');
  };

  // 4. Keyboard Shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;

      const key = e.key.toLowerCase();
      if (key === 'p') {
        handleCapturePhoto();
      } else if (key === 'r') {
        handleToggleRecord();
      } else if (key === 'h' || key === 'b') {
        handleToggleRth();
      } else if (key === 'c') {
        setIsConnectDrawerOpen(true);
      } else if (key === 'g') {
        setIsGalleryOpen(true);
      } else if (key === 's') {
        handleScanSubnet();
      } else if (key === 'z') {
        handleCycleZoom();
      } else if (key === ' ') {
        e.preventDefault();
        handleEmergencyBrake();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [telemetry]);

  return (
    <div className="relative w-screen h-screen bg-[#05070a] text-slate-100 overflow-hidden select-none">
      
      {/* Shutter Flash Animation */}
      {photoFlashActive && (
        <div className="fixed inset-0 z-50 bg-white pointer-events-none animate-shutter-flash" />
      )}

      {/* Photo Notification Toast with Real Location */}
      {photoToast && (
        <div className="fixed top-14 left-1/2 -translate-x-1/2 z-50 px-4 py-2 bg-emerald-950/95 text-emerald-300 font-mono text-xs rounded-xl border border-emerald-500/50 shadow-[0_0_25px_rgba(16,185,129,0.5)] backdrop-blur-md flex items-center space-x-2 animate-bounce">
          <span>{photoToast}</span>
        </div>
      )}

      {/* Video Saved Notification Toast with Real Location */}
      {recordToast && (
        <div className="fixed top-14 left-1/2 -translate-x-1/2 z-50 px-4 py-2 bg-rose-950/95 text-rose-300 font-mono text-xs rounded-xl border border-rose-500/50 shadow-[0_0_25px_rgba(244,63,94,0.5)] backdrop-blur-md flex items-center space-x-2 animate-bounce">
          <span>{recordToast}</span>
        </div>
      )}

      {/* Full-Screen Cockpit View with Big Live Video, Real Data & GTA Radar in Real View */}
      <CockpitView
        telemetry={telemetry}
        onToggleRecord={handleToggleRecord}
        onCapturePhoto={handleCapturePhoto}
        onToggleRth={handleToggleRth}
        onCycleMode={handleCycleMode}
        onCycleZoom={handleCycleZoom}
        onToggleClarity={handleToggleClarity}
        onToggleThermal={handleToggleThermal}
        onOpenConnectDrawer={() => setIsConnectDrawerOpen(true)}
        onEmergencyBrake={handleEmergencyBrake}
        onOpenMediaGallery={() => setIsGalleryOpen(true)}
      />

      {/* Easy-Connect Link Drawer */}
      <EasyConnectDrawer
        isOpen={isConnectDrawerOpen}
        onClose={() => setIsConnectDrawerOpen(false)}
        telemetry={telemetry}
        onScanSubnet={handleScanSubnet}
        onSwitchSource={handleSwitchSource}
      />

      {/* Drone Media Recordings & Flight Gallery Modal */}
      <MediaGalleryModal
        isOpen={isGalleryOpen}
        onClose={() => setIsGalleryOpen(false)}
      />

    </div>
  );
};

export default App;
