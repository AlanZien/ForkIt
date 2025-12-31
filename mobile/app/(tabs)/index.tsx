/**
 * Home Screen
 *
 * Main dashboard after login
 */

import { View, Text, StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useAuthStore } from '../../stores/auth';

export default function HomeScreen() {
  const user = useAuthStore((state) => state.user);
  const userName = user?.user_metadata?.name || 'Utilisateur';

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.greeting}>Bonjour, {userName} 👋</Text>
        <Text style={styles.subtitle}>Bienvenue sur ForkIt</Text>
      </View>

      <View style={styles.content}>
        <Text style={styles.placeholder}>
          Votre planning de repas apparaîtra ici
        </Text>
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
  greeting: {
    fontSize: 24,
    fontWeight: '700',
    color: '#111827',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 16,
    color: '#6B7280',
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 24,
  },
  placeholder: {
    fontSize: 16,
    color: '#9CA3AF',
    textAlign: 'center',
  },
});
