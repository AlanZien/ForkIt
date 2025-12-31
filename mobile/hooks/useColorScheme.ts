/**
 * Hook for detecting color scheme (light/dark mode)
 */

import { useColorScheme as useRNColorScheme } from 'react-native';

export function useColorScheme() {
  return useRNColorScheme() ?? 'light';
}
