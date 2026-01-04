# Agent-OS Usage Guide

## Workflow Tracks

Agent-OS utilise trois tracks adaptes a la complexite de la feature. Le track est **detecte automatiquement** lors du `/shape-spec` mais peut etre override.

---

## Les 3 Tracks

| Track | Score | Duree | Quand l'utiliser |
|-------|-------|-------|------------------|
| 🚀 **FAST** | ≤ 8 pts | 1-3 jours | Bug fixes, petites features, ajustements |
| ⚙️ **STANDARD** | 9-20 pts | 3-7 jours | Features completes, nouveaux ecrans |
| 🏗️ **COMPLEX** | > 20 pts | 1-3 semaines | Multi-composants, integrations complexes |

---

## 🚀 Track FAST

### Workflow
```
/shape-spec → /write-spec → /create-tasks → /implement-tasks
```

### Caracteristiques
- Pas de test-plan obligatoire
- Implementation directe
- Verification standards uniquement

### Exemples
- Ajouter un bouton logout
- Fix bug d'affichage
- Nouveau champ dans un formulaire existant
- Ajustements styling/CSS

---

## ⚙️ Track STANDARD

### Workflow
```
/shape-spec → /write-spec → /plan-tests → /create-tasks → /implement-tasks → /verify
```

### Caracteristiques
- **Test-plan obligatoire** (TDD)
- Implementation avec tests
- Verification complete

### Exemples
- Recipe Browsing (liste + detail)
- Shopping List Generation
- User Profile & Preferences
- Favoris avec persistence

---

## 🏗️ Track COMPLEX

### Workflow
```
/shape-spec → /verify-spec → /write-spec → /plan-tests → /create-tasks → /orchestrate-tasks → /verify
```

### Caracteristiques
- **Verification de spec obligatoire**
- Test-plan exhaustif
- **Orchestration parallele** des agents
- Suite de verification complete

### Exemples
- Systeme d'authentification complet
- AI-Powered Menu Suggestions
- Offline Support avec sync
- Systeme de paiement

---

## Detection Automatique

Lors du `/shape-spec`, l'agent analyse les requirements et calcule un score de complexite :

| Element | Points |
|---------|--------|
| UI Components (ecrans, modals, forms) | 1 pt chacun |
| API Endpoints | 2 pts chacun |
| Database Changes (tables, migrations) | 3 pts chacun |
| External Integrations | 5 pts chacun |
| User Scenarios | 0.5 pts chacun |
| State Management (stores) | 2 pts chacun |
| Auth/Security implique | 3 pts |

### Exemple de calcul

**Feature : Shopping List Generation**
- UI Components : 3 (liste, categories, items) = 3 pts
- API Endpoints : 2 (GET list, PATCH item) = 4 pts
- DB Changes : 1 (table shopping_items) = 3 pts
- User Scenarios : 5 = 2.5 pts
- State Management : 1 (store) = 2 pts

**Total : 14.5 pts → ⚙️ STANDARD**

---

## Override du Track

Apres l'analyse, vous pouvez override le track recommande :

```
🎯 RECOMMENDED TRACK: ⚙️ STANDARD

Do you accept this track? (yes/override with: fast, standard, complex)
> fast
```

### Raisons de faire un override

| Override | Raison valide |
|----------|---------------|
| → FAST | Feature bien comprise, pattern existant, deadline serre |
| → STANDARD | Feature critique meme si petite, besoin de tests |
| → COMPLEX | Integration avec systemes externes, risque eleve |

---

## Fichiers generes par track

### 🚀 FAST
```
agent-os/specs/YYYY-MM-DD-feature-name/
├── raw-idea.md
├── planning/
│   ├── requirements.md
│   └── track.md
├── spec.md
└── tasks.md
```

### ⚙️ STANDARD
```
agent-os/specs/YYYY-MM-DD-feature-name/
├── raw-idea.md
├── planning/
│   ├── requirements.md
│   ├── track.md
│   └── visuals/
├── spec.md
├── tasks.md
├── test-plan.md          ← Obligatoire
└── verifications/
    └── final-verification.md
```

### 🏗️ COMPLEX
```
agent-os/specs/YYYY-MM-DD-feature-name/
├── raw-idea.md
├── planning/
│   ├── requirements.md
│   ├── track.md
│   └── visuals/
├── spec.md
├── spec-verification.md  ← Obligatoire
├── tasks.md
├── test-plan.md          ← Obligatoire
├── implementation/
│   └── [task-group-reports]
└── verifications/
    └── final-verification.md
```

---

## Commandes par Track

| Commande | FAST | STANDARD | COMPLEX |
|----------|------|----------|---------|
| `/shape-spec` | ✅ | ✅ | ✅ |
| `/verify-spec` | - | - | ✅ Obligatoire |
| `/write-spec` | ✅ | ✅ | ✅ |
| `/plan-tests` | Optionnel | ✅ Obligatoire | ✅ Obligatoire |
| `/create-tasks` | ✅ | ✅ | ✅ |
| `/implement-tasks` | ✅ | ✅ | - |
| `/orchestrate-tasks` | - | - | ✅ |
| Verification finale | Standards only | ✅ Complet | ✅ Complet |

---

## Regle de decision rapide

> **En cas de doute, laissez la detection automatique decider.**

Le calcul du score est base sur des criteres objectifs. Si vous pensez que le track recommande est incorrect, c'est souvent parce que :

1. Vous sous-estimez la complexite (laissez STANDARD)
2. Vous avez deja un pattern similaire (override vers FAST)
3. La feature a des implications cachees (override vers COMPLEX)

---

## Notes

- Le track est sauvegarde dans `planning/track.md`
- Changer de track en cours de route est possible mais deconseille
- Les standards (`verify-standards.sh`) sont verifies a tous les tracks
- La sync Notion fonctionne a tous les tracks
