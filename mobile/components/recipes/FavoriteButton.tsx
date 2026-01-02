/**
 * FavoriteButton Component
 *
 * Heart button to toggle favorite status of a recipe.
 * Uses favorites store for state management.
 */

import { useCallback } from 'react';
import {
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  ViewStyle,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useFavoritesStore } from '../../stores/favorites';

interface FavoriteButtonProps {
  recipeId: string;
  recipeName: string;
  recipeThumbnail?: string | null;
  size?: 'small' | 'medium' | 'large';
  variant?: 'default' | 'overlay';
  style?: ViewStyle;
}

const SIZES = {
  small: { button: 28, icon: 16 },
  medium: { button: 36, icon: 20 },
  large: { button: 44, icon: 24 },
};

export function FavoriteButton({
  recipeId,
  recipeName,
  recipeThumbnail,
  size = 'medium',
  variant = 'default',
  style,
}: FavoriteButtonProps) {
  const { isFavorite, addFavorite, removeFavorite, isUpdating } =
    useFavoritesStore();

  const favorite = isFavorite(recipeId);
  const dimensions = SIZES[size];

  const handlePress = useCallback(async () => {
    if (isUpdating) return;

    try {
      if (favorite) {
        await removeFavorite(recipeId);
      } else {
        await addFavorite({
          recipe_id: recipeId,
          recipe_name: recipeName,
          recipe_thumbnail: recipeThumbnail,
        });
      }
    } catch {
      // Error is handled by the store
    }
  }, [
    favorite,
    recipeId,
    recipeName,
    recipeThumbnail,
    addFavorite,
    removeFavorite,
    isUpdating,
  ]);

  const buttonStyle = [
    styles.button,
    {
      width: dimensions.button,
      height: dimensions.button,
      borderRadius: dimensions.button / 2,
    },
    variant === 'overlay' ? styles.overlay : styles.default,
    style,
  ];

  return (
    <TouchableOpacity
      style={buttonStyle}
      onPress={handlePress}
      activeOpacity={0.7}
      hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
    >
      {isUpdating ? (
        <ActivityIndicator
          size="small"
          color={variant === 'overlay' ? '#FFFFFF' : '#14B8A6'}
        />
      ) : (
        <Ionicons
          name={favorite ? 'heart' : 'heart-outline'}
          size={dimensions.icon}
          color={favorite ? '#EF4444' : variant === 'overlay' ? '#FFFFFF' : '#6B7280'}
        />
      )}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  button: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  default: {
    backgroundColor: '#F3F4F6',
  },
  overlay: {
    backgroundColor: 'rgba(0, 0, 0, 0.4)',
  },
});
