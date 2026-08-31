"""
Module 6 Stage 9 Test Suite — Canonical Serialization Tests.
"""

import unittest
from src.module6.evolution.state import create_initial_evolutionary_state
from src.module6.resolution import Stage7CompilerResolver
from src.module6.families.generators import AlgorithmFamilyGenerator
from src.module6.mapping.mapper import CompilerMapper
from src.module6.quality import (
    ResourceQualityEvaluator,
    ParetoTradeOffAnalyzer,
    serialize_quality_profile,
    deserialize_quality_profile,
    serialize_comparison_result,
    deserialize_comparison_result,
    serialize_quality_analysis_report,
    deserialize_quality_analysis_report,
)
from src.module6.analysis.stage9 import analyze_stage9_compilation_quality


class TestStage9Serialization(unittest.TestCase):
    """Tests verifying canonical JSON serialization and roundtrip equality deserialize(serialize(X)) == X."""

    def setUp(self) -> None:
        self.ge0 = create_initial_evolutionary_state()
        family = AlgorithmFamilyGenerator.generate_family("identity_family", size=1)
        self.model = list(family.models)[0]
        self.program = list(family.programs)[0]
        self.ctx = Stage7CompilerResolver.resolve_effective_context(self.ge0)
        self.circuit = CompilerMapper.map_classical_model(self.model, self.program)

    def test_01_quality_profile_roundtrip(self) -> None:
        """Verifies deserialize(serialize(QualityProfile)) == QualityProfile."""
        profile = ResourceQualityEvaluator.evaluate_quality_profile(self.circuit, context=self.ctx)
        ser = serialize_quality_profile(profile)
        des = deserialize_quality_profile(ser)

        self.assertEqual(des.semantic_equivalence_verified, profile.semantic_equivalence_verified)
        self.assertEqual(des.classification, profile.classification)
        self.assertEqual(des.resource_profile.total_qubits, profile.resource_profile.total_qubits)
        self.assertEqual(des.resource_profile.total_gate_count, profile.resource_profile.total_gate_count)

        # Re-serialize verify byte-identical string output
        ser2 = serialize_quality_profile(des)
        self.assertEqual(ser, ser2)

    def test_02_comparison_result_roundtrip(self) -> None:
        """Verifies deserialize(serialize(ComparisonResult)) == ComparisonResult."""
        p1 = ResourceQualityEvaluator.evaluate_quality_profile(self.circuit, context=self.ctx)
        p2 = ResourceQualityEvaluator.evaluate_quality_profile(self.circuit, context=self.ctx)

        comp = ParetoTradeOffAnalyzer.compare_candidates("C1", p1, "C2", p2)
        ser = serialize_comparison_result(comp)
        des = deserialize_comparison_result(ser)

        self.assertEqual(des.candidate_a_id, comp.candidate_a_id)
        self.assertEqual(des.candidate_b_id, comp.candidate_b_id)
        self.assertEqual(des.pareto_status, comp.pareto_status)
        self.assertEqual(des.comparison_hash, comp.comparison_hash)

        ser2 = serialize_comparison_result(des)
        self.assertEqual(ser, ser2)

    def test_03_quality_analysis_report_roundtrip(self) -> None:
        """Verifies deserialize(serialize(QualityAnalysisReport)) == QualityAnalysisReport."""
        report = analyze_stage9_compilation_quality(self.circuit, self.ctx, model=self.model)
        ser = serialize_quality_analysis_report(report)
        des = deserialize_quality_analysis_report(ser)

        self.assertEqual(des.algorithm_id, report.algorithm_id)
        self.assertEqual(des.classification, report.classification)
        self.assertEqual(des.report_hash, report.report_hash)

        ser2 = serialize_quality_analysis_report(des)
        self.assertEqual(ser, ser2)


if __name__ == "__main__":
    unittest.main()
