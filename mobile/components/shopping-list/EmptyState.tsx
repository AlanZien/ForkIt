/**
 * EmptyState Component
 *
 * Displays when the shopping list is empty.
 * Shows illustration and CTA to generate list.
 */

import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface EmptyStateProps {
  onGenerateList: () => void;
  isLoading?: boolean;
}

export function EmptyState({ onGenerateList, isLoading = false }: EmptyStateProps) {
  return (
    <View style={styles.container}>
      <View style={styles.iconContainer}>
        <Ionicons name="cart-outline" size={64} color="#D1D5DB" />
      </View>

      <Text style={styles.title}>Aucune liste de courses</Text>

      <Text style={styles.subtitle}>
        Generez une liste a partir de votre planning de la semaine
      </Text>

      <TouchableOpacity
        style={[styles.button, isLoading && styles.buttonDisabled]}
        onPress={onGenerateList}
        disabled={isLoading}
        activeOpacity={0.8}
        accessibilityRole="button"
        accessibilityLabel="Generer ma liste de courses"
      >
        {isLoading ? (
          <Text style={styles.buttonText}>Generation en cours...</Text>
        ) : (
          <>
            <Ionicons
              name="sparkles"
              size={18}
              color="#FFFFFF"
              style={styles.buttonIcon}
            />
            <Text style={styles.buttonText}>Generer ma liste</Text>
          </>
        )}
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 40,
  },
  iconContainer: {
    marginBottom: 24,
  },
  title: {
    fontSize: 20,
    fontWeight: '600',
    color: '#374151',
    textAlign: 'center',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 15,
    color: '#6B7280',
    textAlign: 'center',
    lineHeight: 22,
    marginBottom: 32,
  },
  button: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#14B8A6',
    paddingVertical: 14,
    paddingHorizontal: 24,
    borderRadius: 12,
  },
  buttonDisabled: {
    backgroundColor: '#9CA3AF',
  },
  buttonIcon: {
    marginRight: 8,
  },
  buttonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFFFFF',
  },
});
