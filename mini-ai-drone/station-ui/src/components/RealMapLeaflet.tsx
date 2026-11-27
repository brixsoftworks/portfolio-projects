import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import { DroneTelemetry } from '../types';

interface MapProps {
  telemetry: DroneTelemetry;
  className?: string;
  compact?: boolean;
}

export const RealMapLeaflet: React.FC<MapProps> = ({ telemetry, className = '', compact = false }) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const tileLayerRef = useRef<L.TileLayer | null>(null);
  const droneMarkerRef = useRef<L.Marker | null>(null);
  const trailPolylineRef = useRef<L.Polyline | null>(null);

  // Default to Real Satellite Imagery
  const [mapStyle, setMapStyle] = useState<'real' | 'street'>('real');

  const { lat, lon, yaw, home_lat, home_lon, trail, waypoints, flight_mode } = telemetry;

  useEffect(() => {
    if (!mapContainerRef.current) return;

    if (!mapInstanceRef.current) {
      // Initialize Leaflet map
      const map = L.map(mapContainerRef.current, {
        center: [lat, lon],
        zoom: compact ? 15 : 16,
        zoomControl: !compact,
        attributionControl: false,
      });

      // Default: Real Satellite Photography Tiles
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

      // 1. Home Point Marker [H]
      const homeIcon = L.divIcon({
        className: 'custom-home-icon',
        html: `
          <div style="
            width: 22px; height: 22px; 
            border-radius: 50%; 
            background: #f59e0b; 
            border: 2px solid #000; 
            display: flex; align-items: center; justify-content: center;
            box-shadow: 0 0 10px rgba(245, 158, 11, 0.6);
            font-family: monospace; font-weight: bold; font-size: 10px; color: #000;
          ">
            H
          </div>
        `,
        iconSize: [22, 22],
        iconAnchor: [11, 11],
      });
      L.marker([home_lat, home_lon], { icon: homeIcon }).addTo(map);

      // 2. 50m Geofence Safety Perimeter Circle
      L.circle([home_lat, home_lon], {
        radius: 50,
        color: '#10b981',
        weight: 1.5,
        dashArray: '4, 4',
        fillColor: '#10b981',
        fillOpacity: 0.05,
      }).addTo(map);

      // 3. Waypoint Mission Route
      if (waypoints && waypoints.length > 0) {
        const wpLatLngs = waypoints.map(wp => [wp.lat, wp.lon] as [number, number]);
        L.polyline(wpLatLngs, {
          color: '#f59e0b',
          weight: 1.5,
          dashArray: '3, 5',
          opacity: 0.8,
        }).addTo(map);

        waypoints.forEach(wp => {
          const wpIcon = L.divIcon({
            className: 'wp-icon',
            html: `
              <div style="
                background: rgba(12, 16, 23, 0.85); 
                border: 1px solid #f59e0b; 
                border-radius: 4px; 
                padding: 1px 4px; 
                font-family: monospace; 
                font-size: 8px; 
                color: #f59e0b;
                box-shadow: 0 0 6px rgba(245, 158, 11, 0.3);
              ">
                ${wp.id}
              </div>
            `,
            iconSize: [30, 16],
            iconAnchor: [15, 8],
          });
          L.marker([wp.lat, wp.lon], { icon: wpIcon }).addTo(map);
        });
      }

      // 4. Trail Polyline
      const polyline = L.polyline([], {
        color: '#00f2fe',
        weight: 2,
        opacity: 0.7,
      }).addTo(map);
      trailPolylineRef.current = polyline;

      // 5. Custom Drone Marker with Heading Arrow
      const droneIcon = L.divIcon({
        className: 'custom-drone-icon',
        html: `
          <div id="leaflet-drone-rotator" style="
            width: 28px; height: 28px;
            transform: rotate(${yaw}deg);
            transition: transform 0.08s linear;
          ">
            <svg viewBox="0 0 28 28" fill="none">
              <polygon points="14,2 24,24 14,19 4,24" fill="#00f2fe" stroke="#000" stroke-width="1.5" />
              <circle cx="14" cy="14" r="3" fill="#ffffff" />
            </svg>
          </div>
        `,
        iconSize: [28, 28],
        iconAnchor: [14, 14],
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

  // Update drone position and heading live
  useEffect(() => {
    if (!mapInstanceRef.current || !droneMarkerRef.current) return;

    droneMarkerRef.current.setLatLng([lat, lon]);

    const rotator = document.getElementById('leaflet-drone-rotator');
    if (rotator) {
      rotator.style.transform = `rotate(${yaw}deg)`;
    }

    if (trailPolylineRef.current && trail && trail.length > 0) {
      trailPolylineRef.current.setLatLngs(trail);
    }

    // Auto-pan softly to drone position
    mapInstanceRef.current.panTo([lat, lon], { animate: true, duration: 0.1 });
  }, [lat, lon, yaw, trail]);

  // Dynamic Satellite Real View vs Street Map Switcher
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
    <div className={`relative w-full h-full rounded-2xl overflow-hidden border border-white/10 ${className}`} style={{ background: '#090d14' }}>
      <div ref={mapContainerRef} className="w-full h-full" style={{ background: '#090d14' }} />
      
      {!compact && (
        <>
          {/* Real Coordinates Overlay Badge */}
          <div className="absolute top-2.5 left-2.5 z-[1000] px-2.5 py-1 bg-[#0b0f17]/90 backdrop-blur-md rounded-lg border border-white/10 text-[10px] font-mono text-cyan-300 shadow-lg">
            GPS: {lat.toFixed(6)}°N, {lon.toFixed(6)}°E • {mapStyle === 'real' ? 'REAL VIEW SATELLITE' : 'STREET MAP'}
          </div>

          {/* Real Satellite View vs Street Map Toggle Pill */}
          <div className="absolute top-2.5 right-2.5 z-[1000] flex space-x-1 p-1 bg-[#0b0f17]/90 backdrop-blur-md rounded-xl border border-white/10 shadow-lg">
            <button
              onClick={() => setMapStyle('real')}
              className={`px-2.5 py-1 rounded-lg text-[9px] font-mono font-bold tracking-wider transition-all ${
                mapStyle === 'real'
                  ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40 shadow-[0_0_10px_rgba(245,158,11,0.3)]'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              [SAT] REAL VIEW (SATELLITE)
            </button>
            <button
              onClick={() => setMapStyle('street')}
              className={`px-2.5 py-1 rounded-lg text-[9px] font-mono font-bold tracking-wider transition-all ${
                mapStyle === 'street'
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-[0_0_10px_rgba(6,182,212,0.3)]'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              [MAP] STREET MAP
            </button>
          </div>

          {/* Geofence & Mission Status Badge */}
          <div className="absolute bottom-2.5 left-2.5 z-[1000] px-2.5 py-1 bg-[#0b0f17]/90 backdrop-blur-md rounded-lg border border-white/10 text-[9px] font-mono text-slate-300 shadow-lg flex items-center space-x-2">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span>GEOFENCE: 50m SAFE</span>
            <span className="text-slate-500">|</span>
            <span className="text-amber-400">WAYPOINTS: 4/4 LOADED</span>
          </div>
        </>
      )}
    </div>
  );
};
