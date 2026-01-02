/**
 * Recipes Screen
 *
 * Recipe catalog with search and category filtering.
 * Displays recipe cards that navigate to detail view.
 */

import { useEffect, useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  FlatList,
  Image,
  TouchableOpacity,
  ActivityIndicator,
  ScrollView,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useRecipesStore } from '../../stores/recipes';
import type { RecipeSummary, Category } from '../../types/recipe';

export default function RecipesScreen() {
  const router = useRouter();
  const [searchText, setSearchText] = useState('');

  const {
    recipes,
    categories,
    searchQuery,
    selectedCategory,
    isLoading,
    isCategoriesLoading,
    error,
    fetchCategories,
    searchRecipes,
    fetchRecipesByCategory,
    clearSearch,
  } = useRecipesStore();

  // Load categories on mount
  useEffect(() => {
    if (categories.length === 0) {
      fetchCategories();
    }
  }, [categories.length, fetchCategories]);

  // Select first category by default when categories are loaded
  useEffect(() => {
    if (categories.length > 0 && !selectedCategory && !searchQuery) {
      fetchRecipesByCategory(categories[0].name);
    }
  }, [categories, selectedCategory, searchQuery, fetchRecipesByCategory]);

  // Handle search with debounce
  const handleSearch = useCallback(() => {
    if (searchText.trim().length >= 2) {
      searchRecipes(searchText.trim());
    }
  }, [searchText, searchRecipes]);

  // Handle category selection
  const handleCategoryPress = useCallback(
    (category: Category) => {
      if (selectedCategory === category.name) {
        clearSearch();
      } else {
        fetchRecipesByCategory(category.name);
      }
    },
    [selectedCategory, fetchRecipesByCategory, clearSearch]
  );

  // Handle recipe press
  const handleRecipePress = useCallback(
    (recipe: RecipeSummary) => {
      router.push(`/recipe/${recipe.id}`);
    },
    [router]
  );

  // Clear search
  const handleClearSearch = useCallback(() => {
    setSearchText('');
    clearSearch();
  }, [clearSearch]);

  // Render category chip
  const renderCategory = ({ item }: { item: Category }) => (
    <TouchableOpacity
      style={[
        styles.categoryChip,
        selectedCategory === item.name && styles.categoryChipSelected,
      ]}
      onPress={() => handleCategoryPress(item)}
      activeOpacity={0.7}
    >
      <Image source={{ uri: item.thumbnail }} style={styles.categoryImage} />
      <Text
        style={[
          styles.categoryText,
          selectedCategory === item.name && styles.categoryTextSelected,
        ]}
        numberOfLines={1}
      >
        {item.name}
      </Text>
    </TouchableOpacity>
  );

  // Render recipe card
  const renderRecipe = ({ item }: { item: RecipeSummary }) => (
    <TouchableOpacity
      style={styles.recipeCard}
      onPress={() => handleRecipePress(item)}
      activeOpacity={0.8}
    >
      <Image source={{ uri: item.thumbnail }} style={styles.recipeImage} />
      <View style={styles.recipeInfo}>
        <Text style={styles.recipeName} numberOfLines={2}>
          {item.name}
        </Text>
      </View>
    </TouchableOpacity>
  );

  // Empty state
  const renderEmpty = () => {
    if (isLoading) return null;

    if (searchQuery || selectedCategory) {
      return (
        <View style={styles.emptyState}>
          <Ionicons name="search-outline" size={48} color="#9CA3AF" />
          <Text style={styles.emptyTitle}>Aucune recette trouvée</Text>
          <Text style={styles.emptySubtitle}>
            Essayez une autre recherche ou catégorie
          </Text>
        </View>
      );
    }

    return (
      <View style={styles.emptyState}>
        <Ionicons name="restaurant-outline" size={48} color="#9CA3AF" />
        <Text style={styles.emptyTitle}>Explorez les recettes</Text>
        <Text style={styles.emptySubtitle}>
          Recherchez une recette ou sélectionnez une catégorie
        </Text>
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>Recettes</Text>
      </View>

      {/* Search Bar */}
      <View style={styles.searchContainer}>
        <View style={styles.searchBar}>
          <Ionicons name="search" size={20} color="#9CA3AF" />
          <TextInput
            style={styles.searchInput}
            placeholder="Rechercher une recette..."
            placeholderTextColor="#9CA3AF"
            value={searchText}
            onChangeText={setSearchText}
            onSubmitEditing={handleSearch}
            returnKeyType="search"
          />
          {searchText.length > 0 && (
            <TouchableOpacity onPress={handleClearSearch}>
              <Ionicons name="close-circle" size={20} color="#9CA3AF" />
            </TouchableOpacity>
          )}
        </View>
      </View>

      {/* Categories */}
      <View style={styles.categoriesSection}>
        <Text style={styles.sectionTitle}>Catégories</Text>
        {isCategoriesLoading ? (
          <ActivityIndicator size="small" color="#14B8A6" />
        ) : (
          <FlatList
            data={categories}
            renderItem={renderCategory}
            keyExtractor={(item) => item.id}
            horizontal
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={styles.categoriesList}
          />
        )}
      </View>

      {/* Error Message */}
      {error && (
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>{error}</Text>
        </View>
      )}

      {/* Recipe List */}
      <View style={styles.recipesSection}>
        {(searchQuery || selectedCategory) && (
          <View style={styles.resultsHeader}>
            <Text style={styles.sectionTitle}>
              {searchQuery
                ? `Résultats pour "${searchQuery}"`
                : `Recettes ${selectedCategory}`}
            </Text>
            <Text style={styles.resultsCount}>
              {recipes.length} recette{recipes.length !== 1 ? 's' : ''}
            </Text>
          </View>
        )}

        {isLoading ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color="#14B8A6" />
          </View>
        ) : (
          <FlatList
            data={recipes}
            renderItem={renderRecipe}
            keyExtractor={(item) => item.id}
            numColumns={2}
            columnWrapperStyle={styles.recipeRow}
            contentContainerStyle={styles.recipesList}
            ListEmptyComponent={renderEmpty}
            showsVerticalScrollIndicator={false}
          />
        )}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  header: {
    paddingHorizontal: 24,
    paddingTop: 16,
    paddingBottom: 8,
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    color: '#111827',
  },
  searchContainer: {
    paddingHorizontal: 24,
    paddingVertical: 12,
  },
  searchBar: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F3F4F6',
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 12,
    gap: 12,
  },
  searchInput: {
    flex: 1,
    fontSize: 16,
    color: '#111827',
  },
  categoriesSection: {
    paddingTop: 8,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#111827',
    paddingHorizontal: 24,
    marginBottom: 12,
  },
  categoriesList: {
    paddingHorizontal: 20,
    gap: 12,
  },
  categoryChip: {
    alignItems: 'center',
    backgroundColor: '#F9FAFB',
    borderRadius: 12,
    padding: 8,
    width: 80,
    borderWidth: 2,
    borderColor: 'transparent',
  },
  categoryChipSelected: {
    backgroundColor: '#CCFBF1',
    borderColor: '#14B8A6',
  },
  categoryImage: {
    width: 48,
    height: 48,
    borderRadius: 24,
    marginBottom: 4,
  },
  categoryText: {
    fontSize: 12,
    color: '#6B7280',
    textAlign: 'center',
  },
  categoryTextSelected: {
    color: '#0D9488',
    fontWeight: '600',
  },
  recipesSection: {
    flex: 1,
    paddingTop: 16,
  },
  resultsHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 24,
    marginBottom: 8,
  },
  resultsCount: {
    fontSize: 14,
    color: '#9CA3AF',
  },
  recipesList: {
    paddingHorizontal: 16,
    paddingBottom: 24,
  },
  recipeRow: {
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  recipeCard: {
    width: '48%',
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
    overflow: 'hidden',
  },
  recipeImage: {
    width: '100%',
    height: 120,
    backgroundColor: '#F3F4F6',
  },
  recipeInfo: {
    padding: 12,
  },
  recipeName: {
    fontSize: 14,
    fontWeight: '600',
    color: '#111827',
    lineHeight: 20,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 48,
    paddingTop: 48,
  },
  emptyTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#374151',
    marginTop: 16,
    textAlign: 'center',
  },
  emptySubtitle: {
    fontSize: 14,
    color: '#9CA3AF',
    marginTop: 8,
    textAlign: 'center',
  },
  errorContainer: {
    marginHorizontal: 24,
    padding: 12,
    backgroundColor: '#FEE2E2',
    borderRadius: 8,
  },
  errorText: {
    color: '#DC2626',
    fontSize: 14,
    textAlign: 'center',
  },
});
