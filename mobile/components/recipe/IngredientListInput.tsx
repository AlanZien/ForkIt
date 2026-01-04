/**
 * IngredientListInput Component
 *
 * Dynamic list of ingredient inputs with add/remove functionality.
 * Each ingredient has: name, quantity, unit, and optional note.
 */

import React from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
} from 'react-native';
import { Picker } from '@react-native-picker/picker';
import { colors, borderRadius, spacing } from '../../constants/theme';
import { UNIT_OPTIONS, type IngredientInput } from '../../types/personal-recipe';

interface IngredientListInputProps {
  /** Current ingredients list */
  ingredients: IngredientInput[];
  /** Callback when ingredients change */
  onChange: (ingredients: IngredientInput[]) => void;
  /** Validation errors by index */
  errors?: Record<number, string>;
  /** Whether the input is disabled */
  disabled?: boolean;
}

const createEmptyIngredient = (): IngredientInput => ({
  name: '',
  quantity: 1,
  unit: 'g',
  note: null,
});

export function IngredientListInput({
  ingredients,
  onChange,
  errors = {},
  disabled = false,
}: IngredientListInputProps) {
  const updateIngredient = (index: number, field: keyof IngredientInput, value: string | number | null) => {
    const updated = [...ingredients];
    updated[index] = { ...updated[index], [field]: value };
    onChange(updated);
  };

  const addIngredient = () => {
    onChange([...ingredients, createEmptyIngredient()]);
  };

  const removeIngredient = (index: number) => {
    if (ingredients.length <= 1) return; // Keep at least one
    const updated = ingredients.filter((_, i) => i !== index);
    onChange(updated);
  };

  return (
    <View style={styles.container}>
      {ingredients.map((ingredient, index) => (
        <View key={index} style={styles.ingredientRow}>
          <View style={styles.rowHeader}>
            <Text style={styles.ingredientNumber}>{index + 1}</Text>
            {ingredients.length > 1 && (
              <TouchableOpacity
                testID={`remove-ingredient-${index}`}
                onPress={() => removeIngredient(index)}
                disabled={disabled}
                style={styles.removeButton}
                accessibilityLabel="Supprimer cet ingredient"
              >
                <Text style={styles.removeButtonText}>x</Text>
              </TouchableOpacity>
            )}
          </View>

          <View style={styles.fieldsContainer}>
            {/* Name input */}
            <TextInput
              testID={`ingredient-name-${index}`}
              style={[
                styles.input,
                styles.nameInput,
                errors[index] && styles.inputError,
              ]}
              value={ingredient.name}
              onChangeText={(text) => updateIngredient(index, 'name', text)}
              placeholder="Ingredient"
              placeholderTextColor={colors.mutedForeground}
              editable={!disabled}
            />

            {/* Quantity input */}
            <TextInput
              testID={`ingredient-quantity-${index}`}
              style={[styles.input, styles.quantityInput]}
              value={ingredient.quantity.toString()}
              onChangeText={(text) => {
                const num = parseFloat(text) || 0;
                updateIngredient(index, 'quantity', num);
              }}
              placeholder="Qte"
              placeholderTextColor={colors.mutedForeground}
              keyboardType="numeric"
              editable={!disabled}
            />

            {/* Unit picker */}
            <View style={styles.pickerContainer}>
              <Picker
                testID={`ingredient-unit-${index}`}
                selectedValue={ingredient.unit}
                onValueChange={(value) => updateIngredient(index, 'unit', value)}
                enabled={!disabled}
                style={styles.picker}
              >
                {UNIT_OPTIONS.map((option) => (
                  <Picker.Item
                    key={option.value}
                    label={option.label}
                    value={option.value}
                  />
                ))}
              </Picker>
            </View>
          </View>

          {/* Note input (optional) */}
          <TextInput
            testID={`ingredient-note-${index}`}
            style={[styles.input, styles.noteInput]}
            value={ingredient.note || ''}
            onChangeText={(text) => updateIngredient(index, 'note', text || null)}
            placeholder="Note (optionnel)"
            placeholderTextColor={colors.mutedForeground}
            editable={!disabled}
          />

          {errors[index] && (
            <Text style={styles.errorText}>{errors[index]}</Text>
          )}
        </View>
      ))}

      <TouchableOpacity
        testID="add-ingredient"
        style={styles.addButton}
        onPress={addIngredient}
        disabled={disabled}
        accessibilityRole="button"
        accessibilityLabel="Ajouter un ingredient"
      >
        <Text style={styles.addButtonText}>+ Ajouter un ingredient</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    gap: spacing.md,
  },
  ingredientRow: {
    backgroundColor: colors.card,
    borderRadius: borderRadius.md,
    padding: spacing.md,
    borderWidth: 1,
    borderColor: colors.border,
  },
  rowHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  ingredientNumber: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.mutedForeground,
  },
  removeButton: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: colors.destructive,
    justifyContent: 'center',
    alignItems: 'center',
  },
  removeButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.destructiveForeground,
  },
  fieldsContainer: {
    flexDirection: 'row',
    gap: spacing.sm,
    marginBottom: spacing.sm,
  },
  input: {
    height: 44,
    backgroundColor: colors.inputBackground,
    borderRadius: borderRadius.sm,
    paddingHorizontal: spacing.md,
    fontSize: 15,
    color: colors.foreground,
    borderWidth: 1,
    borderColor: colors.border,
  },
  inputError: {
    borderColor: colors.destructive,
  },
  nameInput: {
    flex: 2,
  },
  quantityInput: {
    width: 60,
    textAlign: 'center',
  },
  pickerContainer: {
    width: 100,
    height: 44,
    backgroundColor: colors.inputBackground,
    borderRadius: borderRadius.sm,
    borderWidth: 1,
    borderColor: colors.border,
    justifyContent: 'center',
    overflow: 'hidden',
  },
  picker: {
    height: 44,
    marginTop: -8,
  },
  noteInput: {
    height: 40,
    fontSize: 14,
  },
  errorText: {
    fontSize: 12,
    color: colors.destructive,
    marginTop: spacing.xs,
  },
  addButton: {
    height: 48,
    borderRadius: borderRadius.md,
    borderWidth: 2,
    borderStyle: 'dashed',
    borderColor: colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.background,
  },
  addButtonText: {
    fontSize: 15,
    fontWeight: '600',
    color: colors.primary,
  },
});
