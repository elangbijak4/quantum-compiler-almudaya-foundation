"""
Module 6 Stage 11 Test Suite — GAP-3 Sequence & Cross-Reference Integrity Tests.
"""

import unittest
from src.module6.lineage import (
    HistoricalLineageRecord,
    LifecycleEvent,
    HistoricalLineageRepository,
)


class TestStage11Gap3Integrity(unittest.TestCase):
    """Tests verifying GAP-3: sequence origin/gap/duplicate/decreasing & cross-reference integrity."""

    def test_01_valid_sequence_1_2_3(self) -> None:
        """Verifies valid sequence 1, 2, 3 passes integrity check."""
        repo = HistoricalLineageRepository()
        for seq in [1, 2, 3]:
            ev = LifecycleEvent(
                event_id=f"EVT_{seq}", algorithm_id="ALG_SEQ", event_type="AUDIT_VERIFIED",
                previous_state="ANALYZED", new_state="VERIFIED", source_identity="ALG_SEQ",
                evidence_identity=f"CERT_{seq}", sequence=seq
            )
            rec = HistoricalLineageRecord(
                record_id=f"REC_{seq}", algorithm_id="ALG_SEQ", audit_id=f"AUD_{seq}",
                certificate_id=f"CERT_{seq}", circuit_id="C1", provenance_chain_hash="PROV_1",
                lifecycle_event_id=f"EVT_{seq}", event_type="AUDIT_VERIFIED", event_sequence=seq,
                timestamp_identity="TS1"
            )
            repo.append_event(ev)
            repo.append_record(rec)

        integ = repo.verify_integrity()
        self.assertTrue(integ.is_integrity_valid)
        self.assertEqual(len(integ.violations), 0)

    def test_02_non_origin_sequence_starts_at_2(self) -> None:
        """Verifies sequence starting at 2 (not 1) raises NON_ORIGIN_SEQUENCE violation."""
        repo = HistoricalLineageRepository()
        ev = LifecycleEvent(
            event_id="EVT_2", algorithm_id="ALG_NO_ORIGIN", event_type="AUDIT_VERIFIED",
            previous_state="ANALYZED", new_state="VERIFIED", source_identity="ALG_NO_ORIGIN",
            evidence_identity="CERT_2", sequence=2
        )
        rec = HistoricalLineageRecord(
            record_id="REC_2", algorithm_id="ALG_NO_ORIGIN", audit_id="AUD_2",
            certificate_id="CERT_2", circuit_id="C1", provenance_chain_hash="PROV_1",
            lifecycle_event_id="EVT_2", event_type="AUDIT_VERIFIED", event_sequence=2,
            timestamp_identity="TS1"
        )
        repo.append_event(ev)
        repo.append_record(rec)
        integ = repo.verify_integrity()
        self.assertFalse(integ.is_integrity_valid)
        self.assertTrue(any("NON_ORIGIN_SEQUENCE" in v for v in integ.violations))

    def test_03_duplicate_sequence_1_2_2(self) -> None:
        """Verifies sequence 1, 2, 2 raises DUPLICATE_SEQUENCE violation."""
        repo = HistoricalLineageRepository()
        for seq, rec_id in [(1, "REC_1"), (2, "REC_2A"), (2, "REC_2B")]:
            ev = LifecycleEvent(
                event_id=f"EVT_{rec_id}", algorithm_id="ALG_DUP", event_type="AUDIT_VERIFIED",
                previous_state="ANALYZED", new_state="VERIFIED", source_identity="ALG_DUP",
                evidence_identity="CERT_1", sequence=seq
            )
            rec = HistoricalLineageRecord(
                record_id=rec_id, algorithm_id="ALG_DUP", audit_id="AUD_1",
                certificate_id="CERT_1", circuit_id="C1", provenance_chain_hash="PROV_1",
                lifecycle_event_id=f"EVT_{rec_id}", event_type="AUDIT_VERIFIED", event_sequence=seq,
                timestamp_identity="TS1"
            )
            repo.append_event(ev)
            repo.append_record(rec)

        integ = repo.verify_integrity()
        self.assertFalse(integ.is_integrity_valid)
        self.assertTrue(any("DUPLICATE_SEQUENCE" in v for v in integ.violations))

    def test_04_decreasing_sequence_1_3_2(self) -> None:
        """Verifies sequence 1, 3, 2 raises DECREASING_SEQUENCE violation."""
        repo = HistoricalLineageRepository()
        for seq in [1, 3, 2]:
            ev = LifecycleEvent(
                event_id=f"EVT_{seq}", algorithm_id="ALG_DEC", event_type="AUDIT_VERIFIED",
                previous_state="ANALYZED", new_state="VERIFIED", source_identity="ALG_DEC",
                evidence_identity=f"CERT_{seq}", sequence=seq
            )
            rec = HistoricalLineageRecord(
                record_id=f"REC_{seq}", algorithm_id="ALG_DEC", audit_id=f"AUD_{seq}",
                certificate_id=f"CERT_{seq}", circuit_id="C1", provenance_chain_hash="PROV_1",
                lifecycle_event_id=f"EVT_{seq}", event_type="AUDIT_VERIFIED", event_sequence=seq,
                timestamp_identity="TS1"
            )
            repo.append_event(ev)
            repo.append_record(rec)

        integ = repo.verify_integrity()
        self.assertFalse(integ.is_integrity_valid)
        self.assertTrue(any("Sequence Continuity Gap" in v or "DECREASING_SEQUENCE" in v for v in integ.violations))

    def test_05_broken_lifecycle_event_reference(self) -> None:
        """Verifies record referencing non-existent lifecycle event raises BROKEN_REFERENCE."""
        repo = HistoricalLineageRepository()
        rec = HistoricalLineageRecord(
            record_id="REC_1", algorithm_id="ALG_BROKEN", audit_id="AUD_1",
            certificate_id="CERT_1", circuit_id="C1", provenance_chain_hash="PROV_1",
            lifecycle_event_id="EVT_NONEXISTENT", event_type="AUDIT_VERIFIED", event_sequence=1,
            timestamp_identity="TS1"
        )
        repo.append_record(rec)
        integ = repo.verify_integrity()
        self.assertFalse(integ.is_integrity_valid)
        self.assertIn("BROKEN_REFERENCE", integ.violations[0])

    def test_06_algorithm_id_mismatch_cross_reference(self) -> None:
        """Verifies algorithm_id mismatch between record and linked event raises ALGORITHM_ID_MISMATCH."""
        repo = HistoricalLineageRepository()
        ev = LifecycleEvent(
            event_id="EVT_1", algorithm_id="ALG_A", event_type="AUDIT_VERIFIED",
            previous_state="ANALYZED", new_state="VERIFIED", source_identity="ALG_A",
            evidence_identity="CERT_1", sequence=1
        )
        rec = HistoricalLineageRecord(
            record_id="REC_1", algorithm_id="ALG_B", audit_id="AUD_1",
            certificate_id="CERT_1", circuit_id="C1", provenance_chain_hash="PROV_1",
            lifecycle_event_id="EVT_1", event_type="AUDIT_VERIFIED", event_sequence=1,
            timestamp_identity="TS1"
        )
        repo.append_event(ev)
        repo.append_record(rec)
        integ = repo.verify_integrity()
        self.assertFalse(integ.is_integrity_valid)
        self.assertIn("ALGORITHM_ID_MISMATCH", integ.violations[0])


if __name__ == "__main__":
    unittest.main()
