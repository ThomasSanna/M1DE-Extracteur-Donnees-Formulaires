# TP2 — Projet de développement avec IA

## Informations générales

**Modalité** : Individuel
**Évaluation** : Sur livrables, sans soutenance orale  
**Outils autorisés** : Claude, ChatGPT, Cursor, Claude Code, Copilot... tous les outils IA

---

## Ce que ce TP évalue

En 2026, générer du code avec l'IA est trivial. Ce n'est plus une compétence.

**Ce qu'on évalue :**

| On évalue | On n'évalue plus |
|-----------|------------------|
| Ta capacité à formuler un besoin clair | Le volume de code |
| Ta compréhension de ce que l'IA génère | Le fait que ça compile |
| Tes choix d'architecture et leur justification | La vitesse d'exécution |
| Ta gestion des cas limites | Le nombre de features |
| Ton processus d'itération documenté | Les commentaires décoratifs |

**Question centrale** : As-tu construit quelque chose que tu comprends et pourrais maintenir ?

---

## Déroulement

### Cadrage

Choix du projet, analyse du problème, décisions techniques.

**Livrable** : Document de cadrage (1 page)
- Le problème que tu résous (avec tes mots)
- Tes choix techniques justifiés
- Ce que tu ne feras PAS (scope négatif)
- Les difficultés anticipées

### Développement 

Tu développes avec l'IA. Tu documentes dans ton journal.

**À chaque session** :
- Objectif clair
- Prompts significatifs notés
- Problèmes rencontrés → solutions trouvées
- Ce que tu as appris

### Finalisation 

Tests des cas limites, documentation, polish.

**Livrables finaux** :
- Code fonctionnel
- README (installation + utilisation)
- Journal de développement
- Documentation des choix

---

## Évaluation (100 points)

### Fonctionnalité — 25 points

| Critère | Points |
|---------|--------|
| Le projet démarre sans erreur | 5 |
| Les fonctionnalités principales marchent | 10 |
| Les cas limites sont gérés | 5 |
| C'est utilisable (pas juste "ça tourne") | 5 |

### Journal de développement — 25 points

| Critère | Points |
|---------|--------|
| Prompts documentés avec contexte | 8 |
| Itérations et corrections expliquées | 7 |
| Réflexion sur ce qui a marché/échoué | 5 |
| Évolution visible de la compréhension | 5 |

**Bonne entrée de journal :**
```
Session 2 — Objectif : implémenter la recherche sémantique

Prompt : "Ajoute une recherche par embeddings sur mes chunks. 
Utilise l'API OpenAI text-embedding-3-small."

Problème : le code généré stockait les embeddings en mémoire.
Avec 500 chunks, ça crashait au redémarrage (tout perdu).

Solution : j'ai demandé de persister dans un fichier JSON.
Pas optimal mais suffisant pour le MVP.

Apprentissage : toujours penser à la persistance dès le début.
```

**Mauvaise entrée :**
```
J'ai demandé à Claude de faire la recherche. Ça marche.
```

### Compréhension technique — 25 points

Questionnaire écrit de 15/30 minutes (sans IA, sans ordinateur).

Questions type :
- "Explique ce que fait cette fonction de ton code"
- "Si on voulait ajouter X, que faudrait-il modifier ?"
- "Que se passe-t-il si l'utilisateur fait Y ?"

### Documentation — 15 points

| Critère | Points |
|---------|--------|
| README clair et utilisable | 5 |
| Architecture expliquée | 5 |
| Choix techniques justifiés | 5 |

### Qualité — 10 points

| Critère | Points |
|---------|--------|
| Gestion des erreurs | 3 |
| Pas de crash sur inputs invalides | 4 |
| Code maintenable | 3 |

---

## Les pièges classiques

### Piège 1 : Accepter du code sans comprendre

Tu copies le code de l'IA, ça marche, tu passes à la suite. Au questionnaire, tu ne sais pas expliquer.

**Solution** : Pour chaque bloc généré, demande-toi "est-ce que je pourrais l'expliquer à quelqu'un ?"

### Piège 2 : Le projet trop ambitieux

Tu veux tout faire. À la fin, rien ne marche vraiment.

**Solution** : Un MVP (Minimum Viable Product) qui marche vaut mieux qu'un projet complet qui crashe.

### Piège 3 : Pas de gestion d'erreurs

L'IA génère le "happy path". Dès qu'on sort du cas normal, ça explose.

**Solution** : Teste avec des inputs vides, trop longs, mal formatés.

### Piège 4 : Le journal vide

Tu codes, tu oublies de documenter. À la fin, tu ne te souviens plus.

**Solution** : Note en temps réel, même juste 3 lignes par session.

---

## Structure des livrables

```
mon-projet/
├── README.md              # Description, installation, utilisation
├── JOURNAL.md             # Journal de développement
├── src/                   # Code source
└── .env.example           # Variables d'environnement (sans secrets)
```

---

# LES 15 PROJETS

Chaque projet a un **MVP** (objectif minimal) et une **version avancée** (pour ceux qui vont plus vite).

## Projet 13 : Extracteur de données de formulaires

### Le vrai problème

Tu reçois des formulaires remplis (PDF, images, emails mal formatés). Tu dois extraire les données et les mettre dans ton système. Copier-coller manuel, c'est des heures.

### Ce que tu construis

Un extracteur qui prend des formulaires variés, extrait les champs selon un schéma défini, valide, et signale les problèmes.

### Techniques IA utilisées

- **Extraction structurée** : mapping vers un schéma
- **Validation** : règles métier, cohérence
- **Gestion d'erreur** : champs manquants, illisibles

### Architecture requise

```
┌─────────────────┐     ┌──────────────────┐
│ Schéma attendu  │────▶│                  │
│ (champs, types) │     │                  │
└─────────────────┘     │ Extraction IA    │────▶ JSON structuré
                        │                  │
┌─────────────────┐     │                  │
│ Document input  │────▶│                  │
│ (texte/pdf)     │     └────────┬─────────┘
└─────────────────┘              │
                        ┌────────▼─────────┐
                        │ Validation +     │
                        │ Signalement      │
                        └──────────────────┘
```

### MVP (6h)

- Définition d'un schéma (JSON Schema simple)
- Extraction de documents texte vers le schéma
- Validation des types et des contraintes basiques
- Chaque champ a un niveau de confiance
- Les champs non trouvés ou douteux sont signalés
- Export JSON valide

### Version avancée

- Règles de validation métier (ex: IBAN valide, date cohérente)
- Traitement batch (plusieurs documents)
- Interface de correction manuelle
- Apprentissage des corrections (amélioration continue)

### Critères spécifiques

- Le JSON produit est valide contre le schéma
- Les champs "confiance basse" sont vraiment douteux
- Pas d'invention (champ absent = null, pas de valeur inventée)