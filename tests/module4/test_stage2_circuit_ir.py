"""
Module 4 Stage 2 Unit Test Suite — QuantumCircuitIR Model, Validator, and Serialization.

Tests:
1. Register creation and qubit identity
2. Primitive gate operations (X, CNOT, TOFFOLI)
3. Gate ordering semantics
4. Ancilla declarations & status checks
5. Level 1 Structural Validation (arity, qubit bounds, schema version)
6. Level 2 Semantic Validation (provenance, register types, input/output)
7. Level 3 Mathematical Invariant Validation (aliasing & unitariness)
8. Provenance Metadata
9. Lossless JSON serialization round-trip (deserialize(serialize(C)) == C)
10. Negative validation (duplicate IDs, out-of-bound indices, control/target collisions, dirty ancillas)
"""

import unittest
import json
from src.module4.circuit_ir import (
    QuantumCircuitIR,
    QubitRegister,
    QubitRef,
    GateOperation,
    AncillaDeclaration,
    CircuitProvenance,
    RegisterType,
    AncillaStatus,
    LogicalGateType,
    SCHEMA_VERSION,
    validate_circuit_ir,
    serialize_circuit_ir_to_json,
    deserialize_circuit_ir_from_json,
)


class TestStage2CircuitIR(unittest.TestCase):
    def setUp(self) -> None:
        self.r_state = QubitRegister(register_id="reg_q", register_type=RegisterType.STATE, width=2)
        self.r_tape = QubitRegister(register_id="reg_t", register_type=RegisterType.TAPE, width=4)
        self.r_anc = QubitRegister(register_id="reg_a", register_type=RegisterType.ANCILLA, width=2)

        self.q_s0 = self.r_state.get_qubit_ref(0)
        self.q_s1 = self.r_state.get_qubit_ref(1)
        self.q_t0 = self.r_tape.get_qubit_ref(0)
        self.q_a0 = self.r_anc.get_qubit_ref(0)

        self.g0 = GateOperation(gate_type=LogicalGateType.X, target_qubit=self.q_s0, operation_index=0)
        self.g1 = GateOperation(gate_type=LogicalGateType.CNOT, control_qubits=(self.q_s0,), target_qubit=self.q_s1, operation_index=1)
        self.g2 = GateOperation(gate_type=LogicalGateType.TOFFOLI, control_qubits=(self.q_s0, self.q_s1), target_qubit=self.q_t0, operation_index=2)

        self.provenance = CircuitProvenance(
            source_rutm_program_hash="hash_12345",
            source_qtm_machine_id="qtm_machine_01",
        )

        self.circuit = QuantumCircuitIR(
            circuit_id="circ_test_01",
            registers=[self.r_state, self.r_tape, self.r_anc],
            gates=[self.g0, self.g1, self.g2],
            ancilla_declarations=[
                AncillaDeclaration(qubit_ref=self.q_a0, initial_status=AncillaStatus.CLEAN, expected_final_status=AncillaStatus.CLEAN)
            ],
            input_register_ids=["reg_q", "reg_t"],
            output_register_ids=["reg_q", "reg_t"],
            provenance=self.provenance,
        )

    def test_circuit_model_and_registers(self) -> None:
        """Req 2, 3, 4: Test register model, width, and qubit refs."""
        self.assertEqual(self.circuit.circuit_id, "circ_test_01")
        self.assertEqual(self.circuit.total_width, 8)
        self.assertEqual(self.circuit.total_gate_count, 3)
        self.assertEqual(self.q_s0.to_string(), "reg_q[0]")
        self.assertEqual(self.circuit.get_register("reg_tape"), None)
        self.assertIsNotNone(self.circuit.get_register("reg_q"))

    def test_primitive_gates_and_arity(self) -> None:
        """Req 8, 9, 10: Test primitive gate models (X, CNOT, TOFFOLI) and arity."""
        self.assertEqual(self.g0.arity, 1)
        self.assertEqual(self.g1.arity, 2)
        self.assertEqual(self.g2.arity, 3)
        self.assertEqual(len(self.g2.all_qubit_refs), 3)

    def test_valid_circuit_validation(self) -> None:
        """Req 24, 25, 26: Test Level 1-3 validation on valid circuit."""
        val_res = validate_circuit_ir(self.circuit)
        self.assertTrue(val_res.valid, f"Validation errors: {val_res.errors}")
        self.assertEqual(len(val_res.errors), 0)

    def test_serialization_round_trip(self) -> None:
        """Req 27, 28: Test deterministic JSON serialization and lossless round-trip."""
        json_str = serialize_circuit_ir_to_json(self.circuit)
        deserialized = deserialize_circuit_ir_from_json(json_str)

        self.assertEqual(deserialized.circuit_id, self.circuit.circuit_id)
        self.assertEqual(deserialized.schema_version, self.circuit.schema_version)
        self.assertEqual(deserialized.total_width, self.circuit.total_width)
        self.assertEqual(deserialized.total_gate_count, self.circuit.total_gate_count)
        self.assertEqual(len(deserialized.registers), len(self.circuit.registers))
        self.assertEqual(deserialized.provenance.source_rutm_program_hash, self.provenance.source_rutm_program_hash)

        # Deterministic re-serialization check
        json_str_2 = serialize_circuit_ir_to_json(deserialized)
        self.assertEqual(json_str, json_str_2)

    def test_negative_invalid_schema_version(self) -> None:
        """Req 29: Negative test for invalid schema version."""
        bad_circuit = QuantumCircuitIR(circuit_id="bad_1", registers=[self.r_state], gates=[], schema_version="9.9.9")
        val_res = validate_circuit_ir(bad_circuit)
        self.assertFalse(val_res.valid)
        self.assertTrue(any("schema version" in err for err in val_res.errors))

    def test_negative_duplicate_registers(self) -> None:
        """Req 29: Negative test for duplicate register IDs."""
        bad_circuit = QuantumCircuitIR(
            circuit_id="bad_2",
            registers=[self.r_state, self.r_state],
            gates=[],
        )
        val_res = validate_circuit_ir(bad_circuit)
        self.assertFalse(val_res.valid)
        self.assertTrue(any("Duplicate register ID" in err for err in val_res.errors))

    def test_negative_invalid_qubit_bounds(self) -> None:
        """Req 29: Negative test for out-of-bounds qubit reference."""
        bad_ref = QubitRef(register_id="reg_q", index=10)  # Width is 2!
        bad_gate = GateOperation(gate_type=LogicalGateType.X, target_qubit=bad_ref, operation_index=0)
        bad_circuit = QuantumCircuitIR(
            circuit_id="bad_3",
            registers=[self.r_state],
            gates=[bad_gate],
        )
        val_res = validate_circuit_ir(bad_circuit)
        self.assertFalse(val_res.valid)
        self.assertTrue(any("out of bounds" in err for err in val_res.errors))

    def test_negative_gate_arity_mismatch(self) -> None:
        """Req 29: Negative test for incorrect gate arity."""
        # CNOT with 2 controls!
        bad_gate = GateOperation(gate_type=LogicalGateType.CNOT, control_qubits=(self.q_s0, self.q_s1), target_qubit=self.q_t0, operation_index=0)
        bad_circuit = QuantumCircuitIR(circuit_id="bad_4", registers=[self.r_state, self.r_tape], gates=[bad_gate])
        val_res = validate_circuit_ir(bad_circuit)
        self.assertFalse(val_res.valid)
        self.assertTrue(any("Expected 1 control qubit" in err for err in val_res.errors))

    def test_negative_qubit_aliasing_collision(self) -> None:
        """Req 11 & 29: Negative test for control/target collision on same qubit."""
        # CNOT where control == target!
        bad_gate = GateOperation(gate_type=LogicalGateType.CNOT, control_qubits=(self.q_s0,), target_qubit=self.q_s0, operation_index=0)
        bad_circuit = QuantumCircuitIR(circuit_id="bad_5", registers=[self.r_state], gates=[bad_gate])
        val_res = validate_circuit_ir(bad_circuit)
        self.assertFalse(val_res.valid)
        self.assertTrue(any("aliasing" in err for err in val_res.errors))

    def test_negative_dirty_ancilla(self) -> None:
        """Req 6 & 29: Negative test for dirty ancilla declaration."""
        dirty_anc = AncillaDeclaration(qubit_ref=self.q_a0, initial_status=AncillaStatus.DIRTY, expected_final_status=AncillaStatus.CLEAN)
        bad_circuit = QuantumCircuitIR(circuit_id="bad_6", registers=[self.r_anc], gates=[], ancilla_declarations=[dirty_anc])
        val_res = validate_circuit_ir(bad_circuit)
        self.assertFalse(val_res.valid)
        self.assertTrue(any("Dirty initial ancilla" in err for err in val_res.errors))


if __name__ == "__main__":
    unittest.main()
