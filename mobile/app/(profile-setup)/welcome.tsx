/**
 * Welcome Step (Step 1)
 *
 * First step of the profile setup wizard.
 * Displays ForkIt logo with value proposition.
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { useRouter } from 'expo-router';
import { StepLayout } from '../../components/onboarding/StepLayout';
import { colors } from '../../constants/theme';

export default function WelcomeStep() {
  const router = useRouter();

  const handleNext = () => {
    router.push('/(profile-setup)/dietary');
  };

  return (
    <StepLayout
      title="Bienvenue sur ForkIt"
      subtitle="Configurez votre profil en quelques etapes pour recevoir des suggestions de recettes personnalisees."
      currentStep={1}
      totalSteps={5}
      onNext={handleNext}
      nextLabel="Commencer"
    >
      <View style={styles.content}>
        {/* Logo container */}
        <View style={styles.logoContainer}>
          <Text style={styles.logo}>🍴</Text>
        </View>

        {/* Value propositions */}
        <View style={styles.features}>
          <View style={styles.feature}>
            <Text style={styles.featureIcon}>📅</Text>
            <Text style={styles.featureText}>
              Planification hebdomadaire simplifiee
            </Text>
          </View>
          <View style={styles.feature}>
            <Text style={styles.featureIcon}>🛒</Text>
            <Text style={styles.featureText}>
              Liste de courses automatique
            </Text>
          </View>
          <View style={styles.feature}>
            <Text style={styles.featureIcon}>✨</Text>
            <Text style={styles.featureText}>
              Recettes adaptees a vos preferences
            </Text>
          </View>
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
  logoContainer: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 40,
  },
  logo: {
    fontSize: 56,
  },
  features: {
    gap: 20,
    paddingHorizontal: 16,
  },
  feature: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 16,
  },
  featureIcon: {
    fontSize: 28,
  },
  featureText: {
    fontSize: 16,
    color: colors.foreground,
    flex: 1,
  },
});
