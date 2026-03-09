"""Validation metier et technique du resultat d extraction."""

from __future__ import annotations

from datetime import datetime

# Import relatif au package core — évite les dépendances sys.path
from .models import ExtractionResult, ExtractionSchema


def _is_valid_date(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validate_extraction(result: ExtractionResult, schema: ExtractionSchema) -> ExtractionResult:
    """Validate required fields and type consistency without mutating extracted values."""

    alerts = list(result.validation.alerts)
    confidence_values: list[float] = []

    for field in schema.fields:
        field_result = result.data.get(field.name)
        if field_result is None:
            if field.required:
                alerts.append(f"Missing field in result object: {field.name}")
            continue

        confidence_values.append(field_result.confidence)

        if field.required and field_result.status == "missing":
            alerts.append(f"Required field is missing: {field.name}")

        if field_result.value is None:
            continue

        if field.type == "number":
            try:
                float(field_result.value)
            except (TypeError, ValueError):
                alerts.append(f"Type mismatch for {field.name}: expected number")

        if field.type == "boolean" and not isinstance(field_result.value, bool):
            alerts.append(f"Type mismatch for {field.name}: expected boolean")

        if field.type == "date" and not _is_valid_date(field_result.value):
            alerts.append(f"Type mismatch for {field.name}: expected date YYYY-MM-DD")

        if field.type == "string" and not isinstance(field_result.value, str):
            alerts.append(f"Type mismatch for {field.name}: expected string")

    confidence_global = sum(confidence_values) / len(confidence_values) if confidence_values else 0.0

    has_required_missing = any(
        result.data.get(field.name) is None
        or result.data[field.name].status == "missing"
        for field in schema.fields
        if field.required
    )

    result.validation.alerts = alerts
    result.validation.confidence_global = confidence_global

    if result.status == "error":
        return result

    result.status = "success" if confidence_global > 0.8 and not has_required_missing else "warning"
    return result
