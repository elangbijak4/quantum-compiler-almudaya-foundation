"""
Module 6 Stage 3 Unit Test Suite — Codomain Bounds & Mapping Complexity.

Verifies codomain descriptors, qubit bounds n_Q(A), circuit operation count L(A), ancilla bounds a(A), and image containment.
"""

import unittest
from src.module6 import (
    AlgorithmFamilyGenerator,
    CompilerMapper,
    CodomainBoundsAnalyzer,
    ImageBoundsAnalyzer,
    BoundClassification,
    CardinalityType,
)


class TestStage3CodomainBounds(unittest.TestCase):
    def setUp(self) -> None:
        self.family = AlgorithmFamilyGenerator.generate_family("reversible_permutation_family", size=2)
        self.models = list(self.family.models)
        self.programs = list(self.family.programs)
        self.circuits = [CompilerMapper.map_classical_model(m, p) for m, p in zip(self.models, self.programs)]

    def test_01_codomain_qubit_and_size_bounds(self) -> None:
        """Positive test: Verification of qubit bounds, gate size bounds, and ancilla bounds."""
        desc, card, records = CodomainBoundsAnalyzer.analyze_codomain(self.models, self.circuits)
        self.assertEqual(len(records), 2)
        for r in records:
            self.assertGreater(r.logical_qubit_count, 0)
            self.assertGreaterEqual(r.logical_gate_count, 0)
            self.assertGreaterEqual(r.ancilla_qubit_count, 0)

    def test_02_image_containment_bounds(self) -> None:
        """Positive test: Verification of structural Img(F) and semantic Img_Q(F) containment bounds."""
        struct_b, sem_b, card_b = ImageBoundsAnalyzer.analyze_image_bounds(
            sample_size=2, circuit_image_size=2, operator_image_size=2
        )
        self.assertEqual(struct_b.classification, BoundClassification.FORMAL_THEOREM)
        self.assertEqual(sem_b.classification, BoundClassification.FORMAL_THEOREM)
        self.assertTrue(struct_b.is_formally_proven)
        self.assertTrue(sem_b.is_formally_proven)
        self.assertIn("Perm(2^N)", sem_b.formal_expression)


if __name__ == "__main__":
    unittest.main()
