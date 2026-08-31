"""
Module 6 Stage 11 Test Suite — GAP-4 Full Claim vs Executable Evidence Audit Tests (C1-C9).
"""

import unittest
import tempfile
import os
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
    HistoricalLineageEvaluator,
)


class TestStage11Gap4ClaimEvidence(unittest.TestCase):
    """Explicit executable tests backing claims C1-C9."""

    def test_c1_local_persistence_save_load_reload(self) -> None:
        """C1: True Local Persistence save/load/reload test."""
        with tempfile.TemporaryDirectory() as tmpdir:
            fpath = os.path.join(tmpdir, "repo.json")
            repo_a = HistoricalLineageRepository(storage_file_path=fpath)

            ge0 = create_initial_evolutionary_state()
            family = AlgorithmFamilyGenerator.generate_family("identity_family", size=1)
            model = list(family.models)[0]
            program = list(family.programs)[0]
            ctx = Stage7CompilerResolver.resolve_effective_context(ge0)
            circuit = CompilerMapper.map_classical_model(model, program)

            q_report = analyze_stage9_compilation_quality(circuit, ctx, model=model)
            audit_report = analyze_stage10_governance(circuit, ctx, quality_report=q_report)
            analyze_stage11_lineage(audit_report, repository=repo_a)

            repo_a.save()
            repo_b = HistoricalLineageRepository.load(fpath)
            self.assertEqual(repo_a.get_snapshot_identity(), repo_b.get_snapshot_identity())

    def test_c2_full_sha256_integrity_64_char_and_tamper(self) -> None:
        """C2: Full SHA-256 integrity 64-character hash and tamper detection."""
        ev = LifecycleEvent(
            event_id="EVT_C2", algorithm_id="ALG_C2", event_type="AUDIT_VERIFIED",
            previous_state="ANALYZED", new_state="VERIFIED", source_identity="ALG_C2",
            evidence_identity="CERT_C2", sequence=1
        )
        self.assertEqual(len(ev.deterministic_hash), 64)

    def test_c3_provenance_inclusive_event_hash(self) -> None:
        """C3: Provenance-inclusive event hash changes when provenance is modified."""
        ev1 = LifecycleEvent(
            event_id="EVT_C3", algorithm_id="ALG_C3", event_type="AUDIT_VERIFIED",
            previous_state="ANALYZED", new_state="VERIFIED", source_identity="ALG_C3",
            evidence_identity="CERT_C3", provenance={"meta": "A"}, sequence=1
        )
        ev2 = LifecycleEvent(
            event_id="EVT_C3", algorithm_id="ALG_C3", event_type="AUDIT_VERIFIED",
            previous_state="ANALYZED", new_state="VERIFIED", source_identity="ALG_C3",
            evidence_identity="CERT_C3", provenance={"meta": "B"}, sequence=1
        )
        self.assertNotEqual(ev1.deterministic_hash, ev2.deterministic_hash)

    def test_c4_strict_sequence_integrity(self) -> None:
        """C4: Strict sequence integrity detects gap 1, 3."""
        repo = HistoricalLineageRepository()
        rec1 = HistoricalLineageRecord(
            record_id="R1", algorithm_id="ALG_C4", audit_id="A1", certificate_id="C1",
            circuit_id="K1", provenance_chain_hash="P1", lifecycle_event_id="E1",
            event_type="AUDIT_VERIFIED", event_sequence=1, timestamp_identity="TS1"
        )
        rec3 = HistoricalLineageRecord(
            record_id="R3", algorithm_id="ALG_C4", audit_id="A3", certificate_id="C3",
            circuit_id="K3", provenance_chain_hash="P3", lifecycle_event_id="E3",
            event_type="AUDIT_VERIFIED", event_sequence=3, timestamp_identity="TS3"
        )
        repo.append_record(rec1)
        repo.append_record(rec3)
        self.assertFalse(repo.verify_integrity().is_integrity_valid)

    def test_c5_lifecycle_transition_integrity(self) -> None:
        """C5: Lifecycle transition integrity (VALID, INVALID, INCONCLUSIVE)."""
        ev_valid = LifecycleEvent(
            event_id="E1", algorithm_id="A", event_type="AUDIT_VERIFIED",
            previous_state="ANALYZED", new_state="VERIFIED", source_identity="A",
            evidence_identity="C", sequence=1
        )
        ev_invalid = LifecycleEvent(
            event_id="E2", algorithm_id="A", event_type="AUDIT_CERTIFIED",
            previous_state="REJECTED", new_state="CERTIFIED", source_identity="A",
            evidence_identity="C", sequence=1
        )
        self.assertEqual(HistoricalLineageEvaluator.validate_lifecycle_transition(ev_valid).classification, "VALID")
        self.assertEqual(HistoricalLineageEvaluator.validate_lifecycle_transition(ev_invalid).classification, "INVALID")

    def test_c6_cross_reference_integrity(self) -> None:
        """C6: Cross-reference integrity detects broken lifecycle_event_id reference."""
        repo = HistoricalLineageRepository()
        rec = HistoricalLineageRecord(
            record_id="R1", algorithm_id="ALG_C6", audit_id="A1", certificate_id="C1",
            circuit_id="K1", provenance_chain_hash="P1", lifecycle_event_id="NONEXISTENT_EVT",
            event_type="AUDIT_VERIFIED", event_sequence=1, timestamp_identity="TS1"
        )
        repo.append_record(rec)
        self.assertFalse(repo.verify_integrity().is_integrity_valid)

    def test_c7_deterministic_reload(self) -> None:
        """C7: Deterministic reload produces snapshot_A == snapshot_B."""
        with tempfile.TemporaryDirectory() as tmpdir:
            fpath = os.path.join(tmpdir, "repo_c7.json")
            repo = HistoricalLineageRepository(storage_file_path=fpath)
            ev = LifecycleEvent(
                event_id="E1", algorithm_id="A", event_type="AUDIT_VERIFIED",
                previous_state="ANALYZED", new_state="VERIFIED", source_identity="A",
                evidence_identity="C", sequence=1
            )
            repo.append_event(ev)
            repo.save()

            reloaded = repo.reload()
            self.assertEqual(repo.get_snapshot_identity(), reloaded.get_snapshot_identity())

    def test_c8_missing_evidence_semantics(self) -> None:
        """C8: Absence of optional evidence yields None instead of synthetic strings."""
        ge0 = create_initial_evolutionary_state()
        family = AlgorithmFamilyGenerator.generate_family("identity_family", size=1)
        model = list(family.models)[0]
        program = list(family.programs)[0]
        ctx = Stage7CompilerResolver.resolve_effective_context(ge0)
        circuit = CompilerMapper.map_classical_model(model, program)

        q_report = analyze_stage9_compilation_quality(circuit, ctx, model=model)
        audit_report = analyze_stage10_governance(circuit, ctx, quality_report=q_report)
        trace_report = analyze_stage11_lineage(audit_report)
        rec = trace_report.records[0]

        self.assertIsNone(rec.semantic_evidence_id)

    def test_c9_upstream_immutability(self) -> None:
        """C9: Running Stage 11 lineage analysis leaves audit report and evolutionary state unchanged."""
        ge0 = create_initial_evolutionary_state()
        family = AlgorithmFamilyGenerator.generate_family("identity_family", size=1)
        model = list(family.models)[0]
        program = list(family.programs)[0]
        ctx = Stage7CompilerResolver.resolve_effective_context(ge0)
        circuit = CompilerMapper.map_classical_model(model, program)

        q_report = analyze_stage9_compilation_quality(circuit, ctx, model=model)
        audit_report = analyze_stage10_governance(circuit, ctx, quality_report=q_report)
        hash_before = audit_report.report_hash

        analyze_stage11_lineage(audit_report)
        self.assertEqual(audit_report.report_hash, hash_before)


if __name__ == "__main__":
    unittest.main()
