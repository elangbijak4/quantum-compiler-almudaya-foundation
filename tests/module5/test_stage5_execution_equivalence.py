"""
Module 5 Stage 5 Step 3 Unit Test Suite — Execution Equivalence & Result Verification Gate.

Verifies end-to-end semantic consistency across the reference state-vector execution pipeline:
- State vector equivalence & global phase policy
- Probability equivalence & single-pass cross-validation
- Measurement consistency & seeded reproducibility
- Reverse execution (U^\dagger U |psi> = |psi>)
- Provenance integrity & input immutability
- Serialization round-trip & deterministic output equality
- Comprehensive failure domain localization
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
    MeasurementResult,
    ExecutionRequest,
    ExecutionResult,
    ExecutionEngine,
    ShotSampler,
    ExecutionEquivalenceReport,
    ExecutionVerifier,
    STAGE_5_EPSILON,
    serialize_execution_result,
    deserialize_execution_result,
)


class TestStage5ExecutionEquivalence(unittest.TestCase):
    def setUp(self) -> None:
        self.q0 = QubitRef("reg_q", 0)
        self.q1 = QubitRef("reg_q", 1)

        self.p0 = PhysicalQubit(node_id=0)
        self.p1 = PhysicalQubit(node_id=1)

        self.mapping = QubitMapping()
        self.mapping.set_mapping(self.q0, 0)
        self.mapping.set_mapping(self.q1, 1)

        self.topology = DeviceTopology()
        self.topology.add_edge(0, 1)

        self.provenance = ExecutionProvenance(
            source_rutm_program_hash="rutm_hash_eq3",
            source_qtm_machine_id="qtm_id_eq3",
            logical_circuit_id="log_c3",
            physical_circuit_id="phys_c3",
        )

        self.adapter = ReferenceBackendAdapter()

    def _create_native_circuit(self, native_ops: list, qubits: list = [0, 1]) -> NativeCircuitIR:
        return NativeCircuitIR(
            circuit_id="n_circ_eq3",
            backend_id="reference_simulator",
            backend_version="1.0.0",
            qubits=qubits,
            native_operations=native_ops,
            input_mapping=self.mapping,
            output_mapping=self.mapping,
            provenance=self.provenance,
        )

    # ------------------------------------------------------------------
    # POSITIVE TESTS (16)
    # ------------------------------------------------------------------
    def test_pos_01_state_vector_equivalence(self) -> None:
        """Pos 1: State vector numerical equivalence ||psi_actual - psi_expected|| < 10^-12."""
        ops = [NativeOperation(native_gate="X", operands=(0,), operation_index=0)]
        circ = self._create_native_circuit(ops, qubits=[0, 1])
        req = ExecutionRequest(request_id="r_eq1", native_circuit=circ, execution_mode=ExecutionMode.STATE_VECTOR)
        res = ExecutionEngine.execute(req)

        self.assertEqual(res.status, ExecutionStatus.SUCCESS)
        expected = {"00": 0.0, "01": 0.0, "10": 1.0 + 0.0j, "11": 0.0}
        for b, amp in expected.items():
            self.assertAlmostEqual(res.final_state_vector[b].real, amp.real, delta=STAGE_5_EPSILON)
            self.assertAlmostEqual(res.final_state_vector[b].imag, amp.imag, delta=STAGE_5_EPSILON)

    def test_pos_02_probability_equivalence(self) -> None:
        """Pos 2: Probability equivalence P(x) = |alpha_x|^2 analytical distribution."""
        ops = [
            NativeOperation(native_gate="H", operands=(0,), operation_index=0),
            NativeOperation(native_gate="CNOT", operands=(0, 1), operation_index=1),
        ]
        circ = self._create_native_circuit(ops, qubits=[0, 1])
        req = ExecutionRequest(request_id="r_eq2", native_circuit=circ, execution_mode=ExecutionMode.SHOT_SAMPLING, shots=100, seed=42)
        res = ExecutionEngine.execute(req)

        probs = res.measurement_result.probabilities
        self.assertAlmostEqual(probs["00"], 0.5, delta=STAGE_5_EPSILON)
        self.assertAlmostEqual(probs["11"], 0.5, delta=STAGE_5_EPSILON)
        self.assertEqual(probs["01"], 0.0)
        self.assertEqual(probs["10"], 0.0)

    def test_pos_03_state_probability_cross_validation(self) -> None:
        """Pos 3: Single-pass cross-validation P(x) == |alpha_x|^2 in STATE_VECTOR_AND_SHOTS mode."""
        ops = [
            NativeOperation(native_gate="H", operands=(0,), operation_index=0),
            NativeOperation(native_gate="CNOT", operands=(0, 1), operation_index=1),
        ]
        circ = self._create_native_circuit(ops, qubits=[0, 1])
        req = ExecutionRequest(request_id="r_eq3", native_circuit=circ, execution_mode=ExecutionMode.STATE_VECTOR_AND_SHOTS, shots=500, seed=123)
        res = ExecutionEngine.execute(req)

        report = ExecutionVerifier.verify_execution_result(res)
        self.assertTrue(report.valid)
        self.assertTrue(report.cross_validation_verified)

    def test_pos_04_deterministic_basis_state(self) -> None:
        """Pos 4: Deterministic |00> state measurement produces sequence of all '00'."""
        circ = self._create_native_circuit([], qubits=[0, 1])
        req = ExecutionRequest(request_id="r_det", native_circuit=circ, execution_mode=ExecutionMode.SHOT_SAMPLING, shots=200, seed=99)
        res = ExecutionEngine.execute(req)

        self.assertEqual(res.measurement_result.counts["00"], 200)
        self.assertEqual(res.measurement_result.shot_sequence, ["00"] * 200)

    def test_pos_05_bell_state_integration(self) -> None:
        """Pos 5: Bell-state (|00> + |11>)/sqrt(2) sampling yields zero counts for '01' and '10'."""
        ops = [
            NativeOperation(native_gate="H", operands=(0,), operation_index=0),
            NativeOperation(native_gate="CNOT", operands=(0, 1), operation_index=1),
        ]
        circ = self._create_native_circuit(ops, qubits=[0, 1])
        req = ExecutionRequest(request_id="r_bell", native_circuit=circ, execution_mode=ExecutionMode.SHOT_SAMPLING, shots=1000, seed=42)
        res = ExecutionEngine.execute(req)

        meas = res.measurement_result
        self.assertNotIn("01", meas.counts)
        self.assertNotIn("10", meas.counts)
        self.assertEqual(meas.counts["00"] + meas.counts["11"], 1000)

    def test_pos_06_superposition_integration(self) -> None:
        """Pos 6: Multi-qubit superposition |++> analytical P(x) = 0.25 for all basis states."""
        ops = [
            NativeOperation(native_gate="H", operands=(0,), operation_index=0),
            NativeOperation(native_gate="H", operands=(1,), operation_index=1),
        ]
        circ = self._create_native_circuit(ops, qubits=[0, 1])
        req = ExecutionRequest(request_id="r_super", native_circuit=circ, execution_mode=ExecutionMode.SHOT_SAMPLING, shots=800, seed=42)
        res = ExecutionEngine.execute(req)

        report = ExecutionVerifier.verify_execution_result(res)
        self.assertTrue(report.valid)

    def test_pos_07_seeded_reproducibility(self) -> None:
        """Pos 7: Seeded reproducibility: Execute(C, seed=S, N) == Execute(C, seed=S, N)."""
        ops = [NativeOperation(native_gate="H", operands=(0,), operation_index=0)]
        circ = self._create_native_circuit(ops, qubits=[0])
        req1 = ExecutionRequest(request_id="r_rep1", native_circuit=circ, execution_mode=ExecutionMode.SHOT_SAMPLING, shots=500, seed=12345)
        req2 = ExecutionRequest(request_id="r_rep2", native_circuit=circ, execution_mode=ExecutionMode.SHOT_SAMPLING, shots=500, seed=12345)

        res1 = ExecutionEngine.execute(req1)
        res2 = ExecutionEngine.execute(req2)
        self.assertEqual(res1.measurement_result.shot_sequence, res2.measurement_result.shot_sequence)

    def test_pos_08_seed_independent_probabilities(self) -> None:
        """Pos 8: Analytical probabilities P_s1(x) == P_s2(x) independent of random seed."""
        ops = [NativeOperation(native_gate="H", operands=(0,), operation_index=0)]
        circ = self._create_native_circuit(ops, qubits=[0])
        req1 = ExecutionRequest(request_id="r_ind1", native_circuit=circ, execution_mode=ExecutionMode.SHOT_SAMPLING, shots=100, seed=1)
        req2 = ExecutionRequest(request_id="r_ind2", native_circuit=circ, execution_mode=ExecutionMode.SHOT_SAMPLING, shots=100, seed=2)

        res1 = ExecutionEngine.execute(req1)
        res2 = ExecutionEngine.execute(req2)
        self.assertEqual(res1.measurement_result.probabilities, res2.measurement_result.probabilities)

    def test_pos_09_state_vector_result_structure(self) -> None:
        """Pos 9: STATE_VECTOR mode structure: final_state_vector != None, measurement_result == None."""
        ops = [NativeOperation(native_gate="X", operands=(0,), operation_index=0)]
        circ = self._create_native_circuit(ops, qubits=[0])
        req = ExecutionRequest(request_id="r_struct_sv", native_circuit=circ, execution_mode=ExecutionMode.STATE_VECTOR)
        res = ExecutionEngine.execute(req)

        self.assertIsNotNone(res.final_state_vector)
        self.assertIsNone(res.measurement_result)

    def test_pos_10_shot_sampling_result_structure(self) -> None:
        """Pos 10: SHOT_SAMPLING mode structure: measurement_result != None, final_state_vector == None."""
        ops = [NativeOperation(native_gate="X", operands=(0,), operation_index=0)]
        circ = self._create_native_circuit(ops, qubits=[0])
        req = ExecutionRequest(request_id="r_struct_shots", native_circuit=circ, execution_mode=ExecutionMode.SHOT_SAMPLING, shots=50, seed=42)
        res = ExecutionEngine.execute(req)

        self.assertIsNotNone(res.measurement_result)
        self.assertIsNone(res.final_state_vector)

    def test_pos_11_state_vector_and_shots_result_structure(self) -> None:
        """Pos 11: STATE_VECTOR_AND_SHOTS mode structure: BOTH payloads present."""
        ops = [NativeOperation(native_gate="X", operands=(0,), operation_index=0)]
        circ = self._create_native_circuit(ops, qubits=[0])
        req = ExecutionRequest(request_id="r_struct_both", native_circuit=circ, execution_mode=ExecutionMode.STATE_VECTOR_AND_SHOTS, shots=50, seed=42)
        res = ExecutionEngine.execute(req)

        self.assertIsNotNone(res.final_state_vector)
        self.assertIsNotNone(res.measurement_result)

    def test_pos_12_reverse_execution(self) -> None:
        """Pos 12: Reverse execution U^\dagger U |psi> = |psi> within 10^-12."""
        # Circuit: H(0), CNOT(0,1), CNOT(0,1), H(0) == Identity
        ops = [
            NativeOperation(native_gate="H", operands=(0,), operation_index=0),
            NativeOperation(native_gate="CNOT", operands=(0, 1), operation_index=1),
            NativeOperation(native_gate="CNOT", operands=(0, 1), operation_index=2),
            NativeOperation(native_gate="H", operands=(0,), operation_index=3),
        ]
        circ = self._create_native_circuit(ops, qubits=[0, 1])
        req = ExecutionRequest(request_id="r_rev_eq", native_circuit=circ, execution_mode=ExecutionMode.STATE_VECTOR)
        res = ExecutionEngine.execute(req)

        self.assertAlmostEqual(res.final_state_vector["00"].real, 1.0, delta=STAGE_5_EPSILON)

    def test_pos_13_provenance_preservation(self) -> None:
        """Pos 13: Full upstream provenance chain preserved in ExecutionResult."""
        ops = [NativeOperation(native_gate="X", operands=(0,), operation_index=0)]
        circ = self._create_native_circuit(ops, qubits=[0])
        req = ExecutionRequest(request_id="r_prov_eq", native_circuit=circ, execution_mode=ExecutionMode.STATE_VECTOR)
        res = ExecutionEngine.execute(req)

        self.assertEqual(res.provenance.source_rutm_program_hash, "rutm_hash_eq3")
        self.assertEqual(res.provenance.logical_circuit_id, "log_c3")

    def test_pos_14_serialization_round_trip_and_determinism(self) -> None:
        """Pos 14: Serialization round-trip and deterministic string identity."""
        ops = [NativeOperation(native_gate="X", operands=(0,), operation_index=0)]
        circ = self._create_native_circuit(ops, qubits=[0])
        req = ExecutionRequest(request_id="r_ser_eq", native_circuit=circ, execution_mode=ExecutionMode.STATE_VECTOR_AND_SHOTS, shots=100, seed=42)

        res = ExecutionEngine.execute(req)
        s1 = serialize_execution_result(res)
        deser = deserialize_execution_result(s1)
        s2 = serialize_execution_result(deser)
        self.assertEqual(s1, s2)

    def test_pos_15_input_immutability(self) -> None:
        """Pos 15: ExecutionRequest and NativeCircuitIR remain un-mutated."""
        ops = [NativeOperation(native_gate="X", operands=(0,), operation_index=0)]
        circ = self._create_native_circuit(ops, qubits=[0])
        circ_copy = copy.deepcopy(circ)
        req = ExecutionRequest(request_id="r_immut_eq", native_circuit=circ)

        res = ExecutionEngine.execute(req)
        self.assertEqual(circ.native_operations, circ_copy.native_operations)

    def test_pos_16_global_phase_equivalence_verification(self) -> None:
        """Pos 16: Global phase equivalence helper correctly verifies |psi2> = e^(i phi) |psi1>."""
        s1 = {"0": 1.0 + 0.0j, "1": 0.0 + 0.0j}
        # e^(i pi/4) * |0>
        phase_factor = math.cos(math.pi / 4) + 1j * math.sin(math.pi / 4)
        s2 = {"0": phase_factor, "1": 0.0 + 0.0j}

        ok, residual, err = ExecutionVerifier.verify_global_phase_equivalence(s1, s2)
        self.assertTrue(ok)
        self.assertAlmostEqual(residual, 0.0, delta=STAGE_5_EPSILON)

    # ------------------------------------------------------------------
    # NEGATIVE TESTS (10)
    # ------------------------------------------------------------------
    def test_neg_01_malformed_result_verification(self) -> None:
        """Neg 1: ExecutionResult with empty request_id fails ExecutionVerifier."""
        ops = [NativeOperation(native_gate="X", operands=(0,), operation_index=0)]
        circ = self._create_native_circuit(ops, qubits=[0])
        req = ExecutionRequest(request_id="r_empty", native_circuit=circ, execution_mode=ExecutionMode.STATE_VECTOR)
        res = ExecutionEngine.execute(req)
        res.request_id = ""  # Corrupt result

        report = ExecutionVerifier.verify_execution_result(res)
        self.assertFalse(report.valid)

    def test_neg_02_invalid_state_norm_verification(self) -> None:
        """Neg 2: ExecutionResult with un-normalized state fails ExecutionVerifier."""
        s_bad = {"0": 2.0 + 0.0j, "1": 0.0 + 0.0j}
        ok, norm, err = ExecutionVerifier.verify_state_vector_norm(s_bad)
        self.assertFalse(ok)

    def test_neg_03_invalid_probability_normalization_verification(self) -> None:
        """Neg 3: Invalid probability distribution sum fails verifier."""
        ops = [NativeOperation(native_gate="X", operands=(0,), operation_index=0)]
        circ = self._create_native_circuit(ops, qubits=[0])
        req = ExecutionRequest(request_id="r_p_bad", native_circuit=circ, execution_mode=ExecutionMode.SHOT_SAMPLING, shots=100, seed=42)
        res = ExecutionEngine.execute(req)

        res.measurement_result.probabilities["0"] = 0.999  # Corrupt probabilities

        report = ExecutionVerifier.verify_execution_result(res)
        self.assertFalse(report.valid)

    def test_neg_04_inconsistent_state_probability_cross_validation(self) -> None:
        """Neg 4: State-probability cross-validation detects mismatched probabilities."""
        s_dict = {"0": 1.0 + 0.0j, "1": 0.0 + 0.0j}
        meas = MeasurementResult(probabilities={"0": 0.5, "1": 0.5}, counts={"0": 50, "1": 50}, shot_sequence=["0"] * 50 + ["1"] * 50, shot_count=100, seed=1)

        ok, err = ExecutionVerifier.verify_state_probability_cross_validation(s_dict, meas)
        self.assertFalse(ok)

    def test_neg_05_invalid_counts_shot_sum_verification(self) -> None:
        """Neg 5: Count sum mismatch fails ExecutionVerifier."""
        ops = [NativeOperation(native_gate="X", operands=(0,), operation_index=0)]
        circ = self._create_native_circuit(ops, qubits=[0])
        req = ExecutionRequest(request_id="r_c_bad", native_circuit=circ, execution_mode=ExecutionMode.SHOT_SAMPLING, shots=100, seed=42)
        res = ExecutionEngine.execute(req)

        res.measurement_result.counts["1"] = 999  # Corrupt counts sum

        report = ExecutionVerifier.verify_execution_result(res)
        self.assertFalse(report.valid)

    def test_neg_06_broken_provenance_verification(self) -> None:
        """Neg 6: Missing provenance metadata fails ExecutionVerifier."""
        ops = [NativeOperation(native_gate="X", operands=(0,), operation_index=0)]
        circ = self._create_native_circuit(ops, qubits=[0])
        req = ExecutionRequest(request_id="r_no_prov", native_circuit=circ, execution_mode=ExecutionMode.STATE_VECTOR)
        res = ExecutionEngine.execute(req)
        res.provenance = None  # Corrupt provenance

        report = ExecutionVerifier.verify_execution_result(res)
        self.assertFalse(report.valid)

    def test_neg_07_invalid_serialization_corruption(self) -> None:
        """Neg 7: Deserializing invalid JSON raises ValueError or KeyError."""
        with self.assertRaises(Exception):
            deserialize_execution_result("{corrupted_json: true}")

    def test_neg_08_invalid_execution_mode_in_request(self) -> None:
        """Neg 8: ExecutionRequest with invalid execution_mode is rejected during request validation."""
        ops = [NativeOperation(native_gate="X", operands=(0,), operation_index=0)]
        circ = self._create_native_circuit(ops, qubits=[0])
        req = ExecutionRequest(request_id="r_bad_mode", native_circuit=circ, execution_mode="INVALID_MODE")
        res = ExecutionEngine.execute(req)

        self.assertEqual(res.status, ExecutionStatus.FAILED)
        self.assertEqual(res.failure_code, ExecutionFailureCode.INVALID_REQUEST)

    def test_neg_09_invalid_shot_count(self) -> None:
        """Neg 9: shots <= 0 rejected with MEASUREMENT_FAILURE."""
        circ = self._create_native_circuit([], qubits=[0])
        req = ExecutionRequest(request_id="r_neg_shots", native_circuit=circ, execution_mode=ExecutionMode.SHOT_SAMPLING, shots=-10)
        res = ExecutionEngine.execute(req)

        self.assertEqual(res.status, ExecutionStatus.FAILED)
        self.assertEqual(res.failure_code, ExecutionFailureCode.MEASUREMENT_FAILURE)

    def test_neg_10_unsupported_hardware_request(self) -> None:
        """Neg 10: Hardware execution request rejected with FORBIDDEN_HARDWARE_REQUEST."""
        circ = self._create_native_circuit([], qubits=[0])
        req = ExecutionRequest(request_id="r_hw", native_circuit=circ, target_backend_id="ibm_qpu_superconducting")
        res = ExecutionEngine.execute(req)

        self.assertEqual(res.status, ExecutionStatus.FAILED)
        self.assertEqual(res.failure_code, ExecutionFailureCode.FORBIDDEN_HARDWARE_REQUEST)


if __name__ == "__main__":
    unittest.main()
