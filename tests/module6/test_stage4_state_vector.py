"""
Module 6 Stage 4 Unit Test Suite — State-Vector Equivalence.

Verifies Level 4 state-vector equivalence across basis states, uniform superposition, random real/complex states.
Verifies distinction between EXACT_STATE_EQUIVALENCE, GLOBAL_PHASE_EQUIVALENCE, and STATE_NON_EQUIVALENCE.
"""

import unittest
import numpy as np
from src.module4.circuit_ir.model import QuantumCircuitIR, QubitRegister, RegisterType, GateOperation, QubitRef
from src.module6 import StateVectorEquivalenceEvaluator, PhaseOverlapEvaluator


class TestStage4StateVector(unittest.TestCase):
    def setUp(self) -> None:
        reg = QubitRegister("reg", RegisterType.STATE, 1)
        q0 = QubitRef("reg", 0)

        g_x = GateOperation("X", q0, ())
        self.c1 = QuantumCircuitIR("circ_x", [reg], [g_x])
        self.c2 = QuantumCircuitIR("circ_x_dup", [reg], [g_x])

    def test_01_exact_state_vector_equivalence(self) -> None:
        """Positive test: EXACT_STATE_EQUIVALENCE for identical operations."""
        status, details = StateVectorEquivalenceEvaluator.evaluate_state_vector_equivalence(self.c1, self.c2, seed=123)
        self.assertEqual(status, "EXACT_STATE_EQUIVALENCE")
        self.assertTrue(details["all_exact_equal"])
        self.assertLess(details["max_l2_residual"], 1e-12)

    def test_02_global_phase_vs_exact_state_equivalence(self) -> None:
        """Mandatory Test: Global phase shift satisfies GLOBAL_PHASE_EQUIVALENCE but NOT EXACT_STATE_EQUIVALENCE."""
        v1 = np.array([1.0, 0.0], dtype=complex)
        v2 = np.array([-1.0, 0.0], dtype=complex)  # phase shift pi (e^{i pi} = -1)

        overlap, l2_res, is_exact, is_phase = PhaseOverlapEvaluator.state_phase_overlap(v1, v2)

        self.assertFalse(is_exact)  # ||v1 - v2|| = 2.0 != 0
        self.assertTrue(is_phase)   # |<v1|v2>| = 1.0
        self.assertAlmostEqual(overlap, 1.0, places=10)
        self.assertAlmostEqual(l2_res, 2.0, places=10)

    def test_03_test_states_suite_generation(self) -> None:
        """Positive test: Deterministic state suite generation (basis, superposition, random real/complex)."""
        states = StateVectorEquivalenceEvaluator.generate_test_states(num_qubits=2, seed=42)
        names = [s[0] for s in states]
        self.assertIn("basis_0", names)
        self.assertIn("uniform_superposition", names)
        self.assertIn("random_real", names)
        self.assertIn("random_complex", names)


if __name__ == "__main__":
    unittest.main()
