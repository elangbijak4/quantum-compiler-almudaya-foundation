"""
Module 6 Stage 7 Test Suite — Stage 4 Level 6 Semantic Equivalence Integration.
"""

import unittest
from src.module6.evolution.state import create_initial_evolutionary_state
from src.module6.classical.semantic import create_sample_adder_model
from src.module6.resolution.resolver import Stage7CompilerResolver
from src.module6.integration.result import CompilationStatus, EquivalenceStatus


class TestStage7SemanticEquivalence(unittest.TestCase):
    """Tests for Level 6 Semantic Equivalence Integration during resolution compilation."""

    def setUp(self) -> None:
        self.ge0 = create_initial_evolutionary_state()
        self.adder = create_sample_adder_model()

    def test_successful_compilation_requires_level6_semantic_equivalence(self) -> None:
        """Req 22: Compilation SUCCESS status requires verified Stage 4 Level 6 Semantic Equivalence."""
        res = Stage7CompilerResolver.compile_with_resolution(
            model=self.adder,
            evolution_state=self.ge0,
        )
        self.assertEqual(res.compilation_status, CompilationStatus.SUCCESS)
        self.assertEqual(res.equivalence_status, EquivalenceStatus.VERIFIED)
        self.assertIsNotNone(res.circuit_id)


if __name__ == "__main__":
    unittest.main()
