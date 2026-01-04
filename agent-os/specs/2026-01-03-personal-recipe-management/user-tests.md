# Tests Utilisateur - Personal Recipe Management

## Feature
**Nom:** Gestion des Recettes Personnelles
**Date:** 2026-01-03
**Status:** Pret pour tests

---

## Prerequis
- Utilisateur connecte avec un compte valide
- Application mobile ForkIt installee
- Connexion internet active
- Acces a la galerie photos et camera du telephone

---

## Scenarios de Test

### UT-001: Creer une recette avec tous les champs
| Champ | Valeur |
|-------|--------|
| **Priorite** | Critique |
| **Etapes** | 1. Naviguer vers l'onglet "Mes Recettes"<br>2. Appuyer sur le bouton "Creer une recette"<br>3. Remplir le titre: "Tarte aux pommes maison"<br>4. Definir le nombre de portions: 8<br>5. Ajouter temps de preparation: 30 min<br>6. Ajouter temps de cuisson: 45 min<br>7. Selectionner les tags: "Dessert", "Automne"<br>8. Ajouter 3 ingredients avec quantites et unites<br>9. Ajouter 4 etapes d'instructions<br>10. Appuyer sur "Enregistrer" |
| **Resultat attendu** | La recette est creee avec succes. Un message de confirmation s'affiche. La recette apparait dans la liste "Mes Recettes" avec le badge "Ma recette". |
| **Status** | A tester |

---

### UT-002: Creer une recette avec champs minimaux
| Champ | Valeur |
|-------|--------|
| **Priorite** | Critique |
| **Etapes** | 1. Naviguer vers "Creer une recette"<br>2. Remplir uniquement le titre: "Recette rapide"<br>3. Definir les portions: 4<br>4. Ajouter 1 ingredient: "Ingredient test", 100, "g"<br>5. Ajouter 1 etape: "Etape simple"<br>6. Appuyer sur "Enregistrer" |
| **Resultat attendu** | La recette est creee avec succes meme sans image, temps de preparation, temps de cuisson ou tags. |
| **Status** | A tester |

---

### UT-003: Validation du formulaire - Champs obligatoires
| Champ | Valeur |
|-------|--------|
| **Priorite** | Critique |
| **Etapes** | 1. Naviguer vers "Creer une recette"<br>2. Laisser le titre vide<br>3. Appuyer sur "Enregistrer"<br>4. Observer les messages d'erreur<br>5. Ajouter un titre mais sans ingredient<br>6. Appuyer sur "Enregistrer"<br>7. Ajouter un ingredient mais sans etape<br>8. Appuyer sur "Enregistrer" |
| **Resultat attendu** | Des messages d'erreur clairs s'affichent pour chaque champ obligatoire manquant: titre, au moins 1 ingredient, au moins 1 etape. Le formulaire ne peut pas etre soumis tant que ces champs ne sont pas remplis. |
| **Status** | A tester |

---

### UT-004: Validation du nombre de portions (1-20)
| Champ | Valeur |
|-------|--------|
| **Priorite** | Importante |
| **Etapes** | 1. Naviguer vers "Creer une recette"<br>2. Essayer de definir les portions a 0 (via le stepper -)<br>3. Observer le comportement<br>4. Essayer de definir les portions a 21 (via le stepper +)<br>5. Observer le comportement |
| **Resultat attendu** | Le stepper ne permet pas de descendre en dessous de 1 ni de monter au-dessus de 20. La valeur reste dans la plage autorisee. |
| **Status** | A tester |

---

### UT-005: Ajouter et supprimer des ingredients dynamiquement
| Champ | Valeur |
|-------|--------|
| **Priorite** | Critique |
| **Etapes** | 1. Naviguer vers "Creer une recette"<br>2. Observer qu'un champ ingredient existe par defaut<br>3. Appuyer sur "Ajouter un ingredient" 3 fois<br>4. Verifier qu'il y a maintenant 4 lignes d'ingredients<br>5. Remplir le 2eme ingredient: "Sucre", 100, "g"<br>6. Supprimer le 3eme ingredient (vide) via le bouton X<br>7. Verifier qu'il reste 3 lignes d'ingredients<br>8. Verifier que "Sucre" est toujours present |
| **Resultat attendu** | Les ingredients peuvent etre ajoutes et supprimes dynamiquement. La suppression d'un ingredient ne supprime pas les autres. Les donnees saisies sont conservees. |
| **Status** | A tester |

---

### UT-006: Ajouter et supprimer des etapes avec renumerotation
| Champ | Valeur |
|-------|--------|
| **Priorite** | Critique |
| **Etapes** | 1. Naviguer vers "Creer une recette"<br>2. Ajouter 3 etapes avec des instructions differentes<br>3. Verifier la numerotation: 1, 2, 3<br>4. Supprimer l'etape 2<br>5. Verifier la renumerotation: 1, 2 |
| **Resultat attendu** | Les etapes sont numerotees automatiquement. Apres suppression d'une etape, les etapes restantes sont renumerotees correctement. |
| **Status** | A tester |

---

### UT-007: Selection d'unite pour ingredient
| Champ | Valeur |
|-------|--------|
| **Priorite** | Importante |
| **Etapes** | 1. Naviguer vers "Creer une recette"<br>2. Ajouter un ingredient<br>3. Appuyer sur le champ "Unite"<br>4. Verifier les options disponibles<br>5. Selectionner "cuillere a soupe"<br>6. Verifier que l'unite est affichee |
| **Resultat attendu** | Un menu deroulant s'affiche avec les unites: g, kg, ml, L, c. a soupe, c. a cafe, pieces, etc. L'unite selectionnee est affichee dans le champ. |
| **Status** | A tester |

---

### UT-008: Ajouter une photo depuis la galerie
| Champ | Valeur |
|-------|--------|
| **Priorite** | Importante |
| **Etapes** | 1. Naviguer vers "Creer une recette"<br>2. Appuyer sur le bouton d'ajout d'image<br>3. Selectionner "Choisir dans la galerie"<br>4. Choisir une photo<br>5. Verifier que la photo s'affiche en apercu<br>6. Completer le reste du formulaire<br>7. Enregistrer la recette |
| **Resultat attendu** | La photo selectionnee s'affiche en apercu. Apres enregistrement, la photo est visible sur la recette. |
| **Status** | A tester |

---

### UT-009: Prendre une photo avec la camera
| Champ | Valeur |
|-------|--------|
| **Priorite** | Importante |
| **Etapes** | 1. Naviguer vers "Creer une recette"<br>2. Appuyer sur le bouton d'ajout d'image<br>3. Selectionner "Prendre une photo"<br>4. Prendre une photo avec la camera<br>5. Valider la photo<br>6. Verifier l'apercu |
| **Resultat attendu** | La camera s'ouvre. Apres prise de la photo, elle s'affiche en apercu dans le formulaire. |
| **Status** | A tester |

---

### UT-010: Creer une recette sans image
| Champ | Valeur |
|-------|--------|
| **Priorite** | Importante |
| **Etapes** | 1. Naviguer vers "Creer une recette"<br>2. Remplir tous les champs obligatoires SAUF l'image<br>3. Enregistrer la recette<br>4. Consulter la recette dans la liste |
| **Resultat attendu** | La recette est creee avec succes. Une image placeholder s'affiche a la place de la photo manquante. |
| **Status** | A tester |

---

### UT-011: Modifier une recette existante
| Champ | Valeur |
|-------|--------|
| **Priorite** | Critique |
| **Etapes** | 1. Naviguer vers "Mes Recettes"<br>2. Appuyer sur une recette personnelle existante<br>3. Appuyer sur "Modifier"<br>4. Verifier que tous les champs sont pre-remplis<br>5. Modifier le titre: ajouter "(version 2)"<br>6. Ajouter un nouvel ingredient<br>7. Appuyer sur "Enregistrer les modifications" |
| **Resultat attendu** | L'ecran d'edition s'ouvre avec tous les champs pre-remplis. Les modifications sont sauvegardees. Le nouveau titre et l'ingredient ajoute sont visibles. |
| **Status** | A tester |

---

### UT-012: Supprimer une recette avec confirmation
| Champ | Valeur |
|-------|--------|
| **Priorite** | Critique |
| **Etapes** | 1. Naviguer vers "Mes Recettes"<br>2. Appuyer sur une recette personnelle<br>3. Appuyer sur "Modifier" puis "Supprimer la recette"<br>4. Observer la boite de dialogue de confirmation<br>5. Appuyer sur "Annuler"<br>6. Verifier que la recette existe toujours<br>7. Repeter etapes 3-4 et appuyer sur "Supprimer"<br>8. Verifier que la recette n'existe plus |
| **Resultat attendu** | Une confirmation est demandee avant suppression. "Annuler" garde la recette. "Supprimer" efface definitivement la recette et ses ingredients/etapes. |
| **Status** | A tester |

---

### UT-013: Badge "Ma recette" sur les cartes
| Champ | Valeur |
|-------|--------|
| **Priorite** | Importante |
| **Etapes** | 1. Creer une recette personnelle<br>2. Naviguer vers "Mes Recettes"<br>3. Observer la carte de la recette creee<br>4. Comparer avec une recette API dans les resultats de recherche |
| **Resultat attendu** | Les recettes personnelles affichent un badge "Ma recette" (fond jaune clair, texte marron) en haut a gauche de la carte. Les recettes API n'ont pas ce badge. |
| **Status** | A tester |

---

### UT-014: Dupliquer (Fork) une recette API
| Champ | Valeur |
|-------|--------|
| **Priorite** | Critique |
| **Etapes** | 1. Rechercher une recette via la recherche (ex: "Poulet")<br>2. Ouvrir une recette provenant de TheMealDB (pas de badge "Ma recette")<br>3. Appuyer sur le bouton "Dupliquer"<br>4. Attendre la creation<br>5. Verifier que l'ecran d'edition s'ouvre avec les donnees pre-remplies<br>6. Modifier le titre pour ajouter "(ma version)"<br>7. Enregistrer |
| **Resultat attendu** | Un toast confirme "Recette dupliquee dans vos recettes personnelles". L'ecran d'edition s'ouvre avec les ingredients et etapes de la recette originale. La recette modifiee apparait dans "Mes Recettes" avec le badge. |
| **Status** | A tester |

---

### UT-015: Recherche unifiee - Recettes personnelles et API
| Champ | Valeur |
|-------|--------|
| **Priorite** | Critique |
| **Etapes** | 1. Creer une recette personnelle avec le titre "Tarte maison"<br>2. Aller a la recherche<br>3. Rechercher "Tarte"<br>4. Observer les resultats |
| **Resultat attendu** | Les resultats contiennent a la fois la recette personnelle "Tarte maison" (avec badge) et les recettes API contenant "Tarte" (sans badge). |
| **Status** | A tester |

---

### UT-016: Recettes personnelles privees entre utilisateurs
| Champ | Valeur |
|-------|--------|
| **Priorite** | Critique |
| **Etapes** | 1. Utilisateur A: creer une recette "Recette secrete A"<br>2. Se deconnecter<br>3. Se connecter avec Utilisateur B<br>4. Rechercher "Recette secrete"<br>5. Aller dans "Mes Recettes" |
| **Resultat attendu** | Utilisateur B ne voit pas "Recette secrete A" ni dans la recherche ni dans ses recettes. Les recettes personnelles sont privees par utilisateur. |
| **Status** | A tester |

---

### UT-017: Ajouter une recette personnelle au planning
| Champ | Valeur |
|-------|--------|
| **Priorite** | Importante |
| **Etapes** | 1. Creer une recette personnelle<br>2. Naviguer vers le planning hebdomadaire<br>3. Selectionner un creneau (ex: Lundi midi)<br>4. Rechercher la recette personnelle creee<br>5. Ajouter la recette au creneau |
| **Resultat attendu** | La recette personnelle peut etre ajoutee au planning comme une recette API. Elle s'affiche dans le creneau avec le badge "Ma recette". |
| **Status** | A tester |

---

### UT-018: Limite de taille image (5MB)
| Champ | Valeur |
|-------|--------|
| **Priorite** | Importante |
| **Etapes** | 1. Naviguer vers "Creer une recette"<br>2. Appuyer sur ajout d'image<br>3. Selectionner une image tres grande (> 5MB) depuis la galerie<br>4. Observer le comportement |
| **Resultat attendu** | L'application compresse l'image automatiquement OU affiche un message d'erreur indiquant que l'image depasse la limite de 5MB et demande d'en choisir une autre. |
| **Status** | A tester |

---

### UT-019: Navigation retour sans perte de donnees
| Champ | Valeur |
|-------|--------|
| **Priorite** | Normale |
| **Etapes** | 1. Naviguer vers "Creer une recette"<br>2. Remplir le titre et quelques champs<br>3. Appuyer sur le bouton retour<br>4. Observer le comportement |
| **Resultat attendu** | Une alerte demande si l'utilisateur veut quitter sans sauvegarder. Si "Rester", les donnees sont conservees. Si "Quitter", retour sans sauvegarde. |
| **Status** | A tester |

---

### UT-020: Affichage des erreurs de validation inline
| Champ | Valeur |
|-------|--------|
| **Priorite** | Normale |
| **Etapes** | 1. Naviguer vers "Creer une recette"<br>2. Appuyer sur "Enregistrer" sans remplir le formulaire<br>3. Observer l'affichage des erreurs<br>4. Commencer a taper dans le champ titre<br>5. Observer si l'erreur disparait |
| **Resultat attendu** | Les erreurs s'affichent en rouge sous chaque champ invalide. Le champ a un contour rouge. Quand l'utilisateur commence a corriger, l'erreur disparait. |
| **Status** | A tester |

---

## Resume

| Priorite | Nombre de tests |
|----------|-----------------|
| Critique | 10 |
| Importante | 8 |
| Normale | 2 |
| **Total** | **20** |

---

## Notes
- Ces tests doivent etre executes sur iOS et Android
- Tester en mode portrait et paysage pour les ecrans de formulaire
- Verifier l'accessibilite (VoiceOver / TalkBack) pour les champs de formulaire
- Tester avec differentes tailles d'ecran (petit telephone, grand telephone, tablette)
- Verifier le comportement offline: message d'erreur clair si pas de connexion
