# Plan de Tests : Filtrage des Recettes par Preferences

## Metadonnees
- **Feature**: Recipe Filtering by Preferences
- **Spec**: agent-os/specs/2026-01-03-recipe-filtering/spec.md
- **Requirements**: agent-os/specs/2026-01-03-recipe-filtering/planning/requirements.md
- **Cree le**: 2026-01-03
- **Status**: Planification Complete

---

## Resume des Tests

| Groupe | Critique | Haute | Moyenne | Total |
|--------|----------|-------|---------|-------|
| Groupe 1: Mappings | 3 | 4 | 1 | 8 |
| Groupe 2: RecipeFilterService | 6 | 5 | 3 | 14 |
| Groupe 3: Integration API | 5 | 4 | 2 | 11 |
| **Total** | **14** | **13** | **6** | **33** |

**Objectifs de Couverture:**
- Chemins critiques: 100%
- Haute priorite: 100%
- Moyenne priorite: 80%
- Couverture code: >80% pour nouveaux fichiers

---

## Commandes d'Execution

```bash
# Executer tous les tests
cd /Users/cedricgicquiaud/Desktop/DESKTOP/GIVEME5/PROJETS_WINDSURF/ForkIt/backend
pytest tests/test_ingredient_mappings.py tests/test_recipe_filter_service.py tests/test_recipes_filtering.py -v

# Groupe 1: Tests des Mappings
pytest tests/test_ingredient_mappings.py -v

# Groupe 2: Tests du RecipeFilterService
pytest tests/test_recipe_filter_service.py -v

# Groupe 3: Tests d'Integration API
pytest tests/test_recipes_filtering.py -v

# Avec couverture
pytest tests/test_ingredient_mappings.py tests/test_recipe_filter_service.py tests/test_recipes_filtering.py --cov=app/services --cov-report=term-missing
```

---

## Groupe 1 : Tests des Mappings (8 tests)

**Fichier**: `backend/tests/test_ingredient_mappings.py`
**Dependances**: Aucune

### DIETARY_EXCLUSIONS Mapping (4 tests)

#### TM-001: test_dietary_exclusions_vegetarian_contains_meat_ingredients
**Priorite:** Critique
**ID Test:** TM-001
**Given:**
- Import de `DIETARY_EXCLUSIONS` depuis `ingredient_mappings.py`
- Cle `DietaryType.VEGETARIAN` presente dans le dictionnaire
**When:**
- Acceder a `DIETARY_EXCLUSIONS[DietaryType.VEGETARIAN]`
**Then:**
- La liste contient au minimum: "chicken", "beef", "pork", "lamb", "duck", "turkey", "veal", "bacon", "ham"
- Chaque ingredient est en lowercase
- La liste n'est pas vide
**Requirement:** spec.md "Dictionnaires de mapping des preferences > DIETARY_EXCLUSIONS"

---

#### TM-002: test_dietary_exclusions_vegan_contains_all_animal_products
**Priorite:** Critique
**ID Test:** TM-002
**Given:**
- Import de `DIETARY_EXCLUSIONS` depuis `ingredient_mappings.py`
- Cle `DietaryType.VEGAN` presente dans le dictionnaire
**When:**
- Acceder a `DIETARY_EXCLUSIONS[DietaryType.VEGAN]`
**Then:**
- La liste contient les viandes: "chicken", "beef", "pork", "lamb"
- La liste contient les produits laitiers: "milk", "cheese", "cream", "butter", "yogurt"
- La liste contient: "egg", "honey"
- Total: au moins 15 ingredients
**Requirement:** requirements.md "Vegetalien -> exclut: tous les produits animaux"

---

#### TM-003: test_dietary_exclusions_halal_excludes_pork_and_alcohol
**Priorite:** Critique
**ID Test:** TM-003
**Given:**
- Import de `DIETARY_EXCLUSIONS` depuis `ingredient_mappings.py`
- Cle `DietaryType.HALAL` presente dans le dictionnaire
**When:**
- Acceder a `DIETARY_EXCLUSIONS[DietaryType.HALAL]`
**Then:**
- La liste contient les derives du porc: "pork", "bacon", "ham", "lard", "pancetta", "prosciutto"
- La liste contient l'alcool: "wine", "beer", "alcohol"
**Requirement:** requirements.md "halal -> exclut: pork, bacon, ham, lard, alcohol, wine"

---

#### TM-004: test_dietary_exclusions_all_seven_types_defined
**Priorite:** Haute
**ID Test:** TM-004
**Given:**
- Import de `DIETARY_EXCLUSIONS` depuis `ingredient_mappings.py`
- Liste des 7 types de regime: VEGETARIAN, VEGAN, NO_PORK, NO_BEEF, PESCETARIAN, HALAL, KOSHER
**When:**
- Iterer sur les 7 `DietaryType` enum values
**Then:**
- Chaque type a une entree dans `DIETARY_EXCLUSIONS`
- Chaque liste associee n'est pas vide
- Total: 7 entrees dans le dictionnaire
**Requirement:** spec.md "7 types de regime"

---

### ALLERGEN_KEYWORDS Mapping (3 tests)

#### TM-005: test_allergen_keywords_gluten_contains_wheat_derivatives
**Priorite:** Haute
**ID Test:** TM-005
**Given:**
- Import de `ALLERGEN_KEYWORDS` depuis `ingredient_mappings.py`
- Cle `AllergyType.GLUTEN` presente dans le dictionnaire
**When:**
- Acceder a `ALLERGEN_KEYWORDS[AllergyType.GLUTEN]`
**Then:**
- La liste contient: "wheat", "flour", "bread", "pasta", "semolina", "couscous", "barley", "rye"
- Minimum 8 mots-cles
**Requirement:** requirements.md "gluten -> wheat, flour, bread, pasta, semolina, couscous"

---

#### TM-006: test_allergen_keywords_lactose_contains_dairy_products
**Priorite:** Haute
**ID Test:** TM-006
**Given:**
- Import de `ALLERGEN_KEYWORDS` depuis `ingredient_mappings.py`
- Cle `AllergyType.LACTOSE` presente dans le dictionnaire
**When:**
- Acceder a `ALLERGEN_KEYWORDS[AllergyType.LACTOSE]`
**Then:**
- La liste contient: "milk", "cheese", "cream", "butter", "yogurt", "whey"
- Minimum 6 mots-cles
**Requirement:** requirements.md "lactose -> milk, cheese, cream, butter, yogurt, whey"

---

#### TM-007: test_allergen_keywords_all_eleven_types_defined
**Priorite:** Haute
**ID Test:** TM-007
**Given:**
- Import de `ALLERGEN_KEYWORDS` depuis `ingredient_mappings.py`
- Liste des 11 types d'allergies: GLUTEN, LACTOSE, TREE_NUTS, PEANUTS, EGGS, FISH, SHELLFISH, SOY, SESAME, MUSTARD, CELERY
**When:**
- Iterer sur les 11 `AllergyType` enum values
**Then:**
- Chaque type a une entree dans `ALLERGEN_KEYWORDS`
- Chaque liste associee n'est pas vide
- Total: 11 entrees dans le dictionnaire
**Requirement:** spec.md "11 types d'allergies"

---

### EXCEPTIONS Mapping (1 test)

#### TM-008: test_exceptions_prevents_false_positives
**Priorite:** Moyenne
**ID Test:** TM-008
**Given:**
- Import de `EXCEPTIONS` depuis `ingredient_mappings.py`
- Dictionnaire avec format: `{"ingredient_name": ["allergy_to_ignore", ...]}`
**When:**
- Verifier les entrees communes
**Then:**
- "coconut milk" exclut "lactose" (n'est pas du lait animal)
- "coconut cream" exclut "lactose"
- "eggplant" ou "egg plant" exclut "eggs" (c'est un legume)
- "egg noodles" peut etre absent (contient reellement des oeufs)
**Requirement:** requirements.md "Faux positifs potentiels > Coconut milk n'est pas du lait animal"

---

## Groupe 2 : Tests du RecipeFilterService (14 tests)

**Fichier**: `backend/tests/test_recipe_filter_service.py`
**Dependances**: Groupe 1

### Filtrage par Preferences Alimentaires (4 tests)

#### TS-001: test_filter_recipes_vegetarian_excludes_meat_recipes
**Priorite:** Critique
**ID Test:** TS-001
**Given:**
- Liste de 3 recettes:
  - Recipe A: ingredients = ["rice", "vegetables", "tofu"]
  - Recipe B: ingredients = ["chicken breast", "rice", "vegetables"]
  - Recipe C: ingredients = ["pasta", "tomato sauce", "cheese"]
- UserPreferencesResponse avec `dietary_preferences = [DietaryType.VEGETARIAN]`
**When:**
- Appeler `RecipeFilterService.filter_recipes(recipes, preferences)`
**Then:**
- Retourne 2 recettes: Recipe A et Recipe C
- Recipe B est exclue (contient "chicken")
**Requirement:** spec.md "Filtrage cumulatif"

---

#### TS-002: test_filter_recipes_vegan_excludes_all_animal_products
**Priorite:** Critique
**ID Test:** TS-002
**Given:**
- Liste de 4 recettes:
  - Recipe A: ingredients = ["rice", "vegetables", "tofu"]
  - Recipe B: ingredients = ["pasta", "cheese", "tomato"]
  - Recipe C: ingredients = ["salad", "olive oil", "lemon"]
  - Recipe D: ingredients = ["pancakes", "milk", "egg"]
**When:**
- Appeler `RecipeFilterService.filter_recipes(recipes, preferences)` avec `dietary_preferences = [DietaryType.VEGAN]`
**Then:**
- Retourne 2 recettes: Recipe A et Recipe C
- Recipe B exclue (cheese)
- Recipe D exclue (milk, egg)
**Requirement:** requirements.md "US4: Utilisateur vegetarien et allergique au gluten"

---

#### TS-003: test_filter_recipes_halal_excludes_pork_and_alcohol
**Priorite:** Critique
**ID Test:** TS-003
**Given:**
- Liste de 3 recettes:
  - Recipe A: ingredients = ["chicken", "rice", "vegetables"]
  - Recipe B: ingredients = ["bacon", "eggs", "toast"]
  - Recipe C: ingredients = ["beef", "red wine", "mushrooms"]
**When:**
- Appeler avec `dietary_preferences = [DietaryType.HALAL]`
**Then:**
- Retourne 1 recette: Recipe A
- Recipe B exclue (bacon)
- Recipe C exclue (wine)
**Requirement:** requirements.md "US3: Utilisateur halal"

---

#### TS-004: test_filter_recipes_pescetarian_allows_fish_excludes_meat
**Priorite:** Haute
**ID Test:** TS-004
**Given:**
- Liste de 3 recettes:
  - Recipe A: ingredients = ["salmon", "lemon", "dill"]
  - Recipe B: ingredients = ["shrimp", "garlic", "pasta"]
  - Recipe C: ingredients = ["chicken", "vegetables"]
**When:**
- Appeler avec `dietary_preferences = [DietaryType.PESCETARIAN]`
**Then:**
- Retourne 2 recettes: Recipe A et Recipe B
- Recipe C exclue (chicken = viande terrestre)
**Requirement:** requirements.md "pescetarian -> exclut: viandes terrestres (permet poissons)"

---

### Filtrage par Allergies (4 tests)

#### TS-005: test_filter_recipes_gluten_allergy_excludes_wheat_products
**Priorite:** Critique
**ID Test:** TS-005
**Given:**
- Liste de 3 recettes:
  - Recipe A: ingredients = ["rice", "chicken", "vegetables"]
  - Recipe B: ingredients = ["pasta", "tomato sauce", "cheese"]
  - Recipe C: ingredients = ["bread crumbs", "fish", "lemon"]
**When:**
- Appeler avec `allergies = [AllergyType.GLUTEN]`
**Then:**
- Retourne 1 recette: Recipe A
- Recipe B exclue (pasta)
- Recipe C exclue (bread)
**Requirement:** requirements.md "gluten -> wheat, flour, bread, pasta"

---

#### TS-006: test_filter_recipes_lactose_allergy_excludes_dairy
**Priorite:** Critique
**ID Test:** TS-006
**Given:**
- Liste de 3 recettes:
  - Recipe A: ingredients = ["chicken", "olive oil", "herbs"]
  - Recipe B: ingredients = ["pasta", "cream", "parmesan"]
  - Recipe C: ingredients = ["salad", "feta cheese", "olives"]
**When:**
- Appeler avec `allergies = [AllergyType.LACTOSE]`
**Then:**
- Retourne 1 recette: Recipe A
- Recipe B exclue (cream)
- Recipe C exclue (cheese)
**Requirement:** requirements.md "lactose -> milk, cheese, cream, butter"

---

#### TS-007: test_filter_recipes_peanut_allergy_excludes_peanuts
**Priorite:** Haute
**ID Test:** TS-007
**Given:**
- Liste de 2 recettes:
  - Recipe A: ingredients = ["pad thai", "shrimp", "peanuts"]
  - Recipe B: ingredients = ["stir fry", "tofu", "sesame oil"]
**When:**
- Appeler avec `allergies = [AllergyType.PEANUTS]`
**Then:**
- Retourne 1 recette: Recipe B
- Recipe A exclue (peanuts)
**Requirement:** requirements.md "peanuts -> peanut, groundnut"

---

#### TS-008: test_filter_recipes_multiple_allergies_cumulative
**Priorite:** Haute
**ID Test:** TS-008
**Given:**
- Liste de 4 recettes:
  - Recipe A: ingredients = ["rice", "vegetables", "tofu"]
  - Recipe B: ingredients = ["pasta", "tomato"]  # gluten
  - Recipe C: ingredients = ["salad", "milk dressing"]  # lactose
  - Recipe D: ingredients = ["bread", "butter"]  # gluten + lactose
**When:**
- Appeler avec `allergies = [AllergyType.GLUTEN, AllergyType.LACTOSE]`
**Then:**
- Retourne 1 recette: Recipe A
- Les 3 autres exclues (B: gluten, C: lactose, D: les deux)
**Requirement:** spec.md "Le filtrage est cumulatif"

---

### Filtrage par Ingredients Exclus (2 tests)

#### TS-009: test_filter_recipes_excluded_ingredients_removes_matching
**Priorite:** Critique
**ID Test:** TS-009
**Given:**
- Liste de 3 recettes:
  - Recipe A: ingredients = ["chicken", "rice", "broccoli"]
  - Recipe B: ingredients = ["pasta", "garlic", "olive oil"]
  - Recipe C: ingredients = ["fish", "garlic", "lemon"]
**When:**
- Appeler avec `excluded_ingredients = ["garlic"]`
**Then:**
- Retourne 1 recette: Recipe A
- Recipe B et C exclues (contiennent garlic)
**Requirement:** spec.md "Filtrage par ingredients exclus manuellement"

---

#### TS-010: test_filter_recipes_excluded_ingredients_partial_match
**Priorite:** Haute
**ID Test:** TS-010
**Given:**
- Liste de 2 recettes:
  - Recipe A: ingredients = ["Garlic Powder", "chicken", "rice"]
  - Recipe B: ingredients = ["pasta", "tomato", "basil"]
**When:**
- Appeler avec `excluded_ingredients = ["garlic"]`
**Then:**
- Retourne 1 recette: Recipe B
- Recipe A exclue ("Garlic Powder" contient "garlic")
**Requirement:** spec.md "Matching partiel"

---

### Cas Limites (4 tests)

#### TS-011: test_filter_recipes_empty_list_returns_empty
**Priorite:** Moyenne
**ID Test:** TS-011
**Given:**
- Liste vide de recettes: `[]`
- UserPreferencesResponse avec des preferences quelconques
**When:**
- Appeler `RecipeFilterService.filter_recipes([], preferences)`
**Then:**
- Retourne liste vide `[]`
- Pas d'exception levee
**Requirement:** spec.md "Gestion des listes vides"

---

#### TS-012: test_filter_recipes_no_preferences_returns_all
**Priorite:** Haute
**ID Test:** TS-012
**Given:**
- Liste de 3 recettes quelconques
- UserPreferencesResponse vide: `dietary_preferences=[], allergies=[], excluded_ingredients=[]`
**When:**
- Appeler `RecipeFilterService.filter_recipes(recipes, empty_preferences)`
**Then:**
- Retourne les 3 recettes originales
- Aucune recette filtree
**Requirement:** requirements.md "Test sans preferences (retourne tout)"

---

#### TS-013: test_filter_recipes_case_insensitive_matching
**Priorite:** Moyenne
**ID Test:** TS-013
**Given:**
- Liste de 2 recettes:
  - Recipe A: ingredients = ["CHICKEN BREAST", "Rice", "VeGetAbles"]
  - Recipe B: ingredients = ["pasta", "TOMATO", "cheese"]
**When:**
- Appeler avec `dietary_preferences = [DietaryType.VEGETARIAN]`
**Then:**
- Retourne 1 recette: Recipe B
- Recipe A exclue malgre la casse differente ("CHICKEN" detecte)
**Requirement:** spec.md "Comparaison case-insensitive (normaliser en lowercase)"

---

#### TS-014: test_filter_recipes_exception_coconut_milk_not_lactose
**Priorite:** Moyenne
**ID Test:** TS-014
**Given:**
- Liste de 2 recettes:
  - Recipe A: ingredients = ["curry", "coconut milk", "vegetables"]
  - Recipe B: ingredients = ["pasta", "cow milk", "cheese"]
**When:**
- Appeler avec `allergies = [AllergyType.LACTOSE]`
**Then:**
- Retourne 1 recette: Recipe A
- Recipe A conservee ("coconut milk" n'est pas du lait animal)
- Recipe B exclue ("milk", "cheese")
**Requirement:** requirements.md "Faux positifs > Coconut milk n'est pas du lait animal"

---

## Groupe 3 : Tests d'Integration API (11 tests)

**Fichier**: `backend/tests/test_recipes_filtering.py`
**Dependances**: Groupe 2

### Endpoint /search avec Authentification (3 tests)

#### TI-001: test_search_authenticated_user_filters_by_preferences
**Priorite:** Critique
**ID Test:** TI-001
**Given:**
- Utilisateur authentifie avec token JWT valide
- Preferences utilisateur en base: `dietary_preferences = [DietaryType.VEGETARIAN]`
- TheMealDB retourne 5 recettes (3 avec viande, 2 vegetariennes)
**When:**
- `GET /api/recipes/search?query=curry` avec header `Authorization: Bearer <token>`
**Then:**
- Status: 200 OK
- Body: liste de 2 recettes (vegetariennes uniquement)
- Les 3 recettes avec viande sont exclues
**Requirement:** spec.md "Si utilisateur authentifie : appliquer le filtrage"

---

#### TI-002: test_search_unauthenticated_returns_all_recipes
**Priorite:** Critique
**ID Test:** TI-002
**Given:**
- Pas de header Authorization
- TheMealDB retourne 5 recettes
**When:**
- `GET /api/recipes/search?query=curry` sans authentification
**Then:**
- Status: 200 OK
- Body: liste de 5 recettes (aucun filtrage)
- Toutes les recettes de TheMealDB sont retournees
**Requirement:** spec.md "Si utilisateur non authentifie : retourner les recettes sans filtrage"

---

#### TI-003: test_search_authenticated_no_matching_recipes_returns_empty
**Priorite:** Haute
**ID Test:** TI-003
**Given:**
- Utilisateur authentifie
- Preferences tres restrictives: vegan + gluten + lactose allergies
- TheMealDB retourne 5 recettes qui contiennent toutes des allergenes
**When:**
- `GET /api/recipes/search?query=pasta` avec authentification
**Then:**
- Status: 200 OK
- Body: liste vide `[]`
- Pas d'erreur (comportement attendu)
**Requirement:** spec.md "Gestion des listes vides > retourner une liste vide []"

---

### Endpoint /random avec Retry Logic (4 tests)

#### TI-004: test_random_authenticated_returns_compatible_recipe
**Priorite:** Critique
**ID Test:** TI-004
**Given:**
- Utilisateur authentifie avec `dietary_preferences = [DietaryType.VEGETARIAN]`
- Mock TheMealDB pour retourner une recette vegetarienne au 1er appel
**When:**
- `GET /api/recipes/random` avec authentification
**Then:**
- Status: 200 OK
- Body: `{"recipe": {...}}` avec recette vegetarienne
- TheMealDB appele 1 fois
**Requirement:** spec.md "/random doit retourner une recette compatible"

---

#### TI-005: test_random_retries_on_incompatible_recipe
**Priorite:** Critique
**ID Test:** TI-005
**Given:**
- Utilisateur authentifie vegetarien
- Mock TheMealDB pour retourner:
  - 1er appel: recette avec chicken (incompatible)
  - 2eme appel: recette avec beef (incompatible)
  - 3eme appel: recette vegetarienne (compatible)
**When:**
- `GET /api/recipes/random` avec authentification
**Then:**
- Status: 200 OK
- Body: recette vegetarienne du 3eme appel
- TheMealDB appele 3 fois
**Requirement:** spec.md "Si la recette aleatoire est incompatible : fetch jusqu'a 10 recettes"

---

#### TI-006: test_random_max_10_attempts_returns_null
**Priorite:** Haute
**ID Test:** TI-006
**Given:**
- Utilisateur authentifie avec preferences tres restrictives
- Mock TheMealDB pour retourner 10 recettes incompatibles
**When:**
- `GET /api/recipes/random` avec authentification
**Then:**
- Status: 200 OK
- Body: `{"recipe": null}`
- TheMealDB appele exactement 10 fois (pas plus)
**Requirement:** spec.md "Si aucune compatible apres 10 tentatives : retourner recipe: null"

---

#### TI-007: test_random_unauthenticated_no_retry_logic
**Priorite:** Haute
**ID Test:** TI-007
**Given:**
- Pas de header Authorization
- TheMealDB retourne une recette avec viande
**When:**
- `GET /api/recipes/random` sans authentification
**Then:**
- Status: 200 OK
- Body: recette retournee directement (meme avec viande)
- TheMealDB appele 1 fois uniquement
- Pas de retry logic
**Requirement:** requirements.md "US5: Utilisateur non connecte"

---

### Endpoint /category/{name} (2 tests)

#### TI-008: test_category_authenticated_filters_recipes
**Priorite:** Haute
**ID Test:** TI-008
**Given:**
- Utilisateur authentifie avec `allergies = [AllergyType.GLUTEN]`
- Categorie "Pasta" retourne 5 recettes (toutes avec pasta/flour)
**When:**
- `GET /api/recipes/category/Pasta` avec authentification
**Then:**
- Status: 200 OK
- Body: liste potentiellement vide ou reduite
- Les recettes avec gluten sont filtrees
**Requirement:** spec.md "Endpoints concernes: /category/{name}"

---

#### TI-009: test_category_unauthenticated_returns_all
**Priorite:** Moyenne
**ID Test:** TI-009
**Given:**
- Pas de header Authorization
- Categorie "Chicken" retourne 5 recettes
**When:**
- `GET /api/recipes/category/Chicken` sans authentification
**Then:**
- Status: 200 OK
- Body: 5 recettes (pas de filtrage)
**Requirement:** spec.md "Si utilisateur non authentifie : comportement actuel"

---

### Dependance get_optional_user (2 tests)

#### TI-010: test_get_optional_user_with_valid_token_returns_user
**Priorite:** Critique
**ID Test:** TI-010
**Given:**
- Token JWT valide dans header Authorization
- Utilisateur existant en base
**When:**
- Appeler la dependance `get_optional_user()` depuis une route
**Then:**
- Retourne `UserResponse` avec user_id correct
- Pas d'exception levee
**Requirement:** spec.md "Retourne UserResponse | None selon presence du header"

---

#### TI-011: test_get_optional_user_without_token_returns_none
**Priorite:** Moyenne
**ID Test:** TI-011
**Given:**
- Pas de header Authorization dans la requete
**When:**
- Appeler la dependance `get_optional_user()` depuis une route
**Then:**
- Retourne `None`
- Pas d'exception 401 levee (contrairement a `get_current_user`)
**Requirement:** spec.md "Ne pas lever d'erreur si non authentifie"

---

## Dependances des Tests

```
Groupe 1: Mappings
    |
    +-- TM-001 a TM-008
    |
    v
Groupe 2: RecipeFilterService (depend de Groupe 1)
    |
    +-- TS-001 a TS-014
    |
    v
Groupe 3: Integration API (depend de Groupe 2)
    |
    +-- TI-001 a TI-011
```

**Ordre d'execution recommande:**
1. Executer Groupe 1 en premier
2. Si Groupe 1 passe, executer Groupe 2
3. Si Groupe 2 passe, executer Groupe 3
4. Validation finale: tous les groupes ensemble

---

## Donnees de Test Requises

### Fixtures Pytest

```python
# tests/conftest.py - Nouvelles fixtures

@pytest.fixture
def sample_recipes():
    """Liste de recettes pour tests de filtrage."""
    return [
        Recipe(id="1", name="Vegetable Curry", ingredients=[
            Ingredient(name="rice"), Ingredient(name="vegetables"), Ingredient(name="tofu")
        ]),
        Recipe(id="2", name="Chicken Stir Fry", ingredients=[
            Ingredient(name="chicken breast"), Ingredient(name="rice"), Ingredient(name="vegetables")
        ]),
        Recipe(id="3", name="Pasta Carbonara", ingredients=[
            Ingredient(name="pasta"), Ingredient(name="bacon"), Ingredient(name="cheese")
        ]),
    ]

@pytest.fixture
def vegetarian_preferences():
    """Preferences utilisateur vegetarien."""
    return UserPreferencesResponse(
        dietary_preferences=[DietaryType.VEGETARIAN],
        allergies=[],
        excluded_ingredients=[],
        preferred_ingredients=[],
        portions_count=2
    )

@pytest.fixture
def vegan_gluten_free_preferences():
    """Preferences strictes: vegan + sans gluten."""
    return UserPreferencesResponse(
        dietary_preferences=[DietaryType.VEGAN],
        allergies=[AllergyType.GLUTEN],
        excluded_ingredients=[],
        preferred_ingredients=[],
        portions_count=2
    )

@pytest.fixture
def empty_preferences():
    """Preferences vides (aucun filtrage)."""
    return UserPreferencesResponse(
        dietary_preferences=[],
        allergies=[],
        excluded_ingredients=[],
        preferred_ingredients=[],
        portions_count=2
    )
```

### Mocks TheMealDB

```python
@pytest.fixture
def mock_themealdb_vegetarian_response():
    """Mock reponse TheMealDB avec recette vegetarienne."""
    return {
        "meals": [{
            "idMeal": "12345",
            "strMeal": "Vegetable Curry",
            "strIngredient1": "Rice",
            "strIngredient2": "Vegetables",
            "strIngredient3": "Coconut Milk",
            # ...
        }]
    }

@pytest.fixture
def mock_themealdb_meat_response():
    """Mock reponse TheMealDB avec recette contenant viande."""
    return {
        "meals": [{
            "idMeal": "67890",
            "strMeal": "Chicken Curry",
            "strIngredient1": "Chicken Breast",
            "strIngredient2": "Rice",
            # ...
        }]
    }
```

---

## Hors Perimetre

Tests explicitement **NON inclus** dans ce plan:

- **Tests de performance**: Verification du temps < 500ms (dedie phase QA)
- **Tests de charge**: Multiple utilisateurs simultanement
- **Tests UI/Mobile**: Aucun changement frontend pour cette feature
- **Tests de cache**: Le cache est hors scope du POC
- **Tests d'accessibilite**: Pas d'UI impactee
- **Tests de traduction**: Les ingredients restent en anglais
- **Tests de compatibilite navigateur**: Backend uniquement

---

## Criteres de Validation Finale

- [ ] 33/33 tests passent (100%)
- [ ] Couverture code > 80% pour:
  - `ingredient_mappings.py`: 100%
  - `recipe_filter_service.py`: > 90%
  - Modifications `recipes.py`: > 80%
- [ ] Aucune regression sur tests existants
- [ ] Linting ruff passe sans erreur
- [ ] Tests executes en < 30 secondes

---

*Document genere le: 2026-01-03*
*Spec: Recipe Filtering by Preferences*
