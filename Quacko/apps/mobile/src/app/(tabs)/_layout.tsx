import type { ColorValue } from 'react-native';
import { StyleSheet } from 'react-native';
import { Tabs } from 'expo-router';
import { colors, QuackoIcon } from '@quacko/ui';

export default function TabsLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: colors.secondary,
        tabBarInactiveTintColor: colors.onSurfaceMuted,
        tabBarStyle: {
          backgroundColor: colors.scrim,
          borderTopColor: colors.outlineVariant,
          borderTopWidth: StyleSheet.hairlineWidth,
          height: 64,
          paddingBottom: 8,
        },
        tabBarLabelStyle: { fontFamily: 'SpaceGrotesk_700Bold', fontSize: 10 },
      }}
    >
      <Tabs.Screen name="index" options={{ title: 'Today', tabBarIcon: ({ color, size }) => <TabGlyph symbol="local_fire_department" color={color} size={size} /> }} />
      <Tabs.Screen name="chat" options={{ title: 'Chat', tabBarIcon: ({ color, size }) => <TabGlyph symbol="chat_bubble" color={color} size={size} /> }} />
      <Tabs.Screen name="explore" options={{ title: 'Explore', tabBarIcon: ({ color, size }) => <TabGlyph symbol="explore" color={color} size={size} /> }} />
      <Tabs.Screen name="profile" options={{ title: 'Profile', tabBarIcon: ({ color, size }) => <TabGlyph symbol="person" color={color} size={size} /> }} />
    </Tabs>
  );
}

function TabGlyph({ symbol, color, size }: { symbol: string; color: string | ColorValue; size: number }) {
  return <QuackoIcon symbol={symbol} color={color as string} size={size} />;
}