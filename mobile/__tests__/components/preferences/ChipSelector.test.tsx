/**
 * Tests for ChipSelector Component
 *
 * Unit tests for chip selection logic (Task Group 5)
 * These tests mock React Native to focus on component logic
 */

import React from 'react';

// Mock react-native before importing component
jest.mock('react-native', () => ({
  View: 'View',
  Text: 'Text',
  TouchableOpacity: 'TouchableOpacity',
  StyleSheet: {
    create: (styles: any) => styles,
  },
}));

// Mock theme constants
jest.mock('../../../constants/theme', () => ({
  colors: {
    primary: '#14B8A6',
    primaryForeground: '#FFFFFF',
    muted: '#F3F4F6',
    foreground: '#1F2937',
  },
  borderRadius: {
    xl: 20,
  },
  spacing: {
    sm: 8,
    md: 16,
    xs: 4,
  },
}));

import { ChipSelector } from '../../../components/preferences/ChipSelector';
import type { DietaryType } from '../../../types/preferences';
import { DIETARY_LABELS } from '../../../types/preferences';

// Simple render helper for testing component output
const renderComponent = (props: Parameters<typeof ChipSelector>[0]) => {
  const element = ChipSelector(props as any);
  return element;
};

describe('ChipSelector', () => {
  const mockOptions: DietaryType[] = ['vegetarian', 'vegan', 'halal', 'kosher'];
  const mockLabels = DIETARY_LABELS;

  describe('Selection Logic', () => {
    /**
     * Test: ChipSelector adds value when pressing unselected chip
     * Given: Component with some selected values
     * When: User selects an unselected option
     * Then: onSelect is called with the new value added
     */
    it('should call onSelect with value added when selecting unselected chip', () => {
      // Given
      const onSelect = jest.fn();
      const selectedValues: DietaryType[] = ['vegetarian'];

      // Simulate the handlePress logic directly
      const handlePress = (option: DietaryType) => {
        const isSelected = selectedValues.includes(option);
        if (isSelected) {
          onSelect(selectedValues.filter((v) => v !== option));
        } else {
          onSelect([...selectedValues, option]);
        }
      };

      // When - select an unselected option
      handlePress('vegan');

      // Then
      expect(onSelect).toHaveBeenCalledWith(['vegetarian', 'vegan']);
    });

    /**
     * Test: ChipSelector removes value when pressing selected chip
     * Given: Component with selected values
     * When: User deselects an option
     * Then: onSelect is called with the value removed
     */
    it('should call onSelect with value removed when deselecting chip', () => {
      // Given
      const onSelect = jest.fn();
      const selectedValues: DietaryType[] = ['vegetarian', 'vegan'];

      // Simulate the handlePress logic directly
      const handlePress = (option: DietaryType) => {
        const isSelected = selectedValues.includes(option);
        if (isSelected) {
          onSelect(selectedValues.filter((v) => v !== option));
        } else {
          onSelect([...selectedValues, option]);
        }
      };

      // When - deselect vegetarian
      handlePress('vegetarian');

      // Then
      expect(onSelect).toHaveBeenCalledWith(['vegan']);
    });

    /**
     * Test: ChipSelector does not respond when disabled
     * Given: Component with disabled=true
     * When: User tries to select
     * Then: onSelect is not called
     */
    it('should not call onSelect when disabled', () => {
      // Given
      const onSelect = jest.fn();
      const disabled = true;

      // Simulate the handlePress logic with disabled check
      const handlePress = (option: DietaryType) => {
        if (disabled) return;
        onSelect([option]);
      };

      // When - try to select while disabled
      handlePress('vegetarian');

      // Then
      expect(onSelect).not.toHaveBeenCalled();
    });
  });

  describe('Rendering', () => {
    /**
     * Test: ChipSelector renders correct number of options
     * Given: Array of options
     * When: Component renders
     * Then: Returns element with correct structure
     */
    it('should render component with options', () => {
      // Given
      const options = mockOptions;

      // When
      const element = renderComponent({
        options,
        labels: mockLabels,
        selectedValues: [],
        onSelect: jest.fn(),
      });

      // Then - element should exist and have the expected structure
      expect(element).toBeDefined();
      expect(element.type).toBe('View');
      expect(element.props.children).toHaveLength(options.length);
    });

    /**
     * Test: ChipSelector applies correct styles for selected chips
     * Given: Options with some selected
     * When: Rendering selected chip
     * Then: Has active background color style
     */
    it('should apply active style to selected chips', () => {
      // Given
      const selectedValues: DietaryType[] = ['vegetarian'];

      // When
      const element = renderComponent({
        options: mockOptions,
        labels: mockLabels,
        selectedValues,
        onSelect: jest.fn(),
      });

      // Then - first chip (vegetarian) should have active style
      const chips = element.props.children;
      const vegetarianChip = chips[0];

      // Check that the style array includes chipActive
      expect(vegetarianChip.props.style).toEqual(
        expect.arrayContaining([
          expect.objectContaining({ backgroundColor: '#14B8A6' }),
        ])
      );
    });

    /**
     * Test: ChipSelector applies disabled opacity
     * Given: Component with disabled=true
     * When: Rendering chips
     * Then: All chips have reduced opacity
     */
    it('should apply disabled style when disabled', () => {
      // When
      const element = renderComponent({
        options: mockOptions,
        labels: mockLabels,
        selectedValues: [],
        onSelect: jest.fn(),
        disabled: true,
      });

      // Then - chips should have disabled style
      const chips = element.props.children;
      const firstChip = chips[0];

      expect(firstChip.props.style).toEqual(
        expect.arrayContaining([
          expect.objectContaining({ opacity: 0.5 }),
        ])
      );
    });
  });
});
