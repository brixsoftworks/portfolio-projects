import { useState } from 'react';
import { Pressable, ScrollView, StyleSheet, View } from 'react-native';
import { useRouter } from 'expo-router';
import {
  NeonBackdrop,
  QuackoButton,
  QuackoCard,
  QuackoIcon,
  QuackoText,
  SectionHeader,
  colors,
} from '@quacko/ui';
import { spacing } from '@quacko/ui';
import { useApp } from '@/state/app';

const AREAS: { id: string; label: string; icon: string }[] = [
  { id: 'fitness', label: 'Fitness', icon: 'fitness' },
  { id: 'learning', label: 'Learning', icon: 'school' },
  { id: 'skills', label: 'Skills', icon: 'rocket_launch' },
  { id: 'reading', label: 'Reading', icon: 'menu_book' },
  { id: 'wellbeing', label: 'Wellbeing', icon: 'self_improvement' },
  { id: 'digital_habits', label: 'Digital habits', icon: 'nightlight' },
];

export default function OnboardingScreen() {
  const router = useRouter();
  const completeOnboarding = useApp((s) => s.completeOnboarding);
  const [step, setStep] = useState(0);
  const [selected, setSelected] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);

  const toggle = (id: string) =>
    setSelected((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]));

  const finish = async () => {
    setBusy(true);
    await completeOnboarding({ selectedAreas: selected, displayName: 'Demo Ducky' });
    router.replace('/(tabs)');
  };

  return (
    <NeonBackdrop>
      <ScrollView contentContainerStyle={styles.container} showsVerticalScrollIndicator={false}>
        {step === 0 && (
          <View style={styles.step}>
            <View style={styles.bigDuck}>🦆</View>
            <QuackoText variant="display" neon="primary" style={styles.centerText}>
              Meet Quacko
            </QuackoText>
            <QuackoText variant="body" style={styles.centerText}>
              Your high-energy streak coach, training council, and accountability duck. Pick a goal, show up
              daily, and never let the chain break.
            </QuackoText>
          </View>
        )}

        {step === 1 && (
          <View style={styles.step}>
            <SectionHeader label="What are you working on?" />
            <View style={styles.grid}>
              {AREAS.map((area) => {
                const on = selected.includes(area.id);
                return (
                  <Pressable key={area.id} onPress={() => toggle(area.id)}>
                    <QuackoCard surface={on ? 'high' : 'low'} accent={on ? 'primary' : null} style={styles.areaCard}>
                      <QuackoIcon symbol={area.icon} size={22} color={on ? colors.primary : colors.onSurfaceVariant} />
                      <QuackoText variant="labelStrong">{area.label}</QuackoText>
                    </QuackoCard>
                  </Pressable>
                );
              })}
            </View>
          </View>
        )}

        {step === 2 && (
          <View style={styles.step}>
            <QuackoText variant="headline" neon="secondary">
              Your streak, guarded
            </QuackoText>
            <QuackoText variant="bodyMuted" style={styles.centerText}>
              Quacko gives you 2 grace days and a shield before a streak breaks. Show proof, keep the chain
              alive, and earn XP toward your title.
            </QuackoText>
          </View>
        )}

        <View style={styles.footer}>
          <QuackoButton
            label={step === 2 ? 'Start' : 'Next'}
            icon="arrow_forward"
            fullWidth
            loading={busy}
            onPress={() => (step === 2 ? void finish() : setStep((s) => s + 1))}
          />
          {step > 0 ? (
            <Pressable onPress={() => setStep((s) => s - 1)} style={styles.backLink}>
              <QuackoText variant="label">Back</QuackoText>
            </Pressable>
          ) : null}
        </View>
      </ScrollView>
    </NeonBackdrop>
  );
}

const styles = StyleSheet.create({
  container: { flexGrow: 1, padding: 24, paddingTop: 96, gap: 24 },
  step: { flex: 1, alignItems: 'center', gap: 20 },
  centerText: { textAlign: 'center' },
  bigDuck: { fontSize: 72, marginBottom: 8 },
  grid: { flexDirection: 'row', flexWrap: 'wrap', gap: 12, justifyContent: 'center', width: '100%' },
  areaCard: { width: 156, padding: 16, gap: 8, alignItems: 'center' },
  footer: { gap: 12, alignItems: 'center' },
  backLink: { padding: 8 },
});