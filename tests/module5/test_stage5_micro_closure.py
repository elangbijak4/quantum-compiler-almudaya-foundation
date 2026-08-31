"""
Module 5 Stage 5 Micro-Closure Test Suite.

Validates the Stage 5 Execution Model, Result Contract, Boundary Rules, Failure Domains,
and Serialization Contracts across positive and negative paths.
"""

import unittest
import math
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
    ExecutionMode,
    ExecutionStatus,
    ExecutionFailureCode,
    MeasurementResult,
    ExecutionRequest,
    ExecutionResult,
    BackendIdentity,
    BackendType,
    validate_execution_request,
    validate_execution_result,
    serialize_execution_request,
    deserialize_execution_request,
    serialize_execution_result,
    deserialize_execution_result,
)


class TestStage5MicroClosure(unittest.TestCase):
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

        self.g0 = PhysicalGateOperation(gate_type="X", target_node=0, operation_index=0)
        self.g1 = PhysicalGateOperation(gate_type="CNOT", control_nodes=(0,), target_node=1, operation_index=1)

        self.provenance = ExecutionProvenance(
            source_rutm_program_hash="hash_abc",
            source_qtm_machine_id="qtm_xyz",
            logical_circuit_id="log_c1",
            physical_circuit_id="phys_c1",
        )

        self.physical_circuit = PhysicalCircuitIR(
            physical_circuit_id="phys_c1",
            source_logical_circuit_id="log_c1",
            physical_qubits=[self.p0, self.p1],
            gates=[self.g0, self.g1],
            mapping=self.mapping,
            topology=self.topology,
            provenance=self.provenance,
        )

        self.adapter = ReferenceBackendAdapter()
        trans_res = NativeTranslator.translate(self.physical_circuit, self.adapter)
        self.assertTrue(trans_res.success)
        self.native_circuit = trans_res.native_circuit

    # ------------------------------------------------------------------
    # POSITIVE MICRO-CLOSURE TESTS
    # ------------------------------------------------------------------
    def test_pos_01_execution_mode_validity(self) -> None:
        """Pos 1: All 3 baseline execution modes are valid."""
        modes = [ExecutionMode.STATE_VECTOR, ExecutionMode.SHOT_SAMPLING, ExecutionMode.STATE_VECTOR_AND_SHOTS]
        for mode in modes:
            req = ExecutionRequest(request_id="r1", native_circuit=self.native_circuit, execution_mode=mode)
            val_res = validate_execution_request(req)
            self.assertTrue(val_res.valid)

    def test_pos_02_explicit_initial_state_validation(self) -> None:
        """Pos 2: Explicit normalized initial state vector |00> is valid."""
        psi_0 = [1.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j]
        req = ExecutionRequest(request_id="r2", native_circuit=self.native_circuit, initial_state=psi_0)
        val_res = validate_execution_request(req)
        self.assertTrue(val_res.valid)

    def test_pos_03_positive_shot_count_validation(self) -> None:
        """Pos 3: Positive shot count (N_shots = 1000) is valid."""
        req = ExecutionRequest(
            request_id="r3",
            native_circuit=self.native_circuit,
            execution_mode=ExecutionMode.SHOT_SAMPLING,
            shots=1000,
            seed=42,
        )
        val_res = validate_execution_request(req)
        self.assertTrue(val_res.valid)

    def test_pos_04_execution_result_schema_and_counts(self) -> None:
        """Pos 4: Valid ExecutionResult payload passes validation."""
        meas = MeasurementResult(
            probabilities={"00": 0.5, "11": 0.5},
            counts={"00": 500, "11": 500},
            shot_sequence=["00"] * 500 + ["11"] * 500,
            shot_count=1000,
            seed=42,
        )
        b_id = self.adapter.get_backend_identity()
        res = ExecutionResult(
            request_id="r4",
            status=ExecutionStatus.SUCCESS,
            execution_mode=ExecutionMode.SHOT_SAMPLING,
            backend_identity=b_id,
            measurement_result=meas,
            provenance=self.provenance,
        )
        val_res = validate_execution_result(res)
        self.assertTrue(val_res.valid)

    def test_pos_05_request_serialization_round_trip(self) -> None:
        """Pos 5: ExecutionRequest round-trip canonical serialization."""
        req = ExecutionRequest(
            request_id="req_rt",
            native_circuit=self.native_circuit,
            execution_mode=ExecutionMode.STATE_VECTOR_AND_SHOTS,
            shots=2000,
            seed=12345,
        )
        s_json = serialize_execution_request(req)
        deser = deserialize_execution_request(s_json)
        self.assertEqual(deser.request_id, req.request_id)
        self.assertEqual(deser.execution_mode, req.execution_mode)
        self.assertEqual(deser.shots, req.shots)
        self.assertEqual(deser.seed, req.seed)

    def test_pos_06_result_serialization_round_trip(self) -> None:
        """Pos 6: ExecutionResult round-trip canonical serialization."""
        meas = MeasurementResult(
            probabilities={"00": 1.0},
            counts={"00": 100},
            shot_sequence=["00"] * 100,
            shot_count=100,
            seed=99,
        )
        b_id = self.adapter.get_backend_identity()
        res = ExecutionResult(
            request_id="res_rt",
            status=ExecutionStatus.SUCCESS,
            execution_mode=ExecutionMode.SHOT_SAMPLING,
            backend_identity=b_id,
            measurement_result=meas,
            provenance=self.provenance,
        )
        s_json = serialize_execution_result(res)
        deser = deserialize_execution_result(s_json)
        self.assertEqual(deser.request_id, res.request_id)
        self.assertEqual(deser.status, res.status)
        self.assertEqual(deser.measurement_result.shot_count, 100)

    # ------------------------------------------------------------------
    # NEGATIVE MICRO-CLOSURE TESTS
    # ------------------------------------------------------------------
    def test_neg_01_empty_request_id(self) -> None:
        """Neg 1: Empty request_id rejected."""
        req = ExecutionRequest(request_id="", native_circuit=self.native_circuit)
        val_res = validate_execution_request(req)
        self.assertFalse(val_res.valid)
        self.assertEqual(val_res.failure_code, ExecutionFailureCode.INVALID_REQUEST)

    def test_neg_02_dimension_mismatch(self) -> None:
        """Neg 2: Initial state vector dimension mismatch (3 instead of 4) rejected."""
        psi_bad = [1.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j]
        req = ExecutionRequest(request_id="r_bad_dim", native_circuit=self.native_circuit, initial_state=psi_bad)
        val_res = validate_execution_request(req)
        self.assertFalse(val_res.valid)
        self.assertEqual(val_res.failure_code, ExecutionFailureCode.INVALID_INITIAL_STATE)

    def test_neg_03_unnormalized_initial_state(self) -> None:
        """Neg 3: Un-normalized initial state vector (norm = 2.0) rejected."""
        psi_unnorm = [2.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j]
        req = ExecutionRequest(request_id="r_unnorm", native_circuit=self.native_circuit, initial_state=psi_unnorm)
        val_res = validate_execution_request(req)
        self.assertFalse(val_res.valid)
        self.assertEqual(val_res.failure_code, ExecutionFailureCode.INVALID_INITIAL_STATE)

    def test_neg_04_nan_initial_state(self) -> None:
        """Neg 4: NaN amplitude in initial state vector rejected."""
        psi_nan = [complex(float("nan"), 0.0), 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j]
        req = ExecutionRequest(request_id="r_nan", native_circuit=self.native_circuit, initial_state=psi_nan)
        val_res = validate_execution_request(req)
        self.assertFalse(val_res.valid)
        self.assertEqual(val_res.failure_code, ExecutionFailureCode.INVALID_INITIAL_STATE)

    def test_neg_05_non_positive_shot_count(self) -> None:
        """Neg 5: Non-positive shot count (shots = 0) rejected for SHOT_SAMPLING."""
        req = ExecutionRequest(
            request_id="r_shots",
            native_circuit=self.native_circuit,
            execution_mode=ExecutionMode.SHOT_SAMPLING,
            shots=0,
        )
        val_res = validate_execution_request(req)
        self.assertFalse(val_res.valid)
        self.assertEqual(val_res.failure_code, ExecutionFailureCode.MEASUREMENT_FAILURE)

    def test_neg_06_forbidden_hardware_backend(self) -> None:
        """Neg 6: Forbidden external hardware backend request rejected."""
        req = ExecutionRequest(
            request_id="r_hw",
            native_circuit=self.native_circuit,
            target_backend_id="EXTERNAL_QPU_DEVICE",
        )
        val_res = validate_execution_request(req)
        self.assertFalse(val_res.valid)
        self.assertEqual(val_res.failure_code, ExecutionFailureCode.FORBIDDEN_HARDWARE_REQUEST)

    def test_neg_07_result_counts_sum_mismatch(self) -> None:
        """Neg 7: ExecutionResult with counts sum mismatch rejected."""
        meas = MeasurementResult(
            probabilities={"00": 1.0},
            counts={"00": 90},  # Sum is 90, but shot_count is 100!
            shot_sequence=["00"] * 90,
            shot_count=100,
        )
        b_id = self.adapter.get_backend_identity()
        res = ExecutionResult(
            request_id="res_bad_sum",
            status=ExecutionStatus.SUCCESS,
            execution_mode=ExecutionMode.SHOT_SAMPLING,
            backend_identity=b_id,
            measurement_result=meas,
        )
        val_res = validate_execution_result(res)
        self.assertFalse(val_res.valid)

    def test_neg_08_schema_version_mismatch(self) -> None:
        """Neg 8: Schema version mismatch in JSON serialization rejected."""
        req = ExecutionRequest(request_id="req_schema", native_circuit=self.native_circuit)
        s_json = serialize_execution_request(req)
        bad_json = s_json.replace('"1.0.0"', '"9.9.9"')
        with self.assertRaises(ValueError):
            deserialize_execution_request(bad_json)


if __name__ == "__main__":
    unittest.main()
