/**
 * ListHeader Component
 *
 * Header for the shopping list showing title, progress, and action buttons.
 */

import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface ListHeaderProps {
  weekStart: string;
  totalItems: number;
  checkedCount: number;
  lastGeneratedAt: string | null;
  onUncheckAll: () => void;
  onRegenerate: () => void;
  isGenerating?: boolean;
}

export function ListHeader({
  weekStart,
  totalItems,
  checkedCount,
  lastGeneratedAt,
  onUncheckAll,
  onRegenerate,
  isGenerating = false,
}: ListHeaderProps) {
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const day = date.getDate();
    const month = date.toLocaleDateString('fr-FR', { month: 'long' });
    return `${day} ${month}`;
  };

  const formatGeneratedAt = (isoStr: string) => {
    const date = new Date(isoStr);
    return date.toLocaleTimeString('fr-FR', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const progress = totalItems > 0 ? (checkedCount / totalItems) * 100 : 0;

  return (
    <View style={styles.container}>
      {/* Title and subtitle */}
      <View style={styles.titleSection}>
        <Text style={styles.title}>Liste de courses</Text>
        <Text style={styles.subtitle}>
          Semaine du {formatDate(weekStart)}
          {lastGeneratedAt && ` - Generee a ${formatGeneratedAt(lastGeneratedAt)}`}
        </Text>
      </View>

      {/* Progress bar */}
      <View style={styles.progressContainer}>
        <View style={styles.progressBar}>
          <View style={[styles.progressFill, { width: `${progress}%` }]} />
        </View>
        <Text style={styles.progressText}>
          {checkedCount}/{totalItems} articles
        </Text>
      </View>

      {/* Action buttons */}
      <View style={styles.actionsContainer}>
        <TouchableOpacity
          style={styles.ghostButton}
          onPress={onUncheckAll}
          disabled={checkedCount === 0}
          activeOpacity={0.7}
          accessibilityRole="button"
          accessibilityLabel="Tout decocher"
        >
          <Ionicons
            name="refresh-outline"
            size={16}
            color={checkedCount === 0 ? '#9CA3AF' : '#14B8A6'}
          />
          <Text
            style={[
              styles.ghostButtonText,
              checkedCount === 0 && styles.buttonDisabledText,
            ]}
          >
            Tout decocher
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.secondaryButton, isGenerating && styles.buttonDisabled]}
          onPress={onRegenerate}
          disabled={isGenerating}
          activeOpacity={0.8}
          accessibilityRole="button"
          accessibilityLabel="Regenerer la liste"
        >
          <Ionicons name="sync" size={16} color="#FFFFFF" />
          <Text style={styles.secondaryButtonText}>
            {isGenerating ? 'Generation...' : 'Regenerer'}
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    paddingHorizontal: 16,
    paddingTop: 8,
    paddingBottom: 16,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  titleSection: {
    marginBottom: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: '700',
    color: '#111827',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 14,
    color: '#6B7280',
  },
  progressContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  progressBar: {
    flex: 1,
    height: 8,
    backgroundColor: '#E5E7EB',
    borderRadius: 4,
    overflow: 'hidden',
    marginRight: 12,
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#14B8A6',
    borderRadius: 4,
  },
  progressText: {
    fontSize: 13,
    color: '#6B7280',
    fontWeight: '500',
    minWidth: 80,
    textAlign: 'right',
  },
  actionsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  ghostButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    paddingHorizontal: 12,
  },
  ghostButtonText: {
    fontSize: 14,
    fontWeight: '500',
    color: '#14B8A6',
    marginLeft: 6,
  },
  secondaryButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FF8A65',
    paddingVertical: 10,
    paddingHorizontal: 16,
    borderRadius: 8,
  },
  secondaryButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#FFFFFF',
    marginLeft: 6,
  },
  buttonDisabled: {
    backgroundColor: '#9CA3AF',
  },
  buttonDisabledText: {
    color: '#9CA3AF',
  },
});
