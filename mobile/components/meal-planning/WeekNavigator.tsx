/**
 * WeekNavigator Component
 *
 * Navigation header for week-to-week navigation in meal planning.
 * Shows current week label with left/right arrows.
 */

import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ViewStyle } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { formatDayMonth, getMonthName } from '../../utils/date';

interface WeekNavigatorProps {
  onPrevious: () => void;
  onNext: () => void;
  canGoPrev: boolean;
  canGoNext: boolean;
  style?: ViewStyle;
}

export function WeekNavigator({
  onPrevious,
  onNext,
  canGoPrev,
  canGoNext,
  style,
}: WeekNavigatorProps) {
  // Generate label: "7 prochains jours" with date range
  const today = new Date();
  const endDate = new Date(today);
  endDate.setDate(today.getDate() + 6);
  const weekLabel = `${today.getDate()} - ${endDate.getDate()} ${getMonthName(endDate)}`;

  return (
    <View style={[styles.container, style]}>
      <TouchableOpacity
        style={[styles.arrowButton, !canGoPrev && styles.arrowButtonDisabled]}
        onPress={onPrevious}
        disabled={!canGoPrev}
        activeOpacity={0.7}
        hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
        accessibilityRole="button"
        accessibilityLabel="Semaine precedente"
        accessibilityState={{ disabled: !canGoPrev }}
      >
        <Ionicons
          name="chevron-back"
          size={24}
          color={canGoPrev ? '#111827' : '#D1D5DB'}
        />
      </TouchableOpacity>

      <View style={styles.labelContainer}>
        <Text style={styles.weekLabel}>{weekLabel}</Text>
      </View>

      <TouchableOpacity
        style={[styles.arrowButton, !canGoNext && styles.arrowButtonDisabled]}
        onPress={onNext}
        disabled={!canGoNext}
        activeOpacity={0.7}
        hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
        accessibilityRole="button"
        accessibilityLabel="Semaine suivante"
        accessibilityState={{ disabled: !canGoNext }}
      >
        <Ionicons
          name="chevron-forward"
          size={24}
          color={canGoNext ? '#111827' : '#D1D5DB'}
        />
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  arrowButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#F3F4F6',
    justifyContent: 'center',
    alignItems: 'center',
  },
  arrowButtonDisabled: {
    backgroundColor: '#F9FAFB',
  },
  labelContainer: {
    flex: 1,
    alignItems: 'center',
  },
  weekLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111827',
  },
});
