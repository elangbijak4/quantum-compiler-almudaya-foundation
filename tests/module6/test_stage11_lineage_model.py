"""
Module 6 Stage 11 Test Suite — Lineage Model & Evaluator Tests.
"""

import unittest
from src.module6.evolution.state import create_initial_evolutionary_state
from src.module6.resolution import Stage7CompilerResolver
from src.module6.families.generators import AlgorithmFamilyGenerator
from src.module6.mapping.mapper import CompilerMapper
from src.module6.analysis.stage9 import analyze_stage9_compilation_quality
from src.module6.analysis.stage10 import analyze_stage10_governance
from src.module6.analysis.stage11 import analyze_stage11_lineage
from src.module6.lineage import (
    HistoricalLineageRecord,
    LifecycleEvent,
    LineageTraceReport,
)


class TestStage11LineageModel(unittest.TestCase):
    """Tests verifying HistoricalLineageRecord creation and lineage trace extraction from Stage 10 audit evidence."""

    def setUp(self) -> None:
        self.ge0 = create_initial_evolutionary_state()
        family = AlgorithmFamilyGenerator.generate_family("identity_family", size=1)
        self.model = list(family.models)[0]
        self.program = list(family.programs)[0]
        self.ctx = Stage7CompilerResolver.resolve_effective_context(self.ge0)
        self.circuit = CompilerMapper.map_classical_model(self.model, self.program)

    def test_01_lineage_trace_generation(self) -> None:
        """Verifies analyze_stage11_lineage constructs valid LineageTraceReport from Stage 10 audit report."""
        q_report = analyze_stage9_compilation_quality(self.circuit, self.ctx, model=self.model)
        audit_report = analyze_stage10_governance(self.circuit, self.ctx, quality_report=q_report)
        trace_report = analyze_stage11_lineage(audit_report)

        self.assertIsNotNone(trace_report.trace_id)
        self.assertEqual(trace_report.algorithm_id, audit_report.algorithm_id)
        self.assertEqual(len(trace_report.records), 1)
        self.assertEqual(len(trace_report.events), 1)
        self.assertTrue(trace_report.is_valid_chain)

    def test_02_historical_record_fields(self) -> None:
        """Verifies HistoricalLineageRecord accurately binds upstream audit and certificate identities."""
        q_report = analyze_stage9_compilation_quality(self.circuit, self.ctx, model=self.model)
        audit_report = analyze_stage10_governance(self.circuit, self.ctx, quality_report=q_report)
        trace_report = analyze_stage11_lineage(audit_report)

        rec = trace_report.records[0]
        self.assertEqual(rec.audit_id, audit_report.audit_id)
        self.assertEqual(rec.certificate_id, audit_report.certificate.certificate_id)
        self.assertIsNotNone(rec.record_hash)


if __name__ == "__main__":
    unittest.main()
