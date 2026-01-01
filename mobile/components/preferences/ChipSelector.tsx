/**
 * ChipSelector Component
 *
 * A multi-select chip component for dietary preferences and allergies.
 * Follows ForkIt Design System with teal active chips.
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

interface ChipSelectorProps<T extends string> {
  /** Available options to display as chips */
  options: T[];
  /** Labels for each option (localized) */
  labels: Record<T, string>;
  /** Currently selected values */
  selectedValues: T[];
  /** Callback when selection changes */
  onSelect: (values: T[]) => void;
  /** Whether the selector is disabled */
  disabled?: boolean;
  /** Container style override */
  style?: ViewStyle;
}

export function ChipSelector<T extends string>({
  options,
  labels,
  selectedValues,
  onSelect,
  disabled = false,
  style,
}: ChipSelectorProps<T>) {
  const handlePress = (option: T) => {
    if (disabled) return;

    const isSelected = selectedValues.includes(option);
    if (isSelected) {
      // Remove from selection
      onSelect(selectedValues.filter((v) => v !== option));
    } else {
      // Add to selection
      onSelect([...selectedValues, option]);
    }
  };

  return (
    <View style={[styles.container, style]}>
      {options.map((option) => {
        const isSelected = selectedValues.includes(option);
        return (
          <TouchableOpacity
            key={option}
            testID={`chip-${option}`}
            onPress={() => handlePress(option)}
            disabled={disabled}
            activeOpacity={disabled ? 1 : 0.7}
            accessibilityRole="button"
            accessibilityState={{
              selected: isSelected,
              disabled: disabled,
            }}
            accessibilityLabel={labels[option]}
            style={[
              styles.chip,
              isSelected ? styles.chipActive : styles.chipInactive,
              disabled && styles.chipDisabled,
            ]}
          >
            <Text
              style={[
                styles.chipText,
                isSelected ? styles.chipTextActive : styles.chipTextInactive,
              ]}
            >
              {labels[option]}
            </Text>
          </TouchableOpacity>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
  },
  chip: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.xl, // 20px for chips
    marginBottom: spacing.xs,
  },
  chipActive: {
    backgroundColor: colors.primary, // #14B8A6 teal
  },
  chipInactive: {
    backgroundColor: colors.muted, // #F3F4F6
  },
  chipDisabled: {
    opacity: 0.5,
  },
  chipText: {
    fontSize: 14,
    fontWeight: '500',
  },
  chipTextActive: {
    color: colors.primaryForeground, // white
  },
  chipTextInactive: {
    color: colors.foreground, // #1F2937
  },
});
