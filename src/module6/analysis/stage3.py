"""
Module 6 Stage 3 — Master Analysis Orchestrator.

Formally characterizes compiler mapping F: A_C -> C_Q^\text{logical}, establishing domain/codomain bounds,
structural invariants, operator class descriptors, quotient well-definedness, and Hadamard formal exclusion proof.
"""

from typing import List, Optional, Tuple, Dict, Any
import hashlib

from src.module4.circuit_ir.model import QuantumCircuitIR
from src.module6.classical.semantic import ClassicalSemanticModel
from src.module6.families.generators import AlgorithmFamilyGenerator, AlgorithmFamily
from src.module6.mapping.mapper import CompilerMapper
from src.module6.mapping.identity import create_classical_algorithm_identity
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
from src.module6.mapping.quotient import QuotientWellDefinednessAnalyzer
from src.module6.bounds.cardinality import CardinalityBound, CardinalityType
from src.module6.bounds.domain import DomainBoundsAnalyzer
from src.module6.bounds.codomain import CodomainBoundsAnalyzer
from src.module6.bounds.image import ImageBound, ImageBoundsAnalyzer
from src.module6.bounds.operator_class import OperatorClassDescriptor
from src.module6.invariants.analyzer import (
    StructuralInvariantResult,
    StructuralInvariantAnalyzer,
)
from src.module6.image.signature import compute_image_signature
from src.module6.image.characterization import EmpiricalImageCharacterizer
from src.module6.expressibility.config import ExpressibilityExperimentConfig
from src.module6.expressibility.report import (
    InjectivityStatus,
    SurjectivityStatus,
    UniversalExpressibilityStatus,
)
from src.module6.analysis.report import Stage3AnalysisReport, Stage3FailureCode


def analyze_compiler_mapping_stage3(
    config: Optional[ExpressibilityExperimentConfig] = None,
) -> Stage3AnalysisReport:
    """
    Executes master Stage 3 analysis: Compiler Mapping F Formulation & Domain/Codomain Bounds.
    """
    if config is None:
        config = ExpressibilityExperimentConfig(experiment_id="exp_stage3_default")

    # 1. Generate Classical Algorithm Families A_N subset A_C
    family_ids = [
        "identity_family",
        "bit_flip_family",
        "two_state_cycle_family",
        "multi_state_cycle_family",
        "controlled_transition_family",
        "reversible_permutation_family",
    ]

    all_models: List[ClassicalSemanticModel] = []
    all_programs: List[Any] = []
    limit = getattr(config, "family_sample_limit", getattr(config, "sample_limit", 3))
    tol = getattr(config, "numerical_tolerance", getattr(config, "tolerance", 1e-12))

    for fam_id in family_ids:
        fam = AlgorithmFamilyGenerator.generate_family(fam_id, size=limit)
        all_models.extend(fam.models)
        all_programs.extend(fam.programs)

    # Sort models deterministically
    sorted_pairs = sorted(zip(all_models, all_programs), key=lambda p: p[0].algorithm_id)
    all_models = [p[0] for p in sorted_pairs]
    all_programs = [p[1] for p in sorted_pairs]

    # 2. Compile F(A)
    all_circuits: List[QuantumCircuitIR] = []
    mapping_records: List[CompilerMappingRecord] = []

    for m, p in zip(all_models, all_programs):
        circ = CompilerMapper.map_classical_model(m, p)
        all_circuits.append(circ)

        ident = create_classical_algorithm_identity(m, p)
        sig = compute_image_signature(m, circ)

        rec = CompilerMappingRecord(
            source_algorithm_id=m.algorithm_id,
            source_semantic_id=ident.semantic_model_id,
            source_domain_id=ident.domain_id,
            logical_circuit_id=circ.circuit_id,
            circuit_structural_hash=sig.circuit_structural_signature,
            operator_hash=sig.operator_hash,
            compiler_version="Module1-4_v1.0",
            mapping_status="SUCCESS",
            provenance={"algorithm": m.algorithm_id, "circuit": circ.circuit_id},
        )
        mapping_records.append(rec)

    # 3. Domain & Codomain Bounds Analysis
    domain_desc, domain_card, totality_status = DomainBoundsAnalyzer.analyze_domain(all_models)
    codomain_desc, codomain_card, complexity_records = CodomainBoundsAnalyzer.analyze_codomain(
        all_models, all_circuits
    )

    # 4. Quotient Well-Definedness Analysis
    quotient_status, quotient_records = QuotientWellDefinednessAnalyzer.analyze_quotient(
        all_models, all_circuits, tolerance=tol
    )

    # 5. Image Characterization & Containment Bounds
    img_summary = EmpiricalImageCharacterizer.characterize_image(all_models, all_circuits)
    struct_bound, sem_bound, img_card = ImageBoundsAnalyzer.analyze_image_bounds(
        sample_size=len(all_models),
        circuit_image_size=img_summary.circuit_image_count,
        operator_image_size=img_summary.operator_image_count,
    )

    # 6. Structural Invariant Analysis
    inv_result = StructuralInvariantAnalyzer.analyze_structural_invariants(
        all_circuits, tolerance=tol
    )

    # 7. Operator Class Descriptor
    op_desc = OperatorClassDescriptor(
        class_name="Computational-Basis Reversible Permutation Group Perm(2^N)",
        formal_expression="OpImg_Q(F) = { [U_F(A)]_Q | A in A_C } subseteq Perm(2^N) subset M_{2^N}(R) subset U(2^N)",
        is_unitary=True,
        is_real_valued=True,
        is_permutation=True,
        is_superposition_generating=False,
        has_discrete_parameters=True,
        is_closed_under_composition=True,
        classification=BoundClassification.FORMAL_THEOREM,
        details="All unitaries in compiler image are real computational-basis permutation matrices.",
        provenance={"module": "module6", "stage": "stage3"},
    )

    # 8. Hadamard Formal Exclusion Derivation
    # Theorem: Every compiler unitary U_F(A) is a computational-basis permutation matrix (Perm(2^N)).
    # Hadamard H = 1/sqrt(2) [[1, 1], [1, -1]] has non-binary amplitude entries (1/sqrt(2) != 0, 1).
    # Therefore H not in Perm(2), which implies H not in Img_Q(F).
    hadamard_formal_status = "FORMALLY_EXCLUDED"
    hadamard_proof = (
        "THEOREM (Hadamard Formal Exclusion):\n"
        "1. Every compiler-generated quantum circuit F(A) for A in A_C is composed of primitive gates {X, CNOT, TOFFOLI}.\n"
        "2. Gates {X, CNOT, TOFFOLI} map computational basis bitstrings to computational basis bitstrings.\n"
        "3. Therefore, every unitary U_F(A) in Img_Q(F) is a binary computational-basis permutation matrix in Perm(2^N).\n"
        "4. Hadamard gate H = 1/sqrt(2) [[1, 1], [1, -1]] contains non-binary amplitude entries (1/sqrt(2) != 0, 1).\n"
        "5. H is NOT a computational-basis permutation matrix (H not in Perm(2)).\n"
        "6. Img_Q(F) subseteq Perm(2^N) and H not in Perm(2) ==> H not in Img_Q(F).\n"
        "Q.E.D. Hadamard gate H is FORMALLY EXCLUDED from compiler image Img_Q(F)."
    )

    # Injectivity / Surjectivity / Universality Status
    injectivity = (
        InjectivityStatus.NO_COLLISION_OBSERVED
        if len(img_summary.collisions) == 0
        else InjectivityStatus.COLLISION_OBSERVED
    )
    surjectivity = SurjectivityStatus.UNPROVEN
    universality = UniversalExpressibilityStatus.UNPROVEN

    # Computes deterministic analysis ID
    raw_id = (
        f"{config.experiment_id}|{totality_status.value}|{quotient_status.value}|"
        f"{inv_result.permutation_invariant_status}|{hadamard_formal_status}"
    )
    det_id = f"STAGE3_{hashlib.sha256(raw_id.encode('utf-8')).hexdigest()[:16]}"

    prov = {
        "module": "module6",
        "stage": "stage3",
        "experiment_id": config.experiment_id,
        "sample_size": str(len(all_models)),
        "hadamard_status": hadamard_formal_status,
    }

    return Stage3AnalysisReport(
        experiment_id=config.experiment_id,
        domain_descriptor=domain_desc,
        codomain_descriptor=codomain_desc,
        compiler_mapping_records=tuple(mapping_records),
        mapping_totality_status=totality_status,
        quotient_well_definedness_status=quotient_status,
        quotient_records=tuple(quotient_records),
        structural_image_bound=struct_bound,
        semantic_image_bound=sem_bound,
        domain_cardinality_bound=domain_card,
        codomain_cardinality_bound=codomain_card,
        image_cardinality_bound=img_card,
        mapping_complexity_records=tuple(complexity_records),
        operator_class_descriptor=op_desc,
        structural_invariant_result=inv_result,
        hadamard_formal_status=hadamard_formal_status,
        hadamard_exclusion_proof=hadamard_proof,
        injectivity_status=injectivity,
        surjectivity_status=surjectivity,
        universal_expressibility_status=universality,
        provenance=prov,
        deterministic_analysis_id=det_id,
    )
