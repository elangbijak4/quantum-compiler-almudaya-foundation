"""
Module 6 Stage 11 Test Suite — GAP-2 Lifecycle Transition Validation Tests.
"""

import unittest
from src.module6.lineage import (
    LifecycleEvent,
    HistoricalLineageEvaluator,
    HistoricalLineageRepository,
)


class TestStage11Gap2Transitions(unittest.TestCase):
    """Tests verifying GAP-2: explicit lifecycle transition validation (VALID, INVALID, INCONCLUSIVE)."""

    def test_01_valid_lifecycle_transition(self) -> None:
        """Verifies VALID lifecycle transition (ANALYZED -> VERIFIED)."""
        ev = LifecycleEvent(
            event_id="EVT_VALID_01",
            algorithm_id="ALG_01",
            event_type="AUDIT_VERIFIED",
            previous_state="ANALYZED",
            new_state="VERIFIED",
            source_identity="ALG_01",
            evidence_identity="CERT_01",
            sequence=1,
        )
        res = HistoricalLineageEvaluator.validate_lifecycle_transition(ev)
        self.assertTrue(res.valid)
        self.assertEqual(res.classification, "VALID")
        self.assertIn("is valid", res.reason)

    def test_02_invalid_lifecycle_transition(self) -> None:
        """Verifies INVALID lifecycle transition (REJECTED -> CERTIFIED)."""
        ev = LifecycleEvent(
            event_id="EVT_INVALID_01",
            algorithm_id="ALG_01",
            event_type="AUDIT_CERTIFIED",
            previous_state="REJECTED", # REJECTED is terminal!
            new_state="CERTIFIED",
            source_identity="ALG_01",
            evidence_identity="CERT_01",
            sequence=1,
        )
        res = HistoricalLineageEvaluator.validate_lifecycle_transition(ev)
        self.assertFalse(res.valid)
        self.assertEqual(res.classification, "INVALID")
        self.assertIn("prohibited by policy", res.reason)

        # Verify repository integrity flags invalid transition
        repo = HistoricalLineageRepository()
        repo.append_event(ev)
        integ = repo.verify_integrity()
        self.assertFalse(integ.is_integrity_valid)
        self.assertIn("INVALID_LIFECYCLE_TRANSITION", integ.violations[0])

    def test_03_inconclusive_lifecycle_transition(self) -> None:
        """Verifies INCONCLUSIVE lifecycle transition when previous_state is missing."""
        ev = LifecycleEvent(
            event_id="EVT_INCONC_01",
            algorithm_id="ALG_01",
            event_type="AUDIT_UNKNOWN",
            previous_state="", # Missing state
            new_state="CERTIFIED",
            source_identity="ALG_01",
            evidence_identity="CERT_01",
            sequence=1,
        )
        res = HistoricalLineageEvaluator.validate_lifecycle_transition(ev)
        self.assertFalse(res.valid)
        self.assertEqual(res.classification, "INCONCLUSIVE")
        self.assertIn("Insufficient evidence", res.reason)


if __name__ == "__main__":
    unittest.main()
