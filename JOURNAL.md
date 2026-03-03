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

## Session 1.5 (02 Mars 2026) : Mise en place des Skills Copilot

**Objectif** : Configurer des directives personnalisées (Skills) pour encadrer l'IA et garantir le respect des critères de notation du TP2.

**Mise en place des Skills suivants** :
- **`auto-journaling`** : M'aide à capturer systématiquement les moments critiques, les erreurs et les solutions pour remplir les 25 points dédiés au journal de bord.
- **`mvp-rhythm`** : Garde le focus sur un produit minimal viable (MVP). Il m'empêche de m'égarer dans des architectures trop complexes pour une session de 6h (25 points sur la fonctionnalité/compréhension).
- **`qualitative-code`** : Garantit une architecture propre, l'utilisation de patterns comme les ADR (Architecture Decision Records) et le respect des standards (PEP8), assurant les points de qualité du code.
- **`rag-transparency`** : Prépare le questionnaire technique (25 points) en transformant l'IA en tuteur qui m'explique chaque choix LLM (Prompts, température, structured outputs).
- **`robust-rag`** : Force la gestion des cas limites (entrées vides, JSON mal formé, erreurs API) pour éviter les crashs et garantir la robustesse (15 points).

**Apprentissage clé** : 
L'utilisation de "Skills" permet de transformer GitHub Copilot d'un simple générateur de code en un véritable coach méthodologique qui connaît les barèmes de l'examen et me force à rester rigoureux.

## Session 2 (03 Mars 2026)

>IMPORTANT : Tous les prompts sont des "meta-prompts" : Écris par l'IA selon mes instructions.

**Objectif de la session** : Implémentation technique complète du MVP (modèles, moteur d'extraction IA, validation et interface CLI) en suivant une approche modulaire et qualitative.

### Étape 0 : Cadrage technique et définition des prompts d'extraction

**Prompts significatifs** :
```
1. "En tant qu'expert en ingénierie de données IA, analyse le Projet 13 du sujet.md. Explique le problème métier réel, propose un exemple concret d'entrée non-structurée vs sortie JSON, et identifie les points critiques pour un MVP robuste."
2. "Conçois l'architecture de données pour cette application. Détaille les formats d'entrée (Documents sources + JSON Schema de configuration) et structure un format de sortie standardisé incluant obligatoirement des métadonnées de validation et des scores de confiance par champ."
```

**Problème rencontré** : 
Au départ, la vision du projet était centrée sur "extraire du texte". Le risque était de produire un outil qui se contente de reformuler au lieu de structurer véritablement pour une exploitation informatique (base de données, Excel).

**Solution trouvée** :
Définition d'un système à deux entrées strictement séparées : 
1. Le **Document** (donnée brute non structurée).
2. Le **Schéma de configuration** (définition JSON des attentes : types, contraintes, champs obligatoires). 
La sortie a été modifiée pour inclure systématiquement des **métadonnées de validation** (score de confiance, source de l'info, alertes) pour garantir qu'un humain puisse intervenir si l'IA doute.

**Apprentissage clé** : 
L'IA ne doit pas être vue comme un simple lecteur, mais comme un moteur de transformation de type "ETL" (Extract, Transform, Load). La qualité de l'extraction dépend autant de la définition du schéma que du texte d'entrée. Penser à la validation (confiance) dès le début évite le piège des hallucinations silencieuses.

### Étape 1 : Structuration du projet et Environnement
**Objectif** : Créer l'arborescence de fichiers et configurer les dépendances nécessaires.

**Prompt** :
```
Crée la structure de fichiers suivante pour un projet Python "extracteur de données de formulaires" :
src/
  main.py           # Point d'entrée CLI
  extractor.py      # Logique d'extraction IA
  validator.py      # Validation Pydantic
  models.py         # Les modèles Pydantic (schéma + résultat)
schemas/
  exemple_facture.json    # Un schéma exemple
samples/
  exemple_facture.txt     # Un document texte exemple
.env.example
requirements.txt

Pour requirements.txt, inclure : openai, pydantic, python-dotenv
```

**Problème rencontré** : Besoin de s'assurer que les dépendances sont isolées et que les variables d'environnement (OpenAI API Key) sont prévues dès le départ.

**Solution trouvée** : Utilisation d'un fichier `.env.example` pour documenter les secrets et organisation du code dans un dossier `src/` pour séparer la logique des données de test.

**Apprentissage clé** : Une structure claire dès la première minute évite la dette technique et facilite la navigation dans le code lors des phases suivantes.

### Étape 2 : Modélisation des données avec Pydantic
**Objectif** : Définir des modèles de données robustes pour encadrer l'entrée (schéma) et la sortie (résultat d'extraction).

**Prompt** : 
```
Contexte : Je construis un extracteur de données de formulaires en Python.
Exigence : Crée les modèles Pydantic dans models.py.
J'ai besoin de :
1. FieldDefinition : définit un champ attendu...
2. ExtractionSchema : liste de FieldDefinition...
3. FieldResult : résultat d'un champ extrait...
4. ExtractionResult : résultat global...
```

**Problème rencontré** : Aucun.

**Solution trouvée** : Utilisation d'un modèle `FieldResult` qui sépare la `value` (pouvant être `None`) du `status` ("found", "missing", "uncertain") et du score de `confiance`.

**Apprentissage clé** : Pydantic permet de définir des contrats de données stricts qui servent de documentation technique vivante pour le reste de l'application.

### Étape 3 : Création des données de test (Schéma & Sample)
**Objectif** : Générer un cas d'usage concret (facture) pour tester la chaîne d'extraction.

**Prompt** :
```
Crée un fichier schemas/exemple_facture.json qui définit un schéma d'extraction pour une facture commerciale.
Champs attendus : nom_fournisseur, date_facture, montant_total, numero_facture, nom_client.
Crée aussi samples/exemple_facture.txt avec un exemple réaliste de facture en texte brut.
```

**Problème rencontré** : Le texte brut de la facture doit être suffisamment réaliste pour tester la capacité de l'IA à ignorer le bruit (mots-clés, mise en page textuelle).

**Solution trouvée** : Création d'une facture fictive avec des montants clairs mais une structure non-tabulaire complexe.

**Apprentissage clé** : La qualité du document de test est cruciale pour valider les prompts d'extraction par la suite.

### Étape 4 : Le moteur d'extraction IA
**Objectif** : Implémenter la logique de communication avec GPT-4o-mini pour transformer le texte en JSON structuré selon le schéma.

**Prompt** :
```
Contexte : Extracteur de données en Python...
Exigence : Implémente extractor.py avec une fonction extract(document_text: str, schema: ExtractionSchema) -> ExtractionResult.
Architecture :
- Construire un prompt système strict qui interdit à l'IA d'inventer des données manquantes...
- Utiliser l'API OpenAI (gpt-4o-mini) avec response_format JSON...
```

**Problème rencontré** : Aucun, l'IA reconnaît bien les contraintes du prompt et génère un JSON conforme.

**Solution trouvée** : Inclusion d'une instruction impérative dans le prompt système : "Si un champ est absent du document, retourne null. Ne jamais inventer." + Utilisation du `response_format={"type": "json_object"}`.

**Apprentissage clé** : Le contrôle des hallucinations passe par un prompt système sans ambiguïté et un post-traitement rigoureux des scores de confiance.

### Étape 5 : Logique de Validation métier
**Objectif** : Vérifier la cohérence des extractions (champs obligatoires, types de données) et calculer un score de santé global.

**Prompt** :
```
Exigence : Implémente validator.py avec une fonction validate(result: ExtractionResult, schema: ExtractionSchema) -> ExtractionResult.
La validation doit :
1. Vérifier que tous les champs "required=True" sont présents...
2. Vérifier la cohérence des types...
3. Ajouter des alertes...
4. Calculer un statut global...
```

**Problème rencontré** : Le premier jet de validation modifiait les données extraites, ce qui rendait le tracking d'erreur difficile.

**Solution trouvée** : Approche "Read-only" pour la validation : le validateur signale les anomalies via une liste d'alertes sans altérer la valeur brute extraite.

**Apprentissage clé** : Séparer "Extraction" et "Validation" permet de garder une trace fiable de ce que l'IA a réellement produit avant toute décision métier.

### Étape 6 : Interface CLI (Point d'entrée)
**Objectif** : Permettre l'utilisation de l'outil via une ligne de commande simple (`extract` et `validate`).

**Prompt** :
```
Exigence : Crée main.py avec une CLI simple via argparse.
Commandes :
- python main.py extract --document doc.txt --schema schema.json [--output res.json]
- python main.py validate --result res.json --schema schema.json
```

**Problème rencontré** : Aucun

**Solution trouvée** : Implémentation d'un résumé formaté en sortie de console avec mise en évidence des alertes (préfixes [ALERTE] et [SUCCÈS]).

**Apprentissage clé** : Une CLI doit être autant pensée pour les scripts (export JSON) que pour les humains (affichage de résumé).

### Étape 7 : Tests des cas limites et vérification
**Objectif** : Valider la robustesse de l'extracteur face à des entrées dégradées ou inattendues.

**Prompt** :
```
Crée un fichier tests/test_edge_cases.py qui teste les cas limites de l'extracteur.

Tests à écrire (sans appel réel à l'API, utilise unittest.mock) :
1. Document vide → statut "error" ou "warning", pas de crash
2. Tous les champs manquants → chaque champ a statut "missing" et confiance < 0.3
3. JSON malformé retourné par l'IA → géré sans crash
4. Schéma sans champs obligatoires → extraction réussie
5. Valeur de type incorrect (string là où number attendu) → alerte de validation
```

**Problème rencontré** : L'utilisation de mocks pour simuler les réponses de l'API OpenAI est délicate car il faut reproduire fidèlement la structure de l'objet `ChatCompletion`.

**Solution trouvée** : Mise en place d'une suite de tests unitaires utilisant `unittest.mock` pour injecter des réponses JSON variées (valides, corrompues, incomplètes) et vérifier que le système réagit conformément au cahier des charges sans interrompre l'exécution.

**Apprentissage clé** : Tester les "mauvais cas" est aussi important que le "happy path". Cela m'a permis de renforcer la gestion d'erreurs dans `extractor.py` et `validator.py` pour garantir la stabilité du MVP.
