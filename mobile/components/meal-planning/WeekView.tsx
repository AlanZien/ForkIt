/**
 * WeekView Component
 *
 * Horizontal scrollable view of 7 days for meal planning.
 * Shows loading, error, and empty states.
 */

import React from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  ActivityIndicator,
  TouchableOpacity,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { DayColumn } from './DayColumn';
import { useMealPlanningStore } from '../../stores/meal-planning';
import type { MealSlot, MealType } from '../../types/meal-slot';
import { parseISO, getWeekDates, generateSlotKey } from '../../utils/date';

interface WeekViewProps {
  onSlotPress: (date: string, mealType: MealType) => void;
  onSlotLongPress: (date: string, mealType: MealType, slot: MealSlot) => void;
}

export function WeekView({ onSlotPress, onSlotLongPress }: WeekViewProps) {
  const { slots, currentWeekStart, isLoading, error, fetchWeek } =
    useMealPlanningStore();

  // Get week dates
  const weekStartDate = parseISO(currentWeekStart);
  const weekDates = getWeekDates(weekStartDate);

  // Helper to get slot from map
  const getSlotForDay = (dateStr: string, mealType: MealType): MealSlot | null => {
    const key = generateSlotKey(dateStr, mealType);
    return slots.get(key) || null;
  };

  // Loading state
  if (isLoading) {
    return (
      <View style={styles.stateContainer}>
        <ActivityIndicator size="large" color="#14B8A6" />
        <Text style={styles.stateText}>Chargement...</Text>
      </View>
    );
  }

  // Error state
  if (error) {
    return (
      <View style={styles.stateContainer}>
        <Ionicons name="alert-circle-outline" size={48} color="#EF4444" />
        <Text style={styles.errorTitle}>Erreur de chargement</Text>
        <Text style={styles.errorMessage}>{error}</Text>
        <TouchableOpacity
          style={styles.retryButton}
          onPress={() => fetchWeek(currentWeekStart)}
          activeOpacity={0.8}
        >
          <Ionicons name="refresh" size={18} color="#FFFFFF" />
          <Text style={styles.retryButtonText}>Reessayer</Text>
        </TouchableOpacity>
      </View>
    );
  }

  // Count filled slots
  const filledSlotsCount = slots.size;
  const isEmpty = filledSlotsCount === 0;

  return (
    <View style={styles.container}>
      {/* Empty week hint */}
      {isEmpty && (
        <View style={styles.emptyHint}>
          <Ionicons name="information-circle-outline" size={20} color="#14B8A6" />
          <Text style={styles.emptyHintText}>
            Appuyez sur + pour ajouter un repas
          </Text>
        </View>
      )}

      {/* Week scrollable view */}
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.scrollContent}
        style={styles.scrollView}
      >
        {weekDates.map((date) => {
          const dateStr = date.toISOString().split('T')[0];
          return (
            <DayColumn
              key={dateStr}
              date={date}
              dejeunerSlot={getSlotForDay(dateStr, 'dejeuner')}
              dinerSlot={getSlotForDay(dateStr, 'diner')}
              onSlotPress={onSlotPress}
              onSlotLongPress={onSlotLongPress}
            />
          );
        })}
      </ScrollView>

      {/* Stats */}
      <View style={styles.statsContainer}>
        <View style={styles.statItem}>
          <Text style={styles.statNumber}>{filledSlotsCount}</Text>
          <Text style={styles.statLabel}>
            repas planifie{filledSlotsCount !== 1 ? 's' : ''}
          </Text>
        </View>
        <View style={styles.statDivider} />
        <View style={styles.statItem}>
          <Text style={styles.statNumber}>{14 - filledSlotsCount}</Text>
          <Text style={styles.statLabel}>
            creneau{14 - filledSlotsCount !== 1 ? 'x' : ''} libre
            {14 - filledSlotsCount !== 1 ? 's' : ''}
          </Text>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    padding: 16,
    paddingRight: 4,
  },
  stateContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 40,
  },
  stateText: {
    fontSize: 16,
    color: '#6B7280',
    marginTop: 12,
  },
  errorTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#374151',
    marginTop: 16,
  },
  errorMessage: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 8,
    textAlign: 'center',
  },
  retryButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#14B8A6',
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 20,
    marginTop: 20,
    gap: 8,
  },
  retryButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  emptyHint: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#CCFBF1',
    paddingVertical: 10,
    paddingHorizontal: 16,
    marginHorizontal: 16,
    marginTop: 8,
    borderRadius: 10,
    gap: 8,
  },
  emptyHintText: {
    fontSize: 14,
    color: '#0D9488',
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 16,
    paddingHorizontal: 24,
    backgroundColor: '#FFFFFF',
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
  },
  statItem: {
    alignItems: 'center',
    flex: 1,
  },
  statNumber: {
    fontSize: 24,
    fontWeight: '700',
    color: '#14B8A6',
  },
  statLabel: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 2,
  },
  statDivider: {
    width: 1,
    height: 32,
    backgroundColor: '#E5E7EB',
    marginHorizontal: 16,
  },
});
