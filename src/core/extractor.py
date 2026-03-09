"""Logique d extraction IA via API compatible OpenAI (DeepSeek)."""

from __future__ import annotations

import json
import os
from typing import Any, Dict

from dotenv import load_dotenv
from openai import OpenAI

# Import relatif au package core — indépendant du sys.path
from .models import (
    ExtractionMetadata,
    ExtractionResult,
    ExtractionSchema,
    FieldResult,
    ValidationSummary,
)


SYSTEM_RULE = (
    "Tu es un extracteur de donnees strict. Genere un objet JSON valide. "
    "Chaque champ doit etre present dans l'objet JSON final avec sa valeur ou null. "
    "Si un champ est absent du document, retourne null. Ne jamais inventer."
)


def _load_client() -> tuple[OpenAI, str]:
    load_dotenv()

    api_key = os.getenv("DEEPSEEK_API_KEY")
    base_url = os.getenv("DEEPSEEK_API_URL")
    model_name = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    if not api_key:
        raise ValueError("Missing DEEPSEEK_API_KEY in environment")
    if not base_url:
        raise ValueError("Missing DEEPSEEK_API_URL in environment")

    client = OpenAI(api_key=api_key, base_url=base_url)
    return client, model_name


def _build_user_prompt(document_text: str, schema: ExtractionSchema) -> str:
    if not schema.fields:
        raise ValueError("Schema has no fields")

    expected_fields = [
        {
            "name": field.name,
            "type": field.type,
            "required": field.required,
            "description": field.description,
        }
        for field in schema.fields
    ]

    instructions = {
        "task": "Extract fields from document.",
        "output_format": {
            "field_name": {
                "value": "string|number|boolean|date|null",
                "confidence": "float between 0 and 1",
                "status": "found|missing|uncertain",
                "source_hint": "short quote or location",
            }
        },
        "rules": [
            "If data is absent: value=null and status=missing",
            "Never infer missing facts",
            "Keep confidence low (<0.3) for missing values",
        ],
        "schema": expected_fields,
        "document": document_text,
    }
    return json.dumps(instructions, ensure_ascii=True)


def _safe_parse_json(raw_content: str) -> Dict[str, Any]:
    try:
        parsed = json.loads(raw_content)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Model response is not valid JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ValueError("Model response JSON must be an object")
    return parsed


def extract(document_text: str, schema: ExtractionSchema) -> ExtractionResult:
    """Extract fields from free text using an LLM and return typed result."""

    if document_text is None or not document_text.strip():
        return ExtractionResult(
            status="error",
            validation=ValidationSummary(alerts=["Document is empty"], confidence_global=0.0),
        )

    try:
        client, model_name = _load_client()
        user_prompt = _build_user_prompt(document_text=document_text, schema=schema)

        completion = client.chat.completions.create(
            model=model_name,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_RULE},
                {"role": "user", "content": user_prompt},
            ],
            timeout=30,
        )

        raw_content = completion.choices[0].message.content or "{}"
        parsed = _safe_parse_json(raw_content)

        field_results: Dict[str, FieldResult] = {}
        confidence_values: list[float] = []
        alerts: list[str] = []

        for field in schema.fields:
            current = parsed.get(field.name, {})
            value = current.get("value") if isinstance(current, dict) else None
            confidence = float(current.get("confidence", 0.0)) if isinstance(current, dict) else 0.0
            status = current.get("status", "missing") if isinstance(current, dict) else "missing"
            source_hint = current.get("source_hint", "") if isinstance(current, dict) else ""

            if value is None:
                status = "missing"
                confidence = min(confidence, 0.3)
                if field.required:
                    alerts.append(f"Required field missing: {field.name}")

            field_results[field.name] = FieldResult(
                value=value,
                confidence=max(0.0, min(confidence, 1.0)),
                status=status,
                source_hint=source_hint,
            )
            confidence_values.append(field_results[field.name].confidence)

        confidence_global = sum(confidence_values) / len(confidence_values) if confidence_values else 0.0
        status = "success" if confidence_global >= 0.8 and not alerts else "warning"

        return ExtractionResult(
            status=status,
            data=field_results,
            validation=ValidationSummary(confidence_global=confidence_global, alerts=alerts),
            metadata=ExtractionMetadata(model=model_name),
        )
    except Exception as exc:  # Defensive catch for API/network/parser failures.
        return ExtractionResult(
            status="error",
            validation=ValidationSummary(
                confidence_global=0.0,
                alerts=[f"Extraction failed: {exc}"],
            ),
        )
