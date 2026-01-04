/**
 * InstructionStepListInput Component
 *
 * Dynamic list of instruction step inputs with add/remove functionality.
 * Steps are automatically numbered (1, 2, 3...).
 */

import React from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
} from 'react-native';
import { colors, borderRadius, spacing } from '../../constants/theme';
import type { InstructionStepInput } from '../../types/personal-recipe';

interface InstructionStepListInputProps {
  /** Current steps list */
  steps: InstructionStepInput[];
  /** Callback when steps change */
  onChange: (steps: InstructionStepInput[]) => void;
  /** Validation errors by index */
  errors?: Record<number, string>;
  /** Whether the input is disabled */
  disabled?: boolean;
}

const createEmptyStep = (): InstructionStepInput => ({
  instruction: '',
});

export function InstructionStepListInput({
  steps,
  onChange,
  errors = {},
  disabled = false,
}: InstructionStepListInputProps) {
  const updateStep = (index: number, instruction: string) => {
    const updated = [...steps];
    updated[index] = { instruction };
    onChange(updated);
  };

  const addStep = () => {
    onChange([...steps, createEmptyStep()]);
  };

  const removeStep = (index: number) => {
    if (steps.length <= 1) return; // Keep at least one
    const updated = steps.filter((_, i) => i !== index);
    onChange(updated);
  };

  return (
    <View style={styles.container}>
      {steps.map((step, index) => (
        <View key={index} style={styles.stepRow}>
          <View style={styles.stepHeader}>
            <View style={styles.stepNumber}>
              <Text style={styles.stepNumberText}>{index + 1}</Text>
            </View>

            {steps.length > 1 && (
              <TouchableOpacity
                testID={`remove-step-${index}`}
                onPress={() => removeStep(index)}
                disabled={disabled}
                style={styles.removeButton}
                accessibilityLabel="Supprimer cette etape"
              >
                <Text style={styles.removeButtonText}>x</Text>
              </TouchableOpacity>
            )}
          </View>

          <TextInput
            testID={`step-instruction-${index}`}
            style={[
              styles.input,
              errors[index] && styles.inputError,
            ]}
            value={step.instruction}
            onChangeText={(text) => updateStep(index, text)}
            placeholder={`Decrivez l'etape ${index + 1}...`}
            placeholderTextColor={colors.mutedForeground}
            multiline
            numberOfLines={3}
            textAlignVertical="top"
            editable={!disabled}
          />

          {errors[index] && (
            <Text style={styles.errorText}>{errors[index]}</Text>
          )}
        </View>
      ))}

      <TouchableOpacity
        testID="add-step"
        style={styles.addButton}
        onPress={addStep}
        disabled={disabled}
        accessibilityRole="button"
        accessibilityLabel="Ajouter une etape"
      >
        <Text style={styles.addButtonText}>+ Ajouter une etape</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    gap: spacing.md,
  },
  stepRow: {
    backgroundColor: colors.card,
    borderRadius: borderRadius.md,
    padding: spacing.md,
    borderWidth: 1,
    borderColor: colors.border,
  },
  stepHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  stepNumber: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
  },
  stepNumberText: {
    fontSize: 16,
    fontWeight: '700',
    color: colors.primaryForeground,
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
  input: {
    minHeight: 80,
    backgroundColor: colors.inputBackground,
    borderRadius: borderRadius.sm,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.md,
    fontSize: 15,
    color: colors.foreground,
    borderWidth: 1,
    borderColor: colors.border,
  },
  inputError: {
    borderColor: colors.destructive,
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
