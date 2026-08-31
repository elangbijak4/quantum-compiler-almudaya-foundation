"""
Module 6 Stage 8 Test Suite — Initialization & Constitutional Verification.
"""

import unittest

from src.module6.evolution.state import create_initial_evolutionary_state
from src.module6.resolution import Stage7CompilerResolver
from src.module6.families.generators import AlgorithmFamilyGenerator
from src.module6.mapping.mapper import CompilerMapper
from src.module6.optimization import (
    Stage8CircuitOptimizer,
    CircuitCostEvaluator,
    OptimizationStatus,
    serialize_optimization_report,
    deserialize_optimization_report,
)


class TestStage8Initialization(unittest.TestCase):
    """Tests for Stage 8 Optimization Scaffold stubs and constitutional invariants."""

    def setUp(self) -> None:
        self.ge0 = create_initial_evolutionary_state()
        family = AlgorithmFamilyGenerator.generate_family("identity_family", size=1)
        self.model = list(family.models)[0]
        self.program = list(family.programs)[0]
        self.ctx = Stage7CompilerResolver.resolve_effective_context(self.ge0)
        self.circuit = CompilerMapper.map_classical_model(self.model, self.program)

    def test_01_circuit_cost_evaluator(self) -> None:
        """Req 1: CircuitCostEvaluator evaluates exact gate counts and depth."""
        metrics = CircuitCostEvaluator.evaluate_cost(self.circuit)
        self.assertGreaterEqual(metrics.total_gate_count, 0)
        self.assertEqual(metrics.qubit_count, self.circuit.total_width)

    def test_02_stage8_optimizer_scaffold_report(self) -> None:
        """Req 2: Stage8CircuitOptimizer returns valid OptimizationCostReport."""
        report = Stage8CircuitOptimizer.analyze_optimization_bounds(
            circuit=self.circuit,
            context=self.ctx,
            model=self.model,
        )
        self.assertEqual(report.algorithm_id, self.model.algorithm_id)
        self.assertTrue(report.semantic_equivalence_verified)
        self.assertEqual(report.effective_vocabulary, ("CNOT", "TOFFOLI", "X"))

    def test_03_optimization_report_serialization(self) -> None:
        """Req 18: Canonical JSON serialization roundtrip."""
        report = Stage8CircuitOptimizer.analyze_optimization_bounds(
            circuit=self.circuit,
            context=self.ctx,
            model=self.model,
        )
        ser = serialize_optimization_report(report)
        des = deserialize_optimization_report(ser)

        self.assertEqual(des.algorithm_id, report.algorithm_id)
        self.assertEqual(des.effective_vocabulary, report.effective_vocabulary)
        self.assertEqual(des.gate_count_reduction, report.gate_count_reduction)
        self.assertEqual(des.status, report.status)


if __name__ == "__main__":
    unittest.main()
