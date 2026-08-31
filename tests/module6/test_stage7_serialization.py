"""
Module 6 Stage 7 Test Suite — Canonical JSON Serialization.
"""

import unittest
from src.module6.evolution.state import create_initial_evolutionary_state
from src.module6.resolution import (
    Stage7CompilerResolver,
    serialize_compilation_context,
    deserialize_compilation_context,
)


class TestStage7Serialization(unittest.TestCase):
    """Tests for canonical JSON serialization and round-trip deserialization."""

    def setUp(self) -> None:
        self.ge0 = create_initial_evolutionary_state()

    def test_canonical_serialization_roundtrip(self) -> None:
        """Req 32: deserialize(serialize(X)) == X verification."""
        ctx = Stage7CompilerResolver.resolve_effective_context(self.ge0)
        ser = serialize_compilation_context(ctx)
        des = deserialize_compilation_context(ser)

        self.assertEqual(des.evolution_stage, ctx.evolution_stage)
        self.assertEqual(des.evolutionary_vocabulary_hash, ctx.evolutionary_vocabulary_hash)
        self.assertEqual(des.session_id, ctx.session_id)
        self.assertEqual(des.baseline_mode, ctx.baseline_mode)
        self.assertEqual(des.effective_vocabulary, ctx.effective_vocabulary)
        self.assertEqual(des.configuration_status, ctx.configuration_status)
        self.assertEqual(des.context_hash, ctx.context_hash)


if __name__ == "__main__":
    unittest.main()
