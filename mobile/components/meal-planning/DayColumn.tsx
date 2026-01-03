/**
 * DayColumn Component
 *
 * Displays a single day in the weekly planning view.
 * Contains day name header, date, and two meal slot cards (lunch/dinner).
 */

import React from 'react';
import { View, Text, StyleSheet, ViewStyle } from 'react-native';
import { MealSlotCard } from './MealSlotCard';
import type { MealSlot, MealType } from '../../types/meal-slot';
import { getDayName, formatDayMonth, isToday, formatDateISO } from '../../utils/date';

interface DayColumnProps {
  date: Date;
  dejeunerSlot: MealSlot | null;
  dinerSlot: MealSlot | null;
  onSlotPress: (date: string, mealType: MealType) => void;
  onSlotLongPress: (date: string, mealType: MealType, slot: MealSlot) => void;
  style?: ViewStyle;
}

export function DayColumn({
  date,
  dejeunerSlot,
  dinerSlot,
  onSlotPress,
  onSlotLongPress,
  style,
}: DayColumnProps) {
  const dateStr = formatDateISO(date);
  const dayName = getDayName(date);
  const dayMonth = formatDayMonth(date);
  const isTodayDate = isToday(date);

  const handleSlotPress = (mealType: MealType) => {
    onSlotPress(dateStr, mealType);
  };

  const handleSlotLongPress = (mealType: MealType, slot: MealSlot | null) => {
    if (slot) {
      onSlotLongPress(dateStr, mealType, slot);
    }
  };

  return (
    <View style={[styles.container, isTodayDate && styles.todayContainer, style]}>
      <View style={[styles.header, isTodayDate && styles.todayHeader]}>
        <Text style={[styles.dayName, isTodayDate && styles.todayText]}>
          {dayName}
        </Text>
        <Text style={[styles.dateText, isTodayDate && styles.todayDateText]}>
          {dayMonth}
        </Text>
      </View>

      <View style={styles.slotsContainer}>
        <MealSlotCard
          slot={dejeunerSlot}
          date={dateStr}
          mealType="dejeuner"
          onPress={() => handleSlotPress('dejeuner')}
          onLongPress={() => handleSlotLongPress('dejeuner', dejeunerSlot)}
          style={styles.slotCard}
        />
        <MealSlotCard
          slot={dinerSlot}
          date={dateStr}
          mealType="diner"
          onPress={() => handleSlotPress('diner')}
          onLongPress={() => handleSlotLongPress('diner', dinerSlot)}
          style={styles.slotCard}
        />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    width: 140,
    backgroundColor: '#F9FAFB',
    borderRadius: 12,
    padding: 8,
    marginRight: 12,
  },
  todayContainer: {
    backgroundColor: '#CCFBF1',
    borderWidth: 2,
    borderColor: '#14B8A6',
  },
  header: {
    alignItems: 'center',
    marginBottom: 8,
    paddingVertical: 4,
  },
  todayHeader: {
    backgroundColor: '#14B8A6',
    borderRadius: 8,
    marginHorizontal: -4,
    paddingHorizontal: 4,
  },
  dayName: {
    fontSize: 14,
    fontWeight: '600',
    color: '#374151',
  },
  todayText: {
    color: '#FFFFFF',
  },
  dateText: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 2,
  },
  todayDateText: {
    color: '#FFFFFF',
  },
  slotsContainer: {
    gap: 8,
  },
  slotCard: {
    flex: 1,
  },
});
