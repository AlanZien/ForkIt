# ForkIt - Idees d'ameliorations

Ce document recense les idees d'ameliorations futures pour l'application ForkIt.

---

## 1. Internationalisation (i18n)

### Interface multilingue FR/EN
- **Effort** : 1-2 jours
- **Techno** : expo-localization + i18next
- **Taches** :
  - [ ] Setup bibliotheque i18n
  - [ ] Extraction des textes (~50-80 composants)
  - [ ] Fichiers de traduction FR/EN
  - [ ] Selecteur de langue dans Profil
  - [ ] Detection automatique de la langue du telephone
  - [ ] Persistance du choix utilisateur

---

## 2. Sources de recettes

### Etat actuel
- **TheMealDB** : ~1000 recettes internationales (EN)
- **Recettes personnelles** : stockees dans Supabase

### Options d'APIs supplementaires

| API | Recettes | Gratuit | Langues |
|-----|----------|---------|---------|
| Spoonacular | 500k+ | 150 req/jour | EN |
| Edamam | 2M+ | 10k req/mois | EN |
| Tasty (RapidAPI) | 3k+ | 500 req/mois | EN |

### S'affranchir des APIs externes

#### Scrapers Marmiton (recettes francaises)
- [python-marmiton](https://github.com/remaudcorentin-dev/python-marmiton) - Python, simple
- [marmiton-api](https://github.com/SoTrxII/marmiton-api) - Node.js, complet
- [recipe_crawler](https://github.com/madeindjs/recipe_crawler) - Ruby, multi-sites
- [scrap-marmiton](https://github.com/yannguegan/scrap-marmiton) - Export JSON

#### Datasets open source
- [RecipeNLG](https://www.kaggle.com/datasets/paultimothymooney/recipenlg) - 2M+ recettes (EN)
- [Recipe Dataset 2M](https://www.kaggle.com/datasets/wilmerarltstrmberg/recipe-dataset-over-2m) - 2M+ (EN)
- [What's Cooking](https://www.kaggle.com/datasets/kaggle/recipe-ingredients-dataset) - 40k dont FR

#### Strategie recommandee
1. **Phase 1** : Scraper ~5000-10000 recettes Marmiton → Supabase
2. **Phase 2** : Enrichissement communautaire (UGC)
3. **Phase 3** : Generation IA (optionnel)

> **Note legale** : Verifier CGU pour usage commercial

---

## 3. Ameliorations UX

### Planning
- [x] Affichage des 7 prochains jours (a partir d'aujourd'hui)
- [ ] Drag & drop pour reorganiser les repas
- [ ] Vue mensuelle
- [ ] Repetition de repas (ex: tous les lundis)

### Recettes
- [ ] Filtre par source (API / Personnelle / Francaise)
- [ ] Mode hors-ligne (cache des recettes favorites)
- [ ] Timer integre pour la cuisson
- [ ] Mode pas-a-pas avec photos

### Liste de courses
- [ ] Regroupement par rayon de supermarche
- [ ] Integration avec apps de courses (Bring!, etc.)
- [ ] Historique des listes precedentes

### Profil
- [ ] Statistiques (recettes cuisinees, favorites, etc.)
- [ ] Partage de profil / recettes entre utilisateurs
- [ ] Mode famille (plusieurs profils)

---

## 4. Fonctionnalites avancees

### Intelligence artificielle
- [ ] Suggestions de recettes basees sur l'historique
- [ ] Generation de recettes a partir d'ingredients disponibles
- [ ] Analyse nutritionnelle automatique
- [ ] Reconnaissance d'image (photo → ingredients)

### Social
- [ ] Partage de recettes entre utilisateurs
- [ ] Commentaires et notes sur les recettes
- [ ] Feed d'activite (amis, tendances)

### Gamification
- [ ] Badges (premiere recette, 10 recettes, etc.)
- [ ] Defis hebdomadaires
- [ ] Streak de planification

---

## 5. Technique / Performance

- [ ] Cache agressif des images de recettes
- [ ] Optimisation du bundle size
- [ ] Tests E2E automatises
- [ ] CI/CD pour deploiement automatique
- [ ] Monitoring (Sentry, analytics)

---

## Priorites suggérées

| Priorite | Fonctionnalite | Impact utilisateur |
|----------|----------------|-------------------|
| 🔴 Haute | Base de recettes francaises | Tres eleve |
| 🔴 Haute | Interface FR/EN | Eleve |
| 🟡 Moyenne | Mode hors-ligne | Moyen |
| 🟡 Moyenne | Suggestions IA | Moyen |
| 🟢 Basse | Gamification | Faible |
| 🟢 Basse | Social | Faible |

---

*Derniere mise a jour : 4 janvier 2026*
