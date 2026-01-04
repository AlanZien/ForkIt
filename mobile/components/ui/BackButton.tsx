/**
 * BackButton Component
 *
 * Navigation back button with "Retour" text
 */

import React from 'react';
import { TouchableOpacity, Text, StyleSheet } from 'react-native';
import { useRouter } from 'expo-router';

interface BackButtonProps {
  onPress?: () => void;
  label?: string;
}

export function BackButton({ onPress, label = 'Retour' }: BackButtonProps) {
  const router = useRouter();

  const handlePress = () => {
    if (onPress) {
      onPress();
    } else {
      router.back();
    }
  };

  return (
    <TouchableOpacity
      style={styles.container}
      onPress={handlePress}
      accessibilityRole="button"
      accessibilityLabel={label}
    >
      <Text style={styles.arrow}>←</Text>
      <Text style={styles.text}>{label}</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
  },
  arrow: {
    fontSize: 18,
    color: '#14B8A6',
    marginRight: 4,
  },
  text: {
    fontSize: 16,
    color: '#14B8A6',
    fontWeight: '500',
  },
});
