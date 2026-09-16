import { useState } from 'react';
import { KeyboardAvoidingView, Platform, Pressable, StyleSheet, TextInput, View } from 'react-native';
import { useRouter } from 'expo-router';
import { NeonBackdrop, QuackoButton, QuackoText, colors, radius, spacing, textGlow } from '@quacko/ui';
import { useAuth } from '@/state/auth';

export default function LoginScreen() {
  const router = useRouter();
  const login = useAuth((s) => s.login);
  const busy = useAuth((s) => s.busy);
  const error = useAuth((s) => s.error);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const submit = async () => {
    try {
      const profile = await login(email.trim(), password);
      router.replace(profile.hasSeenOnboarding ? '/(tabs)' : '/onboarding');
    } catch {
      // error is surfaced via useAuth().error
    }
  };

  return (
    <NeonBackdrop>
      <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined} style={styles.flex}>
        <View style={styles.container}>
          <View style={styles.header}>
            <QuackoText variant="display" neon="secondary" style={styles.wordmark}>
              QUACKO
            </QuackoText>
            <QuackoText variant="bodyMuted">Don't break the streak</QuackoText>
          </View>

          <View style={styles.card}>
            <TextInput
              value={email}
              onChangeText={setEmail}
              placeholder="email"
              placeholderTextColor={colors.onSurfaceMuted}
              autoCapitalize="none"
              autoCorrect={false}
              keyboardType="email-address"
              style={styles.input}
              testID="login-email"
            />
            <TextInput
              value={password}
              onChangeText={setPassword}
              placeholder="password"
              placeholderTextColor={colors.onSurfaceMuted}
              secureTextEntry
              style={styles.input}
              testID="login-password"
            />
            {error ? (
              <QuackoText variant="caption" style={styles.error}>
                {error}
              </QuackoText>
            ) : null}
            <QuackoButton label="Log in" onPress={submit} loading={busy} fullWidth testID="login-submit" />
          </View>

          <Pressable onPress={() => router.push('/register')} style={styles.switch} testID="goto-register">
            <QuackoText variant="label">
              New here? <QuackoText variant="labelStrong">Create an account</QuackoText>
            </QuackoText>
          </Pressable>
        </View>
      </KeyboardAvoidingView>
    </NeonBackdrop>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1 },
  container: { flex: 1, justifyContent: 'center', padding: spacing.xl, gap: spacing.xl },
  header: { alignItems: 'center', gap: spacing.sm },
  wordmark: { letterSpacing: 6, fontSize: 40, ...textGlow(colors.secondary, 12) },
  card: { backgroundColor: colors.surfaceContainer, borderRadius: radius.xl, borderWidth: 1, borderColor: colors.outlineVariant, padding: spacing.lg, gap: spacing.md },
  input: {
    backgroundColor: colors.surfaceContainerHigh,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.outlineVariant,
    color: colors.onSurface,
    fontFamily: 'Inter_400Regular',
    fontSize: 15,
    paddingHorizontal: spacing.lg,
    height: 52,
  },
  error: { color: colors.error },
  switch: { alignItems: 'center', paddingVertical: spacing.sm },
});