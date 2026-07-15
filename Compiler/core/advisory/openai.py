"""Advisory interface.

This module may explain, recommend, summarize, or diagnose.
It must never participate in deterministic compilation.
"""

from __future__ import annotations

from typing import Protocol


class AdvisoryProvider(Protocol):
    """Contract for advisory implementations."""

    def explain(self, message: str) -> str:
        ...