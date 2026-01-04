/**
 * EditPortionsModal Component
 *
 * Bottom sheet modal for editing meal slot portions.
 * Follows SlotActionMenu bottom sheet pattern.
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  Modal,
  TouchableOpacity,
  StyleSheet,
  Pressable,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { PortionSelector } from '../preferences/PortionSelector';

interface EditPortionsModalProps {
  /** Whether the modal is visible */
  visible: boolean;
  /** Callback when modal should close */
  onClose: () => void;
  /** Callback when portions are confirmed */
  onConfirm: (portions: number) => void;
  /** Current portions value */
  currentPortions: number;
  /** Recipe name for display */
  recipeName: string;
}

export function EditPortionsModal({
  visible,
  onClose,
  onConfirm,
  currentPortions,
  recipeName,
}: EditPortionsModalProps) {
  const [portions, setPortions] = useState(currentPortions);

  // Reset portions when modal opens
  useEffect(() => {
    if (visible) {
      setPortions(currentPortions);
    }
  }, [visible, currentPortions]);

  const handleConfirm = () => {
    onConfirm(portions);
  };

  const handleCancel = () => {
    setPortions(currentPortions);
    onClose();
  };

  return (
    <Modal
      visible={visible}
      animationType="slide"
      transparent
      onRequestClose={handleCancel}
    >
      <Pressable style={styles.overlay} onPress={handleCancel}>
        <Pressable style={styles.sheet} onPress={(e) => e.stopPropagation()}>
          {/* Handle bar */}
          <View style={styles.handleBar} />

          {/* Recipe name header */}
          <View style={styles.header}>
            <Text style={styles.recipeName} numberOfLines={2}>
              {recipeName}
            </Text>
          </View>

          {/* Portions selector section */}
          <View style={styles.selectorSection}>
            <Text style={styles.sectionTitle}>Modifier les portions</Text>

            <View style={styles.selectorContainer}>
              <PortionSelector
                value={portions}
                onChange={setPortions}
                min={1}
                max={20}
              />
            </View>

            {/* Info message */}
            <View style={styles.infoContainer}>
              <Ionicons name="information-circle-outline" size={18} color="#6B7280" />
              <Text style={styles.infoText}>
                La liste de courses devra etre regeneree
              </Text>
            </View>
          </View>

          {/* Action buttons */}
          <View style={styles.buttonsContainer}>
            <TouchableOpacity
              style={styles.confirmButton}
              onPress={handleConfirm}
              activeOpacity={0.8}
            >
              <Text style={styles.confirmButtonText}>Confirmer</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.cancelButton}
              onPress={handleCancel}
              activeOpacity={0.8}
            >
              <Text style={styles.cancelButtonText}>Annuler</Text>
            </TouchableOpacity>
          </View>
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
  selectorSection: {
    paddingVertical: 20,
    paddingHorizontal: 20,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '500',
    color: '#374151',
    marginBottom: 16,
    textAlign: 'center',
  },
  selectorContainer: {
    alignItems: 'center',
    marginBottom: 16,
  },
  infoContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#F3F4F6',
    paddingVertical: 10,
    paddingHorizontal: 16,
    borderRadius: 8,
    gap: 8,
  },
  infoText: {
    fontSize: 13,
    color: '#6B7280',
    flex: 1,
  },
  buttonsContainer: {
    paddingHorizontal: 20,
    gap: 8,
  },
  confirmButton: {
    paddingVertical: 14,
    backgroundColor: '#14B8A6',
    borderRadius: 12,
    alignItems: 'center',
  },
  confirmButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  cancelButton: {
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
