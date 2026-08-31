"""
Module 6 Stage 3 Unit Test Suite — Operator Invariants & Algebraic Structure.

Verifies computational-basis permutation invariant, real amplitude invariant, superposition capability,
composition closure, inverse closure, and identity element detection.
"""

import unittest
import numpy as np
from src.module6 import (
    AlgorithmFamilyGenerator,
    CompilerMapper,
    PermutationInvariantAnalyzer,
    RealAmplitudeInvariantAnalyzer,
    SuperpositionCapabilityAnalyzer,
    CompositionClosureAnalyzer,
    InverseClosureAnalyzer,
    IdentityElementAnalyzer,
    StructuralInvariantAnalyzer,
    BoundClassification,
)


class TestStage3OperatorInvariants(unittest.TestCase):
    def setUp(self) -> None:
        self.family = AlgorithmFamilyGenerator.generate_family("identity_family", size=2)
        self.models = list(self.family.models)
        self.programs = list(self.family.programs)
        self.circuits = [CompilerMapper.map_classical_model(m, p) for m, p in zip(self.models, self.programs)]

    def test_01_permutation_invariant_analysis(self) -> None:
        """Positive test: Verification that all compiler unitaries are computational-basis permutation matrices."""
        status, cls_type, holds = PermutationInvariantAnalyzer.analyze_permutation_invariant(self.circuits)
        self.assertEqual(status, "FORMALLY_ESTABLISHED")
        self.assertEqual(cls_type, BoundClassification.FORMAL_THEOREM)
        self.assertTrue(holds)

    def test_02_real_amplitude_invariant_analysis(self) -> None:
        """Positive test: Verification that all compiler unitaries have purely real matrix entries."""
        status, cls_type, holds = RealAmplitudeInvariantAnalyzer.analyze_real_amplitude_invariant(self.circuits)
        self.assertEqual(status, "FORMALLY_ESTABLISHED")
        self.assertEqual(cls_type, BoundClassification.FORMAL_THEOREM)
        self.assertTrue(holds)

    def test_03_superposition_capability_test(self) -> None:
        """Positive test: Verification that compiler circuits do not generate nontrivial superpositions."""
        status, gen_sup, details = SuperpositionCapabilityAnalyzer.test_superposition_capability(self.circuits)
        self.assertEqual(status, "PROVEN_NOT_GENERATING")
        self.assertFalse(gen_sup)

    def test_04_composition_and_inverse_closure(self) -> None:
        """Positive test: Verification of permutation group composition and inverse closure."""
        comp_status, _, _ = CompositionClosureAnalyzer.analyze_composition_closure(self.circuits)
        inv_status, _, _ = InverseClosureAnalyzer.analyze_inverse_closure(self.circuits)
        id_status, _, _ = IdentityElementAnalyzer.analyze_identity_element(self.circuits)

        self.assertIn("CLOSED", comp_status)
        self.assertIn("CLOSED", inv_status)
        self.assertEqual(id_status, "FOUND")

    def test_05_structural_invariant_master_analyzer(self) -> None:
        """Positive test: Master StructuralInvariantAnalyzer runs all checks successfully."""
        res = StructuralInvariantAnalyzer.analyze_structural_invariants(self.circuits)
        self.assertEqual(res.permutation_invariant_status, "FORMALLY_ESTABLISHED")
        self.assertEqual(res.real_amplitude_status, "FORMALLY_ESTABLISHED")
        self.assertEqual(res.superposition_status, "PROVEN_NOT_GENERATING")
        self.assertFalse(res.superposition_generates)


if __name__ == "__main__":
    unittest.main()
