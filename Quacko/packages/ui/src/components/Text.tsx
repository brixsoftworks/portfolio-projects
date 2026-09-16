import { Text, type TextProps, type TextStyle } from 'react-native';
import { colors, textGlow, typography } from '../theme';

export type QuackoTextVariant = 'display' | 'headline' | 'title' | 'body' | 'bodyMuted' | 'label' | 'labelStrong' | 'caption';

export interface QuackoTextProps extends TextProps {
  variant?: QuackoTextVariant;
  accent?: boolean;
  neon?: 'primary' | 'secondary' | 'tertiary' | null;
  style?: TextStyle | TextStyle[];
}

export function QuackoText({
  variant = 'body',
  accent = false,
  neon = null,
  style,
  ...rest
}: QuackoTextProps) {
  const base = typography[variant] as TextStyle;
  const neonColor = neon ? colors[neon] : null;
  const composed: TextStyle = {
    ...base,
    color: accent ? colors.primary : base.color,
    ...(neonColor ? textGlow(neonColor, 6) : {}),
  };
  return <Text {...rest} style={[composed, style]} />;
}