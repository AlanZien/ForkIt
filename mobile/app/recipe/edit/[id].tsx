/**
 * Recipe Edit Screen
 *
 * Screen for editing an existing personal recipe.
 * Loads recipe data and handles update/delete operations.
 */

import { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Alert,
  ActivityIndicator,
  TouchableOpacity,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter, useLocalSearchParams, Stack } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { RecipeForm } from '../../../components/recipe/RecipeForm';
import { Button } from '../../../components/ui/Button';
import {
  getPersonalRecipe,
  updatePersonalRecipe,
  deletePersonalRecipe,
  uploadRecipeImage,
} from '../../../services/personal-recipes';
import type {
  PersonalRecipeCreate,
  PersonalRecipeResponse,
} from '../../../types/personal-recipe';
import { colors, spacing } from '../../../constants/theme';

export default function EditRecipeScreen() {
  const router = useRouter();
  const { id } = useLocalSearchParams<{ id: string }>();

  const [recipe, setRecipe] = useState<PersonalRecipeResponse | null>(null);
  const [isLoadingRecipe, setIsLoadingRecipe] = useState(true);
  const [isUpdating, setIsUpdating] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isUploadingImage, setIsUploadingImage] = useState(false);
  const [serverErrors, setServerErrors] = useState<Record<string, string>>({});
  const [loadError, setLoadError] = useState<string | null>(null);

  // Load recipe on mount
  useEffect(() => {
    if (id) {
      loadRecipe();
    }
  }, [id]);

  const loadRecipe = async () => {
    try {
      setIsLoadingRecipe(true);
      setLoadError(null);
      const data = await getPersonalRecipe(id!);
      setRecipe(data);
    } catch (error) {
      console.error('Load recipe failed:', error);
      setLoadError('Impossible de charger la recette.');
    } finally {
      setIsLoadingRecipe(false);
    }
  };

  const handleBack = () => {
    router.back();
  };

  const handleSubmit = async (
    data: PersonalRecipeCreate,
    imageFile?: { uri: string; filename: string; mimeType: string }
  ) => {
    if (!id) return;

    try {
      setIsUpdating(true);
      setServerErrors({});

      let imageUrl: string | null | undefined = undefined;

      // Upload new image if provided
      if (imageFile) {
        try {
          setIsUploadingImage(true);
          const uploadResponse = await uploadRecipeImage(
            imageFile.uri,
            imageFile.filename,
            imageFile.mimeType
          );
          imageUrl = uploadResponse.url;
        } catch (error) {
          console.error('Image upload failed:', error);
          Alert.alert(
            'Erreur',
            'Impossible d\'uploader la nouvelle image.'
          );
          return;
        } finally {
          setIsUploadingImage(false);
        }
      }

      // Build update data
      const updateData = {
        ...data,
        ...(imageUrl !== undefined && { image_url: imageUrl }),
      };

      await updatePersonalRecipe(id, updateData);

      Alert.alert('Succes', 'Votre recette a ete mise a jour !', [
        {
          text: 'OK',
          onPress: () => router.back(),
        },
      ]);
    } catch (error) {
      console.error('Update recipe failed:', error);

      if (error instanceof Error) {
        if (error.message.includes('422')) {
          setServerErrors({ form: 'Donnees invalides. Verifiez les champs.' });
        } else if (error.message.includes('401')) {
          Alert.alert('Session expiree', 'Veuillez vous reconnecter.', [
            { text: 'OK', onPress: () => router.replace('/login') },
          ]);
        } else if (error.message.includes('404')) {
          Alert.alert('Erreur', 'Cette recette n\'existe plus.');
          router.back();
        } else {
          Alert.alert('Erreur', 'Impossible de mettre a jour la recette.');
        }
      } else {
        Alert.alert('Erreur', 'Une erreur inattendue est survenue.');
      }
    } finally {
      setIsUpdating(false);
    }
  };

  const handleDelete = () => {
    Alert.alert(
      'Supprimer la recette',
      'Etes-vous sur de vouloir supprimer cette recette ? Cette action est irreversible.',
      [
        { text: 'Annuler', style: 'cancel' },
        {
          text: 'Supprimer',
          style: 'destructive',
          onPress: confirmDelete,
        },
      ]
    );
  };

  const confirmDelete = async () => {
    if (!id) return;

    try {
      setIsDeleting(true);
      await deletePersonalRecipe(id);

      Alert.alert('Succes', 'La recette a ete supprimee.', [
        {
          text: 'OK',
          onPress: () => router.replace('/(tabs)/recipes'),
        },
      ]);
    } catch (error) {
      console.error('Delete recipe failed:', error);
      Alert.alert('Erreur', 'Impossible de supprimer la recette.');
    } finally {
      setIsDeleting(false);
    }
  };

  // Loading state
  if (isLoadingRecipe) {
    return (
      <>
        <Stack.Screen
          options={{
            headerShown: true,
            title: 'Modifier la recette',
          }}
        />
        <SafeAreaView style={styles.container} edges={['bottom']}>
          <View style={styles.centerContainer}>
            <ActivityIndicator size="large" color={colors.primary} />
            <Text style={styles.loadingText}>Chargement de la recette...</Text>
          </View>
        </SafeAreaView>
      </>
    );
  }

  // Error state
  if (loadError || !recipe) {
    return (
      <>
        <Stack.Screen
          options={{
            headerShown: true,
            title: 'Modifier la recette',
            headerLeft: () => (
              <TouchableOpacity onPress={handleBack} style={styles.backButton}>
                <Ionicons name="arrow-back" size={24} color={colors.foreground} />
              </TouchableOpacity>
            ),
          }}
        />
        <SafeAreaView style={styles.container} edges={['bottom']}>
          <View style={styles.centerContainer}>
            <Ionicons
              name="alert-circle-outline"
              size={48}
              color={colors.destructive}
            />
            <Text style={styles.errorTitle}>Recette introuvable</Text>
            <Text style={styles.errorText}>
              {loadError || 'Cette recette n\'existe pas.'}
            </Text>
            <Button
              title="Retour"
              onPress={handleBack}
              variant="secondary"
              style={styles.retryButton}
            />
          </View>
        </SafeAreaView>
      </>
    );
  }

  return (
    <>
      <Stack.Screen
        options={{
          headerShown: true,
          title: 'Modifier la recette',
          headerLeft: () => (
            <TouchableOpacity onPress={handleBack} style={styles.backButton}>
              <Ionicons name="arrow-back" size={24} color={colors.foreground} />
            </TouchableOpacity>
          ),
        }}
      />
      <SafeAreaView style={styles.container} edges={['bottom']}>
        <RecipeForm
          initialData={recipe}
          onSubmit={handleSubmit}
          isLoading={isUpdating}
          isUploadingImage={isUploadingImage}
          serverErrors={serverErrors}
          submitButtonText="Enregistrer les modifications"
        />

        {/* Delete Button */}
        <View style={styles.deleteSection}>
          <Button
            testID="delete-recipe"
            title={isDeleting ? 'Suppression...' : 'Supprimer la recette'}
            onPress={handleDelete}
            variant="danger"
            loading={isDeleting}
            disabled={isUpdating || isDeleting}
          />
        </View>
      </SafeAreaView>
    </>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: spacing.xl,
    gap: spacing.md,
  },
  loadingText: {
    fontSize: 16,
    color: colors.mutedForeground,
    marginTop: spacing.md,
  },
  errorTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: colors.foreground,
    marginTop: spacing.md,
  },
  errorText: {
    fontSize: 14,
    color: colors.mutedForeground,
    textAlign: 'center',
  },
  retryButton: {
    marginTop: spacing.md,
  },
  backButton: {
    marginLeft: 8,
    padding: 8,
  },
  deleteSection: {
    padding: spacing.md,
    paddingBottom: spacing.lg,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
});
