import { View } from 'react-native';
import { QuackoText, type QuackoTextProps } from './Text';

/** Section header with gradient rule under the label. */
export function SectionHeader({ label, ...rest }: { label: string } & Partial<QuackoTextProps>) {
  return (
    <View style={{ gap: 6 }}>
      <QuackoText variant="labelStrong" {...rest} neon="secondary">
        {label.toUpperCase()}
      </QuackoText>
      <View style={{ height: 2, backgroundColor: 'rgba(255,45,120,0.5)', borderRadius: 2 }}>
      </View>
    </View>
  );
}