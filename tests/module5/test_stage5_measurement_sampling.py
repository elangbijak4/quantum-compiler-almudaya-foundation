"""
Module 5 Stage 5 Step 2 Unit Test Suite — Measurement & Seeded Shot Sampling.

Tests computational-basis probability extraction, local PRNG seeded shot sampling,
execution mode handling (STATE_VECTOR, SHOT_SAMPLING, STATE_VECTOR_AND_SHOTS),
reproducibility, invariants, failure domains, and serialization contracts.
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
    STAGE_5_EPSILON,
    serialize_execution_result,
    deserialize_execution_result,
)


class TestStage5MeasurementSampling(unittest.TestCase):
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
            source_rutm_program_hash="rutm_hash_m2",
            source_qtm_machine_id="qtm_id_m2",
            logical_circuit_id="log_c2",
            physical_circuit_id="phys_c2",
        )

        self.adapter = ReferenceBackendAdapter()

    def _create_native_circuit(self, native_ops: list, qubits: list = [0, 1]) -> NativeCircuitIR:
        return NativeCircuitIR(
            circuit_id="n_circ_m2",
            backend_id="reference_simulator",
            backend_version="1.0.0",
            qubits=qubits,
            native_operations=native_ops,
            input_mapping=self.mapping,
            output_mapping=self.mapping,
            provenance=self.provenance,
        )

    # ------------------------------------------------------------------
    # POSITIVE TESTS (17)
    # ------------------------------------------------------------------
    def test_pos_01_probability_extraction(self) -> None:
        """Pos 1: Analytical probability extraction P(x) = |alpha_x|^2 from QuantumState."""
        state = QuantumState.initialize_zero(2)
        probs = ShotSampler.extract_probabilities(state)
        self.assertEqual(probs["00"], 1.0)
        self.assertEqual(probs["01"], 0.0)
        self.assertEqual(probs["10"], 0.0)
        self.assertEqual(probs["11"], 0.0)

    def test_pos_02_probability_normalization_check(self) -> None:
        """Pos 2: Probability distribution sum equals 1.0 +/- 10^-12."""
        inv_sqrt2 = 1.0 / math.sqrt(2)
        psi_super = [inv_sqrt2, 0.0, 0.0, inv_sqrt2]
        state = QuantumState.from_vector(psi_super)
        probs = ShotSampler.extract_probabilities(state)
        self.assertAlmostEqual(sum(probs.values()), 1.0, delta=STAGE_5_EPSILON)

    def test_pos_03_deterministic_zero_basis_measurement(self) -> None:
        """Pos 3: Deterministic |00> state produces all '00' shots and counts['00'] == shots."""
        circ = self._create_native_circuit([], qubits=[0, 1])
        req = ExecutionRequest(
            request_id="req_det_00",
            native_circuit=circ,
            execution_mode=ExecutionMode.SHOT_SAMPLING,
            shots=500,
            seed=42,
        )
        res = ExecutionEngine.execute(req)
        self.assertEqual(res.status, ExecutionStatus.SUCCESS)
        self.assertEqual(res.measurement_result.shot_count, 500)
        self.assertEqual(res.measurement_result.counts["00"], 500)
        self.assertEqual(res.measurement_result.shot_sequence, ["00"] * 500)

    def test_pos_04_seeded_sampling_reproducibility(self) -> None:
        """Pos 4: Seeded reproducibility: Execute(C, seed=S, N) == Execute(C, seed=S, N)."""
        ops = [
            NativeOperation(native_gate="H", operands=(0,), operation_index=0),
            NativeOperation(native_gate="CNOT", operands=(0, 1), operation_index=1),
        ]
        circ = self._create_native_circuit(ops, qubits=[0, 1])
        req1 = ExecutionRequest(
            request_id="req_seed_1",
            native_circuit=circ,
            execution_mode=ExecutionMode.SHOT_SAMPLING,
            shots=1000,
            seed=777,
        )
        req2 = ExecutionRequest(
            request_id="req_seed_2",
            native_circuit=circ,
            execution_mode=ExecutionMode.SHOT_SAMPLING,
            shots=1000,
            seed=777,
        )

        res1 = ExecutionEngine.execute(req1)
        res2 = ExecutionEngine.execute(req2)
        self.assertEqual(res1.measurement_result.shot_sequence, res2.measurement_result.shot_sequence)
        self.assertEqual(res1.measurement_result.counts, res2.measurement_result.counts)

    def test_pos_05_06_07_shot_count_and_sequence_invariants(self) -> None:
        """Pos 5, 6, 7: len(shot_sequence) == shots, sum(counts) == shots, shot_count == shots."""
        ops = [NativeOperation(native_gate="H", operands=(0,), operation_index=0)]
        circ = self._create_native_circuit(ops, qubits=[0])
        req = ExecutionRequest(
            request_id="req_inv",
            native_circuit=circ,
            execution_mode=ExecutionMode.SHOT_SAMPLING,
            shots=350,
            seed=123,
        )
        res = ExecutionEngine.execute(req)

        meas = res.measurement_result
        self.assertEqual(meas.shot_count, 350)
        self.assertEqual(len(meas.shot_sequence), 350)
        self.assertEqual(sum(meas.counts.values()), 350)

    def test_pos_08_bell_state_sampling(self) -> None:
        """Pos 8: Bell state sampling produces zero counts for '01' and '10'."""
        ops = [
            NativeOperation(native_gate="H", operands=(0,), operation_index=0),
            NativeOperation(native_gate="CNOT", operands=(0, 1), operation_index=1),
        ]
        circ = self._create_native_circuit(ops, qubits=[0, 1])
        req = ExecutionRequest(
            request_id="req_bell_sample",
            native_circuit=circ,
            execution_mode=ExecutionMode.SHOT_SAMPLING,
            shots=1000,
            seed=42,
        )
        res = ExecutionEngine.execute(req)

        meas = res.measurement_result
        self.assertNotIn("01", meas.counts)
        self.assertNotIn("10", meas.counts)
        self.assertEqual(meas.counts.get("00", 0) + meas.counts.get("11", 0), 1000)

    def test_pos_09_uniform_superposition_sampling(self) -> None:
        """Pos 9: Uniform superposition state |++> produces analytical P(x) = 0.25 for all 4 states."""
        ops = [
            NativeOperation(native_gate="H", operands=(0,), operation_index=0),
            NativeOperation(native_gate="H", operands=(1,), operation_index=1),
        ]
        circ = self._create_native_circuit(ops, qubits=[0, 1])
        req = ExecutionRequest(
            request_id="req_unif",
            native_circuit=circ,
            execution_mode=ExecutionMode.SHOT_SAMPLING,
            shots=1000,
            seed=42,
        )
        res = ExecutionEngine.execute(req)

        meas = res.measurement_result
        for b in ["00", "01", "10", "11"]:
            self.assertAlmostEqual(meas.probabilities[b], 0.25, delta=STAGE_5_EPSILON)

    def test_pos_10_state_vector_mode_unchanged(self) -> None:
        """Pos 10: STATE_VECTOR mode returns final_state_vector and measurement_result == None."""
        ops = [NativeOperation(native_gate="X", operands=(0,), operation_index=0)]
        circ = self._create_native_circuit(ops, qubits=[0])
        req = ExecutionRequest(request_id="req_sv_only", native_circuit=circ, execution_mode=ExecutionMode.STATE_VECTOR)
        res = ExecutionEngine.execute(req)

        self.assertEqual(res.status, ExecutionStatus.SUCCESS)
        self.assertIsNotNone(res.final_state_vector)
        self.assertIsNone(res.measurement_result)

    def test_pos_11_shot_sampling_mode_result(self) -> None:
        """Pos 11: SHOT_SAMPLING mode returns measurement_result and final_state_vector == None."""
        ops = [NativeOperation(native_gate="X", operands=(0,), operation_index=0)]
        circ = self._create_native_circuit(ops, qubits=[0])
        req = ExecutionRequest(
            request_id="req_shots_only",
            native_circuit=circ,
            execution_mode=ExecutionMode.SHOT_SAMPLING,
            shots=100,
            seed=42,
        )
        res = ExecutionEngine.execute(req)

        self.assertEqual(res.status, ExecutionStatus.SUCCESS)
        self.assertIsNotNone(res.measurement_result)
        self.assertIsNone(res.final_state_vector)

    def test_pos_12_state_vector_and_shots_mode_result(self) -> None:
        """Pos 12: STATE_VECTOR_AND_SHOTS mode returns BOTH final_state_vector and measurement_result."""
        ops = [NativeOperation(native_gate="X", operands=(0,), operation_index=0)]
        circ = self._create_native_circuit(ops, qubits=[0])
        req = ExecutionRequest(
            request_id="req_both",
            native_circuit=circ,
            execution_mode=ExecutionMode.STATE_VECTOR_AND_SHOTS,
            shots=100,
            seed=42,
        )
        res = ExecutionEngine.execute(req)

        self.assertEqual(res.status, ExecutionStatus.SUCCESS)
        self.assertIsNotNone(res.final_state_vector)
        self.assertIsNotNone(res.measurement_result)

    def test_pos_13_probability_seed_independence(self) -> None:
        """Pos 13: Analytical probabilities P_s1(x) == P_s2(x) regardless of seed."""
        ops = [NativeOperation(native_gate="H", operands=(0,), operation_index=0)]
        circ = self._create_native_circuit(ops, qubits=[0])
        req1 = ExecutionRequest(request_id="r1", native_circuit=circ, execution_mode=ExecutionMode.SHOT_SAMPLING, shots=100, seed=111)
        req2 = ExecutionRequest(request_id="r2", native_circuit=circ, execution_mode=ExecutionMode.SHOT_SAMPLING, shots=100, seed=999)

        res1 = ExecutionEngine.execute(req1)
        res2 = ExecutionEngine.execute(req2)
        self.assertEqual(res1.measurement_result.probabilities, res2.measurement_result.probabilities)

    def test_pos_14_provenance_and_seed_preservation(self) -> None:
        """Pos 14: MeasurementResult.seed and upstream provenance are preserved."""
        ops = [NativeOperation(native_gate="X", operands=(0,), operation_index=0)]
        circ = self._create_native_circuit(ops, qubits=[0])
        req = ExecutionRequest(request_id="r_prov_seed", native_circuit=circ, execution_mode=ExecutionMode.SHOT_SAMPLING, shots=50, seed=888)
        res = ExecutionEngine.execute(req)

        self.assertEqual(res.measurement_result.seed, 888)
        self.assertEqual(res.provenance.source_rutm_program_hash, "rutm_hash_m2")

    def test_pos_15_input_immutability(self) -> None:
        """Pos 15: Input ExecutionRequest and NativeCircuitIR are not mutated during sampling."""
        ops = [NativeOperation(native_gate="X", operands=(0,), operation_index=0)]
        circ = self._create_native_circuit(ops, qubits=[0])
        circ_copy = copy.deepcopy(circ)
        req = ExecutionRequest(request_id="req_immut_sample", native_circuit=circ, execution_mode=ExecutionMode.SHOT_SAMPLING, shots=100, seed=42)

        res = ExecutionEngine.execute(req)
        self.assertEqual(circ.native_operations, circ_copy.native_operations)

    def test_pos_16_17_serialization_round_trip_and_determinism(self) -> None:
        """Pos 16 & 17: Canonical JSON serialization round-trip and deterministic serialization for seeded ExecutionResult."""
        ops = [
            NativeOperation(native_gate="H", operands=(0,), operation_index=0),
            NativeOperation(native_gate="CNOT", operands=(0, 1), operation_index=1),
        ]
        circ = self._create_native_circuit(ops, qubits=[0, 1])
        req = ExecutionRequest(request_id="r_ser", native_circuit=circ, execution_mode=ExecutionMode.STATE_VECTOR_AND_SHOTS, shots=200, seed=555)

        res1 = ExecutionEngine.execute(req)
        s1 = serialize_execution_result(res1)
        deser = deserialize_execution_result(s1)
        s2 = serialize_execution_result(deser)
        self.assertEqual(s1, s2)

    # ------------------------------------------------------------------
    # NEGATIVE TESTS (8)
    # ------------------------------------------------------------------
    def test_neg_01_shots_zero(self) -> None:
        """Neg 1: shots == 0 rejected with MEASUREMENT_FAILURE."""
        circ = self._create_native_circuit([], qubits=[0])
        req = ExecutionRequest(request_id="r_s0", native_circuit=circ, execution_mode=ExecutionMode.SHOT_SAMPLING, shots=0)
        res = ExecutionEngine.execute(req)

        self.assertEqual(res.status, ExecutionStatus.FAILED)
        self.assertEqual(res.failure_code, ExecutionFailureCode.MEASUREMENT_FAILURE)

    def test_neg_02_shots_negative(self) -> None:
        """Neg 2: shots < 0 rejected with MEASUREMENT_FAILURE."""
        circ = self._create_native_circuit([], qubits=[0])
        req = ExecutionRequest(request_id="r_s_neg", native_circuit=circ, execution_mode=ExecutionMode.SHOT_SAMPLING, shots=-50)
        res = ExecutionEngine.execute(req)

        self.assertEqual(res.status, ExecutionStatus.FAILED)
        self.assertEqual(res.failure_code, ExecutionFailureCode.MEASUREMENT_FAILURE)

    def test_neg_03_invalid_probability_distribution_sum(self) -> None:
        """Neg 3: Invalid state with non-normalized probabilities raises NUMERICAL_VERIFICATION_FAILURE."""
        psi_bad = [2.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j]
        circ = self._create_native_circuit([], qubits=[0, 1])
        req = ExecutionRequest(request_id="r_bad_p", native_circuit=circ, execution_mode=ExecutionMode.SHOT_SAMPLING, initial_state=psi_bad)
        res = ExecutionEngine.execute(req)

        self.assertEqual(res.status, ExecutionStatus.FAILED)
        self.assertEqual(res.failure_code, ExecutionFailureCode.INVALID_INITIAL_STATE)

    def test_neg_04_malformed_measurement_result(self) -> None:
        """Neg 4: MeasurementResult with negative shot count raises ValueError."""
        with self.assertRaises(ValueError):
            MeasurementResult(shot_count=-10)

    def test_neg_05_unsupported_backend(self) -> None:
        """Neg 5: Unsupported backend ID rejected with FORBIDDEN_HARDWARE_REQUEST."""
        circ = self._create_native_circuit([], qubits=[0])
        req = ExecutionRequest(request_id="r_backend", native_circuit=circ, target_backend_id="UNKNOWN_HARDWARE_QPU")
        res = ExecutionEngine.execute(req)

        self.assertEqual(res.status, ExecutionStatus.FAILED)
        self.assertEqual(res.failure_code, ExecutionFailureCode.FORBIDDEN_HARDWARE_REQUEST)

    def test_neg_06_invalid_execution_request(self) -> None:
        """Neg 6: Invalid ExecutionRequest with empty request_id rejected with INVALID_REQUEST."""
        circ = self._create_native_circuit([], qubits=[0])
        req = ExecutionRequest(request_id="", native_circuit=circ)
        res = ExecutionEngine.execute(req)

        self.assertEqual(res.status, ExecutionStatus.FAILED)
        self.assertEqual(res.failure_code, ExecutionFailureCode.INVALID_REQUEST)

    def test_neg_07_invalid_native_circuit(self) -> None:
        """Neg 7: ExecutionRequest with invalid NativeCircuitIR rejected with INVALID_NATIVE_CIRCUIT."""
        ops = [NativeOperation(native_gate="X", operands=(99,), operation_index=0)]
        circ = self._create_native_circuit(ops, qubits=[0])
        req = ExecutionRequest(request_id="r_bad_c", native_circuit=circ)
        res = ExecutionEngine.execute(req)

        self.assertEqual(res.status, ExecutionStatus.FAILED)
        self.assertEqual(res.failure_code, ExecutionFailureCode.INVALID_NATIVE_CIRCUIT)

    def test_neg_08_sampling_failure_localization(self) -> None:
        """Neg 8: Direct call to ShotSampler with shots <= 0 raises ValueError."""
        state = QuantumState.initialize_zero(1)
        with self.assertRaises(ValueError):
            ShotSampler.sample_shots(state, shots=0)


if __name__ == "__main__":
    unittest.main()
