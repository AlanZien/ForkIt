# Exigences Spec : Recipe Filtering by Preferences

## Description Initiale

Recipe Filtering by Preferences - Filtrer les resultats de recherche de recettes et les suggestions en fonction des preferences alimentaires et des allergies de l'utilisateur. Exclure les recettes contenant des allergenes ou des ingredients incompatibles.

**Contexte:**
- ForkIt est une application mobile francaise de planification de repas (React Native + FastAPI + Supabase)
- Les utilisateurs ont deja un profil avec des preferences alimentaires (vegetarien, sans porc, halal, etc.) et des allergies (gluten, lactose, fruits a coque, etc.)
- La navigation des recettes avec TheMealDB est deja implementee
- Cette fonctionnalite doit filtrer les recettes en fonction des preferences stockees dans Supabase

---

## Discussion des Exigences

### Premiere Serie de Questions

**Q1:** Comment mapper les preferences utilisateur aux ingredients TheMealDB ?
**Reponse:** Creer un systeme de mapping avec des listes d'ingredients a exclure par preference:
- `vegetarian` -> exclut: chicken, beef, pork, lamb, etc.
- `vegan` -> exclut: tous les produits animaux (viandes + dairy, eggs, honey)
- `no_pork` / `halal` -> exclut: pork, bacon, ham, lard, etc.
- `no_beef` -> exclut: beef, veal, etc.
- `pescetarian` -> exclut: viandes terrestres (permet poissons)
- `kosher` -> exclut: shellfish, pork, melanges viande/lait

**Q2:** Comment detecter les allergenes dans les ingredients des recettes ?
**Reponse:** Utiliser des listes de mots-cles par allergene:
- `gluten` -> wheat, flour, bread, pasta, etc.
- `lactose` -> milk, cheese, cream, butter, yogurt, etc.
- `tree_nuts` -> almond, walnut, cashew, pistachio, etc.
- `peanuts` -> peanut, groundnut
- `eggs` -> egg, mayonnaise
- `fish` -> salmon, tuna, cod, etc.
- `shellfish` -> shrimp, crab, lobster, mussel, etc.
- `soy` -> soy, tofu, tempeh, edamame
- `sesame` -> sesame
- `mustard` -> mustard
- `celery` -> celery

**Q3:** Le filtrage doit-il etre cote backend ou frontend ?
**Reponse:** **Filtrage cote backend** pour:
- Eviter de transferer des donnees inutiles au mobile
- Centraliser la logique de filtrage
- Permettre l'evolution vers des suggestions IA futures
- Securite : ne pas exposer la logique de mapping au client

**Q4:** Comment afficher les recettes filtrees ?
**Reponse:** **Cacher completement** les recettes incompatibles:
- UX simple et claire pour les familles
- Eviter la confusion avec des avertissements
- L'utilisateur voit uniquement ce qu'il peut manger
- Option future : mode "voir tout" avec avertissements

**Q5:** Faut-il distinguer "preference stricte" vs "preference souple" ?
**Reponse:** Non, pour le POC toutes les preferences sont traitees comme strictes. L'utilisateur gere la flexibilite en modifiant ses preferences.

---

### Code Existant a Referencer

**Fonctionnalites Similaires Identifiees:**

- **Backend - Modeles de preferences:**
  - Path: `backend/app/models/preferences.py`
  - Contient: `DietaryType`, `AllergyType`, enums et modeles Pydantic

- **Backend - Service de preferences:**
  - Path: `backend/app/services/preferences_service.py`
  - Contient: Logique CRUD pour preferences utilisateur

- **Backend - Routes recettes:**
  - Path: `backend/app/routes/recipes.py`
  - Contient: Endpoints existants `/api/recipes/*`

- **Backend - Client TheMealDB:**
  - Path: `backend/app/services/themealdb.py`
  - Contient: `TheMealDBClient` avec methodes API

- **Backend - Modeles recettes:**
  - Path: `backend/app/models/recipe.py`
  - Contient: `Recipe`, `Ingredient`, `RecipeSummary`

- **Mobile - Types preferences:**
  - Path: `mobile/types/preferences.ts`
  - Contient: Types TypeScript alignes avec backend

- **Mobile - Service recettes:**
  - Path: `mobile/services/recipes.ts`
  - Contient: Appels API pour recettes

---

## Assets Visuels

### Fichiers Fournis:
Aucun asset visuel fourni.

### Recommandations UI:
- Reutiliser les `Preference Chips` existants du design system
- Pas de changement UI visible pour l'utilisateur (filtrage transparent)
- Utiliser les couleurs d'etat existantes si avertissements futurs

---

## Resume des Exigences

### Exigences Fonctionnelles

1. **Filtrage par preferences alimentaires:**
   - Les recettes incompatibles avec les preferences de l'utilisateur sont exclues
   - Support de 7 types: vegetarian, vegan, no_pork, no_beef, pescetarian, halal, kosher
   - Application cumulative (toutes les preferences sont respectees)

2. **Filtrage par allergies:**
   - Les recettes contenant des allergenes declares sont exclues
   - Support de 11 allergenes: gluten, lactose, tree_nuts, peanuts, eggs, fish, shellfish, soy, sesame, mustard, celery
   - Comparaison case-insensitive sur les noms d'ingredients

3. **Filtrage par ingredients exclus:**
   - Les recettes contenant les ingredients exclus par l'utilisateur sont filtrees
   - Utilise les `excluded_ingredients` du profil utilisateur

4. **Endpoints concernes:**
   - `GET /api/recipes/search` - filtrer les resultats de recherche
   - `GET /api/recipes/random` - retourner uniquement des recettes compatibles
   - `GET /api/recipes/category/{name}` - filtrer par categorie
   - Nouvel endpoint optionnel: `GET /api/recipes/for-me` - suggestions personnalisees

5. **Acces aux preferences:**
   - Endpoints authentifies: filtrage automatique selon le token JWT
   - Endpoints publics (sans auth): pas de filtrage, comportement actuel

---

### Approche Technique

**Architecture:**
```
Mobile App
    |
    v
Backend FastAPI
    |
    +-- /api/recipes/* (avec filtre si auth)
    |       |
    |       v
    |   RecipeFilterService (nouveau)
    |       |
    |       +-- Charge preferences user depuis Supabase
    |       +-- Applique IngredientMappings
    |       +-- Filtre les recettes TheMealDB
    |       v
    +-- TheMealDBClient (existant)
    |       |
    |       v
    +-- PreferencesService (existant)
```

**Nouveaux Composants Backend:**
1. `IngredientMappings` - Dictionnaires de mapping preference -> ingredients
2. `RecipeFilterService` - Logique de filtrage centralisee
3. Modifications routes recipes pour integrer le filtrage

**Mapping des Preferences:**
```python
DIETARY_EXCLUSIONS = {
    "vegetarian": ["chicken", "beef", "pork", "lamb", "duck", "turkey", ...],
    "vegan": ["chicken", "beef", "pork", "milk", "cheese", "egg", "honey", ...],
    "no_pork": ["pork", "bacon", "ham", "lard", "pancetta", "prosciutto", ...],
    "halal": ["pork", "bacon", "ham", "lard", "alcohol", "wine", ...],
    # etc.
}

ALLERGEN_KEYWORDS = {
    "gluten": ["wheat", "flour", "bread", "pasta", "semolina", "couscous", ...],
    "lactose": ["milk", "cheese", "cream", "butter", "yogurt", "whey", ...],
    # etc.
}
```

**Algorithme de Filtrage:**
1. Recuperer les preferences utilisateur via JWT
2. Construire la liste des ingredients interdits
3. Pour chaque recette, verifier si ingredients contiennent un interdit
4. Retourner uniquement les recettes compatibles

---

### User Stories

**US1: Utilisateur vegetarien cherche une recette**
> En tant qu'utilisateur vegetarien,
> Quand je recherche "curry" dans l'application,
> Alors je ne vois que les recettes de curry sans viande.

**US2: Parent avec enfant allergique aux arachides**
> En tant que parent d'un enfant allergique aux arachides,
> Quand je parcours les recettes par categorie,
> Alors aucune recette contenant des arachides n'est affichee.

**US3: Utilisateur halal recherche des suggestions**
> En tant qu'utilisateur halal,
> Quand j'utilise la fonction "recette aleatoire",
> Alors je ne recois que des recettes sans porc et sans alcool.

**US4: Utilisateur avec preferences multiples**
> En tant qu'utilisateur vegetarien et allergique au gluten,
> Quand je navigue dans les recettes,
> Alors seules les recettes vegetariennes ET sans gluten sont visibles.

**US5: Utilisateur non connecte**
> En tant qu'utilisateur non connecte,
> Quand je parcours les recettes,
> Alors je vois toutes les recettes sans filtrage.

---

### Cas Limites

1. **Ingredients avec noms variants:**
   - "Chicken Breast" vs "chicken" -> matching partiel case-insensitive
   - "Parmesan Cheese" contient "cheese" -> detecte comme lactose

2. **Ingredients composes:**
   - "Worcestershire Sauce" contient du poisson -> doit etre dans la liste fish

3. **Faux positifs potentiels:**
   - "Coconut milk" n'est pas du lait animal -> exception a gerer
   - "Egg noodles" vs oeufs frais -> contextualiser si necessaire

4. **Preferences conflictuelles:**
   - Deja gere par `UserPreferencesUpdate` validator (vegan incompatible avec no_pork, etc.)

5. **Aucune recette compatible:**
   - Si le filtrage exclut toutes les recettes, retourner liste vide
   - UX: afficher message "Aucune recette trouvee avec vos preferences"

6. **Changement de preferences:**
   - Le filtrage est applique en temps reel a chaque requete
   - Pas de cache des resultats par utilisateur

7. **Performance avec beaucoup de recettes:**
   - Filtrage post-fetch depuis TheMealDB
   - Pour POC acceptable, optimisation future si necessaire

---

### Criteres de Succes

**Criteres Fonctionnels:**
- [ ] Les recettes avec viande sont exclues pour les vegetariens
- [ ] Les recettes avec produits animaux sont exclues pour les vegans
- [ ] Les recettes avec allergenes sont exclues selon les allergies declarees
- [ ] Les ingredients exclus manuellement sont respectes
- [ ] Le filtrage s'applique a la recherche, categories et recette aleatoire
- [ ] Les utilisateurs non connectes voient toutes les recettes

**Criteres Techniques:**
- [ ] Nouveau service `RecipeFilterService` avec tests unitaires
- [ ] Dictionnaires de mapping complets et maintenables
- [ ] Integration transparente dans les routes existantes
- [ ] Temps de reponse < 500ms supplementaires
- [ ] Couverture de tests > 80% pour le service de filtrage

**Criteres UX:**
- [ ] Aucun changement d'interface visible (filtrage transparent)
- [ ] Message informatif si aucune recette compatible
- [ ] Comportement coherent sur tous les endpoints

---

### Perimetre

**Dans le Perimetre:**
- Filtrage backend des recettes par preferences alimentaires
- Filtrage backend des recettes par allergies
- Filtrage backend des recettes par ingredients exclus
- Application aux endpoints de recherche, categories et random
- Tests unitaires et d'integration

**Hors Perimetre:**
- Interface utilisateur pour activer/desactiver le filtrage
- Mode "voir tout avec avertissements"
- Filtrage par ingredients preferes (boost plutot qu'exclusion)
- Suggestions IA basees sur les preferences
- Cache des resultats filtres par utilisateur
- Ingredients preferes (promotion plutot que filtrage)

---

### Considerations Techniques

**Points d'Integration:**
- JWT decode pour identifier l'utilisateur
- `PreferencesService` pour recuperer les preferences
- Routes `/api/recipes/*` existantes a modifier

**Contraintes Systeme:**
- TheMealDB ne supporte pas le filtrage par ingredients
- Le filtrage doit etre fait apres reception des donnees API
- Les ingredients TheMealDB sont en anglais

**Conventions a Suivre:**
- Code Python avec type hints (FastAPI standards)
- Tests pytest avec fixtures
- Documentation docstrings
- Linting ruff conforme

**Technologies:**
- Backend: FastAPI + Pydantic
- Base: Supabase (preferences utilisateur)
- API externe: TheMealDB
- Mobile: React Native (pas de changements requis)

---

*Document genere le: 2026-01-03*
*Spec: Recipe Filtering by Preferences*
