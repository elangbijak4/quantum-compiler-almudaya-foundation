"""
Module 6 Stage 3 — Report Data Model & Canonical Serialization.

Defines Stage3AnalysisReport dataclass, Stage3FailureCode enum, and canonical JSON serialization.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Tuple, Optional, Any
import json
import hashlib

from src.module6.mapping.model import (
    DomainDescriptor,
    CodomainDescriptor,
    CompilerMappingRecord,
    SemanticQuotientRecord,
    MappingComplexityRecord,
    MappingTotalityStatus,
    QuotientWellDefinednessStatus,
    BoundClassification,
)
from src.module6.bounds.cardinality import CardinalityBound, CardinalityType
from src.module6.bounds.image import ImageBound
from src.module6.bounds.operator_class import OperatorClassDescriptor
from src.module6.invariants.analyzer import StructuralInvariantResult
from src.module6.expressibility.report import (
    InjectivityStatus,
    SurjectivityStatus,
    UniversalExpressibilityStatus,
)


class Stage3FailureCode(str, Enum):
    """Explicit Stage 3 failure codes."""
    INVALID_DOMAIN = "INVALID_DOMAIN"
    INVALID_CODOMAIN = "INVALID_CODOMAIN"
    INVALID_MAPPING_INPUT = "INVALID_MAPPING_INPUT"
    MAPPING_FAILURE = "MAPPING_FAILURE"
    PARTIAL_MAPPING = "PARTIAL_MAPPING"
    INVALID_SEMANTIC_MODEL = "INVALID_SEMANTIC_MODEL"
    QUOTIENT_NOT_WELL_DEFINED = "QUOTIENT_NOT_WELL_DEFINED"
    OPERATOR_CONSTRUCTION_FAILURE = "OPERATOR_CONSTRUCTION_FAILURE"
    DIMENSION_MISMATCH = "DIMENSION_MISMATCH"
    INVARIANT_ANALYSIS_FAILURE = "INVARIANT_ANALYSIS_FAILURE"
    INVALID_CARDINALITY_MODEL = "INVALID_CARDINALITY_MODEL"
    INVALID_BOUND = "INVALID_BOUND"
    PROVENANCE_FAILURE = "PROVENANCE_FAILURE"
    SERIALIZATION_FAILURE = "SERIALIZATION_FAILURE"
    INTERNAL_ANALYSIS_FAILURE = "INTERNAL_ANALYSIS_FAILURE"


@dataclass
class Stage3AnalysisReport:
    """
    Comprehensive Stage 3 Compiler Mapping F Formulation & Domain/Codomain Bounds Analysis Report.
    """
    experiment_id: str
    domain_descriptor: DomainDescriptor
    codomain_descriptor: CodomainDescriptor
    compiler_mapping_records: Tuple[CompilerMappingRecord, ...]
    mapping_totality_status: MappingTotalityStatus
    quotient_well_definedness_status: QuotientWellDefinednessStatus
    quotient_records: Tuple[SemanticQuotientRecord, ...]
    structural_image_bound: ImageBound
    semantic_image_bound: ImageBound
    domain_cardinality_bound: CardinalityBound
    codomain_cardinality_bound: CardinalityBound
    image_cardinality_bound: CardinalityBound
    mapping_complexity_records: Tuple[MappingComplexityRecord, ...]
    operator_class_descriptor: OperatorClassDescriptor
    structural_invariant_result: StructuralInvariantResult
    hadamard_formal_status: str
    hadamard_exclusion_proof: str
    injectivity_status: InjectivityStatus
    surjectivity_status: SurjectivityStatus
    universal_expressibility_status: UniversalExpressibilityStatus
    provenance: Dict[str, str]
    deterministic_analysis_id: str
    failure_code: Optional[Stage3FailureCode] = None
    failure_message: Optional[str] = None
    diagnostics: Tuple[str, ...] = ()


def _serialize_object(obj: Any) -> Any:
    """Recursively converts Stage 3 report dataclasses and enums into JSON-serializable primitives."""
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


def serialize_stage3_report(report: Stage3AnalysisReport) -> str:
    """
    Serializes Stage3AnalysisReport into a canonical, deterministic JSON string.
    """
    raw_dict = _serialize_object(report)
    return json.dumps(raw_dict, indent=2, sort_keys=True)


def deserialize_stage3_report(json_str: str) -> Stage3AnalysisReport:
    """
    Deserializes canonical JSON string into Stage3AnalysisReport, validating schema.
    """
    data = json.loads(json_str)

    domain_desc = DomainDescriptor(
        domain_name=data["domain_descriptor"]["domain_name"],
        formal_definition=data["domain_descriptor"]["formal_definition"],
        state_space_type=data["domain_descriptor"]["state_space_type"],
        transition_type=data["domain_descriptor"]["transition_type"],
        finite_domain_bound=data["domain_descriptor"]["finite_domain_bound"],
        is_totality_verified=data["domain_descriptor"]["is_totality_verified"],
        is_determinism_verified=data["domain_descriptor"]["is_determinism_verified"],
        is_reversibility_verified=data["domain_descriptor"]["is_reversibility_verified"],
        cardinality_type=data["domain_descriptor"]["cardinality_type"],
        provenance=data["domain_descriptor"].get("provenance", {}),
    )

    codomain_desc = CodomainDescriptor(
        codomain_name=data["codomain_descriptor"]["codomain_name"],
        formal_definition=data["codomain_descriptor"]["formal_definition"],
        circuit_ir_schema=data["codomain_descriptor"]["circuit_ir_schema"],
        qubit_register_policy=data["codomain_descriptor"]["qubit_register_policy"],
        ancilla_uncomputation_policy=data["codomain_descriptor"]["ancilla_uncomputation_policy"],
        cardinality_type=data["codomain_descriptor"]["cardinality_type"],
        provenance=data["codomain_descriptor"].get("provenance", {}),
    )

    mapping_recs = [
        CompilerMappingRecord(
            source_algorithm_id=r["source_algorithm_id"],
            source_semantic_id=r["source_semantic_id"],
            source_domain_id=r["source_domain_id"],
            logical_circuit_id=r["logical_circuit_id"],
            circuit_structural_hash=r["circuit_structural_hash"],
            operator_hash=r["operator_hash"],
            compiler_version=r["compiler_version"],
            mapping_status=r["mapping_status"],
            provenance=r.get("provenance", {}),
        )
        for r in data["compiler_mapping_records"]
    ]

    quotient_recs = [
        SemanticQuotientRecord(
            evaluation_id=q["evaluation_id"],
            classical_equivalence_class_id=q["classical_equivalence_class_id"],
            quantum_equivalence_class_id=q["quantum_equivalence_class_id"],
            algorithms_in_class=tuple(q["algorithms_in_class"]),
            circuits_in_class=tuple(q["circuits_in_class"]),
            well_defined_in_class=q["well_defined_in_class"],
            details=q["details"],
            provenance=q.get("provenance", {}),
        )
        for q in data["quotient_records"]
    ]

    struct_bound = ImageBound(
        bound_id=data["structural_image_bound"]["bound_id"],
        target_space=data["structural_image_bound"]["target_space"],
        subset_space=data["structural_image_bound"]["subset_space"],
        formal_expression=data["structural_image_bound"]["formal_expression"],
        classification=BoundClassification(data["structural_image_bound"]["classification"]),
        cardinality_upper_bound=data["structural_image_bound"]["cardinality_upper_bound"],
        is_formally_proven=data["structural_image_bound"]["is_formally_proven"],
        details=data["structural_image_bound"]["details"],
        provenance=data["structural_image_bound"].get("provenance", {}),
    )

    sem_bound = ImageBound(
        bound_id=data["semantic_image_bound"]["bound_id"],
        target_space=data["semantic_image_bound"]["target_space"],
        subset_space=data["semantic_image_bound"]["subset_space"],
        formal_expression=data["semantic_image_bound"]["formal_expression"],
        classification=BoundClassification(data["semantic_image_bound"]["classification"]),
        cardinality_upper_bound=data["semantic_image_bound"]["cardinality_upper_bound"],
        is_formally_proven=data["semantic_image_bound"]["is_formally_proven"],
        details=data["semantic_image_bound"]["details"],
        provenance=data["semantic_image_bound"].get("provenance", {}),
    )

    domain_card = CardinalityBound(
        space_name=data["domain_cardinality_bound"]["space_name"],
        cardinality_type=CardinalityType(data["domain_cardinality_bound"]["cardinality_type"]),
        upper_bound_formula=data["domain_cardinality_bound"]["upper_bound_formula"],
        exact_sample_size=data["domain_cardinality_bound"].get("exact_sample_size"),
        is_formally_proven=data["domain_cardinality_bound"]["is_formally_proven"],
        details=data["domain_cardinality_bound"]["details"],
        provenance=data["domain_cardinality_bound"].get("provenance", {}),
    )

    codomain_card = CardinalityBound(
        space_name=data["codomain_cardinality_bound"]["space_name"],
        cardinality_type=CardinalityType(data["codomain_cardinality_bound"]["cardinality_type"]),
        upper_bound_formula=data["codomain_cardinality_bound"]["upper_bound_formula"],
        exact_sample_size=data["codomain_cardinality_bound"].get("exact_sample_size"),
        is_formally_proven=data["codomain_cardinality_bound"]["is_formally_proven"],
        details=data["codomain_cardinality_bound"]["details"],
        provenance=data["codomain_cardinality_bound"].get("provenance", {}),
    )

    img_card = CardinalityBound(
        space_name=data["image_cardinality_bound"]["space_name"],
        cardinality_type=CardinalityType(data["image_cardinality_bound"]["cardinality_type"]),
        upper_bound_formula=data["image_cardinality_bound"]["upper_bound_formula"],
        exact_sample_size=data["image_cardinality_bound"].get("exact_sample_size"),
        is_formally_proven=data["image_cardinality_bound"]["is_formally_proven"],
        details=data["image_cardinality_bound"]["details"],
        provenance=data["image_cardinality_bound"].get("provenance", {}),
    )

    complexity_recs = [
        MappingComplexityRecord(
            algorithm_id=c["algorithm_id"],
            circuit_id=c["circuit_id"],
            source_state_count=c["source_state_count"],
            transition_count=c["transition_count"],
            encoded_configuration_count=c["encoded_configuration_count"],
            logical_qubit_count=c["logical_qubit_count"],
            logical_gate_count=c["logical_gate_count"],
            ancilla_qubit_count=c["ancilla_qubit_count"],
            provenance=c.get("provenance", {}),
        )
        for c in data["mapping_complexity_records"]
    ]

    op_desc = OperatorClassDescriptor(
        class_name=data["operator_class_descriptor"]["class_name"],
        formal_expression=data["operator_class_descriptor"]["formal_expression"],
        is_unitary=data["operator_class_descriptor"]["is_unitary"],
        is_real_valued=data["operator_class_descriptor"]["is_real_valued"],
        is_permutation=data["operator_class_descriptor"]["is_permutation"],
        is_superposition_generating=data["operator_class_descriptor"]["is_superposition_generating"],
        has_discrete_parameters=data["operator_class_descriptor"]["has_discrete_parameters"],
        is_closed_under_composition=data["operator_class_descriptor"]["is_closed_under_composition"],
        classification=BoundClassification(data["operator_class_descriptor"]["classification"]),
        details=data["operator_class_descriptor"]["details"],
        provenance=data["operator_class_descriptor"].get("provenance", {}),
    )

    inv_res = StructuralInvariantResult(
        permutation_invariant_status=data["structural_invariant_result"]["permutation_invariant_status"],
        permutation_invariant_classification=BoundClassification(
            data["structural_invariant_result"]["permutation_invariant_classification"]
        ),
        real_amplitude_status=data["structural_invariant_result"]["real_amplitude_status"],
        real_amplitude_classification=BoundClassification(
            data["structural_invariant_result"]["real_amplitude_classification"]
        ),
        superposition_status=data["structural_invariant_result"]["superposition_status"],
        superposition_generates=data["structural_invariant_result"]["superposition_generates"],
        composition_closure_status=data["structural_invariant_result"]["composition_closure_status"],
        inverse_closure_status=data["structural_invariant_result"]["inverse_closure_status"],
        identity_status=data["structural_invariant_result"]["identity_status"],
        identity_circuit_id=data["structural_invariant_result"].get("identity_circuit_id"),
        provenance=data["structural_invariant_result"].get("provenance", {}),
    )

    fail_code = Stage3FailureCode(data["failure_code"]) if data.get("failure_code") else None

    return Stage3AnalysisReport(
        experiment_id=data["experiment_id"],
        domain_descriptor=domain_desc,
        codomain_descriptor=codomain_desc,
        compiler_mapping_records=tuple(mapping_recs),
        mapping_totality_status=MappingTotalityStatus(data["mapping_totality_status"]),
        quotient_well_definedness_status=QuotientWellDefinednessStatus(data["quotient_well_definedness_status"]),
        quotient_records=tuple(quotient_recs),
        structural_image_bound=struct_bound,
        semantic_image_bound=sem_bound,
        domain_cardinality_bound=domain_card,
        codomain_cardinality_bound=codomain_card,
        image_cardinality_bound=img_card,
        mapping_complexity_records=tuple(complexity_recs),
        operator_class_descriptor=op_desc,
        structural_invariant_result=inv_res,
        hadamard_formal_status=data["hadamard_formal_status"],
        hadamard_exclusion_proof=data["hadamard_exclusion_proof"],
        injectivity_status=InjectivityStatus(data["injectivity_status"]),
        surjectivity_status=SurjectivityStatus(data["surjectivity_status"]),
        universal_expressibility_status=UniversalExpressibilityStatus(data["universal_expressibility_status"]),
        provenance=data["provenance"],
        deterministic_analysis_id=data["deterministic_analysis_id"],
        failure_code=fail_code,
        failure_message=data.get("failure_message"),
        diagnostics=tuple(data.get("diagnostics", ())),
    )
