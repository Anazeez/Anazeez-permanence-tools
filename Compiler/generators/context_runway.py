"""Deterministic portable Markdown generator for contextual runways."""

from __future__ import annotations

from typing import Any, Mapping

from Compiler.core.context_runway import canonical_json


def generate_context_runway_markdown(payload: Mapping[str, Any], manifest_hash: str) -> str:
    """Render the portable, secondary representation without hidden defaults."""

    predecessor = payload.get("predecessor_runway_id") or ""
    source_invocation = payload.get("source_invocation_id") or ""
    return (
        "---\n"
        f"id: {payload['runway_id']}\n"
        f"title: {payload['identity_id']} {payload['scope_key']} runway {payload['generation']}\n"
        f"created: {payload['created_at']}\n"
        "status: sealed\n"
        f"sha256: {manifest_hash}\n"
        f"parents: [{predecessor}]\n"
        f"sources: [invocation:{source_invocation}]\n"
        f"tags: [continuity, runway, {payload['identity_id']}]\n"
        f"schema: {payload['schema']}\n"
        f"identity_id: {payload['identity_id']}\n"
        f"project_id: {payload['project_id']}\n"
        f"scope_key: {payload['scope_key']}\n"
        f"generation: {payload['generation']}\n"
        "---\n"
        "# Objective\n"
        f"{payload['objective']}\n"
        "# Current Operational State\n"
        f"{payload['operational_state']}\n"
        "# Decisions in Force\n"
        f"{_render_list(payload['decisions_in_force'])}\n"
        "# Open Threads\n"
        f"{_render_list(payload['open_threads'])}\n"
        "# Relevant Skills\n"
        f"{_render_list(payload['mounted_skills'])}\n"
        "# Relevant Files\n"
        f"{_render_list(payload['relevant_files'])}\n"
        "# Next Actions\n"
        f"{_render_list(payload['next_actions'])}\n"
        "# Integrity Notes\n"
        f"{_render_list(payload['integrity_warnings'])}\n"
    )


def _render_list(items: list) -> str:
    if not items:
        return "- None"
    return "\n".join(
        "- " + (item if isinstance(item, str) else canonical_json(item))
        for item in items
    )
