"""Deterministic contextual runway compiler contract tests."""

from __future__ import annotations

import copy
import hashlib
import json
import unittest
from pathlib import Path

from Compiler.compiler import (
    compile_context_runway,
    diff_context_runways,
    hash_context_runway,
    validate_context_runway,
    verify_runway_lineage,
)


FIXTURE = Path(__file__).parents[1] / "examples" / "context-runway.json"


class ContextRunwayCompilerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.source = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_same_input_produces_byte_identical_complete_outputs(self) -> None:
        first = compile_context_runway(self.source)
        second = compile_context_runway(copy.deepcopy(self.source))

        self.assertEqual(first, second)
        self.assertEqual(first["canonical_json"].encode(), second["canonical_json"].encode())
        self.assertEqual(first["portable_markdown"].encode(), second["portable_markdown"].encode())
        self.assertEqual(first["source_manifest"], second["source_manifest"])
        self.assertEqual(first["validation_report"], second["validation_report"])
        self.assertEqual(first["predecessor_diff"], second["predecessor_diff"])
        self.assertEqual(first["manifest_hash"], hash_context_runway(self.source))

        manifest = json.dumps(
            {
                "payload": json.loads(first["canonical_json"]),
                "source_hashes": self.source["source_hashes"],
            },
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        self.assertEqual(
            first["manifest_hash"],
            hashlib.sha256(manifest.encode("utf-8")).hexdigest(),
        )

    def test_portable_markdown_preserves_governed_identity_and_sources(self) -> None:
        output = compile_context_runway(self.source)

        self.assertIn("schema: mnemosyne.context-runway/1.0", output["portable_markdown"])
        self.assertIn("identity_id: ariadne", output["portable_markdown"])
        self.assertIn("project_id: project-infinitum", output["portable_markdown"])
        self.assertIn("scope_key: architecture", output["portable_markdown"])
        self.assertIn("# Decisions in Force", output["portable_markdown"])
        self.assertEqual(output["validation_report"]["valid"], True)

    def test_invalid_schema_and_secret_content_are_rejected_without_echo(self) -> None:
        invalid = copy.deepcopy(self.source)
        invalid["payload"]["schema"] = "mnemosyne.context-runway/2.0"
        report = validate_context_runway(invalid)
        self.assertFalse(report["valid"])
        self.assertIn("UNSUPPORTED_SCHEMA", [item["code"] for item in report["errors"]])

        secret_value = "Bearer abcdefghijklmnopqrstuvwxyz123456"
        secret = copy.deepcopy(self.source)
        secret["payload"]["operational_state"] = secret_value
        report = validate_context_runway(secret)
        serialized = json.dumps(report, sort_keys=True)
        self.assertFalse(report["valid"])
        self.assertIn("PROHIBITED_SECRET_CONTENT", serialized)
        self.assertNotIn(secret_value, serialized)

    def test_source_hash_verification_is_deterministic_and_fail_closed(self) -> None:
        report = validate_context_runway(self.source)
        self.assertTrue(report["valid"])

        invalid = copy.deepcopy(self.source)
        invalid["sources"][0]["content"] = "changed source bytes"
        report = validate_context_runway(invalid)
        self.assertFalse(report["valid"])
        self.assertIn("SOURCE_HASH_MISMATCH", [item["code"] for item in report["errors"]])

    def test_lineage_requires_exact_tuple_generation_and_predecessor(self) -> None:
        predecessor = copy.deepcopy(self.source["payload"])
        predecessor["runway_id"] = "rwy_previous"
        predecessor["generation"] = 11
        predecessor["predecessor_runway_id"] = "rwy_genesis"
        current = self.source["payload"]

        self.assertEqual(
            verify_runway_lineage(current, predecessor),
            {"valid": True, "errors": []},
        )

        wrong = copy.deepcopy(predecessor)
        wrong["scope_key"] = "default"
        report = verify_runway_lineage(current, wrong)
        self.assertFalse(report["valid"])
        self.assertIn("LINEAGE_SCOPE_MISMATCH", [item["code"] for item in report["errors"]])

    def test_diff_reports_semantic_payload_changes_without_authority_decisions(self) -> None:
        predecessor = copy.deepcopy(self.source["payload"])
        predecessor["generation"] = 11
        predecessor["runway_id"] = "rwy_previous"
        predecessor["predecessor_runway_id"] = "rwy_genesis"
        predecessor["next_actions"] = []

        diff = diff_context_runways(predecessor, self.source["payload"])
        self.assertEqual(diff["from_runway_id"], "rwy_previous")
        self.assertEqual(diff["to_runway_id"], self.source["payload"]["runway_id"])
        self.assertIn("next_actions", diff["changed_fields"])
        self.assertNotIn("authority", json.dumps(diff).lower())


if __name__ == "__main__":
    unittest.main()
