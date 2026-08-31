"""
Module 6 Stage 6 — Minimal Gate Augmentation Analyzer.

Analyzes minimal gate set C_min = Bu* \ Bu sufficient to establish compilation feasibility under user baseline Bu.
Recommendation-only: MUST NOT automatically mutate Bu or GE(k).
"""

from typing import Tuple, List, Set
from src.module6.evolution.state import EvolutionaryVocabularyState
from src.module6.session.baseline import SessionBaseline


class MinimalAugmentationAnalyzer:
    """
    Analyzes minimal additional gate set C_min sufficient to satisfy required capabilities.
    
    Invariant: Recommendation only. Never mutates session baseline Bu or evolutionary state GE(k).
    """

    @classmethod
    def find_minimal_augmentation(
        cls,
        user_baseline_gates: Tuple[str, ...],
        evolutionary_gates: Tuple[str, ...],
        missing_capabilities: Tuple[str, ...],
    ) -> Tuple[str, ...]:
        """
        Determines minimal additional gate set C_min from evolutionary gates that satisfies missing capabilities.
        """
        if not missing_capabilities:
            return ()

        bu_set = set(user_baseline_gates)
        ge_set = set(evolutionary_gates)

        # Available candidates in GE(k) not in Bu
        available_in_ge = ge_set - bu_set

        c_min: List[str] = []
        for req in missing_capabilities:
            req_upper = req.upper()
            if req_upper in available_in_ge:
                c_min.append(req_upper)
            elif "SUPERPOS" in req_upper and "HADAMARD" in available_in_ge:
                c_min.append("HADAMARD")
            elif "COMPLEX" in req_upper or "PHASE" in req_upper:
                if "PHASE_S" in available_in_ge:
                    c_min.append("PHASE_S")
                elif "T_GATE" in available_in_ge:
                    c_min.append("T_GATE")

        return tuple(sorted(set(c_min)))
