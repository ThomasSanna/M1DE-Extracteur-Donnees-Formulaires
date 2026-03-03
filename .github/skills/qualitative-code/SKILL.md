---
name: qualitative-code
description: 'Développer du code de haute qualité et maintenable avec une justification d''architecture (ADR), une gestion des cas limites et une documentation rigoureuse. Applique la programmation défensive et la validation itérative.'
argument-hint: 'Fonctionnalité ou composant à implémenter avec un focus sur la qualité et l''architecture'
---
# Qualitative Code Development

Flux de travail structuré pour produire un code maintenable, bien documenté et compréhensible.

## Principes Fondamentaux

1. **Comprendre avant de générer** — Ne jamais accepter de code inexplicable.
2. **Architecture avant vitesse** — Justifier chaque décision technique via un ADR.
3. **Défensif par défaut** — Gérer les cas limites de manière proactive.
4. **Documenter le parcours** — Tracer les itérations et les apprentissages.
5. **Standard de nommage** — Respecter les conventions du langage cible (ex: PEP8 pour Python).

## Quand l'utiliser

- Implémentation de nouvelles fonctionnalités ou composants.
- Refactorisation du code existant pour la qualité.
- Code devant être évalué ou maintenu.
- Justification de choix structurants.
- Construction de MVPs robustes.

## Phase de Pré-implémentation

### 1. Clarifier le Problème
Avant d'écrire du code, répondez à :
- **Quel** problème est résolu ? (en langage clair)
- **Qui** l'utilisera et comment ?
- **Pourquoi** la solution actuelle est insuffisante ?
- **Quels** sont les critères de succès ?

### 2. Décisions de Design (ADR)
Utilisez le dossier `references/` pour documenter vos choix :

**Architecture**
- Quel patron convient le mieux ? (MVC, en couches, hexagonal...)
- Pourquoi ce patron plutôt qu'un autre ?
- Quels sont les compromis ?

**Choix technologiques**
- Quelles bibliothèques / frameworks ?
- Pourquoi ces outils spécifiques ?
- Quelles dépendances sont essentielles vs optionnelles ?

**Modèle de données**
- Quelles entités existent ?
- Comment s'articulent-elles ?
- Où l'état est-il stocké et persisté ?

**Limites de périmètre**
- Qu'est-ce que je n'implémenterai PAS ? (exclusions explicites)
- Qu'est-ce qui peut être différé en v2 ?
- Quel est le minimum viable à livrer ?

### 3. Inventaire des cas limites
Listez les modes de défaillance potentiels AVANT de coder :
- Entrées vides, valeurs nulles, indéfinies
- Pannes réseau, délais d'API (timeouts)
- Erreurs système de fichiers (permissions, disque plein)
- Entrée utilisateur invalide, incompatibilités de type
- Accès concurrent, conditions de course
- Épuisement des ressources (mémoire, connexions)

## Implementation Phase

### 4. Rédiger avec contexte
Lors de la rédaction d'instructions pour l'IA, incluez :
```
Contexte: [Bref résumé d'architecture]
Exigence: [Fonctionnalité spécifique]
Contraintes: [Limitations techniques]
Cas limites à gérer: [Depuis l'inventaire]
Nommage: camelCase pour variables/fonctions
Critères de qualité:
- Gestion défensive des erreurs
- Validation des entrées
- Noms de variables explicites
- Fonctions modulaires (responsabilité unique)
```

### 5. Code Review Checklist
After generation, validate EVERY piece:

**Naming & Style**
- [ ] camelCase for variables, functions, methods
- [ ] PascalCase for classes, types, interfaces
- [ ] Descriptive names (no `x`, `temp`, `data`)
- [ ] Consistent formatting and indentation

**Architecture**
- [ ] Single Responsibility Principle (each function does ONE thing)
- [ ] No God objects or monolithic functions
- [ ] Clear separation of concerns
- [ ] Dependencies are injected, not hardcoded

**Error Handling**
- [ ] All external calls wrapped in try-catch
- [ ] Meaningful error messages
- [ ] Graceful degradation (don't just crash)
- [ ] Errors logged with context

**Input Validation**
- [ ] Type checking for all inputs
- [ ] Range/boundary validation
- [ ] Null/undefined checks
- [ ] Sanitization for user input

**Edge Cases**
- [ ] Each identified edge case has a code path
- [ ] Empty arrays/objects handled
- [ ] Default values for optional parameters

**Maintainability**
- [ ] Complex logic has explanatory comments
- [ ] Magic numbers replaced with named constants
- [ ] Functions are testable (pure where possible)
- [ ] No deep nesting (max 3 levels)

### 6. Iterative Refinement
When code quality issues found:

1. **Identify the smell** — What specific problem?
2. **Understand the root cause** — Why was it generated this way?
3. **Propose refactor** — How should it be structured?
4. **Document the learning** — Note in journal for future prompts

**Exemple de pattern d'itération :**
```
Problème : La fonction générée a 5 paramètres (trop)
Cause : Tentative de tout configurer en une seule fois
Solution : Extraire un objet de configuration
Apprentissage : Commencer les prompts par "utiliser un objet de config pour >3 params"
```

## Post-Implementation Phase

### 7. Exigences de documentation
Créer la documentation en parallèle du code :

**README.md** (pour les utilisateurs)
- Étapes d'installation (testées sur un environnement propre)
- Exemples d'utilisation (copier-coller)
- Options de configuration
- Erreurs courantes et solutions

**Architecture Decision Record** (pour les mainteneurs)
- Quoi : Diagramme de la structure des composants
- Pourquoi : Justification de chaque décision majeure
- Compromis : Ce qui a été sacrifié et pourquoi
- Alternatives : Ce qui a été considéré et rejeté

**Commentaires de code** (pour les développeurs)
- Expliquer le POURQUOI, pas le QUOI
- Algorithmes complexes expliqués
- Cas limites non évidents documentés
- TODO avec contexte, pas juste "fix this"

### 8. Testing Strategy
Define verification approach:

**Manual Testing**
- Happy path: Normal usage flow
- Edge cases: Each item from inventory
- Boundary conditions: Min/max values
- Error scenarios: Force failures

**Smoke Tests**
- Does it start without errors?
- Can it perform core function?
- Does it handle invalid input gracefully?
- Does it clean up resources?

### 9. Modèle d'entrée de journal
Documenter chaque session de développement :

```markdown
## Session [N] — [Date]

**Objectif :** [Ce que je voulais accomplir]

**Prompt(s) :**
- "[Prompt exact avec contexte]"
- Résultat : [Ce qui a été généré]
- Qualité : [Évaluation initiale]

**Problèmes rencontrés :**
1. [Problème spécifique]
   - Symptôme : [Comment il s'est manifesté]
   - Cause racine : [Pourquoi c'est arrivé]
   - Solution : [Comment je l'ai corrigé]
   - Itération : [Prompt affiné ou correction manuelle]

**Décisions d'architecture :**
- [Décision] : [Justification]
- Compromis : [Ce qui a été sacrifié]

**Cas limites traités :**
- [Cas] : [Comment il est géré dans le code]

**Ce que j'ai appris :**
- [Insight sur le domaine]
- [Pattern efficace]
- [Erreur à éviter la prochaine fois]

**Prochaines étapes :**
- [ ] [Tâche actionnable]
```

## Quality Gates

Before considering anything "done", ensure:

**Functional**
✓ Runs without errors in target environment
✓ Core functionality works end-to-end
✓ All identified edge cases handled
✓ Degrades gracefully on errors

**Understandable**
✓ You can explain every architectural choice
✓ You can describe what each function does
✓ You know which parts are fragile and why
✓ You've documented non-obvious decisions

**Maintainable**
✓ Someone else could read and modify it
✓ Naming is self-explanatory
✓ Functions are small and focused
✓ Dependencies are minimal and justified

**Documented**
✓ README with installation + usage
✓ Architecture decisions recorded
✓ Journal entries complete for all sessions
✓ Code comments explain WHY

## Common Pitfalls to Avoid

**"It works, ship it"**
- Anti-pattern: Accepting first generation that compiles
- Fix: Always complete the review checklist

**"I'll document later"**
- Anti-pattern: Postponing journal entries
- Fix: Write session notes immediately while context is fresh

**"The AI knows best"**
- Anti-pattern: Blindly trusting generated architecture
- Fix: Question every design decision, demand justification

**"Comments are for weak code"**
- Anti-pattern: No comments because "clean code is self-documenting"
- Fix: Explain WHY and context, especially for edge cases

**"Perfect is the enemy of good"**
- Anti-pattern: Over-engineering simple features
- Fix: Reference scope boundaries, implement MVP first

## Example Workflow

**Task:** Implement semantic search feature

```markdown
1. PROBLEM CLARIFICATION
   - What: Search my document chunks by meaning, not keywords
   - Who: Me, for personal knowledge base
   - Why: Keyword search misses related concepts
   - Success: Find relevant chunks for natural language queries

2. DESIGN DECISIONS
   - Architecture: Embedding-based similarity search
     Why: Captures semantic meaning
     Trade-off: More complex than keyword search, needs API
   
   - Stack: OpenAI text-embedding-3-small
     Why: Good quality/cost ratio, simple API
     Alternative: Local models (rejected: setup complexity for MVP)
   
   - Storage: JSON file for embeddings
     Why: Simple persistence, readable
     Trade-off: Not scalable, okay for MVP
     Future: Migrate to vector DB if >10k chunks

3. EDGE CASES
   - Empty query → return error message
   - API timeout → retry once, then fail gracefully
   - No embeddings file → create on first run
   - Chunk deleted → filter out missing embeddings

4. PROMPT
   "Implement semantic search for text chunks using OpenAI embeddings.
   
   Requirements:
   - Use text-embedding-3-small model
   - Store embeddings in embeddings.json (persist between runs)
   - Function: searchSimilarChunks(query, topK=5)
   - Return: Array of {chunk, similarity}
   
   Error handling:
   - Validate query is non-empty string
   - Handle API timeout with single retry
   - Create embeddings file if missing
   - Filter out chunks that no longer exist
   
   Naming: camelCase
   Make it modular for future vector DB migration."

5. REVIEW
   [Apply checklist from section 5]
   Issue found: Embeddings recalculated every run
   Iteration: Add cache check before API call

6. DOCUMENT
   - Added to README: "Search requires OPENAI_API_KEY env var"
   - ADR: Why JSON over vector DB for MVP
   - Journal: Noted API timeout handling iteration

7. TEST
   - Normal query: ✓
   - Empty string: ✓ Error shown
   - API key missing: ✓ Clear error
   - Malformed embeddings.json: ✓ Recreates file
```

## Success Metrics

You've succeeded when:
1. You can explain your code to a peer without looking at it
2. Your journal shows clear problem→solution evolution
3. Edge cases are handled, not just happy path
4. Someone could fork your project and understand it
5. You made deliberate architectural choices, not just "what AI gave me"

## Related Tools

- [Code review templates](./references/review-templates.md)
- [Architecture decision records](./references/adr-template.md)
- [Prompt refinement guide](./references/prompt-patterns.md)
 - [Code review templates](./references/review-templates.md)
 - [Architecture decision records](./references/adr-template.md)
 - [Guide d'affinage des prompts](./references/prompt-patterns.md)

---

**Remember:** Quality code isn't about perfection. It's about understanding, maintainability, and defensiveness. If you can't explain it, refactor it.
