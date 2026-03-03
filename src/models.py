"""Modeles Pydantic pour le schema d extraction et le resultat."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


AllowedFieldType = Literal["string", "number", "date", "boolean"]
AllowedFieldStatus = Literal["found", "missing", "uncertain"]
AllowedGlobalStatus = Literal["success", "warning", "error"]


class FieldDefinition(BaseModel):
    """Definition d un champ attendu dans le schema d extraction."""

    name: str = Field(min_length=1, description="Nom du champ cible")
    type: AllowedFieldType = Field(description="Type attendu")
    required: bool = Field(default=True, description="Champ obligatoire ou non")
    description: str = Field(default="", description="Contexte metier du champ")


class ExtractionSchema(BaseModel):
    """Schema d extraction complet avec liste des champs attendus."""

    schema_name: str = Field(min_length=1, description="Nom du schema")
    description: str = Field(default="", description="Description du schema")
    fields: List[FieldDefinition] = Field(default_factory=list)

    @field_validator("fields")
    @classmethod
    def validate_unique_names(cls, values: List[FieldDefinition]) -> List[FieldDefinition]:
        names = [field.name for field in values]
        duplicates = {name for name in names if names.count(name) > 1}
        if duplicates:
            duplicated = ", ".join(sorted(duplicates))
            raise ValueError(f"Duplicate field names found: {duplicated}")
        return values


class FieldResult(BaseModel):
    """Resultat d extraction pour un champ unique."""

    value: Optional[Any] = Field(default=None, description="Valeur extraite ou null")
    confidence: float = Field(ge=0.0, le=1.0, description="Confiance de l extraction")
    status: AllowedFieldStatus = Field(description="Etat de presence du champ")
    source_hint: str = Field(default="", description="Indice de provenance dans le document")


class ExtractionMetadata(BaseModel):
    """Metadonnees techniques pour tracer l extraction."""

    model: str = Field(default="", description="Modele IA utilise")
    extracted_at: datetime = Field(default_factory=datetime.utcnow)


class ValidationSummary(BaseModel):
    """Resume de validation transversale du resultat."""

    confidence_global: float = Field(default=0.0, ge=0.0, le=1.0)
    alerts: List[str] = Field(default_factory=list)


class ExtractionResult(BaseModel):
    """Resultat global de l extraction."""

    status: AllowedGlobalStatus = Field(default="warning")
    data: Dict[str, FieldResult] = Field(default_factory=dict)
    validation: ValidationSummary = Field(default_factory=ValidationSummary)
    metadata: ExtractionMetadata = Field(default_factory=ExtractionMetadata)
