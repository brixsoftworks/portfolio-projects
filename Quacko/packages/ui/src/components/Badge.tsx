import { View, type StyleProp, type ViewStyle } from 'react-native';
import { QuackoText } from './Text';
import { colors, glow, radius } from '../theme';

export type BadgeKind = 'primary' | 'secondary' | 'tertiary' | 'dark' | 'danger' | 'success' | 'plain';

const KIND_STYLES: Record<BadgeKind, { bg: string; fg: string; bord: string; neon?: boolean }> = {
  primary: { bg: colors.primaryContainer, fg: colors.onPrimaryContainer, bord: colors.primary, neon: true },
  secondary: { bg: '#063a33', fg: colors.onSecondaryContainer, bord: colors.secondary, neon: true },
  tertiary: { bg: '#3d3a12', fg: colors.tertiary, bord: colors.tertiary, neon: true },
  dark: { bg: colors.surfaceContainerHigh, fg: colors.onSurface, bord: colors.outlineVariant },
  danger: { bg: colors.errorContainer, fg: colors.error, bord: colors.error },
  success: { bg: '#062a24', fg: colors.secondary, bord: colors.secondary, neon: true },
  plain: { bg: colors.surfaceContainer, fg: colors.onSurfaceVariant, bord: colors.outlineVariant },
};

export interface QuackoBadgeProps {
  label: string;
  kind?: BadgeKind;
  emoji?: string;
  style?: StyleProp<ViewStyle>;
}

export function QuackoBadge({ label, kind = 'dark', emoji, style }: QuackoBadgeProps) {
  const k = KIND_STYLES[kind];
  return (
    <View
      style={[
        {
          backgroundColor: k.bg,
          borderColor: k.bord,
          borderWidth: 1,
          borderRadius: radius.pill,
          paddingHorizontal: 12,
          paddingVertical: 5,
          flexDirection: 'row',
          alignItems: 'center',
          gap: 4,
          alignSelf: 'flex-start',
        },
        k.neon ? glow(k.bord, 10, 0.25) : null,
        style,
      ]}
    >
      {emoji ? <QuackoText style={{ fontSize: 12 }}>{emoji}</QuackoText> : null}
      <QuackoText variant="label" style={{ color: k.fg }}>
        {label}
      </QuackoText>
    </View>
  );
}