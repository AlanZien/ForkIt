/**
 * Allergies Step (Step 3)
 *
 * Third step of the profile setup wizard.
 * Allows users to select their allergies.
 */

import React from 'react';
import { View, StyleSheet } from 'react-native';
import { useRouter } from 'expo-router';
import { StepLayout } from '../../components/onboarding/StepLayout';
import { ChipSelector } from '../../components/preferences/ChipSelector';
import { useOnboardingStore } from '../../stores/onboarding';
import {
  ALL_ALLERGY_TYPES,
  ALLERGY_LABELS,
  AllergyType,
} from '../../types/preferences';
import { spacing } from '../../constants/theme';

export default function AllergiesStep() {
  const router = useRouter();
  const allergies = useOnboardingStore((state) => state.allergies);
  const setAllergies = useOnboardingStore((state) => state.setAllergies);

  const handleNext = () => {
    router.push('/(profile-setup)/portions');
  };

  const handleBack = () => {
    router.back();
  };

  const handleSkip = () => {
    setAllergies([]);
    router.push('/(profile-setup)/portions');
  };

  const handleSelect = (values: AllergyType[]) => {
    setAllergies(values);
  };

  return (
    <StepLayout
      title="Vos allergies"
      subtitle="Selectionnez vos allergies pour filtrer les recettes contenant des ingredients inadaptes."
      currentStep={3}
      totalSteps={5}
      onNext={handleNext}
      nextLabel="Suivant"
      onBack={handleBack}
      onSkip={handleSkip}
    >
      <View style={styles.content}>
        <ChipSelector
          options={ALL_ALLERGY_TYPES}
          labels={ALLERGY_LABELS}
          selectedValues={allergies}
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
