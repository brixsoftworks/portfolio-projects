import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import { DroneTelemetry } from '../types';
import { Maximize2, Compass, Navigation } from 'lucide-react';

interface GtaRadarMinimapProps {
  telemetry: DroneTelemetry;
  onExpandMap: () => void;
  className?: string;
}

export const GtaRadarMinimap: React.FC<GtaRadarMinimapProps> = ({
  telemetry,
  onExpandMap,
  className = '',
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const tileLayerRef = useRef<L.TileLayer | null>(null);
  const droneMarkerRef = useRef<L.Marker | null>(null);
  const trailPolylineRef = useRef<L.Polyline | null>(null);

  // Default to Real View (Satellite Photographic Real Earth View)
  const [mapStyle, setMapStyle] = useState<'real' | 'street'>('real');

  const { lat, lon, yaw, home_lat, home_lon, trail, waypoints } = telemetry;

  useEffect(() => {
    if (!mapContainerRef.current) return;

    if (!mapInstanceRef.current) {
      // Initialize Leaflet map
      const map = L.map(mapContainerRef.current, {
        center: [lat, lon],
        zoom: 16,
        zoomControl: false,
        attributionControl: false,
      });

      // Default: Real Satellite Photographic Imagery View
      const tileUrl = mapStyle === 'real'
        ? 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
        : 'https://tile.openstreetmap.org/{z}/{x}/{y}.png';

      const tileLayer = L.tileLayer(tileUrl, {
        maxZoom: 19,
        className: mapStyle === 'real' ? 'gta-satellite-tiles' : 'gta-osm-tiles',
      }).addTo(map);
      tileLayerRef.current = tileLayer;

      setTimeout(() => {
        if (mapInstanceRef.current) {
          mapInstanceRef.current.invalidateSize();
        }
      }, 150);

      // Home Point Marker [H]
      const homeIcon = L.divIcon({
        className: 'gta-home-icon',
        html: `
          <div style="
            width: 20px; height: 20px; 
            border-radius: 50%; 
            background: #f59e0b; 
            border: 2px solid #000; 
            display: flex; align-items: center; justify-content: center;
            box-shadow: 0 0 10px rgba(245, 158, 11, 0.8);
            font-family: monospace; font-weight: bold; font-size: 10px; color: #000;
          ">
            H
          </div>
        `,
        iconSize: [20, 20],
        iconAnchor: [10, 10],
      });
      L.marker([home_lat, home_lon], { icon: homeIcon }).addTo(map);

      // 50m Geofence Perimeter Ring
      L.circle([home_lat, home_lon], {
        radius: 50,
        color: '#10b981',
        weight: 1.5,
        dashArray: '3, 4',
        fillColor: '#10b981',
        fillOpacity: 0.08,
      }).addTo(map);

      // Waypoint Routes
      if (waypoints && waypoints.length > 0) {
        const wpLatLngs = waypoints.map(wp => [wp.lat, wp.lon] as [number, number]);
        L.polyline(wpLatLngs, {
          color: '#f59e0b',
          weight: 1.5,
          dashArray: '2, 4',
          opacity: 0.8,
        }).addTo(map);

        waypoints.forEach(wp => {
          const wpIcon = L.divIcon({
            className: 'wp-mini-icon',
            html: `
              <div style="
                background: rgba(12, 16, 23, 0.9); 
                border: 1px solid #f59e0b; 
                border-radius: 3px; 
                padding: 0px 3px; 
                font-family: monospace; 
                font-size: 7px; 
                color: #f59e0b;
              ">
                ${wp.id}
              </div>
            `,
            iconSize: [24, 14],
            iconAnchor: [12, 7],
          });
          L.marker([wp.lat, wp.lon], { icon: wpIcon }).addTo(map);
        });
      }

      // Trail Polyline
      const polyline = L.polyline([], {
        color: '#00f2fe',
        weight: 2,
        opacity: 0.8,
      }).addTo(map);
      trailPolylineRef.current = polyline;

      // GTA Rotating Player/Drone Chevron Icon
      const droneIcon = L.divIcon({
        className: 'gta-drone-icon',
        html: `
          <div id="gta-drone-rotator" style="
            width: 26px; height: 26px;
            transform: rotate(${yaw}deg);
            transition: transform 0.08s linear;
            display: flex; align-items: center; justify-content: center;
          ">
            <svg viewBox="0 0 28 28" width="26" height="26">
              <polygon points="14,2 25,24 14,18 3,24" fill="#00f2fe" stroke="#000" stroke-width="2" />
              <circle cx="14" cy="14" r="3.5" fill="#ffffff" />
            </svg>
          </div>
        `,
        iconSize: [26, 26],
        iconAnchor: [13, 13],
      });
      const marker = L.marker([lat, lon], { icon: droneIcon }).addTo(map);
      droneMarkerRef.current = marker;

      mapInstanceRef.current = map;
    }

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  // Live Position & Heading Updates
  useEffect(() => {
    if (!mapInstanceRef.current || !droneMarkerRef.current) return;

    droneMarkerRef.current.setLatLng([lat, lon]);

    const rotator = document.getElementById('gta-drone-rotator');
    if (rotator) {
      rotator.style.transform = `rotate(${yaw}deg)`;
    }

    if (trailPolylineRef.current && trail && trail.length > 0) {
      trailPolylineRef.current.setLatLngs(trail);
    }

    mapInstanceRef.current.panTo([lat, lon], { animate: true, duration: 0.1 });
  }, [lat, lon, yaw, trail]);

  // Real Satellite View vs Street View Toggle
  useEffect(() => {
    if (!mapInstanceRef.current) return;
    if (tileLayerRef.current) {
      mapInstanceRef.current.removeLayer(tileLayerRef.current);
    }
    const tileUrl = mapStyle === 'real'
      ? 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
      : 'https://tile.openstreetmap.org/{z}/{x}/{y}.png';

    const layer = L.tileLayer(tileUrl, {
      maxZoom: 19,
      className: mapStyle === 'real' ? 'gta-satellite-tiles' : 'gta-osm-tiles',
    }).addTo(mapInstanceRef.current);
    tileLayerRef.current = layer;
  }, [mapStyle]);

  return (
    <div className={`relative flex flex-col pointer-events-auto ${className}`}>
      
      {/* Outer GTA Radar Chassis with Cyber Bezel */}
      <div className="relative p-1.5 rounded-2xl bg-[#090d14]/90 backdrop-blur-xl border-2 border-white/15 shadow-[0_12px_40px_rgba(0,0,0,0.8)] group overflow-hidden">
        
        {/* Radar Corner Brackets (GTA Cyber Aesthetic) */}
        <div className="absolute top-1 left-1 w-3 h-3 border-t-2 border-l-2 border-cyan-400 z-20 pointer-events-none" />
        <div className="absolute top-1 right-1 w-3 h-3 border-t-2 border-r-2 border-cyan-400 z-20 pointer-events-none" />
        <div className="absolute bottom-1 left-1 w-3 h-3 border-b-2 border-l-2 border-cyan-400 z-20 pointer-events-none" />
        <div className="absolute bottom-1 right-1 w-3 h-3 border-b-2 border-r-2 border-cyan-400 z-20 pointer-events-none" />

        {/* Real Leaflet Map Viewport */}
        <div 
          onClick={onExpandMap}
          className="relative w-64 h-44 rounded-xl overflow-hidden cursor-pointer"
          style={{ background: '#090d14' }}
          title="Click to expand full interactive map [M / TAB]"
        >
          <div ref={mapContainerRef} className="w-full h-full" style={{ background: '#090d14' }} />

          {/* Radar Sweep Reticle & Crosshairs */}
          <div className="absolute inset-0 pointer-events-none flex items-center justify-center">
            <div className="w-28 h-28 rounded-full border border-cyan-400/20" />
            <div className="w-44 h-44 rounded-full border border-cyan-400/15" />
            <div className="absolute top-0 bottom-0 w-[1px] bg-cyan-400/10" />
            <div className="absolute left-0 right-0 h-[1px] bg-cyan-400/10" />
          </div>

          {/* Cardinal North Compass Badge */}
          <div className="absolute top-1.5 left-1.5 z-[1000] px-1.5 py-0.5 rounded bg-black/80 border border-white/20 text-[9px] font-mono font-bold text-cyan-300 flex items-center space-x-1 shadow">
            <Compass className="w-2.5 h-2.5 text-cyan-400" />
            <span>N</span>
          </div>

          {/* Real Satellite View / Street View Switcher Badge */}
          <button
            onClick={(e) => {
              e.stopPropagation();
              setMapStyle((prev) => (prev === 'real' ? 'street' : 'real'));
            }}
            className="absolute top-1.5 right-1.5 z-[1000] px-1.5 py-0.5 rounded bg-black/85 hover:bg-black border border-white/20 text-[8px] font-mono font-bold text-amber-300 flex items-center space-x-1 shadow transition-all active:scale-95"
            title="Switch between Real Satellite Photography View and Street Map"
          >
            <span>{mapStyle === 'real' ? '🛰️ REAL VIEW' : '🗺️ STREET'}</span>
          </button>

          {/* Hover Expand Prompt */}
          <div className="absolute inset-0 z-[1000] bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center space-x-1.5 backdrop-blur-[2px]">
            <Maximize2 className="w-4 h-4 text-cyan-400" />
            <span className="text-[10px] font-mono font-bold text-cyan-300 uppercase tracking-wider">
              EXPAND MAP [M]
            </span>
          </div>
        </div>

        {/* GTA-Style Status Bars (Directly beneath radar) */}
        <div className="px-1 pt-1.5 space-y-1">
          {/* Health / Battery Bar (Green) */}
          <div className="flex items-center space-x-1.5">
            <div className="flex-1 h-1.5 bg-slate-900 rounded-sm overflow-hidden border border-white/5">
              <div 
                className="h-full bg-emerald-400 shadow-[0_0_6px_#10b981] transition-all duration-300"
                style={{ width: `${telemetry.battery_pct}%` }}
              />
            </div>
            <span className="text-[8px] font-mono font-bold text-emerald-400 w-7 text-right">
              {telemetry.battery_pct.toFixed(0)}%
            </span>
          </div>

          {/* Armor / Signal Bar (Cyan / Blue) */}
          <div className="flex items-center space-x-1.5">
            <div className="flex-1 h-1.5 bg-slate-900 rounded-sm overflow-hidden border border-white/5">
              <div 
                className="h-full bg-cyan-400 shadow-[0_0_6px_#00f2fe] transition-all duration-300"
                style={{ width: `${telemetry.signal_pct}%` }}
              />
            </div>
            <span className="text-[8px] font-mono font-bold text-cyan-400 w-7 text-right">
              {telemetry.signal_pct}%
            </span>
          </div>

          {/* Special / Altitude Bar (Yellow) */}
          <div className="flex items-center space-x-1.5">
            <div className="flex-1 h-1.5 bg-slate-900 rounded-sm overflow-hidden border border-white/5">
              <div 
                className="h-full bg-amber-400 shadow-[0_0_6px_#f59e0b] transition-all duration-300"
                style={{ width: `${Math.min(100, (telemetry.rel_alt / 50.0) * 100)}%` }}
              />
            </div>
            <span className="text-[8px] font-mono font-bold text-amber-400 w-7 text-right">
              {telemetry.rel_alt.toFixed(1)}m
            </span>
          </div>
        </div>

        {/* Street Name / Real WGS84 Coordinates Banner */}
        <div className="px-1 pt-1 flex items-center justify-between text-[8px] font-mono text-slate-300 border-t border-white/10 mt-1">
          <span className="text-cyan-300 font-bold tracking-wider">
            {telemetry.lat.toFixed(5)}°N, {telemetry.lon.toFixed(5)}°E
          </span>
          <span className="text-emerald-400 font-semibold">
            {telemetry.sats} SATS (RTK) • {mapStyle === 'real' ? 'REAL VIEW' : 'MAP'}
          </span>
        </div>

      </div>

    </div>
  );
};
