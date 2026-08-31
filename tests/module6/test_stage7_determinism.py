"""
Module 6 Stage 7 Test Suite — Determinism.
"""

import unittest
from src.module6.evolution.state import create_initial_evolutionary_state
from src.module6.resolution import (
    Stage7CompilerResolver,
    serialize_compilation_context,
)


class TestStage7Determinism(unittest.TestCase):
    """Tests enforcing byte-identical output for identical resolution inputs."""

    def setUp(self) -> None:
        self.ge0 = create_initial_evolutionary_state()

    def test_resolution_byte_identical_determinism(self) -> None:
        """Req 31: Identical inputs produce byte-identical JSON serialized output."""
        ctx1 = Stage7CompilerResolver.resolve_effective_context(self.ge0)
        ctx2 = Stage7CompilerResolver.resolve_effective_context(self.ge0)

        ser1 = serialize_compilation_context(ctx1)
        ser2 = serialize_compilation_context(ctx2)

        self.assertEqual(ser1, ser2)
        self.assertEqual(ctx1.context_hash, ctx2.context_hash)


if __name__ == "__main__":
    unittest.main()
