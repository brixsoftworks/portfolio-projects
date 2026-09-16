import { useEffect, useRef } from 'react';
import type { ReactNode } from 'react';
import { Animated, StyleSheet, View } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { backdropGradient } from '../theme';

interface GlowCircle {
  color: string;
  size: number;
  top: `${number}%`;
  left: `${number}%`;
}

const CIRCLES: GlowCircle[] = [
  { color: '#7224e0', size: 320, top: '-8%', left: '-20%' },
  { color: '#1d2f6f', size: 280, top: '38%', left: '68%' },
  { color: '#6b1253', size: 260, top: '72%', left: '-12%' },
  { color: '#00263a', size: 200, top: '6%', left: '72%' },
];

/**
 * Quiet animated "nebula" backdrop matching the Neon Tokyo splash.
 * Uses RN Animated only — no Skia — keeping the bundle lean.
 */
export function NeonBackdrop({ children }: { children?: ReactNode }) {
  const drift = useRef(CIRCLES.map(() => new Animated.Value(0))).current;

  useEffect(() => {
    const anims = drift.map((v, i) =>
      Animated.loop(
        Animated.sequence([
          Animated.timing(v, { toValue: 1, duration: 9000 + i * 2600, useNativeDriver: true }),
          Animated.timing(v, { toValue: 0, duration: 9000 + i * 2600, useNativeDriver: true }),
        ]),
      ),
    );
    anims.forEach((a) => a.start());
    return () => anims.forEach((a) => a.stop());
  }, [drift]);

  return (
    <View style={styles.root}>
      <LinearGradient colors={[...backdropGradient]} testID="backdrop" style={[StyleSheet.absoluteFill as never]} />
      {CIRCLES.map((c, i) => {
        const d = drift[i] ?? new Animated.Value(0);
        const translateY = d.interpolate({
          inputRange: [0, 1],
          outputRange: [-24, 24],
        });
        return (
          <Animated.View
            key={c.color + i}
            style={[
              styles.circle,
              { width: c.size, height: c.size, top: c.top, left: c.left, transform: [{ translateY }] },
            ]}
          >
            <LinearGradient colors={['transparent', c.color, 'transparent']} style={styles.roundFill} />
          </Animated.View>
        );
      })}
      <View style={styles.content}>{children}</View>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1 },
  circle: { position: 'absolute', borderRadius: 999, opacity: 0.5 },
  roundFill: { flex: 1, borderRadius: 999 },
  content: { flex: 1, backgroundColor: 'transparent' },
});