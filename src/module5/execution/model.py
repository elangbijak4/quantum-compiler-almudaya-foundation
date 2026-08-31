"""
Module 5 Stage 5 Micro-Closure — Execution Contracts & Data Models.

Defines ExecutionMode, ExecutionStatus, ExecutionFailureCode, MeasurementResult,
ExecutionRequest, and ExecutionResult.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from src.module5.backend.model import BackendIdentity
from src.module5.physical_ir.model import ExecutionProvenance
from src.module5.native.model import NativeCircuitIR

EXECUTION_SCHEMA_VERSION: str = "1.0.0"
EPSILON: float = 1e-12


class ExecutionMode(str, Enum):
    """Supported baseline execution modes."""
    STATE_VECTOR = "STATE_VECTOR"
    SHOT_SAMPLING = "SHOT_SAMPLING"
    STATE_VECTOR_AND_SHOTS = "STATE_VECTOR_AND_SHOTS"


class ExecutionStatus(str, Enum):
    """Execution outcome status classification."""
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class ExecutionFailureCode(str, Enum):
    """Explicit domain failure classifications for localization."""
    INVALID_REQUEST = "INVALID_REQUEST"
    INVALID_NATIVE_CIRCUIT = "INVALID_NATIVE_CIRCUIT"
    UNSUPPORTED_EXECUTION_MODE = "UNSUPPORTED_EXECUTION_MODE"
    INVALID_INITIAL_STATE = "INVALID_INITIAL_STATE"
    EXECUTION_SEMANTIC_FAILURE = "EXECUTION_SEMANTIC_FAILURE"
    MEASUREMENT_FAILURE = "MEASUREMENT_FAILURE"
    NUMERICAL_VERIFICATION_FAILURE = "NUMERICAL_VERIFICATION_FAILURE"
    PROVENANCE_FAILURE = "PROVENANCE_FAILURE"
    FORBIDDEN_HARDWARE_REQUEST = "FORBIDDEN_HARDWARE_REQUEST"
    FORBIDDEN_NOISE_REQUEST = "FORBIDDEN_NOISE_REQUEST"


@dataclass
class MeasurementResult:
    """Computational-basis readout measurement outcome payload."""
    probabilities: Dict[str, float] = field(default_factory=dict)
    counts: Dict[str, int] = field(default_factory=dict)
    shot_sequence: List[str] = field(default_factory=list)
    shot_count: int = 0
    seed: Optional[int] = None

    def __post_init__(self) -> None:
        if self.shot_count < 0:
            raise ValueError(f"Shot count cannot be negative: {self.shot_count}")


@dataclass
class ExecutionRequest:
    """Input contract payload for circuit execution."""
    request_id: str
    native_circuit: NativeCircuitIR
    execution_mode: ExecutionMode = ExecutionMode.STATE_VECTOR
    initial_state: Optional[List[complex]] = None
    shots: int = 1000
    seed: Optional[int] = None
    target_backend_id: str = "reference_simulator"
    schema_version: str = EXECUTION_SCHEMA_VERSION


@dataclass
class ExecutionResult:
    """Output contract payload for circuit execution."""
    request_id: str
    status: ExecutionStatus
    execution_mode: ExecutionMode
    backend_identity: BackendIdentity
    final_state_vector: Optional[Dict[str, complex]] = None
    measurement_result: Optional[MeasurementResult] = None
    provenance: Optional[ExecutionProvenance] = None
    verification_status: bool = False
    execution_time_ms: float = 0.0
    failure_code: Optional[ExecutionFailureCode] = None
    failure_message: Optional[str] = None
    diagnostics: List[str] = field(default_factory=list)
    schema_version: str = EXECUTION_SCHEMA_VERSION
