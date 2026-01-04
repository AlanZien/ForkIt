/**
 * Shopping List Screen
 *
 * Displays the shopping list generated from the weekly meal plan.
 * Features:
 * - Grouped items by category
 * - Collapsible sections
 * - Check/uncheck items with optimistic updates
 * - Regenerate list functionality
 */

import { useEffect, useCallback, useState } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  RefreshControl,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useFocusEffect } from 'expo-router';
import { useAuthStore } from '../../stores/auth';
import { useShoppingListStore } from '../../stores/shopping-list';
import {
  CategorySection,
  EmptyState,
  ListHeader,
} from '../../components/shopping-list';

export default function ShoppingScreen() {
  const { isAuthenticated } = useAuthStore();
  const [refreshing, setRefreshing] = useState(false);

  const {
    items,
    isLoading,
    isGenerating,
    error,
    lastGeneratedAt,
    currentWeekStart,
    fetchList,
    generateList,
    toggleItem,
    uncheckAll,
    getItemsByCategory,
  } = useShoppingListStore();

  // Fetch list when screen gains focus
  useFocusEffect(
    useCallback(() => {
      if (isAuthenticated) {
        fetchList();
      }
    }, [isAuthenticated, fetchList])
  );

  // Handle pull-to-refresh
  const handleRefresh = useCallback(async () => {
    setRefreshing(true);
    await fetchList();
    setRefreshing(false);
  }, [fetchList]);

  // Handle generate list
  const handleGenerateList = useCallback(async () => {
    try {
      await generateList();
    } catch {
      Alert.alert('Erreur', 'Impossible de generer la liste. Veuillez reessayer.');
    }
  }, [generateList]);

  // Handle regenerate with confirmation
  const handleRegenerate = useCallback(() => {
    Alert.alert(
      'Regenerer la liste ?',
      'Cette action effacera les elements coches.',
      [
        {
          text: 'Annuler',
          style: 'cancel',
        },
        {
          text: 'Regenerer',
          style: 'destructive',
          onPress: handleGenerateList,
        },
      ]
    );
  }, [handleGenerateList]);

  // Handle toggle item
  const handleToggleItem = useCallback(
    async (id: string) => {
      try {
        await toggleItem(id);
      } catch {
        // Error handled by store, item rolls back automatically
      }
    },
    [toggleItem]
  );

  // Handle uncheck all
  const handleUncheckAll = useCallback(async () => {
    try {
      await uncheckAll();
    } catch {
      Alert.alert('Erreur', 'Impossible de decocher les elements.');
    }
  }, [uncheckAll]);

  // Get grouped items
  const categoryGroups = getItemsByCategory();
  const totalItems = items.size;
  const checkedCount = Array.from(items.values()).filter((item) => item.is_checked)
    .length;

  // Loading state
  if (isLoading && !refreshing && totalItems === 0) {
    return (
      <SafeAreaView style={styles.container} edges={['top']}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#14B8A6" />
        </View>
      </SafeAreaView>
    );
  }

  // Empty state
  if (totalItems === 0 && !isLoading) {
    return (
      <SafeAreaView style={styles.container} edges={['top']}>
        <EmptyState onGenerateList={handleGenerateList} isLoading={isGenerating} />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      {/* Header with progress and actions */}
      <ListHeader
        weekStart={currentWeekStart}
        totalItems={totalItems}
        checkedCount={checkedCount}
        lastGeneratedAt={lastGeneratedAt}
        onUncheckAll={handleUncheckAll}
        onRegenerate={handleRegenerate}
        isGenerating={isGenerating}
      />

      {/* Scrollable list */}
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={handleRefresh}
            tintColor="#14B8A6"
            colors={['#14B8A6']}
          />
        }
      >
        {categoryGroups.map((group) => (
          <CategorySection
            key={group.category}
            category={group.category}
            items={group.items}
            onToggleItem={handleToggleItem}
          />
        ))}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    padding: 16,
    paddingBottom: 32,
  },
});
