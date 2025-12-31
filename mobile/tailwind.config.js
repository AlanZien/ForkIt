/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./App.{js,jsx,ts,tsx}", "./app/**/*.{js,jsx,ts,tsx}", "./components/**/*.{js,jsx,ts,tsx}"],
  presets: [require("nativewind/preset")],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#14B8A6',
          foreground: '#FFFFFF',
        },
        secondary: {
          DEFAULT: '#FF8A65',
          foreground: '#FFFFFF',
        },
        accent: {
          DEFAULT: '#FEF3C7',
          foreground: '#92400E',
        },
        destructive: {
          DEFAULT: '#EF4444',
          foreground: '#FFFFFF',
        },
        success: '#22C55E',
        warning: '#F59E0B',
        background: '#FAFBFC',
        foreground: '#1F2937',
        card: {
          DEFAULT: '#FFFFFF',
          foreground: '#1F2937',
        },
        muted: {
          DEFAULT: '#F3F4F6',
          foreground: '#6B7280',
        },
        border: 'rgba(0, 0, 0, 0.08)',
        input: '#F9FAFB',
      },
      borderRadius: {
        sm: '12px',
        md: '14px',
        lg: '16px',
        xl: '20px',
      },
      spacing: {
        xs: '4px',
        sm: '8px',
        md: '16px',
        lg: '24px',
        xl: '32px',
        '2xl': '48px',
      },
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
