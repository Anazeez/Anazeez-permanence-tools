"""Deterministic canonical serialization utilities."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from typing import Any

from Compiler.core.ir import ContractIR


def canonical_json(contract: ContractIR) -> str:
    """Serialize a ContractIR into deterministic canonical JSON."""

    data = asdict(contract)

    authority = data["authority"]
    authority["class"] = authority.pop("class_type")

    data["schema"] = data.pop("schema_version")

    return json.dumps(
        _prune(data),
        sort_keys=True,
        separators=(",", ":"),
    )


def canonical_hash(canonical: str) -> str:
    """Return the SHA-256 identity hash."""

    return hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest()


def _prune(value: Any) -> Any:
    """Remove empty collections and null values."""

    if isinstance(value, dict):
        return {
            k: _prune(v)
            for k, v in value.items()
            if v not in (None, (), [], {})
        }

    if isinstance(value, list):
        return [_prune(v) for v in value]

    return value