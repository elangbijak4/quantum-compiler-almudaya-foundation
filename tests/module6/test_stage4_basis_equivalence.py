"""
Module 6 Stage 4 Unit Test Suite — Computational-Basis Equivalence.

Verifies Level 3 basis equivalence, exhaustive vs sampled limit, and inconclusive status.
"""

import unittest
from src.module4.circuit_ir.model import QuantumCircuitIR, QubitRegister, RegisterType, GateOperation, QubitRef
from src.module6 import BasisEquivalenceEvaluator


class TestStage4BasisEquivalence(unittest.TestCase):
    def setUp(self) -> None:
        reg = QubitRegister("reg", RegisterType.STATE, 2)
        q0 = QubitRef("reg", 0)
        q1 = QubitRef("reg", 1)

        g1 = GateOperation("X", q0, ())
        g2 = GateOperation("X", q1, ())

        # Circuit A: X(0), X(1)
        self.cA = QuantumCircuitIR("circ_x0_x1", [reg], [g1, g2])
        # Circuit B: X(1), X(0) (commute, basis equivalent)
        self.cB = QuantumCircuitIR("circ_x1_x0", [reg], [g2, g1])
        # Circuit C: X(0) only (not basis equivalent)
        self.cC = QuantumCircuitIR("circ_x0", [reg], [g1])

    def test_01_exhaustive_basis_equivalence(self) -> None:
        """Positive test: Exhaustive basis equivalence enumeration."""
        is_eq, status, details = BasisEquivalenceEvaluator.evaluate_basis_equivalence(self.cA, self.cB, exhaustive_limit=1024)
        self.assertTrue(is_eq)
        self.assertEqual(status, "BASIS_EQUIVALENT")
        self.assertTrue(details["exhaustive"])
        self.assertEqual(details["basis_dimension"], 4)

    def test_02_basis_non_equivalence(self) -> None:
        """Negative test: Basis non-equivalence detection."""
        is_eq, status, details = BasisEquivalenceEvaluator.evaluate_basis_equivalence(self.cA, self.cC, exhaustive_limit=1024)
        self.assertFalse(is_eq)
        self.assertEqual(status, "BASIS_NON_EQUIVALENT")
        self.assertFalse(details["equivalent_on_tested"])

    def test_03_non_exhaustive_basis_inconclusive(self) -> None:
        """Positive test: Non-exhaustive basis sampling returns BASIS_INCONCLUSIVE when limit < basis dimension."""
        # 2 qubits => 4 basis states. Set limit = 2 (non-exhaustive)
        is_eq, status, details = BasisEquivalenceEvaluator.evaluate_basis_equivalence(self.cA, self.cB, exhaustive_limit=2)
        self.assertFalse(is_eq)
        self.assertEqual(status, "BASIS_INCONCLUSIVE")
        self.assertFalse(details["exhaustive"])
        self.assertEqual(details["basis_states_tested"], 2)


if __name__ == "__main__":
    unittest.main()
