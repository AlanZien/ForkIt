/**
 * Recipe Detail Screen
 *
 * Displays full recipe details including ingredients and instructions.
 * Accessed via dynamic route /recipe/[id]
 */

import { useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Image,
  TouchableOpacity,
  ActivityIndicator,
  Linking,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useRecipesStore } from '../../stores/recipes';

export default function RecipeDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();

  const {
    selectedRecipe,
    isDetailsLoading,
    error,
    fetchRecipeDetails,
    clearSelectedRecipe,
  } = useRecipesStore();

  // Fetch recipe details on mount
  useEffect(() => {
    if (id) {
      fetchRecipeDetails(id);
    }

    return () => {
      clearSelectedRecipe();
    };
  }, [id, fetchRecipeDetails, clearSelectedRecipe]);

  // Handle back navigation
  const handleBack = () => {
    router.back();
  };

  // Open YouTube video
  const handleOpenYoutube = () => {
    if (selectedRecipe?.youtube) {
      Linking.openURL(selectedRecipe.youtube);
    }
  };

  // Open source URL
  const handleOpenSource = () => {
    if (selectedRecipe?.source) {
      Linking.openURL(selectedRecipe.source);
    }
  };

  // Loading state
  if (isDetailsLoading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#14B8A6" />
          <Text style={styles.loadingText}>Chargement de la recette...</Text>
        </View>
      </SafeAreaView>
    );
  }

  // Error state
  if (error || !selectedRecipe) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.header}>
          <TouchableOpacity onPress={handleBack} style={styles.backButton}>
            <Ionicons name="arrow-back" size={24} color="#111827" />
          </TouchableOpacity>
        </View>
        <View style={styles.errorContainer}>
          <Ionicons name="alert-circle-outline" size={48} color="#DC2626" />
          <Text style={styles.errorTitle}>Recette introuvable</Text>
          <Text style={styles.errorText}>{error || 'Cette recette n\'existe pas'}</Text>
          <TouchableOpacity style={styles.retryButton} onPress={handleBack}>
            <Text style={styles.retryButtonText}>Retour aux recettes</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  // Parse tags
  const tags = selectedRecipe.tags?.split(',').filter(Boolean) || [];

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <ScrollView showsVerticalScrollIndicator={false}>
        {/* Hero Image */}
        <View style={styles.heroContainer}>
          <Image
            source={{ uri: selectedRecipe.thumbnail || undefined }}
            style={styles.heroImage}
          />
          <TouchableOpacity
            style={styles.backButtonOverlay}
            onPress={handleBack}
          >
            <Ionicons name="arrow-back" size={24} color="#FFFFFF" />
          </TouchableOpacity>
        </View>

        {/* Content */}
        <View style={styles.content}>
          {/* Title & Meta */}
          <View style={styles.titleSection}>
            <Text style={styles.title}>{selectedRecipe.name}</Text>
            <View style={styles.metaRow}>
              {selectedRecipe.category && (
                <View style={styles.metaBadge}>
                  <Ionicons name="restaurant-outline" size={14} color="#14B8A6" />
                  <Text style={styles.metaText}>{selectedRecipe.category}</Text>
                </View>
              )}
              {selectedRecipe.area && (
                <View style={styles.metaBadge}>
                  <Ionicons name="globe-outline" size={14} color="#14B8A6" />
                  <Text style={styles.metaText}>{selectedRecipe.area}</Text>
                </View>
              )}
            </View>
          </View>

          {/* Tags */}
          {tags.length > 0 && (
            <View style={styles.tagsContainer}>
              {tags.map((tag, index) => (
                <View key={index} style={styles.tag}>
                  <Text style={styles.tagText}>{tag.trim()}</Text>
                </View>
              ))}
            </View>
          )}

          {/* Quick Actions */}
          <View style={styles.actionsRow}>
            {selectedRecipe.youtube && (
              <TouchableOpacity
                style={styles.actionButton}
                onPress={handleOpenYoutube}
              >
                <Ionicons name="logo-youtube" size={20} color="#DC2626" />
                <Text style={styles.actionText}>Vidéo</Text>
              </TouchableOpacity>
            )}
            {selectedRecipe.source && (
              <TouchableOpacity
                style={styles.actionButton}
                onPress={handleOpenSource}
              >
                <Ionicons name="link-outline" size={20} color="#14B8A6" />
                <Text style={styles.actionText}>Source</Text>
              </TouchableOpacity>
            )}
          </View>

          {/* Ingredients */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Ingrédients</Text>
            <View style={styles.ingredientsList}>
              {selectedRecipe.ingredients.map((ingredient, index) => (
                <View key={index} style={styles.ingredientItem}>
                  <View style={styles.ingredientBullet} />
                  <Text style={styles.ingredientMeasure}>
                    {ingredient.measure}
                  </Text>
                  <Text style={styles.ingredientName}>{ingredient.name}</Text>
                </View>
              ))}
            </View>
          </View>

          {/* Instructions */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Instructions</Text>
            <Text style={styles.instructions}>
              {selectedRecipe.instructions}
            </Text>
          </View>

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
    backgroundColor: '#FFFFFF',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    gap: 16,
  },
  loadingText: {
    fontSize: 16,
    color: '#6B7280',
  },
  header: {
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  backButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#F3F4F6',
    justifyContent: 'center',
    alignItems: 'center',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 48,
    gap: 12,
  },
  errorTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#111827',
  },
  errorText: {
    fontSize: 14,
    color: '#6B7280',
    textAlign: 'center',
  },
  retryButton: {
    marginTop: 16,
    paddingHorizontal: 24,
    paddingVertical: 12,
    backgroundColor: '#14B8A6',
    borderRadius: 12,
  },
  retryButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  heroContainer: {
    position: 'relative',
  },
  heroImage: {
    width: '100%',
    height: 280,
    backgroundColor: '#F3F4F6',
  },
  backButtonOverlay: {
    position: 'absolute',
    top: 16,
    left: 16,
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(0, 0, 0, 0.4)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  content: {
    paddingHorizontal: 24,
    paddingTop: 24,
  },
  titleSection: {
    marginBottom: 16,
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    color: '#111827',
    marginBottom: 12,
  },
  metaRow: {
    flexDirection: 'row',
    gap: 12,
  },
  metaBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#CCFBF1',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
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
    gap: 8,
    marginBottom: 20,
  },
  tag: {
    backgroundColor: '#F3F4F6',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  tagText: {
    fontSize: 12,
    color: '#6B7280',
  },
  actionsRow: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 24,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F9FAFB',
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 12,
    gap: 8,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  actionText: {
    fontSize: 14,
    color: '#374151',
    fontWeight: '500',
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 16,
  },
  ingredientsList: {
    gap: 12,
  },
  ingredientItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  ingredientBullet: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#14B8A6',
  },
  ingredientMeasure: {
    fontSize: 14,
    color: '#6B7280',
    minWidth: 80,
  },
  ingredientName: {
    flex: 1,
    fontSize: 16,
    color: '#111827',
  },
  instructions: {
    fontSize: 16,
    color: '#374151',
    lineHeight: 26,
  },
  bottomSpacer: {
    height: 40,
  },
});
