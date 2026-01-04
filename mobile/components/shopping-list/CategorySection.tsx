/**
 * CategorySection Component
 *
 * Collapsible section for a category of shopping list items.
 * Shows category name, item count, and expandable list.
 */

import React, { useState, useRef } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Animated,
  LayoutAnimation,
  Platform,
  UIManager,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { ShoppingListItem } from './ShoppingListItem';
import type {
  ShoppingListItem as ShoppingListItemType,
  IngredientCategory,
} from '../../types/shopping-list';
import { CATEGORY_LABELS } from '../../types/shopping-list';

// Enable LayoutAnimation on Android
if (
  Platform.OS === 'android' &&
  UIManager.setLayoutAnimationEnabledExperimental
) {
  UIManager.setLayoutAnimationEnabledExperimental(true);
}

interface CategorySectionProps {
  category: IngredientCategory;
  items: ShoppingListItemType[];
  onToggleItem: (id: string) => void;
  defaultExpanded?: boolean;
}

export function CategorySection({
  category,
  items,
  onToggleItem,
  defaultExpanded = true,
}: CategorySectionProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);
  const rotateAnim = useRef(new Animated.Value(defaultExpanded ? 1 : 0)).current;

  const handleToggleExpand = () => {
    LayoutAnimation.configureNext(LayoutAnimation.Presets.easeInEaseOut);

    Animated.timing(rotateAnim, {
      toValue: isExpanded ? 0 : 1,
      duration: 200,
      useNativeDriver: true,
    }).start();

    setIsExpanded(!isExpanded);
  };

  const chevronRotation = rotateAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ['0deg', '90deg'],
  });

  const checkedCount = items.filter((item) => item.is_checked).length;
  const categoryLabel = CATEGORY_LABELS[category] || category;

  return (
    <View style={styles.container}>
      {/* Header */}
      <TouchableOpacity
        style={styles.header}
        onPress={handleToggleExpand}
        activeOpacity={0.7}
        accessibilityRole="button"
        accessibilityLabel={`${categoryLabel}, ${items.length} items, ${isExpanded ? 'collapse' : 'expand'}`}
      >
        <Animated.View
          style={[
            styles.chevronContainer,
            { transform: [{ rotate: chevronRotation }] },
          ]}
        >
          <Ionicons name="chevron-forward" size={20} color="#6B7280" />
        </Animated.View>

        <Text style={styles.categoryName}>{categoryLabel}</Text>

        <View style={styles.countContainer}>
          <Text style={styles.countText}>
            {checkedCount}/{items.length}
          </Text>
        </View>
      </TouchableOpacity>

      {/* Items */}
      {isExpanded && (
        <View style={styles.itemsContainer}>
          {items.map((item) => (
            <ShoppingListItem
              key={item.id}
              item={item}
              onToggle={onToggleItem}
            />
          ))}
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginBottom: 8,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 14,
    paddingHorizontal: 12,
    backgroundColor: '#F9FAFB',
  },
  chevronContainer: {
    marginRight: 8,
  },
  categoryName: {
    flex: 1,
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
  },
  countContainer: {
    backgroundColor: '#E5E7EB',
    borderRadius: 12,
    paddingHorizontal: 10,
    paddingVertical: 4,
  },
  countText: {
    fontSize: 13,
    fontWeight: '500',
    color: '#6B7280',
  },
  itemsContainer: {
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
  },
});
