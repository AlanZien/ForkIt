/**
 * MealSlotCard Component
 *
 * Displays a meal slot in the weekly planning view.
 * Shows empty state with "+" icon or filled state with recipe info.
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  Image,
  TouchableOpacity,
  StyleSheet,
  ViewStyle,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import type { MealSlot, MealType } from '../../types/meal-slot';

interface MealSlotCardProps {
  slot: MealSlot | null;
  date: string;
  mealType: MealType;
  onPress: () => void;
  onLongPress?: () => void;
  style?: ViewStyle;
}

const MEAL_TYPE_LABELS: Record<MealType, string> = {
  dejeuner: 'Dejeuner',
  diner: 'Diner',
};

export function MealSlotCard({
  slot,
  mealType,
  onPress,
  onLongPress,
  style,
}: MealSlotCardProps) {
  const [imageError, setImageError] = useState(false);
  const isEmpty = !slot;

  if (isEmpty) {
    return (
      <TouchableOpacity
        style={[styles.container, styles.emptyContainer, style]}
        onPress={onPress}
        activeOpacity={0.7}
        accessibilityRole="button"
        accessibilityLabel={`Ajouter un repas pour ${MEAL_TYPE_LABELS[mealType]}`}
      >
        <Ionicons name="add-outline" size={24} color="#9CA3AF" />
        <Text style={styles.emptyLabel}>{MEAL_TYPE_LABELS[mealType]}</Text>
      </TouchableOpacity>
    );
  }

  const showPlaceholder = !slot.recipe_thumbnail || imageError;

  return (
    <TouchableOpacity
      style={[styles.container, styles.filledContainer, style]}
      onPress={onPress}
      onLongPress={onLongPress}
      activeOpacity={0.8}
      delayLongPress={300}
      accessibilityRole="button"
      accessibilityLabel={`${slot.recipe_name}, ${slot.portions} portions`}
    >
      {showPlaceholder ? (
        <View style={[styles.thumbnail, styles.placeholderThumbnail]}>
          <Ionicons name="restaurant-outline" size={24} color="#9CA3AF" />
        </View>
      ) : (
        <Image
          source={{ uri: slot.recipe_thumbnail! }}
          style={styles.thumbnail}
          onError={() => setImageError(true)}
        />
      )}
      <View style={styles.content}>
        <Text style={styles.recipeName} numberOfLines={2}>
          {slot.recipe_name}
        </Text>
      </View>
      <View style={styles.portionBadge}>
        <Text style={styles.portionText}>{slot.portions}</Text>
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: {
    minHeight: 72,
    borderRadius: 12,
    overflow: 'hidden',
  },
  emptyContainer: {
    borderWidth: 1,
    borderStyle: 'dashed',
    borderColor: '#D1D5DB',
    backgroundColor: '#FAFAFA',
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 12,
  },
  emptyLabel: {
    fontSize: 12,
    color: '#9CA3AF',
    marginTop: 4,
  },
  filledContainer: {
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#E5E7EB',
    flexDirection: 'row',
    alignItems: 'center',
    padding: 8,
  },
  thumbnail: {
    width: 56,
    height: 56,
    borderRadius: 8,
    backgroundColor: '#F3F4F6',
  },
  placeholderThumbnail: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  content: {
    flex: 1,
    marginLeft: 10,
    marginRight: 4,
  },
  recipeName: {
    fontSize: 13,
    fontWeight: '500',
    color: '#111827',
    lineHeight: 18,
  },
  portionBadge: {
    position: 'absolute',
    top: 4,
    right: 4,
    backgroundColor: '#14B8A6',
    borderRadius: 10,
    minWidth: 20,
    height: 20,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 6,
  },
  portionText: {
    fontSize: 11,
    fontWeight: '600',
    color: '#FFFFFF',
  },
});
