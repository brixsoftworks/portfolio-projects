import { useEffect, useState } from 'react';
import { ScrollView, StyleSheet, View } from 'react-native';
import {
  NeonBackdrop,
  QuackoAvatar,
  QuackoBadge,
  QuackoCard,
  ProgressBar,
  QuackoText,
  Screen,
  SectionHeader,
  colors,
} from '@quacko/ui';
import { spacing } from '@quacko/ui';
import type { LevelState } from '@quacko/types';
import { useApp } from '@/state/app';
import { getApi } from '@/lib/api';

export default function ProfileScreen() {
  const uid = useApp((s) => s.uid);
  const profile = useApp((s) => s.profile);
  const goals = useApp((s) => s.goals);
  const [level, setLevel] = useState<LevelState | null>(null);

  useEffect(() => {
    void (async () => {
      const lvl = await getApi().getLevel(uid);
      setLevel(lvl);
    })();
  }, [uid]);

  const title = profile?.levelTitle ?? 'Fresh Ducky';
  const xpPct = level ? (level.xpIntoLevel / Math.max(1, level.xpForNext)) : 0;

  return (
    <NeonBackdrop>
      <Screen>
        <ScrollView contentContainerStyle={styles.container} showsVerticalScrollIndicator={false}>
          <SectionHeader label="Profile" />
          <QuackoCard surface="high" style={styles.card}>
            <QuackoAvatar name={profile?.displayName ?? 'You'} size={72} neon="secondary" />
            <QuackoText variant="headline" neon="primary">{profile?.displayName ?? 'Quacko Member'}</QuackoText>
            <QuackoText variant="bodyMuted">@{profile?.username ?? 'ducky'}</QuackoText>
            <QuackoBadge label={title} kind="tertiary" emoji="🦆" />

            <View style={styles.levelBox}>
              <QuackoText variant="labelStrong" neon="secondary">
                Level {level?.level ?? 1}
              </QuackoText>
              <ProgressBar value={xpPct} color={colors.tertiary} height={8} />
              <QuackoText variant="caption">
                {(level?.totalXp ?? 0).toLocaleString()} XP · {(level?.xpIntoLevel ?? 0).toLocaleString()} /{' '}
                {level?.xpForNext ?? 0} to next title
              </QuackoText>
            </View>
          </QuackoCard>

          <SectionHeader label="Your goals" />
          {goals.length === 0 ? (
            <QuackoCard><QuackoText variant="bodyMuted">No goals yet — hop over to Today and start one.</QuackoText></QuackoCard>
          ) : (
            goals.map((g) => (
              <QuackoCard key={g.id} surface="low">
                <QuackoText variant="title">{g.title}</QuackoText>
                <QuackoText variant="bodyMuted">{g.category} · {g.schedule.cadence}</QuackoText>
                <View style={styles.goalProgress}>
                  <ProgressBar value={g.progress} color={colors.primary} height={7} />
                  <QuackoText variant="caption">{(g.progress * 100).toFixed(0)}%</QuackoText>
                </View>
              </QuackoCard>
            ))
          )}

          <SectionHeader label="Mode" />
          <QuackoCard surface="low" style={styles.card}>
            <QuackoText variant="body">
              Demo backend running on the in-memory store with the deterministic demo coach. Swap the{' '}
              <QuackoText variant="labelStrong">EXPO_PUBLIC_DEMO_MODE=0</QuackoText> flag and configure
              Firebase to go live.
            </QuackoText>
          </QuackoCard>
        </ScrollView>
      </Screen>
    </NeonBackdrop>
  );
}

const styles = StyleSheet.create({
  container: { padding: 20, paddingBottom: 96, gap: 16 },
  card: { alignItems: 'center', gap: 12, padding: 24 },
  levelBox: { width: '100%', gap: 8, marginTop: 4 },
  goalProgress: { flexDirection: 'row', alignItems: 'center', gap: 10, marginTop: 8 },
});