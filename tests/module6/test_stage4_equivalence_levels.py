"""
Module 6 Stage 4 Unit Test Suite — Equivalence Hierarchy & Non-Implications.

Verifies Level 1..6 hierarchy evaluation and tests non-implications:
- Level 2 structurally different does not imply Level 5 operator non-equivalent.
- Level 5 operator equivalent does not imply Level 1 or Level 2 identity.
- Level 6 semantic equivalent does not imply Level 1 or Level 2 identity.
"""

import unittest
from src.module4.circuit_ir.model import QuantumCircuitIR, QubitRegister, RegisterType, GateOperation, QubitRef
from src.module6 import (
    SyntacticEquivalenceEvaluator,
    StructuralEquivalenceEvaluator,
    BasisEquivalenceEvaluator,
    StateVectorEquivalenceEvaluator,
    Level5OperatorVerifier,
    SemanticEquivalenceEvaluator,
    MappingAnalyzer,
    EquivalenceStatus,
)


class TestStage4EquivalenceLevels(unittest.TestCase):
    def setUp(self) -> None:
        reg1 = QubitRegister("reg", RegisterType.STATE, 1)
        q0 = QubitRef("reg", 0)

        # Circuit 1: X on qubit 0
        g1 = GateOperation("X", q0, ())
        self.c1 = QuantumCircuitIR("circ_x", [reg1], [g1])

        # Circuit 2: X followed by X twice (equivalent to Identity semantically, but different structurally)
        g2a = GateOperation("X", q0, ())
        g2b = GateOperation("X", q0, ())
        self.c2 = QuantumCircuitIR("circ_xx", [reg1], [g2a, g2b])

        # Circuit 3: Identity circuit (0 gates)
        self.c3 = QuantumCircuitIR("circ_id", [reg1], [])

    def test_01_level1_syntactic_identity(self) -> None:
        """Positive test: Level 1 syntactic identity."""
        is_syn, status, details = SyntacticEquivalenceEvaluator.evaluate_syntactic_identity(self.c1, self.c1)
        self.assertTrue(is_syn)
        self.assertEqual(status, "IDENTICAL")

        is_syn2, status2, _ = SyntacticEquivalenceEvaluator.evaluate_syntactic_identity(self.c1, self.c2)
        self.assertFalse(is_syn2)
        self.assertEqual(status2, "NOT_IDENTICAL")

    def test_02_level2_structural_equivalence(self) -> None:
        """Positive test: Level 2 structural circuit equivalence."""
        is_struct, status, details = StructuralEquivalenceEvaluator.evaluate_structural_equivalence(self.c1, self.c1)
        self.assertTrue(is_struct)
        self.assertEqual(status, "STRUCTURALLY_EQUIVALENT")

        is_struct2, status2, _ = StructuralEquivalenceEvaluator.evaluate_structural_equivalence(self.c1, self.c2)
        self.assertFalse(is_struct2)
        self.assertEqual(status2, "STRUCTURALLY_DIFFERENT")

    def test_03_non_implication_structural_different_but_operator_equivalent(self) -> None:
        """Mandatory Test: Structural difference (X X vs I) does NOT imply operator non-equivalence."""
        is_struct, s_status, _ = StructuralEquivalenceEvaluator.evaluate_structural_equivalence(self.c2, self.c3)
        self.assertFalse(is_struct)
        self.assertEqual(s_status, "STRUCTURALLY_DIFFERENT")

        op_status, details = Level5OperatorVerifier.evaluate_operator_equivalence(self.c2, self.c3)
        self.assertEqual(op_status, "OPERATOR_EQUIVALENT")

    def test_04_mapping_analyzer_quantum_pair_matrix(self) -> None:
        """Positive test: MappingAnalyzer.analyze_quantum_pair generates complete 6-level matrix."""
        report = MappingAnalyzer.analyze_quantum_pair(self.c2, self.c3)
        self.assertEqual(report.level_results["LEVEL_1_SYNTACTIC"], "NOT_IDENTICAL")
        self.assertEqual(report.level_results["LEVEL_2_STRUCTURAL"], "STRUCTURALLY_DIFFERENT")
        self.assertEqual(report.level_results["LEVEL_3_BASIS"], "BASIS_EQUIVALENT")
        self.assertEqual(report.level_results["LEVEL_5_OPERATOR"], "OPERATOR_EQUIVALENT")
        self.assertEqual(report.level_results["LEVEL_6_SEMANTIC"], "SEMANTICALLY_EQUIVALENT")
        self.assertEqual(report.final_status, EquivalenceStatus.EQUIVALENT)


if __name__ == "__main__":
    unittest.main()
