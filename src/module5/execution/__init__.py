"""
Module 5 Stage 5 Execution Package.
"""

from src.module5.execution.model import (
    ExecutionMode,
    ExecutionStatus,
    ExecutionFailureCode,
    MeasurementResult,
    ExecutionRequest,
    ExecutionResult,
    EXECUTION_SCHEMA_VERSION,
    EPSILON as STAGE_5_EPSILON,
)
from src.module5.execution.validator import (
    RequestValidationResult,
    ResultValidationResult,
    validate_execution_request,
    validate_execution_result,
)
from src.module5.execution.serialization import (
    serialize_execution_request,
    deserialize_execution_request,
    serialize_execution_result,
    deserialize_execution_result,
)
from src.module5.execution.state import QuantumState
from src.module5.execution.gates import (
    apply_x,
    apply_cnot,
    apply_swap,
    apply_toffoli,
    apply_h,
    apply_z,
    apply_s,
    apply_t,
    apply_cz,
    apply_native_operation,
)
from src.module5.execution.sampler import ShotSampler
from src.module5.execution.engine import ExecutionEngine
from src.module5.execution.verifier import (
    ExecutionEquivalenceReport,
    ExecutionVerifier,
)

__all__ = [
    # Models & Constants
    "ExecutionMode",
    "ExecutionStatus",
    "ExecutionFailureCode",
    "MeasurementResult",
    "ExecutionRequest",
    "ExecutionResult",
    "EXECUTION_SCHEMA_VERSION",
    "STAGE_5_EPSILON",

    # Validators
    "RequestValidationResult",
    "ResultValidationResult",
    "validate_execution_request",
    "validate_execution_result",

    # Serializers
    "serialize_execution_request",
    "deserialize_execution_request",
    "serialize_execution_result",
    "deserialize_execution_result",

    # QuantumState & Gates
    "QuantumState",
    "apply_x",
    "apply_cnot",
    "apply_swap",
    "apply_toffoli",
    "apply_h",
    "apply_z",
    "apply_s",
    "apply_t",
    "apply_cz",
    "apply_native_operation",

    # Sampler, Engine & Verifier
    "ShotSampler",
    "ExecutionEngine",
    "ExecutionEquivalenceReport",
    "ExecutionVerifier",
]
