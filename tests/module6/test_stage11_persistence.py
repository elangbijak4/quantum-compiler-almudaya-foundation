"""
Module 6 Stage 11 Test Suite — True Local File Persistence & Integrity Hardening Tests.
"""

import unittest
import tempfile
import os
import json
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


class TestStage11Persistence(unittest.TestCase):
    """Tests verifying local file persistence, restart equivalence (snapshot_A == snapshot_B), corrupted file detection, and 64-char SHA-256 digests."""

    def setUp(self) -> None:
        self.ge0 = create_initial_evolutionary_state()
        family = AlgorithmFamilyGenerator.generate_family("identity_family", size=1)
        self.model = list(family.models)[0]
        self.program = list(family.programs)[0]
        self.ctx = Stage7CompilerResolver.resolve_effective_context(self.ge0)
        self.circuit = CompilerMapper.map_classical_model(self.model, self.program)
        self.temp_dir = tempfile.mkdtemp()
        self.storage_path = os.path.join(self.temp_dir, "repo_storage.json")

    def tearDown(self) -> None:
        if os.path.exists(self.storage_path):
            os.remove(self.storage_path)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)

    def test_01_full_64_char_sha256_digests(self) -> None:
        """Verifies record_hash, deterministic_hash, and snapshot_hash are full 64-character SHA-256 hex digests."""
        q_report = analyze_stage9_compilation_quality(self.circuit, self.ctx, model=self.model)
        audit_report = analyze_stage10_governance(self.circuit, self.ctx, quality_report=q_report)
        trace_report = analyze_stage11_lineage(audit_report)

        rec = trace_report.records[0]
        ev = trace_report.events[0]

        self.assertEqual(len(rec.record_hash), 64, f"record_hash must be 64 chars, got {len(rec.record_hash)}")
        self.assertEqual(len(rec.provenance_chain_hash), 64, f"provenance_chain_hash must be 64 chars, got {len(rec.provenance_chain_hash)}")
        self.assertEqual(len(ev.deterministic_hash), 64, f"deterministic_hash must be 64 chars, got {len(ev.deterministic_hash)}")
        self.assertEqual(len(trace_report.report_hash), 64, f"report_hash must be 64 chars, got {len(trace_report.report_hash)}")

    def test_02_provenance_inclusive_event_hashing(self) -> None:
        """Verifies LifecycleEvent deterministic_hash changes if provenance dictionary is altered."""
        ev1 = LifecycleEvent(
            event_id="EVT_01",
            algorithm_id="ALG_01",
            event_type="AUDIT_CERTIFIED",
            previous_state="ANALYZED",
            new_state="CERTIFIED",
            source_identity="ALG_01",
            evidence_identity="CERT_01",
            provenance={"audit_hash": "HASH_A"},
            sequence=1,
        )
        ev2 = LifecycleEvent(
            event_id="EVT_01",
            algorithm_id="ALG_01",
            event_type="AUDIT_CERTIFIED",
            previous_state="ANALYZED",
            new_state="CERTIFIED",
            source_identity="ALG_01",
            evidence_identity="CERT_01",
            provenance={"audit_hash": "HASH_B"},
            sequence=1,
        )
        self.assertNotEqual(ev1.deterministic_hash, ev2.deterministic_hash)

    def test_03_local_file_persistence_save_load_reload(self) -> None:
        """Verifies saving repository to local JSON file and reloading yields snapshot_A == snapshot_B."""
        repo_a = HistoricalLineageRepository(storage_file_path=self.storage_path)
        q_report = analyze_stage9_compilation_quality(self.circuit, self.ctx, model=self.model)
        audit_report = analyze_stage10_governance(self.circuit, self.ctx, quality_report=q_report)
        analyze_stage11_lineage(audit_report, repository=repo_a)

        snap_a = repo_a.get_snapshot_identity()
        self.assertEqual(len(snap_a), 64)
        repo_a.save()

        repo_b = HistoricalLineageRepository.load(self.storage_path)
        snap_b = repo_b.get_snapshot_identity()

        self.assertEqual(snap_a, snap_b)
        self.assertEqual(len(repo_b._records), len(repo_a._records))
        self.assertEqual(len(repo_b._events), len(repo_a._events))

        repo_reloaded = repo_a.reload()
        self.assertEqual(repo_reloaded.get_snapshot_identity(), snap_a)

    def test_04_corrupted_storage_detection(self) -> None:
        """Verifies tampering with persisted file content causes load() to raise REPOSITORY_INTEGRITY_FAILURE."""
        repo = HistoricalLineageRepository(storage_file_path=self.storage_path)
        q_report = analyze_stage9_compilation_quality(self.circuit, self.ctx, model=self.model)
        audit_report = analyze_stage10_governance(self.circuit, self.ctx, quality_report=q_report)
        analyze_stage11_lineage(audit_report, repository=repo)
        repo.save()

        with open(self.storage_path, "r", encoding="utf-8") as f:
            data = json.loads(f.read())
        data["records"][0]["record_hash"] = "0000000000000000000000000000000000000000000000000000000000000000"
        with open(self.storage_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(data, indent=2))

        with self.assertRaises(ValueError) as ctx:
            HistoricalLineageRepository.load(self.storage_path)
        self.assertIn("REPOSITORY_INTEGRITY_FAILURE", str(ctx.exception))

    def test_05_sequence_continuity_validation(self) -> None:
        """Verifies trace_lineage and verify_integrity detect sequence gaps (e.g. sequence 1 then sequence 3)."""
        repo = HistoricalLineageRepository()
        ev1 = LifecycleEvent(
            event_id="EVT_1", algorithm_id="ALG_GAP", event_type="AUDIT_VERIFIED",
            previous_state="ANALYZED", new_state="VERIFIED", source_identity="ALG_GAP",
            evidence_identity="CERT_1", sequence=1
        )
        ev3 = LifecycleEvent(
            event_id="EVT_3", algorithm_id="ALG_GAP", event_type="AUDIT_VERIFIED",
            previous_state="ANALYZED", new_state="VERIFIED", source_identity="ALG_GAP",
            evidence_identity="CERT_3", sequence=3
        )
        rec1 = HistoricalLineageRecord(
            record_id="REC_1", algorithm_id="ALG_GAP", audit_id="AUD_1", certificate_id="CERT_1",
            circuit_id="C1", provenance_chain_hash="PROV_1", lifecycle_event_id="EVT_1",
            event_type="AUDIT_VERIFIED", event_sequence=1, timestamp_identity="TS1"
        )
        rec3 = HistoricalLineageRecord(
            record_id="REC_3", algorithm_id="ALG_GAP", audit_id="AUD_3", certificate_id="CERT_3",
            circuit_id="C3", provenance_chain_hash="PROV_3", lifecycle_event_id="EVT_3",
            event_type="AUDIT_VERIFIED", event_sequence=3, timestamp_identity="TS3"
        )
        repo.append_event(ev1)
        repo.append_event(ev3)
        repo.append_record(rec1)
        repo.append_record(rec3)

        trace = repo.trace_lineage("ALG_GAP")
        self.assertFalse(trace.is_valid_chain)

        integ = repo.verify_integrity()
        self.assertFalse(integ.is_integrity_valid)
        self.assertTrue(any("Sequence Continuity Gap" in v or "SEQUENCE_GAP" in v for v in integ.violations))


if __name__ == "__main__":
    unittest.main()
