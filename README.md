# Extracteur de données de formulaires (Projet 13)

Ce projet permet d'extraire des données structurées à partir de formulaires variés (PDF, images, texte) en utilisant l'IA.

## Fonctionnalités
- Extraction intelligente selon un schéma JSON.
- Validation automatique des données.
- Niveau de confiance par champ.
- Signalement des anomalies.

## Installation
S'assurer d'avoir Python 3.10+ installé.
```bash
pip install -r requirements.txt
```

## Utilisation
1. Placez vos documents dans le dossier `data/input`.
2. Lancez l'outil :
```bash
python src/main.py --input data/input --output data/output
```

## Choix techniques
Voir le [JOURNAL.md](JOURNAL.md) pour plus de détails.
- **Extraction** : OpenAI Structured Output
- **Validation** : Pydantic
- **OCR (si nécessaire)** : Tesseract ou PyMuPDF
