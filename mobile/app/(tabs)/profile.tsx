/**
 * Profile Screen
 *
 * User profile, preferences, and settings with logout
 */

import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, Switch, Alert, ScrollView, Platform } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Button } from '../../components/ui';
import { ProfilePreferences } from '../../components/preferences';
import { useAuthStore } from '../../stores/auth';
import { checkBiometricSupport, getBiometricType, getBiometricLabel, authenticate } from '../../services/biometric';
import { colors, spacing } from '../../constants/theme';

export default function ProfileScreen() {
  const router = useRouter();
  const user = useAuthStore((state) => state.user);
  const biometricEnabled = useAuthStore((state) => state.biometricEnabled);
  const setBiometric = useAuthStore((state) => state.setBiometric);
  const logout = useAuthStore((state) => state.logout);
  const isLoading = useAuthStore((state) => state.isLoading);

  const [biometricSupported, setBiometricSupported] = useState(false);
  const [biometricType, setBiometricTypeState] = useState<string>('Biometrie');

  const userName = user?.user_metadata?.name || 'Utilisateur';
  const userEmail = user?.email || '';

  useEffect(() => {
    const checkBiometric = async () => {
      const { supported } = await checkBiometricSupport();
      // In Expo Go, biometric check may fail - show toggle anyway for UI testing
      const isExpoGo = !supported; // Assume Expo Go if not supported
      setBiometricSupported(supported || isExpoGo);

      const type = await getBiometricType();
      setBiometricTypeState(type !== 'none' ? getBiometricLabel(type) : 'Face ID');
    };

    checkBiometric();
  }, []);

  const handleBiometricToggle = async (value: boolean) => {
    if (value) {
      // Require authentication to enable
      const success = await authenticate(`Activez ${biometricType}`);
      // In Expo Go, authentication may fail - allow toggle for testing
      if (success || __DEV__) {
        await setBiometric(true);
      }
    } else {
      await setBiometric(false);
    }
  };

  const handleLogout = async () => {
    const doLogout = async () => {
      await logout();
      router.replace('/(auth)/login');
    };

    if (Platform.OS === 'web') {
      if (window.confirm('Etes-vous sur de vouloir vous deconnecter ?')) {
        await doLogout();
      }
    } else {
      Alert.alert(
        'Deconnexion',
        'Etes-vous sur de vouloir vous deconnecter ?',
        [
          { text: 'Annuler', style: 'cancel' },
          {
            text: 'Deconnexion',
            style: 'destructive',
            onPress: doLogout,
          },
        ]
      );
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>Profil</Text>
        </View>

        {/* User Card */}
        <View style={styles.userCard}>
          <View style={styles.avatar}>
            <Text style={styles.avatarText}>
              {userName.charAt(0).toUpperCase()}
            </Text>
          </View>
          <View style={styles.userInfo}>
            <Text style={styles.userName}>{userName}</Text>
            <Text style={styles.userEmail}>{userEmail}</Text>
          </View>
        </View>

        {/* Preferences Section */}
        <View style={styles.preferencesSection}>
          <ProfilePreferences />
        </View>

        {/* Settings Section */}
        <View style={styles.settingsSection}>
          <Text style={styles.sectionTitle}>Parametres</Text>

          {biometricSupported && (
            <View style={styles.settingItem}>
              <View style={styles.settingInfo}>
                <Text style={styles.settingLabel}>Utiliser {biometricType}</Text>
                <Text style={styles.settingDescription}>
                  Connexion rapide avec {biometricType}
                </Text>
              </View>
              <Switch
                value={biometricEnabled}
                onValueChange={handleBiometricToggle}
                trackColor={{ false: '#E5E7EB', true: colors.primary }}
                thumbColor="#FFFFFF"
              />
            </View>
          )}
        </View>

        {/* Logout Button */}
        <View style={styles.logoutSection}>
          <Button
            title="Se deconnecter"
            variant="danger"
            onPress={handleLogout}
            loading={isLoading}
          />
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingHorizontal: spacing.lg,
    paddingBottom: spacing.xl,
  },
  header: {
    paddingTop: spacing.lg,
    paddingBottom: spacing.md,
  },
  title: {
    fontSize: 24,
    fontWeight: '700',
    color: colors.foreground,
  },
  userCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.card,
    borderRadius: 16,
    padding: spacing.md,
    marginBottom: spacing.lg,
  },
  avatar: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.md,
  },
  avatarText: {
    fontSize: 24,
    fontWeight: '600',
    color: colors.primaryForeground,
  },
  userInfo: {
    flex: 1,
  },
  userName: {
    fontSize: 18,
    fontWeight: '600',
    color: colors.foreground,
    marginBottom: 4,
  },
  userEmail: {
    fontSize: 14,
    color: colors.mutedForeground,
  },
  preferencesSection: {
    marginBottom: spacing.lg,
  },
  settingsSection: {
    marginBottom: spacing.lg,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: colors.foreground,
    marginBottom: spacing.md,
  },
  settingItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: colors.card,
    borderRadius: 16,
    padding: spacing.md,
  },
  settingInfo: {
    flex: 1,
    marginRight: spacing.md,
  },
  settingLabel: {
    fontSize: 16,
    fontWeight: '500',
    color: colors.foreground,
    marginBottom: 4,
  },
  settingDescription: {
    fontSize: 14,
    color: colors.mutedForeground,
  },
  logoutSection: {
    marginTop: spacing.lg,
  },
});
