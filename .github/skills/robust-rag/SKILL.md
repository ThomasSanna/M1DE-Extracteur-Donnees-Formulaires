# SKILL: Robust AI & Edge Case Management

## Description
Ce skill assure que le projet ne crashe pas sur des entrées invalides (10 points de Qualité + 5 points Cas Limites). Il force une approche de programmation défensive spécifique aux applications d'IA.

## Directives pour l'Agent

### 1. Programmation Défensive
- Injecte systématiquement des blocs `try/except` autour des appels API externes (OpenAI, Anthropic).
- Vérifie la présence des clés d'API au démarrage du projet.
- Valide systématiquement les types et la longueur des inputs utilisateurs.

### 2. Cas Limites IA
Pour chaque fonctionnalité, gère explicitement :
- **Input vide** ou trop long (Token limit).
- **Réponse LLM imprévisible** (JSON mal formé).
- **Documentation/RAG vide** (Le système doit dire "Je ne sais pas" proprement).
- **Frustration utilisateur** (Déclenchement d'escalade ou message de secours).

### 3. Logs de Secours
- Suggère toujours un système de logs simple pour tracer les erreurs sans faire planter l'interface.

## Exemples
- **MAUVAIS** : `response = client.chat.completions.create(...)`
- **BON** : `try: response = client.chat.completions.create(...) except Exception as e: logger.error(f"API Error: {e}"); return "Désolé, le service est temporairement indisponible."`
