import { useCallback, useEffect, useMemo, useState } from 'react';
import { Pressable, ScrollView, StyleSheet, View } from 'react-native';
import { useRouter, useFocusEffect } from 'expo-router';
import {
  NeonBackdrop,
  QuackoBadge,
  QuackoButton,
  QuackoCard,
  QuackoIcon,
  ProgressBar,
  QuackoText,
  Screen,
  SectionHeader,
  colors,
  glow,
} from '@quacko/ui';
import { spacing } from '@quacko/ui';
import { localDayKey } from '@quacko/domain/src/streak';
import type { Mission } from '@quacko/types';
import { useApp } from '@/state/app';
import { getApi } from '@/lib/api';

const PROOF_GLYPH: Record<string, string> = {
  gps: 'near_me',
  timer: 'timer',
  quiz: 'quiz',
  manual_log: 'check_circle',
  code_tests: 'terminal',
};

export default function TodayScreen() {
  const router = useRouter();
  const uid = useApp((s) => s.uid);
  const goals = useApp((s) => s.goals);
  const missions = useApp((s) => s.missions);
  const loadingMissions = useApp((s) => s.loadingMissions);
  const refreshGoals = useApp((s) => s.refreshGoals);
  const refreshMissions = useApp((s) => s.refreshMissions);
  const profile = useApp((s) => s.profile);
  const [bestStreak, setBestStreak] = useState(0);

  const today = useMemo(() => {
    const tz = profile?.timezone || 'UTC';
    return localDayKey(new Date(), tz);
  }, [profile]);

  const refreshAll = useCallback(() => {
    void refreshGoals();
    void refreshMissions();
  }, [refreshGoals, refreshMissions]);

  useFocusEffect(
    useCallback(() => {
      void refreshGoals();
      void refreshMissions();
    }, [refreshGoals, refreshMissions]),
  );

  useEffect(() => {
    let alive = true;
    Promise.all(
      goals.map(async (g) => {
        const streak = await getApi().getStreak(uid, g.id);
        return streak?.currentStreak ?? 0;
      }),
    )
      .then((values) => {
        if (alive) setBestStreak(Math.max(0, ...values));
      })
      .catch(() => {});
    return () => {
      alive = false;
    };
  }, [goals, missions, uid]);

  const todayMissions = useMemo(() => missions.filter((m) => m.dueDay === today && m.status !== 'failed'), [missions, today]);
  const upcoming = useMemo(() => missions.filter((m) => m.dueDay !== today).slice(0, 3), [missions, today]);

  const createDemoGoal = async () => {
    const goal = await getApi().createGoal(uid, {
      title: 'Run a little every day',
      description: 'Build the unbreakable running habit.',
      category: 'fitness',
      target: 'Run 3 km',
      dailyAvailabilityMinutes: 30,
      schedule: { cadence: 'daily', days: [], timezone: profile?.timezone || 'UTC' },
      difficulty: 'easy',
      proofRequired: true,
      deadline: null,
    });
    await getApi().generateGoalPlan(uid, goal.id);
    await refreshAll();
  };

  return (
    <NeonBackdrop>
      <Screen>
        <ScrollView contentContainerStyle={styles.container} showsVerticalScrollIndicator={false}>
          <Header bestStreak={bestStreak} />
          <SectionHeader label="Today's missions" />

          {goals.length === 0 ? (
            <QuackoCard padded style={styles.emptyGoal}>
              <QuackoIcon symbol="rocket_launch" size={40} color={colors.secondary} />
              <QuackoText variant="title">No goal yet</QuackoText>
              <QuackoText variant="bodyMuted" style={styles.centerText}>
                Start one and Quacko will generate your first daily mission.
              </QuackoText>
              <QuackoButton label="Create demo goal" variant="accent" icon="add" testID="create-goal" onPress={() => void createDemoGoal()} fullWidth />
            </QuackoCard>
          ) : loadingMissions ? (
            <QuackoCard><QuackoText variant="bodyMuted">Hatching missions…</QuackoText></QuackoCard>
          ) : todayMissions.length === 0 ? (
            <QuackoCard>
              <QuackoText variant="bodyMuted">All clear — you have no missions today. 🎉</QuackoText>
            </QuackoCard>
          ) : (
            todayMissions.map((mission) => <MissionRow key={mission.id} mission={mission} onPress={() => router.push(`/mission/${mission.id}`)} />)
          )}

          {upcoming.length > 0 && (
            <>
              <View style={styles.rule} />
              <SectionHeader label="Coming up" />
              {upcoming.map((mission) => <MissionRow key={mission.id} mission={mission} onPress={() => router.push(`/mission/${mission.id}`)} muted />)}
            </>
          )}
        </ScrollView>
      </Screen>
    </NeonBackdrop>
  );
}

function Header({ bestStreak }: { bestStreak: number }) {
  const profile = useApp((s) => s.profile);
  const goals = useApp((s) => s.goals);
  const streakLabel = profile?.displayName ? `Hi, ${profile.displayName.split(' ')[0]}` : 'Hi there';
  return (
    <View style={styles.header}>
      <View style={{ flex: 1, gap: 4 }}>
        <QuackoText variant="display" neon="secondary">
          {streakLabel} 👋
        </QuackoText>
        <QuackoText variant="bodyMuted">
          {goals.length > 0 ? 'Keep the chain alive.' : 'Ready when you are.'}
        </QuackoText>
      </View>
      <View style={styles.flame}>
        <QuackoIcon symbol="local_fire_department" size={30} color={colors.primary} glowColor={colors.primary} />
        <QuackoText variant="title" neon="primary" style={{ marginLeft: 6 }} testID="header-streak">
          {bestStreak}
        </QuackoText>
      </View>
    </View>
  );
}

function MissionRow({ mission, onPress, muted }: { mission: Mission; onPress: () => void; muted?: boolean }) {
  const statusKind =
    mission.status === 'verified' || mission.status === 'completed'
      ? 'success'
      : mission.status === 'failed' || mission.status === 'expired'
        ? 'danger'
        : 'secondary';
  return (
    <Pressable onPress={onPress} testID={`mission-row-${mission.id}`}>
      <QuackoCard surface={muted ? 'low' : 'base'} accent={!muted && mission.status === 'verified' ? 'secondary' : mission.status === 'failed' ? null : 'primary'}>
        <View style={styles.missionRow}>
          <View style={styles.missionIcon}>
            <QuackoIcon symbol={PROOF_GLYPH[mission.proofType] ?? 'target'} size={22} color={colors.secondary} />
          </View>
          <View style={{ flex: 1, gap: 6 }}>
            <View style={{ flexDirection: 'row', alignItems: 'center', gap: 8 }}>
              <QuackoText variant="title" style={{ flex: 1, opacity: muted ? 0.7 : 1 }}>
                {mission.title}
              </QuackoText>
              <QuackoBadge label={mission.status.replace('_', ' ')} kind={statusKind} />
            </View>
            <QuackoText variant="bodyMuted">
              {mission.durationMinutes} min · proof: {mission.proofType}
            </QuackoText>
            <ProgressBar value={mission.progress} color={mission.status === 'verified' ? colors.secondary : colors.primary} height={6} />
          </View>
        </View>
      </QuackoCard>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  container: { padding: 20, paddingBottom: 96, gap: 16 },
  header: { flexDirection: 'row', alignItems: 'center', gap: 12, marginBottom: 4 },
  flame: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 14,
    paddingVertical: 10,
    borderRadius: 99,
    backgroundColor: colors.surfaceContainer,
    borderWidth: 1,
    borderColor: colors.primaryContainer,
    ...glow(colors.primary, 14, 0.4),
  },
  emptyGoal: { alignItems: 'center', gap: 12, padding: 24 },
  centerText: { textAlign: 'center' },
  rule: { height: 1, backgroundColor: colors.outlineVariant, marginTop: 4 },
  missionRow: { flexDirection: 'row', gap: 12, alignItems: 'flex-start' },
  missionIcon: {
    width: 44,
    height: 44,
    borderRadius: 14,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.surfaceContainerHigh,
  },
});