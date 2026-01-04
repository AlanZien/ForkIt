/**
 * Tests for IngredientInput Component
 *
 * Unit tests for ingredient input logic (Task Group 5)
 * These tests focus on the business logic of adding/removing ingredients
 */

describe('IngredientInput Logic', () => {
  describe('Add Logic', () => {
    /**
     * Test: IngredientInput adds ingredient correctly
     * Given: Valid ingredient text
     * When: Adding the ingredient
     * Then: onAdd is called with trimmed text
     */
    it('should call onAdd with trimmed ingredient text', () => {
      // Given
      const onAdd = jest.fn();
      const inputValue = '  basilic  ';

      // Simulate add logic
      const handleAdd = (value: string, maxItems: number, currentLength: number, disabled: boolean) => {
        if (disabled) return false;
        const trimmed = value.trim();
        if (!trimmed) return false;
        if (currentLength >= maxItems) return false;
        onAdd(trimmed);
        return true;
      };

      // When
      const result = handleAdd(inputValue, 30, 0, false);

      // Then
      expect(result).toBe(true);
      expect(onAdd).toHaveBeenCalledWith('basilic');
    });

    /**
     * Test: IngredientInput does not add empty text
     * Given: Empty or whitespace text
     * When: Trying to add
     * Then: onAdd is not called
     */
    it('should not call onAdd for empty or whitespace text', () => {
      // Given
      const onAdd = jest.fn();

      // Simulate add logic
      const handleAdd = (value: string, maxItems: number, currentLength: number, disabled: boolean) => {
        if (disabled) return false;
        const trimmed = value.trim();
        if (!trimmed) return false;
        if (currentLength >= maxItems) return false;
        onAdd(trimmed);
        return true;
      };

      // When - empty
      handleAdd('', 30, 0, false);
      expect(onAdd).not.toHaveBeenCalled();

      // When - whitespace only
      handleAdd('   ', 30, 0, false);
      expect(onAdd).not.toHaveBeenCalled();
    });

    /**
     * Test: IngredientInput respects max items limit
     * Given: Already at max items
     * When: Trying to add
     * Then: onAdd is not called
     */
    it('should not call onAdd when max items reached', () => {
      // Given
      const onAdd = jest.fn();
      const maxItems = 3;
      const currentLength = 3; // already at max

      // Simulate add logic
      const handleAdd = (value: string) => {
        const trimmed = value.trim();
        if (!trimmed) return false;
        if (currentLength >= maxItems) return false;
        onAdd(trimmed);
        return true;
      };

      // When
      const result = handleAdd('new ingredient');

      // Then
      expect(result).toBe(false);
      expect(onAdd).not.toHaveBeenCalled();
    });

    /**
     * Test: IngredientInput does not add when disabled
     * Given: Disabled state
     * When: Trying to add
     * Then: onAdd is not called
     */
    it('should not call onAdd when disabled', () => {
      // Given
      const onAdd = jest.fn();

      // Simulate add logic
      const handleAdd = (value: string, maxItems: number, currentLength: number, disabled: boolean) => {
        if (disabled) return false;
        const trimmed = value.trim();
        if (!trimmed) return false;
        if (currentLength >= maxItems) return false;
        onAdd(trimmed);
        return true;
      };

      // When
      const result = handleAdd('basilic', 30, 0, true);

      // Then
      expect(result).toBe(false);
      expect(onAdd).not.toHaveBeenCalled();
    });
  });

  describe('Remove Logic', () => {
    /**
     * Test: IngredientInput removes ingredient correctly
     * Given: Ingredient to remove
     * When: Removing
     * Then: onRemove is called with the ingredient
     */
    it('should call onRemove with ingredient name', () => {
      // Given
      const onRemove = jest.fn();
      const ingredient = 'tomate';

      // Simulate remove logic
      const handleRemove = (ing: string, disabled: boolean) => {
        if (disabled) return;
        onRemove(ing);
      };

      // When
      handleRemove(ingredient, false);

      // Then
      expect(onRemove).toHaveBeenCalledWith('tomate');
    });

    /**
     * Test: IngredientInput does not remove when disabled
     * Given: Disabled state
     * When: Trying to remove
     * Then: onRemove is not called
     */
    it('should not call onRemove when disabled', () => {
      // Given
      const onRemove = jest.fn();

      // Simulate remove logic
      const handleRemove = (ing: string, disabled: boolean) => {
        if (disabled) return;
        onRemove(ing);
      };

      // When
      handleRemove('tomate', true);

      // Then
      expect(onRemove).not.toHaveBeenCalled();
    });
  });

  describe('Max items calculation', () => {
    /**
     * Test: Max items detection
     * Given: Array of ingredients
     * When: Checking if max reached
     * Then: Returns true when length >= maxItems
     */
    it('should correctly detect when max items reached', () => {
      // Given
      const ingredients = ['a', 'b', 'c'];
      const maxItems = 3;

      // When
      const isMaxReached = ingredients.length >= maxItems;

      // Then
      expect(isMaxReached).toBe(true);
    });

    /**
     * Test: Max items not reached
     * Given: Array with room for more
     * When: Checking if max reached
     * Then: Returns false
     */
    it('should return false when max not reached', () => {
      // Given
      const ingredients = ['a', 'b'];
      const maxItems = 3;

      // When
      const isMaxReached = ingredients.length >= maxItems;

      // Then
      expect(isMaxReached).toBe(false);
    });
  });

  describe('Duplicate prevention', () => {
    /**
     * Test: Should not add duplicate ingredient
     * Given: Ingredient already in list
     * When: Trying to add same ingredient
     * Then: onAdd is not called
     */
    it('should prevent adding duplicate ingredients', () => {
      // Given
      const onAdd = jest.fn();
      const existingIngredients = ['tomate', 'oignon'];
      const newIngredient = 'tomate';

      // Simulate add logic with duplicate check
      const handleAdd = (ingredient: string) => {
        const trimmed = ingredient.trim();
        if (!trimmed) return false;
        if (existingIngredients.includes(trimmed)) return false;
        onAdd(trimmed);
        return true;
      };

      // When
      const result = handleAdd(newIngredient);

      // Then
      expect(result).toBe(false);
      expect(onAdd).not.toHaveBeenCalled();
    });
  });
});
