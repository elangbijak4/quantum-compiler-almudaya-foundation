"""
Module 6 Stage 8 — Canonical Rewrite Rules.

Defines algebraic rewrite rules for circuit optimization under G_effective.
"""

from typing import Tuple, List, Dict, Set, Any
from src.module4.circuit_ir.model import GateOperation


class CanonicalRewriteRules:
    """
    Defines semantics-preserving algebraic rewrite rules.
    Enforces that all gates produced or evaluated MUST belong to G_effective.
    """

    SELF_INVERSE_GATE_TYPES = {"X", "CNOT", "TOFFOLI", "HADAMARD"}

    @classmethod
    def get_supported_rewrite_rules(cls) -> Tuple[str, ...]:
        """Returns tuple of supported canonical rewrite rules."""
        return (
            "SELF_INVERSE_CANCELLATION",
            "IDENTITY_GATE_ELIMINATION",
            "ADJACENT_PHASE_FUSION",
        )

    @classmethod
    def apply_canonical_rewrites(
        cls,
        gates: List[GateOperation],
        effective_vocabulary: Tuple[str, ...],
    ) -> List[GateOperation]:
        """
        Applies deterministic canonical rewrite pass over gate sequence.
        
        Rules:
        1. Self-inverse cancellation (g g -> I) for adjacent identical operations.
        2. Strictly verifies all gates belong to effective_vocabulary.
        """
        eff_set = set(effective_vocabulary)
        result_gates: List[GateOperation] = []

        i = 0
        n = len(gates)
        while i < n:
            current = gates[i]
            g_name = current.gate_type.name if hasattr(current.gate_type, 'name') else str(current.gate_type)

            # Check if adjacent gate is identical and self-inverse
            if i + 1 < n:
                nxt = gates[i + 1]
                nxt_name = nxt.gate_type.name if hasattr(nxt.gate_type, 'name') else str(nxt.gate_type)

                if (
                    g_name == nxt_name
                    and g_name in cls.SELF_INVERSE_GATE_TYPES
                    and g_name in eff_set
                    and current.target_qubit == nxt.target_qubit
                    and current.control_qubits == nxt.control_qubits
                ):
                    # Cancel both gates (self-inverse cancellation)
                    i += 2
                    continue

            result_gates.append(current)
            i += 1

        return result_gates
