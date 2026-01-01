/**
 * ProfilePreferences Component
 *
 * Complete preferences section for the Profile screen.
 * Manages view/edit modes, displays all preference sections,
 * and handles save/cancel operations.
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ActivityIndicator,
  StyleSheet,
  Alert,
} from 'react-native';
import { Button } from '../ui';
import { ChipSelector } from './ChipSelector';
import { IngredientInput } from './IngredientInput';
import { PortionSelector } from './PortionSelector';
import { SectionCard } from './SectionCard';
import { usePreferencesStore } from '../../stores/preferences';
import {
  ALL_DIETARY_TYPES,
  ALL_ALLERGY_TYPES,
  DIETARY_LABELS,
  ALLERGY_LABELS,
  type DietaryType,
  type AllergyType,
  type UserPreferences,
} from '../../types/preferences';
import { colors, spacing } from '../../constants/theme';

export function ProfilePreferences() {
  const [isEditing, setIsEditing] = useState(false);

  // Store state
  const preferences = usePreferencesStore((state) => state.preferences);
  const localPreferences = usePreferencesStore((state) => state.localPreferences);
  const isLoading = usePreferencesStore((state) => state.isLoading);
  const error = usePreferencesStore((state) => state.error);

  // Store actions
  const fetchPreferences = usePreferencesStore((state) => state.fetchPreferences);
  const updatePreferences = usePreferencesStore((state) => state.updatePreferences);
  const setLocalPreferences = usePreferencesStore((state) => state.setLocalPreferences);
  const resetLocalChanges = usePreferencesStore((state) => state.resetLocalChanges);

  // Fetch preferences on mount
  useEffect(() => {
    fetchPreferences();
  }, [fetchPreferences]);

  // Check for Halal + Kosher warning
  const hasHalalKosherWarning =
    localPreferences?.dietary_preferences.includes('halal') &&
    localPreferences?.dietary_preferences.includes('kosher');

  // Handle entering edit mode
  const handleEdit = () => {
    setIsEditing(true);
  };

  // Handle cancel
  const handleCancel = () => {
    resetLocalChanges();
    setIsEditing(false);
  };

  // Handle save
  const handleSave = async () => {
    if (!localPreferences) return;

    try {
      await updatePreferences(localPreferences);
      setIsEditing(false);
      // Show success toast/alert
      Alert.alert('Succes', 'Preferences enregistrees avec succes');
    } catch {
      // Error is handled by store
    }
  };

  // Update handlers for each section
  const handleDietaryChange = (values: DietaryType[]) => {
    if (!localPreferences) return;
    setLocalPreferences({
      ...localPreferences,
      dietary_preferences: values,
    });
  };

  const handleAllergiesChange = (values: AllergyType[]) => {
    if (!localPreferences) return;
    setLocalPreferences({
      ...localPreferences,
      allergies: values,
    });
  };

  const handleExcludedAdd = (ingredient: string) => {
    if (!localPreferences) return;
    if (localPreferences.excluded_ingredients.includes(ingredient)) return;
    setLocalPreferences({
      ...localPreferences,
      excluded_ingredients: [...localPreferences.excluded_ingredients, ingredient],
    });
  };

  const handleExcludedRemove = (ingredient: string) => {
    if (!localPreferences) return;
    setLocalPreferences({
      ...localPreferences,
      excluded_ingredients: localPreferences.excluded_ingredients.filter(
        (i) => i !== ingredient
      ),
    });
  };

  const handlePreferredAdd = (ingredient: string) => {
    if (!localPreferences) return;
    if (localPreferences.preferred_ingredients.includes(ingredient)) return;
    setLocalPreferences({
      ...localPreferences,
      preferred_ingredients: [...localPreferences.preferred_ingredients, ingredient],
    });
  };

  const handlePreferredRemove = (ingredient: string) => {
    if (!localPreferences) return;
    setLocalPreferences({
      ...localPreferences,
      preferred_ingredients: localPreferences.preferred_ingredients.filter(
        (i) => i !== ingredient
      ),
    });
  };

  const handlePortionsChange = (value: number) => {
    if (!localPreferences) return;
    setLocalPreferences({
      ...localPreferences,
      portions_count: value,
    });
  };

  // Loading state
  if (isLoading && !localPreferences) {
    return (
      <View style={styles.centerContainer} testID="loading-indicator">
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingText}>Chargement des preferences...</Text>
      </View>
    );
  }

  // Error state
  if (error && !localPreferences) {
    return (
      <View style={styles.centerContainer}>
        <Text style={styles.errorText}>{error}</Text>
        <Button
          testID="retry-button"
          title="Reessayer"
          onPress={fetchPreferences}
          style={styles.retryButton}
        />
      </View>
    );
  }

  // No preferences loaded yet
  if (!localPreferences) {
    return null;
  }

  // Render preferences display (static text for view mode)
  const renderStaticChips = (values: string[], labels: Record<string, string>) => {
    if (values.length === 0) {
      return <Text style={styles.emptyText}>Aucun</Text>;
    }
    return (
      <View style={styles.staticChipsContainer}>
        {values.map((value) => (
          <View key={value} style={styles.staticChip}>
            <Text style={styles.staticChipText}>{labels[value] || value}</Text>
          </View>
        ))}
      </View>
    );
  };

  const renderStaticIngredients = (values: string[]) => {
    if (values.length === 0) {
      return <Text style={styles.emptyText}>Aucun</Text>;
    }
    return (
      <View style={styles.staticChipsContainer}>
        {values.map((value) => (
          <View key={value} style={styles.staticChip}>
            <Text style={styles.staticChipText}>{value}</Text>
          </View>
        ))}
      </View>
    );
  };

  return (
    <View style={styles.container}>
      {/* Header with action buttons */}
      <View style={styles.header}>
        <Text style={styles.sectionTitle}>Mes preferences</Text>
        {!isEditing ? (
          <Button
            title="Modifier"
            variant="secondary"
            onPress={handleEdit}
            style={styles.headerButton}
          />
        ) : (
          <View style={styles.headerButtons}>
            <Button
              testID="cancel-button"
              title="Annuler"
              variant="link"
              onPress={handleCancel}
            />
            <Button
              testID="save-button"
              title="Enregistrer"
              onPress={handleSave}
              loading={isLoading}
              style={styles.saveButton}
            />
          </View>
        )}
      </View>

      {/* Error display in edit mode */}
      {error && (
        <View style={styles.errorBanner}>
          <Text style={styles.errorBannerText}>{error}</Text>
          <Button
            testID="retry-button"
            title="Reessayer"
            variant="link"
            onPress={fetchPreferences}
          />
        </View>
      )}

      {/* Halal + Kosher warning */}
      {hasHalalKosherWarning && (
        <View style={styles.warningBanner} testID="halal-kosher-warning">
          <Text style={styles.warningText}>
            Attention : Halal et Casher sont tous deux selectionnes.
            Verifiez la coherence de cette combinaison.
          </Text>
        </View>
      )}

      <View style={styles.scrollContainer}>
        {/* Dietary Preferences Section */}
        <SectionCard title="Regimes alimentaires" editable={isEditing}>
          {isEditing ? (
            <ChipSelector
              options={ALL_DIETARY_TYPES}
              labels={DIETARY_LABELS}
              selectedValues={localPreferences.dietary_preferences}
              onSelect={handleDietaryChange}
            />
          ) : (
            renderStaticChips(localPreferences.dietary_preferences, DIETARY_LABELS)
          )}
        </SectionCard>

        {/* Allergies Section */}
        <SectionCard title="Allergies" editable={isEditing}>
          {isEditing ? (
            <ChipSelector
              options={ALL_ALLERGY_TYPES}
              labels={ALLERGY_LABELS}
              selectedValues={localPreferences.allergies}
              onSelect={handleAllergiesChange}
            />
          ) : (
            renderStaticChips(localPreferences.allergies, ALLERGY_LABELS)
          )}
        </SectionCard>

        {/* Excluded Ingredients Section */}
        <SectionCard title="Ingredients exclus" editable={isEditing}>
          {isEditing ? (
            <IngredientInput
              value={localPreferences.excluded_ingredients}
              onAdd={handleExcludedAdd}
              onRemove={handleExcludedRemove}
              maxItems={30}
              placeholder="Ajouter un ingredient a exclure"
            />
          ) : (
            renderStaticIngredients(localPreferences.excluded_ingredients)
          )}
        </SectionCard>

        {/* Preferred Ingredients Section */}
        <SectionCard title="Ingredients preferes" editable={isEditing}>
          {isEditing ? (
            <IngredientInput
              value={localPreferences.preferred_ingredients}
              onAdd={handlePreferredAdd}
              onRemove={handlePreferredRemove}
              maxItems={30}
              placeholder="Ajouter un ingredient prefere"
            />
          ) : (
            renderStaticIngredients(localPreferences.preferred_ingredients)
          )}
        </SectionCard>

        {/* Portions Section */}
        <SectionCard title="Nombre de portions" editable={isEditing}>
          {isEditing ? (
            <PortionSelector
              value={localPreferences.portions_count}
              onChange={handlePortionsChange}
              min={1}
              max={12}
            />
          ) : (
            <Text style={styles.portionValue}>{localPreferences.portions_count}</Text>
          )}
        </SectionCard>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: spacing.lg,
  },
  loadingText: {
    marginTop: spacing.md,
    fontSize: 16,
    color: colors.mutedForeground,
  },
  errorText: {
    fontSize: 16,
    color: colors.destructive,
    textAlign: 'center',
    marginBottom: spacing.md,
  },
  retryButton: {
    marginTop: spacing.md,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.lg,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: colors.foreground,
  },
  headerButton: {
    paddingHorizontal: spacing.md,
  },
  headerButtons: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
  },
  saveButton: {
    paddingHorizontal: spacing.md,
  },
  errorBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#FEE2E2',
    borderRadius: 12,
    padding: spacing.md,
    marginBottom: spacing.md,
  },
  errorBannerText: {
    flex: 1,
    fontSize: 14,
    color: colors.destructive,
  },
  warningBanner: {
    backgroundColor: colors.accent,
    borderRadius: 12,
    padding: spacing.md,
    marginBottom: spacing.md,
  },
  warningText: {
    fontSize: 14,
    color: colors.accentForeground,
    lineHeight: 20,
  },
  scrollContainer: {
    flex: 1,
  },
  staticChipsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
  },
  staticChip: {
    backgroundColor: colors.muted,
    borderRadius: 20,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
  },
  staticChipText: {
    fontSize: 14,
    color: colors.foreground,
  },
  emptyText: {
    fontSize: 14,
    color: colors.mutedForeground,
    fontStyle: 'italic',
  },
  portionValue: {
    fontSize: 20,
    fontWeight: '600',
    color: colors.foreground,
  },
});
