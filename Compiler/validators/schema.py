"""Schema validation for compiler source contracts."""

from __future__ import annotations

from jsonschema import ValidationError, validate

from Compiler.core.diagnostics import SchemaValidationError
from Compiler.core.source_schema import SOURCE_JSON_SCHEMA


def validate_source(source: dict) -> None:
    """Validate an incoming source contract."""

    try:
        validate(
            instance=source,
            schema=SOURCE_JSON_SCHEMA,
        )
    except ValidationError as exc:
        raise SchemaValidationError(
            exc.message
        ) from exc