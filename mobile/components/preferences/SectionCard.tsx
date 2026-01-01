/**
 * SectionCard Component
 *
 * Reusable card wrapper for preference sections.
 * Provides consistent styling with title and optional edit indicator.
 */

import React, { ReactNode } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ViewStyle,
} from 'react-native';
import { colors, borderRadius, spacing, shadows } from '../../constants/theme';

interface SectionCardProps {
  /** Section title */
  title: string;
  /** Content to render inside the card */
  children: ReactNode;
  /** Whether the card is in editable mode */
  editable?: boolean;
  /** Test ID for the card container */
  testID?: string;
  /** Container style override */
  style?: ViewStyle;
}

export function SectionCard({
  title,
  children,
  editable = false,
  testID,
  style,
}: SectionCardProps) {
  return (
    <View
      testID={editable ? 'section-card-editable' : testID}
      style={[
        styles.container,
        editable && styles.containerEditable,
        style,
      ]}
    >
      <View style={styles.header}>
        <Text style={styles.title}>{title}</Text>
        {editable && (
          <View style={styles.editIndicator}>
            <Text style={styles.editIndicatorText}>En edition</Text>
          </View>
        )}
      </View>
      <View style={styles.content}>{children}</View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: colors.card,
    borderRadius: borderRadius.lg, // 16px for cards
    padding: spacing.md,
    marginBottom: spacing.lg, // 24px section spacing
    ...shadows.card,
  },
  containerEditable: {
    borderWidth: 2,
    borderColor: colors.primary,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: spacing.md,
  },
  title: {
    fontSize: 18,
    fontWeight: '600',
    color: colors.foreground,
  },
  editIndicator: {
    backgroundColor: colors.primary,
    borderRadius: borderRadius.sm,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
  },
  editIndicatorText: {
    fontSize: 12,
    fontWeight: '500',
    color: colors.primaryForeground,
  },
  content: {},
});
