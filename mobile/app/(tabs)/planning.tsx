/**
 * Planning Screen
 *
 * Weekly meal planning view with navigation between weeks.
 * Allows users to add, view, replace, edit portions, and delete recipes in meal slots.
 */

import { useEffect, useState, useCallback } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAuthStore } from '../../stores/auth';
import { useMealPlanningStore } from '../../stores/meal-planning';
import { usePreferencesStore } from '../../stores/preferences';
import {
  WeekNavigator,
  WeekView,
  RecipeSelectionModal,
  SlotActionMenu,
  EditPortionsModal,
} from '../../components/meal-planning';
import type { MealSlot, MealType } from '../../types/meal-slot';

interface SelectedSlotState {
  date: string;
  mealType: MealType;
  slot: MealSlot | null;
}

export default function PlanningScreen() {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();
  const { preferences } = usePreferencesStore();

  const {
    currentWeekStart,
    fetchWeek,
    addSlot,
    updateSlot,
    removeSlot,
    navigateWeek,
    canNavigatePrev,
    canNavigateNext,
    getSlot,
  } = useMealPlanningStore();

  // Modal states
  const [isSelectionModalVisible, setIsSelectionModalVisible] = useState(false);
  const [isActionMenuVisible, setIsActionMenuVisible] = useState(false);
  const [isEditPortionsModalVisible, setIsEditPortionsModalVisible] = useState(false);
  const [selectedSlot, setSelectedSlot] = useState<SelectedSlotState | null>(null);

  // Fetch current week on mount and when authenticated
  useEffect(() => {
    if (isAuthenticated) {
      fetchWeek();
    }
  }, [isAuthenticated, fetchWeek]);

  // Handle slot press (empty or filled)
  const handleSlotPress = useCallback(
    (date: string, mealType: MealType) => {
      const slot = getSlot(date, mealType);

      if (slot) {
        // Filled slot - show action menu
        setSelectedSlot({ date, mealType, slot });
        setIsActionMenuVisible(true);
      } else {
        // Empty slot - show selection modal
        setSelectedSlot({ date, mealType, slot: null });
        setIsSelectionModalVisible(true);
      }
    },
    [getSlot]
  );

  // Handle slot long press (only for filled slots)
  const handleSlotLongPress = useCallback(
    (date: string, mealType: MealType, slot: MealSlot) => {
      setSelectedSlot({ date, mealType, slot });
      setIsActionMenuVisible(true);
    },
    []
  );

  // Handle recipe selection from modal
  const handleRecipeSelect = useCallback(
    async (recipe: {
      recipe_id: string;
      recipe_name: string;
      recipe_thumbnail: string | null;
    }) => {
      if (!selectedSlot) return;

      try {
        await addSlot({
          recipe_id: recipe.recipe_id,
          recipe_name: recipe.recipe_name,
          recipe_thumbnail: recipe.recipe_thumbnail,
          slot_date: selectedSlot.date,
          meal_type: selectedSlot.mealType,
          portions: preferences?.portions_count || 2,
        });
      } catch {
        // Error is handled by the store
      }

      setIsSelectionModalVisible(false);
      setSelectedSlot(null);
    },
    [selectedSlot, addSlot, preferences]
  );

  // Handle view recipe action
  const handleViewRecipe = useCallback(() => {
    if (selectedSlot?.slot) {
      router.push(`/recipe/${selectedSlot.slot.recipe_id}`);
    }
    setIsActionMenuVisible(false);
    setSelectedSlot(null);
  }, [selectedSlot, router]);

  // Handle replace recipe action
  const handleReplaceRecipe = useCallback(() => {
    setIsActionMenuVisible(false);
    setIsSelectionModalVisible(true);
  }, []);

  // Handle edit portions action
  const handleEditPortions = useCallback(() => {
    setIsActionMenuVisible(false);
    setIsEditPortionsModalVisible(true);
  }, []);

  // Handle confirm portions update
  const handleConfirmPortions = useCallback(
    async (newPortions: number) => {
      if (!selectedSlot) return;

      try {
        await updateSlot(selectedSlot.date, selectedSlot.mealType, {
          portions: newPortions,
        });
      } catch {
        // Error is handled by the store
      }

      setIsEditPortionsModalVisible(false);
      setSelectedSlot(null);
    },
    [selectedSlot, updateSlot]
  );

  // Handle delete slot action
  const handleDeleteSlot = useCallback(async () => {
    if (!selectedSlot) return;

    try {
      await removeSlot(selectedSlot.date, selectedSlot.mealType);
    } catch {
      // Error is handled by the store
    }

    setIsActionMenuVisible(false);
    setSelectedSlot(null);
  }, [selectedSlot, removeSlot]);

  // Close modals
  const handleCloseSelectionModal = useCallback(() => {
    setIsSelectionModalVisible(false);
    setSelectedSlot(null);
  }, []);

  const handleCloseActionMenu = useCallback(() => {
    setIsActionMenuVisible(false);
    setSelectedSlot(null);
  }, []);

  const handleCloseEditPortionsModal = useCallback(() => {
    setIsEditPortionsModalVisible(false);
    setSelectedSlot(null);
  }, []);

  // Week navigation
  const handlePreviousWeek = useCallback(() => {
    navigateWeek('prev');
  }, [navigateWeek]);

  const handleNextWeek = useCallback(() => {
    navigateWeek('next');
  }, [navigateWeek]);

  // Not authenticated state
  if (!isAuthenticated) {
    return (
      <SafeAreaView style={styles.container} edges={['top']}>
        <View style={styles.header}>
          <Text style={styles.title}>Planning</Text>
        </View>
        <View style={styles.notAuthContainer}>
          <Ionicons name="calendar-outline" size={64} color="#D1D5DB" />
          <Text style={styles.notAuthTitle}>Connectez-vous</Text>
          <Text style={styles.notAuthSubtitle}>
            Creez un compte pour planifier vos repas de la semaine
          </Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>Planning</Text>
      </View>

      {/* Week Navigator */}
      <WeekNavigator
        onPrevious={handlePreviousWeek}
        onNext={handleNextWeek}
        canGoPrev={false}
        canGoNext={false}
      />

      {/* Week View */}
      <WeekView
        onSlotPress={handleSlotPress}
        onSlotLongPress={handleSlotLongPress}
      />

      {/* Recipe Selection Modal */}
      <RecipeSelectionModal
        visible={isSelectionModalVisible}
        onClose={handleCloseSelectionModal}
        onSelect={handleRecipeSelect}
        selectedDate={selectedSlot?.date || ''}
        selectedMealType={selectedSlot?.mealType || 'dejeuner'}
      />

      {/* Slot Action Menu */}
      <SlotActionMenu
        visible={isActionMenuVisible}
        onClose={handleCloseActionMenu}
        onView={handleViewRecipe}
        onReplace={handleReplaceRecipe}
        onEditPortions={handleEditPortions}
        onDelete={handleDeleteSlot}
        recipeName={selectedSlot?.slot?.recipe_name || ''}
      />

      {/* Edit Portions Modal */}
      <EditPortionsModal
        visible={isEditPortionsModalVisible}
        onClose={handleCloseEditPortionsModal}
        onConfirm={handleConfirmPortions}
        currentPortions={selectedSlot?.slot?.portions || preferences?.portions_count || 2}
        recipeName={selectedSlot?.slot?.recipe_name || ''}
      />
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
  notAuthContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 40,
  },
  notAuthTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#374151',
    marginTop: 20,
  },
  notAuthSubtitle: {
    fontSize: 15,
    color: '#6B7280',
    textAlign: 'center',
    marginTop: 8,
    lineHeight: 22,
  },
});
