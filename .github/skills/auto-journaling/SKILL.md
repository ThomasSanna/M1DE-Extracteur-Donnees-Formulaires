# SKILL: Auto-Journaling & Process Documentation

## Description
Ce skill garantit les 25 points du **Journal de Développement**. Il aide l'étudiant à capturer les moments critiques d'apprentissage, les erreurs rencontrées et les itérations, conformément au modèle de "Bonne entrée" du sujet.md.

## Directives pour l'Agent

### 1. Détection de Moment "Journalisable"
L'agent doit signaler à l'utilisateur de mettre à jour son `JOURNAL.md` quand :
- Une erreur complexe a été résolue.
- Un choix d'architecture a été modifié (ex: passage de JSON à SQLite).
- Un prompt particulièrement efficace a été trouvé.

### 2. Structure de l'Entrée
Propose toujours une structure prête à copier-coller :
- **Objectif de la session**
- **Le Prompt utilisé** (avec son contexte)
- **Le Problème rencontré**
- **La Solution trouvée**
- **L'Apprentissage clé** (Qu'est-ce que j'ai compris aujourd'hui ?)

### 3. Éviter le "Journal Décoratif"
- Refuse de valider des entrées comme "J'ai fait la fonction X, ça marche".
- Insiste sur le "Pourquoi" et le "Comment".

## Exemples
- **SUPPORT** : "C'était une correction intéressante. N'oublie pas de noter dans ton journal que l'erreur venait du mauvais formatage du JSON retourné par le LLM, et que tu as appris à utiliser Pydantic pour forcer la structure."
