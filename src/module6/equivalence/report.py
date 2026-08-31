"""
Module 6 Stage 4 — Equivalence Report & Result Models.

Defines EquivalenceStatus, FailureCode, SemanticEquivalenceReport (Stage 1),
EquivalenceReport (Stage 4), 6-level matrix structures, and canonical JSON serialization/deserialization.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Tuple, Any, Optional
import json
import hashlib
from src.module6.equivalence.levels import EquivalenceLevel
from src.module6.mapping.correspondence import BasisCorrespondenceRecord


class EquivalenceStatus(str, Enum):
    """
    Status of equivalence comparison.
    """
    EQUIVALENT = "EQUIVALENT"
    NON_EQUIVALENT = "NON_EQUIVALENT"
    EQUIVALENT_UP_TO_GLOBAL_PHASE = "EQUIVALENT_UP_TO_GLOBAL_PHASE"
    INCONCLUSIVE = "INCONCLUSIVE"
    INVALID_INPUT = "INVALID_INPUT"
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"

    def __str__(self) -> str:
        return self.value


class FailureCode(str, Enum):
    """
    Explicit Stage 1 & Stage 4 analysis failure codes.
    """
    NONE = "NONE"
    INVALID_CLASSICAL_MODEL = "INVALID_CLASSICAL_MODEL"
    INVALID_QUANTUM_CIRCUIT = "INVALID_QUANTUM_CIRCUIT"
    INVALID_DIMENSION = "INVALID_DIMENSION"
    INVALID_STATE_VECTOR = "INVALID_STATE_VECTOR"
    INVALID_OPERATOR = "INVALID_OPERATOR"
    INVALID_PARAMETER = "INVALID_PARAMETER"
    BASIS_EVALUATION_FAILURE = "BASIS_EVALUATION_FAILURE"
    BASIS_EQUIVALENCE_FAILURE = "BASIS_EQUIVALENCE_FAILURE"
    STATE_VECTOR_EVALUATION_FAILURE = "STATE_VECTOR_EVALUATION_FAILURE"
    OPERATOR_EVALUATION_FAILURE = "OPERATOR_EVALUATION_FAILURE"
    OPERATOR_EQUIVALENCE_FAILURE = "OPERATOR_EQUIVALENCE_FAILURE"
    ANCILLA_CLEANLINESS_FAILURE = "ANCILLA_CLEANLINESS_FAILURE"
    SUPERPOSITION_LINEARITY_FAILURE = "SUPERPOSITION_LINEARITY_FAILURE"
    GLOBAL_PHASE_FAILURE = "GLOBAL_PHASE_FAILURE"
    REVERSE_EXECUTION_FAILURE = "REVERSE_EXECUTION_FAILURE"
    PHASE_ANALYSIS_FAILURE = "PHASE_ANALYSIS_FAILURE"
    QUOTIENT_PRESERVATION_FAILURE = "QUOTIENT_PRESERVATION_FAILURE"
    MAPPING_FAILURE = "MAPPING_FAILURE"
    PROVENANCE_FAILURE = "PROVENANCE_FAILURE"
    SERIALIZATION_FAILURE = "SERIALIZATION_FAILURE"
    INTERNAL_ANALYSIS_FAILURE = "INTERNAL_ANALYSIS_FAILURE"

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class SemanticEquivalenceReport:
    """
    Stage 1 Formal Semantic Mapping & Equivalence Report.
    """
    classical_algorithm_id: str
    classical_domain_size: int
    logical_circuit_id: str
    status: EquivalenceStatus
    level_3_status: EquivalenceStatus
    level_5_status: EquivalenceStatus
    failure_code: Optional[FailureCode] = None
    failure_message: Optional[str] = None
    basis_results: List[BasisCorrespondenceRecord] = field(default_factory=list)
    operator_residual: float = 0.0
    left_unitarity_residual: float = 0.0
    right_unitarity_residual: float = 0.0
    superposition_residual: float = 0.0
    ancilla_cleanliness_pass: bool = True
    global_phase_pass: bool = True
    reverse_equivalence_pass: bool = True
    provenance: Dict[str, str] = field(default_factory=dict)
    deterministic_analysis_id: str = ""
    diagnostics: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "classical_algorithm_id": self.classical_algorithm_id,
            "classical_domain_size": self.classical_domain_size,
            "logical_circuit_id": self.logical_circuit_id,
            "status": str(self.status),
            "level_3_status": str(self.level_3_status),
            "level_5_status": str(self.level_5_status),
            "failure_code": str(self.failure_code) if self.failure_code else None,
            "failure_message": self.failure_message,
            "basis_results": [asdict(b) for b in self.basis_results],
            "operator_residual": self.operator_residual,
            "left_unitarity_residual": self.left_unitarity_residual,
            "right_unitarity_residual": self.right_unitarity_residual,
            "superposition_residual": self.superposition_residual,
            "ancilla_cleanliness_pass": self.ancilla_cleanliness_pass,
            "global_phase_pass": self.global_phase_pass,
            "reverse_equivalence_pass": self.reverse_equivalence_pass,
            "provenance": dict(sorted(self.provenance.items())),
            "deterministic_analysis_id": self.deterministic_analysis_id,
            "diagnostics": self.diagnostics,
        }


@dataclass(frozen=True)
class EquivalenceReport:
    """
    Stage 4 Multi-Level Equivalence Evaluation Report.
    """
    comparison_id: str
    source_type: str
    target_type: str
    level_results: Dict[str, str]  # L1..L6 matrix
    final_status: EquivalenceStatus
    numerical_residuals: Dict[str, float]
    phase_status: str
    basis_results: Dict[str, Any]
    state_results: Dict[str, Any]
    operator_results: Dict[str, Any]
    classical_semantics_result: Optional[Dict[str, Any]] = None
    quantum_semantics_result: Optional[Dict[str, Any]] = None
    evidence_class: str = "EMPIRICAL_EXPERIMENT"
    failure_code: FailureCode = FailureCode.NONE
    provenance: Dict[str, str] = field(default_factory=dict)
    deterministic_analysis_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Converts report to serializable dictionary."""
        d = {
            "comparison_id": self.comparison_id,
            "source_type": self.source_type,
            "target_type": self.target_type,
            "level_results": dict(sorted(self.level_results.items())),
            "final_status": str(self.final_status.value if isinstance(self.final_status, Enum) else self.final_status),
            "numerical_residuals": dict(sorted(self.numerical_residuals.items())),
            "phase_status": str(self.phase_status),
            "basis_results": self.basis_results,
            "state_results": self.state_results,
            "operator_results": self.operator_results,
            "classical_semantics_result": self.classical_semantics_result,
            "quantum_semantics_result": self.quantum_semantics_result,
            "evidence_class": str(self.evidence_class),
            "failure_code": str(self.failure_code.value if isinstance(self.failure_code, Enum) else self.failure_code),
            "provenance": dict(sorted(self.provenance.items())),
            "deterministic_analysis_id": self.deterministic_analysis_id,
        }
        return d


def serialize_report(report: Any) -> str:
    """Canonical JSON serialization for SemanticEquivalenceReport or EquivalenceReport."""
    d = report.to_dict()
    return json.dumps(d, indent=2, sort_keys=True)


def deserialize_report(json_str: str) -> Any:
    """Canonical JSON deserialization for EquivalenceReport or SemanticEquivalenceReport."""
    d = json.loads(json_str)
    if "comparison_id" in d:
        return EquivalenceReport(
            comparison_id=d["comparison_id"],
            source_type=d["source_type"],
            target_type=d["target_type"],
            level_results=d["level_results"],
            final_status=EquivalenceStatus(d["final_status"]),
            numerical_residuals=d["numerical_residuals"],
            phase_status=d["phase_status"],
            basis_results=d["basis_results"],
            state_results=d["state_results"],
            operator_results=d["operator_results"],
            classical_semantics_result=d.get("classical_semantics_result"),
            quantum_semantics_result=d.get("quantum_semantics_result"),
            evidence_class=d.get("evidence_class", "EMPIRICAL_EXPERIMENT"),
            failure_code=FailureCode(d.get("failure_code", "NONE")),
            provenance=d["provenance"],
            deterministic_analysis_id=d["deterministic_analysis_id"],
        )
    else:
        basis_recs = [
            BasisCorrespondenceRecord(
                index=b.get("index", 0),
                config_id=b.get("config_id", ""),
                config_category=b.get("config_category", "INITIAL"),
                encoded_input_bits=b.get("encoded_input_bits", ""),
                classical_successor_bits=b.get("classical_successor_bits", ""),
                quantum_output_bits=b.get("quantum_output_bits", ""),
                expected_output_bits=b.get("expected_output_bits", ""),
                residual_l2=b.get("residual_l2", 0.0),
                passed=b.get("passed", True),
                is_symbolic_exact=b.get("is_symbolic_exact", True),
                error_message=b.get("error_message"),
            )
            for b in d.get("basis_results", [])
        ]
        return SemanticEquivalenceReport(
            classical_algorithm_id=d["classical_algorithm_id"],
            classical_domain_size=d["classical_domain_size"],
            logical_circuit_id=d["logical_circuit_id"],
            status=EquivalenceStatus(d["status"]),
            level_3_status=EquivalenceStatus(d["level_3_status"]),
            level_5_status=EquivalenceStatus(d["level_5_status"]),
            failure_code=FailureCode(d["failure_code"]) if d.get("failure_code") else None,
            failure_message=d.get("failure_message"),
            basis_results=basis_recs,
            operator_residual=d.get("operator_residual", 0.0),
            left_unitarity_residual=d.get("left_unitarity_residual", 0.0),
            right_unitarity_residual=d.get("right_unitarity_residual", 0.0),
            superposition_residual=d.get("superposition_residual", 0.0),
            ancilla_cleanliness_pass=d.get("ancilla_cleanliness_pass", True),
            global_phase_pass=d.get("global_phase_pass", True),
            reverse_equivalence_pass=d.get("reverse_equivalence_pass", True),
            provenance=d.get("provenance", {}),
            deterministic_analysis_id=d.get("deterministic_analysis_id", ""),
            diagnostics=d.get("diagnostics", []),
        )
