"""
Module 6 Stage 8 — Evolutionary Circuit Optimization Engine.

Implements production Stage8CircuitOptimizer for deterministic, semantics-preserving
circuit optimization and synthesis cost bounds analysis under G_effective.
"""

from typing import Dict, List, Tuple, Optional, Any
import hashlib
import json

from src.module4.circuit_ir.model import QuantumCircuitIR, GateOperation
from src.module6.classical.semantic import ClassicalSemanticModel
from src.module6.resolution.model import EffectiveCompilationContext, ConfigurationStatus
from src.module6.equivalence.semantic import SemanticEquivalenceEvaluator
from src.module6.optimization.model import (
    OptimizationCostReport,
    CircuitCostMetrics,
    OptimizationStatus,
)
from src.module6.optimization.metrics import CircuitCostEvaluator
from src.module6.optimization.rules import CanonicalRewriteRules
from src.module6.optimization.provenance import OptimizationProvenanceGenerator


class Stage8CircuitOptimizer:
    """
    Production Stage 8 Circuit Optimization Engine.
    
    Invariants Enforced:
    1. Semantic Equivalence Preservation: Q_opt equiv_Q Q_orig under Stage 4 Level 6 verification.
    2. Vocabulary Containment: All gates in Q_opt belong to G_effective. Zero hidden expansion.
    3. Monotonic Cost Reduction: TotalGateCount(Q_opt) <= TotalGateCount(Q_orig).
    4. Evolutionary Immutability: Optimization does NOT mutate GE(k), SessionBaseline, or Stage 7 context.
    """

    @classmethod
    def optimize_circuit(
        cls,
        circuit: QuantumCircuitIR,
        context: EffectiveCompilationContext,
        model: Optional[ClassicalSemanticModel] = None,
    ) -> Tuple[QuantumCircuitIR, OptimizationCostReport]:
        """
        Orchestrates full deterministic optimization pipeline:
        context validation -> cost evaluation -> canonical rewriting -> fixed point ->
        vocabulary containment -> Level 6 semantic equivalence verification -> report generation.
        """
        alg_id = model.algorithm_id if model else (circuit.circuit_id or "UNKNOWN_ALGORITHM")

        # 1. Validate effective context precondition
        cfg_stat = context.configuration_status
        is_feasible = (
            cfg_stat == ConfigurationStatus.VALID_CONFIGURATION
            or (isinstance(cfg_stat, str) and cfg_stat in ("VALID_CONFIGURATION", "FEASIBLE"))
            or (hasattr(cfg_stat, "value") and cfg_stat.value in ("VALID_CONFIGURATION", "FEASIBLE"))
        )

        initial_metrics = CircuitCostEvaluator.evaluate_cost(circuit)

        if not is_feasible or len(context.effective_vocabulary) == 0:
            prov = OptimizationProvenanceGenerator.generate_provenance(
                algorithm_id=alg_id,
                evolution_stage=context.evolution_stage,
                effective_vocabulary=context.effective_vocabulary,
                initial_cost=initial_metrics.total_gate_count,
                optimized_cost=initial_metrics.total_gate_count,
                context_hash=context.context_hash,
                semantic_verified=False,
            )
            r_hash = hashlib.sha256(json.dumps(prov, sort_keys=True).encode()).hexdigest()[:16]
            report = OptimizationCostReport(
                algorithm_id=alg_id,
                effective_vocabulary=context.effective_vocabulary,
                initial_metrics=initial_metrics,
                optimized_metrics=initial_metrics,
                gate_count_reduction=0,
                depth_reduction=0,
                semantic_equivalence_verified=False,
                vocabulary_containment_verified=False,
                status=OptimizationStatus.INVALID_INPUT,
                provenance=prov,
                report_hash=r_hash,
            )
            return circuit, report

        # 2. Verify Vocabulary Containment of Input Circuit
        eff_vocab_set = set(context.effective_vocabulary)
        for g in circuit.gates:
            g_name = g.gate_type.name if hasattr(g.gate_type, 'name') else str(g.gate_type)
            if g_name not in eff_vocab_set:
                prov = OptimizationProvenanceGenerator.generate_provenance(
                    algorithm_id=alg_id,
                    evolution_stage=context.evolution_stage,
                    effective_vocabulary=context.effective_vocabulary,
                    initial_cost=initial_metrics.total_gate_count,
                    optimized_cost=initial_metrics.total_gate_count,
                    context_hash=context.context_hash,
                    semantic_verified=False,
                )
                r_hash = hashlib.sha256(json.dumps(prov, sort_keys=True).encode()).hexdigest()[:16]
                report = OptimizationCostReport(
                    algorithm_id=alg_id,
                    effective_vocabulary=context.effective_vocabulary,
                    initial_metrics=initial_metrics,
                    optimized_metrics=initial_metrics,
                    gate_count_reduction=0,
                    depth_reduction=0,
                    semantic_equivalence_verified=False,
                    vocabulary_containment_verified=False,
                    status=OptimizationStatus.VOCABULARY_VIOLATION,
                    provenance=prov,
                    report_hash=r_hash,
                )
                return circuit, report

        # 3. Iterative Canonical Rewriting until Fixed Point
        current_gates = list(circuit.gates)
        while True:
            rewritten_gates = CanonicalRewriteRules.apply_canonical_rewrites(
                gates=current_gates,
                effective_vocabulary=context.effective_vocabulary,
            )
            if len(rewritten_gates) == len(current_gates):
                break
            current_gates = rewritten_gates

        # Re-index operation indices
        indexed_gates: List[GateOperation] = []
        for idx, g in enumerate(current_gates):
            indexed_gates.append(
                GateOperation(
                    gate_type=g.gate_type,
                    target_qubit=g.target_qubit,
                    control_qubits=g.control_qubits,
                    operation_index=idx,
                )
            )

        optimized_circuit = QuantumCircuitIR(
            circuit_id=f"{circuit.circuit_id}_opt" if circuit.circuit_id else "OPT_CIRCUIT",
            registers=circuit.registers,
            gates=indexed_gates,
            ancilla_declarations=circuit.ancilla_declarations,
            input_register_ids=circuit.input_register_ids,
            output_register_ids=circuit.output_register_ids,
            provenance=circuit.provenance,
            schema_version=circuit.schema_version,
        )

        optimized_metrics = CircuitCostEvaluator.evaluate_cost(optimized_circuit)
        gate_reduction = initial_metrics.total_gate_count - optimized_metrics.total_gate_count
        depth_reduction = initial_metrics.circuit_depth - optimized_metrics.circuit_depth

        # 4. Verify Vocabulary Containment of Optimized Circuit
        for g in optimized_circuit.gates:
            g_name = g.gate_type.name if hasattr(g.gate_type, 'name') else str(g.gate_type)
            if g_name not in eff_vocab_set:
                prov = OptimizationProvenanceGenerator.generate_provenance(
                    algorithm_id=alg_id,
                    evolution_stage=context.evolution_stage,
                    effective_vocabulary=context.effective_vocabulary,
                    initial_cost=initial_metrics.total_gate_count,
                    optimized_cost=initial_metrics.total_gate_count,
                    context_hash=context.context_hash,
                    semantic_verified=False,
                )
                r_hash = hashlib.sha256(json.dumps(prov, sort_keys=True).encode()).hexdigest()[:16]
                report = OptimizationCostReport(
                    algorithm_id=alg_id,
                    effective_vocabulary=context.effective_vocabulary,
                    initial_metrics=initial_metrics,
                    optimized_metrics=initial_metrics,
                    gate_count_reduction=0,
                    depth_reduction=0,
                    semantic_equivalence_verified=False,
                    vocabulary_containment_verified=False,
                    status=OptimizationStatus.VOCABULARY_VIOLATION,
                    provenance=prov,
                    report_hash=r_hash,
                )
                return circuit, report

        # 5. Verify Stage 4 Level 6 Semantic Equivalence
        if gate_reduction == 0:
            is_sem_eq = True
        else:
            is_sem_eq, status_str, details = SemanticEquivalenceEvaluator.evaluate_semantic_equivalence(
                circuit, optimized_circuit
            )

        if not is_sem_eq:
            prov = OptimizationProvenanceGenerator.generate_provenance(
                algorithm_id=alg_id,
                evolution_stage=context.evolution_stage,
                effective_vocabulary=context.effective_vocabulary,
                initial_cost=initial_metrics.total_gate_count,
                optimized_cost=initial_metrics.total_gate_count,
                context_hash=context.context_hash,
                semantic_verified=False,
            )
            r_hash = hashlib.sha256(json.dumps(prov, sort_keys=True).encode()).hexdigest()[:16]
            report = OptimizationCostReport(
                algorithm_id=alg_id,
                effective_vocabulary=context.effective_vocabulary,
                initial_metrics=initial_metrics,
                optimized_metrics=initial_metrics,
                gate_count_reduction=0,
                depth_reduction=0,
                semantic_equivalence_verified=False,
                vocabulary_containment_verified=True,
                status=OptimizationStatus.SEMANTIC_PRESERVATION_FAILED,
                provenance=prov,
                report_hash=r_hash,
            )
            return circuit, report

        # 6. Final Status Classification
        if gate_reduction > 0:
            final_status = OptimizationStatus.OPTIMIZED
            final_circuit = optimized_circuit
        else:
            final_status = OptimizationStatus.NO_REDUCTION_POSSIBLE
            final_circuit = circuit
            optimized_metrics = initial_metrics

        prov = OptimizationProvenanceGenerator.generate_provenance(
            algorithm_id=alg_id,
            evolution_stage=context.evolution_stage,
            effective_vocabulary=context.effective_vocabulary,
            initial_cost=initial_metrics.total_gate_count,
            optimized_cost=optimized_metrics.total_gate_count,
            context_hash=context.context_hash,
            semantic_verified=True,
        )

        raw_report_id = (
            f"REP_OPT_{alg_id}_{context.evolution_stage}_{final_status.value}_"
            f"{initial_metrics.total_gate_count}_{optimized_metrics.total_gate_count}"
        )
        r_hash = hashlib.sha256(raw_report_id.encode("utf-8")).hexdigest()[:16]

        report = OptimizationCostReport(
            algorithm_id=alg_id,
            effective_vocabulary=context.effective_vocabulary,
            initial_metrics=initial_metrics,
            optimized_metrics=optimized_metrics,
            gate_count_reduction=gate_reduction if gate_reduction > 0 else 0,
            depth_reduction=depth_reduction if depth_reduction > 0 else 0,
            semantic_equivalence_verified=True,
            vocabulary_containment_verified=True,
            status=final_status,
            provenance=prov,
            report_hash=r_hash,
        )

        return final_circuit, report

    @classmethod
    def analyze_optimization_bounds(
        cls,
        circuit: QuantumCircuitIR,
        context: EffectiveCompilationContext,
        model: Optional[ClassicalSemanticModel] = None,
    ) -> OptimizationCostReport:
        """
        Convenience analysis method returning OptimizationCostReport.
        """
        _, report = cls.optimize_circuit(circuit=circuit, context=context, model=model)
        return report
