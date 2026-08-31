"""
Module 5 Stage 5 Micro-Closure — Execution Request & Result Validator.

Implements strict validation for ExecutionRequest and ExecutionResult contracts.
"""

from dataclasses import dataclass, field
from typing import List, Optional
import math
from src.module5.native.validator import validate_native_circuit_ir
from src.module5.execution.model import (
    ExecutionRequest,
    ExecutionResult,
    ExecutionMode,
    ExecutionStatus,
    ExecutionFailureCode,
    EXECUTION_SCHEMA_VERSION,
    EPSILON,
)


@dataclass
class RequestValidationResult:
    """Diagnostic validation result for ExecutionRequest."""
    valid: bool
    failure_code: Optional[ExecutionFailureCode] = None
    errors: List[str] = field(default_factory=list)


@dataclass
class ResultValidationResult:
    """Diagnostic validation result for ExecutionResult."""
    valid: bool
    errors: List[str] = field(default_factory=list)


def validate_execution_request(request: ExecutionRequest) -> RequestValidationResult:
    """
    Validates an ExecutionRequest across all boundary rules before execution.
    """
    errors: List[str] = []

    # 1. Structural Checks
    if request.schema_version != EXECUTION_SCHEMA_VERSION:
        errors.append(f"Invalid schema_version '{request.schema_version}', expected '{EXECUTION_SCHEMA_VERSION}'.")
        return RequestValidationResult(valid=False, failure_code=ExecutionFailureCode.INVALID_REQUEST, errors=errors)

    if not request.request_id or not request.request_id.strip():
        errors.append("Empty or whitespace request_id.")
        return RequestValidationResult(valid=False, failure_code=ExecutionFailureCode.INVALID_REQUEST, errors=errors)

    # Validate execution mode
    if not isinstance(request.execution_mode, ExecutionMode):
        try:
            ExecutionMode(request.execution_mode)
        except Exception:
            errors.append(f"Invalid execution mode '{request.execution_mode}'.")
            return RequestValidationResult(valid=False, failure_code=ExecutionFailureCode.INVALID_REQUEST, errors=errors)

    # 2. Native Circuit Validation
    if request.native_circuit is None:
        errors.append("Missing native_circuit in ExecutionRequest.")
        return RequestValidationResult(valid=False, failure_code=ExecutionFailureCode.INVALID_NATIVE_CIRCUIT, errors=errors)

    circuit_val = validate_native_circuit_ir(request.native_circuit)
    if not circuit_val.valid:
        errors.append(f"Invalid NativeCircuitIR: {circuit_val.errors}")
        return RequestValidationResult(valid=False, failure_code=ExecutionFailureCode.INVALID_NATIVE_CIRCUIT, errors=errors)

    # 3. Hardware / External Backend Boundary Check
    if request.target_backend_id != "reference_simulator":
        errors.append(f"Forbidden backend '{request.target_backend_id}'. Stage 5 baseline permits 'reference_simulator' ONLY.")
        return RequestValidationResult(valid=False, failure_code=ExecutionFailureCode.FORBIDDEN_HARDWARE_REQUEST, errors=errors)

    # 4. Mode and Shot Count Validation
    if request.execution_mode in (ExecutionMode.SHOT_SAMPLING, ExecutionMode.STATE_VECTOR_AND_SHOTS):
        if request.shots <= 0:
            errors.append(f"Shot count must be strictly positive (> 0) for shot sampling modes, got {request.shots}.")
            return RequestValidationResult(valid=False, failure_code=ExecutionFailureCode.MEASUREMENT_FAILURE, errors=errors)

    # 5. Initial State Vector Validation
    if request.initial_state is not None:
        num_qubits = len(request.native_circuit.qubits)
        expected_dim = 1 << num_qubits

        if len(request.initial_state) != expected_dim:
            errors.append(f"Initial state dimension mismatch: expected 2^{num_qubits} = {expected_dim}, got {len(request.initial_state)}.")
            return RequestValidationResult(valid=False, failure_code=ExecutionFailureCode.INVALID_INITIAL_STATE, errors=errors)

        norm_sq = 0.0
        for idx, amp in enumerate(request.initial_state):
            if math.isnan(amp.real) or math.isnan(amp.imag) or math.isinf(amp.real) or math.isinf(amp.imag):
                errors.append(f"NaN or Infinite amplitude at initial state index {idx}: {amp}.")
                return RequestValidationResult(valid=False, failure_code=ExecutionFailureCode.INVALID_INITIAL_STATE, errors=errors)
            norm_sq += abs(amp) ** 2

        norm = math.sqrt(norm_sq)
        if abs(norm - 1.0) >= EPSILON:
            errors.append(f"Un-normalized initial state vector: ||psi_0|| = {norm:.10f}, expected 1.0 +/- {EPSILON}.")
            return RequestValidationResult(valid=False, failure_code=ExecutionFailureCode.INVALID_INITIAL_STATE, errors=errors)

    return RequestValidationResult(valid=True)


def validate_execution_result(result: ExecutionResult) -> ResultValidationResult:
    """
    Validates an ExecutionResult payload against schema and completeness rules.
    """
    errors: List[str] = []

    if result.schema_version != EXECUTION_SCHEMA_VERSION:
        errors.append(f"Invalid schema_version '{result.schema_version}', expected '{EXECUTION_SCHEMA_VERSION}'.")

    if not result.request_id or not result.request_id.strip():
        errors.append("Empty or whitespace request_id.")

    if result.status == ExecutionStatus.SUCCESS:
        if result.execution_mode in (ExecutionMode.STATE_VECTOR, ExecutionMode.STATE_VECTOR_AND_SHOTS):
            if not result.final_state_vector:
                errors.append("Missing final_state_vector in successful STATE_VECTOR result.")

        if result.execution_mode in (ExecutionMode.SHOT_SAMPLING, ExecutionMode.STATE_VECTOR_AND_SHOTS):
            if not result.measurement_result:
                errors.append("Missing measurement_result in successful SHOT_SAMPLING result.")
            else:
                total_counts = sum(result.measurement_result.counts.values())
                if total_counts != result.measurement_result.shot_count:
                    errors.append(f"Measurement count sum {total_counts} does not match shot count {result.measurement_result.shot_count}.")

    return ResultValidationResult(valid=len(errors) == 0, errors=errors)
