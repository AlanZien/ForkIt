/**
 * TagsSelector Component
 *
 * Multi-select chips for recipe tags.
 * Predefined common recipe tags in French.
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

/** Predefined recipe tags */
export const RECIPE_TAGS = [
  'Rapide',
  'Facile',
  'Vegetarien',
  'Vegan',
  'Sans gluten',
  'Sans lactose',
  'Dessert',
  'Plat principal',
  'Entree',
  'Petit-dejeuner',
  'Snack',
  'Fete',
] as const;

export type RecipeTag = (typeof RECIPE_TAGS)[number];

interface TagsSelectorProps {
  /** Currently selected tags */
  selectedTags: string[];
  /** Callback when selection changes */
  onChange: (tags: string[]) => void;
  /** Whether the selector is disabled */
  disabled?: boolean;
  /** Container style override */
  style?: ViewStyle;
}

export function TagsSelector({
  selectedTags,
  onChange,
  disabled = false,
  style,
}: TagsSelectorProps) {
  const handlePress = (tag: string) => {
    if (disabled) return;

    const isSelected = selectedTags.includes(tag);
    if (isSelected) {
      onChange(selectedTags.filter((t) => t !== tag));
    } else {
      onChange([...selectedTags, tag]);
    }
  };

  return (
    <View style={[styles.container, style]}>
      {RECIPE_TAGS.map((tag) => {
        const isSelected = selectedTags.includes(tag);
        return (
          <TouchableOpacity
            key={tag}
            testID={`tag-${tag}`}
            onPress={() => handlePress(tag)}
            disabled={disabled}
            activeOpacity={disabled ? 1 : 0.7}
            accessibilityRole="button"
            accessibilityState={{
              selected: isSelected,
              disabled: disabled,
            }}
            accessibilityLabel={tag}
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
              {tag}
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
    borderRadius: borderRadius.xl,
    marginBottom: spacing.xs,
  },
  chipActive: {
    backgroundColor: colors.primary,
  },
  chipInactive: {
    backgroundColor: colors.muted,
  },
  chipDisabled: {
    opacity: 0.5,
  },
  chipText: {
    fontSize: 14,
    fontWeight: '500',
  },
  chipTextActive: {
    color: colors.primaryForeground,
  },
  chipTextInactive: {
    color: colors.foreground,
  },
});
