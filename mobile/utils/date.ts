/**
 * Date Utilities for Meal Planning
 *
 * Helper functions for week-based date operations with French locale support.
 */

/**
 * French day names (Monday = 0, Sunday = 6)
 */
const FRENCH_DAY_NAMES = [
  'Lundi',
  'Mardi',
  'Mercredi',
  'Jeudi',
  'Vendredi',
  'Samedi',
  'Dimanche',
];

/**
 * French month names (abbreviated)
 */
const FRENCH_MONTH_NAMES = [
  'Jan',
  'Fev',
  'Mar',
  'Avr',
  'Mai',
  'Juin',
  'Juil',
  'Aou',
  'Sep',
  'Oct',
  'Nov',
  'Dec',
];

/**
 * Get Monday of the week for a given date
 * @param date - Any date within the week
 * @returns Date object set to Monday 00:00:00 of that week
 */
export function getWeekStart(date: Date): Date {
  const result = new Date(date);
  const day = result.getDay();
  // Sunday is 0, we need to go back 6 days; Monday is 1, go back 0 days, etc.
  const diff = day === 0 ? -6 : 1 - day;
  result.setDate(result.getDate() + diff);
  result.setHours(0, 0, 0, 0);
  return result;
}

/**
 * Get Sunday of the week for a given date
 * @param date - Any date within the week
 * @returns Date object set to Sunday 23:59:59 of that week
 */
export function getWeekEnd(date: Date): Date {
  const monday = getWeekStart(date);
  const result = new Date(monday);
  result.setDate(monday.getDate() + 6);
  result.setHours(23, 59, 59, 999);
  return result;
}

/**
 * Format date as ISO string (YYYY-MM-DD)
 * @param date - Date to format
 * @returns ISO date string
 */
export function formatDateISO(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

/**
 * Parse ISO date string to Date object
 * @param dateStr - ISO date string (YYYY-MM-DD)
 * @returns Date object at midnight local time
 */
export function parseISO(dateStr: string): Date {
  const [year, month, day] = dateStr.split('-').map(Number);
  return new Date(year, month - 1, day);
}

/**
 * Add or subtract weeks from a date
 * @param date - Starting date
 * @param weeks - Number of weeks to add (negative to subtract)
 * @returns New date with weeks added
 */
export function addWeeks(date: Date, weeks: number): Date {
  const result = new Date(date);
  result.setDate(result.getDate() + weeks * 7);
  return result;
}

/**
 * Check if a week start date is the current week
 * @param weekStart - ISO date string of week start (Monday)
 * @returns true if this is the current week
 */
export function isCurrentWeek(weekStart: string): boolean {
  const today = new Date();
  const currentWeekStart = getWeekStart(today);
  const targetWeekStart = parseISO(weekStart);
  return formatDateISO(currentWeekStart) === formatDateISO(targetWeekStart);
}

/**
 * Check if a week start is within the allowed range
 * @param weekStart - ISO date string of week start (Monday)
 * @param maxWeeksAhead - Maximum weeks ahead from current week (default 4)
 * @returns true if within range (current week to maxWeeksAhead)
 */
export function isWithinRange(weekStart: string, maxWeeksAhead: number = 4): boolean {
  const today = new Date();
  const currentWeekStart = getWeekStart(today);
  const targetWeekStart = parseISO(weekStart);

  // Check not before current week
  if (targetWeekStart < currentWeekStart) {
    return false;
  }

  // Check not beyond max weeks ahead
  const maxDate = addWeeks(currentWeekStart, maxWeeksAhead);
  return targetWeekStart <= maxDate;
}

/**
 * Get French day name for a date
 * @param date - Date object
 * @returns French day name (Lundi, Mardi, etc.)
 */
export function getDayName(date: Date): string {
  const day = date.getDay();
  // Convert from Sunday=0 to Monday=0 index
  const index = day === 0 ? 6 : day - 1;
  return FRENCH_DAY_NAMES[index];
}

/**
 * Get short French day name (3 letters)
 * @param date - Date object
 * @returns Short French day name (Lun, Mar, etc.)
 */
export function getShortDayName(date: Date): string {
  return getDayName(date).slice(0, 3);
}

/**
 * Get French month name (abbreviated)
 * @param date - Date object
 * @returns Abbreviated French month name (Jan, Fev, etc.)
 */
export function getMonthName(date: Date): string {
  return FRENCH_MONTH_NAMES[date.getMonth()];
}

/**
 * Format date as "day month" (e.g., "3 Jan")
 * @param date - Date object
 * @returns Formatted date string
 */
export function formatDayMonth(date: Date): string {
  return `${date.getDate()} ${getMonthName(date)}`;
}

/**
 * Format week label for navigation header
 * @param weekStart - ISO date string of week start (Monday)
 * @returns French label like "Semaine du 6 Jan"
 */
export function formatWeekLabel(weekStart: string): string {
  const date = parseISO(weekStart);
  return `Semaine du ${date.getDate()} ${getMonthName(date)}`;
}

/**
 * Get all dates in a week starting from Monday
 * @param weekStart - Date object for Monday of the week
 * @returns Array of 7 Date objects (Monday to Sunday)
 */
export function getWeekDates(weekStart: Date): Date[] {
  const dates: Date[] = [];
  for (let i = 0; i < 7; i++) {
    const date = new Date(weekStart);
    date.setDate(weekStart.getDate() + i);
    dates.push(date);
  }
  return dates;
}

/**
 * Get 7 dates starting from today
 * @returns Array of 7 Date objects starting from today
 */
export function getDatesFromToday(): Date[] {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const dates: Date[] = [];
  for (let i = 0; i < 7; i++) {
    const date = new Date(today);
    date.setDate(today.getDate() + i);
    dates.push(date);
  }
  return dates;
}

/**
 * Check if a date is today
 * @param date - Date to check
 * @returns true if date is today
 */
export function isToday(date: Date): boolean {
  const today = new Date();
  return (
    date.getDate() === today.getDate() &&
    date.getMonth() === today.getMonth() &&
    date.getFullYear() === today.getFullYear()
  );
}

/**
 * Generate slot key for Map storage
 * @param date - ISO date string (YYYY-MM-DD)
 * @param mealType - 'dejeuner' or 'diner'
 * @returns Key string like "2024-01-15_dejeuner"
 */
export function generateSlotKey(date: string, mealType: string): string {
  return `${date}_${mealType}`;
}

/**
 * Parse slot key back to date and mealType
 * @param key - Key string like "2024-01-15_dejeuner"
 * @returns Object with date and mealType
 */
export function parseSlotKey(key: string): { date: string; mealType: string } {
  const [date, mealType] = key.split('_');
  return { date, mealType };
}
