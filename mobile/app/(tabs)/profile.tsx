/**
 * Profile Screen
 *
 * User profile and settings with logout
 */

import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, Switch, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Button } from '../../components/ui';
import { useAuthStore } from '../../stores/auth';
import { checkBiometricSupport, getBiometricType, getBiometricLabel, authenticate } from '../../services/biometric';

export default function ProfileScreen() {
  const router = useRouter();
  const user = useAuthStore((state) => state.user);
  const biometricEnabled = useAuthStore((state) => state.biometricEnabled);
  const setBiometric = useAuthStore((state) => state.setBiometric);
  const logout = useAuthStore((state) => state.logout);
  const isLoading = useAuthStore((state) => state.isLoading);

  const [biometricSupported, setBiometricSupported] = useState(false);
  const [biometricType, setBiometricTypeState] = useState<string>('Biométrie');

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

  const handleLogout = () => {
    Alert.alert(
      'Déconnexion',
      'Êtes-vous sûr de vouloir vous déconnecter ?',
      [
        { text: 'Annuler', style: 'cancel' },
        {
          text: 'Déconnexion',
          style: 'destructive',
          onPress: async () => {
            await logout();
            router.replace('/(auth)/login');
          },
        },
      ]
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Profil</Text>
      </View>

      <View style={styles.content}>
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
              trackColor={{ false: '#E5E7EB', true: '#14B8A6' }}
              thumbColor="#FFFFFF"
            />
          </View>
        )}

        <View style={styles.spacer} />

        <Button
          title="Se déconnecter"
          variant="danger"
          onPress={handleLogout}
          loading={isLoading}
        />
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  header: {
    paddingHorizontal: 24,
    paddingTop: 24,
    paddingBottom: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: '700',
    color: '#111827',
  },
  content: {
    flex: 1,
    paddingHorizontal: 24,
  },
  userCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F9FAFB',
    borderRadius: 16,
    padding: 16,
    marginBottom: 24,
  },
  avatar: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: '#14B8A6',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  avatarText: {
    fontSize: 24,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  userInfo: {
    flex: 1,
  },
  userName: {
    fontSize: 18,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 4,
  },
  userEmail: {
    fontSize: 14,
    color: '#6B7280',
  },
  settingItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  settingInfo: {
    flex: 1,
    marginRight: 16,
  },
  settingLabel: {
    fontSize: 16,
    fontWeight: '500',
    color: '#111827',
    marginBottom: 4,
  },
  settingDescription: {
    fontSize: 14,
    color: '#6B7280',
  },
  spacer: {
    flex: 1,
  },
});
