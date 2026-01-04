/**
 * ServingsStepper Component
 *
 * Numeric selector with +/- buttons for serving count.
 * Defaults: min=1, max=20 as per spec.
 */

import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ViewStyle,
} from 'react-native';
import { colors, borderRadius, spacing } from '../../constants/theme';

interface ServingsStepperProps {
  /** Current value */
  value: number;
  /** Callback when value changes */
  onChange: (value: number) => void;
  /** Minimum allowed value (default: 1) */
  min?: number;
  /** Maximum allowed value (default: 20) */
  max?: number;
  /** Whether the selector is disabled */
  disabled?: boolean;
  /** Container style override */
  style?: ViewStyle;
}

export function ServingsStepper({
  value,
  onChange,
  min = 1,
  max = 20,
  disabled = false,
  style,
}: ServingsStepperProps) {
  const canDecrement = value > min && !disabled;
  const canIncrement = value < max && !disabled;

  const handleDecrement = () => {
    if (canDecrement) {
      onChange(value - 1);
    }
  };

  const handleIncrement = () => {
    if (canIncrement) {
      onChange(value + 1);
    }
  };

  return (
    <View style={[styles.container, style]}>
      <TouchableOpacity
        testID="decrement-servings"
        style={[styles.button, !canDecrement && styles.buttonDisabled]}
        onPress={handleDecrement}
        disabled={!canDecrement}
        accessibilityRole="button"
        accessibilityLabel="Diminuer le nombre de portions"
        accessibilityState={{ disabled: !canDecrement }}
      >
        <Text
          style={[styles.buttonText, !canDecrement && styles.buttonTextDisabled]}
        >
          -
        </Text>
      </TouchableOpacity>

      <View style={styles.valueContainer}>
        <Text style={[styles.value, disabled && styles.valueDisabled]}>
          {value}
        </Text>
        <Text style={[styles.label, disabled && styles.valueDisabled]}>
          {value === 1 ? 'portion' : 'portions'}
        </Text>
      </View>

      <TouchableOpacity
        testID="increment-servings"
        style={[styles.button, !canIncrement && styles.buttonDisabled]}
        onPress={handleIncrement}
        disabled={!canIncrement}
        accessibilityRole="button"
        accessibilityLabel="Augmenter le nombre de portions"
        accessibilityState={{ disabled: !canIncrement }}
      >
        <Text
          style={[styles.buttonText, !canIncrement && styles.buttonTextDisabled]}
        >
          +
        </Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.md,
  },
  button: {
    width: 44,
    height: 44,
    borderRadius: borderRadius.lg,
    backgroundColor: colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
  },
  buttonDisabled: {
    backgroundColor: colors.muted,
  },
  buttonText: {
    fontSize: 22,
    fontWeight: '600',
    color: colors.primaryForeground,
  },
  buttonTextDisabled: {
    color: colors.mutedForeground,
  },
  valueContainer: {
    minWidth: 80,
    height: 44,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.inputBackground,
    borderRadius: borderRadius.md,
    paddingHorizontal: spacing.md,
  },
  value: {
    fontSize: 18,
    fontWeight: '600',
    color: colors.foreground,
  },
  label: {
    fontSize: 12,
    color: colors.mutedForeground,
    marginTop: -2,
  },
  valueDisabled: {
    opacity: 0.5,
  },
});
