/**
 * Dietary Preferences Step (Step 2)
 *
 * Second step of the profile setup wizard.
 * Allows users to select their dietary preferences.
 */

import React from 'react';
import { View, StyleSheet } from 'react-native';
import { useRouter } from 'expo-router';
import { StepLayout } from '../../components/onboarding/StepLayout';
import { ChipSelector } from '../../components/preferences/ChipSelector';
import { useOnboardingStore } from '../../stores/onboarding';
import {
  ALL_DIETARY_TYPES,
  DIETARY_LABELS,
  DietaryType,
} from '../../types/preferences';
import { spacing } from '../../constants/theme';

export default function DietaryStep() {
  const router = useRouter();
  const dietaryPreferences = useOnboardingStore(
    (state) => state.dietaryPreferences
  );
  const setDietaryPreferences = useOnboardingStore(
    (state) => state.setDietaryPreferences
  );

  const handleNext = () => {
    router.push('/(profile-setup)/allergies');
  };

  const handleBack = () => {
    router.back();
  };

  const handleSkip = () => {
    setDietaryPreferences([]);
    router.push('/(profile-setup)/allergies');
  };

  const handleSelect = (values: DietaryType[]) => {
    setDietaryPreferences(values);
  };

  return (
    <StepLayout
      title="Vos regimes alimentaires"
      subtitle="Selectionnez vos preferences alimentaires pour recevoir des recettes adaptees."
      currentStep={2}
      totalSteps={5}
      onNext={handleNext}
      nextLabel="Suivant"
      onBack={handleBack}
      onSkip={handleSkip}
    >
      <View style={styles.content}>
        <ChipSelector
          options={ALL_DIETARY_TYPES}
          labels={DIETARY_LABELS}
          selectedValues={dietaryPreferences}
          onSelect={handleSelect}
        />
      </View>
    </StepLayout>
  );
}

const styles = StyleSheet.create({
  content: {
    paddingTop: spacing.md,
  },
});
