import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from src.core.extractor import extract
from src.core.models import (
    ExtractionResult,
    ExtractionSchema,
    FieldDefinition,
    FieldResult,
    ValidationSummary,
)
from src.core.validator import validate_extraction


def _build_mock_client(raw_content: str):
    message = SimpleNamespace(content=raw_content)
    choice = SimpleNamespace(message=message)
    completion = SimpleNamespace(choices=[choice])

    completions = SimpleNamespace(create=lambda **kwargs: completion)
    chat = SimpleNamespace(completions=completions)
    return SimpleNamespace(chat=chat)


class TestExtractorEdgeCases(unittest.TestCase):
    def test_empty_document_returns_error_without_crash(self):
        schema = ExtractionSchema(
            schema_name="empty_doc_schema",
            fields=[FieldDefinition(name="nom", type="string", required=True)],
        )

        result = extract("   ", schema)

        self.assertIn(result.status, {"error", "warning"})
        self.assertTrue(any("empty" in alert.lower() for alert in result.validation.alerts))

    def test_all_fields_missing_marked_missing_with_low_confidence(self):
        schema = ExtractionSchema(
            schema_name="all_missing_schema",
            fields=[
                FieldDefinition(name="nom_fournisseur", type="string", required=True),
                FieldDefinition(name="montant_total", type="number", required=True),
                FieldDefinition(name="date_facture", type="date", required=True),
            ],
        )

        mock_client = _build_mock_client(raw_content=json.dumps({}))

        # Patch via le chemin complet du module core
        with patch("src.core.extractor._load_client", return_value=(mock_client, "mock-model")):
            result = extract("Texte sans infos exploitables", schema)

        self.assertIn(result.status, {"warning", "error"})
        for field in schema.fields:
            self.assertIn(field.name, result.data)
            self.assertEqual(result.data[field.name].status, "missing")
            self.assertLess(result.data[field.name].confidence, 0.3)

    def test_malformed_json_from_model_handled_without_crash(self):
        schema = ExtractionSchema(
            schema_name="malformed_json_schema",
            fields=[FieldDefinition(name="numero_facture", type="string", required=True)],
        )

        mock_client = _build_mock_client(raw_content="{not-valid-json")

        with patch("src.core.extractor._load_client", return_value=(mock_client, "mock-model")):
            result = extract("Facture #A-123", schema)

        self.assertEqual(result.status, "error")
        self.assertTrue(any("failed" in alert.lower() for alert in result.validation.alerts))

    def test_schema_without_required_fields_can_succeed(self):
        schema = ExtractionSchema(
            schema_name="optional_only_schema",
            fields=[FieldDefinition(name="note", type="string", required=False)],
        )

        model_payload = {
            "note": {
                "value": "Information optionnelle",
                "confidence": 0.95,
                "status": "found",
                "source_hint": "Ligne 1",
            }
        }
        mock_client = _build_mock_client(raw_content=json.dumps(model_payload))

        with patch("src.core.extractor._load_client", return_value=(mock_client, "mock-model")):
            result = extract("Document avec une note", schema)

        self.assertEqual(result.status, "success")
        self.assertIn("note", result.data)
        self.assertEqual(result.data["note"].status, "found")

    def test_incorrect_type_triggers_validation_alert(self):
        schema = ExtractionSchema(
            schema_name="type_mismatch_schema",
            fields=[FieldDefinition(name="montant_total", type="number", required=True)],
        )

        extraction_result = ExtractionResult(
            status="warning",
            data={
                "montant_total": FieldResult(
                    value="pas_un_nombre",
                    confidence=0.9,
                    status="found",
                    source_hint="Ligne montant",
                )
            },
            validation=ValidationSummary(confidence_global=0.9, alerts=[]),
        )

        validated = validate_extraction(extraction_result, schema)

        self.assertIn(validated.status, {"success", "warning"})
        self.assertTrue(
            any(
                "type mismatch" in alert.lower() and "montant_total" in alert
                for alert in validated.validation.alerts
            )
        )


if __name__ == "__main__":
    unittest.main()
