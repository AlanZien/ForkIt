/**
 * Personal Recipe Detail Screen
 *
 * Displays full details of a personal recipe including
 * structured ingredients and numbered instruction steps.
 * Includes edit button for owned recipes.
 */

import { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Image,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { PersonalBadge } from '../../../components/recipe/PersonalBadge';
import { ServingsStepper } from '../../../components/recipe/ServingsStepper';
import { getPersonalRecipe } from '../../../services/personal-recipes';
import type { PersonalRecipeResponse } from '../../../types/personal-recipe';
import { colors, spacing, borderRadius, typography } from '../../../constants/theme';

export default function PersonalRecipeDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();

  const [recipe, setRecipe] = useState<PersonalRecipeResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [portions, setPortions] = useState<number>(4);

  // Load recipe on mount
  useEffect(() => {
    if (id) {
      loadRecipe();
    }
  }, [id]);

  const loadRecipe = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await getPersonalRecipe(id!);
      setRecipe(data);
      setPortions(data.servings);
    } catch (err) {
      console.error('Load recipe failed:', err);
      setError('Impossible de charger la recette.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleBack = () => {
    router.back();
  };

  const handleEdit = () => {
    router.push(`/recipe/edit/${id}`);
  };

  // Scale ingredient quantity based on portions
  const scaleQuantity = (quantity: number): string => {
    if (!recipe) return quantity.toString();
    const scale = portions / recipe.servings;
    const scaled = quantity * scale;
    // Round to 2 decimal places and remove trailing zeros
    return parseFloat(scaled.toFixed(2)).toString();
  };

  // Loading state
  if (isLoading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={colors.primary} />
          <Text style={styles.loadingText}>Chargement de la recette...</Text>
        </View>
      </SafeAreaView>
    );
  }

  // Error state
  if (error || !recipe) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.header}>
          <TouchableOpacity onPress={handleBack} style={styles.backButton}>
            <Ionicons name="arrow-back" size={24} color={colors.foreground} />
          </TouchableOpacity>
        </View>
        <View style={styles.errorContainer}>
          <Ionicons
            name="alert-circle-outline"
            size={48}
            color={colors.destructive}
          />
          <Text style={styles.errorTitle}>Recette introuvable</Text>
          <Text style={styles.errorText}>
            {error || 'Cette recette n\'existe pas.'}
          </Text>
          <TouchableOpacity style={styles.retryButton} onPress={handleBack}>
            <Text style={styles.retryButtonText}>Retour aux recettes</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  // Format time display
  const formatTime = (minutes: number | null): string | null => {
    if (!minutes) return null;
    if (minutes < 60) return `${minutes} min`;
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return mins > 0 ? `${hours}h ${mins}min` : `${hours}h`;
  };

  const prepTime = formatTime(recipe.prep_time_minutes);
  const cookTime = formatTime(recipe.cook_time_minutes);

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <ScrollView showsVerticalScrollIndicator={false}>
        {/* Hero Image */}
        <View style={styles.heroContainer}>
          {recipe.image_url ? (
            <Image
              source={{ uri: recipe.image_url }}
              style={styles.heroImage}
              resizeMode="cover"
            />
          ) : (
            <View style={[styles.heroImage, styles.placeholderImage]}>
              <Ionicons name="restaurant-outline" size={64} color={colors.muted} />
            </View>
          )}

          {/* Back button */}
          <TouchableOpacity
            style={styles.backButtonOverlay}
            onPress={handleBack}
          >
            <Ionicons name="arrow-back" size={24} color="#FFFFFF" />
          </TouchableOpacity>

          {/* Edit button */}
          <TouchableOpacity
            style={styles.editButtonOverlay}
            onPress={handleEdit}
          >
            <Ionicons name="create-outline" size={24} color="#FFFFFF" />
          </TouchableOpacity>

          {/* Personal badge */}
          <View style={styles.badgeOverlay}>
            <PersonalBadge />
          </View>
        </View>

        {/* Content */}
        <View style={styles.content}>
          {/* Title & Meta */}
          <View style={styles.titleSection}>
            <Text style={styles.title}>{recipe.title}</Text>

            <View style={styles.metaRow}>
              {prepTime && (
                <View style={styles.metaBadge}>
                  <Ionicons name="timer-outline" size={14} color={colors.primary} />
                  <Text style={styles.metaText}>Prep: {prepTime}</Text>
                </View>
              )}
              {cookTime && (
                <View style={styles.metaBadge}>
                  <Ionicons name="flame-outline" size={14} color={colors.primary} />
                  <Text style={styles.metaText}>Cuisson: {cookTime}</Text>
                </View>
              )}
            </View>
          </View>

          {/* Tags */}
          {recipe.tags && recipe.tags.length > 0 && (
            <View style={styles.tagsContainer}>
              {recipe.tags.map((tag, index) => (
                <View key={index} style={styles.tag}>
                  <Text style={styles.tagText}>{tag}</Text>
                </View>
              ))}
            </View>
          )}

          {/* Portion Selector */}
          <View style={styles.portionSection}>
            <Text style={styles.portionLabel}>Ajuster les portions</Text>
            <ServingsStepper
              value={portions}
              onChange={setPortions}
              min={1}
              max={20}
            />
          </View>

          {/* Ingredients */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>
              Ingredients ({recipe.ingredients.length})
            </Text>
            <View style={styles.ingredientsList}>
              {recipe.ingredients.map((ingredient) => (
                <View key={ingredient.id} style={styles.ingredientItem}>
                  <View style={styles.ingredientBullet} />
                  <Text style={styles.ingredientQuantity}>
                    {scaleQuantity(ingredient.quantity)} {ingredient.unit}
                  </Text>
                  <Text style={styles.ingredientName}>{ingredient.name}</Text>
                  {ingredient.note && (
                    <Text style={styles.ingredientNote}>({ingredient.note})</Text>
                  )}
                </View>
              ))}
            </View>
          </View>

          {/* Instructions */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>
              Instructions ({recipe.steps.length} etapes)
            </Text>
            <View style={styles.stepsList}>
              {recipe.steps.map((step) => (
                <View key={step.id} style={styles.stepItem}>
                  <View style={styles.stepNumber}>
                    <Text style={styles.stepNumberText}>{step.step_number}</Text>
                  </View>
                  <Text style={styles.stepInstruction}>{step.instruction}</Text>
                </View>
              ))}
            </View>
          </View>

          {/* Source info if forked */}
          {recipe.source_recipe_id && (
            <View style={styles.sourceSection}>
              <Text style={styles.sourceText}>
                Dupliquee depuis une recette API
              </Text>
            </View>
          )}

          {/* Bottom spacing */}
          <View style={styles.bottomSpacer} />
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.card,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    gap: spacing.md,
  },
  loadingText: {
    fontSize: 16,
    color: colors.mutedForeground,
  },
  header: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
  },
  backButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.muted,
    justifyContent: 'center',
    alignItems: 'center',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: spacing['2xl'],
    gap: spacing.sm,
  },
  errorTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: colors.foreground,
  },
  errorText: {
    fontSize: 14,
    color: colors.mutedForeground,
    textAlign: 'center',
  },
  retryButton: {
    marginTop: spacing.md,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.sm,
    backgroundColor: colors.primary,
    borderRadius: borderRadius.md,
  },
  retryButtonText: {
    color: colors.primaryForeground,
    fontSize: 16,
    fontWeight: '600',
  },
  heroContainer: {
    position: 'relative',
  },
  heroImage: {
    width: '100%',
    height: 280,
    backgroundColor: colors.muted,
  },
  placeholderImage: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  backButtonOverlay: {
    position: 'absolute',
    top: spacing.md,
    left: spacing.md,
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(0, 0, 0, 0.4)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  editButtonOverlay: {
    position: 'absolute',
    top: spacing.md,
    right: spacing.md,
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
  },
  badgeOverlay: {
    position: 'absolute',
    bottom: spacing.md,
    left: spacing.md,
  },
  content: {
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.lg,
  },
  titleSection: {
    marginBottom: spacing.md,
  },
  title: {
    ...typography.h1,
    color: colors.foreground,
    marginBottom: spacing.sm,
  },
  metaRow: {
    flexDirection: 'row',
    gap: spacing.sm,
  },
  metaBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#CCFBF1',
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: borderRadius.xl,
    gap: 6,
  },
  metaText: {
    fontSize: 14,
    color: '#0D9488',
    fontWeight: '500',
  },
  tagsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
    marginBottom: spacing.lg,
  },
  tag: {
    backgroundColor: colors.muted,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: borderRadius.lg,
  },
  tagText: {
    fontSize: 12,
    color: colors.mutedForeground,
  },
  portionSection: {
    marginBottom: spacing.lg,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.md,
    backgroundColor: colors.inputBackground,
    borderRadius: borderRadius.md,
    borderWidth: 1,
    borderColor: colors.border,
  },
  portionLabel: {
    fontSize: 14,
    fontWeight: '500',
    color: colors.mutedForeground,
    marginBottom: spacing.sm,
    textAlign: 'center',
  },
  section: {
    marginBottom: spacing.lg,
  },
  sectionTitle: {
    ...typography.h3,
    color: colors.foreground,
    marginBottom: spacing.md,
  },
  ingredientsList: {
    gap: spacing.sm,
  },
  ingredientItem: {
    flexDirection: 'row',
    alignItems: 'center',
    flexWrap: 'wrap',
    gap: spacing.sm,
  },
  ingredientBullet: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: colors.primary,
  },
  ingredientQuantity: {
    fontSize: 14,
    color: colors.mutedForeground,
    minWidth: 60,
  },
  ingredientName: {
    fontSize: 16,
    color: colors.foreground,
  },
  ingredientNote: {
    fontSize: 14,
    color: colors.mutedForeground,
    fontStyle: 'italic',
  },
  stepsList: {
    gap: spacing.md,
  },
  stepItem: {
    flexDirection: 'row',
    gap: spacing.md,
  },
  stepNumber: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    flexShrink: 0,
  },
  stepNumberText: {
    fontSize: 16,
    fontWeight: '700',
    color: colors.primaryForeground,
  },
  stepInstruction: {
    flex: 1,
    fontSize: 16,
    color: colors.foreground,
    lineHeight: 24,
    paddingTop: 4,
  },
  sourceSection: {
    marginTop: spacing.lg,
    paddingVertical: spacing.md,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  sourceText: {
    fontSize: 12,
    color: colors.mutedForeground,
    fontStyle: 'italic',
    textAlign: 'center',
  },
  bottomSpacer: {
    height: 40,
  },
});
