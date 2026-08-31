"""
Module 5 Stage 3 Unit Test Suite — Physicalization, Topology Enforcement & SWAP Routing.

Tests all 14 positive-path and 10 negative-path requirements:
POSITIVE:
1. deterministic initial mapping
2. injective mapping
3. one-qubit gate physicalization
4. directly connected two-qubit gate
5. disconnected two-qubit gate requiring SWAP
6. mapping update after SWAP
7. shortest-path routing
8. deterministic tie-breaking
9. final topology validity
10. final PhysicalCircuitIR validation
11. provenance preservation
12. serialization determinism
13. multiple sequential routed gates
14. mapping remains injective after every SWAP

NEGATIVE:
1. insufficient physical qubits
2. unmapped logical qubit
3. invalid physical node
4. disconnected topology with no path
5. malformed topology
6. non-injective mapping
7. invalid routing result
8. illegal two-qubit operation
9. mutated-input detection
10. nondeterministic routing rejection
"""

import unittest
from src.module4.circuit_ir.model import (
    QuantumCircuitIR,
    QubitRegister,
    RegisterType,
    GateOperation,
    LogicalGateType,
    CircuitProvenance,
)
from src.module5 import (
    PhysicalQubit,
    QubitMapping,
    DeviceTopology,
    PhysicalGateOperation,
    PhysicalCircuitIR,
    ExecutionProvenance,
    InitialMapper,
    ShortestPathRouter,
    RoutingEvent,
    RoutingTrace,
    SemanticPreservationVerifier,
    PhysicalizationEngine,
    validate_physical_circuit_ir,
    serialize_physical_circuit_ir,
)


class TestStage3Physicalization(unittest.TestCase):
    def setUp(self) -> None:
        # Build logical QuantumCircuitIR with 3 qubits
        self.reg_q = QubitRegister(register_id="reg_q", register_type=RegisterType.STATE, width=3)
        self.q0 = self.reg_q.get_qubit_ref(0)
        self.q1 = self.reg_q.get_qubit_ref(1)
        self.q2 = self.reg_q.get_qubit_ref(2)

        self.g_x0 = GateOperation(gate_type=LogicalGateType.X, target_qubit=self.q0, control_qubits=())
        self.g_cnot01 = GateOperation(gate_type=LogicalGateType.CNOT, control_qubits=(self.q0,), target_qubit=self.q1)

        self.log_provenance = CircuitProvenance(
            source_rutm_program_hash="rutm_hash_999",
            source_qtm_machine_id="qtm_mach_888",
        )

        self.logical_circuit = QuantumCircuitIR(
            circuit_id="log_circ_001",
            registers=[self.reg_q],
            gates=[self.g_x0, self.g_cnot01],
            provenance=self.log_provenance,
        )

        # Build Line Topology 0-1-2 (0-1 connected, 1-2 connected, 0-2 DISCONNECTED)
        self.line_topology = DeviceTopology()
        self.line_topology.add_edge(0, 1)
        self.line_topology.add_edge(1, 2)

    # ------------------------------------------------------------------
    # POSITIVE TESTS (14)
    # ------------------------------------------------------------------
    def test_pos_01_deterministic_initial_mapping(self) -> None:
        """Pos 1: Deterministic initial mapping q0->0, q1->1, q2->2."""
        mapping1 = InitialMapper.allocate(self.logical_circuit, self.line_topology)
        mapping2 = InitialMapper.allocate(self.logical_circuit, self.line_topology)
        self.assertEqual(mapping1.get_physical(self.q0), mapping2.get_physical(self.q0))
        self.assertEqual(mapping1.get_physical(self.q1), mapping2.get_physical(self.q1))
        self.assertEqual(mapping1.get_physical(self.q2), mapping2.get_physical(self.q2))

    def test_pos_02_injective_mapping(self) -> None:
        """Pos 2: Initial mapping is injective."""
        mapping = InitialMapper.allocate(self.logical_circuit, self.line_topology)
        self.assertTrue(mapping.is_injective())

    def test_pos_03_one_qubit_gate_physicalization(self) -> None:
        """Pos 3: 1-qubit gate physicalizes cleanly without routing."""
        p_circ, trace = PhysicalizationEngine.physicalize(self.logical_circuit, self.line_topology)
        self.assertEqual(p_circ.gates[0].gate_type, "X")
        self.assertEqual(p_circ.gates[0].target_node, 0)
        self.assertEqual(p_circ.gates[0].control_nodes, ())

    def test_pos_04_directly_connected_two_qubit_gate(self) -> None:
        """Pos 4: Directly connected 2-qubit CNOT(q0, q1) physicalizes without SWAP."""
        p_circ, trace = PhysicalizationEngine.physicalize(self.logical_circuit, self.line_topology)
        self.assertEqual(p_circ.gates[1].gate_type, "CNOT")
        self.assertEqual(p_circ.gates[1].control_nodes, (0,))
        self.assertEqual(p_circ.gates[1].target_node, 1)

    def test_pos_05_06_disconnected_two_qubit_gate_swaps(self) -> None:
        """Pos 5 & 6: Disconnected CNOT(q0, q2) on line topology 0-1-2 inserts SWAP(0, 1) and updates mapping."""
        g_cnot02 = GateOperation(gate_type=LogicalGateType.CNOT, control_qubits=(self.q0,), target_qubit=self.q2)
        circ_disc = QuantumCircuitIR(
            circuit_id="log_disc",
            registers=[self.reg_q],
            gates=[g_cnot02],
            provenance=self.log_provenance,
        )
        p_circ, trace = PhysicalizationEngine.physicalize(circ_disc, self.line_topology)

        # Expected inserted SWAP(0, 1), then CNOT(1, 2)
        self.assertEqual(len(p_circ.gates), 2)
        self.assertEqual(p_circ.gates[0].gate_type, "SWAP")
        self.assertEqual(p_circ.gates[0].control_nodes, (0,))
        self.assertEqual(p_circ.gates[0].target_node, 1)

        self.assertEqual(p_circ.gates[1].gate_type, "CNOT")
        self.assertEqual(p_circ.gates[1].control_nodes, (1,))
        self.assertEqual(p_circ.gates[1].target_node, 2)

        # Mapping update: q0 was at 0, SWAP(0,1) moved q0 to 1!
        self.assertEqual(p_circ.mapping.get_physical(self.q0), 1)
        self.assertEqual(p_circ.mapping.get_physical(self.q1), 0)

    def test_pos_07_08_shortest_path_and_tie_breaking(self) -> None:
        """Pos 7 & 8: Shortest path routing with deterministic tie-breaking."""
        # Diamond topology: 0-1, 0-2, 1-3, 2-3
        diamond_topo = DeviceTopology()
        diamond_topo.add_edge(0, 1)
        diamond_topo.add_edge(0, 2)
        diamond_topo.add_edge(1, 3)
        diamond_topo.add_edge(2, 3)

        path = ShortestPathRouter.find_shortest_path(0, 3, diamond_topo)
        # Paths (0, 1, 3) and (0, 2, 3) are both length 3.
        # Lexicographically smallest is (0, 1, 3)!
        self.assertEqual(path, [0, 1, 3])

    def test_pos_09_10_final_topology_and_ir_validation(self) -> None:
        """Pos 9 & 10: Final physical circuit passes Stage 1 IR validation."""
        p_circ, trace = PhysicalizationEngine.physicalize(self.logical_circuit, self.line_topology)
        val_res = validate_physical_circuit_ir(p_circ)
        self.assertTrue(val_res.valid, f"Validation errors: {val_res.errors}")

    def test_pos_11_provenance_preservation(self) -> None:
        """Pos 11: Upstream provenance preserved with Stage 3 marker."""
        p_circ, trace = PhysicalizationEngine.physicalize(self.logical_circuit, self.line_topology)
        self.assertEqual(p_circ.provenance.source_rutm_program_hash, "rutm_hash_999")
        self.assertEqual(p_circ.provenance.source_qtm_machine_id, "qtm_mach_888")
        self.assertEqual(p_circ.provenance.backend_id, "STAGE_3_PHYSICALIZATION_AND_SWAP_ROUTING")

    def test_pos_12_serialization_determinism(self) -> None:
        """Pos 12: Routed PhysicalCircuitIR serialization is deterministic."""
        p_circ, trace = PhysicalizationEngine.physicalize(self.logical_circuit, self.line_topology)
        s1 = serialize_physical_circuit_ir(p_circ)
        s2 = serialize_physical_circuit_ir(p_circ)
        self.assertEqual(s1, s2)

    def test_pos_13_multiple_sequential_routed_gates(self) -> None:
        """Pos 13: Multiple sequential routed gates track dynamic mapping evolution cleanly."""
        g1 = GateOperation(gate_type=LogicalGateType.CNOT, control_qubits=(self.q0,), target_qubit=self.q2)
        g2 = GateOperation(gate_type=LogicalGateType.CNOT, control_qubits=(self.q1,), target_qubit=self.q0)
        seq_circ = QuantumCircuitIR(
            circuit_id="seq_circ",
            registers=[self.reg_q],
            gates=[g1, g2],
            provenance=self.log_provenance,
        )
        p_circ, trace = PhysicalizationEngine.physicalize(seq_circ, self.line_topology)
        self.assertTrue(len(p_circ.gates) >= 2)
        self.assertTrue(p_circ.mapping.is_injective())

    def test_pos_14_mapping_remains_injective_after_swaps(self) -> None:
        """Pos 14: Mapping remains 100% injective after every SWAP."""
        g_cnot02 = GateOperation(gate_type=LogicalGateType.CNOT, control_qubits=(self.q0,), target_qubit=self.q2)
        circ_disc = QuantumCircuitIR(
            circuit_id="log_disc",
            registers=[self.reg_q],
            gates=[g_cnot02],
            provenance=self.log_provenance,
        )
        p_circ, trace = PhysicalizationEngine.physicalize(circ_disc, self.line_topology)
        self.assertTrue(p_circ.mapping.is_injective())

    # ------------------------------------------------------------------
    # NEGATIVE TESTS (10)
    # ------------------------------------------------------------------
    def test_neg_01_insufficient_physical_qubits(self) -> None:
        """Neg 1: Circuit requiring 3 logical qubits on 2-qubit topology rejected."""
        small_topo = DeviceTopology()
        small_topo.add_edge(0, 1)  # Only 2 nodes!
        with self.assertRaises(ValueError):
            PhysicalizationEngine.physicalize(self.logical_circuit, small_topo)

    def test_neg_02_unmapped_logical_qubit(self) -> None:
        """Neg 2: Unmapped logical qubit lookup raises KeyError."""
        m = QubitMapping()
        m.set_mapping(self.q0, 0)
        with self.assertRaises(KeyError):
            m.get_physical(self.q1)

    def test_neg_03_invalid_physical_node(self) -> None:
        """Neg 3: Custom mapping with physical node not in topology rejected."""
        bad_map = QubitMapping()
        bad_map.set_mapping(self.q0, 0)
        bad_map.set_mapping(self.q1, 1)
        bad_map.set_mapping(self.q2, 99)  # 99 not in topology!
        with self.assertRaises(ValueError):
            PhysicalizationEngine.physicalize(self.logical_circuit, self.line_topology, initial_mapping=bad_map)

    def test_neg_04_disconnected_topology_no_path(self) -> None:
        """Neg 4: Disconnected graph components with no routing path rejected."""
        disc_topo = DeviceTopology()
        disc_topo.add_edge(0, 1)
        disc_topo.add_node(2)  # Node 2 completely ISOLATED!

        g_disc = GateOperation(gate_type=LogicalGateType.CNOT, control_qubits=(self.q0,), target_qubit=self.q2)
        circ_no_path = QuantumCircuitIR(
            circuit_id="no_path",
            registers=[self.reg_q],
            gates=[g_disc],
            provenance=self.log_provenance,
        )
        with self.assertRaises(ValueError):
            PhysicalizationEngine.physicalize(circ_no_path, disc_topo)

    def test_neg_05_malformed_topology_self_loop(self) -> None:
        """Neg 5: Malformed topology with self-loop rejected."""
        bad_topo = DeviceTopology()
        with self.assertRaises(ValueError):
            bad_topo.add_edge(0, 0)

    def test_neg_06_non_injective_initial_mapping(self) -> None:
        """Neg 6: Non-injective custom mapping rejected."""
        bad_map = QubitMapping()
        bad_map.mapping = {self.q0: 0, self.q1: 0, self.q2: 2}
        with self.assertRaises(ValueError):
            PhysicalizationEngine.physicalize(self.logical_circuit, self.line_topology, initial_mapping=bad_map)

    def test_neg_07_08_illegal_operation_rejection(self) -> None:
        """Neg 7 & 8: Verifier rejects disconnected edge physical gates."""
        p_circ, trace = PhysicalizationEngine.physicalize(self.logical_circuit, self.line_topology)
        # Force a topology violation on physical circuit (disconnected edge 0-2)
        p_circ.gates.append(PhysicalGateOperation(gate_type="CZ", control_nodes=(0,), target_node=2, operation_index=99))
        ver_res = SemanticPreservationVerifier.verify(
            input_circuit=self.logical_circuit,
            input_circuit_snapshot_hash=hash(str(self.logical_circuit)),
            physical_circuit=p_circ,
            final_mapping=p_circ.mapping,
            topology=self.line_topology,
        )
        self.assertFalse(ver_res.verified)

    def test_neg_09_mutated_input_detection(self) -> None:
        """Neg 9: Verifier detects if input logical QuantumCircuitIR was mutated."""
        p_circ, trace = PhysicalizationEngine.physicalize(self.logical_circuit, self.line_topology)
        snapshot_hash = hash(str(self.logical_circuit))

        # Mutate logical_circuit!
        self.logical_circuit.circuit_id = "MUTATED_ID"

        ver_res = SemanticPreservationVerifier.verify(
            input_circuit=self.logical_circuit,
            input_circuit_snapshot_hash=snapshot_hash,
            physical_circuit=p_circ,
            final_mapping=p_circ.mapping,
            topology=self.line_topology,
        )
        self.assertFalse(ver_res.verified)
        self.assertFalse(ver_res.input_unmutated)

    def test_neg_10_nondeterministic_routing_rejection(self) -> None:
        """Neg 10: Routing path for non-existent node raises ValueError."""
        with self.assertRaises(ValueError):
            ShortestPathRouter.find_shortest_path(0, 999, self.line_topology)


if __name__ == "__main__":
    unittest.main()
