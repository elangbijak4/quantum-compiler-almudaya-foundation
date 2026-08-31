"""
Module 6 Stage 4 Unit Test Suite — Negative Error Handling & Mandatory Non-Implication Tests.

Verifies deterministic failure handling on invalid inputs and explicitly tests required non-implications:
TEST 1: structural_difference does NOT imply semantic_difference.
TEST 2: operator_equivalence does NOT imply structural_equivalence.
TEST 3: global_phase_equivalence does NOT imply exact_state_equivalence.
TEST 4: no_observed_collision does NOT imply injectivity_proven.
TEST 5: finite_basis_testing does NOT imply universal equivalence beyond tested domain.
"""

import unittest
import numpy as np
from src.module4.circuit_ir.model import QuantumCircuitIR, QubitRegister, RegisterType, GateOperation, QubitRef
from src.module6 import (
    SyntacticEquivalenceEvaluator,
    StructuralEquivalenceEvaluator,
    BasisEquivalenceEvaluator,
    StateVectorEquivalenceEvaluator,
    Level5OperatorVerifier,
    MappingAnalyzer,
    PhaseOverlapEvaluator,
    EquivalenceStatus,
)


class TestStage4Negative(unittest.TestCase):
    def setUp(self) -> None:
        reg1 = QubitRegister("reg1", RegisterType.STATE, 1)
        reg2 = QubitRegister("reg2", RegisterType.STATE, 2)
        q1_0 = QubitRef("reg1", 0)
        q2_0 = QubitRef("reg2", 0)

        g_x1 = GateOperation("X", q1_0, ())
        g_x2 = GateOperation("X", q2_0, ())

        self.c_1q = QuantumCircuitIR("circ_1q", [reg1], [g_x1])
        self.c_2q = QuantumCircuitIR("circ_2q", [reg2], [g_x2])

    def test_01_mismatched_qubit_dimensions(self) -> None:
        """Negative test: Dimension mismatch handling returns appropriate non-equivalent status."""
        is_syn, status1, _ = SyntacticEquivalenceEvaluator.evaluate_syntactic_identity(self.c_1q, self.c_2q)
        self.assertFalse(is_syn)

        is_struct, status2, _ = StructuralEquivalenceEvaluator.evaluate_structural_equivalence(self.c_1q, self.c_2q)
        self.assertFalse(is_struct)

        is_basis, status3, _ = BasisEquivalenceEvaluator.evaluate_basis_equivalence(self.c_1q, self.c_2q)
        self.assertFalse(is_basis)

        st4, _ = StateVectorEquivalenceEvaluator.evaluate_state_vector_equivalence(self.c_1q, self.c_2q)
        self.assertEqual(st4, "STATE_NON_EQUIVALENCE")

        st5, _ = Level5OperatorVerifier.evaluate_operator_equivalence(self.c_1q, self.c_2q)
        self.assertEqual(st5, "OPERATOR_NON_EQUIVALENT")

    def test_02_non_implication_1_structural_difference_does_not_imply_semantic_difference(self) -> None:
        """Mandatory Non-Implication TEST 1: structural_difference does NOT imply semantic_difference."""
        reg = QubitRegister("reg", RegisterType.STATE, 1)
        q0 = QubitRef("reg", 0)
        g_x = GateOperation("X", q0, ())
        c_x = QuantumCircuitIR("c_x", [reg], [g_x])
        c_xxx = QuantumCircuitIR("c_xxx", [reg], [g_x, g_x, g_x])

        is_struct, _, _ = StructuralEquivalenceEvaluator.evaluate_structural_equivalence(c_x, c_xxx)
        self.assertFalse(is_struct)

        is_eq, _, _ = BasisEquivalenceEvaluator.evaluate_basis_equivalence(c_x, c_xxx)
        self.assertTrue(is_eq)

    def test_03_non_implication_2_operator_equivalence_does_not_imply_structural_equivalence(self) -> None:
        """Mandatory Non-Implication TEST 2: operator_equivalence does NOT imply structural_equivalence."""
        reg = QubitRegister("reg", RegisterType.STATE, 1)
        q0 = QubitRef("reg", 0)
        g_x = GateOperation("X", q0, ())
        c_x = QuantumCircuitIR("c_x", [reg], [g_x])
        c_xxx = QuantumCircuitIR("c_xxx", [reg], [g_x, g_x, g_x])

        st5, _ = Level5OperatorVerifier.evaluate_operator_equivalence(c_x, c_xxx)
        self.assertEqual(st5, "OPERATOR_EQUIVALENT")

        is_struct, _, _ = StructuralEquivalenceEvaluator.evaluate_structural_equivalence(c_x, c_xxx)
        self.assertFalse(is_struct)

    def test_04_non_implication_3_global_phase_does_not_imply_exact_state_equivalence(self) -> None:
        """Mandatory Non-Implication TEST 3: global_phase_equivalence does NOT imply exact_state_equivalence."""
        v1 = np.array([1.0, 0.0], dtype=complex)
        v2 = np.array([-1.0, 0.0], dtype=complex)  # phase shift e^{i pi}

        _, _, is_exact, is_phase = PhaseOverlapEvaluator.state_phase_overlap(v1, v2)
        self.assertFalse(is_exact)
        self.assertTrue(is_phase)

    def test_05_non_implication_4_no_observed_collision_does_not_imply_injectivity_proven(self) -> None:
        """Mandatory Non-Implication TEST 4: no_observed_collision does NOT imply injectivity_proven."""
        inj_status, is_proven = MappingAnalyzer.analyze_injectivity([])
        self.assertEqual(inj_status, "NO_COLLISION_OBSERVED")
        self.assertFalse(is_proven)

    def test_06_non_implication_5_finite_basis_testing_does_not_imply_universal_equivalence(self) -> None:
        """Mandatory Non-Implication TEST 5: finite basis testing does NOT imply universal equivalence beyond tested domain."""
        is_eq, status, details = BasisEquivalenceEvaluator.evaluate_basis_equivalence(self.c_1q, self.c_1q, exhaustive_limit=0)
        self.assertFalse(is_eq)
        self.assertEqual(status, "BASIS_INCONCLUSIVE")
        self.assertFalse(details["exhaustive"])


if __name__ == "__main__":
    unittest.main()
