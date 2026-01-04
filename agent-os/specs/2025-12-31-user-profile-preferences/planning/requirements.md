# Spec Requirements: User Profile & Preferences

## Initial Description

**Feature Name:** User Profile & Preferences

**Description:** Creer l'ecran de profil permettant aux utilisateurs de configurer leurs preferences alimentaires (vegetarien, sans porc, halal, etc.), allergies (gluten, lactose, fruits a coque, etc.), et ingredients exclus/preferes. Donnees persistees dans Supabase.

---

## Requirements Discussion

### First Round Questions

**Q1:** Quels regimes alimentaires doivent etre disponibles en v1 ?
**Answer:** Liste complete comme dans la maquette:
- Vegetarien
- Vegetalien
- Sans porc
- Sans boeuf
- Pescetarien
- Halal
- Casher

**Q2:** Quelles allergies doivent etre disponibles en v1 ?
**Answer:** Liste complete avec ajouts:
- Gluten
- Lactose
- Fruits a coque
- Arachides
- Oeufs
- Poisson
- Fruits de mer (crustaces/mollusques)
- Soja
- Sesame
- Moutarde
- Celeri
- (Optionnel v1: sulfites, lupin)

**Q3:** Comment gerer les ingredients exclus/preferes ?
**Answer:** Saisie libre avec suggestions/auto-completion sur une liste interne qui peut grandir. Implementation via champ texte + tags.

**Q4:** Quelle architecture de base de donnees pour les preferences ?
**Answer:** Tables separees (plus flexible). Permet une meilleure evolutivite et des requetes plus optimisees.

**Q5:** Quelle UX pour l'ecran de profil ?
**Answer:** Deux modes distincts:
- Mode lecture: interface propre et lisible pour consulter
- Bouton "Modifier" pour passer en mode edition
- Boutons "Enregistrer" et "Annuler" en mode edition

**Q6:** Le nombre de portions doit-il etre inclus en v1 ?
**Answer:** Oui, inclure dans v1 - essentiel pour le planning familial et les courses. Permet d'adapter les quantites selon la taille du foyer.

**Q7:** Quelles validations et contraintes appliquer ?
**Answer:**
- **Incompatibilites regimes:**
  - Vegetalien incompatible avec Pescetarien, Sans boeuf, Sans porc (selection mutuellement exclusive)
- **Combinaisons avec avertissement:**
  - Halal + Casher: autorise mais afficher message "Verifiez la coherence"
- **Allergies:** Multi-selection sans incompatibilite
- **Ingredients:** Limite de 30 tags maximum
- **Normalisation:** Texte en lowercase et trim automatique

**Q8:** Quelles fonctionnalites exclure de la v1 ?
**Answer:** Aucune exclusion - tout est inclus dans cette version.

---

### Existing Code to Reference

**Similar Features Identified:**
- Feature: Authentication System - Path: Implementation existante pour patterns d'API et structure Supabase
- Components a potentiellement reutiliser: Patterns de formulaires, gestion d'etat, validation
- Backend logic a referencer: Service patterns, structure des endpoints, middleware auth

---

### Follow-up Questions

Aucune question de suivi necessaire - les reponses sont completes et detaillees.

---

## Visual Assets

### Files Provided:
Aucun fichier visuel trouve dans le dossier `/planning/visuals/`.

### Visual Insights:
L'utilisateur indique d'utiliser la maquette principale existante et d'adapter si besoin. Reference a une maquette externe non fournie dans le dossier.

---

## Requirements Summary

### Functional Requirements

**Gestion des regimes alimentaires:**
- Afficher liste de 7 regimes: Vegetarien, Vegetalien, Sans porc, Sans boeuf, Pescetarien, Halal, Casher
- Permettre selection multiple avec validation des incompatibilites
- Vegetalien exclut automatiquement Pescetarien, Sans boeuf, Sans porc

**Gestion des allergies:**
- Afficher liste de 10-12 allergenes predefinies
- Permettre multi-selection sans restriction
- Liste: Gluten, Lactose, Fruits a coque, Arachides, Oeufs, Poisson, Fruits de mer, Soja, Sesame, Moutarde, Celeri
- Optionnel v1: Sulfites, Lupin

**Gestion des ingredients exclus/preferes:**
- Champ de saisie libre avec auto-completion
- Affichage sous forme de tags
- Limite de 30 tags maximum par categorie
- Normalisation automatique (lowercase, trim)
- Liste de suggestions interne evolutive

**Nombre de portions:**
- Champ pour definir la taille du foyer
- Utilise pour adapter les quantites dans le planning et les courses

**Interface utilisateur:**
- Mode lecture: affichage propre des preferences actuelles
- Mode edition: acces via bouton "Modifier"
- Actions en mode edition: "Enregistrer" et "Annuler"
- Transition fluide entre les deux modes

**Validations et feedback:**
- Message d'avertissement si Halal + Casher selectionnes ensemble
- Prevention des combinaisons impossibles (Vegetalien + Pescetarien)
- Feedback visuel sur les erreurs de saisie

---

### Reusability Opportunities

- **Patterns d'authentification:** Reutiliser la structure de services et endpoints du systeme d'auth existant
- **Composants de formulaire:** Potentiellement des composants Input, Button, Toggle existants
- **Gestion d'etat:** Pattern de store Zustand si deja implemente
- **Middleware auth:** Reutilisation du `get_current_user` pour securiser les endpoints profil

---

### Scope Boundaries

**In Scope:**
- Ecran complet de profil utilisateur
- CRUD des preferences alimentaires (regimes)
- CRUD des allergies
- CRUD des ingredients exclus/preferes
- Gestion du nombre de portions
- Mode lecture et mode edition
- Validations et contraintes metier
- Persistance Supabase
- API Backend FastAPI

**Out of Scope:**
- Gestion de plusieurs profils (membres famille) - potentielle v2
- Synchronisation avec recettes (sera fait dans feature "Recipe Filtering")
- Photo de profil
- Informations personnelles (nom, email) - deja gere par auth
- Historique des modifications

---

### Technical Considerations

**Base de donnees:**
- Tables separees pour flexibilite et performance
- Tables suggerees: `user_dietary_preferences`, `user_allergies`, `user_excluded_ingredients`, `user_preferred_ingredients`
- Relation avec table `users` existante via `user_id`

**API Backend:**
- Endpoints CRUD pour chaque type de preference
- Validation des incompatibilites cote serveur
- Normalisation des donnees avant insertion

**Mobile Frontend:**
- Composant ecran avec deux etats (lecture/edition)
- Composants reutilisables: chips/tags, multi-select, autocomplete
- Gestion d'etat locale pour le mode edition avant sauvegarde

**Securite:**
- Tous les endpoints proteges par authentification JWT
- Validation des donnees entrantes (Pydantic)
- RLS Supabase sur les tables de preferences

**Performance:**
- Chargement des suggestions d'ingredients en lazy loading
- Cache local des preferences utilisateur
