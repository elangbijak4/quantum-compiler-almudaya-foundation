"""
Module 6 Stage 2 — Master Analysis Orchestrator.

Orchestrates Compiler Image Characterization & Expressibility Analysis (Stage 2).
"""

from typing import Dict, List, Tuple, Optional
import hashlib
from src.module1.utm.model import UTMProgram
from src.module4.circuit_ir.model import QuantumCircuitIR
from src.module6.classical.semantic import ClassicalSemanticModel
from src.module6.mapping.mapper import CompilerMapper
from src.module6.families.generators import AlgorithmFamilyGenerator, AlgorithmFamily
from src.module6.image.characterization import EmpiricalImageCharacterizer, EmpiricalImageSummary
from src.module6.targets.catalog import TargetOperator
from src.module6.targets.builder import TargetCatalogBuilder
from src.module6.vocabulary.analyzer import PrimitiveVocabularyAnalyzer, PrimitiveVocabularyResult
from src.module6.expressibility.config import ExpressibilityExperimentConfig
from src.module6.expressibility.matcher import TargetMatcher
from src.module6.expressibility.report import (
    ExpressibilityReport,
    TargetReachabilityResult,
    TargetReachabilityStatus,
    InjectivityStatus,
    SurjectivityStatus,
    UniversalExpressibilityStatus,
    Stage2FailureCode,
)


def analyze_compiler_image_stage2(
    config: Optional[ExpressibilityExperimentConfig] = None,
    custom_models: Optional[List[ClassicalSemanticModel]] = None,
    custom_programs: Optional[List[UTMProgram]] = None,
    custom_targets: Optional[List[TargetOperator]] = None,
) -> ExpressibilityReport:
    """
    Executes Stage 2 Compiler Image Characterization & Expressibility Analysis.
    """
    if config is None:
        config = ExpressibilityExperimentConfig()

    models: List[ClassicalSemanticModel] = []
    programs: List[UTMProgram] = []

    # 1. Gather or Generate Algorithm Sample A_N
    if custom_models is not None and custom_programs is not None:
        if len(custom_models) != len(custom_programs):
            return ExpressibilityReport(
                experiment_id=config.experiment_id,
                algorithm_family="custom_family",
                sample_size=0,
                circuit_image_size=0,
                operator_image_size=0,
                target_count=0,
                target_results=(),
                collision_results=(),
                primitive_vocabulary_results=(),
                compiler_image_summary=EmpiricalImageSummary(0, 0, 0, 0.0, 0.0, (), (), ()),
                injectivity_status=InjectivityStatus.UNPROVEN,
                surjectivity_status=SurjectivityStatus.UNPROVEN,
                universal_expressibility_status=UniversalExpressibilityStatus.UNPROVEN,
                parameter_domain=config.parameter_values,
                maximum_search_depth=config.maximum_circuit_depth,
                numerical_tolerance=config.epsilon,
                provenance={},
                deterministic_analysis_id="INVALID",
                hadamard_result=TargetReachabilityResult("H", "", 1, "", "", (), (), 1.0, "", TargetReachabilityStatus.INVALID_TARGET),
                failure_code=Stage2FailureCode.INVALID_ALGORITHM_FAMILY,
                failure_message="Custom models and programs length mismatch.",
                diagnostics=("Custom models count != custom programs count.",),
            )
        models = list(custom_models)
        programs = list(custom_programs)
    else:
        # Generate algorithm families
        for fam_id in config.algorithm_family_ids:
            limit = config.sample_limits.get(fam_id, config.sample_limits.get("default", 3))
            family = AlgorithmFamilyGenerator.generate_family(fam_id, size=limit)
            models.extend(family.models)
            programs.extend(family.programs)

    if not models:
        return ExpressibilityReport(
            experiment_id=config.experiment_id,
            algorithm_family="empty_family",
            sample_size=0,
            circuit_image_size=0,
            operator_image_size=0,
            target_count=0,
            target_results=(),
            collision_results=(),
            primitive_vocabulary_results=(),
            compiler_image_summary=EmpiricalImageSummary(0, 0, 0, 0.0, 0.0, (), (), ()),
            injectivity_status=InjectivityStatus.UNPROVEN,
            surjectivity_status=SurjectivityStatus.UNPROVEN,
            universal_expressibility_status=UniversalExpressibilityStatus.UNPROVEN,
            parameter_domain=config.parameter_values,
            maximum_search_depth=config.maximum_circuit_depth,
            numerical_tolerance=config.epsilon,
            provenance={},
            deterministic_analysis_id="INVALID",
            hadamard_result=TargetReachabilityResult("H", "", 1, "", "", (), (), 1.0, "", TargetReachabilityStatus.INVALID_TARGET),
            failure_code=Stage2FailureCode.INVALID_ALGORITHM_FAMILY,
            failure_message="No classical algorithm models generated or provided.",
            diagnostics=("Sample A_N is empty.",),
        )

    # 2. Map Classical Models to Logical Circuits F(A)
    circuits: List[QuantumCircuitIR] = []
    for m, p in zip(models, programs):
        circ = CompilerMapper.map_classical_model(m, p)
        circuits.append(circ)

    # 3. Empirical Image Characterization Img_N(F) and OpImg_N(F)
    image_summary = EmpiricalImageCharacterizer.characterize_image(models, circuits)

    # 4. Target Catalog Setup
    targets: List[TargetOperator] = custom_targets if custom_targets is not None else TargetCatalogBuilder.build_default_target_operators()

    # 5. Primitive Vocabulary Analysis & Target Match Search
    target_results: List[TargetReachabilityResult] = []
    vocab_results: List[PrimitiveVocabularyResult] = []

    hadamard_res: Optional[TargetReachabilityResult] = None

    for target in targets:
        # Vocabulary check
        vr = PrimitiveVocabularyAnalyzer.analyze_target_vocabulary(target, max_depth=config.maximum_circuit_depth, tolerance=config.epsilon)
        vocab_results.append(vr)

        # Match check
        tr = TargetMatcher.match_target(
            target=target,
            models=models,
            circuits=circuits,
            global_phase_mode=config.global_phase_mode,
            tolerance=config.epsilon,
        )
        target_results.append(tr)

        if target.target_id == "target_H" or target.is_open_hypothesis:
            hadamard_res = tr

    # Fallback Hadamard result if target_H wasn't explicitly in targets catalog
    if hadamard_res is None:
        h_op = [t for t in TargetCatalogBuilder.build_default_target_operators() if t.target_id == "target_H"][0]
        hadamard_res = TargetMatcher.match_target(h_op, models, circuits, config.global_phase_mode, config.epsilon)

    # 6. Injectivity Status
    has_collisions = len(image_summary.collisions) > 0
    injectivity_status = InjectivityStatus.COLLISION_OBSERVED if has_collisions else InjectivityStatus.NO_COLLISION_OBSERVED

    # Provenance
    provenance = {
        "experiment_config_hash": config.compute_config_hash(),
        "compiler_version": "1.0.0",
        "stage2_version": "1.0.0",
        "sample_algorithm_count": str(len(models)),
        "target_count": str(len(targets)),
    }

    # Deterministic Analysis ID
    raw_det = f"{config.compute_config_hash()}|{len(models)}|{image_summary.circuit_image_count}|{image_summary.operator_image_count}"
    det_id = hashlib.sha256(raw_det.encode("utf-8")).hexdigest()

    return ExpressibilityReport(
        experiment_id=config.experiment_id,
        algorithm_family=",".join(config.algorithm_family_ids),
        sample_size=len(models),
        circuit_image_size=image_summary.circuit_image_count,
        operator_image_size=image_summary.operator_image_count,
        target_count=len(targets),
        target_results=tuple(target_results),
        collision_results=image_summary.collisions,
        primitive_vocabulary_results=tuple(vocab_results),
        compiler_image_summary=image_summary,
        injectivity_status=injectivity_status,
        surjectivity_status=SurjectivityStatus.UNPROVEN,
        universal_expressibility_status=UniversalExpressibilityStatus.UNPROVEN,
        parameter_domain=config.parameter_values,
        maximum_search_depth=config.maximum_circuit_depth,
        numerical_tolerance=config.epsilon,
        provenance=provenance,
        deterministic_analysis_id=det_id,
        hadamard_result=hadamard_res,
        failure_code=None,
        failure_message=None,
        diagnostics=(),
    )
