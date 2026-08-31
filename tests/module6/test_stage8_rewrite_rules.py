"""
Module 6 Stage 8 Test Suite — Canonical Rewrite Rules.
"""

import unittest
from src.module4.circuit_ir.model import (
    QubitRef,
    GateOperation,
    LogicalGateType,
)
from src.module6.optimization.rules import CanonicalRewriteRules


class TestStage8RewriteRules(unittest.TestCase):
    """Tests for canonical algebraic rewrite rules."""

    def setUp(self) -> None:
        self.q0 = QubitRef("r0", 0)
        self.q1 = QubitRef("r0", 1)
        self.vocab = ("CNOT", "TOFFOLI", "X")

    def test_x_x_cancellation(self) -> None:
        """Req 7, 24: X X -> I self-inverse cancellation."""
        gates = [
            GateOperation(gate_type=LogicalGateType.X, target_qubit=self.q0, operation_index=0),
            GateOperation(gate_type=LogicalGateType.X, target_qubit=self.q0, operation_index=1),
        ]
        res = CanonicalRewriteRules.apply_canonical_rewrites(gates, self.vocab)
        self.assertEqual(len(res), 0)

    def test_cnot_cnot_cancellation(self) -> None:
        """Req 7, 24: CNOT CNOT -> I self-inverse cancellation."""
        gates = [
            GateOperation(gate_type=LogicalGateType.CNOT, target_qubit=self.q1, control_qubits=(self.q0,), operation_index=0),
            GateOperation(gate_type=LogicalGateType.CNOT, target_qubit=self.q1, control_qubits=(self.q0,), operation_index=1),
        ]
        res = CanonicalRewriteRules.apply_canonical_rewrites(gates, self.vocab)
        self.assertEqual(len(res), 0)

    def test_non_matching_gates_preserved(self) -> None:
        """Req 7: Non-adjacent or non-matching gates are preserved."""
        gates = [
            GateOperation(gate_type=LogicalGateType.X, target_qubit=self.q0, operation_index=0),
            GateOperation(gate_type=LogicalGateType.X, target_qubit=self.q1, operation_index=1),
        ]
        res = CanonicalRewriteRules.apply_canonical_rewrites(gates, self.vocab)
        self.assertEqual(len(res), 2)


if __name__ == "__main__":
    unittest.main()
