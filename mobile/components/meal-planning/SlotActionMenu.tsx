/**
 * SlotActionMenu Component
 *
 * Bottom sheet action menu for meal slot actions.
 * Shows View, Replace, Edit Portions, and Delete options with delete confirmation.
 */

import React from 'react';
import {
  View,
  Text,
  Modal,
  TouchableOpacity,
  StyleSheet,
  Pressable,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface SlotActionMenuProps {
  visible: boolean;
  onClose: () => void;
  onView: () => void;
  onReplace: () => void;
  onEditPortions: () => void;
  onDelete: () => void;
  recipeName: string;
}

interface ActionItemProps {
  icon: keyof typeof Ionicons.glyphMap;
  label: string;
  onPress: () => void;
  color?: string;
  iconColor?: string;
}

function ActionItem({
  icon,
  label,
  onPress,
  color = '#111827',
  iconColor = '#6B7280',
}: ActionItemProps) {
  return (
    <TouchableOpacity
      style={styles.actionItem}
      onPress={onPress}
      activeOpacity={0.7}
    >
      <View style={styles.actionIconContainer}>
        <Ionicons name={icon} size={22} color={iconColor} />
      </View>
      <Text style={[styles.actionLabel, { color }]}>{label}</Text>
      <Ionicons name="chevron-forward" size={20} color="#D1D5DB" />
    </TouchableOpacity>
  );
}

export function SlotActionMenu({
  visible,
  onClose,
  onView,
  onReplace,
  onEditPortions,
  onDelete,
  recipeName,
}: SlotActionMenuProps) {
  const handleDelete = () => {
    Alert.alert(
      'Supprimer ce repas ?',
      `Voulez-vous retirer "${recipeName}" de votre planning ?`,
      [
        {
          text: 'Annuler',
          style: 'cancel',
        },
        {
          text: 'Supprimer',
          style: 'destructive',
          onPress: () => {
            onDelete();
            onClose();
          },
        },
      ],
      { cancelable: true }
    );
  };

  const handleView = () => {
    onClose();
    onView();
  };

  const handleReplace = () => {
    // Don't call onClose() - it resets selectedSlot which is needed for the next modal
    onReplace();
  };

  const handleEditPortions = () => {
    // Don't call onClose() - it resets selectedSlot which is needed for the next modal
    onEditPortions();
  };

  return (
    <Modal
      visible={visible}
      animationType="slide"
      transparent
      onRequestClose={onClose}
    >
      <Pressable style={styles.overlay} onPress={onClose}>
        <Pressable style={styles.sheet} onPress={(e) => e.stopPropagation()}>
          {/* Handle bar */}
          <View style={styles.handleBar} />

          {/* Recipe name header */}
          <View style={styles.header}>
            <Text style={styles.recipeName} numberOfLines={2}>
              {recipeName}
            </Text>
          </View>

          {/* Actions */}
          <View style={styles.actionsContainer}>
            <ActionItem
              icon="eye-outline"
              label="Voir la recette"
              onPress={handleView}
              iconColor="#14B8A6"
            />
            <ActionItem
              icon="swap-horizontal-outline"
              label="Remplacer"
              onPress={handleReplace}
              iconColor="#F59E0B"
            />
            <ActionItem
              icon="create-outline"
              label="Modifier les portions"
              onPress={handleEditPortions}
              iconColor="#8B5CF6"
            />
            <ActionItem
              icon="trash-outline"
              label="Supprimer"
              onPress={handleDelete}
              color="#EF4444"
              iconColor="#EF4444"
            />
          </View>

          {/* Cancel button */}
          <TouchableOpacity
            style={styles.cancelButton}
            onPress={onClose}
            activeOpacity={0.8}
          >
            <Text style={styles.cancelButtonText}>Annuler</Text>
          </TouchableOpacity>
        </Pressable>
      </Pressable>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.4)',
    justifyContent: 'flex-end',
  },
  sheet: {
    backgroundColor: '#FFFFFF',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    paddingTop: 8,
    paddingBottom: 34,
  },
  handleBar: {
    width: 36,
    height: 4,
    backgroundColor: '#D1D5DB',
    borderRadius: 2,
    alignSelf: 'center',
    marginBottom: 16,
  },
  header: {
    paddingHorizontal: 20,
    paddingBottom: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  recipeName: {
    fontSize: 18,
    fontWeight: '600',
    color: '#111827',
    textAlign: 'center',
  },
  actionsContainer: {
    paddingVertical: 8,
  },
  actionItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 14,
    paddingHorizontal: 20,
  },
  actionIconContainer: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#F3F4F6',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  actionLabel: {
    flex: 1,
    fontSize: 16,
    fontWeight: '500',
  },
  cancelButton: {
    marginHorizontal: 20,
    marginTop: 8,
    paddingVertical: 14,
    backgroundColor: '#F3F4F6',
    borderRadius: 12,
    alignItems: 'center',
  },
  cancelButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
  },
});
