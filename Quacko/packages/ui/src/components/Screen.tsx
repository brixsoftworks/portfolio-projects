import type { ReactNode } from 'react';
import { View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

export interface ScreenProps {
  children?: ReactNode;
  edges?: ('top' | 'bottom' | 'left' | 'right')[];
}

/**
 * Standard page scaffold: safe area + flex container.
 */
export function Screen({ children, edges = ['top', 'bottom'] }: ScreenProps) {
  return (
    <SafeAreaView edges={edges} style={{ flex: 1 }}>
      <View style={{ flex: 1 }}>{children}</View>
    </SafeAreaView>
  );
}