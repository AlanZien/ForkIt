# Tests Utilisateur - Recipe Browsing

## Feature
**Nom:** Recipe Browsing
**Date:** 2026-01-02
**Status:** Pret pour tests

---

## Prerequis
- Application mobile ForkIt installee
- Connexion internet active
- Backend demarre sur localhost:8000

---

## Scenarios de Test

### UT-001: Affichage des categories
| Champ | Valeur |
|-------|--------|
| **Priorite** | Haute |
| **Etapes** | 1. Ouvrir l'application<br>2. Naviguer vers l'onglet Recettes |
| **Resultat attendu** | Les categories s'affichent en scroll horizontal avec image et nom. La premiere categorie est selectionnee automatiquement |
| **Status** | A tester |

---

### UT-002: Selection d'une categorie
| Champ | Valeur |
|-------|--------|
| **Priorite** | Haute |
| **Etapes** | 1. Etre sur l'ecran Recettes<br>2. Cliquer sur une categorie (ex: Seafood) |
| **Resultat attendu** | La categorie devient teal avec bordure. Les recettes de cette categorie s'affichent en grille |
| **Status** | A tester |

---

### UT-003: Deselection d'une categorie
| Champ | Valeur |
|-------|--------|
| **Priorite** | Moyenne |
| **Etapes** | 1. Avoir une categorie selectionnee<br>2. Cliquer a nouveau sur la meme categorie |
| **Resultat attendu** | La categorie se deselectionne. La grille de recettes se vide |
| **Status** | A tester |

---

### UT-004: Recherche de recette
| Champ | Valeur |
|-------|--------|
| **Priorite** | Haute |
| **Etapes** | 1. Etre sur l'ecran Recettes<br>2. Saisir "Chicken" dans la barre de recherche<br>3. Appuyer sur Entree |
| **Resultat attendu** | Les recettes contenant "Chicken" s'affichent. Le titre indique "Resultats pour Chicken" |
| **Status** | A tester |

---

### UT-005: Recherche avec moins de 2 caracteres
| Champ | Valeur |
|-------|--------|
| **Priorite** | Moyenne |
| **Etapes** | 1. Saisir "A" dans la barre de recherche<br>2. Appuyer sur Entree |
| **Resultat attendu** | Aucune recherche n'est effectuee (minimum 2 caracteres requis) |
| **Status** | A tester |

---

### UT-006: Effacer la recherche
| Champ | Valeur |
|-------|--------|
| **Priorite** | Haute |
| **Etapes** | 1. Avoir effectue une recherche<br>2. Cliquer sur le X dans la barre de recherche |
| **Resultat attendu** | Le champ de recherche se vide. Les resultats se reintialisent |
| **Status** | A tester |

---

### UT-007: Affichage grille de recettes
| Champ | Valeur |
|-------|--------|
| **Priorite** | Haute |
| **Etapes** | 1. Selectionner une categorie avec des recettes |
| **Resultat attendu** | Les recettes s'affichent en grille 2 colonnes. Chaque carte montre l'image et le nom |
| **Status** | A tester |

---

### UT-008: Compteur de resultats
| Champ | Valeur |
|-------|--------|
| **Priorite** | Moyenne |
| **Etapes** | 1. Selectionner une categorie ou effectuer une recherche |
| **Resultat attendu** | Le nombre de recettes s'affiche (ex: "12 recettes") |
| **Status** | A tester |

---

### UT-009: Navigation vers detail recette
| Champ | Valeur |
|-------|--------|
| **Priorite** | Haute |
| **Etapes** | 1. Afficher une liste de recettes<br>2. Cliquer sur une carte de recette |
| **Resultat attendu** | Navigation vers l'ecran de detail de la recette |
| **Status** | A tester |

---

### UT-010: Affichage detail recette
| Champ | Valeur |
|-------|--------|
| **Priorite** | Haute |
| **Etapes** | 1. Naviguer vers le detail d'une recette |
| **Resultat attendu** | L'image s'affiche en grand. Le nom, categorie, origine sont visibles. La liste des ingredients et les instructions s'affichent |
| **Status** | A tester |

---

### UT-011: Liste des ingredients
| Champ | Valeur |
|-------|--------|
| **Priorite** | Haute |
| **Etapes** | 1. Etre sur le detail d'une recette<br>2. Consulter la section Ingredients |
| **Resultat attendu** | Chaque ingredient affiche son nom et sa quantite/mesure |
| **Status** | A tester |

---

### UT-012: Instructions de preparation
| Champ | Valeur |
|-------|--------|
| **Priorite** | Haute |
| **Etapes** | 1. Etre sur le detail d'une recette<br>2. Consulter la section Instructions |
| **Resultat attendu** | Les instructions de preparation s'affichent en texte complet |
| **Status** | A tester |

---

### UT-013: Retour depuis detail
| Champ | Valeur |
|-------|--------|
| **Priorite** | Haute |
| **Etapes** | 1. Etre sur le detail d'une recette<br>2. Cliquer sur le bouton Retour |
| **Resultat attendu** | Retour a la liste des recettes. L'etat precedent (categorie/recherche) est conserve |
| **Status** | A tester |

---

### UT-014: Etat de chargement categories
| Champ | Valeur |
|-------|--------|
| **Priorite** | Moyenne |
| **Etapes** | 1. Ouvrir l'onglet Recettes pour la premiere fois |
| **Resultat attendu** | Un indicateur de chargement s'affiche pendant le chargement des categories |
| **Status** | A tester |

---

### UT-015: Etat de chargement recettes
| Champ | Valeur |
|-------|--------|
| **Priorite** | Moyenne |
| **Etapes** | 1. Selectionner une categorie ou effectuer une recherche |
| **Resultat attendu** | Un indicateur de chargement s'affiche pendant le chargement des recettes |
| **Status** | A tester |

---

### UT-016: Etat vide - aucun resultat
| Champ | Valeur |
|-------|--------|
| **Priorite** | Moyenne |
| **Etapes** | 1. Rechercher un terme qui ne retourne aucun resultat (ex: "xyzabc123") |
| **Resultat attendu** | Message "Aucune recette trouvee" avec icone et suggestion |
| **Status** | A tester |

---

### UT-017: Gestion erreur reseau
| Champ | Valeur |
|-------|--------|
| **Priorite** | Moyenne |
| **Etapes** | 1. Desactiver le reseau/backend<br>2. Tenter de charger des recettes |
| **Resultat attendu** | Message d'erreur explicite affiche |
| **Status** | A tester |

---

### UT-018: Performance scroll categories
| Champ | Valeur |
|-------|--------|
| **Priorite** | Moyenne |
| **Etapes** | 1. Faire defiler les categories horizontalement |
| **Resultat attendu** | Le scroll est fluide sans saccades |
| **Status** | A tester |

---

### UT-019: Performance scroll recettes
| Champ | Valeur |
|-------|--------|
| **Priorite** | Moyenne |
| **Etapes** | 1. Charger une categorie avec beaucoup de recettes<br>2. Faire defiler la grille verticalement |
| **Resultat attendu** | Le scroll est fluide, les images se chargent progressivement |
| **Status** | A tester |

---

### UT-020: Recette aleatoire (API)
| Champ | Valeur |
|-------|--------|
| **Priorite** | Basse |
| **Etapes** | 1. Appeler GET /api/recipes/random |
| **Resultat attendu** | Une recette aleatoire est retournee avec tous ses details |
| **Status** | A tester |

---

## Resume

| Priorite | Nombre de tests |
|----------|-----------------|
| Haute | 11 |
| Moyenne | 8 |
| Basse | 1 |
| **Total** | **20** |

---

## Notes
- Ces tests doivent etre executes sur iOS et Android
- Tester avec differentes connexions reseau (WiFi, 4G, lent)
- Verifier le comportement avec des noms de recettes longs
