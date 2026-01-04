# Specification: Recipe Filtering by Preferences

## Goal

Filtrer automatiquement les recettes affichees dans l'application en fonction des preferences alimentaires (vegetarien, halal, etc.), des allergies et des ingredients exclus de l'utilisateur, afin de ne presenter que des recettes compatibles avec son profil.

## User Stories

- En tant qu'utilisateur vegetarien, je veux que les recettes contenant de la viande soient automatiquement exclues des resultats de recherche afin de ne voir que des options compatibles avec mon regime.
- En tant que parent d'un enfant allergique aux arachides, je veux que toutes les recettes contenant des arachides soient filtrees pour garantir la securite alimentaire de ma famille.
- En tant qu'utilisateur non connecte, je veux voir toutes les recettes disponibles sans aucun filtrage automatique.

## Specific Requirements

**Service de filtrage centralise (RecipeFilterService)**
- Creer un nouveau service `RecipeFilterService` dans `backend/app/services/`
- Le service recoit une liste de recettes et les preferences utilisateur
- Retourne uniquement les recettes compatibles avec toutes les preferences
- Utiliser des methodes privees pour chaque type de filtrage (dietary, allergies, excluded)
- Le filtrage est cumulatif : une recette doit passer tous les filtres

**Dictionnaires de mapping des preferences**
- Creer un fichier `backend/app/services/ingredient_mappings.py`
- Definir `DIETARY_EXCLUSIONS` : dict mappant chaque `DietaryType` a une liste d'ingredients a exclure
- Definir `ALLERGEN_KEYWORDS` : dict mappant chaque `AllergyType` a une liste de mots-cles
- Inclure les variantes courantes (ex: "chicken", "chicken breast", "chicken thigh")
- Gerer les exceptions comme "coconut milk" qui n'est pas du lait animal

**Integration dans les routes existantes**
- Modifier les endpoints dans `backend/app/routes/recipes.py`
- Ajouter un parametre optionnel d'authentification (current_user optionnel)
- Si utilisateur authentifie : appliquer le filtrage via RecipeFilterService
- Si utilisateur non authentifie : retourner les recettes sans filtrage
- Endpoints concernes : `/search`, `/random`, `/category/{name}`

**Detection optionnelle de l'utilisateur**
- Creer une dependance `get_optional_user` qui ne leve pas d'erreur si non authentifie
- Retourne `UserResponse | None` selon presence du header Authorization
- Reutiliser la logique existante de `get_current_user` dans `auth.py`

**Algorithme de matching des ingredients**
- Comparaison case-insensitive (normaliser en lowercase)
- Matching partiel : "Chicken Breast" contient "chicken" -> exclure
- Pour les recettes avec ingredients : utiliser `Recipe.ingredients[].name`
- Pour les recettes sans details (RecipeSummary) : fetch les details avant filtrage

**Gestion du endpoint random**
- `/random` doit retourner une recette compatible
- Si la recette aleatoire est incompatible : fetch jusqu'a 10 recettes aleatoires
- Si aucune compatible apres 10 tentatives : retourner `recipe: null`
- Eviter boucle infinie avec compteur de tentatives

**Gestion des listes vides**
- Si le filtrage exclut toutes les recettes, retourner une liste vide `[]`
- Le frontend affichera un message "Aucune recette trouvee avec vos preferences"
- Ne pas lever d'erreur, c'est un comportement attendu

**Performance et optimisation**
- Le filtrage est post-fetch (apres reception des donnees TheMealDB)
- Pas de cache des resultats filtres pour le POC
- Temps de reponse additionnel cible : < 500ms
- Logger les metriques de filtrage pour monitoring futur

## Visual Design

Aucun asset visuel fourni - le filtrage est transparent pour l'utilisateur.

**Comportement UX attendu**
- Le filtrage est automatique et silencieux
- Pas d'indicateur visuel du filtrage actif
- Message "Aucune recette trouvee" si liste vide (composant existant)

## Existing Code to Leverage

**backend/app/models/preferences.py**
- Contient `DietaryType` enum avec les 7 types de regime
- Contient `AllergyType` enum avec les 11 types d'allergies
- Contient `UserPreferencesResponse` a utiliser pour recuperer les preferences
- Fonction `normalize_ingredient()` a reutiliser pour le matching

**backend/app/services/preferences_service.py**
- `PreferencesService.get_preferences(user_id)` recupere toutes les preferences
- Retourne `UserPreferencesResponse` avec dietary, allergies, excluded_ingredients
- Deja integre avec Supabase, pret a l'emploi

**backend/app/routes/recipes.py**
- Structure existante des 5 endpoints a modifier
- Pattern de transformation TheMealDB -> RecipeSummary/Recipe
- Import de `themealdb_client` a reutiliser

**backend/app/models/recipe.py**
- `Recipe.from_api_response()` parse les ingredients depuis TheMealDB
- `Recipe.ingredients` est une liste de `Ingredient(name, measure)`
- Utiliser `ingredient.name` pour le matching

**backend/app/routes/auth.py**
- `get_current_user()` dependency a adapter pour version optionnelle
- Pattern d'extraction du token Bearer a reutiliser
- `UserResponse` contient `id` (user_id) necessaire pour fetch preferences

## Out of Scope

- Interface utilisateur pour activer/desactiver le filtrage manuellement
- Mode "voir tout avec avertissements" affichant les recettes incompatibles
- Filtrage par ingredients preferes (boost/promotion plutot qu'exclusion)
- Suggestions IA basees sur les preferences utilisateur
- Cache des resultats filtres par utilisateur
- Filtrage cote frontend/mobile
- Traduction des noms d'ingredients (rester en anglais comme TheMealDB)
- Modification des preferences depuis l'ecran de recettes
- Statistiques de filtrage visibles par l'utilisateur
- Nouvel endpoint `/api/recipes/for-me` (reserve pour iteration future)
