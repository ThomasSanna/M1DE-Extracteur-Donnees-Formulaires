# Modèle d'Architecture Decision Record (ADR)

Documentez les décisions architecturales importantes pour référence future.

## Format

```markdown
# ADR-[numéro] : [Titre court]

**Date :** YYYY-MM-DD
**Statut :** Proposé | Accepté | Déprécié | Remplacé
**Décideurs :** [Qui a pris la décision]

## Contexte
Quel est le problème à résoudre ? Quels facteurs sont en jeu ?

## Décision
Quel changement proposons-nous ?

## Justification
Pourquoi cette approche plutôt qu'une autre ?

### Options examinées
1. **[Option 1]**
   - Pour : [avantages]
   - Contre : [inconvénients]
   
2. **[Option 2]** ← SÉLECTIONNÉE
   - Pour : [avantages]
   - Contre : [inconvénients]
   
3. **[Option 3]**
   - Pour : [avantages]
   - Contre : [inconvénients]

### Pourquoi [Option sélectionnée] ?
[Justification détaillée]

## Conséquences
Qu'est-ce qui devient plus facile ou plus difficile du fait de cette décision ?

**Positif :**
- [bénéfice]
- [bénéfice]

**Négatif :**
- [compromis]
- [compromis]

**Neutre :**
- [changement sans bon/mauvais clair]

## Notes d'implémentation
Détails techniques sur la façon dont la décision sera mise en œuvre.

## Considérations futures
- Quand pourrions-nous réviser cette décision ?
- Qu'est-ce qui déclencherait un changement ?

## Références
- [Lien vers la documentation pertinente]
- [ADRs liés]
```

## Exemple d'ADR

```markdown
# ADR-001 : Utiliser un fichier JSON pour stocker les embeddings

**Date :** 2026-03-02
**Statut :** Accepté
**Décideurs :** Équipe de développement

## Contexte
Il faut persister les embeddings vectoriels pour la recherche sémantique entre les redémarrages de l'application.
Actuellement, ils sont stockés en mémoire, ce qui entraîne un recalcul à chaque lancement,
générant des appels API et des coûts inutiles (ex. ~0,02€ par relance pour 500 chunks).

## Décision
Stocker les embeddings dans un fichier JSON (`embeddings.json`) à la racine du projet.

## Justification

### Options examinées

1. **En mémoire uniquement**
   - Pour : Simple, pas d'I/O
   - Contre : Perdu au redémarrage, recalcul coûteux

2. **Fichier JSON** ← SÉLECTIONNÉ
   - Pour : Simple, lisible, contrôlable en version, pas de dépendances externes
   - Contre : Peu scalable (>10k vecteurs), pas d'indexation, chargement complet en mémoire

3. **Base vectorielle (Pinecone, Weaviate)**
   - Pour : Scalable, recherche similaire efficace, prête pour la production
   - Contre : Service externe, complexité d'installation, coût, surdimensionné pour un MVP

4. **SQLite avec extension vectorielle**
   - Pour : Local, persistant, plus scalable que JSON
   - Contre : Dépendance supplémentaire, complexité de migration

### Pourquoi le fichier JSON ?

Ceci est un MVP estimé à <1000 chunks. Le JSON offre :
- Zéro configuration initiale (bibliothèques standard)
- Format lisible pour le débogage
- Possibilité de commit dans Git pour reproductibilité
- Chemin de migration simple si besoin

La simplicité permet de se concentrer sur la fonctionnalité core plutôt que sur l'infrastructure.

## Conséquences

**Positif :**
- Implémentation immédiate, pas de dépendances nouvelles
- Embeddings mis en cache entre les exécutions (économie d'API)
- Possibilité d'inspecter/éditer le fichier manuellement
- Itération de développement rapide

**Négatif :**
- Lecture/écriture du fichier complet à chaque opération (pas incrémental)
- Recherche linéaire O(n) pour la similarité (acceptable <1k vecteurs)
- Limitation mémoire selon la RAM disponible
- Pas de sécurité pour accès concurrent

**Neutre :**
- Fichier à la racine du projet (peut être déplacé en `.data/` plus tard)
- Schéma manuel (non-typé)

## Notes d'implémentation

```javascript
// Structure :
{
  "version": "1.0",
  "embeddings": [
    {
      "chunkId": "unique-id",
      "vector": [0.123, -0.456, ...],
      "metadata": {
        "source": "file.md",
        "createdAt": "2026-03-02T10:00:00Z"
      }
    }
  ]
}
```

Invalidation du cache : hacher le contenu du chunk, recompute si différent.

## Considérations futures

**Déclencheur de migration :** Lorsque le nombre de chunks >5000 ou latence de recherche >500ms

**Chemin de migration :**
1. Exporter `embeddings.json` vers une base vectorielle
2. Mettre à jour `searchSimilarChunks()` pour utiliser le client de la base
3. Conserver le JSON en backup/fallback

**Alternative :** Si on reste local, migrer vers SQLite + extension vectorielle.

## Références
- Tarification OpenAI embeddings : https://openai.com/pricing
- Comparatif de bases vectorielles : [lien interne]
```

## Quand créer un ADR

Créez un ADR pour des décisions qui :
- Affectent plusieurs composants
- Impliquent des compromis importants
- Peuvent devoir être réexaminées
- Doivent être comprises par les développeurs futurs

**Exemples :**
- Choix de framework ou base de données
- Conception d'API
- Stratégie d'authentification
- Architecture de déploiement
- Sélection de services externes
- Stratégie de persistance des données

**Ne pas ADR :**
- Détails d'implémentation (choix de boucle)
- Choix évidents (JSON pour fichier de config)
- Décisions réversibles sans conséquence
- Préférences personnelles de style
