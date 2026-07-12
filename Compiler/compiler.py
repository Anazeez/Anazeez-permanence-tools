"""Project Permanence deterministic compiler."""

from __future__ import annotations

from Compiler.core.canonical import canonical_hash, canonical_json
from Compiler.core.parser import parse_contract
from Compiler.validators.schema import validate_source


class Compiler:
    """Deterministic compiler pipeline."""

    def compile(self, source: dict) -> tuple[str, str]:
        """Compile a source contract."""

        validate_source(source)

        contract = parse_contract(source)

        canonical = canonical_json(contract)

        identity = canonical_hash(canonical)

        return canonical, identity