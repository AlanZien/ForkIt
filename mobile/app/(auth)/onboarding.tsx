/**
 * Onboarding Screen
 *
 * 3-slide carousel introducing the app to first-time users
 */

import React, { useState, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Dimensions,
  FlatList,
  ViewToken,
} from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Button } from '../../components/ui';
import { setOnboardingSeen } from '../../services/onboardingStorage';

const { width } = Dimensions.get('window');

interface Slide {
  id: string;
  icon: string;
  title: string;
  description: string;
}

const slides: Slide[] = [
  {
    id: '1',
    icon: '📅',
    title: 'Planification hebdomadaire',
    description: 'Organisez vos repas pour toute la semaine en quelques minutes',
  },
  {
    id: '2',
    icon: '🛒',
    title: 'Liste de courses automatique',
    description: 'Générez votre liste de courses à partir de vos menus planifiés',
  },
  {
    id: '3',
    icon: '✨',
    title: 'Suggestions personnalisées',
    description: 'Recevez des idées de recettes adaptées à vos goûts et préférences',
  },
];

export default function OnboardingScreen() {
  const router = useRouter();
  const [currentIndex, setCurrentIndex] = useState(0);
  const flatListRef = useRef<FlatList>(null);

  const handleViewableItemsChanged = useRef(
    ({ viewableItems }: { viewableItems: ViewToken[] }) => {
      if (viewableItems.length > 0 && viewableItems[0].index !== null) {
        setCurrentIndex(viewableItems[0].index);
      }
    }
  ).current;

  const viewabilityConfig = useRef({ viewAreaCoveragePercentThreshold: 50 }).current;

  const handleGetStarted = async () => {
    await setOnboardingSeen();
    router.replace('/(auth)/register');
  };

  const handleLogin = async () => {
    await setOnboardingSeen();
    router.replace('/(auth)/login');
  };

  const renderSlide = ({ item }: { item: Slide }) => (
    <View style={styles.slide}>
      <View style={styles.iconContainer}>
        <Text style={styles.icon}>{item.icon}</Text>
      </View>
      <Text style={styles.title}>{item.title}</Text>
      <Text style={styles.description}>{item.description}</Text>
    </View>
  );

  const renderPaginationDots = () => (
    <View style={styles.pagination}>
      {slides.map((_, index) => (
        <View
          key={index}
          style={[
            styles.dot,
            index === currentIndex && styles.dotActive,
          ]}
        />
      ))}
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <View style={styles.logoContainer}>
          <Text style={styles.logo}>🍴</Text>
        </View>
        <Text style={styles.appName}>ForkIt</Text>
      </View>

      <FlatList
        ref={flatListRef}
        data={slides}
        renderItem={renderSlide}
        keyExtractor={(item) => item.id}
        horizontal
        pagingEnabled
        showsHorizontalScrollIndicator={false}
        onViewableItemsChanged={handleViewableItemsChanged}
        viewabilityConfig={viewabilityConfig}
        style={styles.carousel}
      />

      {renderPaginationDots()}

      <View style={styles.footer}>
        <Button title="Commencer" onPress={handleGetStarted} />
        <Button
          title="Se connecter"
          variant="link"
          onPress={handleLogin}
          style={styles.loginButton}
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
    alignItems: 'center',
    paddingTop: 40,
    paddingBottom: 20,
  },
  logoContainer: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#14B8A6',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  logo: {
    fontSize: 40,
  },
  appName: {
    fontSize: 28,
    fontWeight: '700',
    color: '#111827',
  },
  carousel: {
    flex: 1,
  },
  slide: {
    width,
    paddingHorizontal: 40,
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
    fontWeight: '600',
    color: '#111827',
    textAlign: 'center',
    marginBottom: 12,
  },
  description: {
    fontSize: 16,
    color: '#6B7280',
    textAlign: 'center',
    lineHeight: 24,
  },
  pagination: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 20,
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#E5E7EB',
    marginHorizontal: 4,
  },
  dotActive: {
    backgroundColor: '#14B8A6',
    width: 24,
  },
  footer: {
    paddingHorizontal: 24,
    paddingBottom: 24,
  },
  loginButton: {
    marginTop: 16,
    alignSelf: 'center',
  },
});
