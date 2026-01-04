/**
 * Forgot Password Screen
 *
 * Request password reset email
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
} from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Input, Button, BackButton } from '../../components/ui';
import { supabase } from '../../services/supabase';

export default function ForgotPasswordScreen() {
  const router = useRouter();

  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [error, setError] = useState('');

  const validate = (): boolean => {
    if (!email) {
      setError('Email requis');
      return false;
    }
    if (!/\S+@\S+\.\S+/.test(email)) {
      setError('Email invalide');
      return false;
    }
    setError('');
    return true;
  };

  const handleSubmit = async () => {
    if (!validate()) return;

    setIsLoading(true);
    try {
      await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: 'forkit://reset-password',
      });
      // Always show success to prevent email enumeration
      setIsSuccess(true);
    } catch (err) {
      // Still show success to prevent email enumeration
      setIsSuccess(true);
    } finally {
      setIsLoading(false);
    }
  };

  const handleBackToLogin = () => {
    router.replace('/(auth)/login');
  };

  if (isSuccess) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.successContent}>
          <View style={styles.iconContainer}>
            <Text style={styles.icon}>✉️</Text>
          </View>

          <Text style={styles.successTitle}>Email envoyé !</Text>

          <Text style={styles.successDescription}>
            Si un compte existe avec cet email, vous recevrez un lien pour
            réinitialiser votre mot de passe.
          </Text>

          <Button
            title="Retour à la connexion"
            onPress={handleBackToLogin}
            style={styles.successButton}
          />
        </View>
      </SafeAreaView>
    );
  }

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
            <Text style={styles.title}>Mot de passe oublié ?</Text>
            <Text style={styles.subtitle}>
              Entrez votre email pour recevoir un lien de réinitialisation
            </Text>
          </View>

          <View style={styles.form}>
            <Input
              label="Email"
              placeholder="votre@email.com"
              value={email}
              onChangeText={setEmail}
              keyboardType="email-address"
              autoCapitalize="none"
              autoComplete="email"
              error={error}
            />

            <Button
              title="Envoyer le lien"
              onPress={handleSubmit}
              loading={isLoading}
              style={styles.submitButton}
            />
          </View>

          <View style={styles.footer}>
            <Button
              title="Retour à la connexion"
              variant="link"
              onPress={handleBackToLogin}
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
    alignItems: 'center',
    paddingVertical: 24,
  },
  successContent: {
    flex: 1,
    paddingHorizontal: 24,
    justifyContent: 'center',
    alignItems: 'center',
  },
  iconContainer: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: '#F0FDFA',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 24,
  },
  icon: {
    fontSize: 48,
  },
  successTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: '#111827',
    marginBottom: 16,
  },
  successDescription: {
    fontSize: 16,
    color: '#6B7280',
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 32,
    paddingHorizontal: 16,
  },
  successButton: {
    width: '100%',
  },
});
