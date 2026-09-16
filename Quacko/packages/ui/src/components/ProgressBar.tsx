import { View, type StyleProp, type ViewStyle } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { colors, radius } from '../theme';

export interface ProgressBarProps {
  /** 0..1 */
  value: number;
  color?: string;
  trackColor?: string;
  height?: number;
  style?: StyleProp<ViewStyle>;
  /** gently animated fill trickery (reanimated optional via driver) */
  gradient?: boolean;
}

export function ProgressBar({
  value,
  color = colors.primary,
  trackColor = colors.surfaceContainerHighest,
  height = 10,
  style,
  gradient = true,
}: ProgressBarProps) {
  const pct = Math.min(1, Math.max(0, value)) * 100;
  const fill = (
    <View
      style={{
        width: `${pct}%`,
        height,
        borderRadius: radius.pill,
        overflow: 'hidden',
        backgroundColor: color,
      }}
    >
      {gradient ? (
        <LinearGradient
          colors={[color, '#ffffff22']}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 0 }}
          style={{ flex: 1 }}
        />
      ) : null}
    </View>
  );
  return (
    <View
      style={[
        { backgroundColor: trackColor, borderRadius: radius.pill, height, overflow: 'hidden', width: '100%' },
        style,
      ]}
    >
      {fill}
    </View>
  );
}