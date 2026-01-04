/**
 * RecipeForm Component
 *
 * Complete form for creating/editing personal recipes.
 * Includes all sections: basic info, image, tags, ingredients, and instructions.
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  ScrollView,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { colors, borderRadius, spacing, typography } from '../../constants/theme';
import { Button } from '../ui/Button';
import { ServingsStepper } from './ServingsStepper';
import { TagsSelector } from './TagsSelector';
import { IngredientListInput } from './IngredientListInput';
import { InstructionStepListInput } from './InstructionStepListInput';
import { RecipeImagePicker } from './RecipeImagePicker';
import type {
  IngredientInput,
  InstructionStepInput,
  PersonalRecipeCreate,
  PersonalRecipeResponse,
} from '../../types/personal-recipe';

interface RecipeFormData {
  title: string;
  servings: number;
  prep_time_minutes: number | null;
  cook_time_minutes: number | null;
  tags: string[];
  ingredients: IngredientInput[];
  steps: InstructionStepInput[];
  // Image handling
  imageUri: string | null;
  imageFilename: string | null;
  imageMimeType: string | null;
}

interface RecipeFormProps {
  /** Initial data for editing (optional) */
  initialData?: PersonalRecipeResponse;
  /** Called when form is submitted with valid data */
  onSubmit: (data: PersonalRecipeCreate, imageFile?: { uri: string; filename: string; mimeType: string }) => void;
  /** Loading state during submission */
  isLoading?: boolean;
  /** Whether image is being uploaded */
  isUploadingImage?: boolean;
  /** Server-side validation errors */
  serverErrors?: Record<string, string>;
  /** Submit button text */
  submitButtonText?: string;
}

const createInitialFormData = (data?: PersonalRecipeResponse): RecipeFormData => {
  if (data) {
    return {
      title: data.title,
      servings: data.servings,
      prep_time_minutes: data.prep_time_minutes,
      cook_time_minutes: data.cook_time_minutes,
      tags: data.tags || [],
      ingredients: data.ingredients.map((ing) => ({
        name: ing.name,
        quantity: ing.quantity,
        unit: ing.unit,
        note: ing.note,
      })),
      steps: data.steps.map((step) => ({
        instruction: step.instruction,
      })),
      imageUri: data.image_url,
      imageFilename: null,
      imageMimeType: null,
    };
  }

  return {
    title: '',
    servings: 4,
    prep_time_minutes: null,
    cook_time_minutes: null,
    tags: [],
    ingredients: [{ name: '', quantity: 1, unit: 'g', note: null }],
    steps: [{ instruction: '' }],
    imageUri: null,
    imageFilename: null,
    imageMimeType: null,
  };
};

export function RecipeForm({
  initialData,
  onSubmit,
  isLoading = false,
  isUploadingImage = false,
  serverErrors = {},
  submitButtonText = 'Enregistrer',
}: RecipeFormProps) {
  const [formData, setFormData] = useState<RecipeFormData>(
    createInitialFormData(initialData)
  );
  const [errors, setErrors] = useState<Record<string, string>>({});

  const updateField = <K extends keyof RecipeFormData>(
    field: K,
    value: RecipeFormData[K]
  ) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    // Clear error when field is updated
    if (errors[field]) {
      setErrors((prev) => {
        const { [field]: _, ...rest } = prev;
        return rest;
      });
    }
  };

  const handleImageChange = (
    uri: string | null,
    filename: string | null,
    mimeType: string | null
  ) => {
    setFormData((prev) => ({
      ...prev,
      imageUri: uri,
      imageFilename: filename,
      imageMimeType: mimeType,
    }));
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    // Title required
    if (!formData.title.trim()) {
      newErrors.title = 'Le titre est requis';
    }

    // At least one ingredient with name
    const validIngredients = formData.ingredients.filter(
      (ing) => ing.name.trim()
    );
    if (validIngredients.length === 0) {
      newErrors.ingredients = 'Au moins un ingredient est requis';
    }

    // At least one step with instruction
    const validSteps = formData.steps.filter(
      (step) => step.instruction.trim()
    );
    if (validSteps.length === 0) {
      newErrors.steps = 'Au moins une etape est requise';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = () => {
    if (!validateForm()) return;

    // Filter out empty ingredients and steps
    const validIngredients = formData.ingredients.filter(
      (ing) => ing.name.trim()
    );
    const validSteps = formData.steps.filter(
      (step) => step.instruction.trim()
    );

    const recipeData: PersonalRecipeCreate = {
      title: formData.title.trim(),
      servings: formData.servings,
      prep_time_minutes: formData.prep_time_minutes,
      cook_time_minutes: formData.cook_time_minutes,
      tags: formData.tags.length > 0 ? formData.tags : null,
      ingredients: validIngredients,
      steps: validSteps,
    };

    // Pass image file info if new image selected (has filename)
    const imageFile = formData.imageFilename && formData.imageUri && formData.imageMimeType
      ? {
          uri: formData.imageUri,
          filename: formData.imageFilename,
          mimeType: formData.imageMimeType,
        }
      : undefined;

    onSubmit(recipeData, imageFile);
  };

  const allErrors = { ...errors, ...serverErrors };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        keyboardShouldPersistTaps="handled"
      >
        {/* Image Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Photo</Text>
          <RecipeImagePicker
            imageUrl={formData.imageUri}
            onChange={handleImageChange}
            uploading={isUploadingImage}
            disabled={isLoading}
          />
        </View>

        {/* Basic Info Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Informations de base</Text>

          <View style={styles.field}>
            <Text style={styles.label}>Titre *</Text>
            <TextInput
              testID="recipe-title"
              style={[styles.input, allErrors.title && styles.inputError]}
              value={formData.title}
              onChangeText={(text) => updateField('title', text)}
              placeholder="Ex: Tarte aux pommes maison"
              placeholderTextColor={colors.mutedForeground}
              editable={!isLoading}
            />
            {allErrors.title && (
              <Text style={styles.errorText}>{allErrors.title}</Text>
            )}
          </View>

          <View style={styles.field}>
            <Text style={styles.label}>Portions *</Text>
            <ServingsStepper
              value={formData.servings}
              onChange={(value) => updateField('servings', value)}
              disabled={isLoading}
            />
          </View>

          <View style={styles.row}>
            <View style={[styles.field, styles.halfField]}>
              <Text style={styles.label}>Temps de preparation (min)</Text>
              <TextInput
                testID="prep-time"
                style={styles.input}
                value={formData.prep_time_minutes?.toString() || ''}
                onChangeText={(text) => {
                  const num = text ? parseInt(text, 10) : null;
                  updateField('prep_time_minutes', num);
                }}
                placeholder="30"
                placeholderTextColor={colors.mutedForeground}
                keyboardType="numeric"
                editable={!isLoading}
              />
            </View>

            <View style={[styles.field, styles.halfField]}>
              <Text style={styles.label}>Temps de cuisson (min)</Text>
              <TextInput
                testID="cook-time"
                style={styles.input}
                value={formData.cook_time_minutes?.toString() || ''}
                onChangeText={(text) => {
                  const num = text ? parseInt(text, 10) : null;
                  updateField('cook_time_minutes', num);
                }}
                placeholder="45"
                placeholderTextColor={colors.mutedForeground}
                keyboardType="numeric"
                editable={!isLoading}
              />
            </View>
          </View>
        </View>

        {/* Tags Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Tags (optionnel)</Text>
          <TagsSelector
            selectedTags={formData.tags}
            onChange={(tags) => updateField('tags', tags)}
            disabled={isLoading}
          />
        </View>

        {/* Ingredients Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Ingredients *</Text>
          {allErrors.ingredients && (
            <Text style={styles.sectionError}>{allErrors.ingredients}</Text>
          )}
          <IngredientListInput
            ingredients={formData.ingredients}
            onChange={(ingredients) => updateField('ingredients', ingredients)}
            disabled={isLoading}
          />
        </View>

        {/* Instructions Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Etapes de preparation *</Text>
          {allErrors.steps && (
            <Text style={styles.sectionError}>{allErrors.steps}</Text>
          )}
          <InstructionStepListInput
            steps={formData.steps}
            onChange={(steps) => updateField('steps', steps)}
            disabled={isLoading}
          />
        </View>

        {/* Submit Button */}
        <View style={styles.submitSection}>
          <Button
            testID="submit-recipe"
            title={submitButtonText}
            onPress={handleSubmit}
            loading={isLoading}
            disabled={isLoading || isUploadingImage}
          />
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    padding: spacing.md,
    paddingBottom: spacing['2xl'],
  },
  section: {
    marginBottom: spacing.lg,
  },
  sectionTitle: {
    ...typography.h3,
    color: colors.foreground,
    marginBottom: spacing.md,
  },
  sectionError: {
    fontSize: 13,
    color: colors.destructive,
    marginBottom: spacing.sm,
  },
  field: {
    marginBottom: spacing.md,
  },
  row: {
    flexDirection: 'row',
    gap: spacing.md,
  },
  halfField: {
    flex: 1,
  },
  label: {
    ...typography.label,
    color: colors.foreground,
    marginBottom: spacing.xs,
  },
  input: {
    height: 48,
    backgroundColor: colors.inputBackground,
    borderRadius: borderRadius.md,
    paddingHorizontal: spacing.md,
    fontSize: 16,
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
  submitSection: {
    marginTop: spacing.lg,
    paddingHorizontal: spacing.md,
  },
});
