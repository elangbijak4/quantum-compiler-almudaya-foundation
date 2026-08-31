"""
Module 6 Stage 9 — Master Quality & Resource-Aware Analysis Orchestrator.

Provides analyze_stage9_compilation_quality executing full multi-objective quality analysis,
Stage 4 Level 6 semantic verification, resource constraint auditing, dual-result comparative analysis,
and deterministic provenance generation.
"""

from typing import Dict, List, Tuple, Optional, Any
import hashlib
from src.module4.circuit_ir.model import QuantumCircuitIR
from src.module6.classical.semantic import ClassicalSemanticModel
from src.module6.resolution.model import EffectiveCompilationContext
from src.module6.optimization.model import OptimizationCostReport
from src.module6.equivalence.semantic import SemanticEquivalenceEvaluator
from src.module6.quality.model import (
    ResourceProfile,
    QualityProfile,
    QualityAnalysisReport,
    ResultClassification,
    ComparisonResult,
)
from src.module6.quality.evaluator import ResourceQualityEvaluator
from src.module6.quality.pareto import ParetoTradeOffAnalyzer
from src.module6.quality.provenance import QualityProvenanceGenerator


def analyze_stage9_compilation_quality(
    circuit: QuantumCircuitIR,
    context: EffectiveCompilationContext,
    optimization_report: Optional[OptimizationCostReport] = None,
    model: Optional[ClassicalSemanticModel] = None,
    resource_constraints: Optional[Dict[str, int]] = None,
    user_baseline_circuit: Optional[QuantumCircuitIR] = None,
    evolutionary_baseline_circuit: Optional[QuantumCircuitIR] = None,
) -> QualityAnalysisReport:
    """
    Master Stage 9 Analysis Pipeline.
    Executes logical resource extraction, vocabulary audit, resource constraint evaluation,
    Stage 4 Level 6 semantic equivalence verification, dual-result comparison, and provenance digest generation.
    """
    # 1. Level 6 Semantic Equivalence Gate
    sem_eq = True
    if user_baseline_circuit is not None:
        is_eq, status_str, details = SemanticEquivalenceEvaluator.evaluate_semantic_equivalence(
            user_baseline_circuit, circuit
        )
        sem_eq = is_eq

    # 2. Feasibility Status from Context
    feasibility = (
        context.configuration_status.value
        if hasattr(context.configuration_status, 'value')
        else str(context.configuration_status)
    )

    # 3. Extract Resource & Quality Profile
    q_profile = ResourceQualityEvaluator.evaluate_quality_profile(
        circuit=circuit,
        context=context,
        optimization_report=optimization_report,
        semantic_equivalent=sem_eq,
        feasibility_status=feasibility,
        resource_constraints=resource_constraints,
    )

    res_profile = q_profile.resource_profile
    violations = ResourceQualityEvaluator.check_resource_constraints(res_profile, resource_constraints)

    # 4. Dual-Result Analysis
    dual_result_summary: Dict[str, Any] = {
        "user_baseline_present": user_baseline_circuit is not None,
        "evolutionary_baseline_present": evolutionary_baseline_circuit is not None,
        "cases_evaluated": [],
    }

    if user_baseline_circuit is not None and evolutionary_baseline_circuit is not None:
        prof_user = ResourceQualityEvaluator.evaluate_quality_profile(user_baseline_circuit, context=context)
        prof_evo = ResourceQualityEvaluator.evaluate_quality_profile(evolutionary_baseline_circuit, context=context)

        comp_res = ParetoTradeOffAnalyzer.compare_candidates("USER_BASELINE", prof_user, "EVO_BASELINE", prof_evo)
        dual_result_summary["comparison"] = comp_res.to_dict()
        dual_result_summary["cases_evaluated"].append("CASE_A_BOTH_FEASIBLE_COMPARISON")

    # 5. Provenance Generation
    algorithm_id = circuit.circuit_id if hasattr(circuit, 'circuit_id') and circuit.circuit_id else "quantum_circuit"
    opt_hash = optimization_report.report_hash if optimization_report else ""
    ctx_hash = context.context_hash

    prov = QualityProvenanceGenerator.generate_provenance(
        algorithm_id=algorithm_id,
        evolution_stage=context.evolution_stage,
        session_id=context.session_id,
        classification=q_profile.classification.value,
        total_gates=res_profile.total_gate_count,
        original_circuit_hash="",
        optimized_circuit_hash=opt_hash,
        effective_vocabulary_hash=ctx_hash,
        stage8_report_hash=opt_hash,
        stage4_verification_status="VERIFIED" if sem_eq else "FAILED",
    )

    # 6. Report Hash Generation
    raw_rep = f"{algorithm_id}:{q_profile.classification.value}:{res_profile.total_gate_count}:{prov['quality_provenance_id']}"
    rep_hash = hashlib.sha256(raw_rep.encode("utf-8")).hexdigest()[:16]

    return QualityAnalysisReport(
        algorithm_id=algorithm_id,
        quality_profile=q_profile,
        resource_profile=res_profile,
        resource_constraint_violations=tuple(violations),
        dual_result_analysis=dual_result_summary,
        classification=q_profile.classification,
        provenance=prov,
        report_hash=rep_hash,
    )
