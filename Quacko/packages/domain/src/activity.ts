import type { RoutePoint } from '@quacko/types';
import { round1 } from './streak';

const EARTH_RADIUS_M = 6371000;

export function haversineM(a: { lat: number; lng: number }, b: { lat: number; lng: number }): number {
  const toRad = (d: number) => (d * Math.PI) / 180;
  const dLat = toRad(b.lat - a.lat);
  const dLng = toRad(b.lng - a.lng);
  const lat1 = toRad(a.lat);
  const lat2 = toRad(b.lat);
  const h =
    Math.sin(dLat / 2) ** 2 + Math.cos(lat1) * Math.cos(lat2) * Math.sin(dLng / 2) ** 2;
  return 2 * EARTH_RADIUS_M * Math.asin(Math.sqrt(h));
}

export function routeDistance(route: readonly RoutePoint[]): number {
  let total = 0;
  for (let i = 1; i < route.length; i += 1) {
    const prev = route[i - 1];
    const cur = route[i];
    if (!prev || !cur) continue;
    total += haversineM(prev, cur);
  }
  return total;
}

export function paceSecPerKm(distanceM: number, durationSec: number): number | null {
  if (distanceM <= 0 || durationSec <= 0) return null;
  return round1((durationSec / (distanceM / 1000)));
}

export function summaryCarbs(durationMinutes: number): string {
  if (durationMinutes === 0) return '0m';
  if (durationMinutes < 60) return `${durationMinutes}m`;
  const h = Math.floor(durationMinutes / 60);
  return `${h}h ${durationMinutes % 60}m`;
}

export function pruneRoute(route: readonly RoutePoint[], keepEvery = 20): RoutePoint[] {
  if (route.length <= keepEvery * 4) return [...route];
  return route.filter((_, i) => i % keepEvery === 0);
}