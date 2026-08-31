"""
Module 6 Stage 11 Test Suite — Canonical Serialization Tests.
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
    serialize_historical_lineage_record,
    deserialize_historical_lineage_record,
    serialize_lifecycle_event,
    deserialize_lifecycle_event,
    serialize_lineage_trace_report,
    deserialize_lineage_trace_report,
)


class TestStage11Serialization(unittest.TestCase):
    """Tests verifying canonical JSON serialization and roundtrip equality deserialize(serialize(X)) == X."""

    def setUp(self) -> None:
        self.ge0 = create_initial_evolutionary_state()
        family = AlgorithmFamilyGenerator.generate_family("identity_family", size=1)
        self.model = list(family.models)[0]
        self.program = list(family.programs)[0]
        self.ctx = Stage7CompilerResolver.resolve_effective_context(self.ge0)
        self.circuit = CompilerMapper.map_classical_model(self.model, self.program)

    def test_01_lineage_record_roundtrip(self) -> None:
        """Verifies deserialize(serialize(HistoricalLineageRecord)) == HistoricalLineageRecord."""
        q_report = analyze_stage9_compilation_quality(self.circuit, self.ctx, model=self.model)
        audit_report = analyze_stage10_governance(self.circuit, self.ctx, quality_report=q_report)
        trace_report = analyze_stage11_lineage(audit_report)

        rec = trace_report.records[0]
        ser = serialize_historical_lineage_record(rec)
        des = deserialize_historical_lineage_record(ser)

        self.assertEqual(des.record_id, rec.record_id)
        self.assertEqual(des.audit_id, rec.audit_id)
        self.assertEqual(des.record_hash, rec.record_hash)

        ser2 = serialize_historical_lineage_record(des)
        self.assertEqual(ser, ser2)

    def test_02_lineage_trace_report_roundtrip(self) -> None:
        """Verifies deserialize(serialize(LineageTraceReport)) == LineageTraceReport."""
        q_report = analyze_stage9_compilation_quality(self.circuit, self.ctx, model=self.model)
        audit_report = analyze_stage10_governance(self.circuit, self.ctx, quality_report=q_report)
        trace_report = analyze_stage11_lineage(audit_report)

        ser = serialize_lineage_trace_report(trace_report)
        des = deserialize_lineage_trace_report(ser)

        self.assertEqual(des.trace_id, trace_report.trace_id)
        self.assertEqual(des.report_hash, trace_report.report_hash)
        self.assertEqual(len(des.records), len(trace_report.records))

        ser2 = serialize_lineage_trace_report(des)
        self.assertEqual(ser, ser2)


if __name__ == "__main__":
    unittest.main()
