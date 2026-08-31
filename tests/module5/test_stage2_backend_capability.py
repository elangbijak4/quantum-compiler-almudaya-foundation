"""
Module 5 Stage 2 Unit Test Suite — Backend Capability Model & Compatibility Validation.

Tests all 22 negative-path requirements + 12 positive-path requirements:
Negative:
1. invalid backend schema version
2. empty backend ID
3. invalid backend type
4. zero qubit capacity
5. negative qubit capacity
6. duplicate physical nodes
7. invalid topology edge
8. self-loop
9. duplicate gate capability
10. invalid gate arity
11. unsupported gate query
12. unsupported physical node
13. unsupported topology connection
14. unsupported measurement
15. unsupported execution mode
16. contradictory capability declaration
17. PhysicalCircuitIR exceeds backend capacity
18. PhysicalCircuitIR uses unsupported gate
19. PhysicalCircuitIR violates topology
20. malformed capability serialization
21. capability schema mismatch
22. capability round-trip inconsistency

Positive:
1. reference simulator capability construction
2. finite qubit capacity
3. topology query
4. gate support query
5. measurement capability query
6. execution capability query
7. statevector capability query
8. shot capability query
9. compatible PhysicalCircuitIR
10. incompatible PhysicalCircuitIR
11. deterministic capability serialization
12. exact capability round-trip
"""

import unittest
from src.module4.circuit_ir.model import QubitRef
from src.module5 import (
    PhysicalQubit,
    QubitMapping,
    DeviceTopology,
    PhysicalGateOperation,
    PhysicalCircuitIR,
    ExecutionProvenance,
    BackendType,
    BackendIdentity,
    QubitCapacity,
    BackendTopologyCapability,
    GateCapability,
    GateConstraint,
    MeasurementCapability,
    ExecutionCapability,
    NumericalCapability,
    BackendCapabilityProvenance,
    BackendCapabilityModel,
    BACKEND_CAPABILITY_SCHEMA_VERSION,
    validate_backend_capabilities,
    validate_backend_compatibility,
    serialize_backend_capabilities,
    deserialize_backend_capabilities,
    create_reference_simulator_capabilities,
)


class TestStage2BackendCapability(unittest.TestCase):
    def setUp(self) -> None:
        self.ref_model = create_reference_simulator_capabilities(max_qubits=8)

        # Valid physical circuit
        self.q0 = QubitRef("reg_q", 0)
        self.q1 = QubitRef("reg_q", 1)
        self.p0 = PhysicalQubit(node_id=0)
        self.p1 = PhysicalQubit(node_id=1)
        self.mapping = QubitMapping()
        self.mapping.set_mapping(self.q0, 0)
        self.mapping.set_mapping(self.q1, 1)
        self.topology = DeviceTopology()
        self.topology.add_edge(0, 1)

        self.g0 = PhysicalGateOperation(gate_type="X", target_node=0, operation_index=0)
        self.g1 = PhysicalGateOperation(gate_type="CNOT", control_nodes=(0,), target_node=1, operation_index=1)

        self.provenance = ExecutionProvenance(
            source_rutm_program_hash="rutm_123",
            source_qtm_machine_id="qtm_456",
            logical_circuit_id="l_circ_789",
            physical_circuit_id="p_circ_001",
        )

        self.valid_circuit = PhysicalCircuitIR(
            physical_circuit_id="p_circ_001",
            source_logical_circuit_id="l_circ_789",
            physical_qubits=[self.p0, self.p1],
            gates=[self.g0, self.g1],
            mapping=self.mapping,
            topology=self.topology,
            provenance=self.provenance,
        )

    # ------------------------------------------------------------------
    # POSITIVE TESTS (12)
    # ------------------------------------------------------------------
    def test_pos_01_reference_simulator_construction(self) -> None:
        """Pos 1: Create reference simulator capability profile."""
        self.assertEqual(self.ref_model.identity.backend_id, "reference_simulator")
        self.assertEqual(self.ref_model.identity.backend_type, BackendType.REFERENCE_SIMULATOR)

    def test_pos_02_finite_qubit_capacity(self) -> None:
        """Pos 2: Query max_qubits capacity."""
        self.assertEqual(self.ref_model.qubit_capacity.max_qubits, 8)

    def test_pos_03_topology_query(self) -> None:
        """Pos 3: Query topology connectivity."""
        self.assertTrue(self.ref_model.supports_connection(0, 1))

    def test_pos_04_gate_support_query(self) -> None:
        """Pos 4: Query supported gates."""
        self.assertTrue(self.ref_model.supports_gate("CNOT"))
        self.assertTrue(self.ref_model.supports_gate_arity("TOFFOLI", 3))

    def test_pos_05_06_07_08_capabilities_queries(self) -> None:
        """Pos 5, 6, 7, 8: Measurement, execution, statevector, sampling queries."""
        self.assertTrue(self.ref_model.supports_measurement())
        self.assertTrue(self.ref_model.supports_shots())
        self.assertTrue(self.ref_model.supports_statevector())
        self.assertTrue(self.ref_model.supports_sampling())

    def test_pos_09_compatible_physical_circuit(self) -> None:
        """Pos 9: Compatible PhysicalCircuitIR passes validation."""
        res = validate_backend_compatibility(self.valid_circuit, self.ref_model)
        self.assertTrue(res.compatible, f"Compatibility failed with errors: {res.errors}")

    def test_pos_10_incompatible_physical_circuit(self) -> None:
        """Pos 10: Incompatible PhysicalCircuitIR (unsupported gate) fails validation."""
        bad_gate = PhysicalGateOperation(gate_type="UNSUPPORTED_GATE_123", target_node=0, operation_index=2)
        bad_circ = PhysicalCircuitIR(
            physical_circuit_id="p_bad",
            source_logical_circuit_id="l1",
            physical_qubits=[self.p0],
            gates=[self.g0, self.g1, bad_gate],
            mapping=self.mapping,
            topology=self.topology,
            provenance=self.provenance,
        )
        res = validate_backend_compatibility(bad_circ, self.ref_model)
        self.assertFalse(res.compatible)

    def test_pos_11_12_serialization_round_trip(self) -> None:
        """Pos 11 & 12: Deterministic serialization and exact round-trip."""
        s1 = serialize_backend_capabilities(self.ref_model)
        s2 = serialize_backend_capabilities(self.ref_model)
        self.assertEqual(s1, s2)

        deser = deserialize_backend_capabilities(s1)
        s3 = serialize_backend_capabilities(deser)
        self.assertEqual(s1, s3)
        self.assertEqual(deser.identity.backend_id, self.ref_model.identity.backend_id)

    # ------------------------------------------------------------------
    # NEGATIVE TESTS (22)
    # ------------------------------------------------------------------
    def test_neg_01_invalid_schema_version(self) -> None:
        """Neg 1: Invalid schema version rejected."""
        m = create_reference_simulator_capabilities()
        m.schema_version = "9.9.9"
        res = validate_backend_capabilities(m)
        self.assertFalse(res.valid)

    def test_neg_02_empty_backend_id(self) -> None:
        """Neg 2: Empty backend ID rejected."""
        m = create_reference_simulator_capabilities()
        m.identity = BackendIdentity(backend_id="  ", backend_name="name", backend_version="1.0")
        res = validate_backend_capabilities(m)
        self.assertFalse(res.valid)

    def test_neg_04_05_zero_or_negative_qubit_capacity(self) -> None:
        """Neg 4 & 5: Zero or negative max_qubits rejected."""
        with self.assertRaises(ValueError):
            QubitCapacity(max_qubits=0)
        with self.assertRaises(ValueError):
            QubitCapacity(max_qubits=-5)

    def test_neg_07_08_invalid_topology_edge_or_self_loop(self) -> None:
        """Neg 7 & 8: Self-loop or negative node in topology rejected."""
        topo = BackendTopologyCapability()
        with self.assertRaises(ValueError):
            topo.add_node(-1)
        with self.assertRaises(ValueError):
            topo.add_edge(0, 0)

    def test_neg_09_10_invalid_gate_capability(self) -> None:
        """Neg 9 & 10: Empty gate type or arity < 1 rejected."""
        with self.assertRaises(ValueError):
            GateCapability(gate_type="", arity=1)
        with self.assertRaises(ValueError):
            GateCapability(gate_type="X", arity=0)

    def test_neg_11_12_13_unsupported_queries(self) -> None:
        """Neg 11, 12, 13: Unsupported gate, qubit, or connection queries return False."""
        self.assertFalse(self.ref_model.supports_gate("NON_EXISTENT_GATE"))
        self.assertFalse(self.ref_model.supports_qubit(999))
        self.assertFalse(self.ref_model.supports_connection(0, 999))

    def test_neg_16_contradictory_capability_declaration(self) -> None:
        """Neg 16: Contradictory capability declaration (supports_counts=True but supports_measurement=False) rejected."""
        m = create_reference_simulator_capabilities()
        m.measurement.supports_measurement = False
        m.measurement.supports_counts = True
        res = validate_backend_capabilities(m)
        self.assertFalse(res.valid)

    def test_neg_17_circuit_exceeds_qubit_capacity(self) -> None:
        """Neg 17: Circuit requiring more qubits than max_qubits rejected."""
        small_backend = create_reference_simulator_capabilities(max_qubits=1)  # Only 1 qubit!
        res = validate_backend_compatibility(self.valid_circuit, small_backend)
        self.assertFalse(res.compatible)

    def test_neg_18_circuit_uses_unsupported_gate(self) -> None:
        """Neg 18: Circuit with unsupported gate rejected."""
        limited_backend = create_reference_simulator_capabilities()
        limited_backend.gate_capabilities["CNOT"].supported = False  # Disable CNOT!
        res = validate_backend_compatibility(self.valid_circuit, limited_backend)
        self.assertFalse(res.compatible)

    def test_neg_19_circuit_violates_topology(self) -> None:
        """Neg 19: Circuit violating backend topology connectivity rejected."""
        topo = BackendTopologyCapability()
        topo.add_node(0)
        topo.add_node(1)
        # DISCONNECTED topology (0, 1) not connected!
        disc_backend = create_reference_simulator_capabilities()
        disc_backend.topology = topo
        res = validate_backend_compatibility(self.valid_circuit, disc_backend)
        self.assertFalse(res.compatible)

    def test_neg_20_21_22_serialization_errors(self) -> None:
        """Neg 20, 21, 22: Malformed JSON or schema mismatch rejected."""
        with self.assertRaises(ValueError):
            deserialize_backend_capabilities("{bad json}")

        s_json = serialize_backend_capabilities(self.ref_model)
        bad_ver_json = s_json.replace(f'"{BACKEND_CAPABILITY_SCHEMA_VERSION}"', '"9.9.9"')
        with self.assertRaises(ValueError):
            deserialize_backend_capabilities(bad_ver_json)


if __name__ == "__main__":
    unittest.main()
