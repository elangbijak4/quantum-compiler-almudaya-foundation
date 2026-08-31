"""
Module 6 Stage 6 — Compilation Feasibility Analyzer.

Implements CompilationFeasibilityAnalyzer executing 3-level vocabulary diagnosis:
- Level 1: User baseline insufficient (Bu insufficient, GE(k) sufficient).
- Level 2: Evolutionary baseline insufficient (GE(k) insufficient).
- Level 3: Representation inconclusive.
"""

from typing import Dict, List, Tuple, Optional, Any
import hashlib
import json

from src.module6.classical.semantic import ClassicalSemanticModel
from src.module6.evolution.state import EvolutionaryVocabularyState
from src.module6.session.baseline import SessionBaseline
from src.module6.session.resolver import EffectiveVocabularyResolver
from src.module6.feasibility.model import (
    FeasibilityStatus,
    DiagnosisLevel,
    CompilationFeasibilityReport,
)
from src.module6.feasibility.augmentation import MinimalAugmentationAnalyzer


class CompilationFeasibilityAnalyzer:
    """
    Analyzes compilation feasibility for a source classical algorithm model under effective gate vocabulary G_effective.
    """

    @classmethod
    def analyze_feasibility(
        cls,
        model: ClassicalSemanticModel,
        evolution_state: EvolutionaryVocabularyState,
        session_baseline: SessionBaseline,
        search_depth: int = 10,
    ) -> CompilationFeasibilityReport:
        """
        Evaluates feasibility and executes 3-level vocabulary diagnosis.
        """
        g_eff = EffectiveVocabularyResolver.resolve_effective_vocabulary(evolution_state, session_baseline)
        ge_vocab = evolution_state.vocabulary
        bu_vocab = session_baseline.selected_gates

        # Analyze required capabilities for algorithm model
        req_caps: List[str] = ["PERMUTATION_REVERSIBLE"]

        # Check if algorithm model requires quantum superposition or complex phase
        alg_name = model.algorithm_id.lower()
        requires_superposition = ("quantum" in alg_name or "superpos" in alg_name or "hadamard" in alg_name)
        requires_complex_phase = ("phase" in alg_name or "fourier" in alg_name or "t_gate" in alg_name)

        if requires_superposition:
            req_caps.append("SUPERPOSITION")
        if requires_complex_phase:
            req_caps.append("COMPLEX_PHASE")

        # Evaluate capability support under G_effective
        g_eff_set = set(g_eff)
        ge_set = set(ge_vocab)

        has_superposition_eff = ("HADAMARD" in g_eff_set or "H" in g_eff_set)
        has_complex_eff = ("PHASE_S" in g_eff_set or "T_GATE" in g_eff_set or "S" in g_eff_set or "T" in g_eff_set)

        has_superposition_ge = ("HADAMARD" in ge_set or "H" in ge_set)
        has_complex_ge = ("PHASE_S" in ge_set or "T_GATE" in ge_set or "S" in ge_set or "T" in ge_set)

        missing_eff: List[str] = []
        if requires_superposition and not has_superposition_eff:
            missing_eff.append("SUPERPOSITION")
        if requires_complex_phase and not has_complex_eff:
            missing_eff.append("COMPLEX_PHASE")

        missing_ge: List[str] = []
        if requires_superposition and not has_superposition_ge:
            missing_ge.append("SUPERPOSITION")
        if requires_complex_phase and not has_complex_ge:
            missing_ge.append("COMPLEX_PHASE")

        # Execute 3-Level Vocabulary Diagnosis
        if not missing_eff:
            status = FeasibilityStatus.FEASIBLE
            diag_level = DiagnosisLevel.FEASIBLE
            fallback_avail = False
            rec_aug: Tuple[str, ...] = ()
        elif not missing_ge and set(bu_vocab) < ge_set:
            # Level 1: User baseline insufficient (Bu insufficient, GE(k) sufficient)
            status = FeasibilityStatus.INFEASIBLE_UNDER_USER_BASELINE
            diag_level = DiagnosisLevel.LEVEL_1_USER_BASELINE_INSUFFICIENT
            fallback_avail = True
            rec_aug = MinimalAugmentationAnalyzer.find_minimal_augmentation(
                bu_vocab, ge_vocab, tuple(missing_eff)
            )
        elif missing_ge:
            # Level 2: Evolutionary baseline insufficient (GE(k) insufficient)
            status = FeasibilityStatus.INFEASIBLE_UNDER_EVOLUTIONARY_BASELINE
            diag_level = DiagnosisLevel.LEVEL_2_EVOLUTIONARY_BASELINE_INSUFFICIENT
            fallback_avail = False
            rec_aug = ()
        else:
            # Level 3: Representation Inconclusive
            status = FeasibilityStatus.INCONCLUSIVE
            diag_level = DiagnosisLevel.LEVEL_3_INCONCLUSIVE
            fallback_avail = False
            rec_aug = ()

        raw_id = f"FEAS_{model.algorithm_id}_{session_baseline.baseline_hash[:8]}_{status.value}"
        det_id = hashlib.sha256(raw_id.encode("utf-8")).hexdigest()[:16]

        return CompilationFeasibilityReport(
            algorithm_id=model.algorithm_id,
            effective_vocabulary=g_eff,
            evolutionary_vocabulary=ge_vocab,
            feasibility_status=status,
            diagnosis_level=diag_level,
            required_capabilities=tuple(req_caps),
            missing_capabilities=tuple(missing_eff),
            fallback_available=fallback_avail,
            fallback_baseline=ge_vocab if fallback_avail else (),
            recommended_augmentation=rec_aug,
            search_depth_evaluated=search_depth,
            provenance={
                "model_hash": model.source_program_hash,
                "session_id": session_baseline.session_id,
                "evolution_stage": evolution_state.evolution_stage_id,
            },
            deterministic_report_id=det_id,
        )
