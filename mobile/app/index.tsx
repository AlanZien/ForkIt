/**
 * App Entry Point
 *
 * Handles initial routing based on auth state and onboarding status.
 *
 * Routing logic:
 * 1. If not authenticated:
 *    - If seen onboarding slides -> login screen
 *    - Else -> onboarding slides screen
 * 2. If authenticated:
 *    - If onboarding NOT completed -> profile setup wizard
 *    - If onboarding completed -> main app (tabs)
 */

import { useEffect, useState } from 'react';
import { useRouter } from 'expo-router';
import { View, ActivityIndicator, StyleSheet } from 'react-native';
import { useAuthStore } from '../stores/auth';
import { hasSeenOnboarding } from '../services/onboardingStorage';
import { getOnboardingStatus } from '../services/onboarding';

export default function Index() {
  const router = useRouter();
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const isLoading = useAuthStore((state) => state.isLoading);
  const [isCheckingOnboarding, setIsCheckingOnboarding] = useState(false);

  useEffect(() => {
    const checkInitialRoute = async () => {
      if (isLoading) return;

      if (isAuthenticated) {
        // Check if user has completed profile setup
        setIsCheckingOnboarding(true);
        try {
          const { onboarding_completed } = await getOnboardingStatus();

          if (onboarding_completed) {
            // User has completed onboarding -> go to main app
            router.replace('/(tabs)');
          } else {
            // User needs to complete profile setup
            router.replace('/(profile-setup)/welcome');
          }
        } catch (error) {
          // If there's an error (e.g., network), assume onboarding not completed
          // to ensure user gets proper setup
          console.error('Error checking onboarding status:', error);
          router.replace('/(profile-setup)/welcome');
        } finally {
          setIsCheckingOnboarding(false);
        }
      } else {
        // Not authenticated - check if user has seen intro slides
        const seenOnboarding = await hasSeenOnboarding();
        if (seenOnboarding) {
          router.replace('/(auth)/login');
        } else {
          router.replace('/(auth)/onboarding');
        }
      }
    };

    checkInitialRoute();
  }, [isAuthenticated, isLoading, router]);

  return (
    <View style={styles.container}>
      <ActivityIndicator size="large" color="#14B8A6" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
  },
});
