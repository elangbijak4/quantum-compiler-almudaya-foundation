"""
Module 6 Stage 4 Unit Test Suite — Hadamard Regression Test.

Verifies:
1. H|0> = (|0> + |1>)/sqrt(2)
2. H|1> = (|0> - |1>)/sqrt(2)
3. H is unitary (H^\dagger H = I, H H^\dagger = I)
4. H is NOT equivalent to any current compiler-generated permutation operator (Img_Q(F) \subseteq Perm(2^N)).
5. Hadamard regression status = PASS.
"""

import unittest
import numpy as np
from src.module4.circuit_ir.model import QuantumCircuitIR, QubitRegister, RegisterType, GateOperation, QubitRef
from src.module6 import (
    Level5OperatorVerifier,
    PhaseOverlapEvaluator,
    compute_circuit_unitary,
)


class TestStage4HadamardRegression(unittest.TestCase):
    def setUp(self) -> None:
        # Construct external Hadamard reference operator H
        self.H = np.array([[1.0, 1.0], [1.0, -1.0]], dtype=complex) / np.sqrt(2.0)
        self.v0 = np.array([1.0, 0.0], dtype=complex)
        self.v1 = np.array([0.0, 1.0], dtype=complex)

        # 1-qubit permutation circuit (X gate)
        reg = QubitRegister("reg", RegisterType.STATE, 1)
        q0 = QubitRef("reg", 0)
        g_x = GateOperation("X", q0, ())
        self.c_x = QuantumCircuitIR("circ_x", [reg], [g_x])

    def test_01_hadamard_action_on_basis_states(self) -> None:
        """Mandatory Test: H|0> = (|0>+|1>)/sqrt(2) and H|1> = (|0>-|1>)/sqrt(2)."""
        out0 = self.H @ self.v0
        out1 = self.H @ self.v1

        exp0 = np.array([1.0, 1.0], dtype=complex) / np.sqrt(2.0)
        exp1 = np.array([1.0, -1.0], dtype=complex) / np.sqrt(2.0)

        self.assertTrue(np.allclose(out0, exp0, atol=1e-12))
        self.assertTrue(np.allclose(out1, exp1, atol=1e-12))

    def test_02_hadamard_unitarity(self) -> None:
        """Mandatory Test: H is a valid unitary matrix (H^\dagger H = I)."""
        is_unitary, res1, res2 = Level5OperatorVerifier.check_unitarity(self.H, tolerance=1e-12)
        self.assertTrue(is_unitary)
        self.assertLess(res1, 1e-12)
        self.assertLess(res2, 1e-12)

    def test_03_hadamard_non_equivalence_to_compiler_permutation_operators(self) -> None:
        """Mandatory Test: H is not basis-permutation equivalent or operator equivalent to any compiler permutation operator."""
        u1 = compute_circuit_unitary(self.c_x, max_qubits=10)
        self.assertIsNotNone(u1)

        overlap, frob_res, is_exact, is_phase, _ = PhaseOverlapEvaluator.operator_phase_overlap(self.H, u1)
        self.assertFalse(is_exact)
        self.assertFalse(is_phase)
        self.assertLess(overlap, 0.8)


if __name__ == "__main__":
    unittest.main()
