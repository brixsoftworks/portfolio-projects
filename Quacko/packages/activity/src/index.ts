import type { ActivityKind, RoutePoint } from '@quacko/types';
import { routeDistance } from '@quacko/domain';

export interface ActivitySample {
  route: RoutePoint[];
  elapsedSeconds: number;
  distanceMeters: number;
  steps: number | null;
}

/**
 * Portable activity-data source. The native implementation streams GPS via
 * expo-location (dynamic import, native only); the mock implements the exact
 * same contract so demo mode and the web build share one code path.
 */
export interface ActivityDataProvider {
  readonly kind: ActivityKind;
  start(targetMinutes: number): Promise<void>;
  stop(): Promise<void>;
  /** Latest cumulative sample (debounced ~ every 2s). */
  current(): ActivitySample;
  onUpdate(cb: (s: ActivitySample) => void): () => void;
  requestPermissions(): Promise<boolean>;
  readonly supported: boolean;
}

/* ------------------------------ mock provider ----------------------------- */

const MOCK_SPEED_MPS = 2.8;

export class MockActivityProvider implements ActivityDataProvider {
  readonly kind: ActivityKind;
  readonly supported = true;
  private route: RoutePoint[] = [];
  private elapsed = 0;
  private timer: ReturnType<typeof setInterval> | null = null;
  private readonly listeners = new Set<(s: ActivitySample) => void>();
  private readonly initial: { lat: number; lng: number } = { lat: 51.5074, lng: -0.1278 };

  constructor(kind: ActivityKind) {
    this.kind = kind;
  }

  async requestPermissions() {
    return true;
  }

  async start() {
    const t0 = Date.now();
    this.route = [{ lat: this.initial.lat, lng: this.initial.lng, t: t0, accuracyM: 5, speedMps: MOCK_SPEED_MPS }];
    this.elapsed = 0;
    this.timer = setInterval(() => {
      this.elapsed = Math.floor((Date.now() - t0) / 1000);
      const last = this.route[this.route.length - 1];
      const bearing = ((this.route.length * 3) % 360) * (Math.PI / 180);
      const lat = (last?.lat ?? this.initial.lat) + (Math.cos(bearing) * MOCK_SPEED_MPS * 2) / 111320;
      const lng =
        (last?.lng ?? this.initial.lng) +
        (Math.sin(bearing) * MOCK_SPEED_MPS * 2) / (111320 * Math.cos(this.initial.lat * (Math.PI / 180)));
      this.route.push({ lat, lng, t: Date.now(), accuracyM: 6, speedMps: MOCK_SPEED_MPS });
      this.emit();
    }, 2000);
  }

  async stop() {
    if (this.timer) clearInterval(this.timer);
    this.timer = null;
  }

  current(): ActivitySample {
    return {
      route: [...this.route],
      elapsedSeconds: this.elapsed,
      distanceMeters: routeDistance(this.route),
      steps: null,
    };
  }

  onUpdate(cb: (s: ActivitySample) => void) {
    this.listeners.add(cb);
    return () => this.listeners.delete(cb);
  }

  private emit() {
    const s = this.current();
    for (const l of this.listeners) l(s);
  }
}

/* --------------------------- native provider ------------------------------ */

/** Native GPS streaming. Only call on a physical device; web is unsupported. */
export async function createNativeActivityProvider(kind: ActivityKind): Promise<ActivityDataProvider> {
  const Location = await import('expo-location');
  return new NativeActivityProvider(kind, Location);
}

class NativeActivityProvider implements ActivityDataProvider {
  readonly kind: ActivityKind;
  readonly supported = true;
  private route: RoutePoint[] = [];
  private elapsed = 0;
  private startedAt = 0;
  private sub: { remove: () => void } | null = null;
  private readonly listeners = new Set<(s: ActivitySample) => void>();

  constructor(kind: ActivityKind, private readonly location: typeof import('expo-location')) {
    this.kind = kind;
  }

  async requestPermissions() {
    const { status } = await this.location.requestForegroundPermissionsAsync();
    return status === 'granted';
  }

  async start() {
    this.startedAt = Date.now();
    this.route = [];
    this.elapsed = 0;
    const granted = await this.requestPermissions();
    if (!granted) throw new Error('Location permission denied');
    this.sub = await this.location.watchPositionAsync(
      { accuracy: this.location.Accuracy.High, distanceInterval: 10, timeInterval: 2000 },
      (pos) => {
        this.route.push({
          lat: pos.coords.latitude,
          lng: pos.coords.longitude,
          t: pos.timestamp,
          accuracyM: pos.coords.accuracy ?? 10,
          speedMps: pos.coords.speed ?? null,
        });
        this.elapsed = Math.floor((Date.now() - this.startedAt) / 1000);
        this.emit();
      },
    );
  }

  async stop() {
    this.sub?.remove();
    this.sub = null;
  }

  current(): ActivitySample {
    return {
      route: [...this.route],
      elapsedSeconds: this.elapsed,
      distanceMeters: routeDistance(this.route),
      steps: null,
    };
  }

  onUpdate(cb: (s: ActivitySample) => void) {
    this.listeners.add(cb);
    return () => this.listeners.delete(cb);
  }

  private emit() {
    const s = this.current();
    for (const l of this.listeners) l(s);
  }
}