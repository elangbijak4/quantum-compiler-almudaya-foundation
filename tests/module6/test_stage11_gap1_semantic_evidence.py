"""
Module 6 Stage 11 Test Suite — GAP-1 Semantic Evidence Integrity Tests.
"""

import unittest
from src.module6.evolution.state import create_initial_evolutionary_state
from src.module6.resolution import Stage7CompilerResolver
from src.module6.families.generators import AlgorithmFamilyGenerator
from src.module6.mapping.mapper import CompilerMapper
from src.module6.analysis.stage9 import analyze_stage9_compilation_quality
from src.module6.analysis.stage10 import analyze_stage10_governance
from src.module6.analysis.stage11 import analyze_stage11_lineage
from src.module6.lineage import HistoricalLineageEvaluator


class TestStage11Gap1SemanticEvidence(unittest.TestCase):
    """Tests verifying GAP-1: zero synthetic semantic evidence ID generation."""

    def test_01_no_synthetic_semantic_evidence_id(self) -> None:
        """Verifies semantic_evidence_id is None when genuine Stage 4 evidence is absent."""
        ge0 = create_initial_evolutionary_state()
        family = AlgorithmFamilyGenerator.generate_family("identity_family", size=1)
        model = list(family.models)[0]
        program = list(family.programs)[0]
        ctx = Stage7CompilerResolver.resolve_effective_context(ge0)
        circuit = CompilerMapper.map_classical_model(model, program)

        q_report = analyze_stage9_compilation_quality(circuit, ctx, model=model)
        audit_report = analyze_stage10_governance(circuit, ctx, quality_report=q_report)

        # In standard compilation lineage without Stage 4 evidence passed in prov:
        trace_report = analyze_stage11_lineage(audit_report)
        rec = trace_report.records[0]

        # Verify semantic_evidence_id is explicitly None (not STAGE4_VERIFIED_True or similar)
        self.assertIsNone(rec.semantic_evidence_id, "semantic_evidence_id must be None when genuine Stage 4 evidence is absent")

    def test_02_genuine_semantic_evidence_id_preserved(self) -> None:
        """Verifies exact genuine Stage 4 evidence identity is preserved when present."""
        ge0 = create_initial_evolutionary_state()
        family = AlgorithmFamilyGenerator.generate_family("identity_family", size=1)
        model = list(family.models)[0]
        program = list(family.programs)[0]
        ctx = Stage7CompilerResolver.resolve_effective_context(ge0)
        circuit = CompilerMapper.map_classical_model(model, program)

        q_report = analyze_stage9_compilation_quality(circuit, ctx, model=model)
        audit_report = analyze_stage10_governance(circuit, ctx, quality_report=q_report)

        # Inject genuine Stage 4 evidence ID into provenance
        audit_report.provenance["semantic_evidence_id"] = "GENUINE_STAGE4_EVIDENCE_999"

        trace_report = HistoricalLineageEvaluator.trace_compilation_lineage(audit_report)
        rec = trace_report.records[0]

        self.assertEqual(rec.semantic_evidence_id, "GENUINE_STAGE4_EVIDENCE_999")


if __name__ == "__main__":
    unittest.main()
