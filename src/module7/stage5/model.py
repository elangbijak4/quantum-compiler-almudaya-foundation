"""
Module 7 Stage 5 — Result Retrieval, Statistical Verification & Lineage Extension Models.

Provides data contracts for statistical verification policies, verification records,
statistical metrics, and Stage 11 historical lineage extension events.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Tuple, Optional, Any
import hashlib
import json


class StatisticalVerificationDecision(Enum):
    """Execution result statistical verification decisions."""
    UNINITIALIZED = "UNINITIALIZED"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    INCONCLUSIVE = "INCONCLUSIVE"


@dataclass(frozen=True)
class StatisticalVerificationPolicy:
    """
    Governance policy for statistical verification of quantum execution results.
    """
    policy_id: str
    policy_version: str = "1.0.0"
    hellinger_threshold: float = 0.05
    ks_threshold: float = 0.05
    min_shots: int = 100
    numerical_tolerance: float = 1e-6
    policy_hash: str = ""

    def __post_init__(self) -> None:
        if not self.policy_hash:
            object.__setattr__(self, "policy_hash", self.compute_hash())

    def compute_hash(self) -> str:
        raw_dict = {
            "policy_id": self.policy_id,
            "policy_version": self.policy_version,
            "hellinger_threshold": float(self.hellinger_threshold),
            "ks_threshold": float(self.ks_threshold),
            "min_shots": int(self.min_shots),
            "numerical_tolerance": float(self.numerical_tolerance),
        }
        canonical_str = json.dumps(raw_dict, sort_keys=True)
        return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "policy_id": self.policy_id,
            "policy_version": self.policy_version,
            "hellinger_threshold": self.hellinger_threshold,
            "ks_threshold": self.ks_threshold,
            "min_shots": self.min_shots,
            "numerical_tolerance": self.numerical_tolerance,
            "policy_hash": self.policy_hash,
        }


@dataclass(frozen=True)
class StatisticalVerificationRecord:
    """
    Immutable record of statistical verification result evaluation.
    """
    verification_id: str
    execution_id: str
    native_circuit_hash: str
    reference_id: str
    observed_result_hash: str
    decision: StatisticalVerificationDecision
    hellinger_distance: Optional[float]
    ks_distance: Optional[float]
    observed_shots: int
    policy_hash: str
    provenance: Dict[str, Any] = field(default_factory=dict)
    verification_hash: str = ""

    def __post_init__(self) -> None:
        if not self.verification_hash:
            object.__setattr__(self, "verification_hash", self.compute_hash())

    def compute_hash(self) -> str:
        raw_dict = {
            "verification_id": self.verification_id,
            "execution_id": self.execution_id,
            "native_circuit_hash": self.native_circuit_hash,
            "reference_id": self.reference_id,
            "observed_result_hash": self.observed_result_hash,
            "decision": self.decision.value,
            "hellinger_distance": float(self.hellinger_distance) if self.hellinger_distance is not None else None,
            "ks_distance": float(self.ks_distance) if self.ks_distance is not None else None,
            "observed_shots": int(self.observed_shots),
            "policy_hash": self.policy_hash,
        }
        canonical_str = json.dumps(raw_dict, sort_keys=True)
        return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "verification_id": self.verification_id,
            "execution_id": self.execution_id,
            "native_circuit_hash": self.native_circuit_hash,
            "reference_id": self.reference_id,
            "observed_result_hash": self.observed_result_hash,
            "decision": self.decision.value,
            "hellinger_distance": self.hellinger_distance,
            "ks_distance": self.ks_distance,
            "observed_shots": self.observed_shots,
            "policy_hash": self.policy_hash,
            "provenance": dict(self.provenance),
            "verification_hash": self.verification_hash,
        }
