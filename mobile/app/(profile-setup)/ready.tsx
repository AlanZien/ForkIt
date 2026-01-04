/**
 * Ready Step (Step 5)
 *
 * Final step of the profile setup wizard.
 * Confirms setup is complete and provides navigation options.
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { useRouter } from 'expo-router';
import { StepLayout } from '../../components/onboarding/StepLayout';
import { useOnboardingStore } from '../../stores/onboarding';
import { colors, spacing } from '../../constants/theme';

export default function ReadyStep() {
  const router = useRouter();
  const isLoading = useOnboardingStore((state) => state.isLoading);
  const completeOnboarding = useOnboardingStore(
    (state) => state.completeOnboarding
  );
  const reset = useOnboardingStore((state) => state.reset);

  const handlePlanWeek = async () => {
    await completeOnboarding();
    reset();
    router.replace('/(tabs)/planning');
  };

  const handleExploreRecipes = async () => {
    await completeOnboarding();
    reset();
    router.replace('/(tabs)/recipes');
  };

  const handleBack = () => {
    router.back();
  };

  return (
    <StepLayout
      title="Vous etes pret !"
      subtitle="Votre profil est configure. Commencez a explorer des recettes ou planifiez votre semaine."
      currentStep={5}
      totalSteps={5}
      onNext={handlePlanWeek}
      nextLabel="Planifier ma semaine"
      onBack={handleBack}
      isLoading={isLoading}
      secondaryLabel="Explorer les recettes"
      onSecondary={handleExploreRecipes}
    >
      <View style={styles.content}>
        {/* Celebration icon */}
        <View style={styles.iconContainer}>
          <Text style={styles.icon}>🎉</Text>
        </View>

        {/* Summary */}
        <View style={styles.summary}>
          <Text style={styles.summaryText}>
            Vos preferences ont ete enregistrees. Vous pouvez les modifier a
            tout moment dans votre profil.
          </Text>
        </View>
      </View>
    </StepLayout>
  );
}

const styles = StyleSheet.create({
  content: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  iconContainer: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: '#F0FDFA',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 32,
  },
  icon: {
    fontSize: 56,
  },
  summary: {
    paddingHorizontal: spacing.lg,
  },
  summaryText: {
    fontSize: 16,
    color: colors.mutedForeground,
    textAlign: 'center',
    lineHeight: 24,
  },
});
