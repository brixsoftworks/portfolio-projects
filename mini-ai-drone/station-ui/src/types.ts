export interface DetectionObject {
  id: number;
  label: string;
  box: [number, number, number, number]; // [x1, y1, x2, y2] normalized 0-1
  dist_m: number;
  width_m: number;
  height_m: number;
  area_sq_m: number;
  color: string;
}

export interface Waypoint {
  id: string;
  name: string;
  lat: number;
  lon: number;
  alt: number;
}

export interface DroneTelemetry {
  pitch: number;
  roll: number;
  yaw: number;
  speed: number;
  altitude: number;
  rel_alt: number;
  climb_rate: number;
  
  lat: number;
  lon: number;
  sats: number;
  hdop: number;
  home_lat: number;
  home_lon: number;
  dist_home: number;
  bearing_home: number;
  
  battery_pct: number;
  battery_voltage: number;
  cell_voltages: number[];
  remaining_flight_time: string;
  rth_threshold_pct: number;
  
  flight_mode: 'N-MODE' | 'S-MODE' | 'C-MODE' | 'RTH';
  is_recording: boolean;
  record_duration: string;
  last_photo_file: string | null;
  photo_flash: boolean;
  
  wire_hazard: boolean;
  landing_safe: boolean;
  roughness: number;
  detections: DetectionObject[];
  
  camera_source: string;
  ping_ms: number;
  signal_pct: number;
  fps: number;
  
  fov_zoom: number;
  clarity_boost: boolean;
  thermal_mode: boolean;
  waypoints: Waypoint[];
  trail: [number, number][]; // [lat, lon]

  // Real Flight Telemetry & Hardware Avionics
  motors: [number, number, number, number]; // M1, M2, M3, M4 loads in %
  rpm: number; // Real calculated rotor RPM
  obstacle_sectors: number[]; // 9 real depth sectors (c1-c9 in meters)
  pitch_history: number[]; // Rolling 30 readings
  roll_history: number[];
  speed_history: number[];
  latency_history: number[];
  gpu_temp: number; // GPU temperature in °C
  ground_speed_kmh: number; // Ground speed in km/h
}
