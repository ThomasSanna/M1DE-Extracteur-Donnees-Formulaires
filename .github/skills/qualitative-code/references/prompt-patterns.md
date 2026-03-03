# Patrons pour l'affinage de prompts

Transformer des requêtes vagues en prompts précis et orientés qualité pour générer un meilleur code.

## Anatomie d'un prompt de qualité

```
[CONTEXTE] + [EXIGENCE] + [CONTRAINTES] + [CRITÈRES_DE_QUALITÉ]
```

### Prompt basique (Faible qualité)
```
Créer une fonction de recherche pour mon application
```

### Prompt amélioré (Haute qualité)
```
Contexte : Application de gestion de documents (~500 fichiers Markdown).
Recherche par mots-clés actuellement utilisée, elle manque des contenus sémantiquement proches.

Exigence : Implémenter une recherche sémantique basée sur des embeddings.

Contraintes techniques :
- Utiliser l'API OpenAI `text-embedding-3-small`
- Persister les embeddings dans un fichier JSON (pas de base externe)
- Signature : `searchSimilarChunks(query: string, topK: number = 5)`
- Type de retour : `Array<{chunk: string, similarity: number}>`

Critères de qualité :
- Nommage en camelCase
- Gérer les cas limites : requête vide, fichier d'embeddings manquant, timeout API
- Responsabilité unique : séparer génération d'embeddings et recherche
- Ajouter des commentaires JSDoc pour les fonctions publiques
- Gestion d'erreurs avec try-catch et messages significatifs

Cas limites à gérer :
1. Premier lancement (pas de `embeddings.json`) → créer le fichier
2. Timeout API → réessayer une fois, puis échouer proprement
3. Chaîne de requête vide → lever une erreur de validation
4. Chunks supprimés → filtrer les embeddings obsolètes

Rendre le code modulaire pour une future migration vers une base vectorielle.
```

## Bibliothèque de patrons

### 1. Implémentation d'une fonctionnalité

```markdown
Contexte : [Brève description du système, état actuel]

Fonctionnalité : [Ce que vous voulez ajouter]

Points d'intégration :
- [Où cela se connecte au code existant]
- [Dépendances]

Critères d'acceptation :
- [Exigences fonctionnelles précises]
- [Objectifs de performance si pertinents]

Exigences de qualité :
- Nommage : camelCase
- Gestion d'erreurs : [scénarios spécifiques]
- Validation : [contraintes d'entrée]
- Logging : [quoi logger et à quel niveau]

Exemple d'utilisation :
[Extrait de code montrant l'appel attendu]
```

### 2. Refactorisation

```markdown
Problème courant :
[Code smell ou problème spécifique]

Code à refactorer :
```[langage]
[coller le code problématique]
```

Objectif du refactor :
[Quel pattern appliquer ou améliorer]

Contraintes :
- [ ] Préserver l'API/interface existante
- [ ] Ne pas casser les tests existants
- [ ] Maintenir la compatibilité

Améliorations attendues :
- [Métrique cible : ex. réduire la longueur d'une fonction < 30 lignes]
- [Pattern : ex. extraire un service]

Résultat attendu :
[Comment le code doit être structuré après refactor]
```

### 3. Correction de bug

```markdown
Description du bug :
[Symptôme observable]

Étapes pour reproduire :
1. [Action]
2. [Action]
3. [Erreur observée]

Comportement attendu :
[Ce qui devrait se passer]

Code actuel :
```[langage]
[section de code concernée]
```

Détails d'erreur :
[Message d'erreur, stack trace si disponible]

Hypothèse :
[Votre théorie sur la cause racine]

Exigences pour la correction :
- [ ] Résoudre la cause racine (pas seulement le symptôme)
- [ ] Ajouter une vérification défensive pour éviter la régression
- [ ] Inclure un test pour ce scénario
- [ ] Logger une erreur significative si cela se reproduit
```

### 4. Conception d'API

```markdown
But de l'API :
[Ce que fait cet endpoint]

Route RESTful :
[méthode HTTP] /api/v1/[ressource]

Schéma de requête :
```json
{
  "field": "type",
  "constraints": "règles de validation"
}
```

Schéma de réponse (Succès) :
```json
{
  "statusCode": 200,
  "data": { }
}
```

Réponses d'erreur :
- 400 : [condition → message]
- 401 : [condition → message]
- 404 : [condition → message]
- 500 : [condition → message]

Logique métier :
1. [Étape de validation]
2. [Étape de traitement]
3. [Étape de persistance]
4. [Étape de retour]

Exigences de qualité :
- Validation des entrées avec messages clairs
- Codes HTTP appropriés
- Format de réponse cohérent
- Prédisposition au rate limiting (express-rate-limit)
- Sécurité : [auth, sanitation]
```

### 5. Schéma de base de données

```markdown
Entité : [Nom en PascalCase]

But : [Ce que représente l'entité dans le domaine]

Champs :
| Nom | Type | Contraintes | Justification |
|-----|------|-------------|--------------|
| id | UUID | PK, non null | Identifiant unique |
| createdAt | timestamp | non null, défaut now() | Audit |
| [champ] | [type] | [contraintes] | [raison] |

Relations :
- [Entité] a plusieurs [Ceci] (1:N)
- [Ceci] appartient à [Entité] (clé étrangère : entityId)

Indexes :
- [champ] — Raison : [motif de requête fréquent]

Exemples de requêtes :
1. [Requête courante supportée]
2. [Autre cas d'usage attendu]

Stratégie de migration :
[Comment créer / faire évoluer ce schéma]
```

## Checklist d'affinage de prompt

Avant d'envoyer un prompt à l'IA, vérifiez :

### Contexte fourni
- [ ] Système / domaine décrit
- [ ] État actuel expliqué
- [ ] Problème clairement formulé

### Exigences spécifiées
- [ ] Exigences fonctionnelles listées
- [ ] Contraintes techniques définies
- [ ] Critères de succès explicites

### Critères de qualité
- [ ] Nommage précisé (camelCase)
- [ ] Gestion d'erreurs spécifiée
- [ ] Validation des entrées requise
- [ ] Structure du code (modularité, patterns)

### Cas limites
- [ ] Au moins 3 cas limites identifiés
- [ ] Comment chacun doit être géré

### Exemples fournis
- [ ] Exemple input/output
- [ ] Exemple d'utilisation
- [ ] Scénarios d'erreur

## Anti-patrons à éviter

### ❌ Exigences vagues
"Améliore ça"
"Ajoute un peu de gestion d'erreurs"
"Optimise le code"

### ✅ Exigences spécifiques
"Extraire la logique dupliquée dans une fonction réutilisable avec objet de config"
"Ajouter try-catch pour les appels API avec stratégie de retry (3 tentatives, backoff)"
"Réduire la complexité temporelle de O(n²) à O(n log n) en utilisant merge sort"

---

### ❌ Contexte manquant
"Créer une fonction de login"

### ✅ Contexte inclus
"Créer une fonction de login pour une app Express utilisant JWT. Session en Redis TTL 24h. bcrypt pour le hash des mots de passe. Retourner 401 pour identifiants invalides, 500 pour erreurs serveur."

---

### ❌ Pas de critères de qualité
"Écrire une fonction de recherche"

### ✅ Critères de qualité
"Écrire une fonction de recherche en respectant :
- Nommage camelCase
- Commentaires JSDoc
- Validation d'entrée (TypeError si invalide)
- Vérifications null défensives
- Responsabilité unique (parsing séparé de la recherche)
- Longueur max : 30 lignes"

---

### ❌ Tout en une fois
"Construire tout le système de gestion d'utilisateurs"

### ✅ Approche incrémentale
"Phase 1 : Modèle utilisateur avec validation (email, robustesse mot de passe)
Phase 2 : Endpoint d'inscription avec détection de doublons
Phase 3 : Login avec génération de JWT
Phase 4 : Flux de réinitialisation de mot de passe"

## Patrons d'itération

### Première génération → Revue → Raffinement

**Itération 1 : Faire fonctionner**
```
Prompt basique centré sur la fonctionnalité
```

**Revue :**
- Compile-t-il ?
- Le happy path fonctionne-t-il ?
- Qu'est-ce qui manque ?

**Itération 2 : Ajouter la qualité**
```
Prompt original + problèmes identifiés :
- Ajouter la gestion d'erreurs pour [cas spécifique]
- Extraire [code dupliqué] en [pattern]
- Renommer [variable confuse] en [nom descriptif]
```

**Revue :**
- Cas limites gérés ?
- Code smell résolu ?
- Maintenable ?

**Itération 3 : Polissage**
```
Code précédent + documentation :
- Ajouter JSDoc avec exemples
- Inclure exemples d'utilisation dans les commentaires
- Documenter les cas limites non évidents
```

## Modèles de prompt par cas d'usage

### Traitement de données
```
Traiter [source de données] pour extraire [information].

Format d'entrée :
[Schéma ou exemple]

Logique de transformation :
1. [Étape]
2. [Étape]

Format de sortie :
[Schéma ou exemple]

Cas limites :
- Entrée malformée → [gestion]
- Champ requis manquant → [gestion]
- Type invalide → [gestion]

Performance : Traiter [volume] en [temps imparti]
```

### Intégration
```
Intégrer [service externe] pour [but].

Authentification : [méthode]
Endpoint API : [URL]
Format de requête : [schéma]
Format de réponse : [schéma]

Scénarios d'erreur :
- Limite de quota → [backoff]
- Timeout → [stratégie de retry]
- Réponse invalide → [fallback]

Configuration :
- Stockage clé API : [var d'environnement]
- Timeout : [durée]
- Retries : [nombre et stratégie]
```

### Tests
```
Créer des tests pour [composant].

Framework : [Jest, Mocha, etc.]

Cas de test :
1. Happy path : [scénario → attendu]
2. Cas limite : [scénario → attendu]
3. Cas d'erreur : [scénario → attendu]

Mocks nécessaires :
- [Dépendance externe] → [comportement simulé]

Objectif de couverture : [X]% pour [composant]
```

## Mesurer la qualité d'un prompt

Un bon prompt doit permettre de répondre OUI à :
- Quelqu'un d'autre peut-il comprendre ce qu'il faut construire ?
- Les critères de succès sont-ils mesurables ?
- Les cas limites sont-ils explicitement traités ?
- Y a-t-il assez de contexte pour décider ?
- Les attentes de qualité sont-elles claires et spécifiques ?

## Ressources associées

- [Checklists de revue de code](./review-templates.md)
- [Records de décisions d'architecture](./adr-template.md)
