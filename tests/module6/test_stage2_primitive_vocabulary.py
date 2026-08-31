"""
Module 6 Stage 2 Unit Test Suite — Primitive Gate Vocabulary Analysis.

Tests PrimitiveVocabularyAnalyzer distinguishing <G_primitive> reachability from compiler image Img(F).
"""

import unittest
from src.module6 import (
    TargetCatalogBuilder,
    PrimitiveVocabularyAnalyzer,
    PrimitiveVocabularyReachabilityStatus,
)


class TestStage2PrimitiveVocabulary(unittest.TestCase):
    def setUp(self) -> None:
        self.targets = TargetCatalogBuilder.build_default_target_operators()
        self.target_dict = {t.target_id: t for t in self.targets}

    def test_01_primitive_gate_expressible(self) -> None:
        """Positive test: Pauli-X, CNOT, TOFFOLI are expressible within primitive gate vocabulary <G_primitive>."""
        x_target = self.target_dict["target_X"]
        res = PrimitiveVocabularyAnalyzer.analyze_target_vocabulary(x_target)
        self.assertEqual(res.reachability_status, PrimitiveVocabularyReachabilityStatus.EXPRESSIBLE)
        self.assertTrue(res.in_primitive_closure)

    def test_02_superposition_hadamard_not_expressible_in_vocabulary(self) -> None:
        """Positive test: Hadamard H gate (non-binary/superposition matrix) is NOT expressible in <G_primitive>."""
        h_target = self.target_dict["target_H"]
        res = PrimitiveVocabularyAnalyzer.analyze_target_vocabulary(h_target)
        self.assertEqual(res.reachability_status, PrimitiveVocabularyReachabilityStatus.NOT_EXPRESSIBLE_IN_PRIMITIVE_VOCABULARY)
        self.assertFalse(res.in_primitive_closure)

    def test_03_phase_gate_not_expressible_in_vocabulary(self) -> None:
        """Positive test: Phase S gate (complex entries) is NOT expressible in <G_primitive>."""
        s_target = self.target_dict["target_S"]
        res = PrimitiveVocabularyAnalyzer.analyze_target_vocabulary(s_target)
        self.assertEqual(res.reachability_status, PrimitiveVocabularyReachabilityStatus.NOT_EXPRESSIBLE_IN_PRIMITIVE_VOCABULARY)
        self.assertFalse(res.in_primitive_closure)


if __name__ == "__main__":
    unittest.main()
