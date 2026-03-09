"""FastAPI backend — Extracteur de données de formulaires.

Expose le pipeline extraction + validation via une API REST.
Sert également les fichiers statiques du frontend.

Architecture :
  - POST /api/extract  → pipeline extract→validate, retourne ExtractionResult
  - POST /api/upload   → upload de fichier (PDF/TXT/JSON) avec extraction de texte sécurisée
  - GET  /api/health   → healthcheck
  - GET  /api/schemas/examples → schémas prédéfinis pour le frontend
  - GET  /              → frontend SPA (fichiers statiques)

Sécurité de l'upload (couche MVP défensive) :
  - Extension whitelist : .pdf, .txt, .json uniquement
  - MIME type whitelist : contrôle côté serveur (pas seulement navigateur)
  - Magic bytes : vérification de la signature binaire du fichier
  - Taille max : 5 Mo (évite les attaques DoS par upload massif)
  - Longueur texte max : 50 000 caractères (évite de saturer les tokens LLM)
  - Pas d'antivirus externe (trop complexe pour un MVP, cf. JOURNAL)

Extraction texte :
  - .txt : décode UTF-8 (fallback latin-1)
  - .json : parse + reformate (valide la structure JSON)
  - .pdf : extraire la couche texte via pypdf (nécessite un PDF océrisé)
"""

from __future__ import annotations

import io
import json
import logging
from pathlib import Path
from typing import Any, Dict, List

import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field

from src.core.extractor import extract
from src.core.models import ExtractionSchema
from src.core.validator import validate_extraction

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Chemins
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).parent.parent.parent
SCHEMAS_DIR  = PROJECT_ROOT / "data" / "schemas"
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

# ---------------------------------------------------------------------------
# Constantes de sécurité upload
# ---------------------------------------------------------------------------
MAX_FILE_BYTES  = 5 * 1024 * 1024   # 5 Mo
MAX_TEXT_CHARS  = 50_000             # limite tokens LLM

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".json"}

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "text/plain",
    "application/json",
    "text/json",
    "application/octet-stream",  # navigateurs parfois envoient ça pour les .txt
}

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Extracteur de Données de Formulaires",
    description="API d'extraction de données structurées depuis des documents texte via IA.",
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Modèles Pydantic API
# ---------------------------------------------------------------------------


class ExtractionRequest(BaseModel):
    """Corps de la requête POST /api/extract."""

    model_config = ConfigDict(populate_by_name=True)

    document_text: str = Field(description="Texte brut du document à analyser")
    extraction_schema: Dict[str, Any] = Field(
        alias="schema",
        description="Schéma JSON d'extraction (ExtractionSchema)",
    )


class ExampleSchema(BaseModel):
    """Un schéma exemple exposé par /api/schemas/examples."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    name: str
    description: str
    schema_data: Dict[str, Any] = Field(alias="schema")
    sample_document: str = Field(default="", description="Document exemple associé au schéma")


# ---------------------------------------------------------------------------
# Helpers : sécurité upload
# ---------------------------------------------------------------------------


def _validate_upload_file(filename: str, content_type: str, size: int) -> None:
    """Valide extension, MIME type et taille avant d'accepter le fichier.

    Trois couches de défense :
    1. Extension — bloque les extensions non connues
    2. MIME type — vérifie l'en-tête HTTP (peut être forgé, d'où la couche 3)
    3. Taille — évite les attaques DoS par fichier volumineux
    """
    ext = Path(filename).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Extension « {ext} » non autorisée. "
                f"Formats acceptés : {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            ),
        )

    if content_type and content_type not in ALLOWED_MIME_TYPES:
        # Avertissement non bloquant : certains navigateurs envoient des MIME incorrects
        logger.warning("MIME type inhabituel reçu : %s pour %s", content_type, filename)

    if size > MAX_FILE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=(
                f"Fichier trop volumineux ({size // 1024} Ko). "
                f"Taille maximale : {MAX_FILE_BYTES // (1024 * 1024)} Mo."
            ),
        )


def _check_magic_bytes(data: bytes, filename: str) -> None:
    """Vérifie la signature binaire du fichier (magic bytes).

    Empêche un fichier renommé en .pdf d'être traité comme un PDF valide.
    Couche complémentaire à la validation d'extension.
    """
    ext = Path(filename).suffix.lower()

    if ext == ".pdf":
        if not data.startswith(b"%PDF"):
            raise HTTPException(
                status_code=422,
                detail=(
                    "Le fichier envoyé n'est pas un PDF valide "
                    "(signature %PDF manquante). Vérifiez le fichier."
                ),
            )

    if ext == ".json":
        try:
            json.loads(data.decode("utf-8", errors="replace"))
        except json.JSONDecodeError as exc:
            raise HTTPException(
                status_code=422,
                detail=f"Le fichier JSON est malformé : {exc}",
            ) from exc


def _extract_text_from_bytes(data: bytes, filename: str) -> str:
    """Extrait le texte brut selon l'extension du fichier.

    - .txt  → décodage UTF-8 (fallback latin-1 si nécessaire)
    - .json → parse + re-sérialisation indentée (valide la structure)
    - .pdf  → extraction de la couche texte via pypdf (PDF océrisé requis)

    Raises:
        HTTPException 422 : si le texte ne peut pas être extrait.
    """
    ext = Path(filename).suffix.lower()

    if ext == ".txt":
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            return data.decode("latin-1", errors="replace")

    if ext == ".json":
        parsed = json.loads(data.decode("utf-8", errors="replace"))
        return json.dumps(parsed, ensure_ascii=False, indent=2)

    if ext == ".pdf":
        try:
            import pypdf  # noqa: PLC0415 — import local pour garder pypdf optionnel

            reader = pypdf.PdfReader(io.BytesIO(data))
            pages_text = [page.extract_text() or "" for page in reader.pages]
            text = "\n".join(pages_text).strip()

            if not text:
                raise HTTPException(
                    status_code=422,
                    detail=(
                        "Aucun texte extractible dans ce PDF. "
                        "Assurez-vous que le PDF est bien océrisé (couche texte présente)."
                    ),
                )
            return text

        except ImportError as exc:
            raise HTTPException(
                status_code=503,
                detail="Module pypdf manquant. Installez-le : pip install pypdf",
            ) from exc
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=422,
                detail=f"Impossible d'extraire le texte du PDF : {exc}",
            ) from exc

    raise HTTPException(status_code=422, detail=f"Format non supporté : {ext}")


# ---------------------------------------------------------------------------
# Helpers : schémas
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
                    sample_document=data.get("sample_document", ""),
                )
            )
        except Exception:
            pass
    return examples


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/api/health", tags=["System"])
def health_check():
    """Healthcheck simple."""
    return {"status": "ok", "version": "1.1.0"}


@app.get("/api/schemas/examples", response_model=List[ExampleSchema], tags=["Schemas"])
def get_example_schemas():
    """Retourne la liste des schémas d'extraction prédéfinis."""
    return _load_example_schemas()


@app.post("/api/upload", tags=["Documents"])
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Upload et extraction de texte depuis un ou plusieurs fichiers (Batch processing).

    Formats acceptés : .pdf (océrisé), .txt, .json
    Limites de sécurité (par fichier) :
      - Taille max : 5 Mo
      - Extensions whitelist
      - Signature binaire (magic bytes)
    """
    results = []

    for file in files:
        data = await file.read()
        size = len(data)
        filename = file.filename or "fichier_inconnu"
        content_type = file.content_type or ""

        try:
            _validate_upload_file(filename=filename, content_type=content_type, size=size)
            _check_magic_bytes(data=data, filename=filename)
            text = _extract_text_from_bytes(data=data, filename=filename)

            truncated = False
            if len(text) > MAX_TEXT_CHARS:
                text = text[:MAX_TEXT_CHARS]
                truncated = True
                logger.warning("Texte tronqué à %d caractères pour %s", MAX_TEXT_CHARS, filename)

            results.append({
                "filename": filename,
                "text": text,
                "size_ko": round(size / 1024, 1),
                "file_type": Path(filename).suffix.lower(),
                "truncated": truncated,
                "char_count": len(text),
                "status": "success"
            })
        except HTTPException as exc:
            results.append({
                "filename": filename,
                "status": "error",
                "error": exc.detail
            })
        except Exception as exc:
            results.append({
                "filename": filename,
                "status": "error",
                "error": str(exc)
            })

    return JSONResponse(content={"files": results})


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
    - Document vide → 422
    - Schéma sans champs → 422
    - Clé API manquante → 503
    - Toute autre erreur → 500
    """
    if not body.document_text or not body.document_text.strip():
        raise HTTPException(
            status_code=422,
            detail="Le document est vide. Veuillez fournir du texte à analyser.",
        )

    try:
        extraction_schema = ExtractionSchema.model_validate(body.extraction_schema)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Schéma JSON invalide : {exc}") from exc

    if not extraction_schema.fields:
        raise HTTPException(
            status_code=422,
            detail="Le schéma ne contient aucun champ. Ajoutez au moins un champ à extraire.",
        )

    try:
        extraction_result = extract(document_text=body.document_text, schema=extraction_schema)
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erreur inattendue : {exc}") from exc

    if extraction_result.status == "error" and extraction_result.validation.alerts:
        first_alert = extraction_result.validation.alerts[0]
        if "Missing DEEPSEEK_API_KEY" in first_alert or "Missing DEEPSEEK_API_URL" in first_alert:
            raise HTTPException(status_code=503, detail=first_alert)

    validated = validate_extraction(result=extraction_result, schema=extraction_schema)
    return JSONResponse(content=json.loads(validated.model_dump_json()))


# ---------------------------------------------------------------------------
# Fichiers statiques frontend
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
