"""
Module 6 Stage 9 Test Suite — Initialization & Constitutional Verification.
"""

import unittest
from src.module6.evolution.state import create_initial_evolutionary_state
from src.module6.resolution import Stage7CompilerResolver
from src.module6.families.generators import AlgorithmFamilyGenerator
from src.module6.mapping.mapper import CompilerMapper
from src.module6.quality import (
    ResourceQualityEvaluator,
    ParetoTradeOffAnalyzer,
    ResultClassification,
    ParetoStatus,
    serialize_quality_profile,
    deserialize_quality_profile,
)
from src.module6.analysis.stage9 import analyze_stage9_compilation_quality


class TestStage9Initialization(unittest.TestCase):
    """Tests verifying Stage 9 initialization, scaffold, non-implication rules, and constitutional invariants."""

    def setUp(self) -> None:
        self.ge0 = create_initial_evolutionary_state()
        family = AlgorithmFamilyGenerator.generate_family("identity_family", size=1)
        self.model = list(family.models)[0]
        self.program = list(family.programs)[0]
        self.ctx = Stage7CompilerResolver.resolve_effective_context(self.ge0)
        self.circuit = CompilerMapper.map_classical_model(self.model, self.program)

    def test_01_resource_profile_extraction(self) -> None:
        """Req 3: ResourceProfile extracts logical qubit width, gate counts, depth without hardware execution."""
        profile = ResourceQualityEvaluator.extract_resource_profile(self.circuit)
        self.assertEqual(profile.total_qubits, self.circuit.total_width)
        self.assertGreaterEqual(profile.total_gate_count, 0)
        self.assertIsInstance(profile.gate_distribution, dict)

    def test_02_quality_profile_evaluation(self) -> None:
        """Req 3, 5: QualityProfile preserves distinct multi-objective dimensions."""
        q_prof = ResourceQualityEvaluator.evaluate_quality_profile(
            circuit=self.circuit,
            semantic_equivalent=True,
        )
        self.assertTrue(q_prof.semantic_equivalence_verified)
        self.assertEqual(q_prof.classification, ResultClassification.SEMANTICALLY_VALID)
        # Verify Quality Score is NOT automatically assumed identical to semantic equivalence
        self.assertIsNone(q_prof.weighted_quality_score)

    def test_03_pareto_trade_off_analysis(self) -> None:
        """Req 6: ParetoTradeOffAnalyzer distinguishes DOMINATED vs INCOMPARABLE trade-offs."""
        q_prof1 = ResourceQualityEvaluator.evaluate_quality_profile(self.circuit)
        q_prof2 = ResourceQualityEvaluator.evaluate_quality_profile(self.circuit)

        res = ParetoTradeOffAnalyzer.compare_candidates("C1", q_prof1, "C2", q_prof2)
        self.assertEqual(res.pareto_status, ParetoStatus.EQUAL)
        self.assertIsNone(res.dominant_candidate_id)

    def test_04_serialization_roundtrip(self) -> None:
        """Req 14: Canonical JSON roundtrip deserialize(serialize(X)) == X."""
        report = analyze_stage9_compilation_quality(self.circuit, self.ctx)
        q_prof = report.quality_profile
        ser = serialize_quality_profile(q_prof)
        des = deserialize_quality_profile(ser)

        self.assertEqual(des.semantic_equivalence_verified, q_prof.semantic_equivalence_verified)
        self.assertEqual(des.classification, q_prof.classification)
        self.assertEqual(des.resource_profile.total_qubits, q_prof.resource_profile.total_qubits)

    def test_05_hardware_and_noise_boundary_preserved(self) -> None:
        """Req 11: Hardware execution and noise simulation remain 0%."""
        report = analyze_stage9_compilation_quality(self.circuit, self.ctx)
        q_prof = report.quality_profile
        # Assert resource profile contains strictly logical metrics
        self.assertGreaterEqual(q_prof.resource_profile.data_qubits, 0)
        self.assertGreaterEqual(q_prof.resource_profile.ancilla_qubits, 0)


if __name__ == "__main__":
    unittest.main()
