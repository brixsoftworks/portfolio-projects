import { ScrollView, StyleSheet, View } from 'react-native';
import {
  NeonBackdrop,
  QuackoCard,
  QuackoIcon,
  QuackoText,
  Screen,
  SectionHeader,
  colors,
} from '@quacko/ui';
import { spacing } from '@quacko/ui';

const FEATURES: { icon: string; title: string; desc: string; tag: string }[] = [
  { icon: 'swords', title: 'Battles', desc: '1v1 streak duels with daily check-ins. Winner takes the XP pool.', tag: 'social' },
  { icon: 'how_to_vote', title: 'Punishment Council', desc: 'Group accountability: propose and vote on consequence rounds.', tag: 'social' },
  { icon: 'smart_toy', title: 'Group AI coach', desc: 'Quacko speaks in your group chat when energy dips.', tag: 'ai' },
  { icon: 'school', title: 'Learning plans', desc: 'Upload material, get a spaced-repetition plan with quizzes.', tag: 'learning' },
  { icon: 'monitor_heart', title: 'Proof verification', desc: 'GPS, timers, and human votes keep every streak honest.', tag: 'proof' },
  { icon: 'sports_martial_arts', title: 'Active tracking', desc: 'Live run/walk sessions auto-submit their own proof.', tag: 'activity' },
];

export default function ExploreScreen() {
  return (
    <NeonBackdrop>
      <Screen>
        <ScrollView contentContainerStyle={styles.container} showsVerticalScrollIndicator={false}>
          <SectionHeader label="Explore" />
          <QuackoText variant="headline" neon="secondary">
            The Quacko universe
          </QuackoText>
          <QuackoText variant="bodyMuted">
            Everything here plugs into the same backend. Each card becomes its own deep flow in the full
            release; demo mode exercises the shared engines today.
          </QuackoText>

          <View style={styles.grid}>
            {FEATURES.map((f) => (
              <QuackoCard key={f.title} surface="low" style={styles.feature}>
                <View style={styles.icon}>
                  <QuackoIcon symbol={f.icon} size={22} color={colors.secondary} />
                </View>
                <QuackoText variant="title">{f.title}</QuackoText>
                <QuackoText variant="bodyMuted">{f.desc}</QuackoText>
                <QuackoText variant="caption" neon="primary">{f.tag.toUpperCase()}</QuackoText>
              </QuackoCard>
            ))}
          </View>
        </ScrollView>
      </Screen>
    </NeonBackdrop>
  );
}

const styles = StyleSheet.create({
  container: { padding: 20, paddingBottom: 96, gap: 16 },
  grid: { flexDirection: 'row', flexWrap: 'wrap', gap: 14 },
  feature: { width: '47.5%', padding: 16, gap: 10, flexGrow: 1 },
  icon: {
    width: 42,
    height: 42,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.surfaceContainerHigh,
  },
});