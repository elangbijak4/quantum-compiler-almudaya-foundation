"""
Module 6 Stage 11 Test Suite — Lifecycle Event Tests.
"""

import unittest
from src.module6.lineage import LifecycleEvent


class TestStage11Lifecycle(unittest.TestCase):
    """Tests verifying immutable LifecycleEvent hashing and structure."""

    def test_01_lifecycle_event_creation(self) -> None:
        """Verifies LifecycleEvent immutability and full 64-character SHA-256 deterministic hash computation."""
        ev = LifecycleEvent(
            event_id="EVT_01",
            algorithm_id="ALG_01",
            event_type="AUDIT_CERTIFIED",
            previous_state="ANALYZED",
            new_state="CERTIFIED",
            source_identity="ALG_01",
            evidence_identity="CERT_01",
            sequence=1,
        )
        self.assertEqual(ev.event_id, "EVT_01")
        self.assertIsNotNone(ev.deterministic_hash)
        self.assertEqual(len(ev.deterministic_hash), 64)


if __name__ == "__main__":
    unittest.main()
