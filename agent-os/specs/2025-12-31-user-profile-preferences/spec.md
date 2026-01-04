# Specification: User Profile & Preferences

## Goal

Permettre aux utilisateurs de configurer et persister leurs preferences alimentaires (regimes, allergies, ingredients exclus/preferes) et le nombre de portions dans un ecran profil avec modes lecture et edition, les donnees etant stockees dans Supabase avec validation des incompatibilites metier.

## User Stories

- En tant qu'utilisateur, je veux configurer mes regimes alimentaires (vegetarien, halal, etc.) afin que les recettes proposees correspondent a mes besoins
- En tant qu'utilisateur, je veux declarer mes allergies pour eviter les ingredients dangereux dans mes repas
- En tant qu'utilisateur, je veux definir mes ingredients exclus/preferes et mon nombre de portions pour personnaliser mon planning et ma liste de courses

## Specific Requirements

**Gestion des regimes alimentaires**
- Afficher 7 regimes sous forme de chips selectionnables: Vegetarien, Vegetalien, Sans porc, Sans boeuf, Pescetarien, Halal, Casher
- Permettre la multi-selection avec validation des incompatibilites cote client ET serveur
- Si Vegetalien selectionne, desactiver automatiquement Pescetarien, Sans boeuf, Sans porc (ces options deviennent mutuellement exclusives)
- Si Halal + Casher selectionnes ensemble, afficher un message d'avertissement non-bloquant "Verifiez la coherence de cette combinaison"
- Stocker les selections dans la table `user_dietary_preferences` avec relation `user_id`

**Gestion des allergies**
- Afficher 10 allergenes principaux sous forme de chips: Gluten, Lactose, Fruits a coque, Arachides, Oeufs, Poisson, Fruits de mer, Soja, Sesame, Moutarde, Celeri
- Optionnel en v1: ajouter Sulfites et Lupin si le temps le permet
- Multi-selection sans aucune restriction d'incompatibilite
- Stocker dans la table `user_allergies` avec relation `user_id`

**Gestion des ingredients exclus/preferes**
- Champ de saisie libre avec auto-completion sur une liste interne d'ingredients
- Affichage des ingredients selectionnes sous forme de tags supprimables
- Limite stricte de 30 tags maximum par categorie (exclus et preferes separes)
- Normalisation automatique des saisies: trim() + lowercase avant stockage
- Tables separees `user_excluded_ingredients` et `user_preferred_ingredients`

**Nombre de portions (taille du foyer)**
- Champ numerique permettant de definir le nombre de personnes (1-20)
- Validation: entier positif, minimum 1, maximum 20
- Stocker dans une colonne `portions_count` de la table utilisateur ou preferences
- Valeur utilisee pour adapter les quantites dans le planning et les courses

**Interface mode lecture/edition**
- Mode lecture par defaut: affichage propre et lisible des preferences actuelles
- Bouton "Modifier" visible en mode lecture pour passer en edition
- Mode edition: tous les champs deviennent interactifs
- Boutons "Enregistrer" et "Annuler" apparaissent en mode edition
- "Annuler" restaure les valeurs initiales sans appel API
- "Enregistrer" envoie les modifications au backend puis repasse en mode lecture

**Validation et feedback utilisateur**
- Feedback visuel immediat sur les erreurs de saisie (bordure rouge, message d'erreur)
- Toast/notification de succes apres sauvegarde reussie
- Gestion des erreurs reseau avec message explicite et option de reessai
- Indicateur de chargement (spinner) pendant les appels API

**Architecture API Backend**
- Endpoint `GET /api/profile/preferences` pour recuperer toutes les preferences de l'utilisateur connecte
- Endpoint `PUT /api/profile/preferences` pour mettre a jour les preferences (payload complet)
- Validation Pydantic des donnees entrantes avec regles metier (incompatibilites regimes)
- Tous les endpoints proteges par JWT via `get_current_user` dependency

**Schema de base de donnees**
- Table `user_dietary_preferences`: id, user_id (FK), dietary_type (enum), created_at
- Table `user_allergies`: id, user_id (FK), allergy_type (enum), created_at
- Table `user_excluded_ingredients`: id, user_id (FK), ingredient_name (text), created_at
- Table `user_preferred_ingredients`: id, user_id (FK), ingredient_name (text), created_at
- Colonne `portions_count` dans la table users existante ou table `user_settings`
- RLS policies pour securiser l'acces aux donnees par user_id

## Visual Design

Aucun fichier visuel fourni dans `planning/visuals/`. Se referer au design system (`agent-os/product/design-system.md`) pour les specs visuelles:

**Chips/Tags de preference (regimes, allergies)**
- Background inactive: `#F3F4F6` (muted)
- Background active: `#14B8A6` (primary)
- Text inactive: `#1F2937` (foreground)
- Text active: `#FFFFFF`
- Border radius: 20px
- Padding: 8px 16px, Height: 36px

**Boutons actions**
- "Modifier": style secondary (outline teal)
- "Enregistrer": style primary (background teal)
- "Annuler": style link ou secondary
- Height: 48px, border-radius: 16px

**Champ de saisie ingredients**
- Height: 48px, background: `#F9FAFB`
- Border: 1px solid `rgba(0, 0, 0, 0.08)`
- Border-radius: 14px
- Focus: border `#14B8A6`

**Layout ecran profil**
- Conserver le header existant avec avatar et infos utilisateur
- Sections separees pour: Regimes, Allergies, Ingredients exclus, Ingredients preferes, Portions
- Spacing entre sections: 24px (lg)

## Existing Code to Leverage

**Pattern routes/services backend (auth.py, auth_service.py)**
- Reutiliser la structure APIRouter avec prefix `/api/profile`
- Suivre le pattern de dependency injection avec `get_auth_service` et `get_current_user`
- Utiliser les memes patterns de gestion d'erreurs avec HTTPException
- S'inspirer de la structure des modeles Pydantic avec validateurs

**Composants UI mobile (Button.tsx, Input.tsx)**
- Reutiliser le composant `Button` existant pour les actions "Modifier", "Enregistrer", "Annuler"
- S'inspirer du composant `Input` pour le champ de saisie des ingredients
- Respecter le design system via `constants/theme.ts` pour les couleurs et spacing

**Store Zustand (stores/auth.ts)**
- Creer un nouveau store `stores/preferences.ts` avec le meme pattern
- Gerer l'etat local des preferences avant sauvegarde
- Actions: `fetchPreferences`, `updatePreferences`, `resetLocalChanges`

**Ecran profil existant (app/(tabs)/profile.tsx)**
- Etendre cet ecran avec les nouvelles sections de preferences
- Conserver la structure StyleSheet existante et l'ajouter
- Reutiliser les patterns de switch et settingItem pour inspiration

**Client Supabase (services/supabase.py)**
- Utiliser `get_supabase_client()` pour les operations CRUD
- Pattern de requetes: `.table("table_name").select().eq("user_id", user_id).execute()`

## Out of Scope

- Gestion de plusieurs profils famille (membres differents avec preferences propres) - potentielle v2
- Synchronisation/filtrage automatique des recettes selon les preferences - sera fait dans feature "Recipe Filtering"
- Upload et affichage de photo de profil utilisateur
- Modification des informations personnelles (nom, email) - deja gere par le systeme auth existant
- Historique des modifications de preferences
- Import/export des preferences en JSON
- Suggestions intelligentes de regimes/allergies basees sur l'historique
- Mode sombre pour l'ecran profil (sera gere globalement plus tard)
- Animation de transition entre mode lecture et edition
- Synchronisation temps reel avec d'autres appareils (offline-first)
