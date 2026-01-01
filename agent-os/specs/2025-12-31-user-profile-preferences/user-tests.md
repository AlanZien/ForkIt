# Tests Utilisateur - User Profile & Preferences

## Feature
**Nom:** User Profile & Preferences
**Date:** 2025-12-31
**Status:** Prêt pour tests

---

## Prérequis
- Utilisateur connecté avec un compte valide
- Application mobile ForkIt installée
- Connexion internet active

---

## Scénarios de Test

### UT-001: Afficher les préférences en mode lecture
| Champ | Valeur |
|-------|--------|
| **Priorité** | Haute |
| **Étapes** | 1. Se connecter à l'application<br>2. Naviguer vers l'onglet "Profil" |
| **Résultat attendu** | Les sections Régimes, Allergies, Ingrédients exclus, Ingrédients préférés et Portions s'affichent en mode lecture seule avec les valeurs actuelles |
| **Status** | À tester |

---

### UT-002: Passer en mode édition
| Champ | Valeur |
|-------|--------|
| **Priorité** | Haute |
| **Étapes** | 1. Être sur l'écran Profil<br>2. Cliquer sur le bouton "Modifier" |
| **Résultat attendu** | Tous les champs deviennent interactifs. Les boutons "Enregistrer" et "Annuler" apparaissent |
| **Status** | À tester |

---

### UT-003: Sélectionner un régime alimentaire
| Champ | Valeur |
|-------|--------|
| **Priorité** | Haute |
| **Étapes** | 1. Être en mode édition<br>2. Cliquer sur le chip "Végétarien" |
| **Résultat attendu** | Le chip devient teal (#14B8A6) avec texte blanc. La sélection est visible |
| **Status** | À tester |

---

### UT-004: Désélectionner un régime alimentaire
| Champ | Valeur |
|-------|--------|
| **Priorité** | Moyenne |
| **Étapes** | 1. Être en mode édition<br>2. Cliquer sur un chip déjà sélectionné |
| **Résultat attendu** | Le chip redevient gris (#F3F4F6) avec texte sombre. La désélection est visible |
| **Status** | À tester |

---

### UT-005: Tester incompatibilité Végétalien
| Champ | Valeur |
|-------|--------|
| **Priorité** | Haute |
| **Étapes** | 1. Être en mode édition<br>2. Sélectionner "Végétalien" |
| **Résultat attendu** | Les chips "Pescétarien", "Sans bœuf", "Sans porc" deviennent désactivés (opacity réduite, non cliquables) |
| **Status** | À tester |

---

### UT-006: Désélectionner Végétalien réactive les options
| Champ | Valeur |
|-------|--------|
| **Priorité** | Moyenne |
| **Étapes** | 1. Avoir "Végétalien" sélectionné<br>2. Désélectionner "Végétalien" |
| **Résultat attendu** | Les chips "Pescétarien", "Sans bœuf", "Sans porc" redeviennent actifs et cliquables |
| **Status** | À tester |

---

### UT-007: Warning Halal + Casher
| Champ | Valeur |
|-------|--------|
| **Priorité** | Haute |
| **Étapes** | 1. Être en mode édition<br>2. Sélectionner "Halal"<br>3. Sélectionner "Casher" |
| **Résultat attendu** | Un message d'avertissement non-bloquant s'affiche : "Vérifiez la cohérence de cette combinaison" |
| **Status** | À tester |

---

### UT-008: Sélectionner une allergie
| Champ | Valeur |
|-------|--------|
| **Priorité** | Haute |
| **Étapes** | 1. Être en mode édition<br>2. Cliquer sur le chip "Gluten" dans la section Allergies |
| **Résultat attendu** | Le chip devient teal avec texte blanc |
| **Status** | À tester |

---

### UT-009: Multi-sélection allergies sans restriction
| Champ | Valeur |
|-------|--------|
| **Priorité** | Moyenne |
| **Étapes** | 1. Être en mode édition<br>2. Sélectionner plusieurs allergies (Gluten, Lactose, Arachides) |
| **Résultat attendu** | Toutes les allergies peuvent être sélectionnées simultanément, aucune restriction |
| **Status** | À tester |

---

### UT-010: Ajouter un ingrédient exclu
| Champ | Valeur |
|-------|--------|
| **Priorité** | Haute |
| **Étapes** | 1. Être en mode édition<br>2. Saisir "champignons" dans le champ Ingrédients exclus<br>3. Cliquer sur "Ajouter" |
| **Résultat attendu** | Un tag "champignons" apparaît sous le champ de saisie |
| **Status** | À tester |

---

### UT-011: Normalisation des ingrédients
| Champ | Valeur |
|-------|--------|
| **Priorité** | Moyenne |
| **Étapes** | 1. Saisir "  TOMATES  " (avec espaces et majuscules)<br>2. Cliquer sur "Ajouter" |
| **Résultat attendu** | Le tag apparaît comme "tomates" (lowercase, sans espaces) |
| **Status** | À tester |

---

### UT-012: Supprimer un ingrédient
| Champ | Valeur |
|-------|--------|
| **Priorité** | Haute |
| **Étapes** | 1. Avoir au moins un ingrédient dans la liste<br>2. Cliquer sur le X du tag |
| **Résultat attendu** | Le tag est supprimé de la liste |
| **Status** | À tester |

---

### UT-013: Limite 30 ingrédients exclus
| Champ | Valeur |
|-------|--------|
| **Priorité** | Haute |
| **Étapes** | 1. Ajouter 30 ingrédients exclus<br>2. Tenter d'en ajouter un 31ème |
| **Résultat attendu** | Message d'erreur "Maximum 30 ingrédients". L'ajout est bloqué |
| **Status** | À tester |

---

### UT-014: Ajouter un ingrédient préféré
| Champ | Valeur |
|-------|--------|
| **Priorité** | Haute |
| **Étapes** | 1. Être en mode édition<br>2. Saisir "poulet" dans le champ Ingrédients préférés<br>3. Cliquer sur "Ajouter" |
| **Résultat attendu** | Un tag "poulet" apparaît dans la section Ingrédients préférés |
| **Status** | À tester |

---

### UT-015: Modifier le nombre de portions (incrément)
| Champ | Valeur |
|-------|--------|
| **Priorité** | Haute |
| **Étapes** | 1. Être en mode édition avec portions = 2<br>2. Cliquer sur le bouton "+" |
| **Résultat attendu** | Le nombre passe à 3 |
| **Status** | À tester |

---

### UT-016: Modifier le nombre de portions (décrément)
| Champ | Valeur |
|-------|--------|
| **Priorité** | Haute |
| **Étapes** | 1. Être en mode édition avec portions = 2<br>2. Cliquer sur le bouton "-" |
| **Résultat attendu** | Le nombre passe à 1 |
| **Status** | À tester |

---

### UT-017: Limite minimum portions (1)
| Champ | Valeur |
|-------|--------|
| **Priorité** | Moyenne |
| **Étapes** | 1. Avoir portions = 1<br>2. Cliquer sur "-" |
| **Résultat attendu** | Le bouton "-" est désactivé. Le nombre reste à 1 |
| **Status** | À tester |

---

### UT-018: Limite maximum portions (20)
| Champ | Valeur |
|-------|--------|
| **Priorité** | Moyenne |
| **Étapes** | 1. Avoir portions = 20<br>2. Cliquer sur "+" |
| **Résultat attendu** | Le bouton "+" est désactivé. Le nombre reste à 20 |
| **Status** | À tester |

---

### UT-019: Annuler les modifications
| Champ | Valeur |
|-------|--------|
| **Priorité** | Haute |
| **Étapes** | 1. Être en mode édition<br>2. Faire plusieurs modifications<br>3. Cliquer sur "Annuler" |
| **Résultat attendu** | Toutes les modifications sont annulées. Les valeurs initiales sont restaurées. Retour en mode lecture |
| **Status** | À tester |

---

### UT-020: Enregistrer les modifications
| Champ | Valeur |
|-------|--------|
| **Priorité** | Haute |
| **Étapes** | 1. Être en mode édition<br>2. Faire des modifications<br>3. Cliquer sur "Enregistrer" |
| **Résultat attendu** | Indicateur de chargement pendant la sauvegarde. Toast de succès. Retour en mode lecture. Les données sont persistées |
| **Status** | À tester |

---

### UT-021: Persistance après refresh
| Champ | Valeur |
|-------|--------|
| **Priorité** | Haute |
| **Étapes** | 1. Enregistrer des modifications<br>2. Fermer et rouvrir l'application<br>3. Retourner sur l'écran Profil |
| **Résultat attendu** | Les préférences enregistrées sont toujours présentes |
| **Status** | À tester |

---

### UT-022: Gestion erreur réseau
| Champ | Valeur |
|-------|--------|
| **Priorité** | Moyenne |
| **Étapes** | 1. Désactiver le réseau<br>2. Tenter d'enregistrer des modifications |
| **Résultat attendu** | Message d'erreur explicite avec option de réessai |
| **Status** | À tester |

---

### UT-023: Accès sans authentification
| Champ | Valeur |
|-------|--------|
| **Priorité** | Haute |
| **Étapes** | 1. Se déconnecter<br>2. Tenter d'accéder à l'écran Profil |
| **Résultat attendu** | Redirection vers l'écran de connexion |
| **Status** | À tester |

---

## Résumé

| Priorité | Nombre de tests |
|----------|-----------------|
| Haute | 16 |
| Moyenne | 7 |
| **Total** | **23** |

---

## Notes
- Ces tests doivent être exécutés sur iOS et Android
- Tester en mode portrait et paysage
- Vérifier l'accessibilité (VoiceOver / TalkBack)
