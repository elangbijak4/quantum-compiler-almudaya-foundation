"""
Module 6 Stage 6 Test Suite — Stage 4 Equivalence Gate Integration.
"""

import unittest

from src.module6.classical.semantic import create_sample_adder_model
from src.module6.integration.context import CompilerContext
from src.module6.integration.result import CompilationStatus, EquivalenceStatus, EquivalenceLevel


class TestStage6Equivalence(unittest.TestCase):
    """Tests for Stage 4 Level 6 Semantic Equivalence Gate Integration."""

    def test_successful_compilation_requires_semantic_equivalence(self) -> None:
        """Req 18, 19, 25: SUCCESS status requires verified Stage 4 Level 6 Semantic Equivalence."""
        adder = create_sample_adder_model()
        ctx = CompilerContext()

        res = ctx.compile(adder)
        self.assertEqual(res.compilation_status, CompilationStatus.SUCCESS)
        self.assertEqual(res.equivalence_status, EquivalenceStatus.VERIFIED)
        self.assertEqual(res.equivalence_level, EquivalenceLevel.LEVEL_6_SEMANTIC)
        self.assertIsNotNone(res.circuit_id)


if __name__ == "__main__":
    unittest.main()
