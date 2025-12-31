/**
 * App Entry Point
 *
 * Handles initial routing based on auth state and onboarding status
 */

import { useEffect } from 'react';
import { useRouter } from 'expo-router';
import { View, ActivityIndicator, StyleSheet } from 'react-native';
import { useAuthStore } from '../stores/auth';
import { hasSeenOnboarding } from '../services/onboardingStorage';

export default function Index() {
  const router = useRouter();
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const isLoading = useAuthStore((state) => state.isLoading);

  useEffect(() => {
    const checkInitialRoute = async () => {
      if (isLoading) return;

      if (isAuthenticated) {
        router.replace('/(tabs)');
      } else {
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
