/**
 * Profile Setup Layout
 *
 * Stack navigator for the 5-step profile setup wizard.
 * Routes: welcome, dietary, allergies, portions, ready
 */

import { Stack } from 'expo-router';

export default function ProfileSetupLayout() {
  return (
    <Stack
      screenOptions={{
        headerShown: false,
        contentStyle: { backgroundColor: '#FFFFFF' },
        animation: 'slide_from_right',
      }}
    >
      <Stack.Screen name="welcome" />
      <Stack.Screen name="dietary" />
      <Stack.Screen name="allergies" />
      <Stack.Screen name="portions" />
      <Stack.Screen name="ready" />
    </Stack>
  );
}
