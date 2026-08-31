"""
Module 6 Stage 9 — Pareto Trade-off Analyzer.

Implements Pareto dominance, multi-objective comparative trade-off analysis,
and Pareto frontier identification.
"""

from typing import Dict, Any, List, Tuple, Optional, Set
import hashlib
from src.module6.quality.model import (
    QualityProfile,
    ComparisonResult,
    ParetoStatus,
    ResourceProfile,
)


class ParetoTradeOffAnalyzer:
    """
    Evaluates Pareto dominance between candidate compilation results across explicitly declared active objectives.
    
    Minimization Rules:
    - Candidate A dominates B iff A_i <= B_i for ALL active objectives i, AND A_j < B_j for AT LEAST ONE active objective j.
    - If A_i == B_i for ALL active objectives, Pareto status is EQUAL.
    - If A is better in objective X and B is better in objective Y, Pareto status is INCOMPARABLE.
    - Inactive objectives MUST NOT influence dominance calculation.
    """

    DEFAULT_OBJECTIVES: Tuple[str, ...] = ("total_gate_count", "circuit_depth", "total_qubits")

    @classmethod
    def extract_objective_value(cls, profile: ResourceProfile, objective: str) -> int:
        """Extracts objective metric value from ResourceProfile."""
        if hasattr(profile, objective):
            return int(getattr(profile, objective))
        elif objective in profile.gate_distribution:
            return profile.gate_distribution[objective]
        else:
            raise ValueError(f"Unknown resource objective: {objective}")

    @classmethod
    def compare_candidates(
        cls,
        candidate_a_id: str,
        profile_a: QualityProfile,
        candidate_b_id: str,
        profile_b: QualityProfile,
        active_objectives: Optional[Tuple[str, ...]] = None,
    ) -> ComparisonResult:
        """
        Executes Pareto comparison between profile_a and profile_b across active_objectives.
        """
        objectives = active_objectives if active_objectives is not None else cls.DEFAULT_OBJECTIVES
        r_a = profile_a.resource_profile
        r_b = profile_b.resource_profile

        trade_offs: Dict[str, int] = {}
        a_worse_in_any = False
        a_strictly_better_in_any = False

        b_worse_in_any = False
        b_strictly_better_in_any = False

        for obj in objectives:
            val_a = cls.extract_objective_value(r_a, obj)
            val_b = cls.extract_objective_value(r_b, obj)

            diff = val_a - val_b
            trade_offs[f"{obj}_diff"] = diff

            if val_a > val_b:
                a_worse_in_any = True
                b_strictly_better_in_any = True
            elif val_a < val_b:
                b_worse_in_any = True
                a_strictly_better_in_any = True

        if not a_worse_in_any and a_strictly_better_in_any:
            status = ParetoStatus.DOMINATED
            dominant = candidate_a_id
        elif not b_worse_in_any and b_strictly_better_in_any:
            status = ParetoStatus.DOMINATED
            dominant = candidate_b_id
        elif not a_strictly_better_in_any and not b_strictly_better_in_any:
            status = ParetoStatus.EQUAL
            dominant = None
        else:
            status = ParetoStatus.INCOMPARABLE
            dominant = None

        raw_id = f"COMP_{candidate_a_id}_{candidate_b_id}_{status.value}_{'_'.join(str(v) for v in trade_offs.values())}"
        c_hash = hashlib.sha256(raw_id.encode("utf-8")).hexdigest()[:16]

        prov = {
            "stage": "Stage 9 Engine Implementation",
            "active_objectives": list(objectives),
        }

        return ComparisonResult(
            candidate_a_id=candidate_a_id,
            candidate_b_id=candidate_b_id,
            pareto_status=status,
            trade_off_summary=trade_offs,
            dominant_candidate_id=dominant,
            provenance=prov,
            comparison_hash=c_hash,
        )

    @classmethod
    def find_pareto_frontier(
        cls,
        candidates: List[Tuple[str, QualityProfile]],
        active_objectives: Optional[Tuple[str, ...]] = None,
    ) -> List[Tuple[str, QualityProfile]]:
        """
        Identifies non-dominated candidate profiles (the Pareto frontier) from a set of candidates.
        """
        if not candidates:
            return []

        frontier: List[Tuple[str, QualityProfile]] = []

        for i, (id_a, prof_a) in enumerate(candidates):
            dominated = False
            for j, (id_b, prof_b) in enumerate(candidates):
                if i == j:
                    continue
                res = cls.compare_candidates(id_a, prof_a, id_b, prof_b, active_objectives)
                if res.pareto_status == ParetoStatus.DOMINATED and res.dominant_candidate_id == id_b:
                    dominated = True
                    break
            if not dominated:
                frontier.append((id_a, prof_a))

        return frontier
