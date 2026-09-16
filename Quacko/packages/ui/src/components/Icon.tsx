import { MaterialIcons } from '@expo/vector-icons';
import type { ComponentProps } from 'react';
import { colors, glyph } from '../theme';

type IconName = ComponentProps<typeof MaterialIcons>['name'];

export interface QuackoIconProps {
  symbol: string;
  size?: number;
  color?: string;
  glowColor?: string;
}

/** Material-Symbol-name icon with neon glow support. */
export function QuackoIcon({ symbol, size = 24, color = colors.onSurface, glowColor }: QuackoIconProps) {
  const style = glowColor
    ? { textShadowColor: glowColor, textShadowRadius: size / 4, textShadowOffset: { width: 0, height: 0 } }
    : undefined;
  return <MaterialIcons name={glyph(symbol) as IconName} size={size} color={color} style={style as never} />;
}