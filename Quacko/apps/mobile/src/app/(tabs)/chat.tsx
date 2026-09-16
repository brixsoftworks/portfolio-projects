import { useEffect, useState } from 'react';
import { Pressable, ScrollView, StyleSheet, TextInput, View } from 'react-native';
import {
  NeonBackdrop,
  QuackoButton,
  QuackoCard,
  QuackoIcon,
  QuackoText,
  Screen,
  SectionHeader,
  colors,
  glow,
} from '@quacko/ui';
import { spacing } from '@quacko/ui';
import { useApp } from '@/state/app';
import { getApi } from '@/lib/api';

interface ChatLine {
  role: 'user' | 'quacko';
  text: string;
}

export default function ChatScreen() {
  const uid = useApp((s) => s.uid);
  const goals = useApp((s) => s.goals);
  const [lines, setLines] = useState<ChatLine[]>([
    { role: 'quacko', text: 'Quack! I\'m your coach. How is today\'s mission going?' },
  ]);
  const [input, setInput] = useState('');
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    void (async () => {
      const goal = goals[0];
      if (!goal) return;
      const msg = await getApi().requestCoachMessage(uid, {
        goalId: goal.id,
        context: 'just_started',
      });
      if (msg?.message) {
        setLines((prev) => {
          if (prev.some((l) => l.text === msg.message)) return prev;
          return [...prev, { role: 'quacko', text: msg.message }];
        });
      }
    })();
  }, [goals, uid]);

  const send = async () => {
    const text = input.trim();
    if (!text) return;
    setInput('');
    setLines((prev) => [...prev, { role: 'user', text }]);
    setBusy(true);
    try {
      const goal = goals[0];
      const msg = await getApi().requestCoachMessage(uid, {
        goalId: goal?.id ?? 'root',
        context: 'chat',
        userMessage: text,
      });
      setLines((prev) => [...prev, { role: 'quacko', text: msg?.message ?? 'Quack!' }]);
    } finally {
      setBusy(false);
    }
  };

  return (
    <NeonBackdrop>
      <Screen>
        <ScrollView contentContainerStyle={styles.container} showsVerticalScrollIndicator={false}>
          <SectionHeader label="Quacko coach" />
          <QuackoCard surface="base">
            <View style={styles.coachRow}>
              <View style={styles.duck}>{busy ? '…' : '🦆'}</View>
              <QuackoText variant="bodyMuted" style={{ flex: 1 }}>
                Chat with Quacko for motivation, plan tweaks, and rescue missions. Demo mode uses the
                deterministic demo coach.
              </QuackoText>
            </View>
          </QuackoCard>

          {lines.map((line, i) => (
            <View key={i} style={[styles.bubbleWrap, line.role === 'user' ? styles.right : styles.left]}>
              <QuackoCard surface={line.role === 'quacko' ? 'high' : 'low'} accent={line.role === 'quacko' ? 'secondary' : null} style={styles.bubble}>
                <QuackoText variant="body">{line.text}</QuackoText>
              </QuackoCard>
            </View>
          ))}
        </ScrollView>

        <View style={styles.inputBar}>
          <TextInput
            value={input}
            onChangeText={setInput}
            placeholder="Message Quacko…"
            placeholderTextColor={colors.onSurfaceMuted}
            style={styles.input}
            onSubmitEditing={() => void send()}
          />
          <Pressable onPress={() => void send()} disabled={busy || !input.trim()} style={styles.send}>
            <QuackoIcon symbol="arrow_upward" size={20} color={colors.black} />
          </Pressable>
        </View>
      </Screen>
    </NeonBackdrop>
  );
}

const styles = StyleSheet.create({
  container: { padding: 20, paddingBottom: 24, gap: 14 },
  coachRow: { flexDirection: 'row', gap: 12, alignItems: 'center' },
  duck: {
    width: 44,
    height: 44,
    borderRadius: 22,
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: 24,
    backgroundColor: colors.surfaceContainerHigh,
    ...glow(colors.secondary, 12, 0.35),
  },
  bubbleWrap: { flexDirection: 'row' },
  left: { justifyContent: 'flex-start' },
  right: { justifyContent: 'flex-end' },
  bubble: { maxWidth: '82%', padding: 12 },
  inputBar: {
    flexDirection: 'row',
    gap: 10,
    paddingHorizontal: 16,
    paddingVertical: 10,
    backgroundColor: colors.scrim,
    borderTopWidth: 1,
    borderTopColor: colors.outlineVariant,
    alignItems: 'center',
  },
  input: {
    flex: 1,
    color: colors.onSurface,
    backgroundColor: colors.surfaceContainer,
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 10,
    fontSize: 15,
  },
  send: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.secondary,
  },
});