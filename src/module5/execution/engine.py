"""
Module 5 Stage 5 — Primary Execution Engine (Step 2 Measurement & Seeded Shot Sampling).

Implements the in-process offline ideal reference execution engine supporting:
- STATE_VECTOR
- SHOT_SAMPLING
- STATE_VECTOR_AND_SHOTS
"""

from typing import Dict, List, Optional
import time
from src.module5.backend.reference import create_reference_simulator_capabilities
from src.module5.execution.model import (
    ExecutionRequest,
    ExecutionResult,
    ExecutionMode,
    ExecutionStatus,
    ExecutionFailureCode,
    EPSILON,
)
from src.module5.execution.state import QuantumState
from src.module5.execution.gates import apply_native_operation
from src.module5.execution.sampler import ShotSampler
from src.module5.execution.validator import validate_execution_request, validate_execution_result


class ExecutionEngine:
    """Primary Offline In-Process Reference Execution Engine."""

    @classmethod
    def execute(cls, request: ExecutionRequest) -> ExecutionResult:
        """
        Executes an ExecutionRequest using the offline reference state-vector & measurement engine.
        
        Guarantees:
        1. Single state-vector evolution pass per request (NO double execution).
        2. Exact 100% deterministic state-vector simulation.
        3. Local PRNG seeded shot sampling (Execute(C, seed=S, N) == Execute(C, seed=S, N)).
        4. Analytical probability distribution seed independence (P_s1(x) == P_s2(x)).
        5. Verification of state normalization (norm = 1.0 +/- 10^-12).
        6. Complete provenance preservation.
        """
        start_time = time.perf_counter()

        # 1. Validate ExecutionRequest
        req_val = validate_execution_request(request)
        if not req_val.valid:
            return ExecutionResult(
                request_id=request.request_id,
                status=ExecutionStatus.FAILED,
                execution_mode=request.execution_mode,
                backend_identity=create_reference_simulator_capabilities().identity,
                failure_code=req_val.failure_code or ExecutionFailureCode.INVALID_REQUEST,
                failure_message=f"Request validation failed: {req_val.errors}",
                diagnostics=req_val.errors,
            )

        num_qubits = len(request.native_circuit.qubits)

        # 2. Initialize QuantumState
        try:
            if request.initial_state is not None:
                state = QuantumState.from_vector(request.initial_state)
            else:
                state = QuantumState.initialize_zero(num_qubits)
        except Exception as e:
            return ExecutionResult(
                request_id=request.request_id,
                status=ExecutionStatus.FAILED,
                execution_mode=request.execution_mode,
                backend_identity=create_reference_simulator_capabilities().identity,
                failure_code=ExecutionFailureCode.INVALID_INITIAL_STATE,
                failure_message=f"Failed to initialize QuantumState: {e}",
                diagnostics=[str(e)],
            )

        # 3. Execute Native Operations in Strict Canonical Order (op_0, op_1, ..., op_m-1)
        sorted_ops = sorted(request.native_circuit.native_operations, key=lambda n: n.operation_index)

        for op in sorted_ops:
            try:
                state = apply_native_operation(state, op)
            except Exception as e:
                diag = [
                    f"Failure at op_index {op.operation_index}",
                    f"Gate type: {op.native_gate}",
                    f"Operands: {op.operands}",
                    f"Parameters: {op.parameters}",
                    f"Error: {e}",
                ]
                return ExecutionResult(
                    request_id=request.request_id,
                    status=ExecutionStatus.FAILED,
                    execution_mode=request.execution_mode,
                    backend_identity=create_reference_simulator_capabilities().identity,
                    failure_code=ExecutionFailureCode.EXECUTION_SEMANTIC_FAILURE,
                    failure_message=f"State-vector execution failed at operation index {op.operation_index} ({op.native_gate}): {e}",
                    diagnostics=diag,
                )

        # 4. Final Normalization Verification (norm = 1.0 +/- 10^-12)
        if not state.is_normalized(EPSILON):
            return ExecutionResult(
                request_id=request.request_id,
                status=ExecutionStatus.FAILED,
                execution_mode=request.execution_mode,
                backend_identity=create_reference_simulator_capabilities().identity,
                failure_code=ExecutionFailureCode.NUMERICAL_VERIFICATION_FAILURE,
                failure_message=f"Final state vector normalization check failed: norm = {state.norm():.10f}, expected 1.0 +/- {EPSILON}.",
                diagnostics=[f"Final norm = {state.norm()}"],
            )

        # 5. Mode Processing (Single execution pass, then optional measurement)
        final_sv_dict = None
        meas_result = None

        if request.execution_mode in (ExecutionMode.STATE_VECTOR, ExecutionMode.STATE_VECTOR_AND_SHOTS):
            final_sv_dict = state.to_state_dict()

        if request.execution_mode in (ExecutionMode.SHOT_SAMPLING, ExecutionMode.STATE_VECTOR_AND_SHOTS):
            try:
                meas_result = ShotSampler.sample_shots(state, request.shots, request.seed)
            except ValueError as ve:
                return ExecutionResult(
                    request_id=request.request_id,
                    status=ExecutionStatus.FAILED,
                    execution_mode=request.execution_mode,
                    backend_identity=create_reference_simulator_capabilities().identity,
                    failure_code=ExecutionFailureCode.MEASUREMENT_FAILURE,
                    failure_message=f"Shot sampling failed: {ve}",
                    diagnostics=[str(ve)],
                )

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        backend_identity = create_reference_simulator_capabilities().identity

        result = ExecutionResult(
            request_id=request.request_id,
            status=ExecutionStatus.SUCCESS,
            execution_mode=request.execution_mode,
            backend_identity=backend_identity,
            final_state_vector=final_sv_dict,
            measurement_result=meas_result,
            provenance=request.native_circuit.provenance,
            verification_status=True,
            execution_time_ms=elapsed_ms,
            diagnostics=[],
        )

        res_val = validate_execution_result(result)
        if not res_val.valid:
            return ExecutionResult(
                request_id=request.request_id,
                status=ExecutionStatus.FAILED,
                execution_mode=request.execution_mode,
                backend_identity=backend_identity,
                failure_code=ExecutionFailureCode.EXECUTION_SEMANTIC_FAILURE,
                failure_message=f"Generated ExecutionResult failed validation: {res_val.errors}",
                diagnostics=res_val.errors,
            )

        return result
