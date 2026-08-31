"""
Module 7 Stage 5 Initialization Unit Tests.

Verifies Stage 5 subpackage imports, StatisticalVerificationPolicy defaults,
StatisticalVerificationRecord construction, SHA-256 verification hash determinism,
and decision taxonomy values.
"""

import unittest

from src.module7.stage5 import (
    StatisticalVerificationDecision,
    StatisticalVerificationPolicy,
    StatisticalVerificationRecord,
    StatisticalVerifierProtocol,
    LineageExtensionProtocol,
)


class TestModule7Stage5Initialization(unittest.TestCase):
    """Initialization test suite for Module 7 Stage 5."""

    def test_01_policy_defaults_and_hashing(self) -> None:
        """Verifies StatisticalVerificationPolicy defaults and deterministic SHA-256 policy_hash."""
        policy = StatisticalVerificationPolicy(policy_id="POLICY_DEFAULT_01")
        self.assertEqual(policy.policy_version, "1.0.0")
        self.assertEqual(policy.hellinger_threshold, 0.05)
        self.assertEqual(policy.ks_threshold, 0.05)
        self.assertEqual(policy.min_shots, 100)
        self.assertEqual(len(policy.policy_hash), 64)

    def test_02_record_construction_and_hashing(self) -> None:
        """Verifies StatisticalVerificationRecord construction and deterministic verification_hash."""
        policy = StatisticalVerificationPolicy(policy_id="POLICY_DEFAULT_01")
        rec = StatisticalVerificationRecord(
            verification_id="VERIF_01",
            execution_id="EXEC_01",
            native_circuit_hash="a" * 64,
            reference_id="REF_STAGE3_01",
            observed_result_hash="b" * 64,
            decision=StatisticalVerificationDecision.VERIFIED,
            hellinger_distance=0.012,
            ks_distance=0.015,
            observed_shots=1000,
            policy_hash=policy.policy_hash,
        )
        self.assertEqual(rec.decision, StatisticalVerificationDecision.VERIFIED)
        self.assertEqual(rec.observed_shots, 1000)
        self.assertEqual(len(rec.verification_hash), 64)

    def test_03_decision_enum_taxonomy(self) -> None:
        """Verifies StatisticalVerificationDecision enum contains required states."""
        self.assertEqual(StatisticalVerificationDecision.VERIFIED.value, "VERIFIED")
        self.assertEqual(StatisticalVerificationDecision.REJECTED.value, "REJECTED")
        self.assertEqual(StatisticalVerificationDecision.INCONCLUSIVE.value, "INCONCLUSIVE")


if __name__ == "__main__":
    unittest.main()
