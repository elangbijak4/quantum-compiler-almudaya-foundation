"""
Module 6 Stage 9 Test Suite — Quality Profile & Resource Extraction Tests.
"""

unittest_imports = True
import unittest
from src.module6.evolution.state import create_initial_evolutionary_state
from src.module6.resolution import Stage7CompilerResolver
from src.module6.families.generators import AlgorithmFamilyGenerator
from src.module6.mapping.mapper import CompilerMapper
from src.module6.quality import (
    ResourceQualityEvaluator,
    ResultClassification,
    ResourceProfile,
    QualityProfile,
)
from src.module6.analysis.stage9 import analyze_stage9_compilation_quality


class TestStage9QualityProfile(unittest.TestCase):
    """Tests verifying ResourceProfile extraction and multi-objective QualityProfile evaluation."""

    def setUp(self) -> None:
        self.ge0 = create_initial_evolutionary_state()
        family = AlgorithmFamilyGenerator.generate_family("identity_family", size=1)
        self.model = list(family.models)[0]
        self.program = list(family.programs)[0]
        self.ctx = Stage7CompilerResolver.resolve_effective_context(self.ge0)
        self.circuit = CompilerMapper.map_classical_model(self.model, self.program)

    def test_01_exact_integer_resource_metrics(self) -> None:
        """Verifies all ResourceProfile metrics are non-negative integers derived solely from QuantumCircuitIR."""
        profile = ResourceQualityEvaluator.extract_resource_profile(self.circuit)
        self.assertIsInstance(profile.total_qubits, int)
        self.assertGreaterEqual(profile.total_qubits, 0)
        self.assertIsInstance(profile.data_qubits, int)
        self.assertGreaterEqual(profile.data_qubits, 0)
        self.assertIsInstance(profile.ancilla_qubits, int)
        self.assertGreaterEqual(profile.ancilla_qubits, 0)
        self.assertIsInstance(profile.total_gate_count, int)
        self.assertGreaterEqual(profile.total_gate_count, 0)
        self.assertIsInstance(profile.circuit_depth, int)
        self.assertGreaterEqual(profile.circuit_depth, 0)
        self.assertIsInstance(profile.t_gate_count, int)
        self.assertGreaterEqual(profile.t_gate_count, 0)
        self.assertIsInstance(profile.t_gate_depth, int)
        self.assertGreaterEqual(profile.t_gate_depth, 0)
        self.assertIsInstance(profile.cnot_gate_count, int)
        self.assertGreaterEqual(profile.cnot_gate_count, 0)
        self.assertIsInstance(profile.cnot_depth, int)
        self.assertGreaterEqual(profile.cnot_depth, 0)

    def test_02_multi_objective_dimensions_preserved(self) -> None:
        """Verifies QualityProfile preserves distinct dimensions without collapsing them into a single scalar score."""
        q_prof = ResourceQualityEvaluator.evaluate_quality_profile(
            circuit=self.circuit,
            context=self.ctx,
            semantic_equivalent=True,
        )
        self.assertTrue(q_prof.semantic_equivalence_verified)
        self.assertEqual(q_prof.classification, ResultClassification.SEMANTICALLY_VALID)
        self.assertIsNone(q_prof.weighted_quality_score)

    def test_03_master_stage9_quality_report(self) -> None:
        """Verifies analyze_stage9_compilation_quality produces a valid QualityAnalysisReport."""
        report = analyze_stage9_compilation_quality(
            circuit=self.circuit,
            context=self.ctx,
            model=self.model,
        )
        self.assertEqual(report.classification, ResultClassification.SEMANTICALLY_VALID)
        self.assertTrue(report.quality_profile.semantic_equivalence_verified)
        self.assertIsNotNone(report.report_hash)
        self.assertTrue(len(report.report_hash) > 0)


if __name__ == "__main__":
    unittest.main()
