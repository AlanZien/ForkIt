# Tests Utilisateur - Weekly Meal Planning

## Feature
**Nom:** Weekly Meal Planning (Planification Hebdomadaire)
**Date:** 2026-01-03
**Status:** Pret pour tests

---

## Prerequis
- Utilisateur connecte avec un compte valide
- Application mobile ForkIt installee
- Connexion internet active
- Au moins 2-3 recettes dans les favoris (pour tests de selection)

---

## Scenarios de Test

### UT-001: Afficher le calendrier hebdomadaire
| Champ | Valeur |
|-------|--------|
| **Priorite** | Critique |
| **Etapes** | 1. Se connecter a l'application<br>2. Naviguer vers l'onglet Planning |
| **Resultat attendu** | Le calendrier affiche 7 jours (Lundi a Dimanche) avec 2 creneaux par jour (Dejeuner et Diner). La semaine courante est affichee par defaut. |
| **Status** | A tester |

---

### UT-002: Naviguer vers la semaine suivante
| Champ | Valeur |
|-------|--------|
| **Priorite** | Haute |
| **Etapes** | 1. Etre sur l'ecran Planning<br>2. Appuyer sur la fleche "Suivant" |
| **Resultat attendu** | Le calendrier affiche la semaine suivante. Les dates dans l'en-tete sont mises a jour. |
| **Status** | A tester |

---

### UT-003: Limite de navigation - Semaine courante
| Champ | Valeur |
|-------|--------|
| **Priorite** | Haute |
| **Etapes** | 1. Etre sur l'ecran Planning (semaine courante)<br>2. Observer le bouton "Precedent" |
| **Resultat attendu** | Le bouton "Precedent" est desactive (grise, non cliquable) car on ne peut pas planifier dans le passe. |
| **Status** | A tester |

---

### UT-004: Limite de navigation - 4 semaines max
| Champ | Valeur |
|-------|--------|
| **Priorite** | Haute |
| **Etapes** | 1. Etre sur l'ecran Planning<br>2. Appuyer 4 fois sur "Suivant"<br>3. Observer le bouton "Suivant" |
| **Resultat attendu** | Apres 4 semaines en avant, le bouton "Suivant" est desactive. On ne peut pas planifier au-dela de 4 semaines. |
| **Status** | A tester |

---

### UT-005: Ajouter une recette via les favoris
| Champ | Valeur |
|-------|--------|
| **Priorite** | Critique |
| **Etapes** | 1. Appuyer sur un creneau vide (affichant "+")<br>2. Dans la modale, selectionner l'onglet "Favoris"<br>3. Appuyer sur une recette favorite |
| **Resultat attendu** | La modale se ferme. Le creneau affiche maintenant la photo, le nom de la recette et le nombre de portions. |
| **Status** | A tester |

---

### UT-006: Ajouter une recette via la recherche
| Champ | Valeur |
|-------|--------|
| **Priorite** | Critique |
| **Etapes** | 1. Appuyer sur un creneau vide<br>2. Selectionner l'onglet "Recherche"<br>3. Taper "poulet" dans le champ de recherche<br>4. Selectionner une recette dans les resultats |
| **Resultat attendu** | Les resultats de recherche s'affichent. La selection ferme la modale et remplit le creneau. |
| **Status** | A tester |

---

### UT-007: Ajouter une recette via les recentes
| Champ | Valeur |
|-------|--------|
| **Priorite** | Haute |
| **Etapes** | 1. Avoir deja ajoute au moins une recette a un creneau<br>2. Appuyer sur un autre creneau vide<br>3. Selectionner l'onglet "Recents" |
| **Resultat attendu** | La liste affiche les dernieres recettes ajoutees (max 10). La selection fonctionne comme les autres onglets. |
| **Status** | A tester |

---

### UT-008: Voir les details d'une recette planifiee
| Champ | Valeur |
|-------|--------|
| **Priorite** | Haute |
| **Etapes** | 1. Avoir une recette dans un creneau<br>2. Faire un appui long sur le creneau<br>3. Selectionner "Voir" dans le menu |
| **Resultat attendu** | Navigation vers la page de details de la recette. Le bouton retour ramene au planning. |
| **Status** | A tester |

---

### UT-009: Remplacer une recette existante
| Champ | Valeur |
|-------|--------|
| **Priorite** | Critique |
| **Etapes** | 1. Avoir "Recette A" dans un creneau<br>2. Appui long sur le creneau<br>3. Selectionner "Remplacer"<br>4. Choisir "Recette B" dans la modale |
| **Resultat attendu** | Le creneau affiche maintenant "Recette B" a la place de "Recette A". |
| **Status** | A tester |

---

### UT-010: Supprimer une recette avec confirmation
| Champ | Valeur |
|-------|--------|
| **Priorite** | Critique |
| **Etapes** | 1. Avoir une recette dans un creneau<br>2. Appui long sur le creneau<br>3. Selectionner "Supprimer"<br>4. Confirmer dans la boite de dialogue |
| **Resultat attendu** | Une confirmation est demandee. Apres confirmation, le creneau redevient vide (affiche "+"). |
| **Status** | A tester |

---

### UT-011: Annuler la suppression
| Champ | Valeur |
|-------|--------|
| **Priorite** | Moyenne |
| **Etapes** | 1. Avoir une recette dans un creneau<br>2. Appui long > "Supprimer"<br>3. Appuyer sur "Annuler" dans la confirmation |
| **Resultat attendu** | La recette reste dans le creneau. Aucune modification. |
| **Status** | A tester |

---

### UT-012: Affichage des portions par defaut
| Champ | Valeur |
|-------|--------|
| **Priorite** | Haute |
| **Etapes** | 1. Verifier le nombre de portions dans le profil (ex: 4)<br>2. Ajouter une nouvelle recette a un creneau<br>3. Observer le badge de portions |
| **Resultat attendu** | Le nombre de portions affiche correspond a celui du profil utilisateur (ex: badge "4"). |
| **Status** | A tester |

---

### UT-013: Persistance des donnees apres fermeture
| Champ | Valeur |
|-------|--------|
| **Priorite** | Critique |
| **Etapes** | 1. Ajouter 2-3 recettes au planning<br>2. Fermer completement l'application<br>3. Rouvrir l'application et aller au Planning |
| **Resultat attendu** | Toutes les recettes planifiees sont toujours visibles apres la reouverture. |
| **Status** | A tester |

---

### UT-014: Etat vide - Nouvelle semaine
| Champ | Valeur |
|-------|--------|
| **Priorite** | Moyenne |
| **Etapes** | 1. Naviguer vers une semaine sans aucune recette planifiee |
| **Resultat attendu** | Tous les 14 creneaux affichent l'icone "+". L'interface reste fonctionnelle. |
| **Status** | A tester |

---

### UT-015: Gestion des erreurs reseau
| Champ | Valeur |
|-------|--------|
| **Priorite** | Haute |
| **Etapes** | 1. Desactiver la connexion internet<br>2. Essayer d'ajouter une recette a un creneau |
| **Resultat attendu** | Un message d'erreur clair s'affiche. L'interface ne reste pas bloquee. Un bouton "Reessayer" est disponible. |
| **Status** | A tester |

---

### UT-016: Fermer la modale sans selection
| Champ | Valeur |
|-------|--------|
| **Priorite** | Moyenne |
| **Etapes** | 1. Appuyer sur un creneau vide<br>2. Dans la modale, appuyer sur X ou faire glisser vers le bas |
| **Resultat attendu** | La modale se ferme. Le creneau reste vide. Aucune modification. |
| **Status** | A tester |

---

### UT-017: Affichage correct des jours en francais
| Champ | Valeur |
|-------|--------|
| **Priorite** | Moyenne |
| **Etapes** | 1. Ouvrir l'ecran Planning<br>2. Verifier les labels des jours |
| **Resultat attendu** | Les jours sont affiches en francais: Lundi, Mardi, Mercredi, Jeudi, Vendredi, Samedi, Dimanche. |
| **Status** | A tester |

---

### UT-018: Troncature du nom de recette long
| Champ | Valeur |
|-------|--------|
| **Priorite** | Basse |
| **Etapes** | 1. Ajouter une recette avec un nom tres long (ex: "Poulet roti aux herbes de Provence et pommes de terre")<br>2. Observer l'affichage dans le creneau |
| **Resultat attendu** | Le nom est tronque proprement (avec "...") sans casser la mise en page. |
| **Status** | A tester |

---

### UT-019: Recherche sans resultats
| Champ | Valeur |
|-------|--------|
| **Priorite** | Moyenne |
| **Etapes** | 1. Ouvrir la modale de selection<br>2. Aller sur l'onglet "Recherche"<br>3. Taper "xyzabc123" (terme sans resultats) |
| **Resultat attendu** | Un message "Aucun resultat" s'affiche. Pas de crash ou d'ecran vide. |
| **Status** | A tester |

---

### UT-020: Accessibilite - Navigation au clavier (si applicable)
| Champ | Valeur |
|-------|--------|
| **Priorite** | Basse |
| **Etapes** | 1. Activer VoiceOver (iOS) ou TalkBack (Android)<br>2. Naviguer dans l'ecran Planning |
| **Resultat attendu** | Tous les elements interactifs sont annonces correctement. La navigation est possible sans ecran. |
| **Status** | A tester |

---

## Resume

| Priorite | Nombre de tests |
|----------|-----------------|
| Critique | 6 |
| Haute | 7 |
| Moyenne | 5 |
| Basse | 2 |
| **Total** | **20** |

---

## Notes
- Ces tests doivent etre executes sur iOS et Android
- Tester en mode portrait et paysage
- Verifier sur differentes tailles d'ecran (petit telephone, grand telephone)
- Les accents ont ete retires pour compatibilite systeme
