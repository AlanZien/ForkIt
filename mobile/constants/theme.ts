/**
 * ForkIt Design System Tokens
 * Auto-generated from design-system.md
 */

export const colors = {
  primary: '#14B8A6',
  primaryForeground: '#FFFFFF',
  secondary: '#FF8A65',
  secondaryForeground: '#FFFFFF',
  accent: '#FEF3C7',
  accentForeground: '#92400E',
  destructive: '#EF4444',
  destructiveForeground: '#FFFFFF',
  success: '#22C55E',
  warning: '#F59E0B',
  background: '#FAFBFC',
  foreground: '#1F2937',
  card: '#FFFFFF',
  cardForeground: '#1F2937',
  muted: '#F3F4F6',
  mutedForeground: '#6B7280',
  border: 'rgba(0, 0, 0, 0.08)',
  inputBackground: '#F9FAFB',
} as const;

export const darkColors = {
  background: '#111827',
  foreground: '#F9FAFB',
  card: '#1F2937',
  muted: '#374151',
  mutedForeground: '#9CA3AF',
  border: 'rgba(255, 255, 255, 0.1)',
} as const;

export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  '2xl': 48,
} as const;

export const borderRadius = {
  sm: 12,
  md: 14,
  lg: 16,
  xl: 20,
  full: 9999,
} as const;

export const typography = {
  h1: { fontSize: 30, fontWeight: '700' as const, lineHeight: 39 },
  h2: { fontSize: 24, fontWeight: '600' as const, lineHeight: 34 },
  h3: { fontSize: 20, fontWeight: '600' as const, lineHeight: 28 },
  h4: { fontSize: 16, fontWeight: '600' as const, lineHeight: 24 },
  body: { fontSize: 16, fontWeight: '400' as const, lineHeight: 26 },
  label: { fontSize: 14, fontWeight: '500' as const, lineHeight: 21 },
  button: { fontSize: 16, fontWeight: '500' as const, lineHeight: 24 },
} as const;

export const shadows = {
  subtle: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  card: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.07,
    shadowRadius: 6,
    elevation: 3,
  },
  modal: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.15,
    shadowRadius: 25,
    elevation: 10,
  },
} as const;
