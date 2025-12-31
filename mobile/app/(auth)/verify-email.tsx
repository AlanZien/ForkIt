/**
 * Verify Email Screen
 *
 * Displays instructions to verify email with resend option
 */

import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, Alert } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Button } from '../../components/ui';
import { supabase } from '../../services/supabase';
import { useAuthStore } from '../../stores/auth';

const RESEND_COOLDOWN = 60; // seconds

export default function VerifyEmailScreen() {
  const router = useRouter();
  const { email } = useLocalSearchParams<{ email: string }>();
  const checkSession = useAuthStore((state) => state.checkSession);
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  const [isResending, setIsResending] = useState(false);
  const [cooldown, setCooldown] = useState(0);

  // Poll for verification status
  useEffect(() => {
    const interval = setInterval(async () => {
      await checkSession();
    }, 5000);

    return () => clearInterval(interval);
  }, [checkSession]);

  // Navigate when authenticated
  useEffect(() => {
    if (isAuthenticated) {
      router.replace('/(tabs)');
    }
  }, [isAuthenticated, router]);

  // Cooldown timer
  useEffect(() => {
    if (cooldown > 0) {
      const timer = setTimeout(() => setCooldown(cooldown - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [cooldown]);

  const handleResend = async () => {
    if (!email || cooldown > 0) return;

    setIsResending(true);
    try {
      const { error } = await supabase.auth.resend({
        type: 'signup',
        email,
      });

      if (error) throw error;

      setCooldown(RESEND_COOLDOWN);
      Alert.alert('Email envoyé', 'Un nouveau lien de vérification a été envoyé.');
    } catch (error) {
      Alert.alert('Erreur', 'Impossible de renvoyer l\'email. Réessayez plus tard.');
    } finally {
      setIsResending(false);
    }
  };

  const handleBackToLogin = () => {
    router.replace('/(auth)/login');
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        <View style={styles.iconContainer}>
          <Text style={styles.icon}>📧</Text>
        </View>

        <Text style={styles.title}>Vérifiez votre email</Text>

        <Text style={styles.description}>
          Nous avons envoyé un lien de vérification à :
        </Text>

        <Text style={styles.email}>{email}</Text>

        <Text style={styles.instructions}>
          Cliquez sur le lien dans l'email pour activer votre compte.
          N'oubliez pas de vérifier vos spams.
        </Text>

        <View style={styles.buttons}>
          <Button
            title={
              cooldown > 0
                ? `Renvoyer l'email (${cooldown}s)`
                : 'Renvoyer l\'email'
            }
            variant="secondary"
            onPress={handleResend}
            loading={isResending}
            disabled={cooldown > 0}
          />

          <Button
            title="Retour à la connexion"
            variant="link"
            onPress={handleBackToLogin}
            style={styles.linkButton}
          />
        </View>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  content: {
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
  title: {
    fontSize: 24,
    fontWeight: '700',
    color: '#111827',
    marginBottom: 16,
    textAlign: 'center',
  },
  description: {
    fontSize: 16,
    color: '#6B7280',
    textAlign: 'center',
    marginBottom: 8,
  },
  email: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 24,
  },
  instructions: {
    fontSize: 14,
    color: '#9CA3AF',
    textAlign: 'center',
    lineHeight: 22,
    marginBottom: 32,
    paddingHorizontal: 16,
  },
  buttons: {
    width: '100%',
  },
  linkButton: {
    marginTop: 16,
    alignSelf: 'center',
  },
});
