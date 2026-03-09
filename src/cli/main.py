"""Point d entree CLI pour extraction et validation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Import absolu depuis la racine du projet (exécuté avec python -m src.cli.main)
from src.core.extractor import extract
from src.core.models import ExtractionResult, ExtractionSchema
from src.core.validator import validate_extraction


def _read_text_file(file_path: Path) -> str:
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    return file_path.read_text(encoding="utf-8")


def _load_schema(schema_path: Path) -> ExtractionSchema:
    schema_raw = _read_text_file(schema_path)
    try:
        schema_obj = json.loads(schema_raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid schema JSON: {exc}") from exc
    return ExtractionSchema.model_validate(schema_obj)


def _write_output(result: ExtractionResult, output_path: Path | None) -> None:
    if output_path is None:
        return
    output_path.write_text(result.model_dump_json(indent=2), encoding="utf-8")


def _print_summary(result: ExtractionResult) -> None:
    print(f"Status: {result.status}")
    print(f"Global confidence: {result.validation.confidence_global:.2f}")
    if result.validation.alerts:
        print("Alerts:")
        for alert in result.validation.alerts:
            print(f"  - {alert}")


def handle_extract(args: argparse.Namespace) -> int:
    schema = _load_schema(Path(args.schema))
    document_text = _read_text_file(Path(args.document))

    extraction = extract(document_text=document_text, schema=schema)
    validated = validate_extraction(result=extraction, schema=schema)

    _print_summary(validated)
    _write_output(validated, Path(args.output) if args.output else None)

    return 1 if validated.status == "error" else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Extracteur de donnees de formulaires")
    subparsers = parser.add_subparsers(dest="command", required=True)

    extract_parser = subparsers.add_parser("extract", help="Extraire des champs d un document")
    extract_parser.add_argument("--document", required=True, help="Chemin du document texte")
    extract_parser.add_argument("--schema", required=True, help="Chemin du schema JSON")
    extract_parser.add_argument("--output", required=False, help="Chemin du resultat JSON")
    extract_parser.set_defaults(func=handle_extract)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        return args.func(args)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}")
        return 1
    except Exception as exc:  # Defensive fallback to avoid raw traceback in CLI usage.
        print(f"Unexpected error: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
