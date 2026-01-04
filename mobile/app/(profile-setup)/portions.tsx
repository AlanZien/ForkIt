/**
 * Portions Step (Step 4)
 *
 * Fourth step of the profile setup wizard.
 * Allows users to set their household size (portions count).
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { useRouter } from 'expo-router';
import { StepLayout } from '../../components/onboarding/StepLayout';
import { PortionSelector } from '../../components/preferences/PortionSelector';
import { useOnboardingStore } from '../../stores/onboarding';
import { colors, spacing } from '../../constants/theme';

export default function PortionsStep() {
  const router = useRouter();
  const portions = useOnboardingStore((state) => state.portions);
  const setPortions = useOnboardingStore((state) => state.setPortions);

  const handleNext = () => {
    router.push('/(profile-setup)/ready');
  };

  const handleBack = () => {
    router.back();
  };

  const handleSkip = () => {
    setPortions(2); // Default value
    router.push('/(profile-setup)/ready');
  };

  return (
    <StepLayout
      title="Nombre de personnes"
      subtitle="Indiquez le nombre de personnes pour ajuster les quantites des recettes."
      currentStep={4}
      totalSteps={5}
      onNext={handleNext}
      nextLabel="Suivant"
      onBack={handleBack}
      onSkip={handleSkip}
    >
      <View style={styles.content}>
        <View style={styles.selectorContainer}>
          <PortionSelector
            value={portions}
            onChange={setPortions}
            min={1}
            max={12}
          />
        </View>
        <Text style={styles.label}>
          {portions} {portions === 1 ? 'personne' : 'personnes'}
        </Text>
      </View>
    </StepLayout>
  );
}

const styles = StyleSheet.create({
  content: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: spacing['2xl'],
  },
  selectorContainer: {
    marginBottom: spacing.lg,
  },
  label: {
    fontSize: 18,
    fontWeight: '600',
    color: colors.foreground,
    textAlign: 'center',
  },
});
