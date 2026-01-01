# Plan de Tests : Profil Utilisateur & Preferences

## Metadonnees
- **Fonctionnalite**: User Profile & Preferences
- **Spec**: agent-os/specs/2025-12-31-user-profile-preferences/spec.md
- **Requirements**: agent-os/specs/2025-12-31-user-profile-preferences/planning/requirements.md
- **Date de creation**: 2025-12-31
- **Statut**: Planification Complete

## Resume des Tests

| Couche | Critique | Haute | Moyenne | Basse | Total |
|--------|----------|-------|---------|-------|-------|
| Base de donnees | 8 | 6 | 4 | 2 | 20 |
| API Backend | 12 | 10 | 6 | 2 | 30 |
| UI Mobile | 8 | 12 | 8 | 4 | 32 |
| **Total** | **28** | **28** | **18** | **8** | **82** |

**Objectifs de couverture:**
- Chemins critiques: 100%
- Haute priorite: 100%
- Moyenne priorite: 80%
- Basse priorite: Differe si necessaire

---

## Couche Base de Donnees (20 tests)

### Table `user_dietary_preferences` (5 tests)

#### 1. test_dietary_preference_creation_with_valid_data
**Priorite:** Critique
**Given:**
- Un utilisateur authentifie avec `user_id = "user-123"`
- Donnees valides: `{"dietary_type": "vegetarien"}`
**When:** Insertion dans `user_dietary_preferences`
**Then:**
- Enregistrement cree avec succes
- `id` genere automatiquement (UUID)
- `user_id` correspond a l'utilisateur
- `created_at` est defini automatiquement
**Requirement:** spec.md "Schema de base de donnees > user_dietary_preferences"

#### 2. test_dietary_preference_user_id_foreign_key_constraint
**Priorite:** Critique
**Given:**
- `user_id = "nonexistent-user"` qui n'existe pas dans la table `users`
**When:** Tentative d'insertion dans `user_dietary_preferences`
**Then:**
- Erreur de contrainte de cle etrangere
- Aucun enregistrement cree
**Requirement:** spec.md "Schema de base de donnees > Relation user_id (FK)"

#### 3. test_dietary_preference_enum_validation
**Priorite:** Haute
**Given:**
- `dietary_type = "regime_invalide"` (valeur hors enum)
**When:** Tentative d'insertion dans `user_dietary_preferences`
**Then:**
- Erreur de validation d'enum
- Seules les valeurs autorisees acceptees: vegetarien, vegetalien, sans_porc, sans_boeuf, pescetarien, halal, casher
**Requirement:** spec.md "Gestion des regimes alimentaires > 7 regimes"

#### 4. test_dietary_preference_rls_policy_user_can_only_read_own_data
**Priorite:** Critique
**Given:**
- Utilisateur A avec `user_id = "user-a"` a des preferences
- Utilisateur B authentifie avec `user_id = "user-b"`
**When:** Utilisateur B tente de lire les preferences de l'utilisateur A
**Then:**
- Resultats vides (RLS bloque l'acces)
- Aucune erreur explicite pour eviter l'enumeration
**Requirement:** spec.md "Schema de base de donnees > RLS policies"

#### 5. test_dietary_preference_deletion_cascade_or_restrict
**Priorite:** Moyenne
**Given:**
- Utilisateur avec des preferences alimentaires existantes
**When:** Suppression de l'utilisateur (si permis)
**Then:**
- Verifier le comportement de cascade ou restriction selon la politique definie
**Requirement:** spec.md "Schema de base de donnees > Relation user_id"

---

### Table `user_allergies` (4 tests)

#### 6. test_allergy_creation_with_valid_enum_values
**Priorite:** Critique
**Given:**
- Un utilisateur authentifie
- Donnees valides: `{"allergy_type": "gluten"}`
**When:** Insertion dans `user_allergies`
**Then:**
- Enregistrement cree avec succes
- Toutes les valeurs enum valides: gluten, lactose, fruits_a_coque, arachides, oeufs, poisson, fruits_de_mer, soja, sesame, moutarde, celeri
**Requirement:** spec.md "Gestion des allergies > 10 allergenes principaux"

#### 7. test_allergy_multiple_selections_same_user
**Priorite:** Haute
**Given:**
- Un utilisateur avec `user_id = "user-123"`
**When:** Insertion de plusieurs allergies: gluten, lactose, arachides
**Then:**
- Trois enregistrements distincts crees
- Tous lies au meme `user_id`
**Requirement:** spec.md "Gestion des allergies > Multi-selection sans restriction"

#### 8. test_allergy_rls_policy_isolation
**Priorite:** Critique
**Given:**
- Utilisateur A avec allergies declarees
- Utilisateur B authentifie
**When:** Utilisateur B tente de supprimer une allergie de A
**Then:**
- Operation echoue (RLS)
- Donnees de A intactes
**Requirement:** spec.md "Schema de base de donnees > RLS policies"

#### 9. test_allergy_duplicate_prevention
**Priorite:** Moyenne
**Given:**
- Utilisateur avec allergie "gluten" deja enregistree
**When:** Tentative d'ajout de "gluten" a nouveau
**Then:**
- Contrainte d'unicite (user_id, allergy_type) ou upsert
**Requirement:** spec.md "Gestion des allergies"

---

### Table `user_excluded_ingredients` (4 tests)

#### 10. test_excluded_ingredient_creation_with_normalization
**Priorite:** Haute
**Given:**
- Utilisateur authentifie
- Saisie: `"  Tomate  "` (avec espaces)
**When:** Insertion dans `user_excluded_ingredients`
**Then:**
- Stockage normalise: `"tomate"` (lowercase + trim)
**Requirement:** spec.md "Gestion des ingredients > Normalisation automatique"

#### 11. test_excluded_ingredient_limit_30_tags
**Priorite:** Critique
**Given:**
- Utilisateur avec 30 ingredients exclus existants
**When:** Tentative d'ajout d'un 31eme ingredient
**Then:**
- Erreur ou rejet (limite stricte)
**Requirement:** spec.md "Gestion des ingredients > Limite stricte de 30 tags"

#### 12. test_excluded_ingredient_text_field_validation
**Priorite:** Moyenne
**Given:**
- Saisie d'ingredient avec caracteres speciaux ou longueur excessive
**When:** Tentative d'insertion
**Then:**
- Validation appropriee (longueur max, caracteres autorises)
**Requirement:** spec.md "Gestion des ingredients > Saisie libre"

#### 13. test_excluded_ingredient_deletion
**Priorite:** Haute
**Given:**
- Utilisateur avec ingredient exclu "tomate"
**When:** Suppression de l'ingredient
**Then:**
- Enregistrement supprime
- Compteur d'ingredients mis a jour
**Requirement:** spec.md "Gestion des ingredients > Tags supprimables"

---

### Table `user_preferred_ingredients` (4 tests)

#### 14. test_preferred_ingredient_creation
**Priorite:** Haute
**Given:**
- Utilisateur authentifie
- Saisie: "Basilic"
**When:** Insertion dans `user_preferred_ingredients`
**Then:**
- Stockage normalise: "basilic"
**Requirement:** spec.md "Gestion des ingredients > Tables separees"

#### 15. test_preferred_ingredient_limit_30_tags_separate_from_excluded
**Priorite:** Critique
**Given:**
- Utilisateur avec 30 ingredients preferes ET 30 ingredients exclus
**When:** Verification des compteurs
**Then:**
- Limites separees respectees (30 + 30 = 60 total possible)
**Requirement:** spec.md "Gestion des ingredients > 30 tags maximum par categorie"

#### 16. test_preferred_ingredient_same_as_excluded_allowed
**Priorite:** Basse
**Given:**
- Utilisateur avec "tomate" dans ingredients exclus
**When:** Ajout de "tomate" dans ingredients preferes
**Then:**
- Comportement defini (autoriser ou avertir - verifier spec)
**Requirement:** spec.md "Gestion des ingredients"

#### 17. test_preferred_ingredient_rls_isolation
**Priorite:** Haute
**Given:**
- Deux utilisateurs distincts
**When:** Chacun gere ses ingredients preferes
**Then:**
- Isolation complete des donnees
**Requirement:** spec.md "Schema de base de donnees > RLS policies"

---

### Colonne `portions_count` (3 tests)

#### 18. test_portions_count_default_value
**Priorite:** Haute
**Given:**
- Nouvel utilisateur sans preferences definies
**When:** Lecture de `portions_count`
**Then:**
- Valeur par defaut (1 ou null selon implementation)
**Requirement:** spec.md "Nombre de portions"

#### 19. test_portions_count_range_validation
**Priorite:** Critique
**Given:**
- Tentative de definir `portions_count = 0` ou `portions_count = 25`
**When:** Mise a jour dans la base
**Then:**
- Contrainte CHECK rejetee (min 1, max 20)
**Requirement:** spec.md "Nombre de portions > Validation: entier positif, minimum 1, maximum 20"

#### 20. test_portions_count_update
**Priorite:** Moyenne
**Given:**
- Utilisateur avec `portions_count = 2`
**When:** Mise a jour vers `portions_count = 4`
**Then:**
- Valeur mise a jour correctement
**Requirement:** spec.md "Nombre de portions > Stocker dans colonne"

---

## Couche API Backend (30 tests)

### GET /api/profile/preferences (10 tests)

#### 21. test_get_preferences_authenticated_success
**Priorite:** Critique
**Given:**
- Utilisateur authentifie avec JWT valide
- Preferences existantes: 2 regimes, 3 allergies, 5 ingredients exclus, 3 preferes, portions = 4
**When:** GET /api/profile/preferences
**Then:**
- Status: 200 OK
- Body contient toutes les preferences structurees:
  ```json
  {
    "dietary_preferences": ["vegetarien", "sans_porc"],
    "allergies": ["gluten", "lactose", "arachides"],
    "excluded_ingredients": ["tomate", "oignon", "ail", "poivron", "aubergine"],
    "preferred_ingredients": ["basilic", "thym", "romarin"],
    "portions_count": 4
  }
  ```
**Requirement:** spec.md "Architecture API Backend > GET /api/profile/preferences"

#### 22. test_get_preferences_unauthenticated_returns_401
**Priorite:** Critique
**Given:**
- Aucun header Authorization
**When:** GET /api/profile/preferences
**Then:**
- Status: 401 Unauthorized
- Body: `{"detail": "Not authenticated"}`
**Requirement:** spec.md "Architecture API Backend > Endpoints proteges par JWT"

#### 23. test_get_preferences_invalid_token_returns_401
**Priorite:** Critique
**Given:**
- Header Authorization avec token expire ou invalide
**When:** GET /api/profile/preferences
**Then:**
- Status: 401 Unauthorized
- Body: `{"detail": "Could not validate credentials"}`
**Requirement:** spec.md "Architecture API Backend > get_current_user dependency"

#### 24. test_get_preferences_new_user_returns_empty_defaults
**Priorite:** Haute
**Given:**
- Utilisateur authentifie sans aucune preference configuree
**When:** GET /api/profile/preferences
**Then:**
- Status: 200 OK
- Body avec valeurs par defaut:
  ```json
  {
    "dietary_preferences": [],
    "allergies": [],
    "excluded_ingredients": [],
    "preferred_ingredients": [],
    "portions_count": 1
  }
  ```
**Requirement:** spec.md "Architecture API Backend > GET preferences"

#### 25. test_get_preferences_only_returns_current_user_data
**Priorite:** Critique
**Given:**
- Utilisateur A avec preferences specifiques
- Utilisateur B authentifie
**When:** GET /api/profile/preferences (avec token de B)
**Then:**
- Retourne uniquement les preferences de B (ou vide)
- Aucune donnee de A exposee
**Requirement:** spec.md "Schema de base de donnees > RLS policies"

#### 26. test_get_preferences_response_time_under_500ms
**Priorite:** Moyenne
**Given:**
- Utilisateur avec preferences completes (max values)
**When:** GET /api/profile/preferences
**Then:**
- Temps de reponse < 500ms
**Requirement:** Non-fonctionnel - Performance

#### 27. test_get_preferences_handles_database_error_gracefully
**Priorite:** Haute
**Given:**
- Connexion base de donnees indisponible
**When:** GET /api/profile/preferences
**Then:**
- Status: 500 Internal Server Error
- Body: `{"detail": "Service temporarily unavailable"}`
- Erreur loggee cote serveur
**Requirement:** spec.md "Validation et feedback > Gestion des erreurs reseau"

#### 28. test_get_preferences_returns_correct_content_type
**Priorite:** Basse
**Given:**
- Requete valide
**When:** GET /api/profile/preferences
**Then:**
- Header Content-Type: application/json
**Requirement:** Standard API

#### 29. test_get_preferences_supports_cors_headers
**Priorite:** Moyenne
**Given:**
- Requete depuis origine mobile autorisee
**When:** GET /api/profile/preferences
**Then:**
- Headers CORS appropries presents
**Requirement:** Standard API

#### 30. test_get_preferences_with_partial_data
**Priorite:** Haute
**Given:**
- Utilisateur avec seulement des allergies (pas de regimes ni ingredients)
**When:** GET /api/profile/preferences
**Then:**
- Retourne les allergies + tableaux vides pour le reste
**Requirement:** spec.md "Architecture API Backend"

---

### PUT /api/profile/preferences (20 tests)

#### 31. test_update_preferences_full_payload_success
**Priorite:** Critique
**Given:**
- Utilisateur authentifie
- Payload complet valide:
  ```json
  {
    "dietary_preferences": ["vegetarien"],
    "allergies": ["gluten"],
    "excluded_ingredients": ["tomate"],
    "preferred_ingredients": ["basilic"],
    "portions_count": 3
  }
  ```
**When:** PUT /api/profile/preferences
**Then:**
- Status: 200 OK
- Toutes les preferences mises a jour en base
- Body retourne les preferences mises a jour
**Requirement:** spec.md "Architecture API Backend > PUT /api/profile/preferences"

#### 32. test_update_preferences_unauthenticated_returns_401
**Priorite:** Critique
**Given:**
- Aucun header Authorization
**When:** PUT /api/profile/preferences
**Then:**
- Status: 401 Unauthorized
**Requirement:** spec.md "Architecture API Backend > Endpoints proteges par JWT"

#### 33. test_update_dietary_preferences_incompatibility_vegetalien_pescetarien
**Priorite:** Critique
**Given:**
- Payload avec `dietary_preferences: ["vegetalien", "pescetarien"]`
**When:** PUT /api/profile/preferences
**Then:**
- Status: 422 Unprocessable Entity
- Body: `{"detail": "Vegetalien est incompatible avec Pescetarien"}`
**Requirement:** spec.md "Gestion des regimes > Vegetalien incompatible avec Pescetarien"

#### 34. test_update_dietary_preferences_incompatibility_vegetalien_sans_boeuf
**Priorite:** Critique
**Given:**
- Payload avec `dietary_preferences: ["vegetalien", "sans_boeuf"]`
**When:** PUT /api/profile/preferences
**Then:**
- Status: 422 Unprocessable Entity
- Body: `{"detail": "Vegetalien est incompatible avec Sans boeuf"}`
**Requirement:** spec.md "Gestion des regimes > Vegetalien incompatible avec Sans boeuf"

#### 35. test_update_dietary_preferences_incompatibility_vegetalien_sans_porc
**Priorite:** Critique
**Given:**
- Payload avec `dietary_preferences: ["vegetalien", "sans_porc"]`
**When:** PUT /api/profile/preferences
**Then:**
- Status: 422 Unprocessable Entity
- Body: `{"detail": "Vegetalien est incompatible avec Sans porc"}`
**Requirement:** spec.md "Gestion des regimes > Vegetalien incompatible avec Sans porc"

#### 36. test_update_dietary_preferences_halal_casher_warning_but_allowed
**Priorite:** Haute
**Given:**
- Payload avec `dietary_preferences: ["halal", "casher"]`
**When:** PUT /api/profile/preferences
**Then:**
- Status: 200 OK (combinaison autorisee)
- Body inclut warning: `{"warning": "Verifiez la coherence de cette combinaison"}`
- Preferences sauvegardees
**Requirement:** spec.md "Gestion des regimes > Halal + Casher: avertissement non-bloquant"

#### 37. test_update_excluded_ingredients_exceeds_30_limit
**Priorite:** Critique
**Given:**
- Payload avec `excluded_ingredients` contenant 31 elements
**When:** PUT /api/profile/preferences
**Then:**
- Status: 422 Unprocessable Entity
- Body: `{"detail": "Maximum 30 ingredients exclus autorises"}`
**Requirement:** spec.md "Gestion des ingredients > Limite stricte de 30 tags"

#### 38. test_update_preferred_ingredients_exceeds_30_limit
**Priorite:** Critique
**Given:**
- Payload avec `preferred_ingredients` contenant 31 elements
**When:** PUT /api/profile/preferences
**Then:**
- Status: 422 Unprocessable Entity
- Body: `{"detail": "Maximum 30 ingredients preferes autorises"}`
**Requirement:** spec.md "Gestion des ingredients > Limite stricte de 30 tags"

#### 39. test_update_portions_count_below_minimum
**Priorite:** Critique
**Given:**
- Payload avec `portions_count: 0`
**When:** PUT /api/profile/preferences
**Then:**
- Status: 422 Unprocessable Entity
- Body: `{"detail": "Le nombre de portions doit etre entre 1 et 20"}`
**Requirement:** spec.md "Nombre de portions > Validation: minimum 1"

#### 40. test_update_portions_count_above_maximum
**Priorite:** Critique
**Given:**
- Payload avec `portions_count: 21`
**When:** PUT /api/profile/preferences
**Then:**
- Status: 422 Unprocessable Entity
- Body: `{"detail": "Le nombre de portions doit etre entre 1 et 20"}`
**Requirement:** spec.md "Nombre de portions > Validation: maximum 20"

#### 41. test_update_portions_count_non_integer
**Priorite:** Haute
**Given:**
- Payload avec `portions_count: 2.5`
**When:** PUT /api/profile/preferences
**Then:**
- Status: 422 Unprocessable Entity
- Body: `{"detail": "Le nombre de portions doit etre un entier"}`
**Requirement:** spec.md "Nombre de portions > Validation: entier positif"

#### 42. test_update_ingredients_normalization
**Priorite:** Haute
**Given:**
- Payload avec `excluded_ingredients: ["  TOMATE  ", "Oignon"]`
**When:** PUT /api/profile/preferences
**Then:**
- Status: 200 OK
- Ingredients stockes en lowercase et trimes: ["tomate", "oignon"]
**Requirement:** spec.md "Gestion des ingredients > Normalisation automatique: trim() + lowercase"

#### 43. test_update_invalid_dietary_preference_enum
**Priorite:** Haute
**Given:**
- Payload avec `dietary_preferences: ["regime_inexistant"]`
**When:** PUT /api/profile/preferences
**Then:**
- Status: 422 Unprocessable Entity
- Body liste les valeurs valides
**Requirement:** spec.md "Gestion des regimes > 7 regimes"

#### 44. test_update_invalid_allergy_enum
**Priorite:** Haute
**Given:**
- Payload avec `allergies: ["allergie_inexistante"]`
**When:** PUT /api/profile/preferences
**Then:**
- Status: 422 Unprocessable Entity
- Body liste les valeurs valides
**Requirement:** spec.md "Gestion des allergies > 10 allergenes"

#### 45. test_update_empty_payload_clears_preferences
**Priorite:** Haute
**Given:**
- Utilisateur avec preferences existantes
- Payload:
  ```json
  {
    "dietary_preferences": [],
    "allergies": [],
    "excluded_ingredients": [],
    "preferred_ingredients": [],
    "portions_count": 1
  }
  ```
**When:** PUT /api/profile/preferences
**Then:**
- Status: 200 OK
- Toutes les preferences effacees (retour aux defauts)
**Requirement:** spec.md "Architecture API Backend > Payload complet"

#### 46. test_update_partial_payload_rejected
**Priorite:** Moyenne
**Given:**
- Payload partiel (seulement `allergies`)
**When:** PUT /api/profile/preferences
**Then:**
- Status: 422 Unprocessable Entity (si payload complet requis)
- OU: Status 200 avec merge (si partiel autorise - verifier spec)
**Requirement:** spec.md "Architecture API Backend > Payload complet"

#### 47. test_update_duplicate_ingredients_deduplicated
**Priorite:** Moyenne
**Given:**
- Payload avec `excluded_ingredients: ["tomate", "tomate", "TOMATE"]`
**When:** PUT /api/profile/preferences
**Then:**
- Status: 200 OK
- Stocke un seul "tomate" (deduplication)
**Requirement:** spec.md "Gestion des ingredients > Normalisation"

#### 48. test_update_transactional_rollback_on_partial_failure
**Priorite:** Haute
**Given:**
- Payload valide mais erreur lors de l'insertion des allergies
**When:** PUT /api/profile/preferences
**Then:**
- Aucune modification persistee (rollback complet)
- Status: 500 Internal Server Error
**Requirement:** Integrite des donnees

#### 49. test_update_concurrent_requests_handled
**Priorite:** Moyenne
**Given:**
- Deux requetes PUT simultanees du meme utilisateur
**When:** Les deux requetes arrivent en meme temps
**Then:**
- Une seule reussit ou merge coherent
- Pas de corruption de donnees
**Requirement:** Integrite des donnees

#### 50. test_update_empty_ingredient_string_rejected
**Priorite:** Basse
**Given:**
- Payload avec `excluded_ingredients: ["", "  ", "tomate"]`
**When:** PUT /api/profile/preferences
**Then:**
- Status: 422 ou filtrage des chaines vides
**Requirement:** spec.md "Gestion des ingredients > Validation"

---

## Couche UI Mobile (32 tests)

### Ecran Profil - Mode Lecture (8 tests)

#### 51. test_profile_screen_renders_in_read_mode_by_default
**Priorite:** Critique
**Given:**
- Utilisateur authentifie navigue vers l'ecran profil
**When:** Chargement initial de l'ecran
**Then:**
- Mode lecture affiche
- Bouton "Modifier" visible
- Aucun champ editable
**Requirement:** spec.md "Interface mode lecture/edition > Mode lecture par defaut"

#### 52. test_profile_screen_displays_dietary_preferences_chips
**Priorite:** Haute
**Given:**
- Utilisateur avec regimes: vegetarien, sans_porc
**When:** Affichage du profil en mode lecture
**Then:**
- Chips affiches avec style actif (background teal)
- Regimes non selectionnes en style inactif (background gris)
**Requirement:** spec.md "Visual Design > Chips/Tags de preference"

#### 53. test_profile_screen_displays_allergies_chips
**Priorite:** Haute
**Given:**
- Utilisateur avec allergies: gluten, lactose
**When:** Affichage du profil en mode lecture
**Then:**
- Chips allergies affiches correctement
**Requirement:** spec.md "Gestion des allergies"

#### 54. test_profile_screen_displays_excluded_ingredients_tags
**Priorite:** Haute
**Given:**
- Utilisateur avec ingredients exclus: tomate, oignon
**When:** Affichage du profil en mode lecture
**Then:**
- Tags affiches dans la section "Ingredients exclus"
- Pas de bouton de suppression en mode lecture
**Requirement:** spec.md "Gestion des ingredients > Tags"

#### 55. test_profile_screen_displays_preferred_ingredients_tags
**Priorite:** Haute
**Given:**
- Utilisateur avec ingredients preferes: basilic, thym
**When:** Affichage du profil en mode lecture
**Then:**
- Tags affiches dans la section "Ingredients preferes"
**Requirement:** spec.md "Gestion des ingredients"

#### 56. test_profile_screen_displays_portions_count
**Priorite:** Haute
**Given:**
- Utilisateur avec portions_count = 4
**When:** Affichage du profil en mode lecture
**Then:**
- Affichage "4 personnes" ou equivalent
**Requirement:** spec.md "Nombre de portions"

#### 57. test_profile_screen_shows_loading_spinner_during_fetch
**Priorite:** Moyenne
**Given:**
- Ecran profil en cours de chargement
**When:** Appel API en cours
**Then:**
- Spinner/ActivityIndicator visible
**Requirement:** spec.md "Validation et feedback > Indicateur de chargement"

#### 58. test_profile_screen_shows_error_state_on_fetch_failure
**Priorite:** Haute
**Given:**
- Erreur reseau lors du fetch des preferences
**When:** Echec de l'API
**Then:**
- Message d'erreur explicite affiche
- Bouton "Reessayer" present
**Requirement:** spec.md "Validation et feedback > Gestion des erreurs reseau"

---

### Ecran Profil - Mode Edition (12 tests)

#### 59. test_edit_button_switches_to_edit_mode
**Priorite:** Critique
**Given:**
- Ecran profil en mode lecture
**When:** Appui sur le bouton "Modifier"
**Then:**
- Passage en mode edition
- Boutons "Enregistrer" et "Annuler" apparaissent
- Bouton "Modifier" disparait
**Requirement:** spec.md "Interface mode lecture/edition > Bouton Modifier"

#### 60. test_dietary_chips_become_selectable_in_edit_mode
**Priorite:** Critique
**Given:**
- Ecran profil en mode edition
**When:** Appui sur un chip de regime non selectionne
**Then:**
- Chip passe a l'etat actif (style change)
- Selection ajoutee a l'etat local
**Requirement:** spec.md "Gestion des regimes > Chips selectionnables"

#### 61. test_dietary_chips_vegetalien_disables_incompatible_options
**Priorite:** Critique
**Given:**
- Mode edition actif
**When:** Selection du regime "Vegetalien"
**Then:**
- Chips "Pescetarien", "Sans boeuf", "Sans porc" deviennent desactives/grisees
- Indication visuelle qu'ils ne sont plus selectionnables
**Requirement:** spec.md "Gestion des regimes > Vegetalien desactive automatiquement..."

#### 62. test_halal_casher_warning_displayed
**Priorite:** Haute
**Given:**
- Mode edition actif
- "Halal" deja selectionne
**When:** Selection de "Casher"
**Then:**
- Message d'avertissement affiche: "Verifiez la coherence de cette combinaison"
- Selection quand meme autorisee
**Requirement:** spec.md "Gestion des regimes > Halal + Casher avertissement non-bloquant"

#### 63. test_allergy_chips_multi_selection_without_restriction
**Priorite:** Haute
**Given:**
- Mode edition actif
**When:** Selection de plusieurs allergies
**Then:**
- Toutes les selections acceptees sans restriction
**Requirement:** spec.md "Gestion des allergies > Multi-selection sans restriction"

#### 64. test_ingredient_input_autocomplete_suggestions
**Priorite:** Haute
**Given:**
- Mode edition actif
- Champ de saisie ingredients actif
**When:** Saisie de "tom"
**Then:**
- Suggestions affichees: "tomate", "tomate cerise", etc.
**Requirement:** spec.md "Gestion des ingredients > Auto-completion"

#### 65. test_ingredient_tag_added_on_selection
**Priorite:** Haute
**Given:**
- Mode edition, champ ingredients actif
**When:** Selection d'une suggestion ou appui sur Entree
**Then:**
- Tag ajoute a la liste
- Champ de saisie vide
**Requirement:** spec.md "Gestion des ingredients > Tags"

#### 66. test_ingredient_tag_removable_with_x_button
**Priorite:** Haute
**Given:**
- Mode edition, tags ingredients affiches
**When:** Appui sur le X d'un tag
**Then:**
- Tag supprime de la liste
**Requirement:** spec.md "Gestion des ingredients > Tags supprimables"

#### 67. test_ingredient_limit_30_shows_error
**Priorite:** Critique
**Given:**
- Mode edition, 30 ingredients exclus deja ajoutes
**When:** Tentative d'ajout d'un 31eme
**Then:**
- Erreur visuelle (bordure rouge, message)
- Ajout refuse
**Requirement:** spec.md "Gestion des ingredients > Limite stricte de 30 tags"

#### 68. test_portions_input_numeric_validation
**Priorite:** Haute
**Given:**
- Mode edition, champ portions actif
**When:** Saisie de valeurs invalides (0, 25, "abc")
**Then:**
- Feedback visuel immediat (bordure rouge)
- Message d'erreur sous le champ
**Requirement:** spec.md "Nombre de portions > Validation 1-20"

#### 69. test_cancel_button_restores_initial_values
**Priorite:** Critique
**Given:**
- Mode edition avec modifications non sauvegardees
**When:** Appui sur "Annuler"
**Then:**
- Toutes les modifications annulees
- Valeurs initiales restaurees
- Retour en mode lecture
- Aucun appel API effectue
**Requirement:** spec.md "Interface mode lecture/edition > Annuler restaure les valeurs initiales"

#### 70. test_save_button_calls_api_and_shows_success_toast
**Priorite:** Critique
**Given:**
- Mode edition avec modifications valides
**When:** Appui sur "Enregistrer"
**Then:**
- Appel PUT /api/profile/preferences
- Spinner pendant l'appel
- Toast de succes affiche
- Retour en mode lecture
**Requirement:** spec.md "Validation et feedback > Toast/notification de succes"

---

### Composants UI (8 tests)

#### 71. test_chip_component_inactive_style
**Priorite:** Moyenne
**Given:**
- Chip en etat inactif
**When:** Rendu du composant
**Then:**
- Background: #F3F4F6
- Text: #1F2937
- Border radius: 20px
**Requirement:** spec.md "Visual Design > Chips inactive"

#### 72. test_chip_component_active_style
**Priorite:** Moyenne
**Given:**
- Chip en etat actif
**When:** Rendu du composant
**Then:**
- Background: #14B8A6 (teal)
- Text: #FFFFFF
**Requirement:** spec.md "Visual Design > Chips active"

#### 73. test_chip_component_disabled_style
**Priorite:** Moyenne
**Given:**
- Chip en etat desactive (ex: Pescetarien quand Vegetalien selectionne)
**When:** Rendu du composant
**Then:**
- Opacite reduite
- Non cliquable
**Requirement:** spec.md "Gestion des regimes > Options deviennent mutuellement exclusives"

#### 74. test_ingredient_input_focus_style
**Priorite:** Basse
**Given:**
- Champ de saisie ingredients
**When:** Focus sur le champ
**Then:**
- Border: #14B8A6
**Requirement:** spec.md "Visual Design > Focus: border teal"

#### 75. test_ingredient_input_error_style
**Priorite:** Moyenne
**Given:**
- Erreur de validation sur le champ
**When:** Affichage de l'erreur
**Then:**
- Bordure rouge
- Message d'erreur visible
**Requirement:** spec.md "Validation et feedback > Feedback visuel immediat"

#### 76. test_save_button_primary_style
**Priorite:** Basse
**Given:**
- Bouton "Enregistrer" en mode edition
**When:** Rendu du composant
**Then:**
- Style primary (background teal)
- Height: 48px
- Border-radius: 16px
**Requirement:** spec.md "Visual Design > Boutons actions"

#### 77. test_cancel_button_secondary_style
**Priorite:** Basse
**Given:**
- Bouton "Annuler" en mode edition
**When:** Rendu du composant
**Then:**
- Style secondary ou link
**Requirement:** spec.md "Visual Design > Boutons actions"

#### 78. test_sections_spacing_24px
**Priorite:** Basse
**Given:**
- Ecran profil avec plusieurs sections
**When:** Rendu de l'ecran
**Then:**
- Spacing entre sections: 24px
**Requirement:** spec.md "Visual Design > Spacing entre sections: 24px"

---

### Store Zustand (4 tests)

#### 79. test_preferences_store_fetch_preferences_action
**Priorite:** Haute
**Given:**
- Store preferences initialise
**When:** Appel de `fetchPreferences()`
**Then:**
- Appel API GET /api/profile/preferences
- State mis a jour avec les donnees recues
**Requirement:** spec.md "Existing Code > Store Zustand > fetchPreferences"

#### 80. test_preferences_store_update_preferences_action
**Priorite:** Haute
**Given:**
- Store avec preferences locales modifiees
**When:** Appel de `updatePreferences(data)`
**Then:**
- Appel API PUT /api/profile/preferences
- State mis a jour en cas de succes
**Requirement:** spec.md "Existing Code > Store Zustand > updatePreferences"

#### 81. test_preferences_store_reset_local_changes_action
**Priorite:** Haute
**Given:**
- Store avec modifications locales non sauvegardees
**When:** Appel de `resetLocalChanges()`
**Then:**
- State revient aux valeurs chargees initialement
- Aucun appel API
**Requirement:** spec.md "Existing Code > Store Zustand > resetLocalChanges"

#### 82. test_preferences_store_handles_api_error
**Priorite:** Moyenne
**Given:**
- Erreur API lors de updatePreferences
**When:** L'API retourne une erreur
**Then:**
- State error mis a jour
- State loading passe a false
- Preferences locales non ecrasees
**Requirement:** spec.md "Validation et feedback > Gestion des erreurs"

---

## Dependances des Tests

### Ordre d'execution recommande

1. **Tests Base de Donnees** - Doivent passer en premier
   - Valident le schema et les contraintes
   - Prerequis pour les tests API

2. **Tests API Backend** - Dependant de la couche DB
   - Tests unitaires des services d'abord
   - Tests d'integration des endpoints ensuite

3. **Tests UI Mobile** - Dependant de l'API
   - Tests de composants isoles d'abord
   - Tests d'ecran avec mocks API ensuite

### Dependances specifiques

- `test_dietary_chips_vegetalien_disables_incompatible_options` depend de `test_update_dietary_preferences_incompatibility_*`
- `test_ingredient_limit_30_shows_error` depend de `test_excluded_ingredient_limit_30_tags`
- Tous les tests UI dependant de l'API necessitent des mocks configures

---

## Donnees de Test Requises

### Fixtures Backend (conftest.py)

```python
@pytest.fixture
def test_user_with_preferences():
    """Utilisateur avec preferences completes pour tests"""
    return {
        "user_id": "test-user-123",
        "dietary_preferences": ["vegetarien", "sans_porc"],
        "allergies": ["gluten", "lactose", "arachides"],
        "excluded_ingredients": ["tomate", "oignon", "ail"],
        "preferred_ingredients": ["basilic", "thym"],
        "portions_count": 4
    }

@pytest.fixture
def test_user_empty_preferences():
    """Utilisateur sans preferences configurees"""
    return {
        "user_id": "test-user-456",
        "dietary_preferences": [],
        "allergies": [],
        "excluded_ingredients": [],
        "preferred_ingredients": [],
        "portions_count": 1
    }
```

### Mocks Mobile (Jest)

```typescript
// Mock du service preferences
jest.mock('@/services/preferences', () => ({
  getPreferences: jest.fn(),
  updatePreferences: jest.fn(),
}));

// Donnees de test
const mockPreferences = {
  dietary_preferences: ['vegetarien'],
  allergies: ['gluten'],
  excluded_ingredients: ['tomate'],
  preferred_ingredients: ['basilic'],
  portions_count: 2,
};
```

### Liste des enums a definir

**DietaryType:**
- vegetarien
- vegetalien
- sans_porc
- sans_boeuf
- pescetarien
- halal
- casher

**AllergyType:**
- gluten
- lactose
- fruits_a_coque
- arachides
- oeufs
- poisson
- fruits_de_mer
- soja
- sesame
- moutarde
- celeri
- (optionnel: sulfites, lupin)

---

## Hors Perimetre

Tests explicitement exclus de ce plan:

- **Tests de performance/charge** - Necessite un sprint dedie
- **Tests d'accessibilite complets** - Audit QA separe
- **Tests de compatibilite navigateurs** - Non applicable (mobile natif)
- **Tests de mode sombre** - Fonctionnalite globale future
- **Tests d'animations** - Hors scope v1
- **Tests offline-first** - Fonctionnalite future
- **Tests multi-profils famille** - v2

---

## Checklist de Validation

- [x] Chaque user story a des tests correspondants
- [x] Chaque endpoint API a des tests succes + erreur
- [x] Chaque regle de validation a un test
- [x] Chaque interaction UI a un test
- [x] Tous les edge cases des requirements sont couverts
- [x] 82 tests total (feature moyenne-grande)
- [x] Priorites assignees a chaque test
- [x] References aux sections spec.md incluses
