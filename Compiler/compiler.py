"""Project Permanence deterministic compiler."""

from __future__ import annotations

from Compiler.core.canonical import canonical_hash, canonical_json
from Compiler.core.parser import parse_contract
from Compiler.validators.schema import validate_source
from Compiler.core.context_runway import (
    canonical_json as canonical_runway_json,
    diff_context_runways,
    hash_context_runway,
    source_manifest,
    verify_runway_lineage,
)
from Compiler.generators.context_runway import generate_context_runway_markdown
from Compiler.validators.context_runway import validate_context_runway


class Compiler:
    """Deterministic compiler pipeline."""

    def compile(self, source: dict) -> tuple[str, str]:
        """Compile a source contract."""

        validate_source(source)

        contract = parse_contract(source)

        canonical = canonical_json(contract)

        identity = canonical_hash(canonical)

        return canonical, identity


def compile_context_runway(source: dict) -> dict:
    """Compile a validated runway into deterministic portable outputs."""

    report = validate_context_runway(source)
    if not report["valid"]:
        raise ValueError("Context runway validation failed")

    payload = source["payload"]
    identity = hash_context_runway(source)
    return {
        "canonical_json": canonical_runway_json(payload),
        "portable_markdown": generate_context_runway_markdown(payload, identity),
        "manifest_hash": identity,
        "source_manifest": source_manifest(source),
        "validation_report": report,
        "predecessor_diff": diff_context_runways(source.get("predecessor"), payload),
    }


__all__ = [
    "Compiler",
    "compile_context_runway",
    "validate_context_runway",
    "hash_context_runway",
    "diff_context_runways",
    "verify_runway_lineage",
]
