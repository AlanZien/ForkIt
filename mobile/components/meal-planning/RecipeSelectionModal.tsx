/**
 * RecipeSelectionModal Component
 *
 * Modal for selecting a recipe to add to a meal slot.
 * Has three tabs: Favorites, Search, and Recents.
 */

import React, { useState, useCallback, useEffect, useRef } from 'react';
import {
  View,
  Text,
  Modal,
  TouchableOpacity,
  TextInput,
  FlatList,
  Image,
  StyleSheet,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useFavoritesStore } from '../../stores/favorites';
import { useMealPlanningStore } from '../../stores/meal-planning';
import { searchRecipes } from '../../services/recipes';
import type { MealType, RecentRecipe } from '../../types/meal-slot';
import type { Favorite } from '../../types/favorite';
import type { RecipeSummary } from '../../types/recipe';

interface RecipeSelectionModalProps {
  visible: boolean;
  onClose: () => void;
  onSelect: (recipe: {
    recipe_id: string;
    recipe_name: string;
    recipe_thumbnail: string | null;
  }) => void;
  selectedDate: string;
  selectedMealType: MealType;
}

type TabType = 'favorites' | 'search' | 'recents';

interface TabConfig {
  key: TabType;
  label: string;
  icon: keyof typeof Ionicons.glyphMap;
}

const TABS: TabConfig[] = [
  { key: 'favorites', label: 'Favoris', icon: 'heart' },
  { key: 'search', label: 'Recherche', icon: 'search' },
  { key: 'recents', label: 'Recents', icon: 'time' },
];

export function RecipeSelectionModal({
  visible,
  onClose,
  onSelect,
  selectedMealType,
}: RecipeSelectionModalProps) {
  const [activeTab, setActiveTab] = useState<TabType>('favorites');
  const [searchText, setSearchText] = useState('');
  const [searchResults, setSearchResults] = useState<RecipeSummary[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const searchTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const { favorites, isLoading: isFavoritesLoading, fetchFavorites } = useFavoritesStore();
  const { recentRecipes, fetchRecentRecipes } = useMealPlanningStore();

  // Load data when modal opens
  useEffect(() => {
    if (visible) {
      fetchFavorites();
      fetchRecentRecipes();
    }
  }, [visible, fetchFavorites, fetchRecentRecipes]);

  // Reset state when modal closes
  useEffect(() => {
    if (!visible) {
      setSearchText('');
      setSearchResults([]);
      setActiveTab('favorites');
    }
  }, [visible]);

  // Debounced search
  useEffect(() => {
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }

    if (searchText.trim().length < 2) {
      setSearchResults([]);
      return;
    }

    searchTimeoutRef.current = setTimeout(async () => {
      setIsSearching(true);
      try {
        const response = await searchRecipes(searchText.trim());
        setSearchResults(response.recipes);
      } catch {
        setSearchResults([]);
      } finally {
        setIsSearching(false);
      }
    }, 300);

    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
    };
  }, [searchText]);

  const handleSelectRecipe = useCallback(
    (recipe: { recipe_id: string; recipe_name: string; recipe_thumbnail: string | null }) => {
      onSelect(recipe);
      onClose();
    },
    [onSelect, onClose]
  );

  const handleSelectFavorite = useCallback(
    (favorite: Favorite) => {
      handleSelectRecipe({
        recipe_id: favorite.recipe_id,
        recipe_name: favorite.recipe_name,
        recipe_thumbnail: favorite.recipe_thumbnail,
      });
    },
    [handleSelectRecipe]
  );

  const handleSelectSearchResult = useCallback(
    (recipe: RecipeSummary) => {
      handleSelectRecipe({
        recipe_id: recipe.id,
        recipe_name: recipe.name,
        recipe_thumbnail: recipe.thumbnail,
      });
    },
    [handleSelectRecipe]
  );

  const handleSelectRecent = useCallback(
    (recipe: RecentRecipe) => {
      handleSelectRecipe({
        recipe_id: recipe.recipe_id,
        recipe_name: recipe.recipe_name,
        recipe_thumbnail: recipe.recipe_thumbnail,
      });
    },
    [handleSelectRecipe]
  );

  const renderFavoriteItem = ({ item }: { item: Favorite }) => (
    <TouchableOpacity
      style={styles.recipeItem}
      onPress={() => handleSelectFavorite(item)}
      activeOpacity={0.7}
    >
      <Image
        source={{ uri: item.recipe_thumbnail || undefined }}
        style={styles.recipeThumbnail}
      />
      <Text style={styles.recipeName} numberOfLines={2}>
        {item.recipe_name}
      </Text>
    </TouchableOpacity>
  );

  const renderSearchItem = ({ item }: { item: RecipeSummary }) => (
    <TouchableOpacity
      style={styles.recipeItem}
      onPress={() => handleSelectSearchResult(item)}
      activeOpacity={0.7}
    >
      <Image source={{ uri: item.thumbnail }} style={styles.recipeThumbnail} />
      <Text style={styles.recipeName} numberOfLines={2}>
        {item.name}
      </Text>
    </TouchableOpacity>
  );

  const renderRecentItem = ({ item }: { item: RecentRecipe }) => (
    <TouchableOpacity
      style={styles.recipeItem}
      onPress={() => handleSelectRecent(item)}
      activeOpacity={0.7}
    >
      <Image
        source={{ uri: item.recipe_thumbnail || undefined }}
        style={styles.recipeThumbnail}
      />
      <View style={styles.recentInfo}>
        <Text style={styles.recipeName} numberOfLines={2}>
          {item.recipe_name}
        </Text>
        <Text style={styles.lastUsedText}>
          {formatLastUsed(item.last_used)}
        </Text>
      </View>
    </TouchableOpacity>
  );

  const renderEmptyState = (message: string) => (
    <View style={styles.emptyState}>
      <Ionicons name="restaurant-outline" size={48} color="#9CA3AF" />
      <Text style={styles.emptyStateText}>{message}</Text>
    </View>
  );

  const renderContent = () => {
    switch (activeTab) {
      case 'favorites':
        if (isFavoritesLoading) {
          return (
            <View style={styles.loadingContainer}>
              <ActivityIndicator size="large" color="#14B8A6" />
            </View>
          );
        }
        if (favorites.length === 0) {
          return renderEmptyState('Aucun favori');
        }
        return (
          <FlatList
            data={favorites}
            renderItem={renderFavoriteItem}
            keyExtractor={(item) => item.id}
            contentContainerStyle={styles.listContent}
            showsVerticalScrollIndicator={false}
          />
        );

      case 'search':
        return (
          <View style={styles.searchContainer}>
            <View style={styles.searchInputContainer}>
              <Ionicons name="search" size={20} color="#9CA3AF" />
              <TextInput
                style={styles.searchInput}
                placeholder="Rechercher une recette..."
                placeholderTextColor="#9CA3AF"
                value={searchText}
                onChangeText={setSearchText}
                autoFocus
                returnKeyType="search"
              />
              {searchText.length > 0 && (
                <TouchableOpacity onPress={() => setSearchText('')}>
                  <Ionicons name="close-circle" size={20} color="#9CA3AF" />
                </TouchableOpacity>
              )}
            </View>
            {isSearching ? (
              <View style={styles.loadingContainer}>
                <ActivityIndicator size="large" color="#14B8A6" />
              </View>
            ) : searchResults.length === 0 && searchText.length >= 2 ? (
              renderEmptyState('Aucune recette trouvee')
            ) : (
              <FlatList
                data={searchResults}
                renderItem={renderSearchItem}
                keyExtractor={(item) => item.id}
                contentContainerStyle={styles.listContent}
                showsVerticalScrollIndicator={false}
              />
            )}
          </View>
        );

      case 'recents':
        if (recentRecipes.length === 0) {
          return renderEmptyState('Aucune recette recente');
        }
        return (
          <FlatList
            data={recentRecipes}
            renderItem={renderRecentItem}
            keyExtractor={(item) => item.recipe_id}
            contentContainerStyle={styles.listContent}
            showsVerticalScrollIndicator={false}
          />
        );

      default:
        return null;
    }
  };

  const mealTypeLabel = selectedMealType === 'dejeuner' ? 'Dejeuner' : 'Diner';

  return (
    <Modal
      visible={visible}
      animationType="slide"
      presentationStyle="pageSheet"
      onRequestClose={onClose}
    >
      <KeyboardAvoidingView
        style={styles.container}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      >
        {/* Header */}
        <View style={styles.header}>
          <View style={styles.headerTitleContainer}>
            <Text style={styles.headerTitle}>Choisir une recette</Text>
            <Text style={styles.headerSubtitle}>{mealTypeLabel}</Text>
          </View>
          <TouchableOpacity
            style={styles.closeButton}
            onPress={onClose}
            hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
          >
            <Ionicons name="close" size={24} color="#374151" />
          </TouchableOpacity>
        </View>

        {/* Tabs */}
        <View style={styles.tabsContainer}>
          {TABS.map((tab) => (
            <TouchableOpacity
              key={tab.key}
              style={[styles.tab, activeTab === tab.key && styles.tabActive]}
              onPress={() => setActiveTab(tab.key)}
              activeOpacity={0.7}
            >
              <Ionicons
                name={tab.icon}
                size={18}
                color={activeTab === tab.key ? '#14B8A6' : '#6B7280'}
              />
              <Text
                style={[
                  styles.tabLabel,
                  activeTab === tab.key && styles.tabLabelActive,
                ]}
              >
                {tab.label}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Content */}
        <View style={styles.content}>{renderContent()}</View>
      </KeyboardAvoidingView>
    </Modal>
  );
}

function formatLastUsed(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffTime = Math.abs(now.getTime() - date.getTime());
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

  if (diffDays === 0) {
    return "Aujourd'hui";
  } else if (diffDays === 1) {
    return 'Hier';
  } else if (diffDays < 7) {
    return `Il y a ${diffDays} jours`;
  } else if (diffDays < 14) {
    return 'La semaine derniere';
  } else {
    return `Il y a ${Math.floor(diffDays / 7)} semaines`;
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingTop: 16,
    paddingBottom: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  headerTitleContainer: {
    flex: 1,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: '#111827',
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 2,
  },
  closeButton: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#F3F4F6',
    justifyContent: 'center',
    alignItems: 'center',
  },
  tabsContainer: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    paddingVertical: 12,
    gap: 8,
  },
  tab: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 10,
    paddingHorizontal: 12,
    borderRadius: 20,
    backgroundColor: '#F3F4F6',
    gap: 6,
  },
  tabActive: {
    backgroundColor: '#CCFBF1',
  },
  tabLabel: {
    fontSize: 14,
    fontWeight: '500',
    color: '#6B7280',
  },
  tabLabelActive: {
    color: '#0D9488',
  },
  content: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  searchContainer: {
    flex: 1,
  },
  searchInputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F3F4F6',
    marginHorizontal: 16,
    marginVertical: 8,
    paddingHorizontal: 12,
    paddingVertical: 10,
    borderRadius: 12,
    gap: 10,
  },
  searchInput: {
    flex: 1,
    fontSize: 16,
    color: '#111827',
  },
  listContent: {
    padding: 16,
  },
  recipeItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#E5E7EB',
    borderRadius: 12,
    padding: 12,
    marginBottom: 12,
  },
  recipeThumbnail: {
    width: 48,
    height: 48,
    borderRadius: 8,
    backgroundColor: '#F3F4F6',
  },
  recipeName: {
    flex: 1,
    marginLeft: 12,
    fontSize: 15,
    fontWeight: '500',
    color: '#111827',
  },
  recentInfo: {
    flex: 1,
    marginLeft: 12,
  },
  lastUsedText: {
    fontSize: 12,
    color: '#9CA3AF',
    marginTop: 4,
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 40,
  },
  emptyStateText: {
    fontSize: 16,
    color: '#9CA3AF',
    textAlign: 'center',
    marginTop: 16,
  },
});
