"""
Module 6 Stage 8 Test Suite — Canonical JSON Serialization Roundtrip.
"""

import unittest
from src.module6.evolution.state import create_initial_evolutionary_state
from src.module6.resolution.resolver import Stage7CompilerResolver
from src.module6.families.generators import AlgorithmFamilyGenerator
from src.module6.mapping.mapper import CompilerMapper
from src.module6.optimization.optimizer import Stage8CircuitOptimizer
from src.module6.optimization.serialization import (
    serialize_optimization_report,
    deserialize_optimization_report,
)


class TestStage8Serialization(unittest.TestCase):
    """Tests canonical JSON serialization roundtrip."""

    def setUp(self) -> None:
        self.ge0 = create_initial_evolutionary_state()
        family = AlgorithmFamilyGenerator.generate_family("identity_family", size=1)
        self.model = list(family.models)[0]
        self.program = list(family.programs)[0]
        self.ctx = Stage7CompilerResolver.resolve_effective_context(self.ge0)
        self.circuit = CompilerMapper.map_classical_model(self.model, self.program)

    def test_canonical_json_roundtrip(self) -> None:
        """Req 16, 24: deserialize(serialize(X)) == X canonical roundtrip."""
        report = Stage8CircuitOptimizer.analyze_optimization_bounds(
            circuit=self.circuit,
            context=self.ctx,
            model=self.model,
        )
        json_str = serialize_optimization_report(report)
        restored = deserialize_optimization_report(json_str)

        self.assertEqual(restored.algorithm_id, report.algorithm_id)
        self.assertEqual(restored.effective_vocabulary, report.effective_vocabulary)
        self.assertEqual(restored.gate_count_reduction, report.gate_count_reduction)
        self.assertEqual(restored.status, report.status)
        self.assertEqual(restored.report_hash, report.report_hash)


if __name__ == "__main__":
    unittest.main()
