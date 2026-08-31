"""
Module 6 Stage 11 Test Suite — Persistent Append-Only Repository Tests.
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
    HistoricalLineageRepository,
    HistoricalLineageRecord,
    LifecycleEvent,
)


class TestStage11Repository(unittest.TestCase):
    """Tests verifying append-only semantics, query execution, and integrity audit in HistoricalLineageRepository."""

    def setUp(self) -> None:
        self.ge0 = create_initial_evolutionary_state()
        family = AlgorithmFamilyGenerator.generate_family("identity_family", size=1)
        self.model = list(family.models)[0]
        self.program = list(family.programs)[0]
        self.ctx = Stage7CompilerResolver.resolve_effective_context(self.ge0)
        self.circuit = CompilerMapper.map_classical_model(self.model, self.program)
        self.repo = HistoricalLineageRepository()

    def test_01_append_and_query(self) -> None:
        """Verifies appending lineage records and querying by algorithm_id."""
        q_report = analyze_stage9_compilation_quality(self.circuit, self.ctx, model=self.model)
        audit_report = analyze_stage10_governance(self.circuit, self.ctx, quality_report=q_report)
        
        analyze_stage11_lineage(audit_report, repository=self.repo)

        query_res = self.repo.query(algorithm_id=audit_report.algorithm_id)
        self.assertEqual(query_res.total_matches, 2) # 1 record + 1 event
        self.assertEqual(len(query_res.matching_records), 1)
        self.assertEqual(len(query_res.matching_events), 1)

    def test_02_append_only_violation(self) -> None:
        """Verifies attempting to overwrite an existing record or event raises ValueError."""
        q_report = analyze_stage9_compilation_quality(self.circuit, self.ctx, model=self.model)
        audit_report = analyze_stage10_governance(self.circuit, self.ctx, quality_report=q_report)
        trace_report = analyze_stage11_lineage(audit_report, repository=self.repo)

        rec = trace_report.records[0]
        with self.assertRaises(ValueError):
            self.repo.append_record(rec) # Duplicate append attempt!

    def test_03_repository_integrity_audit(self) -> None:
        """Verifies verify_integrity confirms repository snapshot validity and zero violations."""
        q_report = analyze_stage9_compilation_quality(self.circuit, self.ctx, model=self.model)
        audit_report = analyze_stage10_governance(self.circuit, self.ctx, quality_report=q_report)
        analyze_stage11_lineage(audit_report, repository=self.repo)

        integ = self.repo.verify_integrity()
        self.assertTrue(integ.is_integrity_valid)
        self.assertEqual(len(integ.violations), 0)
        self.assertIsNotNone(integ.snapshot_hash)


if __name__ == "__main__":
    unittest.main()
