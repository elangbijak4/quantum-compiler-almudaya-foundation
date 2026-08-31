"""
Module 6 Stage 9 — Resource & Quality Evaluator.

Extracts ResourceProfile and constructs QualityProfile without hardware execution or physical noise simulation.
"""

from typing import Dict, Any, Optional, List, Tuple
from src.module4.circuit_ir.model import QuantumCircuitIR
from src.module6.optimization.model import OptimizationCostReport
from src.module6.resolution.model import EffectiveCompilationContext
from src.module6.quality.model import (
    ResourceProfile,
    QualityProfile,
    ResultClassification,
)


class ResourceQualityEvaluator:
    """
    Evaluates exact resource profiles and constructs multi-objective quality profiles.
    
    Non-implication rules enforced:
    - QUALITY != SEMANTIC EQUIVALENCE
    - LOWER GATE COUNT != UNIVERSALLY BETTER CIRCUIT
    - LOWER DEPTH != UNIVERSALLY BETTER CIRCUIT
    - FEASIBLE != OPTIMAL
    - LOGICAL RESOURCE METRIC != PHYSICAL HARDWARE COST
    """

    @classmethod
    def extract_resource_profile(cls, circuit: QuantumCircuitIR) -> ResourceProfile:
        """
        Extracts logical ResourceProfile from QuantumCircuitIR.
        All metrics are non-negative integers derived solely from the logical representation.
        """
        gate_counts: Dict[str, int] = {}
        t_count = 0
        cnot_count = 0

        for gate in circuit.gates:
            g_name = gate.gate_type.name if hasattr(gate.gate_type, 'name') else str(gate.gate_type)
            gate_counts[g_name] = gate_counts.get(g_name, 0) + 1
            if g_name == "T_GATE":
                t_count += 1
            elif g_name == "CNOT":
                cnot_count += 1

        ancilla_count = len(circuit.ancilla_declarations) if circuit.ancilla_declarations else 0
        total_q = circuit.total_width
        data_q = max(0, total_q - ancilla_count)
        total_gates = len(circuit.gates)

        # Depth tracking per qubit line
        qubit_depths: Dict[int, int] = {}
        t_depths: Dict[int, int] = {}
        cnot_depths: Dict[int, int] = {}

        for gate in circuit.gates:
            targets = gate.target_qubits if hasattr(gate, 'target_qubits') and gate.target_qubits else []
            controls = gate.control_qubits if hasattr(gate, 'control_qubits') and gate.control_qubits else []
            all_q = list(set(targets + controls))
            if not all_q:
                all_q = [0]

            max_d = max([qubit_depths.get(q, 0) for q in all_q], default=0) + 1
            for q in all_q:
                qubit_depths[q] = max_d

            g_name = gate.gate_type.name if hasattr(gate.gate_type, 'name') else str(gate.gate_type)
            if g_name == "T_GATE":
                max_td = max([t_depths.get(q, 0) for q in all_q], default=0) + 1
                for q in all_q:
                    t_depths[q] = max_td

            if g_name == "CNOT":
                max_cnotd = max([cnot_depths.get(q, 0) for q in all_q], default=0) + 1
                for q in all_q:
                    cnot_depths[q] = max_cnotd

        c_depth = max(qubit_depths.values(), default=0)
        t_depth = max(t_depths.values(), default=0)
        cnot_depth = max(cnot_depths.values(), default=0)

        return ResourceProfile(
            total_qubits=total_q,
            data_qubits=data_q,
            ancilla_qubits=ancilla_count,
            total_gate_count=total_gates,
            circuit_depth=c_depth,
            t_gate_count=t_count,
            t_gate_depth=t_depth,
            cnot_gate_count=cnot_count,
            cnot_depth=cnot_depth,
            gate_distribution=gate_counts,
        )

    @classmethod
    def check_vocabulary_compatibility(
        cls,
        circuit: QuantumCircuitIR,
        effective_vocabulary: Optional[List[str]] = None,
    ) -> bool:
        """
        Verifies whether every gate in circuit is contained in effective_vocabulary.
        Zero hidden gate insertion or promotion.
        """
        if effective_vocabulary is None:
            return True

        eff_vocab_set = set(effective_vocabulary)

        for gate in circuit.gates:
            g_name = gate.gate_type.name if hasattr(gate.gate_type, 'name') else str(gate.gate_type)
            if g_name not in eff_vocab_set:
                return False
        return True

    @classmethod
    def check_resource_constraints(
        cls,
        resource_profile: ResourceProfile,
        resource_constraints: Optional[Dict[str, int]] = None,
    ) -> List[str]:
        """
        Evaluates declared logical resource constraints against ResourceProfile.
        Returns list of violation descriptions.
        """
        if not resource_constraints:
            return []

        violations: List[str] = []

        if "max_qubits" in resource_constraints and resource_profile.total_qubits > resource_constraints["max_qubits"]:
            violations.append(
                f"total_qubits ({resource_profile.total_qubits}) exceeds max_qubits ({resource_constraints['max_qubits']})"
            )

        if "max_ancillas" in resource_constraints and resource_profile.ancilla_qubits > resource_constraints["max_ancillas"]:
            violations.append(
                f"ancilla_qubits ({resource_profile.ancilla_qubits}) exceeds max_ancillas ({resource_constraints['max_ancillas']})"
            )

        if "max_gate_count" in resource_constraints and resource_profile.total_gate_count > resource_constraints["max_gate_count"]:
            violations.append(
                f"total_gate_count ({resource_profile.total_gate_count}) exceeds max_gate_count ({resource_constraints['max_gate_count']})"
            )

        if "max_depth" in resource_constraints and resource_profile.circuit_depth > resource_constraints["max_depth"]:
            violations.append(
                f"circuit_depth ({resource_profile.circuit_depth}) exceeds max_depth ({resource_constraints['max_depth']})"
            )

        if "max_t_count" in resource_constraints and resource_profile.t_gate_count > resource_constraints["max_t_count"]:
            violations.append(
                f"t_gate_count ({resource_profile.t_gate_count}) exceeds max_t_count ({resource_constraints['max_t_count']})"
            )

        if "max_cnot_count" in resource_constraints and resource_profile.cnot_gate_count > resource_constraints["max_cnot_count"]:
            violations.append(
                f"cnot_gate_count ({resource_profile.cnot_gate_count}) exceeds max_cnot_count ({resource_constraints['max_cnot_count']})"
            )

        return violations

    @classmethod
    def evaluate_quality_profile(
        cls,
        circuit: QuantumCircuitIR,
        context: Optional[EffectiveCompilationContext] = None,
        optimization_report: Optional[OptimizationCostReport] = None,
        semantic_equivalent: bool = True,
        feasibility_status: str = "FEASIBLE",
        resource_constraints: Optional[Dict[str, int]] = None,
    ) -> QualityProfile:
        """
        Constructs a multi-objective QualityProfile.
        """
        res_profile = cls.extract_resource_profile(circuit)

        eff_vocab = context.effective_vocabulary if context else None
        vocab_compat = cls.check_vocabulary_compatibility(circuit, eff_vocab)

        violations = cls.check_resource_constraints(res_profile, resource_constraints)

        opt_reduction = optimization_report.gate_count_reduction if optimization_report else 0

        # Classification precedence:
        # 1. Semantic equivalence failure -> SEMANTICALLY_INVALID
        # 2. Vocabulary incompatibility -> INVALID
        # 3. Resource constraint violation -> RESOURCE_CONSTRAINT_VIOLATION
        # 4. Feasibility failure -> INFEASIBLE
        # 5. Valid -> SEMANTICALLY_VALID / FEASIBLE
        if not semantic_equivalent:
            classification = ResultClassification.SEMANTICALLY_INVALID
        elif not vocab_compat:
            classification = ResultClassification.INVALID
        elif violations:
            classification = ResultClassification.RESOURCE_CONSTRAINT_VIOLATION
        elif feasibility_status not in ("FEASIBLE", "VALID_CONFIGURATION"):
            classification = ResultClassification.INFEASIBLE
        else:
            classification = ResultClassification.SEMANTICALLY_VALID

        return QualityProfile(
            semantic_equivalence_verified=semantic_equivalent,
            feasibility_status=feasibility_status,
            resource_profile=res_profile,
            optimization_reduction=opt_reduction,
            vocabulary_compatibility=vocab_compat,
            provenance_completeness=True,
            classification=classification,
            weighted_quality_score=None,
        )
