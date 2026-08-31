"""
Module 6 Stage 9 Test Suite — Pareto Trade-off Analyzer Tests.
"""

import unittest
from src.module6.quality.model import (
    ResourceProfile,
    QualityProfile,
    ResultClassification,
    ParetoStatus,
)
from src.module6.quality.pareto import ParetoTradeOffAnalyzer


class TestStage9Pareto(unittest.TestCase):
    """Tests verifying Pareto dominance, trade-off analysis, and frontier identification."""

    def _create_profile(
        self,
        total_qubits: int = 5,
        total_gate_count: int = 10,
        circuit_depth: int = 4,
        t_gate_count: int = 2,
    ) -> QualityProfile:
        r_prof = ResourceProfile(
            total_qubits=total_qubits,
            data_qubits=total_qubits,
            ancilla_qubits=0,
            total_gate_count=total_gate_count,
            circuit_depth=circuit_depth,
            t_gate_count=t_gate_count,
            t_gate_depth=t_gate_count,
            cnot_gate_count=2,
            cnot_depth=2,
            gate_distribution={"X": 2, "CNOT": 2, "T_GATE": t_gate_count},
        )
        return QualityProfile(
            semantic_equivalence_verified=True,
            feasibility_status="FEASIBLE",
            resource_profile=r_prof,
            optimization_reduction=0,
            vocabulary_compatibility=True,
            provenance_completeness=True,
            classification=ResultClassification.SEMANTICALLY_VALID,
        )

    def test_01_pareto_equal(self) -> None:
        """Case 1: Identical active objective metrics yield EQUAL status."""
        p1 = self._create_profile(total_gate_count=10, circuit_depth=5)
        p2 = self._create_profile(total_gate_count=10, circuit_depth=5)

        res = ParetoTradeOffAnalyzer.compare_candidates("A", p1, "B", p2)
        self.assertEqual(res.pareto_status, ParetoStatus.EQUAL)
        self.assertIsNone(res.dominant_candidate_id)

    def test_02_pareto_dominates(self) -> None:
        """Case 2: A <= B on all objectives and A < B on at least one -> A DOMINATES B."""
        p1 = self._create_profile(total_gate_count=8, circuit_depth=3)
        p2 = self._create_profile(total_gate_count=10, circuit_depth=5)

        res = ParetoTradeOffAnalyzer.compare_candidates("A", p1, "B", p2)
        self.assertEqual(res.pareto_status, ParetoStatus.DOMINATED)
        self.assertEqual(res.dominant_candidate_id, "A")

    def test_03_pareto_incomparable(self) -> None:
        """Case 3: A better on gate count, B better on depth -> INCOMPARABLE."""
        p1 = self._create_profile(total_gate_count=8, circuit_depth=6)  # Fewer gates, greater depth
        p2 = self._create_profile(total_gate_count=12, circuit_depth=3) # More gates, lower depth

        res = ParetoTradeOffAnalyzer.compare_candidates("A", p1, "B", p2)
        self.assertEqual(res.pareto_status, ParetoStatus.INCOMPARABLE)
        self.assertIsNone(res.dominant_candidate_id)

    def test_04_inactive_objectives_ignored(self) -> None:
        """Case 4: Inactive objective differences MUST NOT affect dominance calculation."""
        p1 = self._create_profile(total_gate_count=10, circuit_depth=5, t_gate_count=100)
        p2 = self._create_profile(total_gate_count=10, circuit_depth=5, t_gate_count=1)

        # Active objectives explicitly do NOT include t_gate_count
        res = ParetoTradeOffAnalyzer.compare_candidates(
            "A", p1, "B", p2, active_objectives=("total_gate_count", "circuit_depth")
        )
        self.assertEqual(res.pareto_status, ParetoStatus.EQUAL)
        self.assertIsNone(res.dominant_candidate_id)

    def test_05_find_pareto_frontier(self) -> None:
        """Verifies find_pareto_frontier identifies only non-dominated candidate profiles."""
        p_dom = self._create_profile(total_gate_count=20, circuit_depth=10) # Dominated by all
        p_opt1 = self._create_profile(total_gate_count=8, circuit_depth=6)  # Frontier 1
        p_opt2 = self._create_profile(total_gate_count=12, circuit_depth=3) # Frontier 2

        candidates = [("C_DOM", p_dom), ("C_OPT1", p_opt1), ("C_OPT2", p_opt2)]
        frontier = ParetoTradeOffAnalyzer.find_pareto_frontier(candidates)

        frontier_ids = [cid for cid, _ in frontier]
        self.assertIn("C_OPT1", frontier_ids)
        self.assertIn("C_OPT2", frontier_ids)
        self.assertNotIn("C_DOM", frontier_ids)


if __name__ == "__main__":
    unittest.main()
