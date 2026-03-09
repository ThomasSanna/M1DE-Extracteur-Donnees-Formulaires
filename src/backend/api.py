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

Imports :
  Les modules core sont importés directement via le package src.core
  (plus besoin de sys.path hack — src/ est un package Python valide).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field

# --- Imports core via le package propre ---
from src.core.extractor import extract
from src.core.models import ExtractionSchema
from src.core.validator import validate_extraction

# ---------------------------------------------------------------------------
# Chemins de référence
# ---------------------------------------------------------------------------
# api.py est dans src/backend/ → project root = parent.parent.parent
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Schémas JSON d'exemple : data/schemas/ à la racine du projet
SCHEMAS_DIR = PROJECT_ROOT / "data" / "schemas"

# Fichiers statiques du frontend : src/frontend/
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

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

    # 'schema' est un nom réservé par BaseModel (classmethod) → on utilise un alias
    # Le JSON envoyé par le frontend reste { "document_text": ..., "schema": ... }
    model_config = ConfigDict(populate_by_name=True)

    document_text: str = Field(description="Texte brut du document à analyser")
    extraction_schema: Dict[str, Any] = Field(
        alias="schema",
        description="Schéma JSON d'extraction (ExtractionSchema)",
    )


class ExampleSchema(BaseModel):
    """Un schéma exemple exposé par /api/schemas/examples."""

    # Même raison : alias pour éviter le conflit avec BaseModel.schema()
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    name: str
    description: str
    schema_data: Dict[str, Any] = Field(alias="schema")


# ---------------------------------------------------------------------------
# Schémas exemples prédéfinis (chargés depuis data/schemas/)
# ---------------------------------------------------------------------------


def _load_example_schemas() -> List[ExampleSchema]:
    """Charge tous les .json présents dans data/schemas/ comme exemples."""
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
                    schema_data=data,
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
        extraction_schema = ExtractionSchema.model_validate(body.extraction_schema)
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

    # Si l'extraction a retourné une erreur interne (ex: clé API), on la propage
    if extraction_result.status == "error" and extraction_result.validation.alerts:
        first_alert = extraction_result.validation.alerts[0]
        if "Missing DEEPSEEK_API_KEY" in first_alert or "Missing DEEPSEEK_API_URL" in first_alert:
            raise HTTPException(status_code=503, detail=first_alert)

    validated = validate_extraction(result=extraction_result, schema=extraction_schema)

    return JSONResponse(content=json.loads(validated.model_dump_json()))


# ---------------------------------------------------------------------------
# Fichiers statiques frontend — montage en dernier pour ne pas masquer /api
# ---------------------------------------------------------------------------

if FRONTEND_DIR.exists():
    @app.get("/", include_in_schema=False)
    def serve_frontend():
        return FileResponse(FRONTEND_DIR / "index.html")

    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


# ---------------------------------------------------------------------------
# Entrypoint direct
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    uvicorn.run("src.backend.api:app", host="0.0.0.0", port=8000, reload=True)
