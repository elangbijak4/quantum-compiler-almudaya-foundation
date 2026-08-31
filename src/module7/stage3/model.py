"""
Module 7 Stage 3 — Local Virtual Reference Simulator Models & Data Contracts.

Provides data contracts for simulator configuration, execution status,
reference statevector summaries, and provider-neutral execution results.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Tuple, Optional, Any
import hashlib
import json


class SimulationExecutionStatus(Enum):
    """Execution status lifecycle for local reference simulator."""
    UNINITIALIZED = "UNINITIALIZED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    INCONCLUSIVE = "INCONCLUSIVE"


@dataclass(frozen=True)
class SimulatorConfig:
    """
    Configuration governing local reference simulator execution.
    """
    config_id: str
    execution_mode: str = "STATEVECTOR_EXACT"  # "STATEVECTOR_EXACT" or "SAMPLED_SHOTS"
    shots: int = 1000
    seed_prng: Optional[int] = 42
    max_qubits: int = 32
    precision: str = "COMPLEX128"
    config_hash: str = ""

    def __post_init__(self) -> None:
        if not self.config_hash:
            object.__setattr__(self, "config_hash", self.compute_hash())

    def compute_hash(self) -> str:
        raw_dict = {
            "config_id": self.config_id,
            "execution_mode": self.execution_mode,
            "shots": self.shots,
            "seed_prng": self.seed_prng,
            "max_qubits": self.max_qubits,
            "precision": self.precision,
        }
        canonical_str = json.dumps(raw_dict, sort_keys=True)
        return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "config_id": self.config_id,
            "execution_mode": self.execution_mode,
            "shots": self.shots,
            "seed_prng": self.seed_prng,
            "max_qubits": self.max_qubits,
            "precision": self.precision,
            "config_hash": self.config_hash,
        }


@dataclass(frozen=True)
class ReferenceStatevectorSummary:
    """
    Immutable summary of simulated quantum statevector probability amplitudes.
    """
    qubit_count: int
    probabilities: Dict[str, float]  # bitstring -> probability |c_k|^2
    statevector_hash: str = ""

    def __post_init__(self) -> None:
        if not self.statevector_hash:
            object.__setattr__(self, "statevector_hash", self.compute_hash())

    def compute_hash(self) -> str:
        raw_dict = {
            "qubit_count": self.qubit_count,
            "probabilities": {str(k): float(v) for k, v in sorted(self.probabilities.items())},
        }
        canonical_str = json.dumps(raw_dict, sort_keys=True)
        return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "qubit_count": self.qubit_count,
            "probabilities": dict(self.probabilities),
            "statevector_hash": self.statevector_hash,
        }


@dataclass(frozen=True)
class SimulatorJobResult:
    """
    Provider-neutral job result produced by local reference simulator.
    """
    job_id: str
    native_circuit_id: str
    native_circuit_hash: str
    backend_id: str
    capability_hash: str
    lowering_id: str
    status: SimulationExecutionStatus
    shots: int
    measurement_counts: Dict[str, int]
    measurement_distribution: Dict[str, float]
    statevector_summary: Optional[ReferenceStatevectorSummary] = None
    provenance: Dict[str, Any] = field(default_factory=dict)
    job_hash: str = ""

    def __post_init__(self) -> None:
        if not self.job_hash:
            object.__setattr__(self, "job_hash", self.compute_hash())

    def compute_hash(self) -> str:
        raw_dict = {
            "job_id": self.job_id,
            "native_circuit_id": self.native_circuit_id,
            "native_circuit_hash": self.native_circuit_hash,
            "backend_id": self.backend_id,
            "capability_hash": self.capability_hash,
            "lowering_id": self.lowering_id,
            "status": self.status.value,
            "shots": self.shots,
            "measurement_counts": {str(k): int(v) for k, v in sorted(self.measurement_counts.items())},
            "measurement_distribution": {str(k): float(v) for k, v in sorted(self.measurement_distribution.items())},
            "statevector_hash": self.statevector_summary.statevector_hash if self.statevector_summary else "",
        }
        canonical_str = json.dumps(raw_dict, sort_keys=True)
        return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "native_circuit_id": self.native_circuit_id,
            "native_circuit_hash": self.native_circuit_hash,
            "backend_id": self.backend_id,
            "capability_hash": self.capability_hash,
            "lowering_id": self.lowering_id,
            "status": self.status.value,
            "shots": self.shots,
            "measurement_counts": dict(self.measurement_counts),
            "measurement_distribution": dict(self.measurement_distribution),
            "statevector_summary": self.statevector_summary.to_dict() if self.statevector_summary else None,
            "provenance": dict(self.provenance),
            "job_hash": self.job_hash,
        }
