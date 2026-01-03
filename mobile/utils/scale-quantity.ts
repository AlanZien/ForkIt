/**
 * Quantity Scaling Utilities
 *
 * Functions for parsing and scaling ingredient quantities.
 * Ported from backend/app/services/shopping_list_service.py
 */

/**
 * Parse a quantity string into numeric value and unit.
 *
 * Handles formats like:
 * - "2" -> { value: 2, unit: "" }
 * - "1.5" -> { value: 1.5, unit: "" }
 * - "1/2" -> { value: 0.5, unit: "" }
 * - "200g" -> { value: 200, unit: "g" }
 * - "2 cups" -> { value: 2, unit: "cups" }
 * - "1/2 cup" -> { value: 0.5, unit: "cup" }
 * - "1 1/2" -> { value: 1.5, unit: "" }
 * - "1 1/2 cups" -> { value: 1.5, unit: "cups" }
 *
 * @param measure - The measure string to parse
 * @returns Object with value (null if unparseable) and unit
 */
export function parseQuantity(measure: string): { value: number | null; unit: string } {
  if (!measure) {
    return { value: null, unit: '' };
  }

  const trimmed = measure.trim();

  // Handle fractions like "1/2", "1/4", "3/4"
  const fractionMatch = trimmed.match(/^(\d+)\/(\d+)\s*(.*)$/);
  if (fractionMatch) {
    const numerator = parseFloat(fractionMatch[1]);
    const denominator = parseFloat(fractionMatch[2]);
    if (denominator !== 0) {
      const value = numerator / denominator;
      const unit = fractionMatch[3].trim();
      return { value, unit };
    }
  }

  // Handle mixed numbers like "1 1/2", "2 1/4"
  const mixedMatch = trimmed.match(/^(\d+)\s+(\d+)\/(\d+)\s*(.*)$/);
  if (mixedMatch) {
    const whole = parseFloat(mixedMatch[1]);
    const numerator = parseFloat(mixedMatch[2]);
    const denominator = parseFloat(mixedMatch[3]);
    if (denominator !== 0) {
      const value = whole + numerator / denominator;
      const unit = mixedMatch[4].trim();
      return { value, unit };
    }
  }

  // Handle decimals with optional unit like "1.5", "200g", "2 cups"
  const decimalMatch = trimmed.match(/^(\d+(?:\.\d+)?)\s*(.*)$/);
  if (decimalMatch) {
    const value = parseFloat(decimalMatch[1]);
    const unit = decimalMatch[2].trim();
    return { value, unit };
  }

  // Cannot parse - return as unit only
  return { value: null, unit: trimmed };
}

/**
 * Format a quantity value and unit into a string.
 *
 * - Whole numbers displayed as integers (e.g., 2 not 2.0)
 * - Decimals displayed with 1 decimal place
 * - Unit appended with space if present
 *
 * @param value - Numeric value
 * @param unit - Unit string
 * @returns Formatted quantity string
 */
export function formatQuantity(value: number, unit: string): string {
  // Format value: use integer if whole number, else 1 decimal
  const valueStr = value === Math.floor(value) ? String(Math.floor(value)) : value.toFixed(1);

  if (unit) {
    return `${valueStr} ${unit}`;
  }
  return valueStr;
}

/**
 * Scale a quantity measure by the number of portions.
 *
 * Takes a measure string (e.g., "200g", "1/2 cup", "1 1/2 tbsp") and
 * multiplies the numeric portion by the specified portions count.
 *
 * If the measure cannot be parsed, returns the original measure unchanged.
 *
 * @param measure - Original measure string
 * @param portions - Number of portions to multiply by (1 = no change)
 * @returns Scaled quantity string
 */
export function scaleQuantity(measure: string, portions: number): string {
  // No scaling needed for 1 portion
  if (portions <= 1) {
    return measure;
  }

  const { value, unit } = parseQuantity(measure);

  if (value !== null) {
    return formatQuantity(value * portions, unit);
  }

  // Cannot parse - return original
  return measure;
}
