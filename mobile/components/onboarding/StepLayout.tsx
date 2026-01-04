/**
 * StepLayout Component
 *
 * Shared layout for profile setup wizard steps.
 * Includes progress indicator, back button, title, subtitle, content area,
 * and action buttons (next/skip).
 */

import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Button } from '../ui';
import { colors, spacing } from '../../constants/theme';

interface StepLayoutProps {
  /** Step title */
  title: string;
  /** Step subtitle/description */
  subtitle: string;
  /** Current step number (1-5) */
  currentStep: number;
  /** Total number of steps */
  totalSteps: number;
  /** Content to render in the main area */
  children: React.ReactNode;
  /** Callback when next/primary button is pressed */
  onNext: () => void;
  /** Label for next/primary button */
  nextLabel: string;
  /** Callback when back button is pressed */
  onBack?: () => void;
  /** Callback when skip button is pressed */
  onSkip?: () => void;
  /** Whether the next button is loading */
  isLoading?: boolean;
  /** Whether to show secondary button (for final step) */
  secondaryLabel?: string;
  /** Callback for secondary button */
  onSecondary?: () => void;
}

export function StepLayout({
  title,
  subtitle,
  currentStep,
  totalSteps,
  children,
  onNext,
  nextLabel,
  onBack,
  onSkip,
  isLoading = false,
  secondaryLabel,
  onSecondary,
}: StepLayoutProps) {
  const showBackButton = currentStep > 1 && onBack;

  return (
    <SafeAreaView style={styles.container}>
      {/* Header with back button and progress */}
      <View style={styles.header}>
        {showBackButton ? (
          <TouchableOpacity
            testID="back-button"
            onPress={onBack}
            style={styles.backButton}
            accessibilityRole="button"
            accessibilityLabel="Retour"
          >
            <Text style={styles.backButtonText}>{'<'}</Text>
          </TouchableOpacity>
        ) : (
          <View style={styles.backButtonPlaceholder} />
        )}

        {/* Progress dots */}
        <View testID="progress-dots" style={styles.progressContainer}>
          {Array.from({ length: totalSteps }, (_, index) => (
            <View
              key={index}
              style={[
                styles.dot,
                index + 1 === currentStep && styles.dotActive,
              ]}
            />
          ))}
        </View>

        <View style={styles.backButtonPlaceholder} />
      </View>

      {/* Scrollable content */}
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Title and subtitle */}
        <View style={styles.textContainer}>
          <Text style={styles.title}>{title}</Text>
          <Text style={styles.subtitle}>{subtitle}</Text>
        </View>

        {/* Main content */}
        <View style={styles.content}>{children}</View>
      </ScrollView>

      {/* Footer with action buttons */}
      <View style={styles.footer}>
        <Button
          title={nextLabel}
          onPress={onNext}
          loading={isLoading}
          testID="next-button"
        />

        {secondaryLabel && onSecondary && (
          <Button
            title={secondaryLabel}
            onPress={onSecondary}
            variant="secondary"
            style={styles.secondaryButton}
            testID="secondary-button"
          />
        )}

        {onSkip && (
          <TouchableOpacity
            onPress={onSkip}
            style={styles.skipButton}
            accessibilityRole="button"
            testID="skip-button"
          >
            <Text style={styles.skipButtonText}>Passer</Text>
          </TouchableOpacity>
        )}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.md,
    paddingBottom: spacing.sm,
  },
  backButton: {
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  backButtonText: {
    fontSize: 24,
    color: colors.foreground,
    fontWeight: '500',
  },
  backButtonPlaceholder: {
    width: 40,
    height: 40,
  },
  progressContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    gap: spacing.xs,
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#E5E7EB',
  },
  dotActive: {
    width: 24,
    backgroundColor: colors.primary,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    paddingHorizontal: spacing.lg,
  },
  textContainer: {
    marginTop: spacing.xl,
    marginBottom: spacing.lg,
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    color: colors.foreground,
    marginBottom: spacing.sm,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 16,
    color: colors.mutedForeground,
    textAlign: 'center',
    lineHeight: 24,
  },
  content: {
    flex: 1,
    paddingVertical: spacing.lg,
  },
  footer: {
    paddingHorizontal: spacing.lg,
    paddingBottom: spacing.lg,
    paddingTop: spacing.md,
  },
  secondaryButton: {
    marginTop: spacing.sm,
  },
  skipButton: {
    marginTop: spacing.md,
    alignSelf: 'center',
    padding: spacing.sm,
  },
  skipButtonText: {
    fontSize: 16,
    color: colors.primary,
    fontWeight: '500',
  },
});
