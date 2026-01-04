# React Native Mobile Standards - ForkIt

**Version**: 1.0 | **Stack**: React Native + Expo + TypeScript | **Token-Optimized**

## Architecture

### Project Structure
```
mobile/
├── app/                     # Expo Router (file-based routing)
│   ├── (auth)/
│   │   ├── login.tsx
│   │   └── signup.tsx
│   ├── (tabs)/              # Bottom tab navigation
│   │   ├── _layout.tsx
│   │   ├── index.tsx        # Recipes feed
│   │   ├── favorites.tsx
│   │   └── profile.tsx
│   ├── recipe/
│   │   └── [id].tsx         # Recipe detail (dynamic route)
│   ├── _layout.tsx          # Root layout
│   └── +not-found.tsx
├── components/
│   ├── ui/                  # Reusable UI components
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   └── Card.tsx
│   ├── RecipeCard.tsx
│   └── RecipeList.tsx
├── hooks/
│   ├── useAuth.ts
│   ├── useRecipes.ts
│   └── useSupabase.ts
├── services/
│   ├── api.ts               # API client (Axios)
│   ├── auth.ts              # Auth logic
│   └── storage.ts           # AsyncStorage
├── store/                   # Zustand state management
│   ├── authStore.ts
│   └── recipesStore.ts
├── types/
│   ├── index.ts
│   ├── recipe.ts
│   └── user.ts
├── utils/
│   ├── constants.ts
│   └── validators.ts
├── app.json
├── package.json
└── tsconfig.json
```

### Dependencies
```json
{
  "dependencies": {
    "expo": "~50.0.0",
    "expo-router": "~3.4.0",
    "react": "18.2.0",
    "react-native": "0.73.0",
    "react-native-safe-area-context": "4.8.0",
    "react-native-screens": "~3.29.0",
    "@supabase/supabase-js": "^2.39.0",
    "@react-native-async-storage/async-storage": "1.21.0",
    "zustand": "^4.4.7",
    "axios": "^1.6.5",
    "react-hook-form": "^7.49.3",
    "zod": "^3.22.4"
  },
  "devDependencies": {
    "@types/react": "~18.2.45",
    "typescript": "^5.3.3"
  }
}
```

## Core Patterns

### 1. Expo Router (File-Based Routing)
```tsx
// app/_layout.tsx - Root Layout
import { Stack } from 'expo-router';
import { AuthProvider } from '@/hooks/useAuth';

export default function RootLayout() {
  return (
    <AuthProvider>
      <Stack>
        <Stack.Screen name="(auth)" options={{ headerShown: false }} />
        <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
      </Stack>
    </AuthProvider>
  );
}

// app/(tabs)/_layout.tsx - Tab Layout
import { Tabs } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';

export default function TabLayout() {
  return (
    <Tabs screenOptions={{ tabBarActiveTintColor: '#FF6B6B' }}>
      <Tabs.Screen
        name="index"
        options={{
          title: 'Recipes',
          tabBarIcon: ({ color }) => <Ionicons name="restaurant" size={24} color={color} />
        }}
      />
      <Tabs.Screen
        name="favorites"
        options={{
          title: 'Favorites',
          tabBarIcon: ({ color }) => <Ionicons name="heart" size={24} color={color} />
        }}
      />
    </Tabs>
  );
}
```

### 2. TypeScript Types
```typescript
// types/recipe.ts
export interface Recipe {
  id: string;
  title: string;
  description?: string;
  ingredients: string[];
  steps: string[];
  user_id: string;
  created_at: string;
  updated_at: string;
}

export type RecipeCreate = Omit<Recipe, 'id' | 'user_id' | 'created_at' | 'updated_at'>;

// types/user.ts
export interface User {
  id: string;
  email: string;
  display_name?: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
}
```

### 3. Zustand State Management
```typescript
// store/authStore.ts
import { create } from 'zustand';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { User } from '@/types';

interface AuthStore {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  setUser: (user: User | null) => void;
  setToken: (token: string | null) => Promise<void>;
  logout: () => Promise<void>;
}

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  token: null,
  isLoading: true,

  setUser: (user) => set({ user }),

  setToken: async (token) => {
    if (token) {
      await AsyncStorage.setItem('auth_token', token);
    } else {
      await AsyncStorage.removeItem('auth_token');
    }
    set({ token });
  },

  logout: async () => {
    await AsyncStorage.removeItem('auth_token');
    set({ user: null, token: null });
  },
}));

// store/recipesStore.ts
import { create } from 'zustand';
import { Recipe } from '@/types';

interface RecipesStore {
  recipes: Recipe[];
  setRecipes: (recipes: Recipe[]) => void;
  addRecipe: (recipe: Recipe) => void;
}

export const useRecipesStore = create<RecipesStore>((set) => ({
  recipes: [],
  setRecipes: (recipes) => set({ recipes }),
  addRecipe: (recipe) => set((state) => ({ recipes: [recipe, ...state.recipes] })),
}));
```

### 4. API Client
```typescript
// services/api.ts
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { API_URL } from '@/utils/constants';

const api = axios.create({
  baseURL: API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - Add auth token
api.interceptors.request.use(async (config) => {
  const token = await AsyncStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor - Handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized - logout user
      AsyncStorage.removeItem('auth_token');
    }
    return Promise.reject(error);
  }
);

export default api;

// services/auth.ts
import api from './api';
import { User } from '@/types';

export const authService = {
  login: async (email: string, password: string) => {
    const { data } = await api.post<{ user: User; token: string }>('/api/auth/login', {
      email,
      password,
    });
    return data;
  },

  register: async (email: string, password: string) => {
    const { data } = await api.post<{ user: User; token: string }>('/api/auth/register', {
      email,
      password,
    });
    return data;
  },

  getProfile: async () => {
    const { data } = await api.get<User>('/api/auth/me');
    return data;
  },
};
```

### 5. Custom Hooks
```typescript
// hooks/useAuth.ts
import { useEffect } from 'react';
import { useAuthStore } from '@/store/authStore';
import { authService } from '@/services/auth';
import AsyncStorage from '@react-native-async-storage/async-storage';

export function useAuth() {
  const { user, token, setUser, setToken, logout } = useAuthStore();

  useEffect(() => {
    loadToken();
  }, []);

  const loadToken = async () => {
    try {
      const savedToken = await AsyncStorage.getItem('auth_token');
      if (savedToken) {
        await setToken(savedToken);
        const profile = await authService.getProfile();
        setUser(profile);
      }
    } catch (error) {
      console.error('Failed to load token:', error);
    }
  };

  const login = async (email: string, password: string) => {
    const { user, token } = await authService.login(email, password);
    await setToken(token);
    setUser(user);
  };

  return { user, token, login, logout };
}

// hooks/useRecipes.ts
import { useEffect } from 'react';
import { useRecipesStore } from '@/store/recipesStore';
import api from '@/services/api';
import { Recipe } from '@/types';

export function useRecipes() {
  const { recipes, setRecipes, addRecipe } = useRecipesStore();

  const fetchRecipes = async () => {
    const { data } = await api.get<Recipe[]>('/api/recipes');
    setRecipes(data);
  };

  const createRecipe = async (recipeData: Partial<Recipe>) => {
    const { data } = await api.post<Recipe>('/api/recipes', recipeData);
    addRecipe(data);
    return data;
  };

  useEffect(() => {
    fetchRecipes();
  }, []);

  return { recipes, fetchRecipes, createRecipe };
}
```

### 6. Reusable Components
```tsx
// components/ui/Button.tsx
import { Pressable, Text, StyleSheet, ActivityIndicator } from 'react-native';

interface ButtonProps {
  title: string;
  onPress: () => void;
  loading?: boolean;
  variant?: 'primary' | 'secondary';
}

export function Button({ title, onPress, loading, variant = 'primary' }: ButtonProps) {
  return (
    <Pressable
      style={[styles.button, variant === 'secondary' && styles.secondary]}
      onPress={onPress}
      disabled={loading}
    >
      {loading ? (
        <ActivityIndicator color="#fff" />
      ) : (
        <Text style={styles.text}>{title}</Text>
      )}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  button: {
    backgroundColor: '#FF6B6B',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  secondary: {
    backgroundColor: '#6B7280',
  },
  text: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});

// components/RecipeCard.tsx
import { View, Text, Image, StyleSheet, Pressable } from 'react-native';
import { useRouter } from 'expo-router';
import { Recipe } from '@/types';

interface RecipeCardProps {
  recipe: Recipe;
}

export function RecipeCard({ recipe }: RecipeCardProps) {
  const router = useRouter();

  return (
    <Pressable
      style={styles.card}
      onPress={() => router.push(`/recipe/${recipe.id}`)}
    >
      <Text style={styles.title}>{recipe.title}</Text>
      {recipe.description && (
        <Text style={styles.description} numberOfLines={2}>
          {recipe.description}
        </Text>
      )}
      <Text style={styles.ingredients}>
        {recipe.ingredients.length} ingredients
      </Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  title: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 8,
  },
  description: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 8,
  },
  ingredients: {
    fontSize: 12,
    color: '#9CA3AF',
  },
});
```

### 7. Form Validation
```typescript
// Example screen with form validation
import { View, TextInput, StyleSheet } from 'react-native';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/Button';

const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
});

type LoginForm = z.infer<typeof loginSchema>;

export default function LoginScreen() {
  const { control, handleSubmit, formState: { errors } } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = (data: LoginForm) => {
    console.log(data);
  };

  return (
    <View style={styles.container}>
      <Controller
        control={control}
        name="email"
        render={({ field: { onChange, value } }) => (
          <TextInput
            style={styles.input}
            placeholder="Email"
            value={value}
            onChangeText={onChange}
            keyboardType="email-address"
            autoCapitalize="none"
          />
        )}
      />
      {errors.email && <Text style={styles.error}>{errors.email.message}</Text>}

      <Button title="Login" onPress={handleSubmit(onSubmit)} />
    </View>
  );
}
```

## Code Quality Rules (OBLIGATOIRE)

### Avant de marquer une tâche comme complète :

**1. Strict TypeScript** - Zéro `any`, types explicites
```typescript
// ❌ Mauvais
const handleData = (data: any) => { ... }

// ✅ Bon
const handleData = (data: Recipe) => { ... }
```

**2. Return Types** - Fonctions avec types de retour explicites
```typescript
// ❌ Mauvais
const fetchRecipes = async () => {
  return await api.get('/recipes');
}

// ✅ Bon
const fetchRecipes = async (): Promise<Recipe[]> => {
  return await api.get('/recipes');
}
```

**3. Mocks pour Tests** - Créer les mocks nécessaires pour react-native/expo
```
mobile/__mocks__/
├── react-native.ts      # Platform, etc.
└── expo-secure-store.ts # Storage mocks
```

### Commandes de validation (exécuter AVANT commit)

```bash
# 1. TypeScript check - zéro erreur
npx tsc --noEmit

# 2. Tests - tous passent
npm test

# 3. (Optionnel) ESLint
npx expo lint
```

### Configuration requise

**tsconfig.json**
```json
{
  "extends": "expo/tsconfig.base",
  "compilerOptions": {
    "strict": true
  }
}
```

**.gitignore** (ajouter)
```
types/generated/
```

---

## Best Practices

1. **TypeScript First** - Always use types, avoid `any`
2. **File-Based Routing** - Use Expo Router for navigation
3. **State Management** - Zustand for global state, useState for local
4. **Component Composition** - Small, reusable components
5. **Hooks** - Extract logic into custom hooks
6. **Form Validation** - Use react-hook-form + zod
7. **Error Handling** - Try/catch in async functions, show user-friendly errors
8. **Performance** - Use React.memo, useMemo, useCallback for expensive operations
9. **Styling** - StyleSheet.create, avoid inline styles
10. **Accessibility** - Use accessibilityLabel, accessibilityHint

## Styling Conventions

```typescript
// Consistent spacing scale
const SPACING = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
};

// Color palette
const COLORS = {
  primary: '#FF6B6B',
  secondary: '#4ECDC4',
  text: '#1F2937',
  textLight: '#6B7280',
  background: '#F9FAFB',
  white: '#FFFFFF',
  error: '#EF4444',
};

// Typography
const TYPOGRAPHY = {
  h1: { fontSize: 32, fontWeight: '700' },
  h2: { fontSize: 24, fontWeight: '600' },
  body: { fontSize: 16, fontWeight: '400' },
  small: { fontSize: 14, fontWeight: '400' },
};
```

## Performance Tips

- Use `FlatList` for long lists (virtualized)
- Memoize expensive computations with `useMemo`
- Debounce search inputs
- Lazy load images
- Cache API responses
- Use Expo's hermes engine for faster startup

## Development

```bash
# Start development server
npx expo start

# Run on iOS simulator
npx expo run:ios

# Run on Android emulator
npx expo run:android

# Build for production
eas build --platform all
```

---

**Token Count**: ~1400 tokens | **Reusable for**: Maison Epigenetic
