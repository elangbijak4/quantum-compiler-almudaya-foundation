"""
Module 6 Stage 7 — Master Evolutionary Compiler Resolution & Control Analysis.

Orchestrates formal Stage 7 analytical evaluation and verification report generation.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Tuple
import hashlib
import json

from src.module6.evolution.state import create_initial_evolutionary_state
from src.module6.evolution.lineage import EvolutionaryLineageManager
from src.module6.session.baseline import SessionBaseline, BaselineMode
from src.module6.session.lifecycle import SessionLifecycle
from src.module6.classical.semantic import create_sample_adder_model
from src.module6.resolution.resolver import Stage7CompilerResolver
from src.module6.resolution.model import (
    EffectiveCompilationContext,
    ResolutionResult,
    ConfigurationStatus,
)
from src.module6.resolution.serialization import serialize_compilation_context


@dataclass(frozen=True)
class Stage7AnalysisReport:
    """
    Immutable comprehensive analytical report for Module 6 Stage 7.
    """
    evolution_stage_id: str
    default_context: EffectiveCompilationContext
    user_context: EffectiveCompilationContext
    dual_result: ResolutionResult
    compilation_success: bool
    evolutionary_immutability_verified: bool
    session_pinning_verified: bool
    no_hidden_gate_expansion_verified: bool
    report_hash: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "evolution_stage_id": self.evolution_stage_id,
            "default_context": self.default_context.to_dict(),
            "user_context": self.user_context.to_dict(),
            "dual_result": self.dual_result.to_dict(),
            "compilation_success": self.compilation_success,
            "evolutionary_immutability_verified": self.evolutionary_immutability_verified,
            "session_pinning_verified": self.session_pinning_verified,
            "no_hidden_gate_expansion_verified": self.no_hidden_gate_expansion_verified,
            "report_hash": self.report_hash,
        }


def analyze_stage7_resolution_and_control() -> Stage7AnalysisReport:
    """
    Executes master Stage 7 resolution and compilation control analysis.
    """
    # 1. Load evolutionary initial state GE(0)
    ge0 = create_initial_evolutionary_state()
    initial_hash = ge0.vocabulary_hash

    # 2. Resolve Default Context
    def_ctx = Stage7CompilerResolver.resolve_effective_context(ge0)

    # 3. User Session & Baseline
    sess, sb = SessionLifecycle.create_session(
        evolution_state=ge0,
        baseline_mode=BaselineMode.USER_SELECTED,
        selected_gates=("CNOT", "X"),
    )

    user_ctx = Stage7CompilerResolver.resolve_effective_context(ge0, sb)

    # 4. Dual Result Feasibility Analysis on Sample Adder
    adder_model = create_sample_adder_model()
    dual_res = Stage7CompilerResolver.resolve_and_evaluate_feasibility(
        model=adder_model,
        evolution_state=ge0,
        session_baseline=sb,
    )

    # 5. Execute Compilation under default state (which has TOFFOLI, CNOT, X)
    comp_res = Stage7CompilerResolver.compile_with_resolution(
        model=adder_model,
        evolution_state=ge0,
    )
    is_success = (comp_res.compilation_status.value == "SUCCESS")

    # 6. Verify Invariants
    immutability_ok = (ge0.vocabulary_hash == initial_hash)
    session_pinning_ok = (sb.source_vocabulary_hash == ge0.vocabulary_hash)
    no_hidden_gates_ok = True

    if comp_res.circuit_ir is not None:
        gates = {g.gate_type.name for g in comp_res.circuit_ir.gates}
        no_hidden_gates_ok = gates.issubset(set(ge0.vocabulary))

    raw_report = (
        f"S7_{ge0.evolution_stage_id}_{def_ctx.context_hash}_{user_ctx.context_hash}_"
        f"{dual_res.user_configuration_status}_{is_success}"
    )
    r_hash = hashlib.sha256(raw_report.encode("utf-8")).hexdigest()[:16]

    return Stage7AnalysisReport(
        evolution_stage_id=ge0.evolution_stage_id,
        default_context=def_ctx,
        user_context=user_ctx,
        dual_result=dual_res,
        compilation_success=is_success,
        evolutionary_immutability_verified=immutability_ok,
        session_pinning_verified=session_pinning_ok,
        no_hidden_gate_expansion_verified=no_hidden_gates_ok,
        report_hash=r_hash,
    )
