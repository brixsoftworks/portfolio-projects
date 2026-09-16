import { Image, View, type StyleProp, type ViewStyle } from 'react-native';
import { QuackoText } from './Text';
import { colors, glow } from '../theme';

export interface QuackoAvatarProps {
  source?: { uri: string } | null;
  name?: string;
  size?: number;
  style?: StyleProp<ViewStyle>;
  neon?: 'primary' | 'secondary' | 'tertiary' | null;
}

/** Avatar with neon ring. Falls back to initials monogram. */
export function QuackoAvatar({ source, name = '?', size = 44, style, neon = 'primary' }: QuackoAvatarProps) {
  const ringColor = neon ? colors[neon] : colors.outlineVariant;
  const background = neon ? colors.surfaceContainerHigh : colors.surfaceContainer;
  return (
    <View
      style={[
        {
          width: size,
          height: size,
          borderRadius: size / 2,
          borderWidth: 2,
          borderColor: ringColor,
          backgroundColor: background,
          alignItems: 'center',
          justifyContent: 'center',
          overflow: 'hidden',
        },
        neon ? glow(ringColor, 8, 0.3) : null,
        style,
      ]}
    >
      {source?.uri ? (
        <Image source={{ uri: source.uri }} style={{ width: size, height: size }} />
      ) : (
        <QuackoText variant="labelStrong" style={{ fontSize: size * 0.4, color: ringColor }}>
          {name.slice(0, 2).toUpperCase()}
        </QuackoText>
      )}
    </View>
  );
}