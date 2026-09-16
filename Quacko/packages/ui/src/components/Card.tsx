import type { ReactNode } from 'react';
import { View, type StyleProp, type ViewStyle } from 'react-native';
import { colors, radius, shadows, spacing } from '../theme';

export interface QuackoCardProps {
  children: ReactNode;
  style?: StyleProp<ViewStyle>;
  surface?: 'low' | 'base' | 'high' | 'highest';
  padded?: boolean;
  accent?: 'primary' | 'secondary' | 'tertiary' | null;
}

const SURFACES: Record<NonNullable<QuackoCardProps['surface']>, string> = {
  low: colors.surfaceContainerLow,
  base: colors.surfaceContainer,
  high: colors.surfaceContainerHigh,
  highest: colors.surfaceContainerHighest,
};

export function QuackoCard({ children, style, surface = 'low', padded = true, accent = null }: QuackoCardProps) {
  return (
    <View
      style={[
        {
          backgroundColor: SURFACES[surface],
          borderRadius: radius.lg,
          borderWidth: 1,
          borderColor: colors.outlineVariant,
          padding: padded ? spacing.lg : 0,
          overflow: 'hidden',
        },
        accent ? { borderColor: colors[accent], shadowColor: colors[accent], shadowRadius: 12, shadowOpacity: 0.25, elevation: 6 } : null,
        shadows.neumorphic,
        style,
      ]}
    >
      {children}
    </View>
  );
}