import { useCallback, useEffect, useState } from 'react';
import { ActivityIndicator, Pressable, ScrollView, StyleSheet, View } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import {
  NeonBackdrop,
  QuackoBadge,
  QuackoButton,
  QuackoCard,
  QuackoIcon,
  ProgressBar,
  QuackoText,
  Screen,
  colors,
  glow,
} from '@quacko/ui';
import { spacing } from '@quacko/ui';
import type { Mission } from '@quacko/types';
import { getApi } from '@/lib/api';
import { useApp } from '@/state/app';

export default function MissionScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const uid = useApp((s) => s.uid);
  const [mission, setMission] = useState<Mission | null>(null);
  const [busy, setBusy] = useState(false);
  const [state, setState] = useState<'loading' | 'ready'>('loading');
  const [lastResult, setLastResult] = useState<string | null>(null);

  const reload = useCallback(async () => {
    if (!id) return;
    const m = await getApi().getMission(id);
    setMission(m ?? null);
    setState('ready');
  }, [id]);

  useEffect(() => {
    void reload();
  }, [reload]);

  const action = async (fn: () => Promise<unknown>, note: string) => {
    setBusy(true);
    setLastResult(null);
    try {
      await fn();
      setLastResult(note);
      await reload();
    } catch (e) {
      setLastResult(e instanceof Error ? e.message : note);
    } finally {
      setBusy(false);
    }
  };

  if (state === 'loading' || !mission) {
    return (
      <NeonBackdrop>
        <Screen>
          <View style={styles.center}><ActivityIndicator color={colors.secondary} /></View>
        </Screen>
      </NeonBackdrop>
    );
  }

  const done = mission.status === 'verified' || mission.status === 'completed';

  return (
    <NeonBackdrop>
      <Screen edges={['bottom']}>
        <ScrollView contentContainerStyle={styles.container} showsVerticalScrollIndicator={false}>
          <View style={styles.topRow}>
            <Pressable onPress={() => router.back()} style={styles.backLink} testID="mission-back" accessibilityRole="button">
              <QuackoIcon symbol="arrow_back" size={20} color={colors.primary} />
              <QuackoText variant="label">Back</QuackoText>
            </Pressable>
            <View style={{ flexDirection: 'row', alignItems: 'center', gap: 10 }}>
              <QuackoBadge label={mission.status.replace('_', ' ')} kind={done ? 'success' : 'secondary'} />
              <QuackoText variant="caption">{mission.dueDay}</QuackoText>
            </View>
          </View>

          <QuackoText variant="display" neon="primary">
            {mission.title}
          </QuackoText>
          <QuackoText variant="body" style={styles.mutedText}>
            {mission.description}
          </QuackoText>

          <QuackoCard padded style={{ gap: 12 }}>
            <QuackoText variant="labelStrong">Goal plan</QuackoText>
            <ProgressBar value={mission.progress} color={done ? colors.secondary : colors.primary} height={8} />
            <View style={styles.metaRow}>
              <Meta icon="timer" label={`${mission.durationMinutes} min`} />
              <Meta icon="target" label={mission.target} />
            </View>
          </QuackoCard>

          {lastResult ? (
            <QuackoCard surface="high" accent="secondary" style={{ padding: 16 }}>
              <View style={{ flexDirection: 'row', gap: 10, alignItems: 'center' }}>
                <QuackoIcon symbol={lastResult.startsWith('error') || lastResult.includes('Error') ? 'warning' : 'check_circle'} size={20} color={colors.tertiary} />
                <QuackoText variant="body" style={{ flex: 1 }}>{lastResult}</QuackoText>
              </View>
            </QuackoCard>
          ) : null}

          <View style={styles.actions}>
            <QuackoButton
              label="Start mission"
              variant="outline"
              icon="play"
              testID="mission-start"
              disabled={mission.status !== 'available' || busy}
              onPress={() => void action(() => getApi().startMission(uid, { missionId: mission.id }), 'Mission started — focus up.')}
            />

            <QuackoButton
              label="I did it"
              variant="accent"
              icon="check"
              fullWidth
              testID="mission-done"
              disabled={done || busy}
              onPress={() =>
                void action(async () => {
                  await getApi().finishMission(uid, { missionId: mission.id, percent: 100 });
                  await submitProofFor(uid, mission);
                }, 'Proof submitted.')
              }
            />
          </View>

          {done ? (
            <QuackoCard surface="high" accent="secondary" style={{ padding: 16, alignItems: 'center', gap: 6 }}>
              <QuackoIcon symbol="emoji_events" size={34} color={colors.tertiary} />
              <QuackoText variant="title" neon="secondary">Streak day saved</QuackoText>
              <QuackoText variant="bodyMuted" style={styles.centerText}>
                Quacko verified your effort and awarded XP.
              </QuackoText>
            </QuackoCard>
          ) : null}
        </ScrollView>
      </Screen>
    </NeonBackdrop>
  );
}

function Meta({ icon, label }: { icon: string; label: string }) {
  return (
    <View style={styles.meta}>
      <QuackoIcon symbol={icon} size={16} color={colors.onSurfaceVariant} />
      <QuackoText variant="label">{label}</QuackoText>
    </View>
  );
}

async function submitProofFor(uid: string, mission: Mission) {
  const goal = await getApi().getGoal(mission.goalId);
  let type: string = mission.proofType;
  let metadata: Record<string, unknown> = {};
  switch (mission.proofType) {
    case 'quiz':
      metadata = { score: 0.9 };
      break;
    case 'gps':
      type = 'gps';
      metadata = { distanceMeters: 2500, durationSeconds: mission.durationMinutes * 60 };
      break;
    case 'timer':
      metadata = { durationSeconds: mission.durationMinutes * 60 };
      break;
    default:
      metadata = { confirm: true };
      break;
  }
  await getApi().submitProof(uid, {
    missionId: mission.id,
    proof: {
      type: type as Mission['proofType'],
      metadata,
      mediaUrl: null,
    },
  });
  void goal;
}

const styles = StyleSheet.create({
  container: { padding: 24, paddingBottom: 120, gap: 18 },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  mutedText: { opacity: 0.85 },
  centerText: { textAlign: 'center' },
  topRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  backLink: { flexDirection: 'row', alignItems: 'center', gap: 6, paddingVertical: 4, paddingRight: 8 },
  metaRow: { flexDirection: 'row', gap: 16 },
  meta: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  actions: { gap: 10, marginTop: 4 },
});