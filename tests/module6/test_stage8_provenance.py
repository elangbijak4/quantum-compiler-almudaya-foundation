"""
Module 6 Stage 8 Test Suite — Deterministic Provenance Generation.
"""

import unittest
from src.module6.optimization.provenance import OptimizationProvenanceGenerator


class TestStage8Provenance(unittest.TestCase):
    """Tests for deterministic provenance generation."""

    def test_provenance_generation(self) -> None:
        """Req 15, 24: OptimizationProvenanceGenerator builds auditable metadata."""
        prov = OptimizationProvenanceGenerator.generate_provenance(
            algorithm_id="ADDER",
            evolution_stage="GE_0",
            effective_vocabulary=("CNOT", "TOFFOLI", "X"),
            initial_cost=5,
            optimized_cost=1,
            context_hash="ctx_123",
            semantic_verified=True,
        )
        self.assertIn("optimization_provenance_id", prov)
        self.assertEqual(prov["algorithm_id"], "ADDER")
        self.assertEqual(prov["initial_gate_count"], 5)
        self.assertEqual(prov["optimized_gate_count"], 1)


if __name__ == "__main__":
    unittest.main()
