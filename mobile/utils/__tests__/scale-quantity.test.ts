/**
 * Tests for scale-quantity utility functions
 */

import { parseQuantity, formatQuantity, scaleQuantity } from '../scale-quantity';

describe('parseQuantity', () => {
  describe('fractions', () => {
    it('parses "1/2" as 0.5', () => {
      const result = parseQuantity('1/2');
      expect(result.value).toBe(0.5);
      expect(result.unit).toBe('');
    });

    it('parses "1/4" as 0.25', () => {
      const result = parseQuantity('1/4');
      expect(result.value).toBe(0.25);
      expect(result.unit).toBe('');
    });

    it('parses "3/4" as 0.75', () => {
      const result = parseQuantity('3/4');
      expect(result.value).toBe(0.75);
      expect(result.unit).toBe('');
    });

    it('parses "1/2 cup" as 0.5 with unit "cup"', () => {
      const result = parseQuantity('1/2 cup');
      expect(result.value).toBe(0.5);
      expect(result.unit).toBe('cup');
    });
  });

  describe('mixed numbers', () => {
    it('parses "1 1/2" as 1.5', () => {
      const result = parseQuantity('1 1/2');
      expect(result.value).toBe(1.5);
      expect(result.unit).toBe('');
    });

    it('parses "2 1/4" as 2.25', () => {
      const result = parseQuantity('2 1/4');
      expect(result.value).toBe(2.25);
      expect(result.unit).toBe('');
    });

    it('parses "1 1/2 cups" as 1.5 with unit "cups"', () => {
      const result = parseQuantity('1 1/2 cups');
      expect(result.value).toBe(1.5);
      expect(result.unit).toBe('cups');
    });
  });

  describe('decimals with units', () => {
    it('parses "200g" as 200 with unit "g"', () => {
      const result = parseQuantity('200g');
      expect(result.value).toBe(200);
      expect(result.unit).toBe('g');
    });

    it('parses "2 cups" as 2 with unit "cups"', () => {
      const result = parseQuantity('2 cups');
      expect(result.value).toBe(2);
      expect(result.unit).toBe('cups');
    });

    it('parses "1.5 tbsp" as 1.5 with unit "tbsp"', () => {
      const result = parseQuantity('1.5 tbsp');
      expect(result.value).toBe(1.5);
      expect(result.unit).toBe('tbsp');
    });

    it('parses "100ml" as 100 with unit "ml"', () => {
      const result = parseQuantity('100ml');
      expect(result.value).toBe(100);
      expect(result.unit).toBe('ml');
    });
  });

  describe('plain numbers', () => {
    it('parses "2" as 2 with no unit', () => {
      const result = parseQuantity('2');
      expect(result.value).toBe(2);
      expect(result.unit).toBe('');
    });

    it('parses "1.5" as 1.5 with no unit', () => {
      const result = parseQuantity('1.5');
      expect(result.value).toBe(1.5);
      expect(result.unit).toBe('');
    });
  });

  describe('non-parseable values', () => {
    it('returns null value for "pinch"', () => {
      const result = parseQuantity('pinch');
      expect(result.value).toBeNull();
      expect(result.unit).toBe('pinch');
    });

    it('returns null value for "to taste"', () => {
      const result = parseQuantity('to taste');
      expect(result.value).toBeNull();
      expect(result.unit).toBe('to taste');
    });

    it('returns null value for empty string', () => {
      const result = parseQuantity('');
      expect(result.value).toBeNull();
      expect(result.unit).toBe('');
    });
  });
});

describe('formatQuantity', () => {
  it('formats whole numbers as integers', () => {
    expect(formatQuantity(2, '')).toBe('2');
    expect(formatQuantity(10, 'cups')).toBe('10 cups');
  });

  it('formats decimals with 1 decimal place', () => {
    expect(formatQuantity(1.5, '')).toBe('1.5');
    expect(formatQuantity(2.75, 'tbsp')).toBe('2.8 tbsp');
  });

  it('appends unit with space when present', () => {
    expect(formatQuantity(200, 'g')).toBe('200 g');
    expect(formatQuantity(3, 'cups')).toBe('3 cups');
  });

  it('returns just value when unit is empty', () => {
    expect(formatQuantity(4, '')).toBe('4');
    expect(formatQuantity(1.5, '')).toBe('1.5');
  });
});

describe('scaleQuantity', () => {
  describe('no scaling (portions = 1)', () => {
    it('returns original measure when portions is 1', () => {
      expect(scaleQuantity('200g', 1)).toBe('200g');
      expect(scaleQuantity('1/2 cup', 1)).toBe('1/2 cup');
    });

    it('returns original measure when portions is 0', () => {
      expect(scaleQuantity('100ml', 0)).toBe('100ml');
    });
  });

  describe('scaling fractions', () => {
    it('scales "1/2 cup" by 2 to "1 cup"', () => {
      expect(scaleQuantity('1/2 cup', 2)).toBe('1 cup');
    });

    it('scales "1/4" by 4 to "1"', () => {
      expect(scaleQuantity('1/4', 4)).toBe('1');
    });

    it('scales "3/4 cup" by 2 to "1.5 cup"', () => {
      expect(scaleQuantity('3/4 cup', 2)).toBe('1.5 cup');
    });
  });

  describe('scaling mixed numbers', () => {
    it('scales "1 1/2 cups" by 2 to "3 cups"', () => {
      expect(scaleQuantity('1 1/2 cups', 2)).toBe('3 cups');
    });

    it('scales "2 1/4 tbsp" by 2 to "4.5 tbsp"', () => {
      expect(scaleQuantity('2 1/4 tbsp', 2)).toBe('4.5 tbsp');
    });
  });

  describe('scaling decimals with units', () => {
    it('scales "200g" by 2 to "400 g"', () => {
      expect(scaleQuantity('200g', 2)).toBe('400 g');
    });

    it('scales "2 cups" by 3 to "6 cups"', () => {
      expect(scaleQuantity('2 cups', 3)).toBe('6 cups');
    });

    it('scales "1.5 tbsp" by 2 to "3 tbsp"', () => {
      expect(scaleQuantity('1.5 tbsp', 2)).toBe('3 tbsp');
    });

    it('scales "100ml" by 4 to "400 ml"', () => {
      expect(scaleQuantity('100ml', 4)).toBe('400 ml');
    });
  });

  describe('non-parseable measures', () => {
    it('returns "pinch" unchanged', () => {
      expect(scaleQuantity('pinch', 2)).toBe('pinch');
    });

    it('returns "to taste" unchanged', () => {
      expect(scaleQuantity('to taste', 4)).toBe('to taste');
    });

    it('returns empty string unchanged', () => {
      expect(scaleQuantity('', 2)).toBe('');
    });
  });
});
