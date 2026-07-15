"""Canonical contextual runway compilation primitives."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping, Optional


RUNWAY_SCHEMA = "mnemosyne.context-runway/1.0"


def canonical_json(value: Any) -> str:
    """Serialize JSON data using the Worker-compatible deterministic projection."""

    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def runway_manifest_json(payload: Mapping[str, Any], source_hashes: list) -> str:
    """Return the exact manifest projection hashed by Mnemosyne-Worker."""

    return canonical_json({"payload": payload, "source_hashes": source_hashes})


def hash_context_runway(source: Mapping[str, Any]) -> str:
    """Hash a contextual runway manifest without deciding its authority."""

    payload = source.get("payload", {})
    source_hashes = source.get("source_hashes", [])
    manifest = runway_manifest_json(payload, source_hashes)
    return hashlib.sha256(manifest.encode("utf-8")).hexdigest()


def source_manifest(source: Mapping[str, Any]) -> list:
    """Build a deterministic, content-free source manifest."""

    manifest = [
        {
            "source_ref": item.get("source_ref"),
            "sha256": item.get("sha256"),
        }
        for item in source.get("sources", [])
        if isinstance(item, Mapping)
    ]
    return sorted(manifest, key=lambda item: (str(item["source_ref"]), str(item["sha256"])))


def diff_context_runways(
    predecessor: Optional[Mapping[str, Any]],
    current: Mapping[str, Any],
) -> dict:
    """Describe field-level payload changes without interpreting standing."""

    previous = dict(predecessor or {})
    present = dict(current)
    fields = sorted(set(previous) | set(present))
    changed = [field for field in fields if previous.get(field) != present.get(field)]
    added = [field for field in fields if field not in previous]
    removed = [field for field in fields if field not in present]

    return {
        "from_runway_id": previous.get("runway_id"),
        "to_runway_id": present.get("runway_id"),
        "changed_fields": changed,
        "added_fields": added,
        "removed_fields": removed,
    }


def verify_runway_lineage(
    current: Mapping[str, Any],
    predecessor: Optional[Mapping[str, Any]],
) -> dict:
    """Verify exact tuple, predecessor, and generation continuity."""

    errors = []
    generation = current.get("generation")
    predecessor_id = current.get("predecessor_runway_id")

    if generation == 1 and predecessor_id is None and predecessor is None:
        return {"valid": True, "errors": []}

    if predecessor is None:
        errors.append(_finding("LINEAGE_PREDECESSOR_REQUIRED"))
        return {"valid": False, "errors": errors}

    for field, code in (
        ("identity_id", "LINEAGE_IDENTITY_MISMATCH"),
        ("project_id", "LINEAGE_PROJECT_MISMATCH"),
        ("scope_key", "LINEAGE_SCOPE_MISMATCH"),
    ):
        if current.get(field) != predecessor.get(field):
            errors.append(_finding(code, field=field))

    if predecessor_id != predecessor.get("runway_id"):
        errors.append(_finding("LINEAGE_PREDECESSOR_MISMATCH"))

    if not isinstance(generation, int) or generation != predecessor.get("generation", -1) + 1:
        errors.append(_finding("LINEAGE_GENERATION_MISMATCH"))

    return {"valid": not errors, "errors": errors}


def _finding(code: str, **details: Any) -> dict:
    finding = {"code": code}
    if details:
        finding["details"] = details
    return finding
