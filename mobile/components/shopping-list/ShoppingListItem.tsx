/**
 * ShoppingListItem Component
 *
 * Displays a single shopping list item with checkbox, name, and quantity.
 * Supports checked/unchecked states with visual feedback.
 */

import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import type { ShoppingListItem as ShoppingListItemType } from '../../types/shopping-list';

interface ShoppingListItemProps {
  item: ShoppingListItemType;
  onToggle: (id: string) => void;
}

export function ShoppingListItem({ item, onToggle }: ShoppingListItemProps) {
  const handlePress = () => {
    onToggle(item.id);
  };

  return (
    <TouchableOpacity
      style={styles.container}
      onPress={handlePress}
      activeOpacity={0.7}
      accessibilityRole="checkbox"
      accessibilityState={{ checked: item.is_checked }}
      accessibilityLabel={`${item.ingredient_name}, ${item.quantity}`}
    >
      {/* Checkbox */}
      <View
        style={[
          styles.checkbox,
          item.is_checked && styles.checkboxChecked,
        ]}
      >
        {item.is_checked && (
          <Ionicons name="checkmark" size={14} color="#FFFFFF" />
        )}
      </View>

      {/* Ingredient name */}
      <Text
        style={[
          styles.ingredientName,
          item.is_checked && styles.textChecked,
        ]}
        numberOfLines={1}
      >
        {item.ingredient_name}
      </Text>

      {/* Quantity */}
      <Text
        style={[
          styles.quantity,
          item.is_checked && styles.textChecked,
        ]}
        numberOfLines={1}
      >
        {item.quantity}
      </Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 16,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6',
  },
  checkbox: {
    width: 22,
    height: 22,
    borderRadius: 6,
    borderWidth: 2,
    borderColor: '#D1D5DB',
    backgroundColor: '#FFFFFF',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  checkboxChecked: {
    backgroundColor: '#14B8A6',
    borderColor: '#14B8A6',
  },
  ingredientName: {
    flex: 1,
    fontSize: 16,
    color: '#1F2937',
    marginRight: 8,
  },
  quantity: {
    fontSize: 14,
    color: '#6B7280',
    minWidth: 60,
    textAlign: 'right',
  },
  textChecked: {
    color: '#9CA3AF',
    textDecorationLine: 'line-through',
  },
});
