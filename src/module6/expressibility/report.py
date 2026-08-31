"""
Module 6 Stage 2 — Expressibility Report & Canonical Serialization.

Defines target reachability results, expressibility report data models, failure codes, and canonical JSON serialization.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Tuple, Optional, Any
import json
import hashlib
from src.module6.image.collision import CollisionRecord, CollisionType
from src.module6.image.characterization import EmpiricalImageSummary
from src.module6.image.signature import ImageSignature
from src.module6.vocabulary.analyzer import PrimitiveVocabularyReachabilityStatus, PrimitiveVocabularyResult


class TargetReachabilityStatus(str, Enum):
    """Explicit status vocabulary for target reachability in Stage 2 search."""
    FOUND = "FOUND"
    NOT_FOUND_IN_SEARCH = "NOT_FOUND_IN_SEARCH"
    DIMENSION_MISMATCH = "DIMENSION_MISMATCH"
    INVALID_TARGET = "INVALID_TARGET"
    SEARCH_LIMIT_REACHED = "SEARCH_LIMIT_REACHED"
    VERIFICATION_FAILURE = "VERIFICATION_FAILURE"
    NOT_ANALYZED = "NOT_ANALYZED"


class InjectivityStatus(str, Enum):
    """Classification of empirical injectivity status (never overclaimed)."""
    COLLISION_OBSERVED = "COLLISION_OBSERVED"
    NO_COLLISION_OBSERVED = "NO_COLLISION_OBSERVED"
    UNPROVEN = "UNPROVEN"


class SurjectivityStatus(str, Enum):
    """Classification of surjectivity status (always UNPROVEN in finite search)."""
    UNPROVEN = "UNPROVEN"


class UniversalExpressibilityStatus(str, Enum):
    """Classification of universal expressibility status (always UNPROVEN in finite search)."""
    UNPROVEN = "UNPROVEN"


class Stage2FailureCode(str, Enum):
    """Explicit Stage 2 failure codes."""
    INVALID_ALGORITHM_FAMILY = "INVALID_ALGORITHM_FAMILY"
    INVALID_TARGET = "INVALID_TARGET"
    INVALID_PARAMETER_DOMAIN = "INVALID_PARAMETER_DOMAIN"
    INVALID_PRIMITIVE_VOCABULARY = "INVALID_PRIMITIVE_VOCABULARY"
    COMPILER_MAPPING_FAILURE = "COMPILER_MAPPING_FAILURE"
    CIRCUIT_VALIDATION_FAILURE = "CIRCUIT_VALIDATION_FAILURE"
    OPERATOR_CONSTRUCTION_FAILURE = "OPERATOR_CONSTRUCTION_FAILURE"
    DIMENSION_MISMATCH = "DIMENSION_MISMATCH"
    EQUIVALENCE_FAILURE = "EQUIVALENCE_FAILURE"
    PROVENANCE_FAILURE = "PROVENANCE_FAILURE"
    SERIALIZATION_FAILURE = "SERIALIZATION_FAILURE"
    SEARCH_CONFIGURATION_FAILURE = "SEARCH_CONFIGURATION_FAILURE"
    INTERNAL_ANALYSIS_FAILURE = "INTERNAL_ANALYSIS_FAILURE"


@dataclass(frozen=True)
class TargetReachabilityResult:
    """
    Immutable result of matching a single target operator against compiler image Img_N(F).
    """
    target_id: str
    target_operator_hash: str
    target_qubit_count: int
    primitive_reachability: str
    compiler_image_reachability: str
    matching_algorithm_ids: Tuple[str, ...]
    matching_circuit_ids: Tuple[str, ...]
    best_operator_residual: float
    global_phase_status: str
    status: TargetReachabilityStatus


@dataclass
class ExpressibilityReport:
    """
    Comprehensive Stage 2 Expressibility & Compiler Image Characterization Report.
    """
    experiment_id: str
    algorithm_family: str
    sample_size: int
    circuit_image_size: int
    operator_image_size: int
    target_count: int
    target_results: Tuple[TargetReachabilityResult, ...]
    collision_results: Tuple[CollisionRecord, ...]
    primitive_vocabulary_results: Tuple[PrimitiveVocabularyResult, ...]
    compiler_image_summary: EmpiricalImageSummary
    injectivity_status: InjectivityStatus
    surjectivity_status: SurjectivityStatus
    universal_expressibility_status: UniversalExpressibilityStatus
    parameter_domain: Dict[str, Any]
    maximum_search_depth: int
    numerical_tolerance: float
    provenance: Dict[str, str]
    deterministic_analysis_id: str
    hadamard_result: TargetReachabilityResult
    failure_code: Optional[Stage2FailureCode] = None
    failure_message: Optional[str] = None
    diagnostics: Tuple[str, ...] = ()


def _serialize_object(obj: Any) -> Any:
    """Recursively converts Stage 2 report dataclasses and enums into JSON-serializable primitives."""
    if isinstance(obj, Enum):
        return obj.value
    elif hasattr(obj, "__dataclass_fields__"):
        result = {}
        for field_name in obj.__dataclass_fields__:
            val = getattr(obj, field_name)
            result[field_name] = _serialize_object(val)
        return result
    elif isinstance(obj, tuple) or isinstance(obj, list):
        return [_serialize_object(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: _serialize_object(v) for k, v in obj.items()}
    else:
        return obj


def serialize_expressibility_report(report: ExpressibilityReport) -> str:
    """
    Serializes ExpressibilityReport into a canonical, deterministic JSON string.
    """
    raw_dict = _serialize_object(report)
    return json.dumps(raw_dict, indent=2, sort_keys=True)


def deserialize_expressibility_report(json_str: str) -> ExpressibilityReport:
    """
    Deserializes canonical JSON string into ExpressibilityReport, validating schema.
    """
    data = json.loads(json_str)

    # Reconstruct ImageSignature list
    signatures = [
        ImageSignature(
            algorithm_id=s["algorithm_id"],
            circuit_id=s.get("circuit_id", "NONE"),
            classical_semantic_signature=s["classical_semantic_signature"],
            circuit_structural_signature=s["circuit_structural_signature"],
            operation_count=s["operation_count"],
            gate_histogram=s["gate_histogram"],
            qubit_count=s["qubit_count"],
            operator_hash=s["operator_hash"],
            operator_equivalence_class_id=s["operator_equivalence_class_id"],
        )
        for s in data["compiler_image_summary"]["signatures"]
    ]

    # Reconstruct CollisionRecord list
    collisions = [
        CollisionRecord(
            collision_id=c["collision_id"],
            collision_type=CollisionType(c["collision_type"]),
            algorithm_id_1=c["algorithm_id_1"],
            algorithm_id_2=c["algorithm_id_2"],
            circuit_id_1=c["circuit_id_1"],
            circuit_id_2=c["circuit_id_2"],
            operator_hash_1=c["operator_hash_1"],
            operator_hash_2=c["operator_hash_2"],
            details=c["details"],
        )
        for c in data["compiler_image_summary"]["collisions"]
    ]

    summary = EmpiricalImageSummary(
        source_algorithm_count=data["compiler_image_summary"]["source_algorithm_count"],
        circuit_image_count=data["compiler_image_summary"]["circuit_image_count"],
        operator_image_count=data["compiler_image_summary"]["operator_image_count"],
        structural_diversity_ratio=data["compiler_image_summary"]["structural_diversity_ratio"],
        operator_diversity_ratio=data["compiler_image_summary"]["operator_diversity_ratio"],
        unique_operator_classes=tuple(data["compiler_image_summary"]["unique_operator_classes"]),
        signatures=tuple(signatures),
        collisions=tuple(collisions),
    )

    target_results = [
        TargetReachabilityResult(
            target_id=tr["target_id"],
            target_operator_hash=tr["target_operator_hash"],
            target_qubit_count=tr["target_qubit_count"],
            primitive_reachability=tr["primitive_reachability"],
            compiler_image_reachability=tr["compiler_image_reachability"],
            matching_algorithm_ids=tuple(tr["matching_algorithm_ids"]),
            matching_circuit_ids=tuple(tr["matching_circuit_ids"]),
            best_operator_residual=tr["best_operator_residual"],
            global_phase_status=tr["global_phase_status"],
            status=TargetReachabilityStatus(tr["status"]),
        )
        for tr in data["target_results"]
    ]

    vocab_results = [
        PrimitiveVocabularyResult(
            target_id=vr["target_id"],
            reachability_status=PrimitiveVocabularyReachabilityStatus(vr["reachability_status"]),
            in_primitive_closure=vr["in_primitive_closure"],
            best_matrix_residual=vr["best_matrix_residual"],
            depth_evaluated=vr["depth_evaluated"],
            details=vr["details"],
        )
        for vr in data["primitive_vocabulary_results"]
    ]

    hr = data["hadamard_result"]
    hadamard_res = TargetReachabilityResult(
        target_id=hr["target_id"],
        target_operator_hash=hr["target_operator_hash"],
        target_qubit_count=hr["target_qubit_count"],
        primitive_reachability=hr["primitive_reachability"],
        compiler_image_reachability=hr["compiler_image_reachability"],
        matching_algorithm_ids=tuple(hr["matching_algorithm_ids"]),
        matching_circuit_ids=tuple(hr["matching_circuit_ids"]),
        best_operator_residual=hr["best_operator_residual"],
        global_phase_status=hr["global_phase_status"],
        status=TargetReachabilityStatus(hr["status"]),
    )

    fail_code = Stage2FailureCode(data["failure_code"]) if data.get("failure_code") else None

    return ExpressibilityReport(
        experiment_id=data["experiment_id"],
        algorithm_family=data["algorithm_family"],
        sample_size=data["sample_size"],
        circuit_image_size=data["circuit_image_size"],
        operator_image_size=data["operator_image_size"],
        target_count=data["target_count"],
        target_results=tuple(target_results),
        collision_results=tuple(collisions),
        primitive_vocabulary_results=tuple(vocab_results),
        compiler_image_summary=summary,
        injectivity_status=InjectivityStatus(data["injectivity_status"]),
        surjectivity_status=SurjectivityStatus(data["surjectivity_status"]),
        universal_expressibility_status=UniversalExpressibilityStatus(data["universal_expressibility_status"]),
        parameter_domain=data["parameter_domain"],
        maximum_search_depth=data["maximum_search_depth"],
        numerical_tolerance=data["numerical_tolerance"],
        provenance=data["provenance"],
        deterministic_analysis_id=data["deterministic_analysis_id"],
        hadamard_result=hadamard_res,
        failure_code=fail_code,
        failure_message=data.get("failure_message"),
        diagnostics=tuple(data.get("diagnostics", ())),
    )
