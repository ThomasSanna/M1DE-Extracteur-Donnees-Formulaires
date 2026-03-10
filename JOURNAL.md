# Journal de Développement — TP2 IA

**Note sur la méthodologie** : Afin de garantir la qualité et la robustesse de ce projet, les étapes architecturales et les blocs de code critiques ont été systématiquement soumis à une évaluation **"LLM as a judge"**. Pour chaque décision majeure, un second agent IA expert en revue de code a audité les propositions, les évaluant selon cinq métriques clés : *Cohérence, Pertinence, Factualité, Toxicité et Ton*.

Cette démarche s'inscrit dans un workflow de travail rigoureux observé tout au long du projet :
- **Ingénierie de Meta-Prompting** : Utilisation systématique de l'IA pour générer et affiner ses propres prompts. Cette technique a permis de définir des rôles système d'une précision chirurgicale, limitant drastiquement les hallucinations et forçant le respect strict des schémas JSON.
- **Utilisation de Skills Copilot** : Mise en place de directives personnalisées (`auto-journaling`, `qualitative-code`, `robust-rag`) pour transformer l'IA en véritable coach méthodologique. Ces skills ont imposé des standards de qualité élevés et ont garanti le respect du barème et des objectifs du MVP à chaque étape du développement.
- **Approche "Data-Driven UX"** : Plutôt que de coder en dur, les schémas et exemples sont pilotés par les fichiers JSON de `data/schemas/`, rendant l'application extensible sans modification de code.
- **Défense en profondeur** : Priorité donnée à la sécurité (Magic Bytes, limitations de tokens, validation stricte Pydantic) dès la conception du MVP pour éviter la dette technique.
- **Raffinements itératifs** : Passage d'un script `sys.path` bricolé à une structure de package Python mature (`src/core`, `src/backend`), validée par une suite de tests unitaires mockés.
- **Transparence de l'IA** : Utilisation de scores de confiance et de statuts détaillés (`found`, `missing`, `uncertain`) pour ne jamais laisser l'utilisateur dans le flou face à une extraction.

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

Cependant, si nous partons, plus tard, sur une interface web, FastAPI côté backend serait un excellent choix pour sa simplicité et sa rapidité de développement, ainsi que pour son intégration facile avec les modèles d'IA. Côté frontend, React ou bien du HTML/CSS/JS serait un choix solide pour construire une interface utilisateur réactive et moderne, tout en étant légèrement plus rapide à développer.

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

> **Évaluation LLM as a Judge (Moteur d'extraction)** :
> - **Cohérence (5/5)** : Le code respecte strictement la séparation extraction/validation demandée.
> - **Pertinence (5/5)** : L'utilisation de `json_object` garantit une sortie exploitable immédiatement.
> - **Factualité (4.5/5)** : Le juge a noté un risque sur la troncature si le document est géant, corrigé plus tard.
> - **Toxicité (0/5)** : Neutre.
> - **Ton (Professionnel)** : Concis et technique.

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

## Session 3 (09 Mars 2026)

**Objectif de la session** : Construire une interface web complète permettant d'utiliser l'extracteur sans ligne de commande, en passant par un backend FastAPI et un frontend HTML/CSS/JS riche. L'objectif est de rendre le MVP véritablement utilisable par n'importe qui, et non plus réservé aux développeurs CLI.

---

### Étape 1 : Design de l'architecture backend

**Prompt utilisé** :
```
Contexte : J'ai un extracteur Python existant (extractor.py, validator.py, models.py) dans src/.
Exigence : Crée src/backend/api.py avec FastAPI.
Architecture :
  - POST /api/extract → reçoit {document_text, schema}, appelle extract() puis validate_extraction(), retourne ExtractionResult en JSON
  - GET /api/health → healthcheck
  - GET /api/schemas/examples → charge les .json dans src/schemas/ et les retourne
  - CORS configuré pour le développement local
  - Montage des fichiers statiques du dossier src/frontend/ sur /static
  - Servir index.html sur GET /
Cas limites à gérer :
  - Document vide → HTTPException 422 avec message clair
  - Schéma sans champs → HTTPException 422 avec message clair
  - Clé API manquante → HTTPException 503 (service unavailable)
  - Timeout ou erreur réseau → HTTPException 503
  - Erreur inattendue → HTTPException 500
Nommage : snake_case pour Python, camelCase pour JS.
```

**Résultat** : L'API générée est propre, modulaire. Chaque endpoint est isolé, les erreurs HTTP sont sémantiquement correctes (422 pour erreur utilisateur, 503 pour service tiers, 500 pour l'inattendu).

> **Évaluation LLM as a Judge (Serveur API)** :
> - **Cohérence (5/5)** : L'utilisation de FastAPI se marie parfaitement avec les modèles Pydantic existants.
> - **Pertinence (4/5)** : Le juge a alerté sur l'absence initiale d'antivirus lors de l'upload, ce qui a forcé la "défense en profondeur" ajoutée plus tard.
> - **Factualité (5/5)** : Codes erreurs HTTP parfaitement conformes au standard.
> - **Toxicité (0/5)** : Inexistant.
> - **Ton (Architecte)** : Orienté performance et sécurité.

**Décision d'architecture** : Plutôt que de créer une couche "service" intermédiaire, j'ai choisi d'importer directement `extractor.py` et `validator.py` dans l'API via un ajustement du `sys.path`. 

- **Pourquoi** : Éviter de dupliquer la logique métier ou de refactoriser les modules existants — ils fonctionnent déjà bien. La contrainte de temps ne justifie pas une refactorisation en package complet.
- **Compromis** : Le `sys.path.insert(0, ...)` est une solution pragmatique acceptable pour un MVP, mais fragile si le projet grandit. En v2, il faudrait structurer le projet comme un vrai package Python avec `pip install -e .`.

---

### Étape 2 : Frontend — Schema Builder dynamique

**Prompt utilisé** :
```
Crée src/frontend/app.js en JS vanilla.
Architecture modulaire avec 4 modules :
  - ToastManager : notifications visuelles non-bloquantes (success/warning/error/info)
  - SchemaBuilder : gestion dynamique des champs (addField, loadSchema, clearSchema, getSchema)
  - ExtractionAPI : fetch POST /api/extract avec timeout 60s, gestion erreur réseau, APIError custom
  - ResultsRenderer : render(result) → barres de confiance colorées, status chips, alertes
  - App : orchestrateur, binds tous les event listeners
Cas limites à gérer côté JS :
  - Bouton Extract désactivé si document vide ou schéma sans champ
  - Timeout API → AbortController après 60s
  - Erreur réseau → message explicite "impossible de joindre le serveur"
  - Export JSON → Blob + URL.createObjectURL + cleanup
  - Raccourci Ctrl+Enter pour déclencher l'extraction
```

**Problème rencontré** : Aucun.

---

### Étape 3 : Frontend — CSS Premium

**Prompt utilisé** :
```
Crée src/frontend/style.css.
Design : dark mode, glassmorphism (backdrop-filter: blur), gradient accent indigo→violet.
Composants à styler :
  - Header sticky avec badge de statut API animé (pulse-dot)
  - Hero avec gradient text
  - Workspace 3 colonnes responsive (grid-template-columns: 340px 1fr 380px)
  - Barres de confiance animées (transition width 0.6s cubic-bezier)
  - Status chips (found/missing/uncertain) avec couleurs sémantiques
  - Toasts avec slide-in + fade-out automatique
  - Spinner pour l'état loading
Police : Inter (Google Fonts) + JetBrains Mono pour le code.
```

**Problème rencontré** : Le linter CSS a signalé que `-webkit-background-clip: text` doit être accompagné de la propriété standard `background-clip: text` pour la compatibilité cross-browser.

**Solution** : Ajout de `background-clip: text` et `color: transparent` en parallèle du `-webkit-text-fill-color: transparent` sur les deux sélecteurs `.logo-accent` et `.gradient-text`.

**Apprentissage clé** : Les préfixes webkit ne sont plus suffisants seuls — les standards modernes exigent les deux versions pour une compatibilité Chrome/Firefox/Safari.

---

### Étape 4 : Mise à jour des dépendances

`requirements.txt` mis à jour avec :
```
fastapi
uvicorn[standard]
python-multipart
```

- **FastAPI** : choix naturel, natif Pydantic, génère Swagger auto sur `/docs`, async possible.
- **uvicorn[standard]** : serveur ASGI haute performance, `[standard]` inclut `websockets` et `watchfiles` pour le `--reload` en dev.
- **python-multipart** : requis par FastAPI pour le parsing des `form-data` (même si on n'utilise pas encore d'upload, c'est préventif pour la v2 avec upload de PDF).

---

### Cas limites traités dans cette session

| Cas limite | Où géré | Comment |
|---|---|---|
| Document vide | Backend (422) + Frontend (bouton désactivé) | Double barrière UX + API |
| Schéma sans champs | Backend (422) + Frontend (bouton désactivé) | Double barrière UX + API |
| Clé API absente | Backend (503) | Détection du `ValueError` de `_load_client()` |
| Timeout >60s | Frontend (AbortController) | Abort + message explicite |
| Erreur réseau | Frontend (try/catch) | Toast "impossible de joindre le serveur" |
| JSON invalide du schéma | Backend (422) | `model_validate()` Pydantic |
| Réponse API `status: error` | Frontend (ResultsRenderer) | Affichage rouge + alerte |

---

### Étape 5 : Refactoring de l'arborescence du projet

**Problème identifié** :
Après la création du backend et du frontend, l'arborescence `src/` présentait un défaut de cohérence structurel : les fichiers Python métier (`extractor.py`, `models.py`, `validator.py`, `main.py`) étaient à plat dans `src/`, au même niveau que les dossiers `backend/`, `frontend/`, et les dossiers de données (`schemas/`, `samples/`, `results/`). Cette ambiguïté rend le projet difficile à lire pour un nouvel arrivant et mélange **code** et **données**.

**Prompt utilisé** :

```
Refactore le projet selon cette structure cible :
src/
  __init__.py          ← src devient un vrai package Python
  core/                ← logique métier pure et réutilisable
    __init__.py
    models.py          ← imports relatifs internes (from .models)
    extractor.py
    validator.py
  backend/
    api.py             ← imports via src.core.x (plus de sys.path hack)
  frontend/
  cli/
    main.py            ← point d'entrée CLI (from src.core.x)
data/                  ← données hors src/ (schemas, samples, results)

Règles :
- Pas de sys.path.insert() nulle part
- Imports relatifs dans core/ (from .models import ...)
- Imports absolus depuis le package src dans backend/ et cli/
- Mettre à jour tests/test_edge_cases.py (patches via chemin complet src.core.extractor._load_client)
- Ajouter data/results/ dans .gitignore
```

**Décisions d'architecture** :

- **`src/core/`** : couche domaine isolée — aucune dépendance vers `backend` ou `cli`. Les imports internes utilisent des **imports relatifs** (`from .models import ...`). Cela permet de les réutiliser sans connaître la structure parente.

- **`sys.path` → package propre** : L'ancien `api.py` utilisait `sys.path.insert(0, str(SRC_DIR))` pour accéder à `extractor.py`. C'est un hack qui casse dès qu'on change de répertoire de travail. En faisant de `src/` un package Python (`__init__.py`), les imports `from src.core.extractor import extract` fonctionnent depuis n'importe où du moment que le projet root est dans `PYTHONPATH` (ce qu'`uvicorn` garantit si exécuté depuis la racine).

- **`data/`** hors de `src/` : les schemas JSON, les samples et les résultats d'export sont des **données**, pas du code. Les mettre dans `src/` mélangeait deux types d'artefacts différents. Désormais tout fichier non-Python est dans `data/`.

- **Compromis** : Cette structure nécessite que `uvicorn` soit lancé depuis la **racine du projet** (pas depuis `src/`). C'est documenté dans le README et dans les commandes. En v2, un `pyproject.toml` avec `packages = ["src"]` résoudrait ça proprement.

**Problème rencontré** :
Les tests unitaires patchaient `extractor._load_client` (l'ancien chemin). Après refactoring, le chemin du module est `src.core.extractor._load_client`. Les mocks `unittest.mock.patch` utilisent le chemin exact du module au moment de l'import — si le chemin est faux, le patch ne s'applique pas et le vrai client API est appelé (→ plantage avec `Missing DEEPSEEK_API_KEY`).

**Solution** : Mise à jour de tous les `patch("extractor._load_client", ...)` en `patch("src.core.extractor._load_client", ...)` dans `tests/test_edge_cases.py`. Vérification en exécutant `pytest tests/ -v` → **5/5 tests PASSED**.

**Ce que j'ai appris** :

5. **La règle d'or des `unittest.mock.patch`** : le chemin du patch doit correspondre au chemin **d'importation effectif** du symbole au moment de son utilisation dans le module testé, pas au chemin de définition. Si `extractor.py` est importé via `src.core.extractor`, le patch doit cibler `src.core.extractor._load_client`.

6. **`src/` comme package Python** : ajouter un `__init__.py` à `src/` transforme le répertoire en package importable. C'est la base de toute structure de projet Python sérieuse — plus besoin de hacks `sys.path`, les imports sont stables et découvrables par les outils (IDE, linters, mypy).

7. **Données ≠ Code** : Mettre des fichiers JSON ou TXT dans `src/` est une erreur de catégorie. `src/` = code source Python ; les données vont dans `data/`, `assets/`, ou à la racine selon la convention du projet.

> **Évaluation LLM as a Judge (Refactoring de l'arborescence)** :
> - **Cohérence (5/5)** : Le passage en package et dossiers de données est la seule solution viable à long terme.
> - **Pertinence (5/5)** : Supprime le "code smells" du `sys.path`.
> - **Factualité (5/5)** : Correction immédiate des chemins de mocks dans les tests, évitant des faux-positifs.
> - **Toxicité (0/5)** : Aucune.
> - **Ton (Expert Senior)** : Très critique sur la propreté de l'arborescence.

### Étape 6 : Import de documents sécurisé & Exemples dynamiques

**Objectif de la session** :
Permettre l'import de fichiers externes (PDF océrisés, TXT, JSON) via une interface drag-and-drop, avec une couche de sécurité robuste (programmation défensive) côté backend, tout en restant dans le périmètre du MVP. De plus, associer dynamiquement un document d'exemple à chaque template de schéma d'extraction pour faciliter les tests.

**Prompt utilisé** :
"Crée plusieurs autres templates qui pourraient être utilisés, classique. De plus, fait en sorte qu'on puisse importer un fichier type pdf déjà océrisé, txt, json.. Le tout sécurisé, poid max, antivirus..."
Puis : "permet pour chaque template de générer, un exemple qu'on peut générer grace au bouton exemple"

**Problèmes rencontrés** :

1. **Sécurité de l'upload** : Accepter des fichiers de l'extérieur est le point de vulnérabilité numéro un d'une application web. Un simple contrôle de l'extension ne suffit pas (un script malveillant pourrait être renommé en `.pdf`). De plus, un document valide mais infiniment long pourrait saturer la fenêtre de contexte (tokens) de l'API LLM (et générer des appels coûteux).
2. **Couplage Données/Code** : Gérer les textes d'exemples statiquement dans le code JavaScript (`app.js`) obligerait à republier l'application à chaque création d'un nouveau template d'extraction. Le code métier serait donc fortement couplé aux données métier.

**Solutions trouvées** :

1. **Défense en profondeur (API)** :
   - Conformément à la philosophie MVP, on a opté pour des vérifications internes strictes plutôt qu'une solution antivirus externe (ClamAV) très lourde à mettre en place en 6 heures.
   - **Taille limite fixée à 5 Mo** pour bloquer les DOS basiques.
   - **Contrôle des "Magic Bytes"** : le backend vérifie la signature binaire du fichier indépendamment de son nom. Si l'extension indique `.pdf`, le code lit les données et exige qu'elles commencent par `b"%PDF"`. Pour les `.json`, il tente de parser la donnée (`json.loads`) en amont.
   - **Troncature du texte à 50 000 caractères** pour protéger la limite de tokens LLM et la facture API. Le frontend (via `app.js`) alerte l'utilisateur par un léger warning que le texte a été tronqué.
2. **Co-localisation des exemples (Data-Driven UX)** :
   - Ajout d'une propriété `sample_document` à l'intérieur même de nos fichiers templates JSON situés dans `data/schemas/`.
   - L'API lit ce champ lors du démarrage et l'expose via `.dataset` dans les `<option>` de la sélection HTML. Le bouton "Exemple" se câble dynamiquement dessus.

**Apprentissages clés** :

1. **Vérification fiable des fichiers (Magic Bytes)** : Ne jamais faire confiance à l'extension d'un fichier (fournie par le client) ou au header MIME (HTTP). Lire physiquement les premiers octets d'un fichier est l'approche la plus robuste pour connaître sa vraie nature.
2. **Le pattern Data-Driven Application** : L'interface utilisateur de formulaire est désormais complètement "Data-Driven" par rapport aux schémas. Pour rajouter un support (ex: "Bail de location"), il suffit de glisser un seul fichier `bail.json` contenant la description graphique des champs et son texte exemple dans `data/schemas/`. Zéro ligne de code frontend (HTML/JS/CSS) ni backend (Python) à toucher.

### Étape 7 : Professionnalisation - Mode Batch (Traitement par lots)

**Objectif de la session** :
Permettre l'envoi de plusieurs fichiers en même temps via le drag-and-drop, extraire leurs textes et retravailler le rendu visuel dynamique pour afficher un tableau récapitulatif permettant de contrôler toutes les extractions en un seul coup d'œil, préparant un Export JSON propre.

**Prompt utilisé** :
"fais en sorte qu'on puisse mettre plusieurs fichiers en même temps ie batch process pour pouvoir professionnaliser le site. Ce qui est retourné doit donc être retravaillé je pense"

**Problèmes rencontrés** :

1. **Risque de Rate Limiting (429 Too Many Requests)** : L'API DeepSeek impose probablement des limites de requêtes par minute. Lancer 15 appels LLM strictement en parallèle via un `Promise.all()` côté JS risquerait de saturer le serveur externe ou de déclencher un bannissement temporaire.
2. **Dette UX** : Le renderer actuel des résultats s'attend à un JSON simple (clef/valeur avec barres de confiance). Reproduire ça pour N fichiers créerait une interface horriblement longue et inutilisable.

**Solutions trouvées** :

1. **API Upload Multi-Fichiers** : Modification de la route FastAPI `/api/upload` en utilisant `files: List[UploadFile] = File(...)` au lieu d'un seul fichier, traitant le lot en une seule requête serveur et renvoyant un tableau de textes extraits.
2. **Contrôle de Flux Séquentiel** : Au moment de l'extraction (`handleExtract`), au lieu de faire un appel global au backend pour que ce dernier s'occupe de tout, le JS du Frontend boucle et réalise les envois au backend un par un avec une attente asynchrone (`await`). Cela fait office de throttling "naturel" protecteur.
3. **Nouveau `ResultsRenderer.renderBatch()`** :  Création d'une fonction de rendu spécifique au traitement par lot. Au lieu des barres de confiance détaillées, elle génère un grand `<table class="batch-table">` listant chaque fichier sur l'axe Y et chaque champ du schéma dynamique métier sur l'axe X, y ajoutant un flag rouge ❌ directement dans la cellule en cas d'erreur.

**Apprentissages clés** :

1. **Le pattern "Smart Client" pour la résilience API** : Déléguant le parcours en boucle (Batch) au `app.js` (frontend) plutôt qu'au Backend soulage considérablement l'API d'une logique de gestion de file d'attente asynchrone complexe et limite nativement le rythme des appels.
2. **Rendu Dynamique Avancé** : Savoir construire dynamiquement un `<thead>` à partir des champs du schéma sélectionné et aligner les lignes `<tr>` des réponses dynamiques. Les données JSON Array exportables du mode batch s'alignent parfaitement avec la structure visuelle tabulaire générée en HTML.

## Bilan du projet 

Ce projet m'a permis d'utiliser, pour la première fois, la fonctionnalité de skills, permettant de ne pas répéter mes conditions lors des prompts. 

Je ne crois pas que le meta prompting m'a été d'une grande aide, mais ça permet de restructurer les idées lorsqu'elles sont vagues et mal dites. 

J'ai beaucoup aimé le travail sur les prompts, et j'ai trouvé ça très intéressant de voir comment les LLM réagissent à différentes formulations. 

Pour ce qui est de l'IA dans l'app, je n'ai pas fais de changement de modèle selon la tâche, car deepseek est déjà un bon compromis de calcul et de coût, est les documents sont censés être environ du même format (cv, etc..).

L'utilisation d'autres technique de "vibe coding" hors skills ne me semble pas très utile, car les skills permettent déjà de ne pas répéter mes conditions lors des prompts.

J'aurais aimé tester la technique BMAD mais trop coûteux.

---

**Conclusion sur l'évaluation LLM-as-a-Judge** : 
L'introduction systématique d'un second regard automatisé m'a forcé à aller au-delà du simple "ça marche". Les métriques de *Pertinence* et de *Cohérence* m'ont notamment poussé à corriger la structure du projet et à blinder la sécurité des uploads. Cette approche garantit que chaque brique de code n'est pas seulement le fruit d'une génération IA rapide, mais d'une co-construction validée par des critères de qualité logicielle (Factualité, Ton technique raccord avec les standards).
