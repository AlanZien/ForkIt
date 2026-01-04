/**
 * Tests for SectionCard Component
 *
 * Unit tests for section card rendering (Task Group 5)
 * These tests mock React Native to focus on component logic
 */

import React from 'react';

// Mock react-native before importing component
jest.mock('react-native', () => ({
  View: 'View',
  Text: 'Text',
  StyleSheet: {
    create: (styles: any) => styles,
  },
}));

// Mock theme constants
jest.mock('../../../constants/theme', () => ({
  colors: {
    card: '#FFFFFF',
    foreground: '#1F2937',
    primary: '#14B8A6',
    primaryForeground: '#FFFFFF',
  },
  borderRadius: {
    lg: 16,
    sm: 12,
  },
  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
  },
  shadows: {
    card: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 4 },
      shadowOpacity: 0.07,
      shadowRadius: 6,
      elevation: 3,
    },
  },
}));

import { SectionCard } from '../../../components/preferences/SectionCard';

// Helper to render component
const renderComponent = (props: Parameters<typeof SectionCard>[0]) => {
  const element = SectionCard(props as any);
  return element;
};

describe('SectionCard', () => {
  describe('Rendering', () => {
    /**
     * Test: SectionCard displays title
     * Given: Title prop
     * When: Component renders
     * Then: Title is present in output
     */
    it('should display the title', () => {
      // Given
      const title = 'Regimes alimentaires';

      // When
      const element = renderComponent({
        title,
        children: React.createElement('View'),
      });

      // Then - find the title in header
      const header = element.props.children[0];
      const titleElement = header.props.children[0];
      expect(titleElement.props.children).toBe(title);
    });

    /**
     * Test: SectionCard renders children
     * Given: Children content
     * When: Component renders
     * Then: Children are present in content area
     */
    it('should render children in content area', () => {
      // Given
      const childContent = 'Test content';

      // When
      const element = renderComponent({
        title: 'Test',
        children: React.createElement('Text', {}, childContent),
      });

      // Then - find content in second child
      const content = element.props.children[1];
      expect(content.props.children.props.children).toBe(childContent);
    });

    /**
     * Test: SectionCard has correct border radius
     * Given: Component renders
     * When: Looking at styles
     * Then: Has 16px border radius
     */
    it('should have card styling with 16px border radius', () => {
      // When
      const element = renderComponent({
        title: 'Test',
        children: React.createElement('View'),
      });

      // Then - check container style
      const containerStyle = element.props.style[0];
      expect(containerStyle.borderRadius).toBe(16);
    });
  });

  describe('Editable state', () => {
    /**
     * Test: SectionCard shows editable indicator when editable
     * Given: editable=true
     * When: Component renders
     * Then: Has editable testID and border styling
     */
    it('should use editable testID when editable', () => {
      // When
      const element = renderComponent({
        title: 'Test',
        children: React.createElement('View'),
        editable: true,
      });

      // Then
      expect(element.props.testID).toBe('section-card-editable');
    });

    /**
     * Test: SectionCard shows edit indicator in header
     * Given: editable=true
     * When: Component renders
     * Then: Edit indicator is present in header
     */
    it('should show edit indicator in header when editable', () => {
      // When
      const element = renderComponent({
        title: 'Test',
        children: React.createElement('View'),
        editable: true,
      });

      // Then - header should have edit indicator as second child
      const header = element.props.children[0];
      const editIndicator = header.props.children[1];
      expect(editIndicator).toBeTruthy();
      // Check it has the "En edition" text
      const editText = editIndicator.props.children;
      expect(editText.props.children).toBe('En edition');
    });

    /**
     * Test: SectionCard does not show editable indicator when not editable
     * Given: editable=false (default)
     * When: Component renders
     * Then: No editable testID
     */
    it('should not use editable testID when not editable', () => {
      // When
      const element = renderComponent({
        title: 'Test',
        children: React.createElement('View'),
        testID: 'section-card',
      });

      // Then
      expect(element.props.testID).toBe('section-card');
    });

    /**
     * Test: SectionCard has border when editable
     * Given: editable=true
     * When: Looking at styles
     * Then: Has primary color border
     */
    it('should have border styling when editable', () => {
      // When
      const element = renderComponent({
        title: 'Test',
        children: React.createElement('View'),
        editable: true,
      });

      // Then - check for editable style in style array
      const styles = element.props.style;
      expect(styles).toEqual(
        expect.arrayContaining([
          expect.objectContaining({
            borderWidth: 2,
            borderColor: '#14B8A6',
          }),
        ])
      );
    });
  });
});
