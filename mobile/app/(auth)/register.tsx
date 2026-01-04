/**
 * Register Screen
 *
 * User registration with name, email, password and confirmation
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  Alert,
} from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Input, Button, BackButton } from '../../components/ui';
import { useAuthStore } from '../../stores/auth';

export default function RegisterScreen() {
  const router = useRouter();
  const register = useAuthStore((state) => state.register);
  const isLoading = useAuthStore((state) => state.isLoading);

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [errors, setErrors] = useState<{
    name?: string;
    email?: string;
    password?: string;
    confirmPassword?: string;
  }>({});

  const validate = (): boolean => {
    const newErrors: typeof errors = {};

    if (!name.trim()) {
      newErrors.name = 'Nom requis';
    }

    if (!email) {
      newErrors.email = 'Email requis';
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      newErrors.email = 'Email invalide';
    }

    if (!password) {
      newErrors.password = 'Mot de passe requis';
    } else if (password.length < 8) {
      newErrors.password = 'Minimum 8 caractères';
    }

    if (!confirmPassword) {
      newErrors.confirmPassword = 'Confirmation requise';
    } else if (password !== confirmPassword) {
      newErrors.confirmPassword = 'Les mots de passe ne correspondent pas';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleRegister = async () => {
    if (!validate()) return;

    try {
      await register(name.trim(), email, password);
      router.replace({
        pathname: '/(auth)/verify-email',
        params: { email },
      });
    } catch (error: any) {
      Alert.alert(
        'Erreur',
        'Impossible de créer le compte. Veuillez réessayer.'
      );
    }
  };

  const handleLogin = () => {
    router.push('/(auth)/login');
  };

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardView}
      >
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          keyboardShouldPersistTaps="handled"
        >
          <BackButton />

          <View style={styles.header}>
            <Text style={styles.title}>Créer un compte</Text>
            <Text style={styles.subtitle}>
              Rejoignez ForkIt gratuitement
            </Text>
          </View>

          <View style={styles.form}>
            <Input
              label="Nom"
              placeholder="Votre nom"
              value={name}
              onChangeText={setName}
              autoCapitalize="words"
              autoComplete="name"
              error={errors.name}
            />

            <Input
              label="Email"
              placeholder="votre@email.com"
              value={email}
              onChangeText={setEmail}
              keyboardType="email-address"
              autoCapitalize="none"
              autoComplete="email"
              error={errors.email}
            />

            <Input
              label="Mot de passe"
              placeholder="Votre mot de passe"
              value={password}
              onChangeText={setPassword}
              secureTextEntry
              autoComplete="new-password"
              error={errors.password}
              hint="Minimum 8 caractères"
            />

            <Input
              label="Confirmer le mot de passe"
              placeholder="Confirmez votre mot de passe"
              value={confirmPassword}
              onChangeText={setConfirmPassword}
              secureTextEntry
              autoComplete="new-password"
              error={errors.confirmPassword}
            />

            <Button
              title="Créer mon compte"
              onPress={handleRegister}
              loading={isLoading}
              style={styles.submitButton}
            />
          </View>

          <View style={styles.footer}>
            <Text style={styles.footerText}>Vous avez déjà un compte ?</Text>
            <Button
              title="Se connecter"
              variant="link"
              onPress={handleLogin}
            />
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  keyboardView: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    paddingHorizontal: 24,
    paddingTop: 16,
  },
  header: {
    marginTop: 24,
    marginBottom: 32,
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    color: '#111827',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#6B7280',
  },
  form: {
    flex: 1,
  },
  submitButton: {
    marginTop: 8,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 24,
  },
  footerText: {
    fontSize: 14,
    color: '#6B7280',
    marginRight: 4,
  },
});
