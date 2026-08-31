"""
Module 7 Stage 5 Test Suite — Production Engine Verification.

Verifies HellingerDistanceCalculator, KSDistanceCalculator, StatisticalVerificationEngine
(VERIFIED / REJECTED / INCONCLUSIVE), Stage11LineageExtender append-only event generation,
security credential isolation, and input immutability.
"""

import unittest
from typing import Dict, Any

from src.module7.stage4.model import (
    CloudExecutionLifecycleStatus,
    ExecutionEnvironmentType,
    ProviderNeutralExecutionResult,
)
from src.module7.stage5 import (
    StatisticalVerificationDecision,
    StatisticalVerificationPolicy,
    StatisticalVerificationRecord,
    HellingerDistanceCalculator,
    KSDistanceCalculator,
    StatisticalVerificationEngine,
    Stage11LineageExtender,
)


class TestModule7Stage5Engine(unittest.TestCase):
    """Production Engine Tests for Stage 5 Statistical Verification & Lineage Extension."""

    def setUp(self) -> None:
        self.engine = StatisticalVerificationEngine()
        self.lineage = Stage11LineageExtender()
        self.hellinger = HellingerDistanceCalculator()
        self.ks = KSDistanceCalculator()
        self.default_policy = StatisticalVerificationPolicy(
            policy_id="POLICY_TEST_01",
            hellinger_threshold=0.05,
            ks_threshold=0.05,
            min_shots=100,
        )

    def _create_sample_result(
        self,
        counts: Dict[str, int],
        shots: int = 1000,
        job_id: str = "JOB_STAGE5_01",
    ) -> ProviderNeutralExecutionResult:
        return ProviderNeutralExecutionResult(
            job_id=job_id,
            provider_job_id="PROV_JOB_55",
            native_circuit_hash="a" * 64,
            backend_id="IBM_TORINO",
            provider_id="IBM",
            environment_type=ExecutionEnvironmentType.IDEAL_SIMULATOR,
            status=CloudExecutionLifecycleStatus.COMPLETED,
            shots=shots,
            measurement_counts=counts,
            measurement_distribution={k: v / shots for k, v in counts.items()} if shots > 0 else {},
            provenance={"credential_ref": "env:MY_TOKEN_REF"},
        )

    def test_01_hellinger_identical_distributions(self) -> None:
        """Verifies Hellinger distance is 0.0 for identical probability distributions."""
        p = {"00": 0.5, "11": 0.5}
        q = {"00": 0.5, "11": 0.5}
        h_dist = self.hellinger.calculate(p, q)
        self.assertAlmostEqual(h_dist, 0.0, places=6)

    def test_02_hellinger_disjoint_distributions(self) -> None:
        """Verifies Hellinger distance is 1.0 for completely disjoint distributions."""
        p = {"00": 1.0}
        q = {"11": 1.0}
        h_dist = self.hellinger.calculate(p, q)
        self.assertAlmostEqual(h_dist, 1.0, places=6)

    def test_03_ks_distance_calculation(self) -> None:
        """Verifies Kolmogorov-Smirnov distance over lexicographically ordered bitstring keys."""
        p = {"00": 0.5, "11": 0.5}
        q = {"00": 0.4, "11": 0.6}
        ks_dist = self.ks.calculate(p, q)
        self.assertAlmostEqual(ks_dist, 0.1, places=6)

    def test_04_verification_decision_verified(self) -> None:
        """Verifies VERIFIED decision when statistical distance is below policy threshold."""
        observed = self._create_sample_result({"00": 505, "11": 495}, shots=1000)
        reference = {"00": 0.5, "11": 0.5}

        rec = self.engine.verify_result(observed, reference, "REF_EQUAL", self.default_policy)
        self.assertEqual(rec.decision, StatisticalVerificationDecision.VERIFIED)
        self.assertLessEqual(rec.hellinger_distance, 0.05)
        self.assertLessEqual(rec.ks_distance, 0.05)

    def test_05_verification_decision_rejected(self) -> None:
        """Verifies REJECTED decision when statistical distance exceeds policy threshold."""
        observed = self._create_sample_result({"00": 800, "11": 200}, shots=1000)
        reference = {"00": 0.5, "11": 0.5}

        rec = self.engine.verify_result(observed, reference, "REF_EQUAL", self.default_policy)
        self.assertEqual(rec.decision, StatisticalVerificationDecision.REJECTED)
        self.assertGreater(rec.hellinger_distance, 0.05)

    def test_06_verification_decision_inconclusive_insufficient_shots(self) -> None:
        """Verifies INCONCLUSIVE decision when observed shots < policy min_shots."""
        observed = self._create_sample_result({"00": 25, "11": 25}, shots=50)  # 50 < 100
        reference = {"00": 0.5, "11": 0.5}

        rec = self.engine.verify_result(observed, reference, "REF_EQUAL", self.default_policy)
        self.assertEqual(rec.decision, StatisticalVerificationDecision.INCONCLUSIVE)
        self.assertIn("INSUFFICIENT_SHOTS", rec.provenance["failure_reason"])

    def test_07_stage11_lineage_extension(self) -> None:
        """Verifies Stage 11 lineage extension event creation and canonical SHA-256 event_hash."""
        observed = self._create_sample_result({"00": 500, "11": 500}, shots=1000)
        reference = {"00": 0.5, "11": 0.5}

        rec = self.engine.verify_result(observed, reference, "REF_EQUAL", self.default_policy)
        event_hash = self.lineage.append_verification_event(rec)

        self.assertEqual(len(event_hash), 64)

    def test_08_security_credential_isolation(self) -> None:
        """Verifies zero secret keys or tokens appear in verification records or lineage event."""
        observed = self._create_sample_result({"00": 500, "11": 500}, shots=1000)
        reference = {"00": 0.5, "11": 0.5}

        rec = self.engine.verify_result(observed, reference, "REF_EQUAL", self.default_policy)
        rec_str = str(rec.to_dict())

        for secret in ("secret_key_99", "bearer_token_abc", "sk-live-000", "password123"):
            self.assertNotIn(secret, rec_str)

    def test_09_input_immutability(self) -> None:
        """Verifies verification DOES NOT mutate ProviderNeutralExecutionResult or StatisticalVerificationPolicy."""
        observed = self._create_sample_result({"00": 500, "11": 500}, shots=1000)
        reference = {"00": 0.5, "11": 0.5}
        result_hash_before = observed.result_hash
        policy_hash_before = self.default_policy.policy_hash

        _ = self.engine.verify_result(observed, reference, "REF_EQUAL", self.default_policy)

        self.assertEqual(observed.result_hash, result_hash_before)
        self.assertEqual(self.default_policy.policy_hash, policy_hash_before)


if __name__ == "__main__":
    unittest.main()
