/**
 * PersonalBadge Component
 *
 * Small badge to indicate a personal recipe.
 * Uses accent colors from design system (amber/gold).
 */

import React from 'react';
import { View, Text, StyleSheet, ViewStyle } from 'react-native';
import { colors, borderRadius, spacing } from '../../constants/theme';

interface PersonalBadgeProps {
  /** Container style override */
  style?: ViewStyle;
}

export function PersonalBadge({ style }: PersonalBadgeProps) {
  return (
    <View style={[styles.badge, style]}>
      <Text style={styles.text}>Ma recette</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    backgroundColor: colors.accent, // #FEF3C7
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: borderRadius.sm,
  },
  text: {
    fontSize: 11,
    fontWeight: '600',
    color: colors.accentForeground, // #92400E
  },
});
