/**
 * Recipe Creation Screen
 *
 * Screen for creating a new personal recipe.
 * Handles image upload and form submission.
 */

import { useState } from 'react';
import { View, Text, StyleSheet, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter, Stack } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { TouchableOpacity } from 'react-native';
import { RecipeForm } from '../../components/recipe/RecipeForm';
import {
  createPersonalRecipe,
  uploadRecipeImage,
} from '../../services/personal-recipes';
import type { PersonalRecipeCreate } from '../../types/personal-recipe';
import { colors } from '../../constants/theme';

export default function CreateRecipeScreen() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [isUploadingImage, setIsUploadingImage] = useState(false);
  const [serverErrors, setServerErrors] = useState<Record<string, string>>({});

  const handleBack = () => {
    router.back();
  };

  const handleSubmit = async (
    data: PersonalRecipeCreate,
    imageFile?: { uri: string; filename: string; mimeType: string }
  ) => {
    try {
      setIsLoading(true);
      setServerErrors({});

      let imageUrl: string | null = null;

      // Upload image first if provided
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
            'Impossible d\'uploader l\'image. La recette sera creee sans photo.'
          );
        } finally {
          setIsUploadingImage(false);
        }
      }

      // Create recipe with image URL
      const recipeData = {
        ...data,
        image_url: imageUrl,
      };

      const createdRecipe = await createPersonalRecipe(recipeData);

      Alert.alert('Succes', 'Votre recette a ete creee avec succes !', [
        {
          text: 'Voir la recette',
          onPress: () => router.replace(`/recipe/personal/${createdRecipe.id}`),
        },
        {
          text: 'Retour aux recettes',
          onPress: () => router.back(),
        },
      ]);
    } catch (error) {
      console.error('Create recipe failed:', error);

      if (error instanceof Error) {
        if (error.message.includes('422')) {
          setServerErrors({ form: 'Donnees invalides. Verifiez les champs.' });
        } else if (error.message.includes('401')) {
          Alert.alert('Session expiree', 'Veuillez vous reconnecter.', [
            { text: 'OK', onPress: () => router.replace('/login') },
          ]);
        } else {
          Alert.alert('Erreur', 'Impossible de creer la recette. Reessayez.');
        }
      } else {
        Alert.alert('Erreur', 'Une erreur inattendue est survenue.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <Stack.Screen
        options={{
          headerShown: true,
          title: 'Nouvelle recette',
          headerLeft: () => (
            <TouchableOpacity onPress={handleBack} style={styles.backButton}>
              <Ionicons name="arrow-back" size={24} color={colors.foreground} />
            </TouchableOpacity>
          ),
        }}
      />
      <SafeAreaView style={styles.container} edges={['bottom']}>
        <RecipeForm
          onSubmit={handleSubmit}
          isLoading={isLoading}
          isUploadingImage={isUploadingImage}
          serverErrors={serverErrors}
          submitButtonText="Creer la recette"
        />
      </SafeAreaView>
    </>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  backButton: {
    marginLeft: 8,
    padding: 8,
  },
});
