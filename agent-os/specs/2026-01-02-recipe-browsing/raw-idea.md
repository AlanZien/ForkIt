# Recipe Browsing Feature

## Idea
Permettre aux utilisateurs de parcourir et rechercher des recettes via l'API TheMealDB. L'application affiche les recettes par catégories et permet une recherche par nom. Chaque recette peut être consultée en détail avec ses ingrédients et instructions.

## User Stories
- En tant qu'utilisateur, je veux voir les catégories de recettes pour explorer facilement
- En tant qu'utilisateur, je veux rechercher une recette par son nom
- En tant qu'utilisateur, je veux voir les recettes d'une catégorie
- En tant qu'utilisateur, je veux voir les détails d'une recette (ingrédients, instructions)
- En tant qu'utilisateur, je veux obtenir une recette aléatoire pour m'inspirer

## Technical Notes
- API externe: TheMealDB (https://www.themealdb.com/api.php)
- Pas de clé API requise pour le POC (utilisation de l'API gratuite)
- Backend FastAPI comme proxy pour l'API externe
- Mobile React Native avec Zustand pour la gestion d'état
