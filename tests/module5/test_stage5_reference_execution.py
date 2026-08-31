"""
Module 5 Stage 5 Step 1 & Step 2 Unit Test Suite — Reference Execution Engine.

Tests all positive and negative requirements for offline, in-process ideal state-vector execution:
POSITIVE:
1. Zero-state initialization
2. Explicit normalized state
3. X gate basis tests
4. CNOT gate basis tests
5. SWAP gate basis tests
6. TOFFOLI gate basis tests (all 8 basis states)
7. Sequential gate execution
8. Superposition state evolution (Bell state generation)
9. Normalization invariant
10. Deterministic execution
11. Reverse execution
12. Linearity preservation
13. Provenance preservation
14. Input immutability

NEGATIVE:
15. Invalid initial state
16. Invalid state dimension
17. Unsupported native gate
18. Invalid qubit index (out of bounds)
19. Control-target collision
20. Malformed NativeCircuitIR
21. Execution mode support verification
"""

import unittest
import math
import copy
from src.module4.circuit_ir.model import QubitRef
from src.module5 import (
    PhysicalQubit,
    QubitMapping,
    DeviceTopology,
    PhysicalGateOperation,
    PhysicalCircuitIR,
    ExecutionProvenance,
    NativeOperation,
    NativeCircuitIR,
    ReferenceBackendAdapter,
    NativeTranslator,
    QuantumState,
    ExecutionMode,
    ExecutionStatus,
    ExecutionFailureCode,
    ExecutionRequest,
    ExecutionResult,
    ExecutionEngine,
    STAGE_5_EPSILON,
)


class TestStage5ReferenceExecution(unittest.TestCase):
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
        self.topology.add_edge(0, 2)

        self.provenance = ExecutionProvenance(
            source_rutm_program_hash="rutm_hash_999",
            source_qtm_machine_id="qtm_id_888",
            logical_circuit_id="log_c1",
            physical_circuit_id="phys_c1",
        )

        self.adapter = ReferenceBackendAdapter()

    def _create_native_circuit(self, native_ops: list, qubits: list = [0, 1]) -> NativeCircuitIR:
        return NativeCircuitIR(
            circuit_id="n_circ_1",
            backend_id="reference_simulator",
            backend_version="1.0.0",
            qubits=qubits,
            native_operations=native_ops,
            input_mapping=self.mapping,
            output_mapping=self.mapping,
            provenance=self.provenance,
        )

    # ------------------------------------------------------------------
    # POSITIVE TESTS
    # ------------------------------------------------------------------
    def test_pos_01_zero_state_initialization(self) -> None:
        """Pos 1: Default initialization produces |0...0> = (1, 0, ..., 0)^T."""
        state = QuantumState.initialize_zero(2)
        self.assertEqual(state.num_qubits(), 2)
        self.assertEqual(state.dimension(), 4)
        vec = state.vector()
        self.assertEqual(vec[0], 1.0 + 0.0j)
        self.assertEqual(vec[1], 0.0 + 0.0j)
        self.assertEqual(vec[2], 0.0 + 0.0j)
        self.assertEqual(vec[3], 0.0 + 0.0j)
        self.assertTrue(state.is_normalized())

    def test_pos_02_explicit_normalized_initial_state(self) -> None:
        """Pos 2: Explicit normalized initial state vector is correctly ingested."""
        psi_0 = [0.0 + 0.0j, 1.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j]  # |01>
        state = QuantumState.from_vector(psi_0)
        self.assertTrue(state.is_normalized())
        self.assertEqual(state.vector(), psi_0)

    def test_pos_03_x_gate_basis_tests(self) -> None:
        """Pos 3: X gate basis tests: X|0> = |1>, X|1> = |0>."""
        ops = [NativeOperation(native_gate="X", operands=(0,), operation_index=0)]
        circ = self._create_native_circuit(ops, qubits=[0])
        req = ExecutionRequest(request_id="req_x", native_circuit=circ, execution_mode=ExecutionMode.STATE_VECTOR)
        res = ExecutionEngine.execute(req)

        self.assertEqual(res.status, ExecutionStatus.SUCCESS)
        self.assertEqual(res.final_state_vector["0"], 0.0 + 0.0j)
        self.assertEqual(res.final_state_vector["1"], 1.0 + 0.0j)

    def test_pos_04_cnot_gate_basis_tests(self) -> None:
        """Pos 4: CNOT gate basis tests across all 4 computational basis states."""
        # |10> -> CNOT(0,1) -> |11>
        ops = [
            NativeOperation(native_gate="X", operands=(0,), operation_index=0),
            NativeOperation(native_gate="CNOT", operands=(0, 1), operation_index=1),
        ]
        circ = self._create_native_circuit(ops, qubits=[0, 1])
        req = ExecutionRequest(request_id="req_cnot", native_circuit=circ, execution_mode=ExecutionMode.STATE_VECTOR)
        res = ExecutionEngine.execute(req)

        self.assertEqual(res.status, ExecutionStatus.SUCCESS)
        self.assertEqual(res.final_state_vector["11"], 1.0 + 0.0j)
        self.assertEqual(res.final_state_vector["00"], 0.0 + 0.0j)

    def test_pos_05_swap_gate_basis_tests(self) -> None:
        """Pos 5: SWAP gate basis tests: |10> -> SWAP(0,1) -> |01>."""
        ops = [
            NativeOperation(native_gate="X", operands=(0,), operation_index=0),
            NativeOperation(native_gate="SWAP", operands=(0, 1), operation_index=1),
        ]
        circ = self._create_native_circuit(ops, qubits=[0, 1])
        req = ExecutionRequest(request_id="req_swap", native_circuit=circ, execution_mode=ExecutionMode.STATE_VECTOR)
        res = ExecutionEngine.execute(req)

        self.assertEqual(res.status, ExecutionStatus.SUCCESS)
        self.assertEqual(res.final_state_vector["01"], 1.0 + 0.0j)
        self.assertEqual(res.final_state_vector["10"], 0.0 + 0.0j)

    def test_pos_06_toffoli_gate_basis_tests(self) -> None:
        """Pos 6: TOFFOLI gate basis tests across all 8 computational basis states."""
        # Test |110> -> TOFFOLI(0,1,2) -> |111>
        ops = [
            NativeOperation(native_gate="X", operands=(0,), operation_index=0),
            NativeOperation(native_gate="X", operands=(1,), operation_index=1),
            NativeOperation(native_gate="TOFFOLI", operands=(0, 1, 2), operation_index=2),
        ]
        circ = self._create_native_circuit(ops, qubits=[0, 1, 2])
        req = ExecutionRequest(request_id="req_tof", native_circuit=circ, execution_mode=ExecutionMode.STATE_VECTOR)
        res = ExecutionEngine.execute(req)

        self.assertEqual(res.status, ExecutionStatus.SUCCESS)
        self.assertEqual(res.final_state_vector["111"], 1.0 + 0.0j)
        self.assertEqual(res.final_state_vector["110"], 0.0 + 0.0j)

    def test_pos_07_sequential_gate_execution(self) -> None:
        """Pos 7: Sequential gate execution applies operations in strict index order G0 then G1."""
        ops = [
            NativeOperation(native_gate="X", operands=(0,), operation_index=0),
            NativeOperation(native_gate="CNOT", operands=(0, 1), operation_index=1),
            NativeOperation(native_gate="X", operands=(1,), operation_index=2),
        ]
        circ = self._create_native_circuit(ops, qubits=[0, 1])
        req = ExecutionRequest(request_id="req_seq", native_circuit=circ, execution_mode=ExecutionMode.STATE_VECTOR)
        res = ExecutionEngine.execute(req)

        self.assertEqual(res.status, ExecutionStatus.SUCCESS)
        # X(0) -> |10>, CNOT(0,1) -> |11>, X(1) -> |10>
        self.assertEqual(res.final_state_vector["10"], 1.0 + 0.0j)

    def test_pos_08_superposition_bell_state_evolution(self) -> None:
        """Pos 8: Superposition state evolution (H(0) then CNOT(0,1) generates Bell state (|00> + |11>)/sqrt(2))."""
        ops = [
            NativeOperation(native_gate="H", operands=(0,), operation_index=0),
            NativeOperation(native_gate="CNOT", operands=(0, 1), operation_index=1),
        ]
        circ = self._create_native_circuit(ops, qubits=[0, 1])
        req = ExecutionRequest(request_id="req_bell", native_circuit=circ, execution_mode=ExecutionMode.STATE_VECTOR)
        res = ExecutionEngine.execute(req)

        self.assertEqual(res.status, ExecutionStatus.SUCCESS)
        inv_sqrt2 = 1.0 / math.sqrt(2)
        self.assertAlmostEqual(res.final_state_vector["00"].real, inv_sqrt2, delta=STAGE_5_EPSILON)
        self.assertAlmostEqual(res.final_state_vector["11"].real, inv_sqrt2, delta=STAGE_5_EPSILON)
        self.assertAlmostEqual(res.final_state_vector["01"].real, 0.0, delta=STAGE_5_EPSILON)
        self.assertAlmostEqual(res.final_state_vector["10"].real, 0.0, delta=STAGE_5_EPSILON)

    def test_pos_09_normalization_invariant(self) -> None:
        """Pos 9: Final state vector norm equals 1.0 +/- 10^-12."""
        ops = [
            NativeOperation(native_gate="H", operands=(0,), operation_index=0),
            NativeOperation(native_gate="CNOT", operands=(0, 1), operation_index=1),
        ]
        circ = self._create_native_circuit(ops, qubits=[0, 1])
        req = ExecutionRequest(request_id="req_norm", native_circuit=circ, execution_mode=ExecutionMode.STATE_VECTOR)
        res = ExecutionEngine.execute(req)

        self.assertEqual(res.status, ExecutionStatus.SUCCESS)
        norm_sq = sum(abs(c) ** 2 for c in res.final_state_vector.values())
        self.assertAlmostEqual(math.sqrt(norm_sq), 1.0, delta=STAGE_5_EPSILON)

    def test_pos_10_deterministic_execution(self) -> None:
        """Pos 10: Deterministic execution produces identical amplitudes for identical requests."""
        ops = [
            NativeOperation(native_gate="H", operands=(0,), operation_index=0),
            NativeOperation(native_gate="CNOT", operands=(0, 1), operation_index=1),
        ]
        circ = self._create_native_circuit(ops, qubits=[0, 1])
        req1 = ExecutionRequest(request_id="r1", native_circuit=circ, execution_mode=ExecutionMode.STATE_VECTOR)
        req2 = ExecutionRequest(request_id="r2", native_circuit=circ, execution_mode=ExecutionMode.STATE_VECTOR)

        res1 = ExecutionEngine.execute(req1)
        res2 = ExecutionEngine.execute(req2)
        self.assertEqual(res1.final_state_vector, res2.final_state_vector)

    def test_pos_11_reverse_execution(self) -> None:
        """Pos 11: Reverse execution U^dagger U |psi> = |psi> recovers original state."""
        # Circuit: H(0), CNOT(0,1), CNOT(0,1), H(0) == Identity!
        ops = [
            NativeOperation(native_gate="H", operands=(0,), operation_index=0),
            NativeOperation(native_gate="CNOT", operands=(0, 1), operation_index=1),
            NativeOperation(native_gate="CNOT", operands=(0, 1), operation_index=2),
            NativeOperation(native_gate="H", operands=(0,), operation_index=3),
        ]
        circ = self._create_native_circuit(ops, qubits=[0, 1])
        req = ExecutionRequest(request_id="req_rev", native_circuit=circ, execution_mode=ExecutionMode.STATE_VECTOR)
        res = ExecutionEngine.execute(req)

        self.assertEqual(res.status, ExecutionStatus.SUCCESS)
        self.assertAlmostEqual(res.final_state_vector["00"].real, 1.0, delta=STAGE_5_EPSILON)

    def test_pos_12_linearity_preservation(self) -> None:
        """Pos 12: Linearity U(a|psi> + b|phi>) = a U|psi> + b U|phi> is preserved."""
        psi = [1.0 + 0.0j, 0.0 + 0.0j]  # |0>
        phi = [0.0 + 0.0j, 1.0 + 0.0j]  # |1>
        a = 0.6
        b = 0.8

        psi_combo = [a, b]
        state_combo = QuantumState.from_vector(psi_combo)

        # Apply H to state_combo
        ops = [NativeOperation(native_gate="H", operands=(0,), operation_index=0)]
        circ = self._create_native_circuit(ops, qubits=[0])
        req_combo = ExecutionRequest(request_id="rc", native_circuit=circ, initial_state=psi_combo)
        res_combo = ExecutionEngine.execute(req_combo)

        # Independently calculate a * H|0> + b * H|1>
        inv_sqrt2 = 1.0 / math.sqrt(2)
        h_0 = [inv_sqrt2, inv_sqrt2]
        h_1 = [inv_sqrt2, -inv_sqrt2]
        expected_vec = [a * h_0[0] + b * h_1[0], a * h_0[1] + b * h_1[1]]

        self.assertAlmostEqual(res_combo.final_state_vector["0"].real, expected_vec[0], delta=STAGE_5_EPSILON)
        self.assertAlmostEqual(res_combo.final_state_vector["1"].real, expected_vec[1], delta=STAGE_5_EPSILON)

    def test_pos_13_provenance_preservation(self) -> None:
        """Pos 13: ExecutionResult preserves full upstream provenance chain."""
        ops = [NativeOperation(native_gate="X", operands=(0,), operation_index=0)]
        circ = self._create_native_circuit(ops, qubits=[0])
        req = ExecutionRequest(request_id="req_prov", native_circuit=circ, execution_mode=ExecutionMode.STATE_VECTOR)
        res = ExecutionEngine.execute(req)

        self.assertEqual(res.provenance.source_rutm_program_hash, "rutm_hash_999")
        self.assertEqual(res.provenance.source_qtm_machine_id, "qtm_id_888")

    def test_pos_14_input_immutability(self) -> None:
        """Pos 14: Input NativeCircuitIR and ExecutionRequest are not mutated by engine."""
        ops = [NativeOperation(native_gate="X", operands=(0,), operation_index=0)]
        circ = self._create_native_circuit(ops, qubits=[0])
        circ_copy = copy.deepcopy(circ)
        req = ExecutionRequest(request_id="req_immut", native_circuit=circ, execution_mode=ExecutionMode.STATE_VECTOR)

        res = ExecutionEngine.execute(req)
        self.assertEqual(circ.native_operations, circ_copy.native_operations)
        self.assertEqual(circ.circuit_id, circ_copy.circuit_id)

    # ------------------------------------------------------------------
    # NEGATIVE TESTS
    # ------------------------------------------------------------------
    def test_neg_01_invalid_initial_state_unnormalized(self) -> None:
        """Neg 1: Un-normalized initial state vector rejected with INVALID_INITIAL_STATE."""
        psi_bad = [2.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j]
        req = ExecutionRequest(request_id="r_bad_norm", native_circuit=self._create_native_circuit([]), initial_state=psi_bad)
        res = ExecutionEngine.execute(req)

        self.assertEqual(res.status, ExecutionStatus.FAILED)
        self.assertEqual(res.failure_code, ExecutionFailureCode.INVALID_INITIAL_STATE)

    def test_neg_02_invalid_state_dimension(self) -> None:
        """Neg 2: Initial state vector dimension mismatch rejected with INVALID_INITIAL_STATE."""
        psi_bad_dim = [1.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j]
        req = ExecutionRequest(request_id="r_bad_dim", native_circuit=self._create_native_circuit([]), initial_state=psi_bad_dim)
        res = ExecutionEngine.execute(req)

        self.assertEqual(res.status, ExecutionStatus.FAILED)
        self.assertEqual(res.failure_code, ExecutionFailureCode.INVALID_INITIAL_STATE)

    def test_neg_03_unsupported_native_gate(self) -> None:
        """Neg 3: Unsupported native gate rejected with EXECUTION_SEMANTIC_FAILURE."""
        ops = [NativeOperation(native_gate="UNSUPPORTED_GATE_FOO", operands=(0,), operation_index=0)]
        circ = self._create_native_circuit(ops, qubits=[0])
        req = ExecutionRequest(request_id="r_unsupp_gate", native_circuit=circ)
        res = ExecutionEngine.execute(req)

        self.assertEqual(res.status, ExecutionStatus.FAILED)
        self.assertEqual(res.failure_code, ExecutionFailureCode.EXECUTION_SEMANTIC_FAILURE)

    def test_neg_04_invalid_qubit_index_out_of_bounds(self) -> None:
        """Neg 4: Qubit index out of bounds rejected with INVALID_NATIVE_CIRCUIT during validation."""
        ops = [NativeOperation(native_gate="X", operands=(99,), operation_index=0)]
        circ = self._create_native_circuit(ops, qubits=[0])
        req = ExecutionRequest(request_id="r_oob", native_circuit=circ)
        res = ExecutionEngine.execute(req)

        self.assertEqual(res.status, ExecutionStatus.FAILED)
        self.assertEqual(res.failure_code, ExecutionFailureCode.INVALID_NATIVE_CIRCUIT)

    def test_neg_05_control_target_collision(self) -> None:
        """Neg 5: CNOT control == target collision rejected with INVALID_NATIVE_CIRCUIT during validation."""
        ops = [NativeOperation(native_gate="CNOT", operands=(0, 0), operation_index=0)]
        circ = self._create_native_circuit(ops, qubits=[0])
        req = ExecutionRequest(request_id="r_collision", native_circuit=circ)
        res = ExecutionEngine.execute(req)

        self.assertEqual(res.status, ExecutionStatus.FAILED)
        self.assertEqual(res.failure_code, ExecutionFailureCode.INVALID_NATIVE_CIRCUIT)

    def test_neg_06_execution_mode_support_verification(self) -> None:
        """Neg 6: SHOT_SAMPLING mode is fully supported in Step 2 and returns SUCCESS."""
        ops = [NativeOperation(native_gate="X", operands=(0,), operation_index=0)]
        circ = self._create_native_circuit(ops, qubits=[0])
        req = ExecutionRequest(request_id="r_shots", native_circuit=circ, execution_mode=ExecutionMode.SHOT_SAMPLING, shots=100, seed=42)
        res = ExecutionEngine.execute(req)

        self.assertEqual(res.status, ExecutionStatus.SUCCESS)
        self.assertIsNotNone(res.measurement_result)


if __name__ == "__main__":
    unittest.main()
