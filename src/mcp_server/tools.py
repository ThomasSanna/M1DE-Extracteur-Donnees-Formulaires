"""Définition des Tools MCP exposés par le serveur FormAI.

Chaque fonction est un tool MCP autonome. Elle wrappe la logique métier
existante (src.core.extractor, src.core.models) et retourne un dict
JSON-sérialisable que le client MCP (LLM) peut interpréter directement.

Choix de design :
- Aucun crash : toute exception est capturée et retournée comme erreur structurée.
- Sécurité : le texte est tronqué à 50 000 caractères (même limite que l'API REST).
- Sérialisation : ExtractionResult.model_dump(mode="json") gère les datetime et types custom.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List

from src.core.extractor import extract
from src.core.models import ExtractionSchema

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent
SCHEMAS_DIR = PROJECT_ROOT / "data" / "schemas"

MAX_TEXT_CHARS = 50_000  # même limite que l'API REST — protège contre les inputs massifs


def extract_from_text(document_text: str, schema: Dict[str, Any]) -> Dict[str, Any]:
    """Extrait des données structurées depuis un texte brut selon un schéma JSON.

    Utilise le moteur IA DeepSeek (via OpenAI SDK) pour analyser le document
    et mapper les champs définis dans le schéma. Chaque champ extrait dispose
    d'un score de confiance (0.0 à 1.0) et d'un statut (found / missing / uncertain).

    Paramètres :
        document_text : Le texte brut du document à analyser (CV, facture, fiche de paie...).
        schema : Schéma JSON décrivant les champs à extraire.
                 Format attendu :
                 {
                   "schema_name": "cv",
                   "description": "Extraction CV",
                   "fields": [
                     {"name": "nom", "type": "string", "required": true, "description": "Nom complet"}
                   ]
                 }

    Retourne :
        Un dict avec les champs extraits, leurs valeurs, scores de confiance et alertes.
    """
    # --- Sécurité : troncature input ---
    if not document_text or not document_text.strip():
        return {"status": "error", "message": "Le document est vide."}

    if len(document_text) > MAX_TEXT_CHARS:
        logger.warning("Texte tronqué à %d caractères par le tool MCP.", MAX_TEXT_CHARS)
        document_text = document_text[:MAX_TEXT_CHARS]

    # --- Validation du schéma ---
    try:
        extraction_schema = ExtractionSchema.model_validate(schema)
    except Exception as exc:
        return {"status": "error", "message": f"Schéma JSON invalide : {exc}"}

    if not extraction_schema.fields:
        return {"status": "error", "message": "Le schéma ne contient aucun champ à extraire."}

    # --- Extraction IA ---
    try:
        result = extract(document_text=document_text, schema=extraction_schema)
        # model_dump(mode="json") sérialise les datetime → str automatiquement
        return result.model_dump(mode="json")
    except Exception as exc:
        logger.exception("Erreur inattendue dans extract_from_text")
        return {"status": "error", "message": f"Erreur inattendue : {exc}"}


def list_schemas() -> List[Dict[str, Any]]:
    """Liste tous les schémas d'extraction prédéfinis disponibles dans FormAI.

    Les schémas sont des templates JSON stockés dans data/schemas/.
    Chaque schéma définit un type de document et ses champs attendus
    (ex: CV, Facture, Fiche de paie...).

    Retourne :
        Une liste de dicts décrivant chaque schéma disponible :
        [{"name": ..., "description": ..., "fields": [...]}]
        Retourne une liste vide si aucun schéma n'est disponible.
    """
    schemas: List[Dict[str, Any]] = []

    if not SCHEMAS_DIR.exists():
        logger.warning("Dossier data/schemas/ introuvable : %s", SCHEMAS_DIR)
        return schemas

    for schema_file in sorted(SCHEMAS_DIR.glob("*.json")):
        try:
            data = json.loads(schema_file.read_text(encoding="utf-8"))
            schemas.append({
                "name": data.get("schema_name", schema_file.stem),
                "description": data.get("description", ""),
                "fields": data.get("fields", []),
            })
        except Exception as exc:
            logger.warning("Impossible de lire le schéma %s : %s", schema_file.name, exc)

    return schemas


def extract_from_file(file_path: str, schema: Dict[str, Any]) -> Dict[str, Any]:
    """Extrait des données structurées depuis un fichier local (PDF, TXT, JSON).

    Lit le fichier spécifié par file_path, extrait son texte brut selon son extension,
    puis utilise l'extracteur IA pour extraire les données selon le schéma JSON fourni.

    Paramètres :
        file_path : Chemin absolu vers le fichier local à analyser.
        schema : Schéma JSON décrivant les champs à extraire. Ex: {"schema_name": "...", "fields": [...]}

    Retourne :
        Un dict avec les champs extraits (valeurs, statuts, confiance) ou un message d'erreur.
    """
    path = Path(file_path)
    if not path.is_file():
        return {"status": "error", "message": f"Fichier introuvable ou invalide : {file_path}"}
    
    try:
        data = path.read_bytes()
        ext = path.suffix.lower()
        text = ""

        if ext == ".txt":
            try:
                text = data.decode("utf-8")
            except UnicodeDecodeError:
                text = data.decode("latin-1", errors="replace")
        elif ext == ".json":
            parsed = json.loads(data.decode("utf-8", errors="replace"))
            text = json.dumps(parsed, ensure_ascii=False, indent=2)
        elif ext == ".pdf":
            try:
                import io
                import pypdf
                reader = pypdf.PdfReader(io.BytesIO(data))
                pages_text = [page.extract_text() or "" for page in reader.pages]
                text = "\n".join(pages_text).strip()
                if not text:
                    return {"status": "error", "message": "Aucun texte extractible dans ce PDF (besoin d'OCR)."}
            except ImportError:
                return {"status": "error", "message": "Module pypdf manquant. Installez-le pour lire les PDF."}
            except Exception as exc:
                return {"status": "error", "message": f"Erreur de lecture PDF : {exc}"}
        else:
            return {"status": "error", "message": f"Format de fichier non supporté par MCP FormAI : {ext}"}

        # Délègue l'extraction au tool principal extract_from_text
        return extract_from_text(document_text=text, schema=schema)

    except Exception as exc:
        logger.exception("Erreur lors de la lecture du fichier %s", file_path)
        return {"status": "error", "message": f"Erreur de traitement du fichier : {exc}"}
