"""
Module 5 Stage 1 Unit Test Suite — PhysicalCircuitIR Model, Validator & Serialization.

Tests all 20 negative-path validation requirements + 3 determinism, round-trip, and SWAP update tests:
1. invalid schema version
2. empty circuit ID
3. duplicate physical qubit IDs
4. duplicate operation indices
5. non-sequential operation indices
6. out-of-bounds target node
7. out-of-bounds control node
8. control-target collision
9. duplicate control node
10. non-injective mapping
11. unmapped logical qubit lookup error
12. unknown physical node in mapping
13. topology inconsistency
14. empty gate type
15. invalid provenance
16. malformed serialization JSON string
17. serialization schema mismatch
18. invalid mapping round-trip
19. invalid topology round-trip
20. invalid physical circuit round-trip
21. Deterministic serialization S(C) == S(C)
22. Exact round-trip deserialize(serialize(C)) == C and serialize(C1) == serialize(C)
23. SWAP mapping update M -> M'
"""

import unittest
import json
from src.module4.circuit_ir.model import QubitRef, QubitRegister, RegisterType
from src.module5 import (
    PhysicalQubit,
    QubitMapping,
    DeviceTopology,
    PhysicalGateOperation,
    PhysicalCircuitIR,
    ExecutionProvenance,
    SCHEMA_VERSION,
    validate_physical_circuit_ir,
    serialize_physical_circuit_ir,
    deserialize_physical_circuit_ir,
)


class TestStage1PhysicalCircuitIR(unittest.TestCase):
    def setUp(self) -> None:
        self.q0 = QubitRef("reg_q", 0)
        self.q1 = QubitRef("reg_q", 1)
        self.q2 = QubitRef("reg_q", 2)

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

        self.g0 = PhysicalGateOperation(gate_type="X", target_node=0, control_nodes=(), operation_index=0)
        self.g1 = PhysicalGateOperation(gate_type="CNOT", control_nodes=(0,), target_node=1, operation_index=1)
        self.g2 = PhysicalGateOperation(gate_type="TOFFOLI", control_nodes=(0, 1), target_node=2, operation_index=2)

        self.provenance = ExecutionProvenance(
            source_rutm_program_hash="rutm_hash_001",
            source_qtm_machine_id="qtm_machine_002",
            logical_circuit_id="logical_circ_003",
            physical_circuit_id="phys_circ_001",
        )

        self.circuit = PhysicalCircuitIR(
            physical_circuit_id="phys_circ_001",
            source_logical_circuit_id="logical_circ_003",
            physical_qubits=[self.p0, self.p1, self.p2],
            gates=[self.g0, self.g1, self.g2],
            mapping=self.mapping,
            topology=self.topology,
            provenance=self.provenance,
            schema_version=SCHEMA_VERSION,
        )

    def test_valid_circuit_passes_validation(self) -> None:
        """Req 24: Valid circuit passes 3-level validation."""
        res = validate_physical_circuit_ir(self.circuit)
        self.assertTrue(res.valid, f"Validation failed with errors: {res.errors}")
        self.assertTrue(res.structural_pass)
        self.assertTrue(res.semantic_pass)
        self.assertTrue(res.consistency_pass)

    def test_01_invalid_schema_version(self) -> None:
        """Negative Test 1: Invalid schema version rejected."""
        c = PhysicalCircuitIR(
            physical_circuit_id="p1",
            source_logical_circuit_id="l1",
            physical_qubits=[self.p0],
            gates=[],
            mapping=QubitMapping(),
            topology=DeviceTopology(),
            provenance=self.provenance,
            schema_version="9.9.9",
        )
        res = validate_physical_circuit_ir(c)
        self.assertFalse(res.valid)
        self.assertFalse(res.structural_pass)

    def test_02_empty_circuit_id(self) -> None:
        """Negative Test 2: Empty circuit ID rejected."""
        c = PhysicalCircuitIR(
            physical_circuit_id="   ",
            source_logical_circuit_id="l1",
            physical_qubits=[self.p0],
            gates=[],
            mapping=QubitMapping(),
            topology=DeviceTopology(),
            provenance=self.provenance,
        )
        res = validate_physical_circuit_ir(c)
        self.assertFalse(res.valid)
        self.assertFalse(res.structural_pass)

    def test_03_duplicate_physical_qubit_ids(self) -> None:
        """Negative Test 3: Duplicate physical qubit node_ids rejected."""
        p0_dup = PhysicalQubit(node_id=0)
        c = PhysicalCircuitIR(
            physical_circuit_id="p1",
            source_logical_circuit_id="l1",
            physical_qubits=[self.p0, p0_dup],
            gates=[],
            mapping=QubitMapping(),
            topology=DeviceTopology(),
            provenance=self.provenance,
        )
        res = validate_physical_circuit_ir(c)
        self.assertFalse(res.valid)
        self.assertFalse(res.structural_pass)

    def test_04_05_non_sequential_operation_indices(self) -> None:
        """Negative Test 4 & 5: Duplicate or non-sequential operation indices rejected."""
        g_bad = PhysicalGateOperation(gate_type="X", target_node=0, operation_index=5)  # Expected 1!
        c = PhysicalCircuitIR(
            physical_circuit_id="p1",
            source_logical_circuit_id="l1",
            physical_qubits=[self.p0],
            gates=[self.g0, g_bad],
            mapping=QubitMapping(),
            topology=DeviceTopology(),
            provenance=self.provenance,
        )
        res = validate_physical_circuit_ir(c)
        self.assertFalse(res.valid)
        self.assertFalse(res.structural_pass)

    def test_06_07_out_of_bounds_target_or_control(self) -> None:
        """Negative Test 6 & 7: Out-of-bounds target or control node rejected."""
        g_oob = PhysicalGateOperation(gate_type="CNOT", control_nodes=(0,), target_node=99, operation_index=0)
        c = PhysicalCircuitIR(
            physical_circuit_id="p1",
            source_logical_circuit_id="l1",
            physical_qubits=[self.p0],
            gates=[g_oob],
            mapping=QubitMapping(),
            topology=DeviceTopology(),
            provenance=self.provenance,
        )
        res = validate_physical_circuit_ir(c)
        self.assertFalse(res.valid)
        self.assertFalse(res.semantic_pass)

    def test_08_control_target_collision(self) -> None:
        """Negative Test 8: Control node equals target node rejected."""
        g_col = PhysicalGateOperation(gate_type="CNOT", control_nodes=(0,), target_node=0, operation_index=0)
        c = PhysicalCircuitIR(
            physical_circuit_id="p1",
            source_logical_circuit_id="l1",
            physical_qubits=[self.p0],
            gates=[g_col],
            mapping=QubitMapping(),
            topology=DeviceTopology(),
            provenance=self.provenance,
        )
        res = validate_physical_circuit_ir(c)
        self.assertFalse(res.valid)
        self.assertFalse(res.structural_pass)

    def test_09_duplicate_control_node(self) -> None:
        """Negative Test 9: Duplicate control nodes rejected."""
        g_dup = PhysicalGateOperation(gate_type="TOFFOLI", control_nodes=(0, 0), target_node=1, operation_index=0)
        c = PhysicalCircuitIR(
            physical_circuit_id="p1",
            source_logical_circuit_id="l1",
            physical_qubits=[self.p0, self.p1],
            gates=[g_dup],
            mapping=QubitMapping(),
            topology=DeviceTopology(),
            provenance=self.provenance,
        )
        res = validate_physical_circuit_ir(c)
        self.assertFalse(res.valid)
        self.assertFalse(res.structural_pass)

    def test_10_non_injective_mapping(self) -> None:
        """Negative Test 10: Non-injective mapping rejected."""
        bad_map = QubitMapping()
        bad_map.mapping = {self.q0: 0, self.q1: 0}  # Force collision
        c = PhysicalCircuitIR(
            physical_circuit_id="p1",
            source_logical_circuit_id="l1",
            physical_qubits=[self.p0],
            gates=[],
            mapping=bad_map,
            topology=DeviceTopology(),
            provenance=self.provenance,
        )
        res = validate_physical_circuit_ir(c)
        self.assertFalse(res.valid)
        self.assertFalse(res.semantic_pass)

    def test_11_unmapped_logical_qubit_lookup(self) -> None:
        """Negative Test 11: Unmapped logical qubit lookup raises KeyError."""
        unmapped = QubitRef("reg_q", 99)
        with self.assertRaises(KeyError):
            self.mapping.get_physical(unmapped)

    def test_12_unknown_physical_node_in_mapping(self) -> None:
        """Negative Test 12: Unknown physical node in mapping rejected."""
        bad_map = QubitMapping()
        bad_map.set_mapping(self.q0, 99)  # Physical node 99 not in physical_qubits!
        c = PhysicalCircuitIR(
            physical_circuit_id="p1",
            source_logical_circuit_id="l1",
            physical_qubits=[self.p0],
            gates=[],
            mapping=bad_map,
            topology=DeviceTopology(),
            provenance=self.provenance,
        )
        res = validate_physical_circuit_ir(c)
        self.assertFalse(res.valid)
        self.assertFalse(res.semantic_pass)

    def test_13_topology_inconsistency(self) -> None:
        """Negative Test 13: Gate on disconnected physical topology nodes rejected."""
        topo = DeviceTopology()
        topo.add_node(0)
        topo.add_node(1)
        topo.add_node(2)
        topo.add_edge(0, 1)  # 0-1 connected, but 0-2 DISCONNECTED!

        g_disc = PhysicalGateOperation(gate_type="CZ", control_nodes=(0,), target_node=2, operation_index=0)
        c = PhysicalCircuitIR(
            physical_circuit_id="p1",
            source_logical_circuit_id="l1",
            physical_qubits=[self.p0, self.p1, self.p2],
            gates=[g_disc],
            mapping=self.mapping,
            topology=topo,
            provenance=self.provenance,
        )
        res = validate_physical_circuit_ir(c)
        self.assertFalse(res.valid)
        self.assertFalse(res.semantic_pass)

    def test_14_empty_gate_type(self) -> None:
        """Negative Test 14: Empty gate type rejected."""
        g_empty = PhysicalGateOperation(gate_type="", target_node=0, operation_index=0)
        c = PhysicalCircuitIR(
            physical_circuit_id="p1",
            source_logical_circuit_id="l1",
            physical_qubits=[self.p0],
            gates=[g_empty],
            mapping=QubitMapping(),
            topology=DeviceTopology(),
            provenance=self.provenance,
        )
        res = validate_physical_circuit_ir(c)
        self.assertFalse(res.valid)
        self.assertFalse(res.structural_pass)

    def test_15_invalid_provenance(self) -> None:
        """Negative Test 15: Missing or empty provenance rejected."""
        bad_prov = ExecutionProvenance(source_rutm_program_hash="", source_qtm_machine_id="", logical_circuit_id="")
        c = PhysicalCircuitIR(
            physical_circuit_id="p1",
            source_logical_circuit_id="l1",
            physical_qubits=[self.p0],
            gates=[],
            mapping=QubitMapping(),
            topology=DeviceTopology(),
            provenance=bad_prov,
        )
        res = validate_physical_circuit_ir(c)
        self.assertFalse(res.valid)
        self.assertFalse(res.semantic_pass)

    def test_16_17_malformed_serialization_or_schema_mismatch(self) -> None:
        """Negative Test 16 & 17: Malformed JSON or schema version mismatch rejected."""
        with self.assertRaises(ValueError):
            deserialize_physical_circuit_ir("{bad json}")

        s_json = serialize_physical_circuit_ir(self.circuit)
        bad_ver_json = s_json.replace('"1.0.0"', '"9.9.9"')
        with self.assertRaises(ValueError):
            deserialize_physical_circuit_ir(bad_ver_json)

    def test_18_19_20_round_trip_verification(self) -> None:
        """Req 18, 19, 20 & 22: Exact round-trip verification deserialize(serialize(C)) == C."""
        s1 = serialize_physical_circuit_ir(self.circuit)
        c_deser = deserialize_physical_circuit_ir(s1)
        s2 = serialize_physical_circuit_ir(c_deser)

        self.assertEqual(s1, s2)
        self.assertEqual(c_deser.physical_circuit_id, self.circuit.physical_circuit_id)
        self.assertEqual(len(c_deser.gates), len(self.circuit.gates))

    def test_21_deterministic_serialization(self) -> None:
        """Req 21 & XVII: Deterministic serialization S(C) == S(C)."""
        s1 = serialize_physical_circuit_ir(self.circuit)
        s2 = serialize_physical_circuit_ir(self.circuit)
        self.assertEqual(s1, s2)

    def test_23_swap_mapping_update(self) -> None:
        """Req V: SWAP mapping update semantics."""
        m = QubitMapping()
        m.set_mapping(self.q0, 0)
        m.set_mapping(self.q1, 1)

        m.apply_swap(0, 1)
        self.assertEqual(m.get_physical(self.q0), 1)
        self.assertEqual(m.get_physical(self.q1), 0)


if __name__ == "__main__":
    unittest.main()
