/**
 * RecipeImagePicker Component
 *
 * Image picker for recipe photos using expo-image-picker.
 * Supports camera and gallery selection with preview.
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  Image,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { colors, borderRadius, spacing } from '../../constants/theme';

interface RecipeImagePickerProps {
  /** Current image URL or local URI */
  imageUrl: string | null;
  /** Callback when image changes */
  onChange: (uri: string | null, filename: string | null, mimeType: string | null) => void;
  /** Whether the picker is disabled */
  disabled?: boolean;
  /** Show loading indicator during upload */
  uploading?: boolean;
}

export function RecipeImagePicker({
  imageUrl,
  onChange,
  disabled = false,
  uploading = false,
}: RecipeImagePickerProps) {
  const [requestingPermission, setRequestingPermission] = useState(false);

  const pickImage = async (source: 'camera' | 'gallery') => {
    if (disabled || uploading) return;

    try {
      setRequestingPermission(true);

      // Request appropriate permission
      if (source === 'camera') {
        const { status } = await ImagePicker.requestCameraPermissionsAsync();
        if (status !== 'granted') {
          Alert.alert(
            'Permission requise',
            'Veuillez autoriser l\'acces a la camera dans les parametres.'
          );
          return;
        }
      } else {
        const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
        if (status !== 'granted') {
          Alert.alert(
            'Permission requise',
            'Veuillez autoriser l\'acces a la galerie dans les parametres.'
          );
          return;
        }
      }

      setRequestingPermission(false);

      // Launch picker
      const result = await (source === 'camera'
        ? ImagePicker.launchCameraAsync({
            mediaTypes: ['images'],
            allowsEditing: true,
            aspect: [4, 3],
            quality: 0.8,
          })
        : ImagePicker.launchImageLibraryAsync({
            mediaTypes: ['images'],
            allowsEditing: true,
            aspect: [4, 3],
            quality: 0.8,
          }));

      if (!result.canceled && result.assets[0]) {
        const asset = result.assets[0];
        const filename = asset.fileName || `recipe-${Date.now()}.jpg`;
        const mimeType = asset.mimeType || 'image/jpeg';
        onChange(asset.uri, filename, mimeType);
      }
    } catch (error) {
      Alert.alert('Erreur', 'Impossible de selectionner l\'image.');
      console.error('Image picker error:', error);
    } finally {
      setRequestingPermission(false);
    }
  };

  const showOptions = () => {
    Alert.alert(
      'Ajouter une photo',
      'Choisissez une source',
      [
        {
          text: 'Camera',
          onPress: () => pickImage('camera'),
        },
        {
          text: 'Galerie',
          onPress: () => pickImage('gallery'),
        },
        {
          text: 'Annuler',
          style: 'cancel',
        },
      ]
    );
  };

  const removeImage = () => {
    Alert.alert(
      'Supprimer la photo',
      'Voulez-vous supprimer cette photo ?',
      [
        {
          text: 'Annuler',
          style: 'cancel',
        },
        {
          text: 'Supprimer',
          style: 'destructive',
          onPress: () => onChange(null, null, null),
        },
      ]
    );
  };

  return (
    <View style={styles.container}>
      {imageUrl ? (
        <View style={styles.imageContainer}>
          <Image
            source={{ uri: imageUrl }}
            style={styles.image}
            resizeMode="cover"
          />
          {uploading && (
            <View style={styles.uploadingOverlay}>
              <ActivityIndicator size="large" color={colors.primaryForeground} />
              <Text style={styles.uploadingText}>Envoi en cours...</Text>
            </View>
          )}
          {!uploading && !disabled && (
            <View style={styles.imageActions}>
              <TouchableOpacity
                testID="change-image"
                style={styles.actionButton}
                onPress={showOptions}
              >
                <Text style={styles.actionButtonText}>Changer</Text>
              </TouchableOpacity>
              <TouchableOpacity
                testID="remove-image"
                style={[styles.actionButton, styles.removeActionButton]}
                onPress={removeImage}
              >
                <Text style={styles.removeActionButtonText}>Supprimer</Text>
              </TouchableOpacity>
            </View>
          )}
        </View>
      ) : (
        <TouchableOpacity
          testID="add-image"
          style={styles.placeholder}
          onPress={showOptions}
          disabled={disabled || requestingPermission}
        >
          {requestingPermission ? (
            <ActivityIndicator size="small" color={colors.mutedForeground} />
          ) : (
            <>
              <Text style={styles.placeholderIcon}>📷</Text>
              <Text style={styles.placeholderText}>Ajouter une photo</Text>
              <Text style={styles.placeholderHint}>
                Optionnel - Max 5 Mo
              </Text>
            </>
          )}
        </TouchableOpacity>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginBottom: spacing.md,
  },
  imageContainer: {
    position: 'relative',
    borderRadius: borderRadius.lg,
    overflow: 'hidden',
  },
  image: {
    width: '100%',
    height: 200,
    borderRadius: borderRadius.lg,
  },
  uploadingOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0, 0, 0, 0.6)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  uploadingText: {
    color: colors.primaryForeground,
    fontSize: 14,
    marginTop: spacing.sm,
  },
  imageActions: {
    position: 'absolute',
    bottom: spacing.md,
    right: spacing.md,
    flexDirection: 'row',
    gap: spacing.sm,
  },
  actionButton: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    backgroundColor: 'rgba(0, 0, 0, 0.6)',
    borderRadius: borderRadius.sm,
  },
  actionButtonText: {
    color: colors.primaryForeground,
    fontSize: 14,
    fontWeight: '500',
  },
  removeActionButton: {
    backgroundColor: colors.destructive,
  },
  removeActionButtonText: {
    color: colors.destructiveForeground,
    fontSize: 14,
    fontWeight: '500',
  },
  placeholder: {
    width: '100%',
    height: 160,
    backgroundColor: colors.muted,
    borderRadius: borderRadius.lg,
    borderWidth: 2,
    borderStyle: 'dashed',
    borderColor: colors.border,
    justifyContent: 'center',
    alignItems: 'center',
  },
  placeholderIcon: {
    fontSize: 32,
    marginBottom: spacing.sm,
  },
  placeholderText: {
    fontSize: 16,
    fontWeight: '500',
    color: colors.foreground,
  },
  placeholderHint: {
    fontSize: 13,
    color: colors.mutedForeground,
    marginTop: spacing.xs,
  },
});
