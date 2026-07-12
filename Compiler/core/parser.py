"""Lower validated source mappings into immutable Contract IR."""

from __future__ import annotations

from typing import Any, Mapping

from Compiler.core.ir import (
    AuthorityIR,
    ContextIR,
    ContractIR,
    IdentityIR,
    InvariantIR,
)


def parse_contract(source: Mapping[str, Any]) -> ContractIR:
    """Convert a validated source mapping into ContractIR."""

    identity = IdentityIR(
        id=str(source["identity"]["id"]),
        title=str(source["identity"]["title"]),
        version=str(source["identity"]["version"]),
    )

    authority = AuthorityIR(
        class_type=str(source["authority"]["class"]),
        source=str(source["authority"]["source"]),
        authoritative=bool(source["authority"]["authoritative"]),
    )

    context = ContextIR(
        scope=str(source["context"]["scope"]),
    )

    invariants = tuple(
        InvariantIR(
            id=str(item["id"]),
            severity=str(item["severity"]),
        )
        for item in source.get("invariants", ())
    )

    return ContractIR(
        schema_version=str(source["schema"]),
        identity=identity,
        authority=authority,
        context=context,
        invariants=invariants,
    )