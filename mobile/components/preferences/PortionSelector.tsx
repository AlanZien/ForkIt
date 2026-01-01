/**
 * PortionSelector Component
 *
 * Numeric selector with +/- buttons for portion count.
 * Enforces min/max bounds with visual feedback.
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

interface PortionSelectorProps {
  /** Current value */
  value: number;
  /** Callback when value changes */
  onChange: (value: number) => void;
  /** Minimum allowed value */
  min: number;
  /** Maximum allowed value */
  max: number;
  /** Whether the selector is disabled */
  disabled?: boolean;
  /** Container style override */
  style?: ViewStyle;
}

export function PortionSelector({
  value,
  onChange,
  min,
  max,
  disabled = false,
  style,
}: PortionSelectorProps) {
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
      {/* Decrement button */}
      <TouchableOpacity
        testID="decrement-button"
        style={[
          styles.button,
          !canDecrement && styles.buttonDisabled,
        ]}
        onPress={handleDecrement}
        disabled={!canDecrement}
        accessibilityRole="button"
        accessibilityLabel="Diminuer"
        accessibilityState={{ disabled: !canDecrement }}
      >
        <Text
          style={[
            styles.buttonText,
            !canDecrement && styles.buttonTextDisabled,
          ]}
        >
          -
        </Text>
      </TouchableOpacity>

      {/* Value display */}
      <View style={styles.valueContainer}>
        <Text style={[styles.value, disabled && styles.valueDisabled]}>
          {value}
        </Text>
      </View>

      {/* Increment button */}
      <TouchableOpacity
        testID="increment-button"
        style={[
          styles.button,
          !canIncrement && styles.buttonDisabled,
        ]}
        onPress={handleIncrement}
        disabled={!canIncrement}
        accessibilityRole="button"
        accessibilityLabel="Augmenter"
        accessibilityState={{ disabled: !canIncrement }}
      >
        <Text
          style={[
            styles.buttonText,
            !canIncrement && styles.buttonTextDisabled,
          ]}
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
    width: 48,
    height: 48,
    borderRadius: borderRadius.lg, // 16px
    backgroundColor: colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
  },
  buttonDisabled: {
    backgroundColor: colors.muted,
  },
  buttonText: {
    fontSize: 24,
    fontWeight: '600',
    color: colors.primaryForeground,
  },
  buttonTextDisabled: {
    color: colors.mutedForeground,
  },
  valueContainer: {
    minWidth: 48,
    height: 48,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.inputBackground,
    borderRadius: borderRadius.md,
    paddingHorizontal: spacing.md,
  },
  value: {
    fontSize: 20,
    fontWeight: '600',
    color: colors.foreground,
  },
  valueDisabled: {
    opacity: 0.5,
  },
});
