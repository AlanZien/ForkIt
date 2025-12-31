# Design System - ForkIt

## Palette de Couleurs

### Couleurs Primaires
- **Primary**: `#14B8A6` (Teal) - Boutons principaux, liens, elements d'accent
- **Primary Foreground**: `#FFFFFF` - Texte sur fond primary

### Couleurs Secondaires
- **Secondary**: `#FF8A65` (Coral/Orange) - Boutons secondaires, accents chaleureux
- **Secondary Foreground**: `#FFFFFF` - Texte sur fond secondary

### Couleurs d'Accent
- **Accent**: `#FEF3C7` (Warm Yellow) - Highlights, badges, notifications
- **Accent Foreground**: `#92400E` - Texte sur fond accent

### Couleurs d'Etat
- **Destructive**: `#EF4444` - Erreurs, suppressions, alertes critiques
- **Destructive Foreground**: `#FFFFFF` - Texte sur fond destructive
- **Success**: `#22C55E` - Validations, confirmations (derive du primary)
- **Warning**: `#F59E0B` - Avertissements (derive de l'accent)

### Couleurs Neutres
- **Background**: `#FAFBFC` - Fond principal de l'application
- **Foreground**: `#1F2937` - Texte principal
- **Card**: `#FFFFFF` - Fond des cartes et surfaces elevees
- **Card Foreground**: `#1F2937` - Texte sur cartes
- **Muted**: `#F3F4F6` - Fonds secondaires, zones inactives
- **Muted Foreground**: `#6B7280` - Texte secondaire, placeholders
- **Border**: `rgba(0, 0, 0, 0.08)` - Bordures subtiles
- **Input Background**: `#F9FAFB` - Fond des champs de saisie
- **Switch Background**: `#D1D5DB` - Fond des switches inactifs

### Mode Sombre (Dark Mode)
- **Background**: `#111827`
- **Foreground**: `#F9FAFB`
- **Card**: `#1F2937`
- **Muted**: `#374151`
- **Muted Foreground**: `#9CA3AF`
- **Border**: `rgba(255, 255, 255, 0.1)`

## Typographie

### Polices
- **Font Family**: System fonts stack
  ```
  -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
  'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif
  ```
- **Base Size**: 16px (1rem)

### Tailles de Police

| Element | Taille | Poids | Line Height | Letter Spacing |
|---------|--------|-------|-------------|----------------|
| H1 | 1.875rem (30px) | 700 | 1.3 | -0.02em |
| H2 | 1.5rem (24px) | 600 | 1.4 | -0.01em |
| H3 | 1.25rem (20px) | 600 | 1.4 | - |
| H4 | 1rem (16px) | 600 | 1.5 | - |
| Body | 1rem (16px) | 400 | 1.6 | - |
| Label | 0.875rem (14px) | 500 | 1.5 | - |
| Button | 1rem (16px) | 500 | 1.5 | - |
| Input | 1rem (16px) | 400 | 1.5 | - |

### Poids de Police
- **Normal**: 400 - Texte courant
- **Medium**: 500 - Labels, boutons
- **Semibold**: 600 - Sous-titres, H2-H4
- **Bold**: 700 - Titres H1

## Spacing & Layout

### Systeme de Spacing (base 4px)
| Token | Valeur | Usage |
|-------|--------|-------|
| xs | 4px (0.25rem) | Micro-espacements |
| sm | 8px (0.5rem) | Espacements internes compacts |
| md | 16px (1rem) | Espacements standards |
| lg | 24px (1.5rem) | Espacements entre sections |
| xl | 32px (2rem) | Grands espacements |
| 2xl | 48px (3rem) | Espacements majeurs |

### Border Radius
| Token | Valeur | Usage |
|-------|--------|-------|
| sm | 12px (radius - 4px) | Petits elements, badges |
| md | 14px (radius - 2px) | Inputs, petits boutons |
| lg | 16px (1rem) | Cartes, boutons principaux |
| xl | 20px (radius + 4px) | Modals, grandes cartes |
| full | 9999px | Avatars, boutons ronds |

## Shadows

- **Subtle**: `0 1px 2px rgba(0, 0, 0, 0.05)` - Elevation legere
- **Card**: `0 4px 6px rgba(0, 0, 0, 0.07)` - Cartes de recettes
- **Modal**: `0 10px 25px rgba(0, 0, 0, 0.15)` - Modals, popovers
- **Button Hover**: `0 4px 12px rgba(20, 184, 166, 0.3)` - Boutons primary au hover

## Composants Globaux

### Buttons

**Primary Button**
- Background: `#14B8A6`
- Text: `#FFFFFF`
- Height: 48px (touch-friendly)
- Padding: 16px horizontal
- Border Radius: 16px (lg)
- Font: 16px / 500

**Secondary Button**
- Background: `#FF8A65`
- Text: `#FFFFFF`
- Memes dimensions que primary

**Outline Button**
- Background: transparent
- Border: 1px solid `#14B8A6`
- Text: `#14B8A6`

**Ghost Button**
- Background: transparent
- Text: `#14B8A6`

### Inputs

- Height: 48px minimum (touch-friendly)
- Background: `#F9FAFB`
- Border: 1px solid `rgba(0, 0, 0, 0.08)`
- Border Radius: 14px (md)
- Padding: 12px 16px
- Focus: Border `#14B8A6`, ring shadow

### Cards

**Recipe Card**
- Background: `#FFFFFF`
- Border Radius: 16px (lg)
- Shadow: Card shadow
- Padding: 0 (image full-bleed) + 12px (content)
- Image: aspect-ratio 16:10, border-radius top 16px

**Planning Card**
- Background: `#FFFFFF`
- Border: 1px solid `rgba(0, 0, 0, 0.08)`
- Border Radius: 12px (sm)
- Padding: 12px

### Chips / Tags

**Preference Chips** (dietary, allergies)
- Background inactive: `#F3F4F6`
- Background active: `#14B8A6`
- Text inactive: `#1F2937`
- Text active: `#FFFFFF`
- Border Radius: 20px
- Padding: 8px 16px
- Height: 36px

### Bottom Navigation

- Background: `#FFFFFF`
- Height: 64px + safe area
- Icons: 24px
- Active color: `#14B8A6`
- Inactive color: `#6B7280`
- 5 tabs: Accueil, Recettes, Planning, Courses, Profil

## Elements Decoratifs

### Blobs (arriere-plans)
```css
.bg-blob-teal {
  background: radial-gradient(circle at center, rgba(20, 184, 166, 0.15) 0%, transparent 70%);
}

.bg-blob-orange {
  background: radial-gradient(circle at center, rgba(255, 138, 101, 0.15) 0%, transparent 70%);
}

.bg-blob-yellow {
  background: radial-gradient(circle at center, rgba(251, 191, 36, 0.15) 0%, transparent 70%);
}
```

### Icones
- Style: Outline / Line icons
- Taille standard: 24px
- Taille petite: 20px
- Taille grande: 32px
- Library recommandee: Lucide Icons ou Phosphor Icons

## Design Tokens (React Native)

```typescript
export const colors = {
  primary: '#14B8A6',
  primaryForeground: '#FFFFFF',
  secondary: '#FF8A65',
  secondaryForeground: '#FFFFFF',
  accent: '#FEF3C7',
  accentForeground: '#92400E',
  destructive: '#EF4444',
  background: '#FAFBFC',
  foreground: '#1F2937',
  card: '#FFFFFF',
  cardForeground: '#1F2937',
  muted: '#F3F4F6',
  mutedForeground: '#6B7280',
  border: 'rgba(0, 0, 0, 0.08)',
  inputBackground: '#F9FAFB',
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
  h1: { fontSize: 30, fontWeight: '700', lineHeight: 39 },
  h2: { fontSize: 24, fontWeight: '600', lineHeight: 34 },
  h3: { fontSize: 20, fontWeight: '600', lineHeight: 28 },
  h4: { fontSize: 16, fontWeight: '600', lineHeight: 24 },
  body: { fontSize: 16, fontWeight: '400', lineHeight: 26 },
  label: { fontSize: 14, fontWeight: '500', lineHeight: 21 },
  button: { fontSize: 16, fontWeight: '500', lineHeight: 24 },
} as const;
```

## Fichiers de Reference

**Design References** (situes dans `agent-os/product/design-references/`):
- `Image PNG.png` - Mockups complets de l'application (onboarding, auth, profil, home, recettes, planning, liste de courses)
- `globals.css` - Variables CSS avec tokens de design extraits

**Style Notes:**
- Design moderne, epure et chaleureux
- Palette teal/coral evoquant la fraicheur et la convivialite
- Coins arrondis genereux pour une sensation accueillante
- Photographie culinaire mise en avant sur les cartes de recettes
- Interface francophone, ton amical ("Bonjour, Cedric!")
- Navigation bottom tab a 5 elements pour acces rapide aux fonctions principales
