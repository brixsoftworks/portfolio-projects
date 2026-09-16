import {
  Pressable,
  ActivityIndicator,
  type StyleProp,
  type ViewStyle,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { QuackoText } from './Text';
import { QuackoIcon } from './Icon';
import { colors, glow, primaryGradient, accentGradient, radius, spacing } from '../theme';

export interface QuackoButtonProps {
  label: string;
  onPress?: () => void;
  variant?: 'primary' | 'accent' | 'outline' | 'ghost' | 'danger';
  icon?: string;
  disabled?: boolean;
  loading?: boolean;
  style?: StyleProp<ViewStyle>;
  fullWidth?: boolean;
  testID?: string;
}

export function QuackoButton({
  label,
  onPress,
  variant = 'primary',
  icon,
  disabled = false,
  loading = false,
  style,
  fullWidth = false,
  testID,
}: QuackoButtonProps) {
  const isGradient = variant === 'primary' || variant === 'accent';

  const content = (
    <>
      {loading ? (
        <ActivityIndicator color={variant === 'outline' || variant === 'ghost' ? colors.primary : colors.background} />
      ) : (
        <>
          {icon ? <QuackoIcon symbol={icon} size={18} color={variant === 'ghost' ? colors.onSurfaceVariant : colors.background} /> : null}
          <QuackoText
            variant="labelStrong"
            style={{
              color:
                variant === 'outline'
                  ? colors.primary
                  : variant === 'ghost'
                    ? colors.onSurfaceVariant
                    : colors.background,
              marginLeft: icon ? spacing.sm : 0,
            }}
          >
            {label}
          </QuackoText>
        </>
      )}
    </>
  );

  const base: ViewStyle = {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    height: 52,
    paddingHorizontal: spacing.xl,
    borderRadius: radius.lg,
    gap: spacing.xs,
    opacity: disabled ? 0.5 : 1,
  };

  if (isGradient) {
    return (
      <Pressable
        onPress={onPress}
        disabled={disabled || loading}
        testID={testID}
        style={[base, glow(variant === 'primary' ? colors.primary : colors.secondary, 16, 0.4), fullWidth ? { flexGrow: 1 } : null, style]}
      >
        <LinearGradient
          colors={variant === 'primary' ? primaryGradient : accentGradient}
          style={base}
        >
          {content}
        </LinearGradient>
      </Pressable>
    );
  }

  const styleForVariant: ViewStyle =
    variant === 'outline'
      ? { borderWidth: 1.5, borderColor: colors.primary, backgroundColor: 'transparent' }
      : variant === 'danger'
        ? { backgroundColor: colors.errorContainer, borderWidth: 1, borderColor: colors.error }
        : { backgroundColor: colors.surfaceContainerHigh };

  return (
    <Pressable
      onPress={onPress}
      disabled={disabled || loading}
      testID={testID}
      style={[base, styleForVariant, fullWidth ? { flexGrow: 1 } : null, style]}
    >
      {content}
    </Pressable>
  );
}