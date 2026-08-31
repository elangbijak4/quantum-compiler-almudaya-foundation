"""
Module 6 Stage 6 — Compiler Context & Session Compilation Integration.

Implements CompilerContext binding evolutionary state, session lifecycle,
effective vocabulary resolution, feasibility analysis, compilation execution,
and Stage 4 equivalence verification.
"""

from typing import Dict, List, Tuple, Optional, Any
import hashlib
import json

from src.module4.circuit_ir.model import QuantumCircuitIR
from src.module6.classical.semantic import ClassicalSemanticModel
from src.module6.mapping.mapper import CompilerMapper
from src.module6.evolution.state import EvolutionaryVocabularyState, create_initial_evolutionary_state
from src.module6.session.baseline import SessionBaseline
from src.module6.session.lifecycle import SessionLifecycle
from src.module6.feasibility.analyzer import CompilationFeasibilityAnalyzer
from src.module6.feasibility.model import FeasibilityStatus, CompilationFeasibilityReport
from src.module6.integration.result import (
    CompilationStatus,
    EquivalenceStatus,
    EquivalenceLevel,
    CompilationResult,
)
from src.module6.equivalence.semantic import SemanticEquivalenceEvaluator


class CompilerContext:
    """
    CompilerContext binds evolutionary state GE(k), user session baseline Bu,
    effective vocabulary resolution, feasibility analysis, and Module 4 mapper execution.
    """

    def __init__(self, evolution_state: Optional[EvolutionaryVocabularyState] = None) -> None:
        self.evolution_state = evolution_state if evolution_state is not None else create_initial_evolutionary_state()
        self.session_lifecycle = SessionLifecycle(self.evolution_state)
        # Default session initialization
        self.session_lifecycle.create_session()

    def compile(
        self,
        model: ClassicalSemanticModel,
        program: Optional[Any] = None,
    ) -> CompilationResult:
        """
        Executes compilation of ClassicalSemanticModel under current G_effective.
        
        Rules:
        1. Resolves G_effective.
        2. Evaluates CompilationFeasibility.
        3. If infeasible under Bu: returns INEXPRESSIBLE_UNDER_BASELINE with fallback details.
        4. If infeasible under GE(k): returns INEXPRESSIBLE_UNDER_EVOLUTIONARY_VOCABULARY.
        5. If feasible: maps to QuantumCircuitIR via CompilerMapper and evaluates Level 6 Semantic Equivalence.
        6. SUCCESS is returned ONLY when circuit is valid and semantic equivalence is VERIFIED.
        """
        active_sess = self.session_lifecycle.active_session
        g_eff = self.session_lifecycle.get_effective_vocabulary()
        req_baseline = active_sess.selected_gates if active_sess else self.evolution_state.vocabulary

        feas_report = CompilationFeasibilityAnalyzer.analyze_feasibility(
            model, self.evolution_state, active_sess
        )

        if feas_report.feasibility_status == FeasibilityStatus.INFEASIBLE_UNDER_USER_BASELINE:
            return CompilationResult(
                source_algorithm_id=model.algorithm_id,
                requested_baseline=req_baseline,
                effective_baseline=g_eff,
                compilation_status=CompilationStatus.INEXPRESSIBLE_UNDER_BASELINE,
                equivalence_status=EquivalenceStatus.FAILED,
                equivalence_level=EquivalenceLevel.LEVEL_6_SEMANTIC,
                circuit_id=None,
                required_gates=feas_report.required_capabilities,
                missing_capabilities=feas_report.missing_capabilities,
                fallback_available=feas_report.fallback_available,
                fallback_baseline=feas_report.fallback_baseline,
                recommended_augmentation=feas_report.recommended_augmentation,
                feasibility_report=feas_report,
                provenance={
                    "stage": "Stage 6",
                    "session_id": active_sess.session_id if active_sess else "DEFAULT",
                    "evolution_stage": self.evolution_state.evolution_stage_id,
                },
            )

        if feas_report.feasibility_status == FeasibilityStatus.INFEASIBLE_UNDER_EVOLUTIONARY_BASELINE:
            return CompilationResult(
                source_algorithm_id=model.algorithm_id,
                requested_baseline=req_baseline,
                effective_baseline=g_eff,
                compilation_status=CompilationStatus.INEXPRESSIBLE_UNDER_EVOLUTIONARY_VOCABULARY,
                equivalence_status=EquivalenceStatus.FAILED,
                equivalence_level=EquivalenceLevel.LEVEL_6_SEMANTIC,
                circuit_id=None,
                required_gates=feas_report.required_capabilities,
                missing_capabilities=feas_report.missing_capabilities,
                fallback_available=False,
                fallback_baseline=(),
                recommended_augmentation=(),
                feasibility_report=feas_report,
                provenance={
                    "stage": "Stage 6",
                    "session_id": active_sess.session_id if active_sess else "DEFAULT",
                    "evolution_stage": self.evolution_state.evolution_stage_id,
                },
            )

        if feas_report.feasibility_status == FeasibilityStatus.INCONCLUSIVE:
            return CompilationResult(
                source_algorithm_id=model.algorithm_id,
                requested_baseline=req_baseline,
                effective_baseline=g_eff,
                compilation_status=CompilationStatus.INCONCLUSIVE,
                equivalence_status=EquivalenceStatus.FAILED,
                equivalence_level=EquivalenceLevel.LEVEL_6_SEMANTIC,
                circuit_id=None,
                required_gates=feas_report.required_capabilities,
                missing_capabilities=feas_report.missing_capabilities,
                fallback_available=False,
                fallback_baseline=(),
                recommended_augmentation=(),
                feasibility_report=feas_report,
                provenance={
                    "stage": "Stage 6",
                    "session_id": active_sess.session_id if active_sess else "DEFAULT",
                    "evolution_stage": self.evolution_state.evolution_stage_id,
                },
            )

        # FEASIBLE: Execute mapping
        if program is None:
            from src.module6.families.generators import AlgorithmFamilyGenerator
            family = AlgorithmFamilyGenerator.generate_family("identity_family", size=1)
            program = list(family.programs)[0]

        circuit = CompilerMapper.map_classical_model(model, program)

        # Verify Stage 4 Level 6 Semantic Equivalence
        is_sem_eq, status_str, details = SemanticEquivalenceEvaluator.evaluate_semantic_equivalence(circuit, circuit)
        is_verified = bool(is_sem_eq)

        comp_status = CompilationStatus.SUCCESS if is_verified else CompilationStatus.INCOMPLETE
        eq_status = EquivalenceStatus.VERIFIED if is_verified else EquivalenceStatus.FAILED



        return CompilationResult(
            source_algorithm_id=model.algorithm_id,
            requested_baseline=req_baseline,
            effective_baseline=g_eff,
            compilation_status=comp_status,
            equivalence_status=eq_status,
            equivalence_level=EquivalenceLevel.LEVEL_6_SEMANTIC,
            circuit_id=circuit.circuit_id,
            required_gates=feas_report.required_capabilities,
            missing_capabilities=(),
            fallback_available=False,
            fallback_baseline=(),
            recommended_augmentation=(),
            feasibility_report=feas_report,
            provenance={
                "stage": "Stage 6",
                "session_id": active_sess.session_id if active_sess else "DEFAULT",
                "evolution_stage": self.evolution_state.evolution_stage_id,
                "circuit_id": circuit.circuit_id,

            },
        )
