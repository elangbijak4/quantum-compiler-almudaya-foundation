"""
Module 6 Stage 4 Unit Test Suite — Operator Equivalence.

Verifies Level 5 operator equivalence, dense matrix comparison, unitarity checks, and global phase operator overlap.
"""

import unittest
import numpy as np
from src.module4.circuit_ir.model import QuantumCircuitIR, QubitRegister, RegisterType, GateOperation, QubitRef
from src.module6 import Level5OperatorVerifier, PhaseOverlapEvaluator


class TestStage4OperatorEquivalence(unittest.TestCase):
    def setUp(self) -> None:
        reg = QubitRegister("reg", RegisterType.STATE, 1)
        q0 = QubitRef("reg", 0)

        g_x = GateOperation("X", q0, ())
        self.c1 = QuantumCircuitIR("circ_x1", [reg], [g_x])

        g_x_a = GateOperation("X", q0, ())
        g_x_b = GateOperation("X", q0, ())
        self.c_id = QuantumCircuitIR("circ_id", [reg], [g_x_a, g_x_b])

    def test_01_operator_identical(self) -> None:
        """Positive test: OPERATOR_IDENTICAL for byte-identical & matrix-identical circuits."""
        status, details = Level5OperatorVerifier.evaluate_operator_equivalence(self.c1, self.c1)
        self.assertEqual(status, "OPERATOR_IDENTICAL")
        self.assertTrue(details["u1_is_unitary"])

    def test_02_operator_equivalent_not_syntactically_identical(self) -> None:
        """Positive test: OPERATOR_EQUIVALENT for semantically identical but syntactically different circuits."""
        # X X X is semantically X
        reg = QubitRegister("reg", RegisterType.STATE, 1)
        q0 = QubitRef("reg", 0)
        g_x = GateOperation("X", q0, ())
        c_xxx = QuantumCircuitIR("circ_xxx", [reg], [g_x, g_x, g_x])

        status, details = Level5OperatorVerifier.evaluate_operator_equivalence(self.c1, c_xxx)
        self.assertEqual(status, "OPERATOR_EQUIVALENT")
        self.assertFalse(details["is_syntactically_identical"])

    def test_03_operator_global_phase_overlap(self) -> None:
        """Positive test: PhaseOverlapEvaluator.operator_phase_overlap trace criterion."""
        u1 = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=complex)
        u2 = np.array([[-1.0, 0.0], [0.0, -1.0]], dtype=complex)  # -I (global phase pi)

        overlap, frob_res, is_exact, is_phase, phase_factor = PhaseOverlapEvaluator.operator_phase_overlap(u1, u2)
        self.assertFalse(is_exact)
        self.assertTrue(is_phase)
        self.assertAlmostEqual(overlap, 1.0, places=10)
        self.assertAlmostEqual(phase_factor, -1.0, places=10)


if __name__ == "__main__":
    unittest.main()
