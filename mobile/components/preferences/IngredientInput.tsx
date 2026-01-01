/**
 * IngredientInput Component
 *
 * Tag input for managing ingredient lists (excluded/preferred).
 * Supports add, remove, and max limit validation.
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ViewStyle,
} from 'react-native';
import { colors, borderRadius, spacing } from '../../constants/theme';

interface IngredientInputProps {
  /** Current list of ingredients */
  value: string[];
  /** Callback when ingredient is added */
  onAdd: (ingredient: string) => void;
  /** Callback when ingredient is removed */
  onRemove: (ingredient: string) => void;
  /** Maximum number of ingredients allowed */
  maxItems?: number;
  /** Placeholder text for input */
  placeholder?: string;
  /** Whether the input is disabled */
  disabled?: boolean;
  /** Container style override */
  style?: ViewStyle;
}

export function IngredientInput({
  value,
  onAdd,
  onRemove,
  maxItems = 30,
  placeholder = 'Ajouter un ingredient',
  disabled = false,
  style,
}: IngredientInputProps) {
  const [inputValue, setInputValue] = useState('');

  const isMaxReached = value.length >= maxItems;

  const handleAdd = () => {
    if (disabled) return;

    const trimmed = inputValue.trim();
    if (!trimmed) return;
    if (isMaxReached) return;

    onAdd(trimmed);
    setInputValue('');
  };

  const handleRemove = (ingredient: string) => {
    if (disabled) return;
    onRemove(ingredient);
  };

  return (
    <View style={[styles.container, style]}>
      {/* Input row */}
      <View style={styles.inputRow}>
        <TextInput
          style={[styles.input, disabled && styles.inputDisabled]}
          value={inputValue}
          onChangeText={setInputValue}
          placeholder={placeholder}
          placeholderTextColor={colors.mutedForeground}
          editable={!disabled && !isMaxReached}
          onSubmitEditing={handleAdd}
          returnKeyType="done"
        />
        <TouchableOpacity
          testID="add-button"
          style={[
            styles.addButton,
            (disabled || isMaxReached || !inputValue.trim()) &&
              styles.addButtonDisabled,
          ]}
          onPress={handleAdd}
          disabled={disabled || isMaxReached || !inputValue.trim()}
          accessibilityRole="button"
          accessibilityLabel="Ajouter"
          accessibilityState={{
            disabled: disabled || isMaxReached || !inputValue.trim(),
          }}
        >
          <Text style={styles.addButtonText}>+</Text>
        </TouchableOpacity>
      </View>

      {/* Error message when max reached */}
      {isMaxReached && (
        <Text style={styles.errorText}>
          Maximum {maxItems} ingredients atteint
        </Text>
      )}

      {/* Tags list */}
      {value.length > 0 && (
        <View style={styles.tagsContainer}>
          {value.map((ingredient) => (
            <View key={ingredient} style={styles.tag}>
              <Text style={styles.tagText}>{ingredient}</Text>
              <TouchableOpacity
                testID={`remove-${ingredient}`}
                onPress={() => handleRemove(ingredient)}
                disabled={disabled}
                style={styles.removeButton}
                accessibilityRole="button"
                accessibilityLabel={`Supprimer ${ingredient}`}
              >
                <Text style={styles.removeButtonText}>x</Text>
              </TouchableOpacity>
            </View>
          ))}
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    gap: spacing.sm,
  },
  inputRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
  },
  input: {
    flex: 1,
    height: 48,
    backgroundColor: colors.inputBackground,
    borderRadius: borderRadius.md,
    paddingHorizontal: spacing.md,
    fontSize: 16,
    color: colors.foreground,
    borderWidth: 1,
    borderColor: colors.border,
  },
  inputDisabled: {
    opacity: 0.5,
  },
  addButton: {
    width: 48,
    height: 48,
    borderRadius: borderRadius.md,
    backgroundColor: colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
  },
  addButtonDisabled: {
    backgroundColor: colors.muted,
    opacity: 0.5,
  },
  addButtonText: {
    fontSize: 24,
    fontWeight: '600',
    color: colors.primaryForeground,
  },
  errorText: {
    fontSize: 12,
    color: colors.destructive,
  },
  tagsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
    marginTop: spacing.xs,
  },
  tag: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.muted,
    borderRadius: borderRadius.xl,
    paddingLeft: spacing.sm + 4,
    paddingRight: spacing.xs,
    paddingVertical: spacing.xs,
    gap: spacing.xs,
  },
  tagText: {
    fontSize: 14,
    color: colors.foreground,
  },
  removeButton: {
    width: 20,
    height: 20,
    borderRadius: 10,
    backgroundColor: colors.mutedForeground,
    justifyContent: 'center',
    alignItems: 'center',
  },
  removeButtonText: {
    fontSize: 12,
    fontWeight: '600',
    color: colors.card,
  },
});
