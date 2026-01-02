# Agent-OS Usage Guide

## Quand utiliser agent-os ?

Ce guide aide a decider quel niveau de workflow utiliser selon la complexite de la feature.

---

## Niveaux de workflow

| Niveau | Criteres | Workflow | Duree estimee |
|--------|----------|----------|---------------|
| **Direct** | < 5 fichiers, pattern existant | Pas de spec, implementation directe | < 2h |
| **Leger** | 5-15 fichiers, nouveau pattern | spec.md + tasks.md | 2h - 1 jour |
| **Complet** | > 15 fichiers, architecture nouvelle | Tous les agents | > 1 jour |

---

## Direct (sans agent-os)

### Quand l'utiliser
- Bug fixes
- Ajout d'un champ a un formulaire existant
- Nouvelle route API simple (CRUD basique)
- Modifications de texte/traduction
- Ajustements CSS/styling

### Processus
1. Comprendre le probleme
2. Implementer directement
3. Tester
4. Commit

---

## Leger (spec + tasks)

### Quand l'utiliser
- Nouveau composant UI reutilisable
- Integration API externe simple
- Nouvelle page avec etat local
- Feature avec 2-3 couches (backend + mobile)

### Fichiers a creer
```
agent-os/specs/YYYY-MM-DD-feature-name/
  raw-idea.md      # Idee brute (optionnel)
  spec.md          # Specification technique
  tasks.md         # Liste des taches
  user-tests.md    # Tests utilisateur (optionnel)
```

### Processus
1. Ecrire spec.md avec les endpoints, modeles, UI
2. Decouper en tasks.md avec groupes et dependances
3. Implementer groupe par groupe
4. Valider avec tests

### Exemple
- Recipe Browsing (ForkIt)
- User Profile & Preferences (ForkIt)

---

## Complet (tous les agents)

### Quand l'utiliser
- Systeme de paiement/abonnement
- Notifications push avec backend
- Systeme de recommandation/ML
- Refactoring majeur d'architecture
- Multi-tenancy / multi-workspace
- Features avec 5+ couches interdependantes

### Agents disponibles
| Agent | Role |
|-------|------|
| `spec-initializer` | Initialise le dossier spec |
| `spec-shaper` | Affine les requirements via questions |
| `spec-writer` | Ecrit la specification detaillee |
| `task-list-creator` | Cree le decoupage en taches |
| `test-planner` | Planifie les tests techniques |
| `implementer` | Implemente les taches |
| `implementation-verifier` | Verifie l'implementation |

### Processus
1. `/agent-os:shape-spec` - Clarifier les besoins
2. `/agent-os:write-spec` - Specification complete
3. `/agent-os:create-tasks` - Decoupage strategique
4. `/agent-os:plan-tests` - Plan de tests
5. `/agent-os:implement-tasks` - Implementation
6. Verification et sync Notion

---

## Regle de decision rapide

> **"Est-ce que je peux expliquer la feature en 1 paragraphe ?"**

| Reponse | Niveau |
|---------|--------|
| Oui, c'est simple | **Direct** |
| Oui, mais avec des details techniques | **Leger** |
| Non, c'est complexe avec plusieurs systemes | **Complet** |

---

## Exemples par categorie

### Backend seul
| Feature | Niveau |
|---------|--------|
| Ajouter un champ au modele User | Direct |
| Nouveau endpoint CRUD | Direct |
| Integration TheMealDB | Leger |
| Systeme de cache Redis | Complet |

### Mobile seul
| Feature | Niveau |
|---------|--------|
| Fix bug affichage | Direct |
| Nouveau composant bouton | Direct |
| Ecran avec formulaire + validation | Leger |
| Navigation complexe multi-stack | Complet |

### Full-stack
| Feature | Niveau |
|---------|--------|
| Ajouter un champ profile | Direct |
| Recipe Browsing (liste + detail) | Leger |
| Systeme d'authentification complet | Complet |
| Real-time collaboration | Complet |

---

## Notes

- En cas de doute, commencer par **Leger** et ajuster
- Le workflow **Complet** n'est pas toujours necessaire meme pour les grosses features
- La sync Notion est optionnelle a tous les niveaux
- Les user-tests.md peuvent etre crees meme en mode Direct pour des features critiques
