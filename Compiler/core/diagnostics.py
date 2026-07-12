"""Compiler diagnostics and validation exceptions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Diagnostic:
    code: str
    message: str
    severity: str
    location: str | None = None
    details: dict[str, Any] | None = None


class CompilerError(Exception):
    """Base compiler exception."""


class SchemaValidationError(CompilerError):
    """Raised when source schema validation fails."""


class CanonicalizationError(CompilerError):
    """Raised when canonical serialization fails."""


class ParserError(CompilerError):
    """Raised when semantic lowering fails."""