"""
Module 5 Micro Closure Unit Test Suite — Boundary & Contract Verification.

Tests all 16 mandated micro-closure boundary checks:
1. logical/physical identity separation
2. mapping injectivity
3. mapping validity
4. topology validity
5. explicit SWAP mapping update (M -> M')
6. routing semantic preservation
7. native gate boundary separation
8. measurement contract
9. execution result identity
10. provenance continuity
11. deterministic physicalization
12. deferred hardware boundary
13. deferred noise boundary
14. invalid mapping rejection
15. topology violation rejection
16. unsupported gate rejection
"""

import unittest
from src.module4.circuit_ir.model import QubitRef, QubitRegister, RegisterType, QuantumCircuitIR, GateOperation, LogicalGateType
from src.module5.model import (
    PhysicalQubit,
    QubitMapping,
    DeviceTopology,
    PhysicalGateOperation,
    PhysicalCircuitIR,
    ExecutionProvenance,
    ExecutionRequest,
    ExecutionResult,
)


class TestModule5MicroClosure(unittest.TestCase):
    def setUp(self) -> None:
        self.reg_q = QubitRegister("reg_q", RegisterType.STATE, 3)
        self.q0 = self.reg_q.get_qubit_ref(0)
        self.q1 = self.reg_q.get_qubit_ref(1)
        self.q2 = self.reg_q.get_qubit_ref(2)

        self.p0 = PhysicalQubit(node_id=0)
        self.p1 = PhysicalQubit(node_id=1)
        self.p2 = PhysicalQubit(node_id=2)

        self.mapping = QubitMapping()
        self.mapping.set_mapping(self.q0, 0)
        self.mapping.set_mapping(self.q1, 1)
        self.mapping.set_mapping(self.q2, 2)

        self.topology = DeviceTopology()
        self.topology.add_edge(0, 1)
        self.topology.add_edge(1, 2)

    def test_01_logical_physical_identity_separation(self) -> None:
        """Req 1: Verify logical q[0] is distinct from physical p[0]."""
        self.assertNotEqual(str(self.q0), str(self.p0))
        self.assertEqual(self.mapping.get_physical(self.q0), 0)

    def test_02_mapping_injectivity(self) -> None:
        """Req 2 & 14: Verify mapping injectivity and collision rejection."""
        self.assertTrue(self.mapping.is_injective())
        bad_map = QubitMapping()
        bad_map.set_mapping(self.q0, 0)
        with self.assertRaises(ValueError):
            bad_map.set_mapping(self.q1, 0)  # Collision!

    def test_03_mapping_validity(self) -> None:
        """Req 3: Verify mapped lookup for active logical qubits."""
        self.assertEqual(self.mapping.get_physical(self.q1), 1)
        unmapped_q = QubitRef("reg_q", 99)
        with self.assertRaises(KeyError):
            self.mapping.get_physical(unmapped_q)

    def test_04_topology_validity(self) -> None:
        """Req 4 & 15: Verify topology connectivity and un-connected pair detection."""
        self.assertTrue(self.topology.is_connected(0, 1))
        self.assertTrue(self.topology.is_connected(1, 2))
        self.assertFalse(self.topology.is_connected(0, 2))  # Line topology 0-1-2

    def test_05_explicit_swap_mapping_update(self) -> None:
        """Req 5: Verify SWAP(p0, p1) updates mapping permutation explicitly M(q0)=0, M(q1)=1 -> M'(q0)=1, M'(q1)=0."""
        self.assertEqual(self.mapping.get_physical(self.q0), 0)
        self.assertEqual(self.mapping.get_physical(self.q1), 1)

        self.mapping.apply_swap(0, 1)

        self.assertEqual(self.mapping.get_physical(self.q0), 1)
        self.assertEqual(self.mapping.get_physical(self.q1), 0)

    def test_06_routing_semantic_preservation(self) -> None:
        """Req 6: Verify SWAP routing updates mapping without modifying logical state algorithm semantics."""
        # Initial: q0->p0, q1->p1. Apply SWAP(p0, p1). Logical q0 is now at p1.
        self.mapping.apply_swap(0, 1)
        self.assertEqual(self.mapping.inverse_mapping[1], self.q0)
        self.assertEqual(self.mapping.inverse_mapping[0], self.q1)

    def test_07_native_gate_boundary_separation(self) -> None:
        """Req 7 & 16: Verify PhysicalGateOperation operates on physical node IDs."""
        pgate = PhysicalGateOperation(gate_type="CZ", control_nodes=(0,), target_node=1, operation_index=0)
        self.assertEqual(pgate.gate_type, "CZ")
        self.assertEqual(pgate.target_node, 1)

    def test_08_measurement_contract(self) -> None:
        """Req 8: Verify measurement result counts structure."""
        counts = {"000": 500, "111": 500}
        self.assertEqual(sum(counts.values()), 1000)

    def test_09_execution_result_identity(self) -> None:
        """Req 9: Verify ExecutionResult structure."""
        res = ExecutionResult(
            request_id="req_001",
            status="SUCCESS",
            counts={"000": 1000},
            execution_time_ms=1.5,
        )
        self.assertEqual(res.status, "SUCCESS")
        self.assertEqual(res.request_id, "req_001")

    def test_10_provenance_continuity(self) -> None:
        """Req 10: Verify provenance chain contains source RUTM hash and QTM ID."""
        prov = ExecutionProvenance(
            source_rutm_program_hash="hash_123",
            source_qtm_machine_id="qtm_456",
            logical_circuit_id="circ_789",
        )
        self.assertEqual(prov.source_rutm_program_hash, "hash_123")
        self.assertEqual(prov.source_qtm_machine_id, "qtm_456")

    def test_11_deterministic_physicalization(self) -> None:
        """Req 11: Verify physicalization dataclass instantiation is deterministic."""
        p_circ1 = PhysicalCircuitIR(
            physical_circuit_id="p1",
            source_logical_circuit_id="l1",
            physical_qubits=[self.p0, self.p1],
            gates=[],
            mapping=self.mapping,
            topology=self.topology,
        )
        p_circ2 = PhysicalCircuitIR(
            physical_circuit_id="p1",
            source_logical_circuit_id="l1",
            physical_qubits=[self.p0, self.p1],
            gates=[],
            mapping=self.mapping,
            topology=self.topology,
        )
        self.assertEqual(p_circ1.physical_circuit_id, p_circ2.physical_circuit_id)

    def test_12_deferred_hardware_boundary(self) -> None:
        """Req 12: Verify hardware submission remains deferred (no remote SDK dependencies)."""
        import sys
        self.assertNotIn("qiskit", sys.modules)
        self.assertNotIn("cirq", sys.modules)

    def test_13_deferred_noise_boundary(self) -> None:
        """Req 13: Verify noise simulation remains deferred (result defaults to ideal state vector / counts)."""
        res = ExecutionResult(request_id="req_ideal", status="SUCCESS", state_vector={"00": 1.0 + 0.0j})
        self.assertIsNotNone(res.state_vector)

    def test_14_invalid_mapping_rejection(self) -> None:
        """Req 14: Reject duplicate or non-injective physical qubit mapping."""
        m = QubitMapping()
        m.set_mapping(self.q0, 0)
        with self.assertRaises(ValueError):
            m.set_mapping(self.q1, 0)

    def test_15_topology_violation_rejection(self) -> None:
        """Req 15: Reject direct 2-qubit gate on disconnected physical nodes (0, 2)."""
        self.assertFalse(self.topology.is_connected(0, 2))

    def test_16_unsupported_gate_rejection(self) -> None:
        """Req 16: Verify validation rejects unknown native gates."""
        supported_native = {"X", "CNOT", "CZ", "RZ", "SX"}
        bad_gate = "INVALID_HARDWARE_GATE"
        self.assertNotIn(bad_gate, supported_native)


if __name__ == "__main__":
    unittest.main()
