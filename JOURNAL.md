# Journal de Développement — TP2 IA

## Session 1 (02 Mars 2026)

### Initialisation du workflow de développement selon le sujet.md

**Objectif** : Mise en place de l'environnement de travail et automatisation de la qualité.

## (Livrable 1) Cadrage du Projet 13 : Extracteur de données de formulaires

### Le problème qui va être résolu
Le projet vise à automatiser le traitement de formulaires hétérogènes (PDF, images, emails) qui arrivent souvent de manière désordonnée dans les entreprises. Au lieu d'une saisie manuelle fastidieuse et sujette aux erreurs, je construis un système capable d'extraire, de façon intelligente, des données spécifiques comme des champs textuels, dates ou montants selon un schéma prédéfini, le tout, en évaluant la fiabilité de l'extraction avec un score de confiance, par exemple, pour permettre une validation humaine ciblée.

### Choix techniques justifiés

Le langage principal sera, évidemment, Python en raison de son écosystème riche en bib d'IA et manipulation de documents.

Pour l'extration des informations, l'utilisation de plusieurs modèles plus ou moins coûteux d'OpenAI ou Gemini ou Deepseek (probablement ce qui va être utilisé pour le projet) via l'API en utilisant le format de sortie structuré en JSON. L'utilisation de plusieurs modèles permettra peut-être de faire du "fallback" en cas d'échec d'un modèle plus rapide mais moins précis, ou alors reconnaître si un document est trop complexe pour le modèle "mini" et basculer automatiquement vers une version plus puissante.

Pour la validation des données extraites, Pydantic est un choix naturel pour sa capacité à définir des schémas de données robustes et à fournir une validation automatique, ce qui renforcera la fiabilité du système dès le MVP.

Pour le moment, je me concentrerai probablement sur une interface CLI, on verra. L'objectif étant de se concentrer sur la logique d'extraction etc. Plutôt que de perdre du temps sur l'interface utilisateur.

Cependant, si nous partons, plus tard, sur une interface web, FastAPI côté backend serait un excellent choix pour sa simplicité et sa rapidité de développement, ainsi que pour son intégration facile avec les modèles d'IA. Côté frontend, React serait un choix solide pour construire une interface utilisateur réactive et moderne.

### Scope négatif
- Pas de déploiement Cloud complexe (AWS/Azure).
- Probablement pas d'utilisation d'IA locale type LLama pour simplifier la stack.
- Pas de support pour les formulaires manuscrits extrêmement dégradés (OCR de base uniquement).

### Difficultés anticipées
- **Variabilité des formats** : Gérer la différence de structure entre un PDF natif et un scan de mauvaise qualité.
- **Hallucinations de l'IA** : S'assurer que l'IA ne "devine" pas des informations manquantes (contrainte : champ absent = null).
- **Scores de confiance** : Définir une méthode fiable pour que l'IA exprime son incertitude.

### Adresse GitHub du projet
[https://github.com/ThomasSanna/M1DE-Extracteur-Donnees-Formulaires](https://github.com/ThomasSanna/M1DE-Extracteur-Donnees-Formulaires)