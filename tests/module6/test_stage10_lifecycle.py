"""
Module 6 Stage 10 Test Suite — Lifecycle State Transition Tests.
"""

import unittest
from src.module6.governance import (
    CertificationLevel,
    LifecycleStatus,
    GovernanceAuditor,
    AuditCertificate,
)


class TestStage10Lifecycle(unittest.TestCase):
    """Tests verifying valid and invalid lifecycle state transitions."""

    def test_01_valid_lifecycle_transitions(self) -> None:
        """Verifies valid lifecycle transitions (CANDIDATE -> ANALYZED -> VERIFIED -> GOVERNED)."""
        self.assertTrue(GovernanceAuditor.validate_lifecycle_transition(LifecycleStatus.CANDIDATE, LifecycleStatus.ANALYZED))
        self.assertTrue(GovernanceAuditor.validate_lifecycle_transition(LifecycleStatus.ANALYZED, LifecycleStatus.VERIFIED))
        self.assertTrue(GovernanceAuditor.validate_lifecycle_transition(LifecycleStatus.VERIFIED, LifecycleStatus.GOVERNED))

    def test_02_invalid_lifecycle_transitions(self) -> None:
        """Verifies invalid transitions (e.g. CANDIDATE -> CERTIFIED directly or REJECTED -> VERIFIED) fail."""
        self.assertFalse(GovernanceAuditor.validate_lifecycle_transition(LifecycleStatus.CANDIDATE, LifecycleStatus.CERTIFIED))
        self.assertFalse(GovernanceAuditor.validate_lifecycle_transition(LifecycleStatus.REJECTED, LifecycleStatus.VERIFIED))
        self.assertFalse(GovernanceAuditor.validate_lifecycle_transition(LifecycleStatus.DEPRECATED, LifecycleStatus.CERTIFIED))

    def test_03_certified_prerequisite_guard(self) -> None:
        """Verifies transition to CERTIFIED requires FULLY_GOVERNED_CERTIFIED level."""
        uncert_cert = AuditCertificate(
            certificate_id="C1",
            algorithm_id="A1",
            certification_level=CertificationLevel.UNCERTIFIED,
            lifecycle_status=LifecycleStatus.DRAFT,
            stage4_verified=False,
            stage7_feasible=False,
            stage8_optimized=False,
            stage9_quality_passed=False,
            provenance_hash="",
            prerequisites_satisfied=(),
            prerequisites_failed=("STAGE_4_SEMANTIC_VERIFICATION_FAILED",),
        )
        self.assertFalse(GovernanceAuditor.validate_lifecycle_transition(LifecycleStatus.GOVERNED, LifecycleStatus.CERTIFIED, uncert_cert))


if __name__ == "__main__":
    unittest.main()
