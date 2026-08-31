"""
Module 6 Stage 4 Unit Test Suite — Mapping Semantic Preservation.

Verifies A1 \equiv_C A2 => F(A1) \equiv_Q F(A2) preservation evaluation.
"""

import unittest
from src.module6 import (
    AlgorithmFamilyGenerator,
    CompilerMapper,
    MappingPreservationEvaluator,
    ClassicalEquivalenceEvaluator,
)


class TestStage4MappingPreservation(unittest.TestCase):
    def setUp(self) -> None:
        fam = AlgorithmFamilyGenerator.generate_family("bit_flip_family", size=2)
        self.models = list(fam.models)
        self.programs = list(fam.programs)
        self.circuits = [CompilerMapper.map_classical_model(m, p) for m, p in zip(self.models, self.programs)]

    def test_01_classical_equivalence_evaluation(self) -> None:
        """Positive test: ClassicalEquivalenceEvaluator on same model."""
        is_c_eq, status, details = ClassicalEquivalenceEvaluator.evaluate_classical_equivalence(self.models[0], self.models[0])
        self.assertTrue(is_c_eq)
        self.assertEqual(status, "CLASSICALLY_EQUIVALENT")

    def test_02_mapping_preservation_evaluation(self) -> None:
        """Positive test: MappingPreservationEvaluator returns PRESERVED for classically equivalent algorithms."""
        report = MappingPreservationEvaluator.evaluate_preservation(
            self.models[0], self.models[0], self.circuits[0], self.circuits[0]
        )
        self.assertEqual(report.preservation_status, "PRESERVED")
        self.assertEqual(report.classical_equivalence, "CLASSICALLY_EQUIVALENT")
        self.assertIsNone(report.counterexample_witness)


if __name__ == "__main__":
    unittest.main()
