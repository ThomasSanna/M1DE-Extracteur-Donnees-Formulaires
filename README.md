# FormAI — Extracteur de données IA (Projet 13)

**Auteur** : Sanna Thomas — M1 Data Engineer

FormAI est une application web intelligente permettant d'extraire automatiquement des données structurées à partir de n'importe quel document texte ou PDF non-structuré (factures, CV, fiches de paie, etc.). Grâce à un schéma JSON défini dynamiquement et à la puissance d'un moteur LLM, l'outil transforme du texte brut en données prêtes à l'emploi.

---

## 🚀 Fonctionnalités principales

- **Extraction Dynamique** : Construisez dynamiquement votre schéma d'extraction (nom, type, obligatoire, description) directement depuis l'interface utilisateur.
- **Import Intelligent (Batch Mode)** : Uploadez un ou plusieurs fichiers simultanément (PDF océrisés, TXT, JSON). Les fichiers sont lus et traités avec un envoi en file d'attente pour éviter le rate-limiting du LLM.
- **Data-Driven Mocks** : Templates intégrés (`data/schemas/*.json`) avec documents d'exemples natifs.
- **Sécurité & Défense** :
  - Limitation de taille (5 Mo max).
  - Vérification des "Magic Bytes" pour s'assurer du vrai format des fichiers (indépendamment de leur extension).
  - Troncature sécurisée à 50 000 caractères pour respecter les limites (Token limit) des API LLM.
- **Analyse de Confiance** : L'IA évalue son taux de certitude pour l'extraction de *chaque champ*. Code couleur visuel des pourcentages de confiance (Faible/Moyen/Élevé).
- **Export Standardisé** : Téléchargement natif de l'extraction vers un fichier `.json`.

---

## 🛠️ Stack Technique

### Backend
- **Python 3.10+**
- **FastAPI** & **Uvicorn** : Création d'une API REST robuste et asynchrone pour l'interface entre le client et l'intelligence artificielle.
- **Pydantic** : Validation stricte des données (Typage, erreurs) en entrée et en sortie.
- **OpenAI SDK** : Implémentation via l'API client d'OpenAI tout en pointant grâce au paramètre `base_url` vers l'API de DeepSeek (`deepseek-chat`). L'utilisation du `response_format={"type": "json_object"}` garantit de tout le temps recevoir un JSON.
- **PyPDF** : Lecture et extraction du contenu textuel des fichiers PDF.
- **Pytest** : Suite de tests unitaires pour assurer la fiabilité du code.

### Frontend
- **HTML5 / CSS3 Vanilla** : Architecture UI moderne, "Glassmorphism" et Responsive. UI/UX "Premium" sans frameworks lourds.
- **JavaScript Vanilla (ES6+)** : Logique applicative (Single Page Application locale). Système événementiel (AbortController, File Reader) couplé à une architecture modulaire (`ToastManager`, `SchemaBuilder`, `ResultsRenderer`). Zéro dépendance.

---

## 🗺️ Architecture du projet

```text
C:
│   .env                      # Variables d'environnement (clés API)
│   .env.example              # Exemple de fichier env
│   JOURNAL.md                # Journal de bord détaillé des décisions architecturales
│   README.md                 # Documentation du projet (vous êtes ici)
│   requirements.txt          # Dépendances Python
│   sujet.md                  # Consignes du projet
│
├───data
│   ├───results               # Exports JSON téléchargeables
│   ├───samples               # Fichiers d'exemples (.txt, .pdf) pour tests de robustesse
│   └───schemas               # Templates JSON des schémas d'extraction
│
├───src
│   ├───backend
│   │       api.py            # Point d'entrée FastAPI / Routes API
│   │       models.py         # Modèles de données (Pydantic)
│   │
│   ├───core
│   │       extractor.py      # Logique de communication avec le LLM (DeepSeek)
│   │
│   └───frontend
│           app.js            # Logique applicative JavaScript (Batch processing, UI)
│           index.html        # Vue unique de l'application
│           style.css         # Styling, tokens, et animations
│
└───tests
        test_edge_cases.py    # Tests unitaires du projet
```

---

## ⚙️ Installation et Exécution

### 1. Prérequis
- Installer Python (>= 3.10)
- Créer un environnement virtuel :
```bash
python -m venv venv
# Windows :
venv\Scripts\activate
# Linux/Mac :
source venv/bin/activate
```

### 2. Dépendances
```bash
pip install -r requirements.txt
```

### 3. Configuration
Copiez le fichier d'exemple et renseignez votre clé API :
```bash
cp .env.example .env
```
Éditez le `.env` pour y ajouter :
```properties
DEEPSEEK_API_KEY="votre-clé-api-ici"
```

### 4. Lancement de l'application
Le lancement nécessite impérativement d'être à la racine du projet, pour que le chemin complet du module `src` soit bien détecté.

```bash
uvicorn src.backend.api:app --reload --port 8000
```
**Accédez ensuite à l'interface graphique :** [http://127.0.0.1:8000](http://127.0.0.1:8000)
Vous pourrez également observer la documentation Swagger de FastAPI générée automatiquement sur : [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🧪 Lancer les tests

L'application dispose d'une suite de tests (vérification de la gestion des erreurs HTTP 503, validation de JSON mal formés, document inexploitable par l'IA, conformité de JSON).

```bash
pytest tests/ -v
```
