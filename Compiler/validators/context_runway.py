"""Fail-closed contextual runway validation."""

from __future__ import annotations

import hashlib
import re
from typing import Any, Mapping

from Compiler.core.context_runway import RUNWAY_SCHEMA, verify_runway_lineage


MAX_PAYLOAD_BYTES = 128 * 1024
SHA256 = re.compile(r"^[a-f0-9]{64}$")
IDENTITY = re.compile(r"^[a-z0-9][a-z0-9_-]{1,63}$")
PROJECT = re.compile(r"^[a-z0-9][a-z0-9._-]{1,63}$")
SCOPE = re.compile(
    r"^(?:[a-z0-9][a-z0-9_-]{1,63}|(?:mandate|thread):[a-z0-9][a-z0-9_-]{1,63})$"
)
SECRET_KEY = re.compile(
    r"(?:^|_)(?:api_?key|access_?token|auth_?token|password|private_?key|cookie|secret)(?:$|_)",
    re.IGNORECASE,
)
SECRET_VALUE = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", re.IGNORECASE),
    re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{20,}", re.IGNORECASE),
    re.compile(r"\b(?:gh[opusr]|sk|pk)_[A-Za-z0-9_-]{20,}\b", re.IGNORECASE),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
)
REQUIRED_ARRAYS = (
    "decisions_in_force",
    "open_threads",
    "next_actions",
    "mounted_skills",
    "relevant_agents",
    "relevant_files",
    "knowledge_references",
    "library_references",
    "pending_handoffs",
    "constraints",
    "prohibited_assumptions",
    "integrity_warnings",
    "source_hashes",
)


def validate_context_runway(source: Mapping[str, Any]) -> dict:
    """Validate structure, content, sources, and optional lineage."""

    errors = []
    warnings = []
    if not isinstance(source, Mapping) or not isinstance(source.get("payload"), Mapping):
        return _report([_finding("INVALID_PAYLOAD")], warnings)

    payload = source["payload"]
    if _contains_secret(source):
        return _report([_finding("PROHIBITED_SECRET_CONTENT")], warnings)

    if payload.get("schema") != RUNWAY_SCHEMA:
        errors.append(_finding("UNSUPPORTED_SCHEMA"))

    _check_pattern(payload, "identity_id", IDENTITY, errors)
    _check_pattern(payload, "project_id", PROJECT, errors)
    _check_pattern(payload, "scope_key", SCOPE, errors)

    for field in ("runway_id", "source_invocation_id", "created_at", "objective", "operational_state"):
        if not isinstance(payload.get(field), str) or not payload[field].strip():
            errors.append(_finding("MISSING_REQUIRED_FIELD", field=field))

    generation = payload.get("generation")
    if not isinstance(generation, int) or isinstance(generation, bool) or generation < 1:
        errors.append(_finding("INVALID_GENERATION"))

    for field in REQUIRED_ARRAYS:
        if not isinstance(payload.get(field), list):
            errors.append(_finding("INVALID_ARRAY_FIELD", field=field))

    payload_bytes = len(_canonical_bytes(payload))
    if payload_bytes > MAX_PAYLOAD_BYTES:
        errors.append(_finding("PAYLOAD_TOO_LARGE", bytes=payload_bytes))

    source_hashes = source.get("source_hashes")
    if not isinstance(source_hashes, list):
        errors.append(_finding("INVALID_SOURCE_HASHES"))
        source_hashes = []
    elif payload.get("source_hashes") != source_hashes:
        errors.append(_finding("SOURCE_HASH_MANIFEST_MISMATCH"))

    declared = {}
    for item in source_hashes:
        if not isinstance(item, Mapping):
            errors.append(_finding("INVALID_SOURCE_HASH"))
            continue
        source_ref = item.get("source_ref")
        digest = item.get("sha256")
        if not isinstance(source_ref, str) or not source_ref or not isinstance(digest, str) or not SHA256.fullmatch(digest):
            errors.append(_finding("INVALID_SOURCE_HASH"))
            continue
        declared[source_ref] = digest

    for item in source.get("sources", []):
        if not isinstance(item, Mapping):
            errors.append(_finding("INVALID_SOURCE"))
            continue
        source_ref = item.get("source_ref")
        content = item.get("content")
        if not isinstance(source_ref, str) or not isinstance(content, str):
            errors.append(_finding("INVALID_SOURCE"))
            continue
        observed = hashlib.sha256(content.encode("utf-8")).hexdigest()
        if declared.get(source_ref) != observed or item.get("sha256") != observed:
            errors.append(_finding("SOURCE_HASH_MISMATCH", source_ref=source_ref))

    predecessor = source.get("predecessor")
    if predecessor is not None or payload.get("generation") == 1:
        lineage = verify_runway_lineage(payload, predecessor)
        errors.extend(lineage["errors"])
    elif payload.get("predecessor_runway_id"):
        warnings.append(_finding("PREDECESSOR_NOT_SUPPLIED_FOR_OFFLINE_VERIFICATION"))

    return _report(errors, warnings)


def _canonical_bytes(value: Any) -> bytes:
    from Compiler.core.context_runway import canonical_json

    return canonical_json(value).encode("utf-8")


def _check_pattern(payload: Mapping[str, Any], field: str, pattern: re.Pattern, errors: list) -> None:
    value = payload.get(field)
    if not isinstance(value, str) or not pattern.fullmatch(value):
        errors.append(_finding("INVALID_" + field.upper(), field=field))


def _contains_secret(value: Any, key: str = "") -> bool:
    if key and SECRET_KEY.search(key):
        return True
    if isinstance(value, Mapping):
        return any(_contains_secret(item, str(name)) for name, item in value.items())
    if isinstance(value, list):
        return any(_contains_secret(item) for item in value)
    if isinstance(value, str):
        return any(pattern.search(value) for pattern in SECRET_VALUE)
    return False


def _finding(code: str, **details: Any) -> dict:
    finding = {"code": code}
    if details:
        finding["details"] = details
    return finding


def _report(errors: list, warnings: list) -> dict:
    return {"valid": not errors, "errors": errors, "warnings": warnings}
