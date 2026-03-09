"""FastAPI backend — Extracteur de données de formulaires.

Expose le pipeline extraction + validation via une API REST.
Sert également les fichiers statiques du frontend.

Architecture :
  - POST /api/extract  → pipeline extract→validate, retourne ExtractionResult
  - GET  /api/health   → healthcheck
  - GET  /api/schemas/examples → schémas prédéfinis pour le frontend
  - GET  /              → frontend SPA (fichiers statiques)

Pourquoi FastAPI ?
  - Compatible Pydantic (mêmes modèles que le core)
  - Validation automatique des corps de requête
  - Documentation Swagger générée gratuitement (/docs)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# --- Ajout du répertoire src/ au path pour importer les modules core ---
SRC_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SRC_DIR))

from extractor import extract  # noqa: E402
from models import ExtractionSchema  # noqa: E402
from validator import validate_extraction  # noqa: E402

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Extracteur de Données de Formulaires",
    description="API d'extraction de données structurées depuis des documents texte via IA.",
    version="1.0.0",
)

# CORS — autoriser le frontend servi localement
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restreindre en production
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Schémas de requête / réponse spécifiques à l'API
# ---------------------------------------------------------------------------


class ExtractionRequest(BaseModel):
    """Corps de la requête POST /api/extract."""

    document_text: str = Field(description="Texte brut du document à analyser")
    schema: Dict[str, Any] = Field(description="Schéma JSON d'extraction (ExtractionSchema)")


class ExampleSchema(BaseModel):
    """Un schéma exemple exposé par /api/schemas/examples."""

    name: str
    description: str
    schema: Dict[str, Any]


# ---------------------------------------------------------------------------
# Schémas exemples prédéfinis (chargés depuis src/schemas/)
# ---------------------------------------------------------------------------

SCHEMAS_DIR = SRC_DIR / "schemas"


def _load_example_schemas() -> List[ExampleSchema]:
    """Charge tous les .json présents dans src/schemas/ comme exemples."""
    examples: List[ExampleSchema] = []
    if not SCHEMAS_DIR.exists():
        return examples
    for schema_file in sorted(SCHEMAS_DIR.glob("*.json")):
        try:
            data = json.loads(schema_file.read_text(encoding="utf-8"))
            examples.append(
                ExampleSchema(
                    name=data.get("schema_name", schema_file.stem),
                    description=data.get("description", ""),
                    schema=data,
                )
            )
        except Exception:
            # Fichier malformé — on ignore silencieusement
            pass
    return examples


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/api/health", tags=["System"])
def health_check():
    """Healthcheck simple."""
    return {"status": "ok", "version": "1.0.0"}


@app.get("/api/schemas/examples", response_model=List[ExampleSchema], tags=["Schemas"])
def get_example_schemas():
    """
    Retourne la liste des schémas d'extraction prédéfinis.
    Utile pour pré-charger le frontend avec des schémas ready-to-use.
    """
    return _load_example_schemas()


@app.post("/api/extract", tags=["Extraction"])
def extract_document(body: ExtractionRequest):
    """
    Extrait les données structurées d'un document texte selon un schéma.

    Pipeline :
    1. Valide le schéma (Pydantic)
    2. Appelle l'extracteur IA (DeepSeek)
    3. Passe le résultat par le validateur métier
    4. Retourne l'ExtractionResult sérialisé en JSON

    Cas limites gérés :
    - Document vide → 422 avec message clair
    - Schéma sans champs → 422 avec message clair
    - Clé API manquante → 503 Service Unavailable
    - Timeout API → 503 Service Unavailable
    - Toute autre erreur → 500 avec détail
    """
    # Validation préalable du document
    if not body.document_text or not body.document_text.strip():
        raise HTTPException(
            status_code=422,
            detail="Le document est vide. Veuillez fournir du texte à analyser.",
        )

    # Validation et parsing du schéma
    try:
        extraction_schema = ExtractionSchema.model_validate(body.schema)
    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Schéma JSON invalide : {exc}",
        ) from exc

    if not extraction_schema.fields:
        raise HTTPException(
            status_code=422,
            detail="Le schéma ne contient aucun champ. Ajoutez au moins un champ à extraire.",
        )

    # Pipeline extraction → validation
    try:
        extraction_result = extract(
            document_text=body.document_text,
            schema=extraction_schema,
        )
    except ValueError as exc:
        # Cas typique : clé API manquante
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur inattendue lors de l'extraction : {exc}",
        ) from exc

    # Si l'extraction a retourné une erreur interne (ex: timeout), on la propage
    if extraction_result.status == "error" and extraction_result.validation.alerts:
        first_alert = extraction_result.validation.alerts[0]
        if "Missing DEEPSEEK_API_KEY" in first_alert or "Missing DEEPSEEK_API_URL" in first_alert:
            raise HTTPException(status_code=503, detail=first_alert)

    validated = validate_extraction(result=extraction_result, schema=extraction_schema)

    return JSONResponse(content=json.loads(validated.model_dump_json()))


# ---------------------------------------------------------------------------
# Fichiers statiques frontend — montage en dernier pour ne pas masquer /api
# ---------------------------------------------------------------------------

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

if FRONTEND_DIR.exists():
    # Servir index.html pour la racine
    @app.get("/", include_in_schema=False)
    def serve_frontend():
        return FileResponse(FRONTEND_DIR / "index.html")

    # Servir les assets statiques
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


# ---------------------------------------------------------------------------
# Entrypoint direct (python api.py)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
