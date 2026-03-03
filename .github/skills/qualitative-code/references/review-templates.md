# Modèles de revue de code

Listes de vérification rapides pour valider la qualité du code généré.

## Revue de sécurité rapide

```markdown
- [ ] Pas de secrets en dur (clés API, mots de passe, tokens)
- [ ] Les entrées utilisateur sont validées et assainies
- [ ] Requêtes SQL/NoSQL paramétrées
- [ ] Chemins de fichiers validés (pas de traversal)
- [ ] Authentification requise pour opérations sensibles
- [ ] Les messages d'erreur ne fuité pas d'informations sensibles
```

## Revue de performance

```markdown
- [ ] Pas de pattern N+1
- [ ] Requêtes DB avec index appropriés
- [ ] Les gros jeux de données paginés, pas chargés entièrement
- [ ] Opérations coûteuses mises en cache si possible
- [ ] Pas d'opérations synchrones bloquantes (event loop)
- [ ] Ressources libérées (connexions, handles de fichiers)
```

## Checklist qualité des fonctions

Pour chaque fonction générée :

```markdown
Fonction : [nom]

- [ ] Responsabilité unique : fait UNE chose
- [ ] Nommage : verbe décrivant l'action (getUserById, calculateTotal)
- [ ] Paramètres : ≤ 3 (utiliser objet de config si plus)
- [ ] Type de retour : cohérent et documenté
- [ ] Effets de bord : documentés ou évités
- [ ] Gestion d'erreur : try-catch ou retour d'erreur
- [ ] Testabilité : testable en isolation
- [ ] Longueur : < 50 lignes (extraire si plus long)
```

## Validateur de conventions de nommage

```markdown
**Variables & Fonctions :** camelCase
✓ userName, fetchDataFromApi, isValid
✗ user_name, FetchDataFromAPI, is_valid

**Classes & Types :** PascalCase
✓ UserProfile, ApiResponse, ConfigManager
✗ userProfile, apiresponse, config_manager

**Constantes :** UPPER_SNAKE_CASE (ou const camelCase)
✓ MAX_RETRY_COUNT, API_BASE_URL
✓ maxRetryCount (si utilisé en const)
✗ MaxRetryCount, max_retry_count

**Membres privés :** préfixe _ (optionnel, selon langage)
✓ _internalState, _handleError
✓ internalState (si le langage a le mot-clé private)

**Booléens :** noms prédicats
✓ isActive, hasPermission, canEdit
✗ active, permission, edit
```

## Revue de conception d'API

```markdown
- [ ] Principes RESTful suivis
- [ ] Méthodes HTTP correctes (GET, POST, PUT, DELETE)
- [ ] Codes de statut appropriés (200, 201, 400, 404, 500)
- [ ] Schémas requête/réponse définis
- [ ] Stratégie de versioning en place (/v1/...)
- [ ] Rate limiting envisagé
- [ ] CORS correctement configuré
```

## Revue de conception de base de données

```markdown
- [ ] Normalisation appropriée (ni trop, ni trop peu)
- [ ] Clés primaires sur toutes les tables
- [ ] Clés étrangères pour les relations
- [ ] Index sur colonnes fréquemment interrogées
- [ ] Timestamp (createdAt, updatedAt) pour audit
- [ ] Soft deletes si récupération nécessaire
- [ ] Stratégie de migration pour évolutions de schéma
```

## Audit des dépendances

```markdown
Librairie : [nom]

- [ ] Pourquoi est-elle nécessaire ? [cas d'usage]
- [ ] Alternative envisagée : [quoi d'autre fonctionnerait ?]
- [ ] Impact sur la taille du bundle : [acceptable ?]
- [ ] Statut de maintenance : [activement maintenue ?]
- [ ] Licence compatible : [avec la licence du projet ?]
- [ ] Sécurité : [vulnérabilités connues ?]
```

## Déclencheurs de refactor

Si vous observez ces patterns, refactoriser avant d'accepter :

**Code smells :**
- Fonctions > 50 lignes
- Paramètres > 3
- Profondeur d'imbrication > 3
- Blocages de code dupliqué
- Objets "god" (classes > 10 méthodes)
- Nombres magiques non expliqués
- Commentaires expliquant le QUOI (le code doit montrer cela)

**Patterns de refactor :**
- Extraire fonction
- Extraire objet de config
- Remplacer conditionnelle par polymorphisme
- Remplacer nombre magique par constante
- Décomposer grande classe
- Introduire objet de paramètres
```
