# SKILL: MVP Rhythm & Scope Control

## Description
Ce skill garantit que le projet reste un **Minimum Viable Product (MVP)** réalisable en 6 heures. Il empêche la sur-ingénierie et privilégie la clarté technique sur la complexité des fonctionnalités, conformément au barème (25 points sur la fonctionnalité mais 25 points sur la compréhension).

## Directives pour l'Agent

### 1. Filtrage du Scope
- **Règle d'or** : Si une fonctionnalité prend plus de 45 minutes à implémenter ou à expliquer, propose une alternative plus simple.
- **Architecture** : Privilégie les solutions "Single File" ou monolithiques simples (ex: FastAPI, SQLite, scripts Python) plutôt que des micro-services ou des infrastructures complexes (Docker, Redis, etc.) sauf si explicitement demandé.
- **Priorisation** : Toujours suggérer d'implémenter le "Happy Path" (cas nominal) d'abord, puis les cas limites.

### 2. Validation du Temps
- Avant de proposer un changement majeur, estime le temps d'implémentation restant sur les 6 heures recommandées.
- Divise les tâches complexes en sous-tâches de maximum 15 minutes de code.

### 3. Justification du MVP
- Chaque choix technique doit être accompagné d'une justification courte : "Choisi pour sa simplicité d'explication lors du questionnaire technique".

## Exemples
- **MAUVAIS** : "Ajoutons une base de données PostgreSQL avec des migrations Alembic et un cache Redis."
- **BON** : "Utilisons SQLite pour la persistance car c'est un simple fichier facile à manipuler et à expliquer sans configuration externe."
