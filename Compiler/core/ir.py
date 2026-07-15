"""Immutable semantic model for Project Permanence contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping


def empty_extensions() -> Mapping[str, Any]:
    """Return an immutable empty extension mapping."""
    return MappingProxyType({})


@dataclass(frozen=True)
class IdentityIR:
    id: str
    title: str
    version: str


@dataclass(frozen=True)
class AuthorityIR:
    class_type: str
    source: str
    authoritative: bool = False


@dataclass(frozen=True)
class ContextIR:
    scope: str


@dataclass(frozen=True)
class ConditionIR:
    id: str
    expression: str


@dataclass(frozen=True)
class OperationIR:
    id: str
    target: str


@dataclass(frozen=True)
class InvariantIR:
    id: str
    severity: str


@dataclass(frozen=True)
class FailureIR:
    id: str
    action: str


@dataclass(frozen=True)
class OutputIR:
    id: str
    format: str


@dataclass(frozen=True)
class CompatibilityIR:
    minimum_version: str


@dataclass(frozen=True)
class EvidenceIR:
    mechanism: str


@dataclass(frozen=True)
class ContractIR:
    schema_version: str
    identity: IdentityIR
    authority: AuthorityIR
    context: ContextIR

    preconditions: tuple[ConditionIR, ...] = ()
    operations: tuple[OperationIR, ...] = ()
    postconditions: tuple[ConditionIR, ...] = ()
    invariants: tuple[InvariantIR, ...] = ()
    failures: tuple[FailureIR, ...] = ()
    outputs: tuple[OutputIR, ...] = ()

    compatibility: CompatibilityIR | None = None
    evidence: EvidenceIR | None = None

    extensions: Mapping[str, Any] = field(
        default_factory=empty_extensions
    )