import type { TextStyle, ViewStyle } from 'react-native';

/* ---------------------------- Neon Tokyo tokens --------------------------- */

export const colors = {
  primary: '#ff2d78',
  secondary: '#00ffcc',
  tertiary: '#ffe04a',
  background: '#0a0a12',
  surfaceContainerLow: '#111118',
  surfaceContainer: '#141422',
  surfaceContainerHigh: '#1e1e30',
  surfaceContainerHighest: '#28283e',
  onSurface: '#e8e0f0',
  onSurfaceVariant: '#a098b0',
  onSurfaceMuted: '#6f6880',
  error: '#ff4444',
  errorContainer: '#3d0f0f',
  outlineVariant: '#302840',
  primaryContainer: '#b3004e',
  onPrimaryContainer: '#ffd3e4',
  onSecondaryContainer: '#c0fff4',
  onPrimaryFixed: '#3d0020',
  scrim: '#05050a',
  black: '#000000',
  white: '#ffffff',
} as const;

export const fonts = {
  display: 'Sora_700Bold',
  headline: 'Sora_700Bold',
  title: 'Sora_600SemiBold',
  body: 'Inter_400Regular',
  bodyMedium: 'Inter_500Medium',
  bodyBold: 'Inter_700Bold',
  label: 'SpaceGrotesk_500Medium',
  labelBold: 'SpaceGrotesk_700Bold',
} as const;

export const fontStack = {
  display: 'Sora',
  body: 'Inter',
  label: 'Space Grotesk',
} as const;

export const spacing = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 24,
  xxl: 32,
  xxxl: 48,
} as const;

export const radius = {
  sm: 8,
  md: 14,
  lg: 20,
  xl: 28,
  pill: 999,
} as const;

/** Diffuse glow shadow. iOS uses colored shadow; Android uses elevation fallback. */
export function glow(color: string, blur: number, opacity = 0.45): ViewStyle {
  return {
    shadowColor: color,
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: opacity,
    shadowRadius: blur,
    elevation: blur / 2,
  };
}

/** Neon text glow. */
export function textGlow(color: string, blur = 8): TextStyle {
  return {
    textShadowColor: color,
    textShadowOffset: { width: 0, height: 0 },
    textShadowRadius: blur,
  };
}

/** Primary action gradient (pink). */
export const primaryGradient = ['#ff2d78', '#d4145a'] as const;
/** Accent gradient (cyan). */
export const accentGradient = ['#00ffcc', '#00b8d4'] as const;
/** Background nebula gradient (deep). */
export const backdropGradient = ['#0a0a12', '#12081f', '#0a0a12'] as const;

export const typography = {
  display: { fontFamily: fonts.display, fontSize: 34, lineHeight: 40, letterSpacing: -0.5, color: colors.onSurface },
  headline: { fontFamily: fonts.headline, fontSize: 26, lineHeight: 32, letterSpacing: -0.3, color: colors.onSurface },
  title: { fontFamily: fonts.title, fontSize: 18, lineHeight: 24, color: colors.onSurface },
  body: { fontFamily: fonts.body, fontSize: 15, lineHeight: 22, color: colors.onSurface },
  bodyMuted: { fontFamily: fonts.body, fontSize: 14, lineHeight: 20, color: colors.onSurfaceVariant },
  label: { fontFamily: fonts.label, fontSize: 13, lineHeight: 16, color: colors.onSurfaceVariant },
  labelStrong: { fontFamily: fonts.labelBold, fontSize: 13, lineHeight: 16, color: colors.primary },
  caption: { fontFamily: fonts.label, fontSize: 11, lineHeight: 14, color: colors.onSurfaceMuted },
} satisfies Record<string, TextStyle>;

export const shadows = {
  neumorphic: {
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.5,
    shadowRadius: 12,
    elevation: 6,
  } as ViewStyle,
};

/** Material Symbol → MaterialIcons glyph fallback map. */
export const iconMap: Record<string, string> = {
  local_fire_department: 'whatshot',
  calendar_today: 'calendar-today',
  chat_bubble: 'chat-bubble',
  explore: 'explore',
  person: 'person',
  add: 'add',
  warning: 'warning',
  check_circle: 'check-circle',
  lock: 'lock',
  lock_open: 'lock-open',
  more_vert: 'more-vert',
  arrow_forward: 'arrow-forward',
  search: 'search',
  terminal: 'terminal',
  group: 'groups',
  rocket_launch: 'rocket-launch',
  psychology: 'psychology',
  sports_martial_arts: 'sports-martial-arts',
  military_tech: 'military-tech',
  how_to_vote: 'how-to-vote',
  arrow_upward: 'arrow-upward',
  trend_up: 'trending-up',
  verified: 'verified',
  timer: 'timer',
  satellite_alt: 'satellite-alt',
  smart_toy: 'smart-toy',
  target: 'track-changes',
  speed: 'speed',
  favorite: 'favorite',
  pause: 'pause',
  stop: 'stop',
  emoji_events: 'emoji-events',
  swords: 'gavel',
  near_me: 'near-me',
  quiz: 'quiz',
  monitor_heart: 'monitor-heart',
  photo_camera: 'photo-camera',
  videocam: 'videocam',
  mic: 'mic',
  screenshot: 'screenshot',
  chevron_right: 'chevron-right',
  close: 'close',
  upload: 'upload',
  menu_book: 'menu-book',
  school: 'school',
  fitness: 'fitness-center',
  self_improvement: 'self-improvement',
  notifications: 'notifications',
  visibility_off: 'visibility-off',
  ios_share: 'share',
  north_east: 'north-east',
  south_west: 'south-west',
  play: 'play-arrow',
  check: 'check',
  filter: 'filter-list',
  edit: 'edit',
  loop: 'loop',
  nightlight: 'nightlight',
};

export function glyph(symbol: string): string {
  return iconMap[symbol] ?? 'circle';
}