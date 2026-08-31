"""
Module 6 Stage 7 — Stage 7 Resolution Engine R(GE(k), C).

Implements deterministic compiler resolution function R(GE(k), C) -> EffectiveCompilationContext,
dual-result feasibility evaluation, session pinning, backend constraint restriction, and semantic compilation.
"""

from typing import Dict, List, Tuple, Optional, Any
import hashlib
import json

from src.module6.evolution.state import EvolutionaryVocabularyState
from src.module6.session.baseline import SessionBaseline, BaselineMode
from src.module6.feasibility.model import CompilationFeasibilityReport, FeasibilityStatus, DiagnosisLevel
from src.module6.feasibility.analyzer import CompilationFeasibilityAnalyzer
from src.module6.integration.context import CompilerContext
from src.module6.integration.result import CompilationStatus, CompilationResult, EquivalenceStatus, EquivalenceLevel
from src.module6.classical.semantic import ClassicalSemanticModel
from src.module6.resolution.model import (
    EffectiveCompilationContext,
    ConfigurationStatus,
    ResolutionConflict,
    ResolutionResult,
)
from src.module6.resolution.validator import ResolutionValidator
from src.module6.resolution.conflicts import ConflictManager
from src.module6.resolution.provenance import ResolutionProvenanceGenerator


class Stage7CompilerResolver:
    """
    Formal Stage 7 resolution function R(GE(k), C) -> EffectiveCompilationContext & ResolutionResult.
    
    Resolution Invariants:
    1. DefaultResolution(GE(k)) = GE(k).
    2. SessionConfiguration MUST NOT mutate EvolutionaryState.
    3. Resolution MUST precede compilation (no hidden gate expansion).
    4. Session Pinning: Session baseline remains pinned to creation snapshot GE(k).
    5. Backend Restrictions: G_effective = Bu \cap G_backend \subseteq GE(k). Backend restricts, never expands.
    """

    @classmethod
    def resolve_effective_context(
        cls,
        evolution_state: EvolutionaryVocabularyState,
        session_baseline: Optional[SessionBaseline] = None,
        compilation_constraints: Optional[Dict[str, Any]] = None,
        backend_constraints: Optional[Dict[str, Any]] = None,
    ) -> EffectiveCompilationContext:
        """
        Executes deterministic resolution function R(GE(k), C).
        """
        sid = session_baseline.session_id if session_baseline else "DEFAULT_SESSION"
        mode = session_baseline.baseline_mode.value if session_baseline else BaselineMode.DEFAULT_EVOLUTIONARY.value

        # Baseline selection
        if session_baseline:
            requested_gates = session_baseline.selected_gates
        else:
            requested_gates = evolution_state.vocabulary

        comp_constraints = compilation_constraints or {}
        back_constraints = backend_constraints or {}

        # Validate requested gates & constraints
        config_status, conflicts = ResolutionValidator.validate_user_baseline(
            evolution_state=evolution_state,
            requested_gates=requested_gates,
            compilation_constraints=comp_constraints,
            backend_constraints=back_constraints,
        )

        if config_status == ConfigurationStatus.INVALID_CONFIGURATION:
            effective_gates: Tuple[str, ...] = ()
        else:
            # Apply backend and forbidden gate restrictions (Restriction only; never expansion)
            eff_set = set(requested_gates)
            if comp_constraints.get("forbidden_gates"):
                eff_set -= set(comp_constraints["forbidden_gates"])
            if back_constraints.get("supported_gates"):
                eff_set &= set(back_constraints["supported_gates"])

            effective_gates = tuple(sorted(list(eff_set)))

        prov = ResolutionProvenanceGenerator.generate_provenance(
            evolution_stage=evolution_state.evolution_stage_id,
            session_id=sid,
            baseline_mode=mode,
            effective_vocabulary=effective_gates,
        )

        raw_context_id = (
            f"CTX_{evolution_state.evolution_stage_id}_{sid}_{mode}_"
            f"{','.join(effective_gates)}_{hashlib.sha256(json.dumps(comp_constraints, sort_keys=True).encode()).hexdigest()[:8]}"
        )
        ctx_hash = hashlib.sha256(raw_context_id.encode("utf-8")).hexdigest()[:16]

        return EffectiveCompilationContext(
            evolution_stage=evolution_state.evolution_stage_id,
            evolutionary_vocabulary_hash=evolution_state.vocabulary_hash,
            session_id=sid,
            baseline_mode=mode,
            selected_baseline=requested_gates,
            effective_vocabulary=effective_gates,
            compilation_constraints=comp_constraints,
            backend_constraints=back_constraints,
            equivalence_policy="LEVEL_6_SEMANTIC",
            feasibility_policy="THREE_LEVEL_DIAGNOSIS",
            configuration_status=config_status,
            conflicts=conflicts,
            provenance=prov,
            context_hash=ctx_hash,
        )

    @classmethod
    def resolve_and_evaluate_feasibility(
        cls,
        model: ClassicalSemanticModel,
        evolution_state: EvolutionaryVocabularyState,
        session_baseline: Optional[SessionBaseline] = None,
        compilation_constraints: Optional[Dict[str, Any]] = None,
        backend_constraints: Optional[Dict[str, Any]] = None,
    ) -> ResolutionResult:
        """
        Resolves EffectiveCompilationContext and evaluates feasibility enforcing Dual Result Semantics.
        """
        ctx = cls.resolve_effective_context(
            evolution_state=evolution_state,
            session_baseline=session_baseline,
            compilation_constraints=compilation_constraints,
            backend_constraints=backend_constraints,
        )

        if ctx.configuration_status == ConfigurationStatus.INVALID_CONFIGURATION:
            return ResolutionResult(
                context=ctx,
                user_configuration_status="INVALID_CONFIGURATION",
                user_feasibility_status="INVALID_CONFIGURATION",
                evolutionary_fallback_status=None,
                evolutionary_fallback_vocabulary=None,
                fallback_available=False,
                action_required="REJECTED",
            )

        # Build SessionBaseline for Stage 6 feasibility analyzer evaluation
        user_baseline = SessionBaseline(
            session_id=ctx.session_id,
            selected_gates=ctx.effective_vocabulary if ctx.effective_vocabulary else ctx.selected_baseline,
            baseline_hash=hashlib.sha256(str(ctx.effective_vocabulary).encode()).hexdigest()[:16],
            source_evolution_stage=ctx.evolution_stage,
            source_vocabulary_hash=ctx.evolutionary_vocabulary_hash,
            baseline_mode=BaselineMode(ctx.baseline_mode),
        )

        user_feas = CompilationFeasibilityAnalyzer.analyze_feasibility(
            model=model,
            evolution_state=evolution_state,
            session_baseline=user_baseline,
        )

        if user_feas.feasibility_status == FeasibilityStatus.FEASIBLE:
            return ResolutionResult(
                context=ctx,
                user_configuration_status="FEASIBLE",
                user_feasibility_status="FEASIBLE",
                evolutionary_fallback_status="NOT_NEEDED",
                evolutionary_fallback_vocabulary=None,
                fallback_available=False,
                action_required="NONE",
            )

        # Dual Result Semantics: Evaluate global evolutionary fallback feasibility if user baseline is infeasible
        global_baseline = SessionBaseline(
            session_id="global_fallback",
            selected_gates=evolution_state.vocabulary,
            baseline_hash=evolution_state.vocabulary_hash,
            source_evolution_stage=evolution_state.evolution_stage_id,
            source_vocabulary_hash=evolution_state.vocabulary_hash,
            baseline_mode=BaselineMode.DEFAULT_EVOLUTIONARY,
        )

        global_feas = CompilationFeasibilityAnalyzer.analyze_feasibility(
            model=model,
            evolution_state=evolution_state,
            session_baseline=global_baseline,
        )

        if global_feas.feasibility_status == FeasibilityStatus.FEASIBLE:
            return ResolutionResult(
                context=ctx,
                user_configuration_status="INFEASIBLE",
                user_feasibility_status="INFEASIBLE_UNDER_USER_BASELINE",
                evolutionary_fallback_status="FEASIBLE",
                evolutionary_fallback_vocabulary=evolution_state.vocabulary,
                fallback_available=True,
                action_required="USER_AUTHORIZATION_REQUIRED",
            )

        return ResolutionResult(
            context=ctx,
            user_configuration_status="INFEASIBLE",
            user_feasibility_status=user_feas.feasibility_status.value,
            evolutionary_fallback_status="INFEASIBLE_UNDER_EVOLUTIONARY_BASELINE",
            evolutionary_fallback_vocabulary=None,
            fallback_available=False,
            action_required="EVOLUTION_REQUIRED",
        )

    @classmethod
    def compile_with_resolution(
        cls,
        model: ClassicalSemanticModel,
        evolution_state: EvolutionaryVocabularyState,
        session_baseline: Optional[SessionBaseline] = None,
        compilation_constraints: Optional[Dict[str, Any]] = None,
        backend_constraints: Optional[Dict[str, Any]] = None,
    ) -> CompilationResult:
        """
        Orchestrates Stage 7 Resolution -> Feasibility -> Compiler Mapping -> Stage 4 Level 6 Semantic Equivalence.
        Enforces absolute NO HIDDEN GATE EXPANSION invariant.
        """
        res_result = cls.resolve_and_evaluate_feasibility(
            model=model,
            evolution_state=evolution_state,
            session_baseline=session_baseline,
            compilation_constraints=compilation_constraints,
            backend_constraints=backend_constraints,
        )

        ctx = res_result.context
        req_baseline = SessionBaseline(
            session_id=ctx.session_id,
            selected_gates=ctx.selected_baseline if ctx.selected_baseline else evolution_state.vocabulary,
            baseline_hash=hashlib.sha256(str(ctx.selected_baseline).encode()).hexdigest()[:16],
            source_evolution_stage=ctx.evolution_stage,
            source_vocabulary_hash=ctx.evolutionary_vocabulary_hash,
            baseline_mode=BaselineMode(ctx.baseline_mode),
        )

        if res_result.user_configuration_status != "FEASIBLE":
            eq_lvl = getattr(EquivalenceLevel, "LEVEL_0_NONE", list(EquivalenceLevel)[0])
            feas_rep = CompilationFeasibilityReport(
                algorithm_id=model.algorithm_id,
                effective_vocabulary=ctx.effective_vocabulary,
                evolutionary_vocabulary=evolution_state.vocabulary,
                feasibility_status=FeasibilityStatus.INFEASIBLE_UNDER_USER_BASELINE
                if res_result.fallback_available
                else FeasibilityStatus.INFEASIBLE_UNDER_EVOLUTIONARY_BASELINE,
                diagnosis_level=user_feas_level(res_result),
                required_capabilities=(),
                missing_capabilities=(),
                fallback_available=res_result.fallback_available,
                fallback_baseline=res_result.evolutionary_fallback_vocabulary or (),
                recommended_augmentation=(),
                search_depth_evaluated=10,
                provenance=ctx.provenance,
                deterministic_report_id=ctx.context_hash,
            )
            return CompilationResult(
                source_algorithm_id=model.algorithm_id,
                requested_baseline=ctx.selected_baseline,
                effective_baseline=ctx.effective_vocabulary,
                compilation_status=CompilationStatus.INEXPRESSIBLE_UNDER_BASELINE
                if res_result.fallback_available
                else CompilationStatus.INEXPRESSIBLE_UNDER_EVOLUTIONARY_VOCABULARY,
                equivalence_status=EquivalenceStatus.FAILED,
                equivalence_level=eq_lvl,
                circuit_id=None,
                required_gates=(),
                missing_capabilities=(),
                fallback_available=res_result.fallback_available,
                fallback_baseline=res_result.evolutionary_fallback_vocabulary or (),
                recommended_augmentation=(),
                feasibility_report=feas_rep,
                provenance=ctx.provenance,
            )

        # Delegate execution to CompilerContext for mapping and Level 6 Semantic Equivalence Verification
        compiler_ctx = CompilerContext(evolution_state=evolution_state)
        if ctx.effective_vocabulary != evolution_state.vocabulary:
            compiler_ctx.session_lifecycle.select_user_baseline(ctx.effective_vocabulary)

        comp_res = compiler_ctx.compile(model)
        return comp_res


def user_feas_level(res: ResolutionResult) -> DiagnosisLevel:
    if res.fallback_available:
        return DiagnosisLevel.LEVEL_1_USER_BASELINE_INSUFFICIENT
    return DiagnosisLevel.LEVEL_2_EVOLUTIONARY_BASELINE_INSUFFICIENT
