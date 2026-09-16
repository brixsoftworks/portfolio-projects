import { useEffect } from 'react';
import { StyleSheet, View } from 'react-native';
import { useRouter } from 'expo-router';
import { NeonBackdrop, QuackoText } from '@quacko/ui';
import { colors, glow } from '@quacko/ui';
import { useApp } from '@/state/app';

export default function SplashScreen() {
  const router = useRouter();
  const bootstrap = useApp((s) => s.bootstrap);
  const booted = useApp((s) => s.booted);
  const profile = useApp((s) => s.profile);
  const booting = useApp((s) => s.booting);

  useEffect(() => {
    void bootstrap();
  }, [bootstrap]);

  useEffect(() => {
    if (!booted) return;
    const t = setTimeout(() => {
      const seen = profile?.hasSeenOnboarding;
      if (profile) {
        router.replace(seen ? '/(tabs)' : '/onboarding');
      } else {
        router.replace('/login');
      }
    }, 1400);
    return () => clearTimeout(t);
  }, [booted, profile, router]);

  return (
    <NeonBackdrop>
      <View style={styles.center}>
        <View style={styles.duckBubble}>
          <QuackoText variant="display" neon="primary" style={styles.duck}>
            🦆
          </QuackoText>
        </View>
        <QuackoText variant="display" neon="secondary" style={styles.wordmark}>
          QUACKO
        </QuackoText>
        <QuackoText variant="bodyMuted" style={styles.tagline}>
          Don't break the streak
        </QuackoText>
        {booting ? <QuackoText variant="caption">waking the duck…</QuackoText> : null}
      </View>
    </NeonBackdrop>
  );
}

const styles = StyleSheet.create({
  center: { flex: 1, alignItems: 'center', justifyContent: 'center', gap: 16 },
  duckBubble: {
    width: 120,
    height: 120,
    borderRadius: 60,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.surfaceContainer,
    borderWidth: 1,
    borderColor: colors.primaryContainer,
    ...glow(colors.primary, 24, 0.5),
  },
  duck: { fontSize: 60 },
  wordmark: { letterSpacing: 6 },
  tagline: { opacity: 0.8 },
});